import datetime
import json
import traceback
from typing import Union

import webexteamssdk
from dateutil import parser, tz
from flask import Flask, request

from bot.controller import Controller

app = Flask(__name__)
greeting_card = json.load(open('bot/cards/greeting.json'))
controller = Controller()


def rooms_both_in() -> list[webexteamssdk.models.immutable.Room]:
    rooms = []
    for room in controller.api.rooms.list():
        if room.type == 'group':
            for membership in controller.api.memberships.list(roomId=room.id):
                if request.json.get('data', {}).get('personId') == membership.personId:
                    rooms.append(room)
                    break
    return rooms


def save_reminder(
    room: webexteamssdk.models.immutable.Room,
    message: str,
    date: datetime.datetime
) -> Union[str, int]:
    try:
        return controller.db.set(date.timestamp(), json.dumps({'roomId': room.id, 'markdown': message}).encode())
    except Exception as e:
        return send_unexpected_error(e)


def send_card(sender: str) -> None:
    dm = [{"title": "Direct Message", "value": request.json['data']['roomId']}]
    group_rooms = dm + [{"title": i.title, "value": i.id} for i in rooms_both_in()]
    greeting_card['attachments'][0]['content']['body'][5]['actions'][0]['card']['body'][4]['choices'] = group_rooms
    controller.api.messages.create(**greeting_card, roomId=sender)


def send_unexpected_error(e: Exception) -> str:
    try:
        print(traceback.print_exc())
        print(e)
        message = f"An unexpected error occurred:( -- '{e}' -- Please reach out to my creator."
        controller.api.messages.create(text=message, roomId=request.json.get('data').get('personId'))
        return 'OK'
    except Exception as exc:
        print(traceback.print_exc())
        print(exc)
        return 'NOT OK'


@app.route('/greeting', methods=["POST"])
def greeting() -> str:
    try:
        if controller.api.people.me().id != request.json.get('data', {}).get('personId') and \
                (request.json.get('data', {}).get('roomType') == 'direct') or \
                controller.api.people.me().id in request.json.get('data', {}).get('mentionedPeople', []):
            send_card(request.json['data']['roomId'])
            return 'OK'
        return ''
    except Exception as e:
        return send_unexpected_error(e)


@app.route('/healthcheck')
def healthcheck() -> str:
    return 'OK'


@app.route('/card_submit', methods=["POST"])
def card_submit() -> str:
    try:
        request_payload = request.json
        action = controller.api.attachment_actions.get(request_payload['data']['id'])
        # This will work for direct or group chats
        sender = request_payload['data']['roomId']
        # {'createReminder': True,
        # 'reminderDate': '',
        # 'reminderLocationRoomID': '',
        # 'reminderMessage': '',
        # 'reminderTime': ''}
        if action.inputs.get('createReminder') is True:
            # if action.inputs.get('reminderLocationEmail') and action.inputs.get('reminderLocationRoomID'):
            #     api.messages.create(roomId=sender, text="You cannot provide both an email and a room! Try again:)")
            #     send_card(sender)
            #     return 'NOT OK'
            # elif not action.inputs.get('reminderLocationEmail') and not action.inputs.get('reminderLocationRoomID'):
            #     api.messages.create(roomId=sender, text="You must provide either an email or a room! Try again:)")
            #     send_card(sender)
            #     return 'NOT OK'
            if not action.inputs.get('reminderMessage'):
                controller.api.messages.create(roomId=sender, text="You must provide a reminder message! Try again:)")
                send_card(sender)
                return 'NOT OK'

            if not action.inputs.get('reminderDate') or not action.inputs.get('reminderTime'):
                controller.api.messages.create(roomId=sender, text="You must provide both a date and time! Try again:)")
                send_card(sender)
                return 'NOT OK'

            try:
                # Parse time and date and check to make sure it's at least 5 seconds from now
                # Always assume EST per note in the card to the user
                date = parser.parse(f'{action.inputs["reminderDate"]} {action.inputs["reminderTime"]}-4:00')
            except Exception as e:
                print(e)
                message = "Date should be in the format 'XX-YY-ZZZZ' and time should be in the " + \
                    "format 'AA:BB:CC'! Try again:)"
                controller.api.messages.create(roomId=sender, text=message)
                send_card(sender)
                return 'NOT OK'

            if date <= (datetime.datetime.now(tz.tzutc()) + datetime.timedelta(seconds=5)):
                message = "Date and time must be at least 5 seconds in the future! Try again:)"
                controller.api.messages.create(roomId=sender, text=message)
                send_card(sender)
                return 'NOT OK'

            room = None

            # Validate room ID
            # Basic room membership check

            is_current_room = action.inputs.get('reminderLocationRoomID') == request_payload['data']['roomId']
            if action.inputs.get('reminderLocationRoomID') not in rooms_both_in() and not is_current_room:
                message = "We both must have access to the location you want me to send the reminders in! Try again:)"
                controller.api.messages.create(roomId=sender, text=message)
                send_card(sender)
                return 'NOT OK'

            try:
                room = controller.api.rooms.get(action.inputs.get('reminderLocationRoomID'))
            except webexteamssdk.exceptions.ApiError:
                message = "I don't think I'm in that room. Please add me and try again:)"
                controller.api.messages.create(roomId=sender, text=message)
                send_card(sender)
                return 'NOT OK'

            message = action.inputs.get('reminderMessage')
            nice_date = date.strftime("%A, %B %d %Y at %I:%M:%S %p")
            info = f'I will remind you via "{room.title}" on "{nice_date}" that "{message}"'
            save_reminder(room=room, message=message, date=date)
            controller.api.messages.create(roomId=sender, text=f"Reminder created successfully! Thank you:)\n\n{info}")

        return 'OK'
    except Exception as e:
        return send_unexpected_error(e)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")

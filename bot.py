import json
from flask import Flask, request
from webexteamssdk import WebexTeamsAPI

app = Flask(__name__)
greeting_card = json.load(open('cards/greeting.json'))

secrets = json.load(open('/run/secrets/token'))
api = WebexTeamsAPI(access_token=secrets['WEBEX_TEAMS_ACCESS_TOKEN'])


@app.route('/greeting', methods=["POST"])
def greeting():
    request_payload = request.json
    if request_payload['data']['roomType'] == 'group':
        sender = {'roomId': request_payload['data']['roomId']}
    else:
        sender = {'toPersonId': request_payload['data']['personId']}
        
    group_rooms = [{"title": i.title, "value": i.id} for i in api.rooms.list() if i.type == "group"]
    greeting_card['attachments'][0]['content']['body'][5]['actions'][0]['card']['body'][6]['choices'] = group_rooms
    api.messages.create(**greeting_card, **sender)
    return 'OK'


@app.route('/card_submit', methods=["POST"])
def card_submit():
    pass



if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")
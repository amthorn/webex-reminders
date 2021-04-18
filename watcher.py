import datetime
import json
import time

import redis
from webexteamssdk import WebexTeamsAPI

secrets = json.load(open('/run/secrets/token'))
api = WebexTeamsAPI(access_token=secrets['WEBEX_TEAMS_ACCESS_TOKEN'])
db = redis.Redis(host='127.0.0.1', port=6379, db=0)


print("Relaxing...")
while True:
    try:
        # Relax
        keys = db.keys()  # Atomic to avoid multithreading issues since we don't use a lock
        now = datetime.datetime.utcnow().timestamp()
        for key in keys:
            timestamp = float(key.decode())
            if now >= timestamp:
                print(f"Delivering reminder {timestamp}")
                # Trigger reminder
                api.messages.create(**json.loads(db.get(key).decode()))

                # atomic db pop
                db.delete(key)
        time.sleep(1)
    except Exception as e:
        print(e)

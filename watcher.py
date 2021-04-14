import json
import traceback
import datetime
import pytz
import redis
import time
from dateutil import parser
from webexteamssdk import WebexTeamsAPI

print("Relaxing...")
while True:
    try:
        secrets = json.load(open('/run/secrets/token'))
        api = WebexTeamsAPI(access_token=secrets['WEBEX_TEAMS_ACCESS_TOKEN'])
        db = redis.Redis(host='redis', port=6379, db=0)
        
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
import json

import redis
from webexteamssdk import WebexTeamsAPI


class Controller:
    TOKEN_FILE = '/run/secrets/token'
    WEBEX_KEY = 'WEBEX_TEAMS_ACCESS_TOKEN'
    REDIS_HOST = 'redis'
    REDIS_PORT = 6379

    def __init__(self) -> None:
        self.secrets = json.load(open(Controller.TOKEN_FILE))
        self.api = WebexTeamsAPI(access_token=self.secrets[Controller.WEBEX_KEY])
        self.db = redis.Redis(host=Controller.REDIS_HOST, port=Controller.REDIS_PORT, db=0)

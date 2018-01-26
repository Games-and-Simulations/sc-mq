import json
from typing import List


class PlayMessage:
    bots: List[str]
    map: str
    game_name: str

    def __init__(self, bots, map, game_name):
        self.bots = bots
        self.map = map
        self.game_name = game_name

    def serialize(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def deserialize(json_msg):
        msg = json.loads(json_msg)
        return PlayMessage(msg['bots'],
                           msg['map'],
                           msg['game_name'])

    def __str__(self):
        return self.serialize()

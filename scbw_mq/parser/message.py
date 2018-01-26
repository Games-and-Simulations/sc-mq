import json
from typing import List


class ParseMessage:
    map: str

    def __init__(self, map):
        self.map = map

    def serialize(self) -> str:
        return self.map

    @staticmethod
    def deserialize(msg):
        return ParseMessage(msg)

    def __str__(self):
        return self.serialize()

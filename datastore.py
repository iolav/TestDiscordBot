import os
import json
from typing import Final

DEFAULT_USER_DATA : Final[dict] = {
    "coins_wallet": 250,
    "coins_bank": 1000,
}

opFuncs : Final[dict] = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "=": lambda _, y: y,
}

class Datastore:
    def __init__(self, fileName):
        self.fileName = fileName
        
        if not os.path.exists(self.fileName):
            with open(self.fileName, "w") as file:
                json.dump({}, file)

        with open(self.fileName, "r") as file:
            self.data = json.load(file)

    def save(self):
        with open(self.fileName, "w") as file:
            json.dump(self.data, file, indent = 4)

    def steralize_user(self, user : str):
        if user not in self.data:
            self.data[user] = DEFAULT_USER_DATA.copy()
            self.save()

    def fetch(self, user : str, key : str):
        self.steralize_user(user)

        try:
            return self.data[user][key]
        except:
            return None
    
    def fetchAll(self):
        try:
            return self.data
        except:
            return None

    def change(self, user: str, key: str, value, op: str):
        self.steralize_user(user)

        self.data.setdefault(user, {}).setdefault(key, type(value)())

        current: int = self.data[user][key]
        self.data[user][key] = opFuncs[op](current, value)

        self.save()
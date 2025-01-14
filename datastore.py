import os
import json
from typing import Final

DEFAULT_USER_DATA : Final[dict] = { #Default values for new users
    "coins_wallet": 250,
    "coins_bank": 1000,
}

opFuncs : Final[dict] = { #Thank you python for blessing me with lambda functions
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "=": lambda _, y: y,
}

class Datastore:
    def __init__(self, filename): #Setting up the "database" json file
        self.filename = filename
        
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as file:
                json.dump({}, file)

        with open(self.filename, "r") as file:
            self.data = json.load(file)

    def save(self): #Saving data
        with open(self.filename, "w") as file:
            json.dump(self.data, file, indent=4)

    def steralize_user(self, user : str): #If its a new user, give them the default values (Again, DRY)
        if user not in self.data:
            self.data[user] = DEFAULT_USER_DATA.copy()
            self.save()

    def fetch(self, user : int, key : str): #Fetching data
        self.steralize_user(user)

        try:
            current = self.data[user][key]
        except:
            current = None

        return current

    def change(self, user: str, key: str, value, op: str): #Modifying data
        self.steralize_user(user)

        self.data.setdefault(user, {}).setdefault(key, type(value)()) #What

        current: int = self.data[user][key]
        self.data[user][key] = opFuncs[op](current, value)

        self.save()
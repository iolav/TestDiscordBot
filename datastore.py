import os
import json

opFuncs : dict = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "=": lambda _, y: y,
}

def getDefault(type_):
    return type_()

class Datastore:
    def __init__(self, filename):
        self.filename = filename
        
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as file:
                json.dump({}, file)

        with open(self.filename, "r") as file:
            self.data = json.load(file)

    def save(self):
        with open(self.filename, "w") as file:
            json.dump(self.data, file, indent=4)

    def fetch(self, user : int, key : str):
        try:
            current = self.data[user][key]
        except:
            current = None

        return current

    def change(self, user: str, key: str, value, op: str):
        self.data.setdefault(user, {}).setdefault(key, getDefault(type(value)))

        current: int = self.data[user][key]
        self.data[user][key] = opFuncs[op](current, value)

        self.save()
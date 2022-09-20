import json
from datetime import datetime


class Database:
    def __init__(self, url="data/database.json", logfile="data/log") -> None:
        self.url = url
        self.logfile = logfile

    def _log(self, message) -> None:
        with open(self.logfile, "a") as file:
            file.write(f"[{datetime.now()}] {message}")

    def get(self, key) -> None | dict | list:
        with open(self.url, "r") as file:
            data = json.load(file)
            if key in data:
                self._log(f"Loaded key {key} from database.\n")
                return data[key]
            self._log(f"Key {key} not found in database.\n")
            return None

    def post(self, key, value) -> None:
        with open(self.url, "r") as file:
            data = json.load(file)
            data[key] = value
        with open(self.url, "w") as file:
            self._log(f"Wrote a value to key {key} in database of {str(value)}.\n")
            json.dump(data, file, indent=2)

    def delete(self, key) -> None:
        with open(self.url, "r") as file:
            data = json.load(file)
            if key in data:
                del data[key]
            else:
                return None
        with open(self.url, "w") as file:
            self._log(f"Deleted key {key} from database.\n")
            json.dump(data, file, indent=2)

# import pymongo
#
#
# class Database:
#     def __init__(self, uri, collection):
#         self.uri = uri
#         self.client = pymongo.MongoClient(uri)
#         self.db = self.client["Pineabase"]
#         self.collection = self.db[collection]
#
#     def get(self, key):
#         return self.collection.find_one({"_id": key})
#
#     def post(self, key, value):
#         return self.collection.insert_one({"_id": key, "value": value})
#
#     def delete(self, key):
#         return self.collection.delete_one({"_id": key})

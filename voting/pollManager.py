import discord
import tinydb
import re
import poll

class PollManager:
    commandWords = {"vote": "vote"}
    _tableName = "polls"

    def __init__(self, db: tinydb.TinyDB):
        self.table = db.table(self._tableName)

    def processMessage(self, message: discord.Message):
        author: int = message.author.id
        msg = re.sub("^.*"+self.commandWords.get("vote"),"",message.content,1).strip()

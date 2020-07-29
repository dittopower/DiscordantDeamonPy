import tinydb
import poll as polllib
from config import Configuration
from collections import namedtuple
from auth import AuthManager

config = Configuration("config.json")
db = tinydb.TinyDB("testdb.json")
auth = AuthManager(config)
db.drop_tables()

import pollManager

pm = pollManager.PollManager(db,auth)
Message = namedtuple('Message', ['author', 'content', 'channel'])
User = namedtuple('User', ['id','permissions_in'])
Channel = namedtuple('Channel', ['send'])
Perms = namedtuple('Perms', ['administrator'])

async def sss(text):
    print(text)

def t(text):
    return Perms(True)
def f(text):
    return Perms(False)

async def runA(st):
    print("----##runA##----")
    await pm.processMessage(Message(User(123,t),st,Channel(sss)))
async def runB(st):
    print("----##runB##----")
    await pm.processMessage(Message(User(456,f),st,Channel(sss)))

async def main():
    await runA("vote new hi?")
    await runA("vote new bye! !")
    await runA("vote %1 finish")
    await runA("vote history")
    await runA("vote current")
    await runA("vote %2 add aaa")
    await runA("vote %2 add b b b")
    await runA("vote %2 list")
    await runA("vote %2 2")
    await runB("vote %2 2")
    await runA("vote %2 results")

import asyncio
asyncio.run(main())

db.close()

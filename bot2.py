import discord
import sys
import tinydb
from config import Configuration
from serverOrchestrator import Server
from voting.democraticPoll import democraticPoll
from auth import AuthManager

cmd_prefix: str = '~'
servers = {}
config = Configuration("config.json")
auth = AuthManager(config)
db = tinydb.TinyDB(config.databaseFile)
polls = {}

# create server managers
for server in config.servers:
    servers[server.name] = Server(server)

client = discord.Client()


@client.event
async def on_connect():
    print('Connected to Discord')


@client.event
async def on_disconnect():
    print('Disconnected from Discord')


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_resumed():
    print('Resumed previous session.')


@client.event
async def on_error(event, *args, **kwargs):
    print('[Error] {0} [{1[0].guild}][{1[0].channel}]: {1} - {2}'.format(event, args, kwargs))


async def shutdown():
    for server in servers.values():
        server.stop()
    await client.close()


@client.event
async def on_message(message: discord.Message):
    try:
        if message.author == client.user:
            return

        user: discord.Member = message.author
        msg: str = message.content
        if msg.startswith(cmd_prefix):
            msg = msg.replace("~", "", 1).strip()
            print('[msg][{0.guild}][{0.channel}]@{0.author}: {0.content}'.format(message))

            # Bot Admin Commands
            # TODO: Config file
            if auth.isBotAdmin(user.id):
                if msg.startswith('shutdown'):
                    return await shutdown()

            # Role based
            roles: [str] = list()
            if message.guild:
                for r in user.roles:
                    role: discord.Role = r
                    roles.append(role.name)

            # Server Commands
            serverMsg = msg.split(" ", 1)
            serverName = serverMsg[0].upper()
            if serverName in servers:
                server: Server = servers[serverName]
                if len(serverMsg) > 1:
                    serverCmd = serverMsg[1]
                else:
                    serverCmd = "status"
                if auth.isBotAdmin(user.id) or server.config.role in roles or server.config.admin_role in roles:
                    if 'start' in serverCmd:
                        return await message.channel.send(servers[serverName].start())
                    elif 'stop' in serverCmd:
                        return await message.channel.send(servers[serverName].stop())
                    elif 'status' in serverCmd:
                        return await message.channel.send(servers[serverName].statusText())
                if auth.isBotAdmin(user.id) or server.config.admin_role in roles:
                    if 'run' in serverCmd:
                        serverCmd = serverCmd.replace("run", "", 1).strip()
                        return await message.channel.send(servers[serverName].cmd(msg))

            # User Commands
            if msg.startswith('ping'):
                return await message.channel.send('pong!')
            if msg.startswith('help'):
                return await message.channel.send('Not today...')
            if msg.startswith("multivote"):
                multivote = True
                msg = msg.replace("multivote", "vote", 1)
            else:
                multivote = False
            if msg.startswith('vote'):
                msg = msg.replace("vote", "", 1).strip()
                cmd = msg.split(" ", 1)
                cmd[0] = cmd[0].lower()
                if cmd[0].startswith("new") or cmd[0].startswith("create"):
                    for i in polls:
                        poll: democraticPoll = polls[i]
                        if poll.question.lower() == cmd[1].lower():
                            return await message.channel.send('Poll already exists! ||%{0.id}|| "{0.question}"'.format(poll))
                    poll = democraticPoll(user, cmd[1], multivote)
                    poll.id = len(polls)
                    while polls.get(poll.id):
                        poll.id += 1
                    polls[poll.id] = poll
                    return await message.channel.send('Poll created: ||%{0.id}|| {0.question}'.format(poll))
                if cmd[0].startswith("history"):
                    output = "Historical Polls:"
                    output+= "\n-----------------"
                    for poll in polls.values():
                        output += "\n\|\| ||%{0.id}|| \|\| {0.question}".format(poll)
                    output+= "\n-----------------"
                    return await message.channel.send(output)
                if cmd[0].startswith("%"):
                    cmd[0] = cmd[0].replace("%", "")
                if cmd[0].isnumeric():
                    poll = polls.get(int(cmd[0]))
                    if not poll:
                        return await message.channel.send('Unknown Poll ID!')
                    cmd = cmd[1].split(" ", 1)
                    cmd[0] = cmd[0].lower()
                    if cmd[0].startswith("add"):
                        if poll.addOption(user, cmd[1]):
                            return await message.channel.send('Added option {1} to ||%{0.id}|| {0.question}'.format(poll, cmd[1]))
                        else:
                            return await message.channel.send("Couldn't add option {1} to ||%{0.id}|| {0.question}. The poll may not allow editing.".format(poll, cmd[1]))
                    if cmd[0].isnumeric():
                        return await poll.vote(user,int(cmd[0]))
                    if cmd[0].startswith("status"):
                        return await message.channel.send(poll.status())
                    if cmd[0].startswith("list"):
                        return await message.channel.send("Poll ||%{0.id}|| {0.question}:\n".format(poll) + poll.listOptions())
                    if cmd[0].startswith("results") or cmd[0].startswith("tally"):
                        return await message.channel.send("Poll ||%{0.id}|| {0.question}:\n{1}".format(poll,poll.listOptions(True)))
                    if cmd[0].startswith("redo"):
                        poll = poll.redo(user)
                        poll.id = len(polls)
                        while polls.get(poll.id):
                            poll.id += 1
                        polls[poll.id] = poll
                        return await message.channel.send('Recreated: {0}\n{1}'.format(poll.status(),poll.listOptions()))
                    if auth.isBotAdmin(user.id) or user.permissions_in(message.channel).administrator or user is poll.owner:
                        if cmd[0].startswith("delete"):
                            polls.pop(poll.id)
                            return await message.channel.send('Poll deleted: ||%{0.id}|| {0.question}'.format(poll))
                        if cmd[0].startswith("start") or cmd[0].startswith("restart"):
                            poll.start()
                            return await message.channel.send('Poll: ||%{0.id}|| {0.question}\n{1}\n----\nPlease vote now: msg me "~vote ||%{0.id}|| your_options_number"'.format(poll, poll.listOptions()))
                        if cmd[0].startswith("finish") or cmd[0].startswith("end"):
                            return await message.channel.send(poll.finish())
                return await message.channel.send('Looks like your vote command was incomplete or invalid! "{0}"'.format(message.content))

    except:  # catch *all* exceptions
        e = sys.exc_info()
        # print("Error: {0}".format(e[0]))
        print(e)
    return

print("Launching Bot...")
client.run(config.discordBotKey)

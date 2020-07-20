import discord
import sys
from config import Configuration
from serverOrchestrator import Server

cmd_prefix: str = '~'
servers = {}
config = Configuration("config.json")

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


def isBotAdmin(user: discord.User):
    return str(user.id) in config.adminUsers


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
            if isBotAdmin(user):
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
                if isBotAdmin(user) or server.config.role in roles or server.config.admin_role in roles:
                    if 'start' in serverCmd:
                        return await message.channel.send(servers[serverName].start())
                    elif 'stop' in serverCmd:
                        return await message.channel.send(servers[serverName].stop())
                    elif 'status' in serverCmd:
                        return await message.channel.send(servers[serverName].statusText())
                if isBotAdmin(user) or server.config.admin_role in roles:
                    if 'run' in serverCmd:
                        serverCmd = serverCmd.replace("run", "", 1).strip()
                        return await message.channel.send(servers[serverName].cmd(msg))

            # User Commands
            if msg.startswith('ping'):
                return await message.channel.send('pong!')
    except:  # catch *all* exceptions
        e = sys.exc_info()
        # print("Error: {0}".format(e[0]))
        print(e)
    return

print("Launching Bot...")
client.run(config.discordBotKey)

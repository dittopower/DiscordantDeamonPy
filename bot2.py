import discord
import serverClient
import sys
import config

cmd_prefix: str = '~'
servers = {}
cfg = config.config("config.json")

# create server managers
for index in range(len(cfg.getServers())):
    servers[cfg.getServerName(index)] = serverClient.server(cfg.getServerLauncher(index), cfg.getServerArguements(index), cfg.getServerStopCmd(index), cfg.getServerSaveCmd(index))

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
    return str(user.id) in cfg.getAdmins()


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
            serverCmd = serverMsg[1]
            if serverName in servers:
                if isBotAdmin(user) or cfg.getServerRole(serverName) in roles or cfg.getServerAdminRole(serverName) in roles:
                    if 'start' in serverCmd:
                        await message.channel.send(servers[serverName].start())
                        return
                    elif 'stop' in serverCmd:
                        await message.channel.send(servers[serverName].stop())
                        return
                    elif 'status' in serverCmd:
                        await message.channel.send(servers[serverName].statusText())
                        return
                if isBotAdmin(user) or cfg.getServerAdminRole(serverName) in roles:
                    if 'run' in serverCmd:
                        serverCmd = serverCmd.replace("run", "", 1).strip()
                        await message.channel.send(servers[serverName].cmd(msg))
                        return

            # User Commands
            if msg.startswith('ping'):
                await message.channel.send('pong!')
                return
    except:  # catch *all* exceptions
        e = sys.exc_info()[0]
        print("<p>Error: %s</p>" % e)
    return

client.run(cfg.discordBotKey())

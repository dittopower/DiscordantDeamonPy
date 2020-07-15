import discord
# https://discord.com/api/oauth2/authorize?client_id=732879774321737749&permissions=93248&scope=bot

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

client = MyClient()
client.run('discord bot secret')
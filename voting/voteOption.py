import discord

class voteOption:
    count = 0
    def __init__(self, author: discord.User, option: str):
        self.author = author
        self.option = option
        
import json
import typing
from serverConfig import ServerConfiguration


class Configuration:

    def __init__(self, path: str):
        with open('config.json', 'r') as file:
            self.filePath = path
            config: dict = json.load(file)

        self.discordBotKey = config.get('discord_bot_key')
        if not self.discordBotKey:
            raise Exception("Configuration is missing 'discord_bot_key' element", config)

        self.databaseFile = config.get('database_file')
        if not self.databaseFile:
            raise Exception("Configuration is missing 'database_file' element", config)

        self.role = config.get('default_role')
        if self.role:
            self.role.upper()
        self.adminRole = config.get('default_admin_role')
        if self.adminRole:
            self.adminRole = self.adminRole.upper()

        self.adminUsers = config.get('admin_users')
        if not self.adminUsers:
            raise Exception("Configuration is missing 'admin_users' element", config)

        server_list: [] = config.get('servers')
        self.servers: [ServerConfiguration] = []
        for server in server_list:
            self.servers.append(ServerConfiguration(server))

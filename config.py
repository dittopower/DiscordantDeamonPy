import json
import typing


class config:
    discord_bot_key = 'discord_bot_key'
    admin_users = 'admin_users'
    default_server_role = 'default_role'
    default_server_admin_role = 'default_admin_role'
    server_list = 'servers'
    server_name = 'name'
    server_launcher = 'launcher'
    server_arguments = 'args'
    server_stop_command = 'stop'
    server_save_command = 'save'
    server_role = 'role'
    server_admin_role = 'admin_role'

    def __init__(self, path: str):
        with open('config.json', 'r') as file:
            self.filePath = path
            self.config = json.load(file)
    
    def __getKeyUpper__(self,key:str):
        if (self.config[key]):
            return self.config[key].upper()
        return None

    def discordBotKey(self) -> str:
        return self.config[self.discord_bot_key]

    def getAdmins(self) -> [str]:
        return self.config[self.admin_users]

    def default_Role(self) -> str:
        return self.__getKeyUpper__(self.default_Role)

    def defaultAdminRole(self) -> str:
        return self.__getKeyUpper__(self.default_server_admin_role)

    def getServers(self) -> list:
        return self.config[self.server_list]

    def getServer(self, i: int):
        return self.config[self.server_list][i]

    def getServerName(self, i: int) -> str:
        return self.__getKeyUpper__(self.server_name)

    def getServerLauncher(self, i: int) -> str:
        return self.config[self.server_list][i][self.server_launcher]

    def getServerArguements(self, i: int) -> str:
        return self.config[self.server_list][i][self.server_arguments]

    def getServerStopCmd(self, i: int) -> str:
        return self.config[self.server_list][i][self.server_stop_command]

    def getServerSaveCmd(self, i: int) -> str:
        return self.config[self.server_list][i][self.server_save_command]

    def getServerRole(self, i: int) -> str:
        return self.__getKeyUpper__(self.server_role)

    def getServerAdminRole(self, i: int) -> str:
        return self.__getKeyUpper__(self.server_admin_role)

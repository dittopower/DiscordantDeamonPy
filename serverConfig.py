import json
import typing


class ServerConfiguration:

    def __init__(self, jsonDict: dict):
        self.name = jsonDict.get('name')
        if self.name:
            self.name = self.name.upper()
        else:
            raise Exception("Server Configuration is missing a 'name' element", jsonDict)
        print("Configuring Server: {0}".format(self.name))

        self.launcher = jsonDict.get('launcher')
        if self.launcher:
            self.launcher = self.launcher.upper()
        else:
            raise Exception("Server Configuration is missing a 'launcher' element", jsonDict)

        self.role = jsonDict.get('role')
        if self.role:
            self.role.upper()
        self.admin_role = jsonDict.get('admin_role')
        if self.admin_role:
            self.admin_role = self.admin_role.upper()
        if (not self.role) and (not self.admin_role):
            print("No linked roles, will use bot defaults.")
        else:
            print("Linking roles: Monitor: {0} Admin: {1}".format([self.role],[self.admin_role]))

        self.arguments = jsonDict.get('args')
        if self.arguments:
            self.arguments = self.arguments.upper()
        self.cmd_stop = jsonDict.get('stop')
        if self.cmd_stop:
            self.cmd_stop = self.cmd_stop.upper()
        self.cmd_save = jsonDict.get('save')
        if self.cmd_save:
            self.cmd_save = self.cmd_save.upper()
        self.cmd_status = jsonDict.get('status')
        if self.cmd_status:
            self.cmd_status.upper()

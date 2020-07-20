import subprocess
import io
from serverConfig import ServerConfiguration


class Server:
    Server: subprocess.Popen = None

    def __init__(self, cfg: ServerConfiguration):
        self.config = cfg

    def start(self):
        if self.Server and self.status() is None:
            return "It's already running!"
        else:
            envinfo = subprocess.STARTUPINFO()
            envinfo.dwFlags |= subprocess.CREATE_NEW_CONSOLE
            envinfo.dwFlags |= subprocess.REALTIME_PRIORITY_CLASS
            self.Server = subprocess.Popen(
                [self.config.launcher,self.config.arguments], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=envinfo)
        return self.statusText()

    def statusText(self):
        us = self.status()
        if us is None:
            extraStatusDetails = ""
            if self.config.cmd_status:
                extraStatusDetails = self.cmd(self.config.cmd_status)
            return "Status: Online\n{}".format(extraStatusDetails)
        return "Status: Offline {0}".format(us)

    def status(self):
        if self.Server:
            return self.Server.poll()
        else:
            return 0

    def stop(self):
        if self.Server and self.status() is None:
            if self.config.cmd_stop:
                self.Server.communicate(self.config.cmd_stop, 15)
            else:
                self.Server.kill()
            return self.statusText()
        else:
            return "It's already stopped!"

    def cmd(self, input: str):
        if self.Server and self.status() is None:
            out = self.Server.stdout
            out.seek(0, io.SEEK_END)
            self.Server.stdin.write(input)
            return out.readlines()
        else:
            return "Error: It's not running..."

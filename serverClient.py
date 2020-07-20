import subprocess
import io
class server:
    server: subprocess.Popen = None
    execute = None
    arguments = []
    def __init__(self,exe:str,args = [],cmdStop = None,cmdSave = None):
        self.execute = exe
        self.arguments = args
        self.cmdStop = cmdStop
        self.cmdSave = cmdSave

    def start(self):
        if self.server and self.status() is None:
            return "It's already running!"
        else:
            envinfo= subprocess.STARTUPINFO()
            envinfo.dwFlags |= subprocess.CREATE_NEW_CONSOLE
            envinfo.dwFlags |= subprocess.REALTIME_PRIORITY_CLASS
            self.server = subprocess.Popen([self.execute]+self.arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=envinfo)
        return self.statusText()

    def statusText(self):
        us = self.status()
        if us is None:
            us = "Ok"
        return "Status: {0}".format(us)

    def status(self):
        if self.server:
            return self.server.poll()
        else:
            return 0

    def stop(self):
        if self.server and self.status() is None:
            if self.cmdStop :
                self.server.communicate(self.cmdStop,15)
            else:
                self.server.kill()
            return self.statusText()
        else:
            return "It's already stopped!"
    
    def cmd(self,input: str):
        if self.server and self.status() is None:
            out = self.server.stdout
            out.seek(0,io.SEEK_END)
            self.server.stdin.write(input)
            return out.readlines()
        else:
            return "It's not running..."

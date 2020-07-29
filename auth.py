import config


class AuthManager:
    def __init__(self, cfg: config.Configuration):
        self._cfg = cfg

    def isBotAdmin(self, userId: int):
        return str(userId) in self._cfg.adminUsers

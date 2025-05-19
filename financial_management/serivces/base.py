class BaseWalletService:
    def _init_(self, user, amount, ip, agent, **kwargs):
        self.user = user
        self.amount = amount
        self.ip = ip
        self.agent = agent
        self.kwargs = kwargs

    def validate(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError
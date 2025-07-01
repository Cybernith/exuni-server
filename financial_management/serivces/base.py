class BaseWalletService:
    def __init__(self, user, amount, ip, agent, transaction_id=None, authority=None, **kwargs):
        self.user = user
        self.amount = amount
        self.ip = ip
        self.transaction_id = transaction_id
        self.agent = agent
        self.authority = authority
        self.kwargs = kwargs

    def validate(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError
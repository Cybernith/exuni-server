class BaseWalletService:
    def _init_(self, user, amount, **kwargs):
        self.user = user
        self.amount = amount
        self.kwargs = kwargs

    def validate(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError
# What am I doing in this branch

1. Use AccountMixin everywhere I used account, floatAccount, costCenter
    1. update models one by one and test in front
    2. migrate from old fields to new ones

### Guid

- Update models
- Update serializers
- Make migrations
- Migrate
- Check and test in front

### Finished Tasks:

- write AccountMixin and update AccountProxy
- finished (models || non-models):
    - `SanadItem`
    - `Cheque`, `Chequebook`, `StatusChange` || `AccountGroup`
    - `Transaction`, `TransactionItem`, `AcountBalance`, `ImprestSettlementItem` || `helpers/functions.py`, `AutoSanad`
    - `Factor`, `Expense`, `FactorExpense`
- _dashtbashi doesn't use cost_center to float_account in that way
- distribution accounts part is not implemented
- THE JOB IS DONE
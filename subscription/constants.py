SANADS = 'sanads'
TRANSACTIONS = 'transactions'
FACTORS = 'factors'
WAREHOUSES = 'warehouses'
DISTRIBUTION = 'distribution'
CONST_ACCOUNTING = 'const_accounting'
MODULES = (
    (SANADS, 'حسابداری'),
    (TRANSACTIONS, 'خزانه داری'),
    (FACTORS, 'بازرگانی'),
    (WAREHOUSES, 'انبار'),
    (DISTRIBUTION, 'پخش'),
    (CONST_ACCOUNTING, 'بهای تمام شده'),
)

ACCOUNTS_CUD = 'ACCOUNTS_CUD'  # 4 levels, does not included banks & persons
UNLIMITED_SIDE_ACCOUNT = 'UNLIMITED_BANK_ACCOUNT'
UPDATE_ACCOUNT_IN_TREE = 'UPDATE_ACCOUNT_IN_TREE'
FLOAT_ACCOUNTS = 'FLOAT_ACCOUNTS'
BANK_TRANSFER_TRANSACTION = 'BANK_TRANSFER_TRANSACTION'
GUARANTEE_DOCUMENTS = 'GUARANTEE_DOCUMENTS'
IMPREST_TRANSACTION = 'IMPREST_TRANSACTION'
PERMANENT_FINANCIAL_YEAR = 'PERMANENT_FINANCIAL_YEAR'
FIFO_INVENTORY = 'FIFO_INVENTORY'
UNLIMITED_WAREHOUSE = 'UNLIMITED_WAREHOUSE'  # todo develop it
RECEIPT_AND_REMITTANCE = 'RECEIPT_AND_REMITTANCE'
FACTOR_VISITOR = 'FACTOR_VISITOR'  # todo develop it
FACTOR_EXPENSES = 'FACTOR_EXPENSES'
CONSUMPTION_WARE_FACTOR = 'CONSUMPTION_WARE_FACTOR'
JOURNAL_REPORT = 'JOURNAL_REPORT'  # todo develop it
INCOME_STATEMENT_REPORT = 'INCOME_STATEMENT_REPORT'
DETAILED_INCOME_STATEMENT_REPORT = 'DETAILED_INCOME_STATEMENT_REPORT'
FEATURES = (
    (ACCOUNTS_CUD, 'امکان افزودن، ویرایش و حذف حساب در چهار سطح گروه، کل، معین، تفصیلی'),
    (UNLIMITED_SIDE_ACCOUNT, 'تعریف حساب بانک و صندوق نامحدود'),
    (UPDATE_ACCOUNT_IN_TREE, 'امکان  ویرایش حساب در چهار سطح گروه، کل، معین، تفصیلی در نمودار درختی'),

    (FLOAT_ACCOUNTS, 'امکان تعریف گروه و حساب شناور'),

    (BANK_TRANSFER_TRANSACTION, 'امکان ثبت پرداخت بین بانکی'),
    (GUARANTEE_DOCUMENTS, 'امکان ثبت اسناد ضمانتی'),
    (IMPREST_TRANSACTION, 'امکان ثبت تنخواه'),

    (PERMANENT_FINANCIAL_YEAR, 'امکان تعریف سال مالی دائمی'),
    (FIFO_INVENTORY, 'امکان انتخاب ارزیابی موجودی کالا به روش فایفو'),
    (UNLIMITED_WAREHOUSE, 'تعریف انبار به صورت نا محدود'),
    (RECEIPT_AND_REMITTANCE, 'امکان ثبت رسید و حواله'),
    (FACTOR_VISITOR, 'امکان انتخاب ویزیتور در فاکتور'),
    (FACTOR_EXPENSES, 'امکان ثبت هزینه های فاکتور'),
    (CONSUMPTION_WARE_FACTOR, 'امکان ثبت حواله کالای مصرفی'),

    (JOURNAL_REPORT, 'مشاهده گزارش دفتر روزنامه'),
    (INCOME_STATEMENT_REPORT, 'مشاهده گزارش سود و زیان'),
    (DETAILED_INCOME_STATEMENT_REPORT, 'مشاهده گزارش سود و زیان جامع '),
)

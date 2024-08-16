# Deploy notes
* comment lines 345 and 346 of `filterset.py` of `django_filters` package

# Notes

* accounts which has method in Account model can't have floatAccount

# Naming

### Models

* relation: floatAccountGroup
* fields: postal_code
* methods: get_new_code

### Serializers

Serializer of a model should be in one of the following formats:

* One serializer:
    * ModelSerializer
* Two Serializers:
    * ModelCreateUpdateSerializer
    * ModelListRetrieveSerializer
* Three or more:
    * ModelCreateSerializer
    * ModelUpdateSerializer
    * ModelListSerializer
    * ModelRetrieveSerializer
* There can be more serializers, like `ModelSimpleSerializer`

### Apps

* _* apps are add-on apps

### Default Accounts

* 1001 to 1999 ids are for dashtbashi module

# PDF Export Ubuntu Installation Commands

    wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.3/wkhtmltox-0.12.3_linux-generic-amd64.tar.xz 
    tar vxf wkhtmltox-0.12.3_linux-generic-amd64.tar.xz
    sudo cp wkhtmltox/bin/wk* /usr/local/bin/
    sudo apt-get install libxrender1

# Notes

## Sanad

* after creating / updating sanad you should call `update_values` method to updating `sanad.bed` & `sanad.bes`
* `clearSanad` make sanad an empty manual sanad and it can be used by user again

## Factor

* after creating / updating factor you should call `factor.sync` to sync factor items and factor expenses
* factor doesn't effect inventory until you definite it or call `DefiniteFactor.updateFactorInventory` (you should call that with `revert=True` before
  updating a factor)
* before updating a factor you should verify items by `factor.verify_items` method by passing items data and item ids to delete to it. Verifying means
  for each item check if it changed or not, if we have newer items on it's ware raise an exception
* ware inventory validation performs in `increase_inventory` & `decrease_inventory` of `WareInventory`

## Imprest

* you should add imprest moein account to imprest default accounts

## Helpers

* queryset
    * `add_sum`: adds sum for passed fields to `response.data.sum` for queryset and `response.data.page_sum` for page

* db
    * `bulk_create`: inserts multiple rows into database in one query
    * `queryset_iterator`: returns generator of queryset, useful to iterate large rows

* exports
    * `get_xlsx_response`: generates an xlsx download response from provided data, data structure is 2D array :)
    

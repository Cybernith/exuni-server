import datetime

from django.core.exceptions import ValidationError
from django.db import models, transaction

from main.models import Store
from server.store_configs import PACKING_STORE_ID


class ProductStoreInventory(models.Model):
    product = models.ForeignKey('products.Product', related_name='store_inventory', on_delete=models.SET_NULL, null=True)
    store = models.ForeignKey('main.Store', related_name='store_inventory', on_delete=models.SET_NULL, null=True)
    inventory = models.IntegerField(default=0)
    reserved_inventory = models.IntegerField(default=0)
    minimum_inventory = models.IntegerField(default=0)
    aisle = models.CharField(max_length=10, null=True)
    shelf_number = models.CharField(max_length=10, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def shelf_code(self):
        return f"{self.aisle or ''}-{self.shelf_number or ''}"

    @property
    def store_with_inventory(self):
        return self.product.store_inventory.exclude(id=PACKING_STORE_ID).filter(inventory__gt=0).first()

    def reduce_inventory_in_store(self, val, user=None):
        if not val > 0:
            raise ValidationError('reduce value most be positive number')
        if self.inventory < val:
            raise ValidationError(f"موجودی محصول {self.product.name} کافی نیست.")
        previous_quantity = self.inventory
        self.inventory -= val
        self.last_updated = datetime.datetime.now()
        self.save()

        ProductStoreInventoryHistory.objects.create(
            inventory=self,
            action=ProductStoreInventoryHistory.DECREASE,
            quantity=val,
            previous_quantity=previous_quantity,
            new_quantity=self.inventory,
            changed_by=user
        )

    def increase_inventory_in_store(self, val, user=None):
        if not val >= 0:
            raise ValidationError('increase value most be positive number')
        else:
            previous_quantity = self.inventory
            self.inventory += val
            self.last_updated = datetime.datetime.now()
            self.save()

            ProductStoreInventoryHistory.objects.create(
                inventory=self,
                action=ProductStoreInventoryHistory.INCREASE,
                quantity=val,
                previous_quantity=previous_quantity,
                new_quantity=self.inventory,
                changed_by=user
            )

    def handle_inventory_in_store(self, val, user=None):
        val = int(val)
        with transaction.atomic():
            previous_quantity = self.inventory
            self.inventory = val
            self.last_updated = datetime.datetime.now()
            self.save()

            ProductStoreInventoryHistory.objects.create(
                inventory=self,
                action=ProductStoreInventoryHistory.STORE_HANDLE,
                quantity=val,
                previous_quantity=previous_quantity,
                new_quantity=self.inventory,
                changed_by=user
            )

    def __str__(self):
        return ' موجودی {} در {} برابر {}'.format(self.product, self.store, self.inventory)

    class Meta:
        unique_together = ('store', 'product')
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['product']),
        ]


class ProductStoreInventoryHistory(models.Model):
    INCREASE = 'i'
    DECREASE = 'd'
    STORE_HANDLE = 's'

    ACTION_CHOICES = (
        (INCREASE, 'افزایش'),
        (DECREASE, 'کاهش'),
        (STORE_HANDLE, 'انبارگردانی'),
    )

    inventory = models.ForeignKey(ProductStoreInventory, related_name='history', on_delete=models.CASCADE)
    action = models.CharField(max_length=1, choices=ACTION_CHOICES)
    quantity = models.IntegerField()
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.get_action_display()} موجودی {self.inventory.product}   در {self.inventory.store} برابر {self.new_quantity}"


class ProductStoreInventoryHandle(models.Model):
    product = models.ForeignKey('products.Product', related_name='store_handle', on_delete=models.SET_NULL, null=True)
    store = models.ForeignKey('main.Store', related_name='store_handle', on_delete=models.SET_NULL, null=True)
    minimum_inventory = models.IntegerField(blank=True, null=True)
    inventory = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True)
    is_applied = models.BooleanField(default=False)

    def apply(self):
        if not self.product:
            raise ValidationError('product needed')
        if not self.store:
            raise ValidationError('store needed')

        store_inventory, created = ProductStoreInventory.objects.get_or_create(
            product=self.product,
            store=self.store,
        )

        if self.minimum_inventory:
            store_inventory.minimum_inventory = self.minimum_inventory
            store_inventory.save()

        if self.inventory:
            store_inventory.handle_inventory_in_store(val=self.inventory, user=self.changed_by)

        self.is_applied = True
        self.save()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'store'],
                name='unique_not_applied_product_store_inventory',
                condition=models.Q(is_applied=False)
            )
        ]


class ProductPackingInventoryHandle(models.Model):
    product = models.ForeignKey('products.Product', related_name='packing_handle', on_delete=models.SET_NULL, null=True)
    minimum_inventory = models.IntegerField(blank=True, null=True)
    inventory = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True)
    is_applied = models.BooleanField(default=False)

    def apply(self):
        if not self.product:
            raise ValidationError('product needed')

        store_inventory, created = ProductStoreInventory.objects.get_or_create(
            product=self.product,
            store=Store.objects.get(code=Store.PACKING),
        )

        if self.minimum_inventory:
            store_inventory.minimum_inventory = self.minimum_inventory
            store_inventory.save()

        if self.inventory:
            store_inventory.handle_inventory_in_store(val=self.inventory, user=self.changed_by)

        self.is_applied = True
        self.save()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                name='unique_not_applied_product_packing_inventory',
                condition=models.Q(is_applied=False)
            )
        ]


class ProductHandleChange(models.Model):
    product = models.ForeignKey('products.Product', related_name='change_handle', on_delete=models.SET_NULL, null=True)
    sixteen_digit_code = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=150, blank=True, null=True)
    postal_weight = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    width = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    aisle = models.CharField(max_length=10, null=True)
    shelf_number = models.CharField(max_length=10, null=True)
    expired_date = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True)
    is_applied = models.BooleanField(default=False)

    def apply(self):
        if not self.product:
            raise ValidationError('product needed')
        product = self.product
        if self.sixteen_digit_code:
            product.sixteen_digit_code = self.sixteen_digit_code
        if self.name:
            product.name = self.name
        if self.postal_weight:
            product.postal_weight = self.postal_weight
        if self.length:
            product.length = self.length
        if self.width:
            product.width = self.width
        if self.height:
            product.height = self.height
        if self.aisle:
            product.aisle = self.aisle
        if self.shelf_number:
            product.shelf_number = self.shelf_number
        if self.expired_date:
            product.expired_date = self.expired_date
        product.save()
        self.is_applied = True
        self.save()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                name='unique_not_applied_product_changes',
                condition=models.Q(is_applied=False)
            )
        ]

    def __str__(self):
        return self.product.name if self.product else None


class ShippingBox(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=150, blank=True, null=True)
    max_postal_weight = models.FloatField(blank=True, null=True)
    postal_weight = models.FloatField(blank=True, null=True)
    foam_weight = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    width = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    aisle = models.CharField(max_length=10, null=True)
    shelf_number = models.CharField(max_length=10, null=True)
    available = models.BooleanField(default=True)

    @staticmethod
    def describe_rotation(rotation_type: int) -> str:
        return {
            0: "ایستاده روی کف (بدون چرخش)",
            1: "خوابیده از پهلو روی عرض",
            2: "خوابیده از پشت روی طول",
            3: "خوابیده از پشت روی عرض",
            4: "خوابیده از پهلو روی طول",
            5: "خوابیده از بالا روی کف (برعکس)"
        }.get(rotation_type, "نامشخص")

    @property
    def weight(self):
        return (self.foam_weight or 0) + (self.postal_weight or 0)


class InventoryTransfer(models.Model):
    from_store = models.ForeignKey(ProductStoreInventory, on_delete=models.PROTECT, related_name="transfers_from")
    to_store = models.ForeignKey(ProductStoreInventory, on_delete=models.PROTECT, related_name="transfers_to")
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} from {self.from_store.store.name} to {self.to_store.store.name}"


class TransferToPackingRequest(models.Model):
    order = models.ForeignKey('shop.ShopOrder', on_delete=models.PROTECT, related_name="transfers_product_to_packing", blank=True, null=True)
    from_store = models.ForeignKey(ProductStoreInventory, on_delete=models.PROTECT, related_name="transfers_product_to_packing")
    quantity = models.PositiveIntegerField(default=0)
    product = models.ForeignKey('products.Product', related_name='transfers_product_to_packing', on_delete=models.SET_NULL, null=True)
    is_done = models.BooleanField(default=False)


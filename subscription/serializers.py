from rest_framework import serializers

from helpers.serializers import SModelSerializer
from subscription.models import Wallet, Transaction, FactorItem, Factor, Plan, Extension, CompanyExtension


class WalletSerializer(SModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ('balance', 'created_at', 'updated_at')


class TransactionListSerializer(SModelSerializer):
    wallet = WalletSerializer(read_only=True, many=False)

    class Meta:
        model = Transaction
        fields = '__all__'


class FactorItemCreateUpdateSerializer(SModelSerializer):
    class Meta:
        model = FactorItem
        fields = '__all__'
        read_only_fields = ('factor', 'created_at', 'updated_at')

    def validate(self, attrs):
        instance_type = attrs.pop('type')
        plan = attrs.pop('plan')
        if instance_type == FactorItem.BUY_PLAN and not plan.is_active:
            raise serializers.ValidationError("Plan is not active")
        return attrs


class FactorItemListSerializer(SModelSerializer):
    type_display = serializers.SerializerMethodField()

    def get_type_display(self, obj: FactorItem):
        return obj.get_type_display()

    class Meta:
        model = FactorItem
        fields = '__all__'
        read_only_fields = ('factor', 'created_at', 'updated_at')


class FactorListSerializer(SModelSerializer):
    added_value_tax = serializers.ReadOnlyField()
    final_amount = serializers.ReadOnlyField()
    after_discount_amount = serializers.ReadOnlyField()
    payable_amount = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_plan = serializers.CharField(source='company.plan.title', read_only=True)

    class Meta:
        model = Factor
        fields = '__all__'


class FactorRetrieveSerializer(SModelSerializer):
    items = FactorItemListSerializer(read_only=True, many=True)
    created_by = serializers.CharField(source='created_by.name')
    expired_at = serializers.SerializerMethodField()

    class Meta:
        model = Factor
        fields = '__all__'


class PlanListSerializer(SModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class ExtensionSerializer(SModelSerializer):
    title = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = Extension
        fields = '__all__'


class CompanyExtensionSerializer(SModelSerializer):
    extension = ExtensionSerializer(read_only=True)
    remain_days = serializers.ReadOnlyField()

    class Meta:
        model = CompanyExtension
        fields = '__all__'


class UserTurnoverSerializer(SModelSerializer):
    bed = serializers.SerializerMethodField()
    bes = serializers.SerializerMethodField()
    remain = serializers.SerializerMethodField()

    cumulative_bes = serializers.CharField()
    cumulative_bed = serializers.CharField()

    def get_bed(self, transaction: Transaction):
        if transaction.type == Transaction.DEPOSIT:
            return transaction.amount
        return 0

    def get_bes(self, transaction: Transaction):
        if transaction.type == Transaction.WITHDRAW:
            return transaction.amount
        return 0

    def get_remain(self, transaction: Transaction):
        return transaction.cumulative_bed - transaction.cumulative_bes

    class Meta:
        model = Transaction
        fields = '__all__'

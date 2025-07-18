from rest_framework import serializers

from helpers.functions import get_current_user
from issues.models import Issue, IssueStatusHistory
from users.serializers import UserSimpleSerializer


class IssueCreateSerializer(serializers.ModelSerializer):
    pic = serializers.ImageField(write_only=True, required=False, source='image')

    class Meta:
        model = Issue
        fields = [
            'title',
            'description',
            'issue_type',
            'severity',
            'pic',
        ]

        def create(self, validated_data):
            image_data = validated_data.pop('pic', None)
            issue = Issue.objects.create(**validated_data)

            if image_data:
                issue.image = image_data
                issue.save()

            return issue


class IssueStatusHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at',)
        model = IssueStatusHistory
        fields = '__all__'


class IssueSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    status_history = IssueStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at',)
        model = Issue
        fields = '__all__'


class IssueStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Issue.STATUS_CHOICES)

    def update(self, instance, validated_data):
        user = get_current_user()
        instance.change_status(validated_data['status'], user=user)
        return instance

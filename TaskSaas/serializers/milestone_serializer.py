
from rest_framework import serializers

from web.models import Milestone


class MilestoneSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    remark = serializers.CharField(read_only=True)
    date_range = serializers.CharField(read_only=True)
    create_datetime = serializers.DateTimeField(read_only=True)
    update_datetime = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Milestone
        fields = '__all__'
        read_only_fields = (
            "id",
            "name",
            "remark",
            "date_range",
            "create_datetime",
            "update_datetime",
        )

    def to_representation(self, instance):
        return super().to_representation(instance)
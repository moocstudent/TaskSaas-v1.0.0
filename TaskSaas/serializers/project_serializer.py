from rest_framework import serializers

from web.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    remark = serializers.CharField(read_only=True)
    creator_name = serializers.CharField(read_only=True)
    star = serializers.BooleanField(read_only=True)
    join_count = serializers.IntegerField(read_only=True)
    create_datetime = serializers.DateTimeField(read_only=True)
    color_display = serializers.CharField(read_only=True)
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = (
            "id",
            "name",
            "remark",
            "creator_name",
            "star",
            "join_count",
            "create_datetime",
            "color_display",
        )

    def to_representation(self, instance):
        color_display = instance.get_color_display()
        creator_name = instance.creator.username
        setattr(instance, "color_display", color_display)
        setattr(instance, "creator_name", creator_name)
        return super().to_representation(instance)

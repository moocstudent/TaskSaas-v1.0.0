from rest_framework import serializers

from web.models import Issues, IssuesReply


class IssuesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    issue_id = serializers.IntegerField(read_only=True)
    issue_type = serializers.IntegerField(read_only=True)
    # module = serializers.CharField(read_only=True)
    subject = serializers.CharField(read_only=True)
    desc = serializers.CharField(read_only=True)
    create_datetime = serializers.DateTimeField(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    avatars = serializers.ListField(read_only=True)

    class Meta:
        model = Issues
        fields = '__all__'
        read_only_fields = (
            "id",
            "issue_id",
            "issue_type",
            "subject",
            "desc",
            "create_datetime",
            "reply_count",
            "avatars",
        )

    def to_representation(self, instance):
        reply_count = IssuesReply.objects.filter(issues_id=instance.id).count()
        setattr(instance, "reply_count", reply_count)
        setattr(instance, "avatars", [{'url':instance.creator.wechat_avatar}])

        return super().to_representation(instance)

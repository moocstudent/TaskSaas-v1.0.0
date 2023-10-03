from rest_framework import serializers


class GitInfoRelationSerializer(serializers.Serializer):
    project_id = serializers.ManyRelatedField()
    git_project_id = serializers.IntegerField()

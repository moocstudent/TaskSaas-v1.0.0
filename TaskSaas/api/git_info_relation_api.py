from rest_framework.viewsets import ModelViewSet

from TaskSaas.filters.git_info_relation_filter import GitInfoRelationFilterSet
from TaskSaas.serializers.git_info_relation_serializer import GitInfoRelationSerializer
from web.models import GitInfoRelation


class GitInfoRelationApi(ModelViewSet):
    queryset = GitInfoRelation.objects.all()
    serializer_class = GitInfoRelationSerializer
    filterset_class = GitInfoRelationFilterSet
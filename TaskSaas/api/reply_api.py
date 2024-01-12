from django.db.models import Q
from django.http import JsonResponse

from web.models import IssuesReply

#删除评论
def del_reply(request, project_id):
    reply_id = request.POST.get('reply_id')
    issues_pk = request.POST.get('issues_pk')
    print('reply_id',reply_id)
    print('issues_pk',issues_pk)
    IssuesReply.objects.filter(Q(issues_id=issues_pk),Q(id=reply_id)).first().delete()
    return JsonResponse({'status':1})

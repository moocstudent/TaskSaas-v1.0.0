from django.http import JsonResponse

from web.models import Collect, Issues


def make_collect(request,project_id):
    issue_pk = request.POST.get('issue_pk')
    issue = Issues.objects.filter(id=issue_pk).first()
    issue_id = request.POST.get('issue_id')
    curr_user = request.web.user
    coll = Collect(project_id=project_id,creator=curr_user,issues=issue,
            link='/manage/{}/issues/detail/{}/'.format(project_id,issue_id),
            title=issue.subject)
    coll.save()
    return JsonResponse({'status':1})

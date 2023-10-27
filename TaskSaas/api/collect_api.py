from django.http import JsonResponse

from web.models import Collect, Issues, Wiki, FileRepository


def make_collect(request,project_id):
    issue_pk = request.POST.get('issue_pk')
    issue = Issues.objects.filter(id=issue_pk).first()
    issue_id = request.POST.get('issue_id')
    curr_user = request.web.user
    coll = Collect(project_id=project_id,creator=curr_user,issues=issue,
            link='/manage/{}/issues/detail/{}/'.format(project_id,issue_id),
            title=issue.subject,type=1)
    coll.save()
    return JsonResponse({'status':1})

def wiki_collect(request,project_id):
    wiki_pk = request.POST.get('wiki_pk')
    wiki = Wiki.objects.filter(id=wiki_pk).first()
    curr_user = request.web.user
    coll = Collect(project_id=project_id,creator=curr_user,wiki=wiki,
            link='/manage/{}/wiki/?wiki_id={}'.format(project_id,wiki_pk),
            title=wiki.title,type=2)
    coll.save()
    return JsonResponse({'status':1})

def file_collect(request,project_id):
    file_pk = request.POST.get('file_pk')
    file_repo = FileRepository.objects.filter(id=file_pk).first()
    curr_user = request.web.user
    coll = Collect(project_id=project_id,creator=curr_user,file=file_repo,
            link='/manage/{}/file/download/{}/'.format(project_id,file_pk),
            title=file_repo.name,type=3)
    coll.save()
    return JsonResponse({'status':1})

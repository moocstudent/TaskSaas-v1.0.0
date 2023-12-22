from django.http import JsonResponse

from web.models import ProjectUser


def remove_user_from_project(request,project_id):
    remove_user_id = request.POST.get('remove_user_id')
    print('remove_user_id',remove_user_id)
    user_will_remove = ProjectUser.objects.filter(user__id=remove_user_id,project=request.web.project).first()
    print('user_will_remove',user_will_remove)
    if user_will_remove:
        user_will_remove.delete()
    return JsonResponse({'status':1})
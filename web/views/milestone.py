from django.http import JsonResponse
from django.shortcuts import render


def milestone(request, project_id):
    return render(request, 'web/milestone.html', {})

def milestone_add(request,project_id):
    milestone_name = request.POST.get('milestone_name')
    milestone_remark = request.POST.get('milestone_remark')
    milestone_date_range = request.POST.get('milestone_date_range')
    print('milestone_name',milestone_name)
    print('milestone_remark',milestone_remark)
    print('milestone_date_range',milestone_date_range)
    return JsonResponse({'status':1})
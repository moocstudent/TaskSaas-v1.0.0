import json

from django.http import JsonResponse
from django.shortcuts import render

from TaskSaas.serializers.milestone_serializer import MilestoneSerializer
from web.models import Milestone, Project, Issues


def milestone(request, project_id):
    mss = Milestone.objects.filter(project_id=project_id).order_by('create_datetime')
    mss_json = MilestoneSerializer(mss,many=True)
    context = {
        'ms_list': json.dumps(mss_json.data)
    }
    return render(request, 'web/milestone.html', context)

def milestone_add_or_update(request,project_id):
    milestone_id = request.POST.get('milestone_id')
    milestone_name = request.POST.get('milestone_name')
    milestone_remark = request.POST.get('milestone_remark')
    milestone_date_range = request.POST.get('milestone_date_range')
    sync_issues = request.POST.get('sync_issues')
    is_sync_issues = sync_issues.lower() == 'true'

    if milestone_id:
        # update
        ms_update = Milestone.objects.filter(id=milestone_id).first()
        ms_update.name = milestone_name
        ms_update.remark = milestone_remark
        ms_update.date_range = milestone_date_range
        if is_sync_issues:
            ms_dates = milestone_date_range.split(' - ')
            ms_issues = Issues.objects.filter(project_id=project_id,create_datetime__range=(ms_dates[0], ms_dates[1]))
            for i in ms_issues:
                i.milestone = ms_update
                i.save()
            ms_update.sync_count = len(ms_issues)
        ms_update.save()
            # 将这些issues更新milestone到当前milestone
    else:
        #add
        project = Project.objects.filter(id=project_id).first()
        ms_add = Milestone(project=project,name=milestone_name,remark=milestone_remark,
            date_range=milestone_date_range)
        if is_sync_issues:
            ms_dates = milestone_date_range.split(' - ')
            ms_issues = Issues.objects.filter(project_id=project_id,create_datetime__range=(ms_dates[0], ms_dates[1]))
            print('ms_issues len ', len(ms_issues))
            for i in ms_issues:
                i.milestone = ms_add
                i.save()
            ms_add.sync_count = len(ms_issues)
        ms_add.save()
            # 将这些issues更新milestone到当前milestone
    return JsonResponse({'status':1})

def milestone_del(request,project_id):
    milestone_id = request.POST.get('milestone_id')
    ms = Milestone.objects.filter(project_id=project_id,id=milestone_id).first()
    if ms:
        ms.delete()
        issues_ms = Issues.objects.filter(project_id=project_id,milestone_id=milestone_id)
        for i in issues_ms:
            i.milestone = None
            i.save()
    return JsonResponse({'status': 1})
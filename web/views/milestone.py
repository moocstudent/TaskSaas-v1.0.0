import json

from django.http import JsonResponse
from django.shortcuts import render

from TaskSaas.serializers.milestone_serializer import MilestoneSerializer
from web.models import Milestone, Project


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
    if milestone_id:
        # update
        ms_update = Milestone.objects.filter(id=milestone_id).first()
        ms_update.name = milestone_name
        ms_update.remark = milestone_remark
        ms_update.date_range = milestone_date_range
        ms_update.save()
    else:
        #add
        project = Project.objects.filter(id=project_id).first()
        ms_add = Milestone(project=project,name=milestone_name,remark=milestone_remark,
            date_range=milestone_date_range)
        ms_add.save()
    return JsonResponse({'status':1})

def milestone_del(request,project_id):
    milestone_id = request.POST.get('milestone_id')
    ms = Milestone.objects.filter(project_id=project_id,id=milestone_id).first()
    ms.delete()
    return JsonResponse({'status': 1})
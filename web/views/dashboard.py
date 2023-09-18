from django.shortcuts import render
import collections
from web import models
from django.db.models import Count


def dashboard(request, project_id):
    """概览"""
    # 项目状态
    status_dict = collections.OrderedDict()

    echarts_data = []

    for key, text in sorted(models.Issues.status_choices):
        status_dict[key] = {'text': text, 'count': 0}

    issues_data = models.Issues.objects.filter(project_id=project_id).values('status').annotate(ct=Count('id'))

    print('issues_data',issues_data)
    for item in issues_data:
        status_dict[item['status']]['count'] = item['ct']

    for item in sorted(status_dict.items()):
        # print('key',d)
        print('item',)
        print('item count',item[1]['count'])
        echarts_data.insert(item[0]-1,item[1]['count'])
        # print('count',d['count'])
        # echarts_data[d['count']]

    join_user = models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__username')

    print('join_user',join_user)
    print('echarts_data',echarts_data)
    top_ten = models.Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by('-id')[0:10]

    context = {
        'status_dict': status_dict,
        'join_user': join_user,
        'top_ten': top_ten,
        'echarts_data': echarts_data
    }

    return render(request, 'web/dashboard.html', context)

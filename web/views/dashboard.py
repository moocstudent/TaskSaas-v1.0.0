from django.shortcuts import render
import collections
from web import models
from django.db.models import Count


def dashboard(request, project_id):
    """概览"""
    # 项目状态
    status_dict = collections.OrderedDict()
    status_choices = []
    issues_types_dict = []

    echarts_data = []
    tasks_count = []
    funcs_count = []
    bugs_count = []
    demand_count = []
    issues_filter = models.Issues.objects.filter(project_id=project_id)
    issues_types = issues_filter.values('issues_type').annotate(count=Count('issues_type')).values('issues_type')
    print(issues_types)
    # keys = []
    index = 0
    for key, text in sorted(models.Issues.status_choices):
        status_dict[key] = {'text': text, 'count': 0}
        status_choices.append(key)
        if len(issues_types) > 0:
            tasks_count.insert(index, issues_filter.filter(issues_type=issues_types[0]['issues_type'],
                                                           status=key).count())
        if len(issues_types) > 1:
            funcs_count.insert(index, issues_filter.filter(issues_type=issues_types[1]['issues_type'],
                                                           status=key).count())
        if len(issues_types) > 2:
            bugs_count.insert(index, issues_filter.filter(issues_type=issues_types[2]['issues_type'],
                                                          status=key).count())
        if len(issues_types) > 3:
            demand_count.insert(index, issues_filter.filter(issues_type=issues_types[3]['issues_type'],
                                                            status=key).count())
        # keys.index(index,key)
        index += 1

    issues_data = issues_filter.values('status').annotate(ct=Count('id'))

    print('issues_data', issues_data)
    for item in issues_data:
        status_dict[item['status']]['count'] = item['ct']

    for item in sorted(status_dict.items()):
        echarts_data.insert(item[0] - 1, item[1]['count'])
        # print('count',d['count'])
        # echarts_data[d['count']]
    join_user = models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__username')

    print('join_user', join_user)
    print('echarts_data', echarts_data)
    top_ten = models.Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by('-id')[0:10]
    tasks_count.reverse()
    funcs_count.reverse()
    bugs_count.reverse()
    demand_count.reverse()
    if len(issues_types) > 0:
        issues_types_dict.append(issues_types[0]['issues_type'])
    if len(issues_types) > 1:
        issues_types_dict.append(issues_types[1]['issues_type'])
    if len(issues_types) > 2:
        issues_types_dict.append(issues_types[2]['issues_type'])
    if len(issues_types) > 3:
        issues_types_dict.append(issues_types[3]['issues_type'])
    context = {
        'status_dict': status_dict,
        'join_user': join_user,
        'top_ten': top_ten,
        'echarts_data': echarts_data,
        'tasks_count': tasks_count,
        'funcs_count': funcs_count,
        'bugs_count': bugs_count,
        'demand_count': demand_count,
        'issues_types': issues_types_dict,
        'status_choices': status_choices
    }

    return render(request, 'web/dashboard.html', context)

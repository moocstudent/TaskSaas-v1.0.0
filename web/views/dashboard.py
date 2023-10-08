import json
import operator

from django.core.cache import cache
from django.shortcuts import render
import collections
from web import models
from django.db.models import Count, Q, F


def dashboard(request, project_id):
    print('dashboard pid ',request.web.project.id)
    # print(request.web.project.id)
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
    print('issues_filter size bef filter ', len(issues_filter))
    trigger = cache.get('mytaskTrigger'+str(request.web.user.id)+'_'+str(request.web.project.id),'off')
    if trigger == 'on':
        issues_filter=issues_filter.filter(Q(assign=request.web.user)|Q(attention=request.web.user)|Q(creator=request.web.user)).distinct()
        print('issues_filter size aft filter ', len(issues_filter))
    main_legend_trigger = cache.get('mainLegendTrigger'+str(request.web.user.id)+'_'+str(request.web.project.id),'任务,功能,Bug,需求确认')
    types = []
    type_ids = ''
    all_type_ids = ''
    if main_legend_trigger is not None:
        types = (list(main_legend_trigger.split(',')))
        issues_filter=issues_filter.filter(issues_type__title__in=types)

    issues_types = models.IssuesType.objects.filter(project_id=project_id)
    for i in issues_types.values('id'):
        all_type_ids += str(i['id'])+','
    all_type_ids =  all_type_ids[0:-1]
    print('issues_types',issues_types)
    print('myis size', len(issues_filter))
    for i in list(issues_types.filter(title__in=types).values('id')):
        type_ids+=str(i['id'])+','
    type_ids=type_ids[0:-1]
    # print('issues_types dict',dict(issues_types))

    # keys = []
    index = 0
    for key, text in sorted(models.Issues.status_choices):
        status_dict[key] = {'text': text, 'count': 0}
        status_choices.append(key)
        if len(issues_types) > 0:
            tasks_count.insert(index, issues_filter.filter(issues_type=issues_types[0],
                                                           status=key).count())
        if len(issues_types) > 1:
            funcs_count.insert(index, issues_filter.filter(issues_type=issues_types[1],
                                                           status=key).count())
        if len(issues_types) > 2:
            bugs_count.insert(index, issues_filter.filter(issues_type=issues_types[2],
                                                          status=key).count())
        if len(issues_types) > 3:
            demand_count.insert(index, issues_filter.filter(issues_type=issues_types[3],
                                                            status=key).count())
        # keys.index(index,key)
        index += 1
    print('issues size bef ct ', len(issues_filter))
    n = 0
    for i in issues_filter:
        print('i>>>>',i.status)
        if i.status ==1 :
            n+=1
    print('n>>>',n)
    issues_data = issues_filter.values('status').annotate(ct=Count('id',distinct=True))

    print('issues_data', issues_data)
    for item in issues_data:
        print("item['status'] {} ct:{}".format(item['status'],item['ct']))
        status_dict[item['status']]['count'] = item['ct']

    for item in sorted(status_dict.items()):
        echarts_data.insert(item[0] - 1, item[1]['count'])
        # print('count',d['count'])
        # echarts_data[d['count']]
    join_user = models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__username')

    print('join_user', join_user)
    print('echarts_data', echarts_data)
    # top ten 结合查询 新建了哪些项目？谁分配了工作？谁进行了修改/回复？

    top_ten = models.Issues.objects.filter(project_id=project_id).order_by('-latest_update_datetime','-create_datetime')
    if trigger == 'on':
        print("trigger == 'on':")
        print(request.web.user)
        top_ten=top_ten.filter(Q(assign=request.web.user)|Q(attention=request.web.user)
                             |Q(creator=request.web.user))
    print('tt size', len(top_ten))
    top_ten_reply = models.IssuesReply.objects.filter(issues__project_id=project_id).exclude(content__startswith='指派更新').order_by('-create_datetime')
    if trigger == 'on':
        print("trigger == 'on':")
        print(request.web.user)
        top_ten_reply=top_ten_reply.filter(Q(issues__assign=request.web.user)|Q(issues__attention=request.web.user)
                             |Q(issues__creator=request.web.user))
    print('tr size', len(top_ten_reply))
    top_ten_dict = collections.OrderedDict()
    for t in top_ten:
        is_assign = 0
        assign = None
        if t.assign_id:
            is_assign=1
            assign = t.assign.username
        top_ten_dict[t.latest_update_datetime] = {'is_assign': is_assign, 'is_fresh': 1,'is_reply':0,
                                                  'creator':t.creator.username,'assign':assign,
                                                  'desc':t.subject,'reply_type':0,
                                                  'title': t.subject,
                                                  'issue_id':t.issue_id,'id':t.id}
    for tr in top_ten_reply:
        top_ten_dict[tr.create_datetime] = {'is_assign': 0, 'is_fresh': 0,'is_reply':1,
                                                  'creator':tr.creator.username,'assign':tr.reply_id,
                                                  'desc': tr.content,'reply_type':tr.reply_type,
                                                  'title':tr.issues.subject,
                                                  'issue_id':t.issue_id,'id':tr.issues_id}

    top_ten_re_sorted = dict(sorted(top_ten_dict.items(), key=operator.itemgetter(0), reverse=True))

    tasks_count.reverse()
    funcs_count.reverse()
    bugs_count.reverse()
    demand_count.reverse()
    if len(issues_types) > 0:
        issues_types_dict.append(issues_types[0].title)
    if len(issues_types) > 1:
        issues_types_dict.append(issues_types[1].title)
    if len(issues_types) > 2:
        issues_types_dict.append(issues_types[2].title)
    if len(issues_types) > 3:
        issues_types_dict.append(issues_types[3].title)

    context = {
        'status_dict': status_dict,
        'join_user': join_user,
        'top_ten': top_ten_re_sorted,
        'echarts_data': echarts_data,
        'tasks_count': tasks_count,
        'funcs_count': funcs_count,
        'bugs_count': bugs_count,
        'demand_count': demand_count,
        'issues_types': issues_types_dict,
        'status_choices': status_choices,
        'type_ids':type_ids,
        'all_type_ids':all_type_ids
    }

    return render(request, 'web/dashboard.html', context)

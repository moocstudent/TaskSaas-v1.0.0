import json

import requests
from channels.auth import login
from django.core.cache import cache
from django.db.models import Q, Count, Max, Min
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from TaskSaasAPP import date_util
from TaskSaasAPP.date_util import get_every_day, get_today, get_last_week_since_today
from utils.pagination import Pagination
from web import models


def statistics(request, project_id):
    return render(request, 'web/statistics.html')

# todo commit具体信息 当点击页面commit message时弹出详情
def git_commit(request,git_project_id,commit_hash):
    # 'http://39.99.215.169:8099/api/v4/projects/4/repository/commits/56b02ef687f66e4e375effbd95c3b2d5776dc595'
    git_host = "http://39.99.215.169:8099"
    # project = models.Project.objects.filter(id=project_id).first()
    print(request.web.project)
    relation_git_infos = models.GitInfoRelation.objects.filter(project_id=request.web.project).order_by('create_datetime')

    return HttpResponse()

def git(request, project_id):
    project = models.Project.objects.filter(id=project_id).first()
    relation_git_infos = models.GitInfoRelation.objects.filter(project_id=project_id).order_by('create_datetime')
    relation_git_ids = []
    if relation_git_infos:
        for v in relation_git_infos:
            relation_git_ids.append(v.git_project_id)

    git_host = "http://39.99.215.169:8099"
    task_project_name = project.name
    project_infos = []
    if relation_git_ids:
        for git_info in relation_git_infos:
            try:
                git_project_id = str(git_info.git_project_id)
                project_private_token = git_info.git_access_token
                members_url = git_host + "/api/v4/projects/" + git_project_id + "/members?private_token=" + project_private_token
                project_info_url = git_host + "/api/v4/projects/" + git_project_id + "?private_token=" + project_private_token
                project_events_url = git_host + "/api/v4/projects/" + git_project_id + "/events?private_token=" + project_private_token
                project_branches_url = git_host + "/api/v4/projects/" + git_project_id + "/repository/branches?private_token=" + project_private_token
                members_response = json.loads(requests.get(members_url).text)
                project_info_response = json.loads(requests.get(project_info_url).text)
                project_events_response = json.loads(requests.get(project_events_url).text)
                project_branches_response = json.loads(requests.get(project_branches_url).text)
                commit_base_url = project_info_response['web_url']
                project_info_response['desc'] = git_info.desc
                for br in project_branches_response:
                    br['graph_url'] = br['web_url'].replace('tree','network')

                for br in project_events_response:
                    push_data = br.get('push_data')
                    if push_data is not None:
                        commit_from = push_data.get('commit_from')
                        commit_to = push_data.get('commit_to')
                        if commit_from is not None:
                            br['commit_from_url'] = commit_base_url+'/-/commit/'+commit_from
                        if commit_to is not None:
                            br['commit_to_url'] = commit_base_url + '/-/commit/' + commit_to

                members = list(
                    filter(lambda i: not ('bot_' in i['username'] and 'project_' in i['username']), members_response))
                one_project_info = {
                    'git_project_id': git_project_id,
                    'members': members,
                    'member_size': len(members),
                    'project_info': project_info_response,
                    'project_events': project_events_response,
                    'project_branches': project_branches_response
                }
                project_infos.append(one_project_info)
            except Exception as e:
                print('get git_project error',e)
                continue
    context = {
        'task_project_name': task_project_name,
        'git_project_infos': project_infos,
    }
    return render(request, 'web/git.html', context=context)


def workbench(request, project_id):
    print('workbench pid ',request.web.project.id)
    # 根据优先级排序
    ordering = "FIELD(`priority`, 'danger','warning','success')"
    legendTriggrer = cache.get('myechartlegendTrigger'+str(request.web.user.id)+'_'+str(request.web.project.id),'1257')
    attention_trigger = cache.get('myAttentionTrigger'+str(request.web.user.id)+'_'+str(request.web.project.id),'off')
    people_involve_q = Q(assign=request.web.user)| Q(creator=request.web.user)
    if attention_trigger == 'on':
        people_involve_q = people_involve_q | Q(attention=request.web.user)
    my_issues_set = models.Issues.objects.filter(Q(project_id=project_id) & (people_involve_q)
                                                 & Q(status__in=(list(legendTriggrer)))).extra(
        select={'ordering': ordering}, order_by=('ordering', 'id',)).distinct()
    day_trigger = cache.get('mydayTrigger'+str(request.web.user.id)+'_'+str(request.web.project.id),'day7')
    my_issues_set = filter_by_day(my_issues_set, day_trigger)
    # elif day_trigger == 'day0':

    print('total size', len(my_issues_set))
    danger_count = my_issues_set.filter(priority='danger').count()
    warning_count = my_issues_set.filter(priority='warning').count()
    success_count = my_issues_set.filter(priority='success').count()
    todo_count = len(my_issues_set)
    min_date = None
    if my_issues_set:
        max_dates = my_issues_set.aggregate(cd=Min('create_datetime'), lud=Min('latest_update_datetime'))
        for k, v in max_dates.items():
            if min_date:
                if v < min_date:
                    min_date = v
                    continue
            min_date = v
    days = []
    print('min_date',min_date)
    if min_date and day_trigger!='day1':
        days = get_every_day(day_trigger, min_date, '%Y-%m-%d')
    elif day_trigger=='day1':
        days = get_every_day(day_trigger, date_util.get_today(), '%Y-%m-%d')
    print('days', days)

    fresh_counts = ['新建']
    handle_counts = ['处理中']
    resolve_counts = ['已解决']
    wait_counts = ['待反馈']
    reopen_counts = ['重新打开']
    for d in days:
        fresh_counts.append(my_issues_set.filter(Q(status=1) & (Q(create_datetime__date=d) |
                                                                Q(latest_update_datetime__date=d))).count())
        handle_counts.append(my_issues_set.filter(Q(status=2) & (Q(create_datetime__date=d) |
                                                                 Q(latest_update_datetime__date=d))).count())
        resolve_counts.append(my_issues_set.filter(Q(status=3) & (Q(create_datetime__date=d) |
                                                                  Q(latest_update_datetime__date=d))).count())
        wait_counts.append(my_issues_set.filter(Q(status=5) & (Q(create_datetime__date=d) |
                                                               Q(latest_update_datetime__date=d))).count())
        reopen_counts.append(my_issues_set.filter(Q(status=7) & (Q(create_datetime__date=d) |
                                                                 Q(latest_update_datetime__date=d))).count())

    my_issues_set.filter()
    fresh_count = my_issues_set.filter(status=1).count()
    print('fresh c', fresh_count)
    handle_count = my_issues_set.filter(status=2).count()
    resolve_count = my_issues_set.filter(status=3).count()
    wait_count = my_issues_set.filter(status=5).count()
    reopen_count = my_issues_set.filter(status=7).count()

    current_page = request.GET.get('page')
    pagesize = my_issues_set.count() / 3
    if int(pagesize) != pagesize:
        pagesize = int(pagesize) + 1
    if current_page and int(current_page) > pagesize:
        current_page = 1
    page_object = Pagination(
        current_page=current_page,
        all_count=my_issues_set.count(),
        base_url=request.path_info,
        query_params=request.GET,
        per_page=3
    )
    issues_object_list = my_issues_set[page_object.start:page_object.end]

    print('myis size', len(issues_object_list))
    count_data = {
        'danger': danger_count,
        'warning': warning_count,
        'success': success_count,
    }

    # c = login(request, request.web.user)
    context = {
        'issues_object_list': issues_object_list,
        'page_html': page_object.page_html(),
        'count_data': count_data,
        'days': days,
        'fresh_counts': fresh_counts,
        'handle_counts': handle_counts,
        'resolve_counts': resolve_counts,
        'wait_counts': wait_counts,
        'reopen_counts': reopen_counts,
    }
    return render(request, 'web/workbench.html', context)


# deprecated
def workbench_json(request):
    print('workbench_json')
    project_id = request.POST.get('project_id')
    # 根据优先级排序
    ordering = "FIELD(`priority`, 'danger','warning','success')"
    legendTriggrer = cache.get('myechartlegendTrigger'+str(request.web.user.id)+'_'+str(request.web.project.id),'1257')
    my_issues_set = models.Issues.objects.filter(Q(project_id=project_id) & (Q(assign=request.web.user)
                                                                             | Q(attention=request.web.user)
                                                                             | Q(creator=request.web.user))
                                                 & Q(status__in=(list(legendTriggrer)))).extra(
        select={'ordering': ordering}, order_by=('ordering', 'id',))
    day_trigger = cache.get('mydayTrigger'+str(request.web.user.id)+'_'+str(request.web.project.id),'day7')
    my_issues_set = filter_by_day(my_issues_set, day_trigger)
    # elif day_trigger == 'day0':

    print('total size', len(my_issues_set))
    danger_count = my_issues_set.filter(priority='danger').count()
    warning_count = my_issues_set.filter(priority='warning').count()
    success_count = my_issues_set.filter(priority='success').count()
    todo_count = len(my_issues_set)
    min_date = None
    if day_trigger == 'day0':
        max_dates = my_issues_set.aggregate(cd=Min('create_datetime'), lud=Min('latest_update_datetime'))
        for k, v in max_dates.items():
            if min_date:
                if v < min_date:
                    min_date = v
                    continue
            min_date = v
    days = []
    if min_date:
        days = get_every_day(day_trigger, min_date, '%Y-%m-%d')
    print('days', days)

    fresh_counts = ['新建']
    handle_counts = ['处理中']
    resolve_counts = ['已解决']
    wait_counts = ['待反馈']
    reopen_counts = ['重新打开']
    for d in days:
        fresh_counts.append(my_issues_set.filter(Q(status=1) & (Q(create_datetime__date=d) |
                                                                Q(latest_update_datetime__date=d))).count())
        handle_counts.append(my_issues_set.filter(Q(status=2) & (Q(create_datetime__date=d) |
                                                                 Q(latest_update_datetime__date=d))).count())
        resolve_counts.append(my_issues_set.filter(Q(status=3) & (Q(create_datetime__date=d) |
                                                                  Q(latest_update_datetime__date=d))).count())
        wait_counts.append(my_issues_set.filter(Q(status=5) & (Q(create_datetime__date=d) |
                                                               Q(latest_update_datetime__date=d))).count())
        reopen_counts.append(my_issues_set.filter(Q(status=7) & (Q(create_datetime__date=d) |
                                                                 Q(latest_update_datetime__date=d))).count())

    my_issues_set.filter()
    fresh_count = my_issues_set.filter(status=1).count()
    print('fresh c', fresh_count)
    handle_count = my_issues_set.filter(status=2).count()
    resolve_count = my_issues_set.filter(status=3).count()
    wait_count = my_issues_set.filter(status=5).count()
    reopen_count = my_issues_set.filter(status=7).count()

    current_page = request.GET.get('page')
    pagesize = my_issues_set.count() / 3
    if int(pagesize) != pagesize:
        pagesize = int(pagesize) + 1
    if current_page and int(current_page) > pagesize:
        current_page = 1
    page_object = Pagination(
        current_page=current_page,
        all_count=my_issues_set.count(),
        base_url=request.path_info,
        query_params=request.GET,
        per_page=3
    )
    issues_object_list = my_issues_set[page_object.start:page_object.end]

    print('myis size', len(issues_object_list))
    count_data = {
        'danger': danger_count,
        'warning': warning_count,
        'success': success_count,
    }
    context = {
        'issues_object_list': issues_object_list,
        'page_html': page_object.page_html(),
        'count_data': count_data,
        'days': days,
        'fresh_counts': fresh_counts,
        'handle_counts': handle_counts,
        'resolve_counts': resolve_counts,
        'wait_counts': wait_counts,
        'reopen_counts': reopen_counts,
    }
    return HttpResponse(1)


def filter_by_day(my_issues_set, day_trigger):
    if day_trigger == 'day1':
        return my_issues_set.filter(Q(create_datetime__date=date_util.get_today()) |
                                    Q(latest_update_datetime__date=date_util.get_today()))
    elif day_trigger == 'day7':
        return my_issues_set.filter(Q(create_datetime__date__range=(date_util.get_last_week_since_today(),
                                                                    date_util.get_today())) |
                                    Q(latest_update_datetime__date__range=(
                                        date_util.get_last_week_since_today(),
                                        date_util.get_today())))
    elif day_trigger == 'day30':
        return my_issues_set.filter(
            (Q(create_datetime__year=date_util.get_year()) & Q(create_datetime__month=date_util.get_month())) |
            (Q(latest_update_datetime__year=date_util.get_year()) & Q(
                latest_update_datetime__month=date_util.get_month())))
    else:
        print('day0 no filtered')
        return my_issues_set


def tool(request,project_id):
    context = {
    }
    return render(request, 'web/tool.html', context)


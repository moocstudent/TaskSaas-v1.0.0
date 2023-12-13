import collections
import json
from datetime import datetime

import requests
from django.core.cache import cache
from django.db.models import Q, Min
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from TaskSaas.result.result import APIResult
from TaskSaasAPP import date_util
from TaskSaasAPP.date_util import get_every_day
from TaskSaasAPP.type_util import isint
from utils.pagination import Pagination
from web import models
from web.models import Collect, Issues, UserInfo, WorkRecord, Project


def statistics(request, project_id):
    the_proj_issues = Issues.objects.filter(project_id=project_id)
    assign_count = the_proj_issues.filter(assign_id=request.web.user.id).count()
    attention_count = the_proj_issues.filter(attention__id__in=[request.web.user.id]).count()
    creation_count = the_proj_issues.filter(creator=request.web.user.id).count()
    resolve_count = the_proj_issues.filter(status=3, assign_id=request.web.user.id).count()
    context = {
        'assign_count': assign_count,
        'attention_count': attention_count,
        'resolve_count': resolve_count,
        'creation_count': creation_count
    }
    return render(request, 'web/statistics.html', context)


def work_record(request,project_id):
    content = request.POST.get("content")
    calendar_day = request.POST.get("calendar_day")
    work_record = WorkRecord()
    work_record.user= request.web.user
    work_record.project = request.web.project
    work_record.content = content
    work_record.calendar_day = calendar_day
    calendar_day_date = datetime.strptime(calendar_day, "%Y-%m-%d")
    work_record.calendar_day_date=calendar_day_date
    work_record.save()
    return JsonResponse({'status':1})

def work_record_update(request,project_id):
    id = request.POST.get("id")
    content = request.POST.get("content")
    work_record= WorkRecord.objects.filter(id=id).first()
    if work_record:
        if work_record.content == content:
            return JsonResponse({'status': 1,'msg':'not changed'})
        else:
            work_record.id = id
            work_record.content = content
            work_record.save()
            return JsonResponse({'status': 1, 'msg': 'changed'})
    return JsonResponse({'status': 0, 'msg': 'can not find record'})

def find_work_record(request,project_id):
    print('find work record')
    calendar_day = request.GET.get("calendar_day")
    work_record = WorkRecord.objects.filter(user=request.web.user,project=request.web.project,calendar_day=calendar_day).first()
    print('work record:',work_record)
    if work_record:
        return JsonResponse({'status':1,'record':{'id':work_record.id,'content':work_record.content,
                                                  'create_time':work_record.create_datetime,'update_time':work_record.update_datetime,
                                                  'day':work_record.calendar_day}})
    return JsonResponse({'status': 0, 'record': None})


def work_record_list(request,project_id):
    # all_object_list = (list(my_issues_set.values_list("issue_id", "subject")))
    # all_object_list = json.dumps(all_object_list)
    year = request.GET.get("year")
    print(year)
    print('project_id at work record list:',project_id)
    project = None
    if request.web.project:
        project = request.web.project
    else:
        project = Project.objects.filter(id=project_id).first()
    work_records = WorkRecord.objects.filter(user=request.web.user, project=project,
                                               calendar_day__startswith=year).order_by('calendar_day')
    print('work_records',work_records)
    api_result = APIResult(work_records.values())
    return JsonResponse(api_result,safe=False)



# todo commit具体信息 当点击页面commit message时弹出详情
def git_commit(request, git_project_id, commit_hash):
    # 'http://39.99.215.169:8099/api/v4/projects/4/repository/commits/56b02ef687f66e4e375effbd95c3b2d5776dc595'
    git_host = "http://39.99.215.169:8099"
    # project = models.Project.objects.filter(id=project_id).first()
    print(request.web.project)
    relation_git_infos = models.GitInfoRelation.objects.filter(project_id=request.web.project).order_by(
        'create_datetime')

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
                    br['graph_url'] = br['web_url'].replace('tree', 'network')

                for br in project_events_response:
                    push_data = br.get('push_data')
                    if push_data is not None:
                        commit_from = push_data.get('commit_from')
                        commit_to = push_data.get('commit_to')
                        if commit_from is not None:
                            br['commit_from_url'] = commit_base_url + '/-/commit/' + commit_from
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
                print('get git_project error', e)
                continue
    context = {
        'task_project_name': task_project_name,
        'git_project_infos': project_infos,
    }
    return render(request, 'web/git.html', context=context)


def workbench(request, project_id):
    q = request.GET.get('q')
    print('workbench pid ', request.web.project.id)
    # 根据优先级排序
    ordering = "FIELD(`priority`, 'danger','warning','success')"
    legendTriggrer = cache.get('myechartlegendTrigger' + str(request.web.user.id) + '_' + str(request.web.project.id),
                               '1257')
    attention_trigger = cache.get('myAttentionTrigger' + str(request.web.user.id) + '_' + str(request.web.project.id),
                                  'off')
    people_involve_q = Q(assign=request.web.user) | Q(creator=request.web.user)
    if attention_trigger == 'on':
        people_involve_q = people_involve_q | Q(attention=request.web.user)
    my_issues_set = models.Issues.objects.filter(Q(project_id=project_id) & (people_involve_q)
                                                 & Q(status__in=(list(legendTriggrer)))).extra(
        select={'ordering': ordering}, order_by=('ordering', 'id',)).distinct()
    if q:
        qq = None
        if isint(q):
            qq = Q(issue_id=q) | Q(subject__icontains=q)
        else:
            qq = Q(subject__icontains=q)
        my_issues_set = my_issues_set.filter(qq)
    day_trigger = cache.get('mydayTrigger' + str(request.web.user.id) + '_' + str(request.web.project.id), 'day7')
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
    print('min_date', min_date)
    if min_date and day_trigger != 'day1':
        days = get_every_day(day_trigger, min_date, '%Y-%m-%d')
    elif day_trigger == 'day1':
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
    all_object_list = (list(my_issues_set.values_list("issue_id", "subject")))
    all_object_list = json.dumps(all_object_list)
    # c = login(request, request.web.user)
    context = {
        'all_object_list': all_object_list,
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


def workbench_tasks_json(request):
    print('workbench tasks json')
    project_id = request.POST.get('project_id')


# deprecated
def workbench_json(request):
    print('workbench_json')
    project_id = request.GET.get('project_id')
    user_id = request.GET.get('user_id')
    if not project_id or not user_id:
        print('用户id或项目id不能为空')
        return JsonResponse({"status": 0, "msg": '用户id或项目id不能为空'})
    user = UserInfo.objects.filter(id=user_id).first()
    if not user:
        print('用户找不到')
        return JsonResponse({"status": 0, "msg": '用户找不到'})
    # 根据优先级排序
    ordering = "FIELD(`priority`, 'danger','warning','success')"
    legendTriggrer = cache.get('myechartlegendTrigger' + str(user_id) + '_' + str(project_id),
                               '1257')
    my_issues_set = models.Issues.objects.filter(Q(project_id=project_id) & (Q(assign=user)
                                                                             | Q(attention=user)
                                                                             | Q(creator=user))
                                                 & Q(status__in=(list(legendTriggrer)))).extra(
        select={'ordering': ordering}, order_by=('ordering', 'id',))
    day_trigger = cache.get('mydayTrigger' + str(user_id) + '_' + str(project_id), 'day7')
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
    fresh_count = my_issues_set.filter(status=1).count()
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
    return JsonResponse({'status': 1, 'data': context})


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


def tool(request, project_id):
    context = {
    }
    return render(request, 'web/tool.html', context)


def calendar(request, project_id):
    return render(request, 'web/calendar.html', {})


def remind(request, project_id):
    reminds = models.InfoLog.objects.filter(receiver=request.web.user, project_id=project_id).order_by('status',
                                                                                                       '-create_datetime')
    reminds_hint = reminds.filter(type=2)
    reminds_sys = reminds.filter(type=1)
    hints = collections.OrderedDict()
    sysinfos = collections.OrderedDict()
    for re in reminds_hint:
        hints[re.id] = {'sender': re.sender.username, 'receiver': re.receiver.username,
                        'create_time': re.create_datetime, 'content': re.content, 'status': re.status,
                        'pure_link': re.pure_link, 'pure_content': re.pure_content}
    for ss in reminds_sys:
        sysinfos[ss.id] = {'sender': ss.sender.username, 'receiver': ss.receiver.username,
                           'create_time': ss.create_datetime, 'content': ss.content, 'status': ss.status,
                           'pure_link': ss.pure_link, 'pure_content': ss.pure_content}

    context = {
        'info_size': 10,
        'hint_size': len(reminds_hint),
        'sys_size': len(reminds_sys),
        'hints': hints,
        'sysinfos': sysinfos
    }
    # raise Exception
    return render(request, 'web/remind.html', context=context)


def remind_json(request):
    user_id = request.GET.get("user_id")
    # project_id = request.GET.get("project_id")
    if not user_id:
        return JsonResponse({"status": 0, "msg": "用户id不能为空"})
    user = UserInfo.objects.filter(id=user_id).first()
    reminds = models.InfoLog.objects.filter(receiver=user).order_by('status', '-create_datetime')
    unread_count = reminds.filter(status=1).count()
    reminds_hint = reminds.filter(type=2)
    reminds_hint_total = (reminds_hint.count())
    page_object = Pagination(
        current_page=request.GET.get('page'),
        all_count=reminds_hint.count(),
        base_url=request.path_info,
        query_params=request.GET,
        per_page=5
    )
    reminds_hint = reminds_hint[page_object.start:page_object.end]
    print('reminds_hint ', len(reminds_hint))
    reminds_sys = reminds.filter(type=1)
    hints = []
    sysinfos = []
    projinfos = []
    for re in reminds_hint:
        hints.append({'sender': re.sender.username, 'receiver': re.receiver.username,
                        'sender_profile_photo': re.sender.git_avatar,
                        'create_time': re.create_datetime, 'content': re.content, 'status': re.status,
                        'pure_link': re.pure_link, 'pure_content': re.pure_content})
    for ss in reminds_sys:
        sysinfos.append({'sender': ss.sender.username, 'receiver': ss.receiver.username,
                           'sender_profile_photo': ss.sender.git_avatar,
                           'create_time': ss.create_datetime, 'content': ss.content, 'status': ss.status,
                           'pure_link': ss.pure_link, 'pure_content': ss.pure_content})
    context = {
        'info_size': 10,
        'unread_count':unread_count,
        'hint_size': reminds_hint_total,
        'sys_size': len(reminds_sys),
        'proj_size': len(projinfos),
        'hints': hints,
        'hints_page_total':page_object.pager_count,
        'hints_current_page':page_object.current_page,
        'sysinfos': sysinfos,
        'projinfos': projinfos
    }
    # raise Exception
    return JsonResponse({"status": 1, "results": context})


# 标记已读
def remind_status(request, project_id):
    remind_id = request.POST.get('id')
    print(remind_id)
    print(project_id)
    info = models.InfoLog.objects.filter(project_id=project_id, id=remind_id).first()
    info.status = 2
    info.save()
    return JsonResponse({'status': 1})


def collect(request, project_id):
    collects_set = Collect.objects.filter(creator=request.web.user)
    collects = collections.OrderedDict()
    for coll in collects_set:
        if coll.type == 1:
            collects[coll.id] = {'create_time': coll.create_datetime, 'title': coll.title, 'type': 'issue',
                                 'link': coll.link, 'id': coll.issues.issue_id, 'project': coll.project.name}
        if coll.type == 2:
            collects[coll.id] = {'create_time': coll.create_datetime, 'title': coll.title, 'type': 'wiki',
                                 'link': coll.link, 'id': coll.wiki.id, 'project': coll.project.name}
        if coll.type == 3:
            collects[coll.id] = {'create_time': coll.create_datetime, 'title': coll.title, 'type': 'file',
                                 'link': coll.link, 'id': coll.file.id, 'project': coll.project.name}
    context = {
        'collects': collects,
        'coll_size': len(collects)
    }
    return render(request, 'web/collect.html', context)

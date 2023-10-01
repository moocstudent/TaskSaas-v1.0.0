import json

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


def workbench(request, project_id):
    # 根据优先级排序
    ordering = "FIELD(`priority`, 'danger','warning','success')"
    legendTriggrer = cache.get(str(request.web.user.id) + 'myechartlegendTrigger','1257')
    my_issues_set = models.Issues.objects.filter(Q(project_id=project_id) & (Q(assign=request.web.user)
                                                                             | Q(attention=request.web.user)
                                                                             | Q(creator=request.web.user))
                                                 & Q(status__in=(list(legendTriggrer)))).extra(
        select={'ordering': ordering}, order_by=('ordering', 'id',))
    day_trigger = cache.get(str(request.web.user.id)+'mydayTrigger', 'day0')
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
    if int(pagesize)!=pagesize:
        pagesize = int(pagesize)+1
    if current_page and int(current_page)>pagesize:
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
    return render(request, 'web/workbench.html', context)

def workbench_json(request):
    print('workbench_json')
    project_id = request.POST.get('project_id')
    # 根据优先级排序
    ordering = "FIELD(`priority`, 'danger','warning','success')"
    legendTriggrer = cache.get(str(request.web.user.id) + 'myechartlegendTrigger')
    my_issues_set = models.Issues.objects.filter(Q(project_id=project_id) & (Q(assign=request.web.user)
                                                                             | Q(attention=request.web.user)
                                                                             | Q(creator=request.web.user))
                                                 & Q(status__in=(list(legendTriggrer)))).extra(
        select={'ordering': ordering}, order_by=('ordering', 'id',))
    day_trigger = cache.get(str(request.web.user.id)+'mydayTrigger', 'day0')
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
    if int(pagesize)!=pagesize:
        pagesize = int(pagesize)+1
    if current_page and int(current_page)>pagesize:
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
        return my_issues_set

from django.core.cache import cache
from django.db.models import Min, Q
from django.template import Library
from django.urls import reverse

from TaskSaasAPP.date_util import get_every_day
from utils.pagination import Pagination
from web import models
from web.views.manage import filter_by_day

register = Library()


@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
    # 1.获取创建的所有项目
    my_project = models.Project.objects.filter(creator=request.web.user)

    # 2.获取参与的所有项目
    join_project = models.ProjectUser.objects.filter(user=request.web.user)

    return {'my': my_project, 'join': join_project, 'request': request}


@register.inclusion_tag('inclusion/workbench_task_list.html')
def workbench_task_list(request):
    project_id = request.POST.get('project_id')
    # 根据优先级排序
    ordering = "FIELD(`priority`, 'danger','warning','success')"
    legendTriggrer = cache.get(str(request.web.user.id) + 'myechartlegendTrigger','1257')
    my_issues_set = models.Issues.objects.filter(Q(project_id=project_id) & (Q(assign=request.web.user)
                                                                             | Q(attention=request.web.user)
                                                                             | Q(creator=request.web.user))
                                                 & Q(status__in=(list(legendTriggrer)))).extra(
        select={'ordering': ordering}, order_by=('ordering', 'id',))
    day_trigger = cache.get(str(request.web.user.id) + 'mydayTrigger', 'day7')
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

    return {'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
            'count_data': count_data,
            'days': days,
            'fresh_counts': fresh_counts,
            'handle_counts': handle_counts,
            'resolve_counts': resolve_counts,
            'wait_counts': wait_counts,
            'reopen_counts': reopen_counts}


@register.inclusion_tag('inclusion/manage_menu_list.html')
def manage_menu_list(request):
    data_list = [
        {'title': '概览', 'url': reverse('dashboard', kwargs={'project_id': request.web.project.id})},
        {'title': '问题', 'url': reverse('issues', kwargs={'project_id': request.web.project.id})},
        {'title': '统计', 'url': reverse('statistics', kwargs={'project_id': request.web.project.id})},
        {'title': 'Git', 'url': reverse('git', kwargs={'project_id': request.web.project.id})},
        {'title': '文件', 'url': reverse('file', kwargs={'project_id': request.web.project.id})},
        {'title': 'wiki', 'url': reverse('wiki', kwargs={'project_id': request.web.project.id})},
        {'title': '设置', 'url': reverse('setting', kwargs={'project_id': request.web.project.id})},
    ]

    for item in data_list:
        if request.path_info.startswith(item['url']):
            item['class'] = 'active'

    return {'data_list': data_list}


@register.inclusion_tag('inclusion/right_side_manage_menu_list.html')
def right_side_manage_menu_list(request):
    right_side_data_list = [
        {'id': 'workbench', 'title': '(新)*工作台',
         'url': reverse('workbench', kwargs={'project_id': request.web.project.id})}
    ]

    for item in right_side_data_list:
        if request.path_info.startswith(item['url']):
            item['class'] = 'active'
    return {'right_side_data_list': right_side_data_list}


@register.inclusion_tag('inclusion/workbench_task_list.html')
def workbench_task_list(request):
    # 根据优先级排序
    ordering = "FIELD(`priority`, 'danger','warning','success')"
    legendTriggrer = cache.get(str(request.web.user.id) + 'myechartlegendTrigger', '1257')
    attention_trigger = cache.get(str(request.web.user.id) + 'myAttentionTrigger', 'off')
    people_involve_q = Q(assign=request.web.user) | Q(creator=request.web.user)
    if attention_trigger == 'on':
        people_involve_q = people_involve_q | Q(attention=request.web.user)
    my_issues_set = models.Issues.objects.filter(Q(project_id=request.web.project.id) & (people_involve_q)
                                                 & Q(status__in=(list(legendTriggrer)))).extra(
        select={'ordering': ordering}, order_by=('ordering', 'id',))
    day_trigger = cache.get(str(request.web.user.id) + 'mydayTrigger', 'day7')
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

    workbench_task_list = [
        {'issues_object_list': issues_object_list,
         'page_html': page_object.page_html(),
         'count_data': count_data,
         'days': days,
         'fresh_counts': fresh_counts,
         'handle_counts': handle_counts,
         'resolve_counts': resolve_counts,
         'wait_counts': wait_counts,
         'reopen_counts': reopen_counts, }
    ]

    # for item in workbench_task_list:
    #     if request.path_info.startswith(item['url']):
    #         item['class'] = 'active'
    return {'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
            'count_data': count_data,
            'days': days,
            'project_id': request.web.project.id,
            'fresh_counts': fresh_counts,
            'handle_counts': handle_counts,
            'resolve_counts': resolve_counts,
            'wait_counts': wait_counts,
            'reopen_counts': reopen_counts, }

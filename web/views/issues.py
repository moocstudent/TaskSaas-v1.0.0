import datetime
import json

from django.core.cache import cache
from django.db.models import Q, Max
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from utils.encrypt import uid
from utils.pagination import Pagination
from web import models
from web.forms.issues import IssuesModelForm, IssuesReplyModelForm, IssuesInviteModelForm


class CheckFilter(object):
    """Checkbox筛选器"""

    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = sorted(data_list)
        self.request = request
    # fixme
    def __iter__(self):
        print('len>>>>',len(self.data_list))
        for item in self.data_list:
            key = str(item[0])
            print('key>>',key)
            text = item[1]
            ck = ""
            # 如果用户请求的url中status和当前key相等
            # url:xxx?status=1
            value = None
            value_list = self.request.GET.getlist(self.name)
            print('request value_list', value_list)
            request_object = self.request.GET.get(self.name)
            if self.name == 'issues_type' and request_object:
                issues_type_ids = request_object.split(',')
                if issues_type_ids:
                    print('request value_str', issues_type_ids)
                    if len(value_list) > len(issues_type_ids):
                        value = value_list
                    else:
                        value = issues_type_ids
            else:
                value = value_list

            print('self.request.GET.get(self.name) >>>',value)
            query_dict = self.request.GET.copy()  # {'status',[1]}
        # if value:
            if key in value:
                ck = "checked"
                print('key in value',ck)
                value.remove(key)  # 1,2,3:{'status',[2]}
            else:
                print('key not in value', ck)
                value.append(key)  # 1,2,3:{'status',[2]}
            query_dict.setlist(self.name, value)  # {'status',[]}
        # 在当前url的参数上，新增参数

            query_dict._mutable = True  # 允许修改


            if 'page' in query_dict:
                query_dict.pop('page')

            if query_dict.urlencode():
                url = "{}?{}".format(self.request.path_info, query_dict.urlencode())
            else:
                url = self.request.path_info

            tpl = "<a class='cell' href='{url}'><input type='checkbox' {ck} /><label>{text}</label></a>"
            html = tpl.format(url=url, ck=ck, text=text)

            yield mark_safe(html)


class SelectFilter(object):
    """Select筛选器"""

    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        yield mark_safe("<select class='select2' multiple='multiple' style='width:100%'>")
        for item in self.data_list:
            key = str(item[0])
            text = item[1]

            selected = ""
            value_list = self.request.GET.getlist(self.name)

            if key in value_list:
                selected = "selected"
                value_list.remove(key)
            else:
                value_list.append(key)

            # 在当前url的参数上，新增参数
            query_dict = self.request.GET.copy()  # {'status',[1]}
            query_dict._mutable = True  # 允许修改
            query_dict.setlist(self.name, value_list)  # {'status',[]}

            if 'page' in query_dict:
                query_dict.pop('page')

            if query_dict.urlencode():
                url = "{}?{}".format(self.request.path_info, query_dict.urlencode())
            else:
                url = self.request.path_info

            html = "<option value='{url}' {selected}>{text}</option>".format(url=url, selected=selected, text=text)
            yield mark_safe(html)

        yield mark_safe("</select>")

# todo 改为对应的restframework form
def issues(request, project_id):
    if request.method == 'GET':
        allow_filter_name = ['issues_type', 'status', 'priority', 'assign', 'attention']
        # 筛选条件(根据用户通过GET传过来的参数实现)
        # ?status=1&status=2&issues_type=1
        condition = {}
        for name in allow_filter_name:
            print('name>>>>>>',name)
            value_list = request.GET.getlist(name)
            print('request value_list',value_list)
            request_object = request.GET.get(name)
            if name == 'issues_type' and request_object:
                issues_type_ids = request_object.split(',')
                if issues_type_ids:
                    print('request value_str',issues_type_ids)
                    if len(value_list)>len(issues_type_ids):
                        print('BIG')
                        condition['{}__in'.format(name)] = value_list
                    else:
                        condition['{}__in'.format(name)] = issues_type_ids
                    continue
            value_list = request.GET.getlist(name)
            if not value_list:
                continue
            condition['{}__in'.format(name)] = value_list
        """
        condition={
        "status__in":[1,2]
        "issues_type__in":[1,]
        }
        """

        # 分页获取数据
        queryset = models.Issues.objects.filter(project_id=project_id).filter(**condition)
        trigger = cache.get(str(request.web.user.id) + 'mytaskTrigger','off')
        if trigger == 'on':
            print("trigger == 'on':")
            print(request.web.user)
            queryset = queryset.filter(Q(assign=request.web.user) | Q(attention=request.web.user)
                                       | Q(creator=request.web.user))
        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
        )

        issues_object_list = queryset[page_object.start:page_object.end]

        form = IssuesModelForm(request)

        project_total_user = [(request.web.project.creator_id, request.web.project.creator.username)]
        join_user = models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__username')
        project_total_user.extend(join_user)

        invite_form = IssuesInviteModelForm()
        context = {
            'form': form,
            'invite_form': invite_form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
            'filter_list': [
                {'title': '问题类型', 'filter': CheckFilter('issues_type', models.IssuesType.objects.filter(
                    project_id=project_id).values_list('id', 'title'), request)},
                {'title': '状态', 'filter': CheckFilter('status', models.Issues.status_choices, request)},
                {'title': '优先级', 'filter': CheckFilter('priority', models.Issues.priority_choices, request)},
                {'title': '指派者', 'filter': SelectFilter('assign', project_total_user, request)},
                {'title': '关注者', 'filter': SelectFilter('attention', project_total_user, request)},
            ]
        }
        return render(request, 'web/issues.html', context)

    form = IssuesModelForm(request, data=request.POST)
    this_proj_max_issue_id = models.Issues.objects.filter(project_id=request.web.project.id).aggregate(
        this_proj_max_issue_id=Max('issue_id'))
    if this_proj_max_issue_id:
        this_proj_max_issue_id = this_proj_max_issue_id['this_proj_max_issue_id']
        if this_proj_max_issue_id is None:
            this_proj_max_issue_id = 0
    else:
        this_proj_max_issue_id = 0
    if form.is_valid():
        form.instance.project = request.web.project
        form.instance.creator = request.web.user
        form.instance.issue_id = this_proj_max_issue_id + 1
        print('form>>',form.instance.desc)
        if form.instance.desc is None or len(form.instance.desc)==0:
            form.instance.desc=form.instance.subject
        # 保存
        form.save()
        return JsonResponse({'status': True, })
    print('form is invalid',form.errors)
    return JsonResponse({'status': False, 'error': form.errors})


def issues_detail(request, project_id, issues_id):
    """编辑问题"""

    issues_object = models.Issues.objects.filter(issue_id=issues_id, project_id=project_id).first()

    form = IssuesModelForm(request, instance=issues_object)

    context = {
        'form': form,
        'issues_object': issues_object
    }
    return render(request, 'web/issues_detail.html', context)


@csrf_exempt
def issues_record(request, project_id, issues_pk):
    """初始化操作记录"""
    print(request.web.project)
    if request.method == 'GET':
        reply_list = models.IssuesReply.objects.filter(issues=issues_pk, issues__project=request.web.project)
        print(reply_list)
        # 将queryset转换为json格式
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id
            }
            data_list.append(data)

        return JsonResponse({'status': True, 'data': data_list})

    form = IssuesReplyModelForm(data=request.POST)

    if form.is_valid():
        # 这里不要动就好，这里id=pk就是没问题的，虽然在数据库字段是issues_pk，但instance的不是
        form.instance.issues_id = issues_pk
        form.instance.reply_type = 2
        form.instance.creator = request.web.user

        instance = form.save()

        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.username,
            'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': instance.reply_id
        }
        return JsonResponse({'status': True, 'data': info})
    return JsonResponse({'status': False, 'error': form.errors})


@csrf_exempt
def issues_change(request, project_id, issues_pk):
    """表单更新数据"""
    issues_object = models.Issues.objects.filter(id=issues_pk, project_id=project_id).first()
    # print('issues_object',issues_object)
    post_dict = json.loads(request.body.decode('utf-8'))
    # 数据库字段更新
    name = post_dict.get('name')
    value = post_dict.get('value')

    field_object = models.Issues._meta.get_field(name)

    def create_reply_record(change_record):
        new_object = models.IssuesReply.objects.create(
            reply_type=1,
            issues=issues_object,
            content=change_record,
            creator=request.web.user
        )

        new_reply_dict = {
            'id': new_object.id,
            'reply_type_text': new_object.get_reply_type_display(),
            'content': new_object.content,
            'creator': new_object.creator.username,
            'datetime': new_object.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': new_object.reply_id
        }

        return new_reply_dict

    # 文本内容
    if name in ['subject', 'desc', 'start_date', 'end_date']:
        if not value:
            if not field_object.null:
                return JsonResponse({'status': False, 'error': '您选择的值不能为空！'})
            setattr(issues_object, name, None)
            issues_object.save()
            # 记录
            change_record = "{}更新为空".format(field_object.verbose_name)

        else:
            setattr(issues_object, name, value)
            issues_object.save()
            # 记录
            change_record = "{}更新为{}".format(field_object.verbose_name, value)

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    # FKEY对象
    if name in ['issues_type', 'module', 'assign', 'parent']:
        if not value:
            if not field_object.null:
                return JsonResponse({'status': False, 'error': '您选择的值不能为空！'})
            setattr(issues_object, name, None)
            issues_object.save()
            # 记录
            change_record = "{}更新为空".format(field_object.verbose_name)

        else:
            if name == 'assign':
                if value == str(request.web.project.creator_id):
                    instance = request.web.project.creator
                else:
                    project_user_object = models.ProjectUser.objects.filter(project_id=project_id,
                                                                            user_id=value).first()
                    if project_user_object:
                        instance = project_user_object.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({'status': False, 'error': '您选择的值不存在！'})

            else:
                print('用户输入的值是自己的值value:',value)
                # 用户输入的值是自己的值
                instance = field_object.rel.model.objects.filter(id=value, project_id=project_id).first()
                if not instance:
                    return JsonResponse({'status': False, 'error': '您选择的值不存在！'})

            change_record = "{}更新为{}".format(field_object.verbose_name, str(instance))
            setattr(issues_object, name, instance)
            issues_object.save()

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    # choice字段
    if name in ['mode', 'status', 'priority']:
        seleted_text = None
        for key, text in field_object.choices:
            if str(key) == value:
                seleted_text = text
        if not seleted_text:
            return JsonResponse({'status': False, 'error': '您选择的值不存在！'})

        setattr(issues_object, name, value)
        issues_object.save()
        change_record = "{}更新为{}".format(field_object.verbose_name, seleted_text)
        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    # M2M字段
    if name in ['attention']:

        # {'name':'abc','value':[1,2,3]}
        # if not isinstance(value, list):
        #     return JsonResponse({'status': False, 'error': '数据格式错误！'})

        if not value:
            issues_object.attention.set([])
            issues_object.save()
            change_record = "{}更新为空".format(field_object.verbose_name)
        else:
            # values=[1,2,3,4] 参与者/创建者
            # 获取当前项目所有成员
            user_dict = {str(request.web.project.creator_id): request.web.project.creator.username}
            project_user_list = models.ProjectUser.objects.filter(project_id=project_id)

            # 将项目成员全放入user_dict
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username
            username_list = []
            for user_id in value:
                username = user_dict.get(user_id)
                if not username:
                    return JsonResponse({'status': False, 'error': '数据错误！'})
                username_list.append(username)

            issues_object.attention.set(value)
            issues_object.save()
            change_record = "{}更新为{}".format(field_object.verbose_name, ",".join(username_list))
        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    return JsonResponse({'status': False, 'error': 'Error！'})


def invite_url(request, project_id):
    """生成邀请码"""
    form = IssuesInviteModelForm(data=request.POST)

    if form.is_valid():
        """
        1/创建随机邀请码
        2/验证码保存到数据库
        3/只有创建者才能邀请
        """
        if request.web.project.creator != request.web.user:
            form.add_error('period', '无权创建邀请码')
            return JsonResponse({'status': False, 'error': form.errors})

        random_invite_code = uid(request.web.user.mobile_phone)

        form.instance.project = request.web.project
        form.instance.code = random_invite_code
        form.instance.creator = request.web.user
        form.save()

        # 生成url
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path=reverse('invite_join', kwargs={'code': random_invite_code})
        )

        return JsonResponse({'status': True, 'data': url})

    return JsonResponse({'status': False, 'error': form.errors})


def invite_join(request, code):
    """访问邀请码"""
    invite_object = models.ProjectInvite.objects.filter(code=code).first()
    if not invite_object:
        return render(request, 'web/invite_join.html', {'error': '邀请码不存在！'})

    if invite_object.project.creator == request.web.user:
        return render(request, 'web/invite_join.html', {'error': '创建者无需再加入项目！'})

    exists = models.ProjectUser.objects.filter(project=invite_object.project, user=request.web.user).first()
    if exists:
        return render(request, 'web/invite_join.html', {'error': '您已在项目中，无需再加入项目！'})

    # max_member = request.web.price_policy.project_member
    # current_member = models.ProjectUser.objects.filter(project=invite_object.project).count()
    # if current_member + 1 >= max_member:
    #     return render(request, 'web/invite_join.html', {'error': '项目成员已满，请升级套餐！'})

    # 邀请码有效性判断
    current_datetime = datetime.datetime.now()
    limit_datetime = invite_object.create_datetime + datetime.timedelta(minutes=invite_object.period)
    if current_datetime > limit_datetime:
        return render(request, 'web/invite_join.html', {'error': '邀请码已过期！'})

    # # 数量限制
    # max_count = invite_object.count
    # use_count = invite_object.use_count
    # if max_count:
    #     if use_count >= max_count:
    #         return render(request, 'web/invite_join.html', {'error': '邀请成员数量已用完！'})
    #     use_count += 1
    #     invite_object.save()

    models.ProjectUser.objects.create(user=request.web.user, project=invite_object.project)
    return render(request, 'web/invite_join.html', {'project': invite_object.project})

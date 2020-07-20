import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from web import models
from web.forms.issues import IssuesModelForm, IssuesReplyModelForm

from utils.pagination import Pagination


def issues(request, project_id):
    if request.method == 'GET':
        # 分页获取数据
        queryset = models.Issues.objects.filter(project_id=project_id)

        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
        )

        issues_object_list = queryset[page_object.start:page_object.end]

        form = IssuesModelForm(request)

        context = {
            'form': form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html()
        }
        return render(request, 'web/issues.html', context)

    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project = request.web.project
        form.instance.creator = request.web.user
        # 保存
        form.save()
        return JsonResponse({'status': True, })
    return JsonResponse({'status': False, 'error': form.errors})


def issues_detail(request, project_id, issues_id):
    """编辑问题"""

    issues_object = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()

    form = IssuesModelForm(request, instance=issues_object)

    context = {
        'form': form,
        'issues_object': issues_object
    }
    return render(request, 'web/issues_detail.html', context)


@csrf_exempt
def issues_record(request, project_id, issues_id):
    """初始化操作记录"""

    if request.method == 'GET':
        reply_list = models.IssuesReply.objects.filter(issues_id=issues_id, issues__project=request.web.project)

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
        form.instance.issues_id = issues_id
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
def issues_change(request, project_id, issues_id):
    """表单更新数据"""
    issues_object = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()

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

    return JsonResponse({'status': False, 'error': '好自为之！'})

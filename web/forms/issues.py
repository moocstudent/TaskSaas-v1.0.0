from django import forms

from web import models
from web.forms.bootstrap import BootStrapForm


class IssuesModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        widgets = {
            "assign": forms.Select(attrs={'class': "selectpicker", "data-live-search": "true"}),
            "attention": forms.SelectMultiple(
                attrs={'class': "selectpicker", "data-live-search": "true", "data-actions-box": "true"}),
            "parent": forms.Select(attrs={'class': "selectpicker", "data-live-search": "true"}
                                   ),
            "start_date": forms.DateTimeInput(attrs={'autocomplete': "off"}),
            "end_date": forms.DateTimeInput(attrs={'autocomplete': "off"})
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        # 处理数据初始化
        # 获取当前项目的所有问题类型
        self.fields['issues_type'].choices = models.IssuesType.objects.filter(project=request.web.project).values_list(
            'id', 'title')

        # 获取当前项目的所有模块
        module_list = [('', '没有选中任何项'), ]
        module_object_list = models.Module.objects.filter(project=request.web.project).values_list(
            'id', 'title')
        module_list.extend(module_object_list)
        self.fields['module'].choices = module_list

        # 获取当前项目的指派和关注者
        total_user_list = [(request.web.project.creator_id, request.web.project.creator.username), ]
        project_user_list = models.ProjectUser.objects.filter(project=request.web.project).values_list('user_id',
                                                                                                       'user__username')

        print('total_user_list',total_user_list)
        print('project_user_list',project_user_list)
        total_user_list.extend(project_user_list)

        self.fields['assign'].choices = [('', '没有选中任何项')] + total_user_list
        self.fields['attention'].choices = total_user_list

        # 当前项目已创建的问题
        parent_list = [('', '没有选中任何项')]
        parent_object_list = models.Issues.objects.filter(project=request.web.project).values_list('id', 'subject')
        parent_list.extend(parent_object_list)
        self.fields['parent'].choices = parent_list


class IssuesReplyModelForm(forms.ModelForm):
    class Meta:
        model = models.IssuesReply
        fields = ['content', 'reply']


class IssuesInviteModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.ProjectInvite
        fields = ['period', 'count', ]

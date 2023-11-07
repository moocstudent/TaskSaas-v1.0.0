from django import forms
from django.core.exceptions import ValidationError

from web import models
from web.forms.bootstrap import BootStrapForm
from web.forms.widgets import ColorRadioSelect


class ProjectModelForm(BootStrapForm, forms.ModelForm):
    bootstrap_class_exclude = ['color']

    def __init__(self, request,user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user=user

    class Meta:
        model = models.Project
        fields = ['name', 'color', 'desc']
        widgets = {
            'desc': forms.Textarea,
            'color': ColorRadioSelect(attrs={'class': 'color-radio'}),
        }

    def clean_name(self):
        """
        项目校验
        :return:
        """
        name = self.cleaned_data['name']
        # 1/当前用户是否已创建此项目

        exists = models.Project.objects.filter(name=name, creator=self.user).exists()
        if exists:
            raise ValidationError('项目名已存在！')

        # 2/项目不存在的情况下，当前用户是否还有额度创建项目
        # 现在已经创建的项目数
        # count = models.Project.objects.filter(creator=self.request.web.user).count()
        # if count >= self.request.web.price_policy.project_num:
        #     raise ValidationError('项目个数已达上限，请购买套餐！')

        return name

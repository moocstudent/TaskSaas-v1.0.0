from web import models
from web.forms.bootstrap import BootStrapForm
from django import forms
from django.core.exceptions import ValidationError


class FileFolderModelForm(BootStrapForm, forms.ModelForm):
    def __init__(self, request, parent_object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_object = parent_object

    class Meta:
        model = models.FileRepository
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']

        queryset = models.FileRepository.objects.filter(file_type=2, name=name,
                                                        project=self.request.web.project)
        if self.parent_object:
            exists = queryset.filter(parent=self.parent_object).exists()
        else:
            exists = queryset.filter(parent__isnull=True).exists()

        if exists:
            raise ValidationError("此文件夹已存在！")

        return name

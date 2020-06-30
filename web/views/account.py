'''
用户账号相关功能：注册/短信/登陆/注销
'''
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from web.forms.account import RegisterModelForm, SendSmsForm
from django.conf import settings


def register(request):
    """
    :param request:
    :return:
    注册
    """
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'web/register.html', {'form': form})

    form = RegisterModelForm(data=request.POST)

    if form.is_valid():
        # 验证通过，写入数据库(密码转换成密文)
        form.save()
        return JsonResponse({'status': True, 'data': '/login/'})

    return JsonResponse({'status': False, 'error': form.errors})


def send_sms(request):
    """
    :param request:
    :return:
    发送短信
    """
    form = SendSmsForm(request, data=request.GET)
    # 单独校验手机号,不能为空，格式是否正确
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})

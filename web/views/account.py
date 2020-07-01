'''
用户账号相关功能：注册/短信/登陆/注销
'''
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSmsForm
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
    发送短信
    :param request:
    :return:
    """
    form = SendSmsForm(request, data=request.GET)
    # 单独校验手机号,不能为空，格式是否正确
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


def login_sms(request):
    """
    短信登陆
    :param request:
    :return:
    """
    if request.method == 'GET':
        form = LoginSmsForm()
        return render(request, 'web/login_sms.html', {'form': form})

    form = LoginSmsForm(request.POST)
    if form.is_valid():
        # 用户输入正确，登陆成功
        user_object = form.cleaned_data['mobile_phone']
        # 将用户信息放入session
        request.session['user_id'] = user_object.id
        request.session['user_name'] = user_object.username

        return JsonResponse({'status': True, 'data': '/index/'})
    return JsonResponse({'status': False, 'error': form.errors})

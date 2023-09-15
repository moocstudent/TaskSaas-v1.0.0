'''
用户账号相关功能：注册/短信/登陆/注销
'''
import datetime
import uuid

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from web import models
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSmsForm, LoginForm
from django.conf import settings
from io import BytesIO
from utils.image_code import check_code
from django.db.models import Q


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
        instance = form.save()

        # policy_object = models.PricePolicy.objects.filter(category=1, title='个人免费版').first()
        # # 创建交易记录
        # models.Transaction.objects.create(
        #     status=2,
        #     order=str(uuid.uuid4()),
        #     user=instance,
        #     price_policy=policy_object,
        #     count=0,
        #     price=0,
        #     start_datetime=datetime.datetime.now(),
        # )
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
        request.session.set_expiry(60 * 60 * 24 * 14)

        return JsonResponse({'status': True, 'data': '/index/'})
    return JsonResponse({'status': False, 'error': form.errors})


def login(request):
    """
    用户名密码登陆
    :param request:
    :return:
    """
    if request.method == 'GET':
        form = LoginForm(request)
        return render(request, 'web/login.html', {'form': form})
    form = LoginForm(request, data=request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        print('password',password)

        user_object = models.UserInfo.objects.filter(Q(email=username) | Q(username=username)) \
            .filter(password=password).first()
        print('user_obj',user_object)
        if user_object:
            # 登陆成功
            request.session['user_id'] = user_object.id
            request.session.set_expiry(60 * 60 * 24 * 14)

            return redirect('index')
        form.add_error('username', '用户名或密码错误')
    return render(request, 'web/login.html', {'form': form})


def image_code(request):
    """
    生成图片验证码
    """

   ### image_object, code = check_code()

   # request.session['image_code'] = code
   # request.session.set_expiry(60)  # 60秒过期

    #stream = BytesIO()
   # image_object.save(stream, 'png')

    return HttpResponse(1)


def logout(request):
    request.session.flush()
    return redirect('index')

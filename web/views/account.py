'''
用户账号相关功能：注册/短信/登陆/注销
'''
import json

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view

from TaskSaas.task.remind_task import remind_deadline
from TaskSaasAPP.string_format_util import format_error_msg
from utils import encrypt
from web import models
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSmsForm, LoginForm
from web.models import UserInfo


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
        user_object = UserInfo.objects.filter(username=form.cleaned_data['username']).first()
        request.session['user_id'] = user_object.id
        request.session.set_expiry(60 * 60 * 24 * 14)

        return JsonResponse({'status': True, 'token':user_object.id,'data': '/login/'})
    return JsonResponse({'status': False, 'error': format_error_msg(form.errors)})


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


from django.middleware.csrf import get_token


def get_token(request):
    token = get_token(request)
    return HttpResponse(json.dumps({'token': token}), content_type="application/json,charset=utf-8")


# @csrf_exempt
# def do_login(request):
#     print('do_login')
#
#     # form = LoginForm(request, data=request.POST)
#     username = request.POST.get('username')
#     password = request.POST.get('password')
#     print('password',password)
#     user_object = models.UserInfo.objects.filter(Q(email=username) | Q(username=username)) \
#         .filter(password=password).first()
#     print('user_obj',user_object)
#     if user_object:
#         # 登陆成功
#         request.session['user_id'] = user_object.id
#         request.session.set_expiry(60 * 60 * 24 * 14)
#         # execution remind deadline task
#         remind_deadline()
#         return JsonResponse({'status':1})
#     return JsonResponse({'status':0})


# @csrf_exempt
@api_view(['POST'])
def do_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    print('username', username)
    """
    用户名密码登陆
    :param request:
    :return:
    """
    username = request.POST.get('username')
    password = request.POST.get('password')
    print('username',username)
    user_object = models.UserInfo.objects.filter(Q(email=username) | Q(username=username)) \
        .filter(password=encrypt.md5(password)).first()
    print('user_obj',user_object)
    if user_object:
        # 登陆成功
        request.session['user_id'] = user_object.id
        request.session.set_expiry(60 * 60 * 24 * 14)
        # execution remind deadline task
        remind_deadline()
        return JsonResponse({'status':1,'token':user_object.id,'token_expiry':60 * 60 * 24 * 14})

# @csrf_exempt
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
            # execution remind deadline task
            remind_deadline()
            print('hello')
            return redirect('index')
        form.add_error('username', '用户名或密码错误')
    return render(request, 'web/login.html', {'form': form})


def image_code(request):
    """
    生成图片验证码 dr
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

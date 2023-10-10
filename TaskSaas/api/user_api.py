import json

import requests
from django.db.transaction import atomic
from django.shortcuts import render

from TaskSaasAPP import encrypt_util
from utils import encrypt
from web import models


def profile(request):
    nick_name = request.POST.get('nick_name')
    password = request.POST.get('password')
    password_flag = None
    try:
        user = models.UserInfo.objects.filter(id=request.web.user.id).first()
        if user:
            if nick_name:
                user.nick_name = nick_name
            if password:
                user.password = encrypt.md5(password)
                password_flag = True
            user.save()
    except:
        nick_name=None
    print(nick_name)
    context = {
        'nick_name': nick_name,
        'password_flag':password_flag
    }
    return render(request, 'web/profile.html',context)


@atomic
def profile_git(request):
    git_un = request.POST.get('git_username')
    git_pd = request.POST.get('git_password')
    user = models.UserInfo.objects.filter(id=request.web.user.id).first()
    bind_name = None
    git_avatar = None
    if user and git_pd and git_un:
        try:
            parameters = "grant_type=password&username=" + git_un + "&password=" + git_pd
            oauth_token_res = json.loads(requests.post("http://39.99.215.169:8099/oauth/token", parameters).text)
            user_git_info_res = json.loads(
                requests.get("http://39.99.215.169:8099/api/v4/user?access_token=" + oauth_token_res['access_token']).text)
            print(user_git_info_res)
            if user_git_info_res['username'] == git_un and user:
                # 获取用户ok，存git信息到userinfo
                user.git_username = git_un
                user.git_password = encrypt_util.encrypt(git_pd, '123')
                user.git_avatar = user_git_info_res['avatar_url']
                user.save()
                bind_name = git_un
                git_avatar = user_git_info_res['avatar_url']
        except Exception as e:
            print(e)
    else:
        pass
    context = {
        'bind_name': bind_name,
        'git_avatar': git_avatar
    }
    return render(request, 'web/profile.html', context)

import json

import requests
from django.http import HttpResponse

from TaskSaasAPP import encrypt_util


# 配置使用的gitlab
def callback(request):
    # todo
    try:
        code = request.GET.get('code')
        client_id = request.GET.get('client_id')
        client_secret = request.GET.get('client_secret')
        gitlab_host = request.GET.get('gitlab_host')
        print('callback code ',code)
        parameters = "client_id=91ff90724fa45c86901ab947d6c148da1e6e26d100fb2d78675da46885c38780&client_secret=6f26e70acc17d3a25ee0fbee98bb0c0b3f377843fd5a4d7735decea703a8230d&code="+code+"&grant_type=authorization_code&redirect_uri=http://localhost:3000/callback/gitlab"
        oauth_token_response = json.loads(requests.post("http://39.99.215.169:8099/oauth/token", parameters).text)
        print(oauth_token_response)
    except:
        return HttpResponse('配置异常')

    # render
    # todo 入库 总setting
    return HttpResponse('配置成功')



def callback_token(request):

    # print(git_password)
    "grant_type=password&username=<your_username>&password=<your_password>"
    print(request)
    return None

def callback_userpassword(request):

    git_username = request.web.user.git_username
    git_password = encrypt_util.decrypt(request.web.user.git_password,"123")
    parameters = "grant_type=password&username=root&password=48o2qLQFOAkt3vqcvIgGkiYjhDfRoAHBpI1O0xRSG6M="
    oauth_token_res = json.loads(requests.post("http://39.99.215.169:8099/oauth/token", parameters).text)
    user_git_info_res = json.loads(requests.get("http://39.99.215.169:8099/api/v4/user?access_token="+oauth_token_res['access_token']).text)
    print(user_git_info_res)
    return HttpResponse(str(user_git_info_res))

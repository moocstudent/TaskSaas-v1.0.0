from django.http import JsonResponse

from TaskSaas.task.remind_task import remind_deadline
from web.models import UserInfo


def get_user_by_openid(request):
    openid = request.GET.get('openid')
    print('openid ',openid)
    user = UserInfo.objects.filter(wechat_openid=openid).first()
    print('user:',user)
    if user:
        # 登陆成功
        request.session['user_id'] = user.id
        request.session.set_expiry(60 * 60 * 24 * 14)
        # execution remind deadline task
        remind_deadline()
        return JsonResponse({'status':1,'token_expiry':60 * 60 * 24 * 14,'userinfo':{'id':user.id,'username':user.username,
                                                    'wechat_avatar':user.wechat_avatar,
                                                    'wechat_nickname':user.wechat_nickname}})
    else:
        return JsonResponse({'status':0,'msg':'根据openid无法获取用户'})


def bind_user_with_openid(request):
    openid = request.POST.get('openid')
    print('openid ', openid)
    user_id = request.POST.get('user_id')
    print('user_id ', user_id)

    user = UserInfo.objects.filter(id=user_id).first()
    user.wechat_openid = openid
    user.save()

    return JsonResponse({'status':1})


def do_profile(request):
    wechat_avatar = request.POST.get('wechat_avatar')
    wechat_nickname = request.POST.get('wechat_nickname')
    user_id = request.POST.get('user_id')
    user = UserInfo.objects.filter(id=user_id).first()
    print('wechat_nickname' ,wechat_nickname)
    if user:
        user.wechat_avatar = wechat_avatar
        user.wechat_nickname = wechat_nickname
        user.save()
        return JsonResponse({'status':1})
    else:
        return JsonResponse({'status':0,'msg':'无此用户'})

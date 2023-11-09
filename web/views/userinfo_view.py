from django.http import JsonResponse

from web.models import UserInfo


def get_user_by_openid(request):
    openid = request.GET.get('openid')
    print('openid ',openid)
    user = UserInfo.objects.filter(wechat_openid=openid).first()
    print('user:',user)
    if user:
        return JsonResponse({'status':1,'userinfo':{'id':user.id,'username':user.username,
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

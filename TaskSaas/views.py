from django.shortcuts import render,HttpResponse

# Create your views here.
import random
from utils.tencent.sms import send_sms_single
from django.conf import settings


def send_sms(request):
    """ 发送短信
        ?tpl=login -> 645736
        ?tpl=register -> 645735
    """
    tpl = request.GET.get('tpl')
    template_id = settings.TENCENT_SMS_TEMPLATES.get(tpl)

    if not template_id:
        return HttpResponse('模板不存在')

    code = random.randrange(1000,9999)
    res = send_sms_single('15773154328',template_id,[code,])
    print(res)
    if res['result'] == 0:
        return HttpResponse('成功')
    else:
        return HttpResponse(res['errmsg'])
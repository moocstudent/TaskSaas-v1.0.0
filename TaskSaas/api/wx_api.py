
from django.http import HttpResponse
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.utils import check_signature


def wx_entry_api(request):
    signature = request.GET.get('signature', "")
    timestamp = request.GET.get('timestamp', "")
    echostr = request.GET.get('echostr', "")
    nonce = request.GET.get('nonce', "")
    print('sign ',signature)
    print('timestamp ',timestamp)
    print('nonce ',nonce)
    try:
        check_signature("wechat_implements",signature,timestamp,nonce)
        print('check through')
        return HttpResponse(echostr)
    except InvalidSignatureException:
        raise InvalidSignatureException()


def wx_callback_api(request):
    print('callback invoke')
    # signature = request.GET.get('signature', "")
    # timestamp = request.GET.get('timestamp', "")
    # echostr = request.GET.get('echostr', "")
    # nonce = request.GET.get('nonce', "")
    # print('sign ',signature)
    # print('timestamp ',timestamp)
    # print('nonce ',nonce)
    # try:
    #     check_signature("wechat_implements",signature,timestamp,nonce)
    #     print('check through')
    #     return HttpResponse(echostr)
    # except InvalidSignatureException:
    #     raise InvalidSignatureException()


def wx_verify_txt(request):
    return "O7ZsD2KZoE5w9Usg"
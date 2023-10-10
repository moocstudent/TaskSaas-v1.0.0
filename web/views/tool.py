import random

from django.http import JsonResponse


# 生成随机的中文字符
def generate_random_chinese_string(request,project_id):
    str_length=request.POST.get('str_length')
    print('str_length',str_length)
    str_length = int(str_length)
    chinese_characters = [chr(random.randint(0x4e00, 0x9fff)) for _ in range(str_length)]
    # return
    return JsonResponse({'status':1,'str': ''.join(chinese_characters) })

import os
import random

from django.http import JsonResponse
import subprocess

from TaskSaasAPP import settings


# 生成随机的中文字符
def generate_random_chinese_string(request,project_id):
    str_length=request.POST.get('str_length')
    print('str_length',str_length)
    str_length = int(str_length)
    chinese_characters = [chr(random.randint(0x4e00, 0x9fff)) for _ in range(str_length)]
    # return
    return JsonResponse({'status':1,'str': ''.join(chinese_characters) })

def encrypt_druid_password(request,project_id):
    original_pwd = request.POST.get('original_pwd')
    if original_pwd:
        java_path = "/usr/bin/java"  # Java 的路径
        jar_name = "druid-1.2.18.jar"  # jar 包的路径
        jar_ab_path = os.path.join(settings.STATICFILES_DIRS[0] + 'druid', jar_name)
        print(jar_ab_path)
        # 要执行的命令
        cmd =  [java_path,"-cp",jar_ab_path,"com.alibaba.druid.filter.config.ConfigTools",original_pwd]

        # 执行
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        exe_output = out.decode("utf-8")
        public_k_index = exe_output.find("publicKey:")
        password_k_index = exe_output.find("password:")

        output_public_key = exe_output[public_k_index+len("publicKey:"):password_k_index]
        output_password = exe_output[password_k_index+len("password:"):len(exe_output)]

        # 打印输出和错误
        return JsonResponse({'status': 1, 'public_key':output_public_key,'encrypt_pwd':output_password})


#查看ipv4的子掩网码支持的地址数
def resolve_mask_of_ipv4(request,project_id):
    ipv4 = request.POST.get("ipv4")
    mask = ipv4.split("/")[1]
    support_ip_size = 2**(abs(32-int(mask)))-2
    return JsonResponse({'status':1,'support_ip_size':support_ip_size})

# def color_picker(request,project_id):
#     if request.method == 'POST':
#         color_code = request.POST.get('color_code')  # 获取带有#的色值
#         if color_code and color_code.startswith('#'):
#             red = int(color_code[1:3], 16)  # 提取红色分量
#             green = int(color_code[3:5], 16)  # 提取绿色分量
#             blue = int(color_code[5:7], 16)  # 提取蓝色分量
#             return JsonResponse({'status':1,'color': (red, green, blue)})
#
#     return JsonResponse({'status':0})
# def test_ip():
#     mask = '127.0.0.1/24'.split("/")[1]
#     support_ip_size = 2**(abs(32-int(mask)))-2
#     print(support_ip_size)
#
# test_ip()
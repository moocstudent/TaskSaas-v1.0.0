import requests

res = requests.get(
    'https://15773154328-1594572164-1302500499.cos.ap-chengdu.myqcloud.com/1594651908039_%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20200624131716.jpg')

print(res.content)

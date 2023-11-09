import random


#1、随机生成小数
def create_random_decimal(start,end):
    '''
    :param start: 要处理数值的起始值
    :param end: 要处理数值的结尾值
    :return: 返回介于start和end之间的小数
    '''
    if end > start:
        number = random.uniform(start,end)
        print('获取start-end之间的小数')
        return format(number, '.2f')
    raise '请输入符合end > start的数字'


# print(create_random_decimal(1.00, 100.00))

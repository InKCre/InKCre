# env: python3.10
# author: Lanzhijiang
# date: 2023/05/01
# description: 通用内容，函数、类、配置之类的

import string
import random


def get_path_generator():

    pass


def generate_random_key(length=6):

    """
    生成随机钥匙
    :return:
    """
    maka = string.digits + string.ascii_letters
    maka_list = list(maka)
    x = [random.choice(maka_list) for i in range(length)]
    return ''.join(x)
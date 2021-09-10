# -*- coding = utf-8 -*-
# @Time : 2021-07-25 13:39
# @Author : Danny
# @File : utility.py
# @Software: PyCharm
from django.contrib.auth.models import User
import sys

from typing import List

# from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
# from alibabacloud_tea_openapi import models as open_api_models
# from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from django.http import JsonResponse


def _exist_username(username):
    if User.objects.filter(username=username).exists():
        return True
    else:
        return False


# required_login decorate
def required_login(func):
    def wrapper(request, *args, **kw):
        if not request.user.is_authenticated:
            msg = {
                "status": 2,
                "msg": "account unauthorized"
            }
            return JsonResponse(msg, status=401)
        return func(request, *args, **kw)
    return wrapper


# class Sample:
#     def __init__(self):
#         pass
#
#     @staticmethod
#     def create_client(
#         access_key_id: str,
#         access_key_secret: str,
#     ) -> Dysmsapi20170525Client:
#         """
#         使用AK&SK初始化账号Client
#         @param access_key_id:
#         @param access_key_secret:
#         @return: Client
#         @throws Exception
#         """
#         config = open_api_models.Config(
#             # 您的AccessKey ID,
#             access_key_id=access_key_id,
#             # 您的AccessKey Secret,
#             access_key_secret=access_key_secret
#         )
#         # 访问的域名
#         config.endpoint = 'dysmsapi.aliyuncs.com'
#         return Dysmsapi20170525Client(config)
#
#     @staticmethod
#     def main(
#         args: List[str],
#     ) -> None:
#         client = Sample.create_client('accessKeyId', 'accessKeySecret')
#         send_sms_request = dysmsapi_20170525_models.SendSmsRequest()
#         # 复制代码运行请自行打印 API 的返回值
#         client.send_sms(send_sms_request)
#
#     @staticmethod
#     async def main_async(
#         args: List[str],
#     ) -> None:
#         client = Sample.create_client('accessKeyId', 'accessKeySecret')
#         send_sms_request = dysmsapi_20170525_models.SendSmsRequest()
#         # 复制代码运行请自行打印 API 的返回值
#         await client.send_sms_async(send_sms_request)


# if __name__ == '__main__':
#     Sample.main(sys.argv[1:])
# -*- coding: utf-8 -*-
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider

# 从环境变量中获取访问凭证。运行本代码示例之前，请先配置环境变量。
auth = oss2.ProviderAuthV4(EnvironmentVariableCredentialsProvider())
# 填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
endpoint = 'https://oss-cn-beijing.aliyuncs.com'
# 填写Endpoint对应的Region信息，例如cn-hangzhou。
region = 'cn-beijing'

# 填写Bucket名称。
bucket = oss2.Bucket(auth, endpoint, 'llmbattle', region=region)


def download_file(object_name, file_name):
    #object_name是在oss存储里的路径
    #file_name是本地路径
    bucket.get_object_to_file(object_name, file_name)

    print('download file: %s' % file_name)


def upload_file(object_name, file_name):
    #object_name是在oss存储里的路径
    #file_name是本地路径
    bucket.put_object_from_file(object_name, file_name)
    print('upload file: %s' % file_name)

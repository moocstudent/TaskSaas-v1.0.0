# -*- coding=utf-8
# appid 已在配置中移除,请在参数 Bucket 中带上 appid。Bucket 由 BucketName-APPID 组成
# 1. 设置用户配置, 包括 secretId，secretKey 以及 Region
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings

secret_id = settings.SECRET_ID  # 替换为用户的 secretId
secret_key = settings.SECRET_KEY  # 替换为用户的 secretKey
region = settings.REGION  # 替换为用户的 Region

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, )
# 2. 获取客户端对象
client = CosS3Client(config)

response = client.upload_file(
    Bucket='web-1302500499',
    LocalFilePath='pic.jpg',
    Key='p1.jpg',
)
print(response['ETag'])

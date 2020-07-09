# -*- coding=utf-8
# appid 已在配置中移除,请在参数 Bucket 中带上 appid。Bucket 由 BucketName-APPID 组成
# 1. 设置用户配置, 包括 secretId，secretKey 以及 Region
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings


def create_bucket(bucket, region='ap-chengdu'):
    """
    创建COS桶
    :param bucket:桶名称
    :param region: 区域
    :return:
    """

    config = CosConfig(Region=region, SecretId=settings.SECRET_ID, SecretKey=settings.SECRET_KEY, )
    client = CosS3Client(config)
    client.create_bucket(
        Bucket=bucket,
        ACL='public-read'  # private/public-read/public-read-write
    )


def upload_file(bucket, region, file_object, key, ):
    """
    COS上传文件
    :param bucket:
    :param file_object:
    :param key:
    :param region:
    :return:
    """
    config = CosConfig(Region=region, SecretId=settings.SECRET_ID, SecretKey=settings.SECRET_KEY, )
    client = CosS3Client(config)

    client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_object,
        Key=key,
    )

    return "https://{}.cos.{}.myqcloud.com/{}".format(bucket, region, key)

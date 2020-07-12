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

    # 跨域解决
    cors_config = {
        'CORSRule': [{
            'AllowedOrigin': '*',
            'AllowedMethod': ['GET', 'PUT', 'HEAD', 'POST', 'DELETE'],
            'AllowedHeader': '*',
            'ExposeHeader': '*',
            'MaxAgeSeconds': 500
        }
        ]
    }

    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
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


def delete_file(bucket, region, key, ):
    """
    COS删除文件
    :param bucket:
    :param key:
    :param region:
    :return:
    """
    config = CosConfig(Region=region, SecretId=settings.SECRET_ID, SecretKey=settings.SECRET_KEY, )
    client = CosS3Client(config)

    client.delete_object(
        Bucket=bucket,
        Key=key,
    )


def delete_file_list(bucket, region, key_list):
    """
    COS批量删除文件
    :param bucket:
    :param key_list:
    :param region:
    :return:
    """
    config = CosConfig(Region=region, SecretId=settings.SECRET_ID, SecretKey=settings.SECRET_KEY, )
    client = CosS3Client(config)

    objects = {
        "Quiet": "true",
        "Object": key_list
    }

    client.delete_objects(
        Bucket=bucket,
        Delete=objects
    )

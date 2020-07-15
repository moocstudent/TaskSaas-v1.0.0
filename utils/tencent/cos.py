# -*- coding=utf-8
# appid 已在配置中移除,请在参数 Bucket 中带上 appid。Bucket 由 BucketName-APPID 组成
# 1. 设置用户配置, 包括 secretId，secretKey 以及 Region
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings
from qcloud_cos.cos_exception import CosServiceError


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


def check_file(bucket, region, key):
    """
    COS文件校验
    :param bucket:
    :param key_list:
    :param region:
    :return:
    """
    config = CosConfig(Region=region, SecretId=settings.SECRET_ID, SecretKey=settings.SECRET_KEY, )
    client = CosS3Client(config)

    data = client.head_object(
        Bucket=bucket,
        Key=key
    )

    return data


def credential(bucket, region):
    """ 获取cos上传临时凭证 """

    from sts.sts import Sts
    config = {
        # 临时密钥有效时长，单位是秒（30分钟=1800秒）
        'duration_seconds': 5,
        # 固定密钥 id
        'secret_id': settings.SECRET_ID,
        # 固定密钥 key
        'secret_key': settings.SECRET_KEY,
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # "name/cos:PutObject",
            # 'name/cos:PostObject',
            # 'name/cos:DeleteObject',
            # "name/cos:UploadPart",
            # "name/cos:UploadPartCopy",
            # "name/cos:CompleteMultipartUpload",
            # "name/cos:AbortMultipartUpload",
            "*",
        ],
    }

    sts = Sts(config)
    result_dict = sts.get_credential()
    return result_dict


def delete_bucket(bucket, region):
    """删除桶"""
    config = CosConfig(Region=region, SecretId=settings.SECRET_ID, SecretKey=settings.SECRET_KEY, )
    client = CosS3Client(config)

    try:
        # 删除桶中所有文件 & 碎片
        while True:
            part_objects = client.list_objects(bucket)

            contents = part_objects.get('Contents')
            # contents为空，获取完毕
            if not contents:
                break

            # 批量删除
            objects = {
                "Quiet": "true",
                "Object": [{'Key': item['Key']} for item in contents]
            }
            client.delete_objects(bucket, objects)

            # 删除桶
            if part_objects['IsTruncated'] == "false":
                break

        # 找到碎片
        while True:
            part_uploads = client.list_multipart_uploads(bucket)
            uploads = part_uploads.get('Upload')
            if not uploads:
                break

            for item in uploads:
                client.abort_multipart_upload(bucket, item['Key'], item['uploadId'])

            if part_uploads['IsTruncated'] == 'false':
                break

        client.delete_bucket(bucket)
    except CosServiceError as e:
        pass

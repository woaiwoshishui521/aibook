import os
import uuid
import logging
import oss2
from django.conf import settings

logger = logging.getLogger(__name__)


def get_oss_bucket():
    """获取OSS Bucket实例"""
    auth = oss2.Auth(
        settings.OSS_ACCESS_KEY_ID,
        settings.OSS_ACCESS_KEY_SECRET
    )
    bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
    return bucket


def generate_oss_key(original_filename: str, file_type: str) -> str:
    """生成OSS对象Key（按类型分目录存储）"""
    from datetime import datetime
    ext = os.path.splitext(original_filename)[1].lower()
    date_path = datetime.now().strftime('%Y/%m/%d')
    unique_name = f"{uuid.uuid4().hex}{ext}"

    type_dir_map = {
        'image': 'images',
        'video': 'videos',
        'audio': 'audios',
        'document': 'documents',
        'other': 'others',
    }
    dir_name = type_dir_map.get(file_type, 'others')
    return f"{dir_name}/{date_path}/{unique_name}"


def upload_file_to_oss(file_obj, oss_key: str, content_type: str = None) -> dict:
    """
    上传文件到OSS
    :param file_obj: 文件对象
    :param oss_key: OSS对象Key
    :param content_type: MIME类型
    :return: {'url': str, 'size': int}
    """
    bucket = get_oss_bucket()
    headers = {}
    if content_type:
        headers['Content-Type'] = content_type

    # 读取文件内容
    file_obj.seek(0)
    file_data = file_obj.read()
    file_size = len(file_data)

    # 上传到OSS
    result = bucket.put_object(oss_key, file_data, headers=headers)

    if result.status != 200:
        raise Exception(f"OSS上传失败，状态码: {result.status}")

    # 构建访问URL
    url = build_oss_url(oss_key)
    return {'url': url, 'size': file_size}


def upload_file_to_oss_multipart(file_obj, oss_key: str, content_type: str = None,
                                  progress_callback=None) -> dict:
    """
    分片上传大文件到OSS（适用于超过100MB的文件）
    :param file_obj: 文件对象
    :param oss_key: OSS对象Key
    :param content_type: MIME类型
    :param progress_callback: 进度回调函数 callback(bytes_consumed, total_bytes)
    :return: {'url': str, 'size': int}
    """
    bucket = get_oss_bucket()
    headers = {}
    if content_type:
        headers['Content-Type'] = content_type

    file_obj.seek(0, 2)  # seek to end
    file_size = file_obj.tell()
    file_obj.seek(0)

    # 使用resumable_upload进行断点续传
    oss2.resumable_upload(
        bucket,
        oss_key,
        file_obj,
        headers=headers,
        progress_callback=progress_callback,
        multipart_threshold=10 * 1024 * 1024,  # 10MB以上使用分片
        part_size=5 * 1024 * 1024,  # 每片5MB
        num_threads=4
    )

    url = build_oss_url(oss_key)
    return {'url': url, 'size': file_size}


def build_oss_url(oss_key: str) -> str:
    """构建OSS文件访问URL"""
    custom_domain = getattr(settings, 'OSS_CUSTOM_DOMAIN', '')
    if custom_domain:
        return f"https://{custom_domain}/{oss_key}"
    return f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{oss_key}"


def delete_file_from_oss(oss_key: str) -> bool:
    """从OSS删除文件"""
    try:
        bucket = get_oss_bucket()
        bucket.delete_object(oss_key)
        return True
    except Exception as e:
        logger.error(f"OSS删除文件失败: {oss_key}, 错误: {str(e)}")
        return False


def generate_presigned_url(oss_key: str, expires: int = 3600) -> str:
    """
    生成OSS预签名URL（用于私有Bucket的临时访问）
    :param oss_key: OSS对象Key
    :param expires: 过期时间(秒)，默认1小时
    :return: 预签名URL
    """
    bucket = get_oss_bucket()
    url = bucket.sign_url('GET', oss_key, expires)
    return url


def check_oss_connection() -> dict:
    """检查OSS连接状态"""
    try:
        bucket = get_oss_bucket()
        # 尝试列举少量对象来验证连接
        list(oss2.ObjectIterator(bucket, max_keys=1))
        return {'status': 'ok', 'message': 'OSS连接正常'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

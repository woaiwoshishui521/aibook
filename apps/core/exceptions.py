from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError


class CustomAPIException(APIException):
    """自定义API异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '发生错误'
    default_code = 'error'


class NotFoundException(CustomAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = '资源不存在'
    default_code = 'not_found'


class ConflictException(CustomAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = '资源冲突'
    default_code = 'conflict'


def custom_exception_handler(exc, context):
    """自定义异常处理器"""
    # 先调用DRF默认的异常处理器
    response = exception_handler(exc, context)
    
    # 处理Django的ValidationError
    if isinstance(exc, DjangoValidationError):
        return Response(
            {'detail': exc.message if hasattr(exc, 'message') else str(exc)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 自定义响应格式
    if response is not None:
        error_data = {
            'success': False,
            'code': getattr(exc, 'code', 'error'),
            'message': response.data.get('detail', '发生错误'),
            'errors': response.data if 'detail' not in response.data else None,
            'status_code': response.status_code,
        }
        response.data = error_data
    
    return response

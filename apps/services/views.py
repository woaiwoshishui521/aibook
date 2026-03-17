import os
import signal
import subprocess
import psutil
import socket
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_port(port):
    """检查端口是否开放"""
    if not port:
        return False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False


class ProcessInfo:
    """进程信息"""
    def __init__(self, name, command, port=None, description=None):
        self.name = name
        self.command = command
        self.port = port
        self.description = description
        self.process = None
        self.pid = None
        self.status = 'stopped'

    def get_process(self):
        """获取进程状态"""
        # 先检查端口是否开放（对于 Flower、Django 等有端口的服务）
        if self.port and check_port(self.port):
            self.status = 'running'
            # 尝试找到对应的 PID
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline')
                    if cmdline:
                        cmd_str = ' '.join(cmdline)
                        # 根据服务类型匹配
                        if self.port == 5555:  # Flower
                            if 'flower' in cmd_str.lower():
                                self.pid = proc.info['pid']
                                self.process = proc
                                return
                        elif self.port == 8000:  # Django
                            if 'runserver' in cmd_str:
                                self.pid = proc.info['pid']
                                self.process = proc
                                return
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            # 如果没找到进程但端口开放，标记为运行中（PID 待定）
            return

        # 对于没有端口的服务，通过进程名检测
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline')
                if cmdline:
                    cmd_str = ' '.join(cmdline)
                    # Celery worker 检测
                    if 'celery' in cmd_str and 'worker' in cmd_str:
                        self.process = proc
                        self.pid = proc.info['pid']
                        self.status = 'running'
                        return
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        self.status = 'stopped'


def get_services():
    """获取服务实例 - 每次调用创建新实例以获取实时状态"""
    return {
        'django': ProcessInfo(
            name='Django Server',
            command='runserver',
            port=8000,
            description='Django 开发服务器'
        ),
        'celery': ProcessInfo(
            name='Celery Worker',
            command='celery -A config worker',
            description='Celery 任务 worker'
        ),
        'flower': ProcessInfo(
            name='Flower Monitor',
            command='celery -A config flower',
            port=5555,
            description='Celery 监控面板'
        ),
    }


# 定义需要管理的服务（用于模板显示）
SERVICES_DISPLAY = {
    'django': {'name': 'Django Server', 'port': 8000, 'description': 'Django 开发服务器'},
    'celery': {'name': 'Celery Worker', 'port': None, 'description': 'Celery 任务 worker'},
    'flower': {'name': 'Flower Monitor', 'port': 5555, 'description': 'Celery 监控面板'},
}


def get_service_status(request):
    """获取所有服务状态"""
    result = {}
    services = get_services()
    for key, service in services.items():
        service.get_process()
        result[key] = {
            'name': service.name,
            'status': service.status,
            'pid': service.pid,
            'port': service.port,
            'description': service.description,
            'command': service.command
        }
    return JsonResponse(result)


@method_decorator(csrf_exempt, name='dispatch')
class ServiceControl(View):
    """服务控制"""

    def post(self, request):
        action = request.POST.get('action')
        service_key = request.POST.get('service')

        services = get_services()
        if service_key not in services:
            return JsonResponse({'success': False, 'message': '未知服务'})

        svc = services[service_key]

        # 获取启动命令
        commands = {
            'django': 'python manage.py runserver 0.0.0.0:8000',
            'celery': 'celery -A config worker -l info --concurrency=2',
            'flower': 'celery -A config flower',
        }

        if action == 'start':
            return self.start_service(svc, service_key, commands.get(service_key, ''))
        elif action == 'stop':
            return self.stop_service(svc)
        elif action == 'restart':
            return self.restart_service(svc, service_key, commands.get(service_key, ''))
        else:
            return JsonResponse({'success': False, 'message': '未知操作'})

    def start_service(self, service, key, command):
        """启动服务"""
        service.get_process()
        if service.status == 'running':
            return JsonResponse({'success': False, 'message': f'{service.name} 已在运行'})

        try:
            # 使用 nohup 在后台运行
            log_dir = os.path.join(PROJECT_ROOT, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f'{key}.log')

            with open(log_file, 'a') as f:
                subprocess.Popen(
                    command.split(),
                    cwd=PROJECT_ROOT,
                    stdout=f,
                    stderr=f,
                    preexec_fn=os.setsid
                )

            return JsonResponse({'success': True, 'message': f'{service.name} 启动成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'启动失败: {str(e)}'})

    def stop_service(self, service):
        """停止服务"""
        service.get_process()
        if service.status == 'stopped':
            return JsonResponse({'success': False, 'message': f'{service.name} 未在运行'})

        try:
            if service.process and service.pid:
                # 终止进程组
                try:
                    os.killpg(os.getpgid(service.pid), signal.SIGTERM)
                except:
                    service.process.terminate()
            elif service.port:
                # 如果没有找到进程但端口开放，尝试通过端口找到进程并终止
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = proc.info.get('cmdline')
                        if cmdline:
                            cmd_str = ' '.join(cmdline)
                            if 'flower' in cmd_str or 'runserver' in cmd_str:
                                proc.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            return JsonResponse({'success': True, 'message': f'{service.name} 已停止'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'停止失败: {str(e)}'})

    def restart_service(self, service, key, command):
        """重启服务"""
        service.get_process()
        if service.status == 'running':
            try:
                if service.process:
                    os.killpg(os.getpgid(service.pid), signal.SIGTERM)
            except:
                pass
        # 等待一下让进程完全终止
        import time
        time.sleep(1)
        return self.start_service(service, key, command)


class ServiceDashboard(View):
    """服务管理仪表盘"""

    def get(self, request):
        # 获取系统信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        context = {
            'services': [],
            'system': {
                'cpu': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used': round(memory.used / (1024**3), 2),
                'memory_total': round(memory.total / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_used': round(disk.used / (1024**3), 2),
                'disk_total': round(disk.total / (1024**3), 2),
            }
        }

        # 获取每个服务的状态
        services = get_services()
        display_info = SERVICES_DISPLAY
        for key, service in services.items():
            service.get_process()
            info = display_info.get(key, {})
            context['services'].append({
                'key': key,
                'name': info.get('name', service.name),
                'status': service.status,
                'pid': service.pid,
                'port': info.get('port', service.port),
                'description': info.get('description', ''),
            })

        return render(request, 'services/dashboard.html', context)











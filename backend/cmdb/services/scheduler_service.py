"""
定时任务服务层
"""
from typing import List, Dict, Any
from django.db import transaction
from django.utils import timezone
from .base_service import BaseService


class SchedulerService(BaseService):
    """定时任务服务"""
    
    @staticmethod
    def create_job(name: str, task_type: str, cron_expression: str = '',
                  description: str = '') -> Dict[str, Any]:
        """创建定时任务"""
        from cmdb.models import ScheduledJob
        
        job = ScheduledJob.objects.create(
            name=name,
            task_type=task_type,
            cron_expression=cron_expression,
            description=description
        )
        return {'success': True, 'data': job.to_dict()}
    
    @staticmethod
    def get_job_list() -> Dict[str, Any]:
        """获取定时任务列表"""
        from cmdb.models import ScheduledJob
        
        jobs = ScheduledJob.objects.all().order_by('-created_at')
        return {
            'success': True,
            'data': [j.to_dict() for j in jobs]
        }
    
    @staticmethod
    def start_job(job_id: int) -> Dict[str, Any]:
        """启动定时任务"""
        from cmdb.models import ScheduledJob
        
        job = ScheduledJob.objects.get(id=job_id)
        
        if job.status != 'stopped':
            return {'success': False, 'message': '任务不是停止状态'}
        
        job.status = 'running'
        job.save()
        
        # 计算下次运行时间
        if job.cron_expression:
            job.next_run_time = timezone.now()  # 简化版
        else:
            job.next_run_time = timezone.now() + timezone.timedelta(seconds=job.interval_seconds)
        
        job.save()
        
        return {'success': True, 'message': '任务启动成功'}
    
    @staticmethod
    def stop_job(job_id: int) -> Dict[str, Any]:
        """停止定时任务"""
        from cmdb.models import ScheduledJob
        
        job = ScheduledJob.objects.get(id=job_id)
        
        if job.status != 'running':
            return {'success': False, 'message': '任务不是运行状态'}
        
        job.status = 'stopped'
        job.save()
        
        return {'success': True, 'message': '任务停止成功'}
    
    @staticmethod
    def execute_job(job_id: int) -> Dict[str, Any]:
        """立即执行定时任务"""
        from cmdb.models import ScheduledJob
        
        job = ScheduledJob.objects.get(id=job_id)
        
        job.status = 'running'
        job.save()
        
        try:
            # 这里应该调用实际的定时任务执行逻辑
            # 简化实现：模拟执行
            job.run_count += 1
            job.last_run_time = timezone.now()
            job.status = 'running'
            job.save()
            
            return {'success': True, 'message': '任务执行成功'}
        except Exception as e:
            job.status = 'error'
            job.error_message = str(e)
            job.save()
            
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def check_cron_expression(cron_expression: str) -> Dict[str, Any]:
        """校验 Cron 表达式"""
        from croniter import croniter
        
        try:
            # 尝试解析 cron 表达式
            croniter(cron_expression, timezone.now())
            return {'success': True, 'message': 'Cron 表达式格式正确'}
        except Exception as e:
            return {'success': False, 'message': f'Cron 表达式格式错误: {str(e)}'}

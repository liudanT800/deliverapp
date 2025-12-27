import asyncio
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.db.session import get_session


async def cleanup_expired_tasks():
    """
    清理过期任务的定时任务
    将超过抢单截止时间且仍处于pending状态的任务标记为已取消
    """
    async for session in get_session():
        try:
            # 查找所有已过期但仍未被接取的任务
            stmt = select(Task).where(
                Task.status == TaskStatus.pending,
                Task.grab_expires_at < datetime.utcnow()
            )
            
            result = await session.execute(stmt)
            expired_tasks = result.scalars().all()
            
            # 将过期任务标记为已取消
            for task in expired_tasks:
                task.status = TaskStatus.cancelled
                task.cancelled_by = "system"  # 系统自动取消
            
            if expired_tasks:
                await session.commit()
                print(f"已清理 {len(expired_tasks)} 个过期任务")
                
        except Exception as e:
            print(f"清理过期任务时出错: {e}")
            await session.rollback()
        finally:
            await session.close()


async def start_cleanup_scheduler(interval_seconds: int = 3600):
    """
    启动定时清理任务调度器
    
    Args:
        interval_seconds: 清理间隔（秒），默认为3600秒（1小时）
    """
    while True:
        try:
            await cleanup_expired_tasks()
        except Exception as e:
            print(f"执行定时清理任务时出错: {e}")
        
        # 等待指定的时间间隔
        await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    # 运行定时清理任务
    asyncio.run(start_cleanup_scheduler())
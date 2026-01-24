"""
后台工作线程
用于执行耗时任务
"""
from PyQt6.QtCore import QThread, pyqtSignal
from functools import wraps
import traceback


def run_in_thread(func):
    """装饰器：在线程中运行函数"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return self.run_in_thread(func, *args, **kwargs)
    return wrapper


class WorkerThread(QThread):
    """通用工作线程"""

    # 信号
    finished = pyqtSignal(object)  # 任务完成
    error = pyqtSignal(str)        # 错误
    progress = pyqtSignal(int, str)  # 进度（百分比, 消息）

    def __init__(self, target_func, *args, **kwargs):
        super().__init__()
        self.target_func = target_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """运行任务"""
        try:
            result = self.target_func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.error.emit(error_msg)

# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller运行时钩子 - 修复无控制台模式下的stdout/stderr问题
在无控制台模式下(sys.stdout=None, sys.stderr=None)，uvicorn会崩溃
此钩子在应用启动前重新定向stdout/stderr到NullWriter
"""

import sys
import os


class NullWriter:
    """空写入器，用于重定向输出"""

    def write(self, text):
        pass

    def flush(self):
        pass

    def isatty(self):
        return False


# 修复stdout和stderr
if sys.stdout is None:
    sys.stdout = NullWriter()

if sys.stderr is None:
    sys.stderr = NullWriter()

# 确保环境变量设置正确（影响uvicorn日志行为）
os.environ['UVICORN_NO_COLORS'] = '1'

"""
文件管理工具
"""
import os
import json
from pathlib import Path
from datetime import datetime


class FileManager:
    """文件管理器"""

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.ensure_directories()

    def ensure_directories(self):
        """确保所需目录存在"""
        dirs = [
            'images',
            'output',
            'user_data',
            'logs'
        ]

        for dir_name in dirs:
            dir_path = self.data_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_images_dir(self):
        """获取图片目录"""
        return str(self.data_dir / 'images')

    def get_output_dir(self):
        """获取输出目录"""
        return str(self.data_dir / 'output')

    def get_logs_dir(self):
        """获取日志目录"""
        return str(self.data_dir / 'logs')

    def get_user_data_dir(self):
        """获取用户数据目录"""
        return str(self.data_dir / 'user_data')

    def generate_unique_filename(self, directory, prefix, extension):
        """生成唯一文件名"""
        counter = 1
        while True:
            if counter == 1:
                filename = f"{prefix}.{extension}"
            else:
                filename = f"{prefix}_{counter}.{extension}"

            filepath = Path(directory) / filename
            if not filepath.exists():
                return str(filepath), filename

            counter += 1

    def save_json(self, data, filepath):
        """保存JSON文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_json(self, filepath):
        """加载JSON文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def clean_old_files(self, directory, days=7):
        """清理旧文件"""
        dir_path = Path(directory)
        if not dir_path.exists():
            return

        now = datetime.now()
        deleted_count = 0

        for filepath in dir_path.iterdir():
            if filepath.is_file():
                # 获取文件修改时间
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                # 计算天数差
                age = (now - mtime).days

                if age > days:
                    try:
                        filepath.unlink()
                        deleted_count += 1
                    except Exception:
                        pass

        return deleted_count

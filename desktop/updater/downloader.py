"""
更新下载器
"""
import os
import requests
from PyQt6.QtCore import QThread, pyqtSignal


class UpdateDownloader(QThread):
    """更新下载线程"""

    # 信号
    download_progress = pyqtSignal(int)  # 进度百分比
    download_completed = pyqtSignal(str)  # 下载文件路径
    download_failed = pyqtSignal(str)  # 错误消息

    def __init__(self, download_url, output_dir):
        super().__init__()
        self.download_url = download_url
        self.output_dir = output_dir
        self.output_file = os.path.join(output_dir, "update_installer.exe")

    def run(self):
        """运行下载"""
        try:
            # 流式下载
            response = requests.get(self.download_url, stream=True, timeout=300)
            response.raise_for_status()

            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))

            # 写入文件
            downloaded = 0
            with open(self.output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # 计算进度
                        if total_size > 0:
                            percent = int(downloaded * 100 / total_size)
                            self.download_progress.emit(percent)

            self.download_completed.emit(self.output_file)

        except requests.exceptions.RequestException as e:
            self.download_failed.emit(str(e))
        except Exception as e:
            self.download_failed.emit(str(e))

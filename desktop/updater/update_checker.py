"""
版本检查器 - 通过GitHub API检查更新
"""
import requests
from packaging import version
from PyQt6.QtCore import QThread, pyqtSignal, QCoreApplication


class UpdateChecker(QThread):
    """更新检查线程"""

    # 信号
    check_completed = pyqtSignal(dict)  # {status, current, latest, url, notes}
    check_failed = pyqtSignal(str)

    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
        self.github_api_url = "https://api.github.com/repos/Astwea/Perler_By_Banana/releases/latest"

    def run(self):
        """运行检查"""
        try:
            # 获取最新版本信息
            response = requests.get(self.github_api_url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 解析版本号
            latest_version_str = data.get('tag_name', '').lstrip('v')
            latest_url = data.get('html_url', '')
            release_notes = data.get('body', '')

            # 比较版本
            current = version.parse(self.current_version)
            latest = version.parse(latest_version_str)

            if latest > current:
                # 有新版本
                result = {
                    'status': 'update_available',
                    'current': self.current_version,
                    'latest': latest_version_str,
                    'url': latest_url,
                    'notes': release_notes
                }
            elif latest == current:
                # 已是最新
                result = {
                    'status': 'up_to_date',
                    'current': self.current_version,
                    'latest': latest_version_str
                }
            else:
                # 本地版本更新（开发版本）
                result = {
                    'status': 'dev_version',
                    'current': self.current_version,
                    'latest': latest_version_str
                }

            self.check_completed.emit(result)

        except requests.exceptions.Timeout:
            self.check_failed.emit(QCoreApplication.translate('UpdateChecker', "Network error, please check your connection"))
        except requests.exceptions.RequestException as e:
            self.check_failed.emit(f"{QCoreApplication.translate('UpdateChecker', 'Failed to check for updates')}: {str(e)}")
        except Exception as e:
            self.check_failed.emit(f"{QCoreApplication.translate('UpdateChecker', 'Failed to check for updates')}: {str(e)}")

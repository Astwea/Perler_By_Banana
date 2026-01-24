"""
桌面应用配置管理器
数据存储在安装目录
"""
import json
import os
from pathlib import Path


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        # 数据目录（安装目录下的data子目录）
        self.app_dir = Path(__file__).parent.parent
        self.data_dir = self.app_dir / 'data'
        self.config_file = self.data_dir / 'config.json'
        self.history_file = self.data_dir / 'history.json'
        self.user_data_dir = self.data_dir / 'user_data'

        # 确保目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.user_data_dir.mkdir(parents=True, exist_ok=True)

        # 配置数据
        self.config = self._load_config()

    def _load_config(self):
        """加载配置"""
        default_config = {
            'language': 'zh_CN',
            'theme': 'light_blue',
            'nano_banana_api_key': '',
            'nano_banana_base_url': 'https://api.grsai.com',
            'nano_banana_proxy': '',
            'auto_check_updates': True,
            'last_update_check': '',
            'skipped_version': '',
            'max_history_items': 100,
            'default_bead_size': 2.6,
            'default_max_dimension': 200,
            'default_target_colors': 20,
            'remember_last_params': True,
            'window_geometry': {},
            'nano_banana_model': 'nano-banana-fast',
            'nano_banana_image_size': '1K',
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    default_config.update(saved_config)
            except Exception:
                pass

        return default_config

    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get(self, key, default=None):
        """获取配置值"""
        return self.config.get(key, default)

    def set(self, key, value):
        """设置配置值"""
        self.config[key] = value
        self.save_config()

    # 便捷方法
    def get_language(self):
        """获取语言"""
        return self.get('language', 'zh_CN')

    def set_language(self, language):
        """设置语言"""
        self.set('language', language)

    def get_theme(self):
        """获取主题"""
        return self.get('theme', 'light_blue')

    def set_theme(self, theme):
        """设置主题"""
        self.set('theme', theme)

    def get_nano_banana_config(self):
        """获取Nano Banana配置"""
        return {
            'api_key': self.get('nano_banana_api_key', ''),
            'base_url': self.get('nano_banana_base_url', 'https://api.grsai.com'),
            'proxy': self.get('nano_banana_proxy', ''),
        }

    def set_nano_banana_config(self, api_key, base_url, proxy):
        """设置Nano Banana配置"""
        self.set('nano_banana_api_key', api_key)
        self.set('nano_banana_base_url', base_url)
        self.set('nano_banana_proxy', proxy)

    def should_auto_check_updates(self):
        """是否自动检查更新"""
        return self.get('auto_check_updates', True)

    def set_last_update_check(self, date_str):
        """设置最后更新检查时间"""
        self.set('last_update_check', date_str)

    def get_skipped_version(self):
        """获取跳过的版本"""
        return self.get('skipped_version', '')

    def set_skipped_version(self, version):
        """设置跳过的版本"""
        self.set('skipped_version', version)

    def get_window_geometry(self):
        """获取窗口几何信息"""
        return self.get('window_geometry', {})

    def set_window_geometry(self, geometry):
        """设置窗口几何信息"""
        self.set('window_geometry', geometry)

    # 历史记录管理
    def add_history_item(self, item):
        """添加历史记录"""
        history = self.get_history()
        history.insert(0, item)  # 添加到开头

        # 限制数量
        max_items = self.get('max_history_items', 100)
        if len(history) > max_items:
            history = history[:max_items]

        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get_history(self):
        """获取历史记录"""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def clear_history(self):
        """清空历史记录"""
        if self.history_file.exists():
            self.history_file.unlink()

    def get_data_dir(self):
        """获取数据目录"""
        return str(self.data_dir)

    def get_user_data_dir(self):
        """获取用户数据目录"""
        return str(self.user_data_dir)

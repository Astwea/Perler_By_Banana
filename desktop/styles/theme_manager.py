"""
主题管理器
"""
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor


class ThemeManager:
    """主题管理器"""

    def __init__(self):
        self.colors = self._load_colors()

    def _load_colors(self):
        """加载颜色配置"""
        colors_path = Path(__file__).parent.parent / 'resources' / 'styles' / 'colors.json'

        default_colors = {
            "primary": "#4A90E2",
            "primaryLight": "#7DB3F0",
            "primaryDark": "#357ABD",
            "accent": "#50E3C2",
            "background": "#F5F9FF",
            "surface": "#FFFFFF",
            "textPrimary": "#2C3E50",
            "textSecondary": "#7F8C8D",
            "border": "#E1E8F0",
            "success": "#2ECC71",
            "warning": "#F39C12",
            "error": "#E74C3C",
            "shadow": "rgba(74, 144, 226, 0.15)"
        }

        if colors_path.exists():
            try:
                with open(colors_path, 'r', encoding='utf-8') as f:
                    default_colors.update(json.load(f))
            except Exception:
                pass

        return default_colors

    def apply_light_blue_theme(self):
        """应用浅蓝色主题"""
        qss_path = Path(__file__).parent.parent / 'resources' / 'styles' / 'light_blue.qss'

        if qss_path.exists():
            with open(qss_path, 'r', encoding='utf-8') as f:
                qss = f.read()

            app = QApplication.instance()
            app.setStyleSheet(qss)

            # Set the palette colors explicitly to keep text from turning white on some systems.
            palette = app.palette()
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#2C3E50"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#2C3E50"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#E8F2FF"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#2C3E50"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#F5F9FF"))
            app.setPalette(palette)

    def get_color(self, name):
        """获取颜色值"""
        return self.colors.get(name)

"""
拼豆图案生成系统 - 桌面应用入口
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop.main_window import MainWindow
from desktop.styles.theme_manager import ThemeManager
from desktop.config import ConfigManager


def main():
    # 创建应用
    app = QApplication(sys.argv)

    # 设置应用信息
    app.setApplicationName("拼豆图案生成系统")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PerlerByBanana")

    # 设置字体
    font = QFont("Microsoft YaHei UI", 10)
    app.setFont(font)

    # 配置管理器
    config = ConfigManager()

    # 应用主题
    theme_manager = ThemeManager()
    theme_manager.apply_light_blue_theme()

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 运行
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

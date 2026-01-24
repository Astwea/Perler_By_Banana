"""
主窗口
"""
import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QLabel, QMessageBox, QMenuBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QAction
from pathlib import Path

from .widgets.sidebar import Sidebar
from .widgets.pages import (
    UploadPage, ParameterPage, ProcessPage, ResultPage,
    PalettePage, HistoryPage, SettingsPage
)
from .config import ConfigManager
from .styles.theme_manager import ThemeManager
from .i18n.translator import Translator


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.current_file = None
        self.process_results = {}
        self.config = ConfigManager()
        self.theme_manager = ThemeManager()
        self.translator = Translator()
        self.init_ui()
        self.setup_menu_bar()
        self.apply_settings()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('拼豆图案生成系统 / Perler Pattern Generator System')
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # 设置窗口图标
        icon_path = self._get_resource_path('icons/app_icon.ico')
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 侧边栏
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self.on_page_changed)

        # 内容区域（堆栈窗口）
        self.content_stack = QStackedWidget()

        # 创建所有页面组件
        self.upload_page = UploadPage()
        self.parameter_page = ParameterPage()
        self.process_page = ProcessPage()
        self.result_page = ResultPage()
        self.palette_page = PalettePage()
        self.history_page = HistoryPage()
        self.settings_page = SettingsPage()

        # 连接信号
        self.upload_page.image_loaded.connect(self.on_image_loaded)
        self.upload_page.continue_btn.clicked.connect(lambda: self.on_page_changed('parameter'))
        self.parameter_page.params_changed.connect(self.on_params_changed)
        self.process_page.process_completed.connect(self.on_process_completed)
        self.result_page.export_requested.connect(self.on_export_requested)
        self.history_page.history_selected.connect(self.on_history_selected)

        # 添加到堆栈
        self.content_stack.addWidget(self.upload_page)
        self.content_stack.addWidget(self.parameter_page)
        self.content_stack.addWidget(self.process_page)
        self.content_stack.addWidget(self.result_page)
        self.content_stack.addWidget(self.palette_page)
        self.content_stack.addWidget(self.history_page)
        self.content_stack.addWidget(self.settings_page)

        # 添加到布局
        main_layout.addWidget(self.sidebar, 1)  # 20%宽度
        main_layout.addWidget(self.content_stack, 4)  # 80%宽度

    def on_page_changed(self, page_name):
        """页面切换"""
        page_map = {
            'upload': 0,
            'parameter': 1,
            'process': 2,
            'result': 3,
            'palette': 4,
            'history': 5,
            'settings': 6
        }

        if page_name in page_map:
            self.content_stack.setCurrentIndex(page_map[page_name])
            self.sidebar.set_active_page(page_name)

    def on_image_loaded(self, image_path: str, image_info: dict):
        """图片加载事件"""
        self.current_file = image_path
        self.process_results['image_info'] = image_info
        print(f"Image loaded: {image_path}")

    def on_params_changed(self, params: dict):
        """参数变更事件"""
        self.process_results['params'] = params
        print(f"Params changed: {params}")

    def on_process_completed(self, results: dict):
        """处理完成事件"""
        self.process_results.update(results)
        # 切换到结果页面
        self.on_page_changed('result')

    def on_export_requested(self, export_info: tuple):
        """导出请求事件"""
        format_type, file_path = export_info
        print(f"Export requested: {format_type} to {file_path}")
        # TODO: 实际导出逻辑

    def on_history_selected(self, path: str):
        """历史记录选中事件"""
        print(f"History selected: {path}")
        # TODO: 加载历史项目

    def setup_menu_bar(self):
        """设置菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件 / File')

        new_action = QAction('新建项目 (Ctrl+N)', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.on_new_project)
        file_menu.addAction(new_action)

        open_action = QAction('打开最近 (Ctrl+O)', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.on_open_recent)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction('退出 (Ctrl+Q)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 设置菜单
        settings_menu = menubar.addMenu('设置 / Settings')

        language_action = QAction('语言 / Language', self)
        language_menu = settings_menu.addMenu('语言 / Language')

        zh_cn_action = QAction('简体中文', self)
        zh_cn_action.triggered.connect(lambda: self.change_language('zh_CN'))
        language_menu.addAction(zh_cn_action)

        en_us_action = QAction('English', self)
        en_us_action.triggered.connect(lambda: self.change_language('en_US'))
        language_menu.addAction(en_us_action)

        check_update_action = QAction('检查更新 / Check for Updates', self)
        check_update_action.triggered.connect(self.on_check_updates)
        settings_menu.addAction(check_update_action)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助 / Help')

        about_action = QAction('关于 (Ctrl+A)', self)
        about_action.setShortcut('Ctrl+A')
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def on_new_project(self):
        """新建项目"""
        self.current_file = None
        self.process_results = {}
        self.on_page_changed('upload')
        self.upload_page.clear_image()

    def on_open_recent(self):
        """打开最近项目"""
        self.on_page_changed('history')

    def on_check_updates(self):
        """检查更新"""
        # TODO: 实现更新对话框
        QMessageBox.information(self, '提示 / Info', '更新功能正在开发中...')

    def on_about(self):
        """关于对话框"""
        QMessageBox.about(
            self,
            "关于拼豆图案生成系统 / About",
            """
            <h3>拼豆图案生成系统 v1.0.0</h3>
            <p>Perler Pattern Generator System v1.0.0</p>
            <p>一款专业的拼豆图案生成工具</p>
            <p>A professional perler bead pattern generation tool</p>
            <p>支持AI图像转换、智能颜色匹配、图案优化等功能</p>
            <p>Supports AI image conversion, intelligent color matching, pattern optimization and more</p>
            <hr/>
            <p>© 2024 PerlerByBanana</p>
            """
        )

    def apply_settings(self):
        """应用设置"""
        # 应用主题
        self.theme_manager.apply_light_blue_theme()

        # 应用语言
        language = self.config.get_language()
        self.translator.load_language(language)

    def change_language(self, language):
        """切换语言"""
        self.config.set_language(language)
        self.translator.load_language(language)
        QMessageBox.information(self, '提示 / Info', f'已切换到 {language}')

    def closeEvent(self, event):
        """关闭事件"""
        # 保存窗口位置
        geometry = {
            'x': self.x(),
            'y': self.y(),
            'width': self.width(),
            'height': self.height(),
            'maximized': self.isMaximized()
        }
        self.config.set_window_geometry(geometry)

        event.accept()

    def _get_resource_path(self, relative_path):
        """获取资源文件路径"""
        try:
            # PyInstaller打包后的路径
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        path = os.path.join(base_path, 'resources', relative_path)
        return path if os.path.exists(path) else None

"""
侧边栏组件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QButtonGroup, QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class Sidebar(QWidget):
    """侧边栏"""

    page_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 'upload'
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setFixedWidth(240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(8)

        # Logo区域
        logo_label = QLabel("🎨 拼豆助手")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setFont(QFont("Microsoft YaHei UI", 18, QFont.Weight.Bold))
        logo_label.setStyleSheet("""
            QLabel {
                color: #4A90E2;
                padding: 20px 0;
                background: linear-gradient(135deg, #FFFFFF, #F5F9FF);
                border-radius: 12px;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(logo_label)

        # 导航按钮
        self.btn_group = QButtonGroup(self)

        self.upload_btn = self.create_nav_button("📁 上传图片", "upload")
        self.param_btn = self.create_nav_button("⚙️ 参数设置", "parameter")
        self.process_btn = self.create_nav_button("🔄 处理流程", "process")
        self.result_btn = self.create_nav_button("📊 处理结果", "result")
        self.palette_btn = self.create_nav_button("🎨 色板管理", "palette")
        self.history_btn = self.create_nav_button("📜 历史记录", "history")

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background: #E1E8F0;")
        layout.addWidget(separator)

        # 设置按钮
        self.settings_btn = self.create_nav_button("⚙️ 系统设置", "settings")

        # 底部弹簧
        layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        # 默认选中
        self.upload_btn.setChecked(True)

    def create_nav_button(self, text, page_name):
        """创建导航按钮"""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setProperty("page", page_name)
        btn.setMinimumHeight(45)

        # 样式
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 12px 18px;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                color: #7F8C8D;
                background: transparent;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #E8F2FF;
                color: #4A90E2;
            }
            QPushButton:checked {
                background: linear-gradient(135deg, #4A90E2, #7DB3F0);
                color: white;
                font-weight: bold;
            }
        """)

        self.btn_group.addButton(btn)
        btn.clicked.connect(lambda: self.page_changed.emit(page_name))
        self.layout().addWidget(btn)
        return btn

    def set_active_page(self, page_name):
        """设置当前激活页面"""
        buttons = {
            'upload': self.upload_btn,
            'parameter': self.param_btn,
            'process': self.process_btn,
            'result': self.result_btn,
            'palette': self.palette_btn,
            'history': self.history_btn,
            'settings': self.settings_btn
        }

        if page_name in buttons:
            self.current_page = page_name
            for btn_name, btn in buttons.items():
                btn.setChecked(btn_name == page_name)

"""
处理流程页面组件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QGroupBox, QTextEdit,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from enum import Enum


class ProcessStep(Enum):
    """处理步骤"""
    AI_CONVERSION = "AI增强 / AI Enhancement"
    PREPROCESSING = "预处理 / Preprocessing"
    PATTERN_GENERATION = "图案生成 / Pattern Generation"
    PREVIEW_GENERATION = "预览生成 / Preview Generation"
    COMPLETE = "完成 / Complete"


class ProcessPage(QWidget):
    """处理流程页面"""

    process_completed = pyqtSignal(dict)  # 处理完成信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("🔄 处理流程 / Processing")
        title_label.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 状态区域
        status_group = QGroupBox("处理状态 / Status")
        status_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        status_layout = QVBoxLayout(status_group)
        status_layout.setContentsMargins(15, 15, 15, 15)

        # 当前步骤
        self.step_label = QLabel("准备就绪 / Ready")
        self.step_label.setFont(QFont("Microsoft YaHei UI", 14))
        self.step_label.setStyleSheet("color: #4A90E2;")
        status_layout.addWidget(self.step_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        status_layout.addWidget(self.progress_bar)

        layout.addWidget(status_group)

        # 日志区域
        log_group = QGroupBox("处理日志 / Log")
        log_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(15, 15, 15, 15)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(300)
        self.log_text.setFont(QFont("Consolas", 10))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #F5F9FF;
                border: 1px solid #E1E8F0;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_group)

        # 底部弹簧
        layout.addStretch()

        # 操作按钮
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶️ 开始处理 / Start Processing")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.clicked.connect(self.on_start_clicked)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹️ 停止 / Stop")
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setProperty("class", "danger")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        btn_layout.addWidget(self.stop_btn)

        layout.addLayout(btn_layout)

        # 一键执行按钮
        execute_all_btn = QPushButton("🚀 一键执行所有步骤 / Execute All Steps")
        execute_all_btn.setMinimumHeight(50)
        execute_all_btn.setProperty("class", "success")
        execute_all_btn.clicked.connect(self.on_execute_all_clicked)
        layout.addWidget(execute_all_btn)

    def on_start_clicked(self):
        """开始处理按钮点击事件"""
        self.log_message("开始处理 / Start processing...")
        self.progress_bar.setValue(10)
        self.step_label.setText("预处理 / Preprocessing")
        # TODO: 实际处理逻辑
        self.simulate_processing()

    def on_execute_all_clicked(self):
        """一键执行所有步骤按钮点击事件"""
        self.log_message("一键执行所有步骤 / Execute all steps...")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.simulate_processing()

    def on_stop_clicked(self):
        """停止按钮点击事件"""
        self.log_message("已停止 / Stopped")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.step_label.setText("已停止 / Stopped")

    def simulate_processing(self):
        """模拟处理过程"""
        import time

        steps = [
            (20, "预处理 / Preprocessing", "正在加载图像..."),
            (40, "预处理 / Preprocessing", "应用降噪和对比度调整..."),
            (60, "颜色匹配 / Color Matching", "匹配拼豆色板颜色..."),
            (80, "图案生成 / Pattern Generation", "生成拼豆图案网格..."),
            (100, "完成 / Complete", "处理完成！")
        ]

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        for progress, step, message in steps:
            if not self.stop_btn.isEnabled():
                break

            self.progress_bar.setValue(progress)
            self.step_label.setText(step)
            self.log_message(message)
            QApplication.instance().processEvents()

        if self.stop_btn.isEnabled():
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.process_completed.emit({})

    def log_message(self, message: str):
        """记录日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def set_step(self, step: ProcessStep):
        """设置当前步骤"""
        self.current_step = step
        self.step_label.setText(step.value)

    def set_progress(self, value: int):
        """设置进度"""
        self.progress_bar.setValue(value)

    def reset(self):
        """重置状态"""
        self.log_text.clear()
        self.progress_bar.setValue(0)
        self.step_label.setText("准备就绪 / Ready")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def log_error(self, message: str):
        """记录错误日志"""
        self.log_message(f"❌ 错误 / Error: {message}")
        self.step_label.setText(f"错误 / Error: {message}")
        self.step_label.setStyleSheet("color: #E74C3C;")

    def log_success(self, message: str):
        """记录成功日志"""
        self.log_message(f"✅ {message}")
        self.step_label.setStyleSheet("color: #2ECC71;")


# 修正导入
from PyQt6.QtWidgets import QApplication

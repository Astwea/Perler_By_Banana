"""
上传图片页面组件
"""
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QGroupBox, QScrollArea
)
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QPixmap, QImage, QFont, QDragEnterEvent, QDropEvent
from PIL import Image as PILImage


class UploadPage(QWidget):
    """上传图片页面"""

    image_loaded = pyqtSignal(str, dict)  # 图片路径, 图片信息

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image_path = None
        self.current_image = None
        self.image_info = {}
        self.setAcceptDrops(True)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("上传图片 / Upload Image")
        title_label.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2C3E50 !important;")
        layout.addWidget(title_label)

        # 说明文字
        info_label = QLabel(
            "支持 PNG、JPG、JPEG 等常见图像格式\n"
            "Supported formats: PNG, JPG, JPEG, etc."
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #5A6C7D !important; font-size: 14px;")
        layout.addWidget(info_label)

        # 上传区域
        upload_group = QGroupBox()
        upload_group.setStyleSheet("""
            QGroupBox {
                border: 2px dashed #E1E8F0;
                border-radius: 12px;
                background: #FFFFFF;
                margin-top: 10px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #4A90E2;
                font-weight: bold;
            }
        """)
        upload_layout = QVBoxLayout(upload_group)
        upload_layout.setContentsMargins(30, 30, 30, 30)
        upload_layout.setSpacing(20)

        # 图片预览区域
        self.image_label = QLabel()
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setMaximumSize(600, 450)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background: #F5F9FF;
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                color: #2C3E50;
                font-size: 16px;
            }
        """)
        self.image_label.setText("暂无图片 / No Image\n点击此区域或拖拽图片上传")
        self.image_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.image_label.mousePressEvent = self._on_preview_clicked
        self.image_label.setWordWrap(True)
        upload_layout.addWidget(self.image_label, 0, Qt.AlignmentFlag.AlignCenter)

        # 滚动区域包装
        scroll = QScrollArea()
        scroll.setWidget(upload_group)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(scroll)

        # 图片信息区域
        self.info_group = QGroupBox("图片信息 / Image Information")
        self.info_group.setVisible(False)
        self.info_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        info_layout = QVBoxLayout(self.info_group)
        info_layout.setContentsMargins(15, 15, 15, 15)

        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #2C3E50; font-size: 14px;")
        info_layout.addWidget(self.info_label)

        layout.addWidget(self.info_group)

        # 底部弹簧
        layout.addStretch()

        # 操作按钮
        btn_layout = QHBoxLayout()

        self.clear_btn = QPushButton("清除 / Clear")
        self.clear_btn.setMinimumHeight(45)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setProperty("class", "secondary")
        self.clear_btn.setEnabled(False)
        self.clear_btn.clicked.connect(self.on_clear_clicked)
        btn_layout.addWidget(self.clear_btn)

        self.continue_btn = QPushButton("继续 / Continue")
        self.continue_btn.setMinimumHeight(45)
        self.continue_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.continue_btn.setEnabled(False)
        self.continue_btn.setStyleSheet("""
            QPushButton {
                background: #E1E8F0;
                border: 2px solid #D4DBE4;
                border-radius: 8px;
                color: #2C3E50;
                font-weight: 600;
            }
            QPushButton:pressed {
                background: #CCD5E0;
            }
            QPushButton:disabled {
                background: #F5F7FF;
                color: #94A0B2;
                border-color: #E1E8F0;
            }
        """)
        self.continue_btn.clicked.connect(self.on_continue_clicked)
        btn_layout.addWidget(self.continue_btn)

        layout.addLayout(btn_layout)

    def on_upload_clicked(self):
        """上传按钮点击事件"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("选择图片 / Choose Image")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)")

        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            if files:
                self.load_image(files[0])

    def _on_preview_clicked(self, event):
        """图片区域点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_upload_clicked()

    def load_image(self, image_path: str):
        """加载图片"""
        try:
            # 使用 PIL 加载图片
            self.current_image = PILImage.open(image_path)
            self.current_image_path = image_path

            # 获取图片信息
            self.image_info = {
                'path': image_path,
                'filename': os.path.basename(image_path),
                'format': self.current_image.format,
                'mode': self.current_image.mode,
                'size': self.current_image.size,
                'width': self.current_image.width,
                'height': self.current_image.height
            }

            # 显示预览
            self.display_preview(image_path)

            # 显示图片信息
            self.display_info()

            # 启用按钮
            self.clear_btn.setEnabled(True)
            self.continue_btn.setEnabled(True)

            # 发送信号
            self.image_loaded.emit(image_path, self.image_info)

        except Exception as e:
            self.show_error(f"加载图片失败 / Failed to load image: {str(e)}")

    def display_preview(self, image_path: str):
        """显示图片预览"""
        try:
            pixmap = QPixmap(image_path)

            scaled_pixmap = pixmap.scaled(
                600, 450,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            self.image_label.setPixmap(scaled_pixmap)

        except Exception as e:
            self.show_error(f"显示预览失败 / Failed to display preview: {str(e)}")

    def display_info(self):
        """显示图片信息"""
        info_text = f"""
        <b>文件名 / Filename:</b> {self.image_info['filename']}<br>
        <b>格式 / Format:</b> {self.image_info['format']}<br>
        <b>尺寸 / Size:</b> {self.image_info['width']} x {self.image_info['height']} 像素 / pixels<br>
        <b>颜色模式 / Color Mode:</b> {self.image_info['mode']}<br>
        <b>文件路径 / Path:</b> {self.image_info['path']}
        """
        self.info_label.setText(info_text.strip())
        self.info_group.setVisible(True)

    def on_clear_clicked(self):
        """清除按钮点击事件"""
        self.clear_image()

    def clear_image(self):
        """清除图片"""
        self.current_image = None
        self.current_image_path = None
        self.image_info = {}

        # 重置UI
        self.image_label.clear()
        self.image_label.setText("暂无图片 / No Image\n点击此区域或拖拽图片上传")
        self.info_label.clear()
        self.info_group.setVisible(False)

        # 禁用按钮
        self.clear_btn.setEnabled(False)
        self.continue_btn.setEnabled(False)

    def on_continue_clicked(self):
        """继续按钮点击事件"""
        # 这个信号会被主窗口捕获，用于切换到参数设置页面
        pass

    def show_error(self, message: str):
        """显示错误信息"""
        self.image_label.setText(f"❌ {message}")

    def get_current_image_path(self) -> str:
        """获取当前图片路径"""
        return self.current_image_path or ""

    def get_current_image(self):
        """获取当前图片对象"""
        return self.current_image

    def get_image_info(self) -> dict:
        """获取图片信息"""
        return self.image_info

    def dragEnterEvent(self, a0: Optional[QDragEnterEvent]):
        """拖拽进入事件"""
        if not a0:
            return
        mime_data = a0.mimeData()
        if mime_data and mime_data.hasUrls():
            urls = mime_data.urls()
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                        a0.acceptProposedAction()
                        self.image_label.setStyleSheet("""
            QLabel {
                background: #E8F2FF;
                border: 2px dashed #4A90E2;
                border-radius: 8px;
                color: #4A90E2;
                font-size: 16px;
                font-weight: bold;
            }
        """)
                        return
        a0.ignore()

    def dragLeaveEvent(self, a0):
        """拖拽离开事件"""
        if not self.current_image_path:
            self.image_label.setStyleSheet("""
            QLabel {
                background: #F5F9FF;
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                color: #2C3E50;
                font-size: 16px;
            }
        """)

    def dropEvent(self, a0: Optional[QDropEvent]):
        """拖拽放下事件"""
        if not a0:
            return
        self.image_label.setStyleSheet("""
            QLabel {
                background: #F5F9FF;
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                color: #2C3E50;
                font-size: 16px;
            }
        """)
        
        mime_data = a0.mimeData()
        if mime_data:
            urls = mime_data.urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                    self.load_image(file_path)
                    a0.acceptProposedAction()
                else:
                    self.show_error("不支持的文件格式 / Unsupported file format")
                    a0.ignore()
            else:
                a0.ignore()
        else:
            a0.ignore()

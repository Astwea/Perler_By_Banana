"""
处理结果页面组件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QScrollArea, QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
import os


class ResultPage(QWidget):
    """处理结果页面"""

    export_requested = pyqtSignal(str)  # 导出请求信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pattern_data = None
        self.pattern_image = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("📊 处理结果 / Result")
        title_label.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 统计信息区域
        self.stats_group = QGroupBox("图案统计 / Pattern Statistics")
        self.stats_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        stats_layout = QVBoxLayout(self.stats_group)
        stats_layout.setContentsMargins(15, 15, 15, 15)

        self.stats_label = QLabel("暂无数据 / No Data")
        self.stats_label.setWordWrap(True)
        self.stats_label.setFont(QFont("Microsoft YaHei UI", 12))
        stats_layout.addWidget(self.stats_label)

        layout.addWidget(self.stats_group)

        # 图案预览区域
        preview_group = QGroupBox("图案预览 / Pattern Preview")
        preview_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(15, 15, 15, 15)

        # 图片显示标签
        self.image_label = QLabel()
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background: #F5F9FF;
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                color: #7F8C8D;
                font-size: 16px;
            }
        """)
        self.image_label.setText("暂无图案 / No Pattern")
        preview_layout.addWidget(self.image_label)

        # 缩放控制
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("缩放 / Zoom:")
        zoom_layout.addWidget(zoom_label)

        self.zoom_out_btn = QPushButton("➖")
        self.zoom_out_btn.setMinimumWidth(40)
        self.zoom_out_btn.clicked.connect(self.on_zoom_out)
        zoom_layout.addWidget(self.zoom_out_btn)

        self.zoom_value_label = QLabel("100%")
        self.zoom_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_value_label.setMinimumWidth(50)
        zoom_layout.addWidget(self.zoom_value_label)

        self.zoom_in_btn = QPushButton("➕")
        self.zoom_in_btn.setMinimumWidth(40)
        self.zoom_in_btn.clicked.connect(self.on_zoom_in)
        zoom_layout.addWidget(self.zoom_in_btn)

        self.zoom_reset_btn = QPushButton("↺")
        self.zoom_reset_btn.setMinimumWidth(40)
        self.zoom_reset_btn.clicked.connect(self.on_zoom_reset)
        zoom_layout.addWidget(self.zoom_reset_btn)

        self.toggle_numbers_btn = QPushButton("🔢 显示编号")
        self.toggle_numbers_btn.clicked.connect(self.on_toggle_numbers)
        zoom_layout.addWidget(self.toggle_numbers_btn)

        zoom_layout.addStretch()
        preview_layout.addLayout(zoom_layout)

        # 滚动区域包装
        scroll = QScrollArea()
        scroll.setWidget(preview_group)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(scroll)

        # 底部弹簧
        layout.addStretch()

        # 导出按钮区域
        export_group = QGroupBox("导出 / Export")
        export_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        export_layout = QHBoxLayout(export_group)
        export_layout.setContentsMargins(15, 15, 15, 15)

        export_json_btn = QPushButton("📄 导出JSON")
        export_json_btn.clicked.connect(lambda: self.on_export('json'))
        export_layout.addWidget(export_json_btn)

        export_csv_btn = QPushButton("📊 导出CSV")
        export_csv_btn.clicked.connect(lambda: self.on_export('csv'))
        export_layout.addWidget(export_csv_btn)

        export_png_btn = QPushButton("🖼️ 导出PNG")
        export_png_btn.clicked.connect(lambda: self.on_export('png'))
        export_layout.addWidget(export_png_btn)

        export_pdf_btn = QPushButton("📑 生成PDF")
        export_pdf_btn.clicked.connect(lambda: self.on_export('pdf'))
        export_layout.addWidget(export_pdf_btn)

        layout.addWidget(export_group)

    def set_pattern_data(self, data: dict, image_path: str = None):
        """设置图案数据"""
        self.pattern_data = data

        # 更新统计信息
        if data:
            stats_text = f"""
            <b>图案尺寸 / Pattern Size:</b> {data.get('width', 0)} x {data.get('height', 0)} 拼豆 / beads<br>
            <b>颜色数量 / Color Count:</b> {data.get('color_count', 0)}<br>
            <b>拼豆总数 / Total Beads:</b> {data.get('total_beads', 0)}<br>
            <b>拼豆类型 / Bead Type:</b> {data.get('bead_size', '5.0mm')}
            """
            self.stats_label.setText(stats_text.strip())

            # 显示图片
            if image_path and os.path.exists(image_path):
                self.display_image(image_path)
        else:
            self.stats_label.setText("暂无数据 / No Data")

    def display_image(self, image_path: str):
        """显示图片"""
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.pattern_image = pixmap
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
        except Exception as e:
            self.image_label.setText(f"❌ 显示失败 / Failed to display: {str(e)}")

    def on_zoom_in(self):
        """放大"""
        if self.pattern_image:
            current_scale = self.zoom_value_label.text().replace('%', '')
            try:
                scale = int(current_scale) + 25
                if scale <= 300:
                    self.update_zoom(scale)
            except ValueError:
                self.update_zoom(100)

    def on_zoom_out(self):
        """缩小"""
        if self.pattern_image:
            current_scale = self.zoom_value_label.text().replace('%', '')
            try:
                scale = int(current_scale) - 25
                if scale >= 25:
                    self.update_zoom(scale)
            except ValueError:
                self.update_zoom(100)

    def on_zoom_reset(self):
        """重置缩放"""
        self.update_zoom(100)

    def update_zoom(self, scale: int):
        """更新缩放"""
        if self.pattern_image:
            scaled_pixmap = self.pattern_image.scaled(
                self.pattern_image.size() * scale // 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.zoom_value_label.setText(f"{scale}%")

    def on_toggle_numbers(self):
        """切换编号显示"""
        self.toggle_numbers_btn.setText("🔢 隐藏编号" if "显示" in self.toggle_numbers_btn.text() else "🔢 显示编号")
        # TODO: 实现编号显示切换逻辑

    def on_export(self, format_type: str):
        """导出文件"""
        if not self.pattern_data:
            QMessageBox.warning(self, "警告 / Warning", "请先生成图案 / Please generate pattern first")
            return

        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle(f"导出{format_type.upper()} / Export {format_type.upper()}")

        if format_type == 'json':
            file_dialog.setNameFilter("JSON Files (*.json)")
        elif format_type == 'csv':
            file_dialog.setNameFilter("CSV Files (*.csv)")
        elif format_type == 'png':
            file_dialog.setNameFilter("PNG Files (*.png)")
        elif format_type == 'pdf':
            file_dialog.setNameFilter("PDF Files (*.pdf)")

        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.export_requested.emit((format_type, file_path))
            QMessageBox.information(self, "成功 / Success", f"已导出到 {file_path}")

    def reset(self):
        """重置页面"""
        self.pattern_data = None
        self.pattern_image = None
        self.stats_label.setText("暂无数据 / No Data")
        self.image_label.clear()
        self.image_label.setText("暂无图案 / No Pattern")
        self.update_zoom(100)

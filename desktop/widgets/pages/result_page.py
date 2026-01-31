"""
处理结果页面组件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QScrollArea, QFileDialog,
    QMessageBox, QProgressDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QSplitter, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QSize
from PyQt6.QtGui import QPixmap, QFont, QColor, QBrush
from typing import Optional, Dict
import os
import threading
import shutil
import json
import csv


class ResultPage(QWidget):
    """处理结果页面"""

    export_requested = pyqtSignal(tuple)  # 导出请求信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pattern_data = None
        self.pattern_image = None
        self.pattern_object = None
        self.pattern_path_with_labels = None
        self.pattern_path_no_labels = None
        self._export_thread = None
        self._progress_dialog = None
        self._worker_ref = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("📊 处理结果 / Result")
        title_label.setFont(QFont("Microsoft YaHei UI", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("padding: 10px;")
        layout.addWidget(title_label)

        self.stats_group = QGroupBox("图案统计 / Pattern Statistics")
        self.stats_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 5px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        stats_layout = QVBoxLayout(self.stats_group)
        stats_layout.setContentsMargins(15, 15, 15, 15)

        self.stats_label = QLabel("暂无数据 / No Data")
        self.stats_label.setWordWrap(True)
        self.stats_label.setFont(QFont("Microsoft YaHei UI", 11))
        stats_layout.addWidget(self.stats_label)

        layout.addWidget(self.stats_group)

        self.color_list_group = QGroupBox("📋 色号使用清单 / Color Usage List")
        self.color_list_group.setMaximumHeight(400)
        self.color_list_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 5px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        color_list_layout = QVBoxLayout(self.color_list_group)
        color_list_layout.setContentsMargins(15, 15, 15, 15)

        self.color_summary_label = QLabel("暂无数据 / No Data")
        self.color_summary_label.setWordWrap(True)
        self.color_summary_label.setFont(QFont("Microsoft YaHei UI", 11))
        self.color_summary_label.setStyleSheet("background: #F5F9FF; padding: 10px; border-radius: 5px; border: 1px solid #E1E8F0;")
        color_list_layout.addWidget(self.color_summary_label)

        self.color_table = QTableWidget()
        self.color_table.setColumnCount(5)
        self.color_table.setHorizontalHeaderLabels(["颜色", "色号", "数量", "占比", "进度"])

        self.color_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E1E8F0;
                border-radius: 5px;
                background: white;
                gridline-color: #E1E8F0;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px 5px;
                border: none;
            }
            QTableWidget::item:selected {
                background: #E3F2FD;
                color: #1976D2;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                padding: 10px 5px;
                border: none;
                font-weight: 700;
                font-size: 13px;
            }
            QTableWidget::verticalHeader {
                background: #F5F9FF;
            }
        """)

        header = self.color_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
            header.setMinimumSectionSize(50)

        self.color_table.setColumnWidth(0, 60)
        self.color_table.setColumnWidth(1, 80)
        self.color_table.setColumnWidth(2, 70)
        self.color_table.setColumnWidth(3, 70)
        self.color_table.setColumnWidth(4, 120)

        self.color_table.setAlternatingRowColors(True)
        self.color_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.color_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.color_table.verticalHeader().setVisible(False)
        self.color_table.verticalHeader().setDefaultSectionSize(35)

        color_list_layout.addWidget(self.color_table)

        layout.addWidget(self.color_list_group)

        preview_group = QGroupBox("图案预览 / Pattern Preview")
        preview_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 5px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(15, 15, 15, 15)

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

        layout.addWidget(preview_group)

        export_group = QGroupBox("导出 / Export")
        export_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 5px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        export_layout = QHBoxLayout(export_group)
        export_layout.setContentsMargins(15, 15, 15, 15)

        self.export_json_btn = QPushButton("📄 导出JSON")
        self.export_json_btn.clicked.connect(lambda: self.on_export('json'))
        export_layout.addWidget(self.export_json_btn)

        self.export_csv_btn = QPushButton("📊 导出CSV")
        self.export_csv_btn.clicked.connect(lambda: self.on_export('csv'))
        export_layout.addWidget(self.export_csv_btn)

        self.export_png_btn = QPushButton("🖼️ 导出PNG")
        self.export_png_btn.clicked.connect(lambda: self.on_export('png'))
        export_layout.addWidget(self.export_png_btn)

        self.export_technical_btn = QPushButton("📋 导出工程图")
        self.export_technical_btn.clicked.connect(lambda: self.on_export('technical'))
        export_layout.addWidget(self.export_technical_btn)

        self.export_pdf_btn = QPushButton("📑 生成PDF")
        self.export_pdf_btn.clicked.connect(lambda: self.on_export('pdf'))
        export_layout.addWidget(self.export_pdf_btn)

        layout.addWidget(export_group)
        layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def set_pattern_data(self, data: Dict, image_path: Optional[str] = None):
        """设置图案数据"""
        self.pattern_data = data

        # 更新统计信息
        if data:
            subject_width = data.get('subject_width', 0)
            subject_height = data.get('subject_height', 0)
            subject_width_mm = data.get('subject_width_mm', 0.0)
            subject_height_mm = data.get('subject_height_mm', 0.0)

            stats_text = f"""
            <b>图案尺寸 / Pattern Size:</b> {subject_width} x {subject_height} 拼豆 / beads<br>
            <b>拼豆尺寸 / Bead Size:</b> {subject_width_mm / 10:.1f} x {subject_height_mm / 10:.1f} cm<br>
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

    def set_pattern_images(self, image_path_no_labels: Optional[str], image_path_with_labels: Optional[str] = None) -> None:
        """设置图案预览图片路径"""
        self.pattern_path_no_labels = image_path_no_labels
        self.pattern_path_with_labels = image_path_with_labels
        if image_path_no_labels and os.path.exists(image_path_no_labels):
            self.display_image(image_path_no_labels)

    def set_pattern_object(self, bead_pattern) -> None:
        """设置图案对象（用于高质量导出）"""
        self.pattern_object = bead_pattern

    def set_color_statistics(self, color_counts: Dict, color_details: Dict, total_beads: int) -> None:
        """设置并显示色号使用清单"""
        if not color_counts or total_beads == 0:
            self.color_table.setRowCount(0)
            self.color_summary_label.setText("暂无颜色数据 / No color data available")
            return

        sorted_colors = sorted(
            color_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        self.color_table.setRowCount(len(sorted_colors))

        for row, (color_id, count) in enumerate(sorted_colors):
            color_info = color_details.get(color_id)
            if not color_info:
                continue

            rgb = color_info.get('rgb', [128, 128, 128])
            name_zh = color_info.get('name_zh', '未知')
            name_en = color_info.get('name_en', 'Unknown')
            code = color_info.get('code', str(color_id))
            percentage = (count / total_beads) * 100

            color_widget = QWidget()
            color_widget.setStyleSheet(f"background: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); border-radius: 4px;")

            self.color_table.setCellWidget(row, 0, color_widget)

            code_item = QTableWidgetItem(code)
            code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            code_item.setFont(QFont("Microsoft YaHei UI", 10, QFont.Weight.Bold))
            self.color_table.setItem(row, 1, code_item)

            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.color_table.setItem(row, 2, count_item)

            percentage_item = QTableWidgetItem(f"{percentage:.1f}%")
            percentage_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.color_table.setItem(row, 3, percentage_item)

            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(int(percentage))
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(16)
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    border-radius: 8px;
                    background-color: #E9ECEF;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2);
                    border-radius: 8px;
                }}
            """)

            self.color_table.setCellWidget(row, 4, progress_bar)

        top_colors = sorted_colors[:5]
        top_percentage = sum(count for _, count in top_colors) / total_beads * 100

        most_used_code = color_details.get(sorted_colors[0][0], {}).get('code', str(sorted_colors[0][0]))

        summary_text = f"""
        <b>颜色种类:</b> {len(sorted_colors)}  &nbsp;&nbsp;
        <b>总拼豆数:</b> {total_beads}  &nbsp;&nbsp;
        <b>最常用色号:</b> <span style="color: #667eea; font-weight: 700;">{most_used_code}</span> ({sorted_colors[0][1]}个)  &nbsp;&nbsp;
        <b>前5色占比:</b> {top_percentage:.1f}%
        """.strip()

        self.color_summary_label.setText(summary_text)

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
            scaled_size = QSize(
                int(self.pattern_image.width() * scale / 100),
                int(self.pattern_image.height() * scale / 100)
            )
            scaled_pixmap = self.pattern_image.scaled(
                scaled_size,
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
        elif format_type == 'technical':
            file_dialog.setNameFilter("PNG Files (*.png)")
        elif format_type == 'pdf':
            file_dialog.setNameFilter("PDF Files (*.pdf)")

        # technical格式使用png作为文件后缀
        suffix = format_type if format_type != 'technical' else 'png'

        file_dialog.setDefaultSuffix(suffix)

        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            if not os.path.splitext(file_path)[1]:
                file_path = f"{file_path}.{suffix}"
            self.export_requested.emit((format_type, file_path))

    
    def _start_export(self, format_type: str, file_path: str):
        """后台导出（使用threading）"""
        if self._export_thread and self._export_thread.is_alive():
            QMessageBox.information(self, "提示 / Info", "已有导出任务在进行 / Export in progress")
            return

        # 禁用导出按钮
        self._set_export_buttons_enabled(False)

        # 创建进度对话框
        self._progress_dialog = QProgressDialog("正在导出... / Exporting...", "取消 / Cancel", 0, 100, self)
        self._progress_dialog.setWindowTitle(f"导出{format_type.upper()} / Export {format_type.upper()}")
        self._progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self._progress_dialog.setCancelButton(None)
        self._progress_dialog.setMinimumDuration(0)
        self._progress_dialog.show()

        worker = ExportWorker(
            format_type,
            file_path,
            self.pattern_object,
            self.pattern_data,
            self.pattern_path_with_labels
        )

        # 使用Python threading
        export_thread = threading.Thread(target=worker.run, daemon=True)
 
        # 连接信号
        worker.progress.connect(self._on_export_progress)
        worker.finished.connect(self._on_export_finished)
 
        # 保存引用
        self._worker_ref = worker
        self._export_thread = export_thread
 
        export_thread.start()
        return

    def _on_export_progress(self, percent: int, message: str):
        """更新导出进度"""
        if self._progress_dialog:
            self._progress_dialog.setValue(percent)
            self._progress_dialog.setLabelText(message)






















































































































































































































































































        """导出进度更新"""
        print(f"[DEBUG] Progress update: {percent}% - {message}")
        if self._progress_dialog:
            self._progress_dialog.setValue(percent)
            self._progress_dialog.setLabelText(f"{message}\\n{percent}%")

    def _on_export_finished(self, success: bool, message: str):
        """导出完成"""
        print(f"[DEBUG] Export finished: success={success}, message={message}")

        # 关闭进度对话框
        if self._progress_dialog:
            QTimer.singleShot(100, self._progress_dialog.close)
            self._progress_dialog = None

        # 重新启用导出按钮
        self._set_export_buttons_enabled(True)

        # 显示结果
        if success:
            QMessageBox.information(self, "导出成功 / Export Success", message or "导出完成 / Export finished")
        else:
            QMessageBox.critical(self, "导出失败 / Export Failed", message or "导出失败 / Export failed")

    def _set_export_buttons_enabled(self, enabled: bool):
        """启用/禁用导出按钮"""
        if hasattr(self, 'export_png_btn'):
            self.export_png_btn.setEnabled(enabled)
        if hasattr(self, 'export_technical_btn'):
            self.export_technical_btn.setEnabled(enabled)
        if hasattr(self, 'export_json_btn'):
            self.export_json_btn.setEnabled(enabled)
        if hasattr(self, 'export_csv_btn'):
            self.export_csv_btn.setEnabled(enabled)
        if hasattr(self, 'export_pdf_btn'):
            self.export_pdf_btn.setEnabled(enabled)

    def reset(self):
        """重置页面"""
        self.pattern_data = None
        self.pattern_image = None
        self.pattern_object = None
        self.pattern_path_with_labels = None
        self.pattern_path_no_labels = None
        self.stats_label.setText("暂无数据 / No Data")
        self.color_summary_label.setText("暂无数据 / No Data")
        self.color_table.setRowCount(0)
        self.image_label.clear()
        self.image_label.setText("暂无图案 / No Pattern")
        self.update_zoom(100)


class ExportWorker(QObject):
    """导出线程"""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)

    def __init__(
        self,
        format_type: str,
        file_path: str,
        pattern_object,
        pattern_data: Optional[Dict],
        labeled_path: Optional[str]
    ):
        super().__init__()
        self.format_type = format_type
        self.file_path = file_path
        self.pattern_object = pattern_object
        self.pattern_data = pattern_data
        self.labeled_path = labeled_path

    def run(self):
        try:
            self.progress.emit(5, "准备导出 / Preparing")
            self.progress.emit(10, f"正在导出 {self.format_type.upper()} / Exporting {self.format_type.upper()}")

            if self.format_type == 'png':
                self.progress.emit(20, "生成基础图像 / Rendering base image")
                self.progress.emit(30, "添加网格 / Adding grid")
                self.progress.emit(40, "渲染标签 / Rendering labels")
                self.progress.emit(50, "合成图像 / Compositing image")

                if self.pattern_object:
                    export_image = self.pattern_object.to_image(cell_size=20, show_labels=True, show_grid=True)
                    self.progress.emit(70, "准备保存 / Preparing save")
                    self.progress.emit(80, "保存文件 / Saving")
                    self.progress.emit(90, "完成保存 / Finishing save")
                    export_image.save(self.file_path, compress_level=1)
                elif self.labeled_path and os.path.exists(self.labeled_path):
                    self.progress.emit(60, "使用缓存图像 / Using cached image")
                    self.progress.emit(80, "保存文件 / Saving")
                    shutil.copyfile(self.labeled_path, self.file_path)
                else:
                    self.progress.emit(60, "错误 / Error")
                    self.finished.emit(False, "没有可导出的图片 / No image to export")
                    return

                self.progress.emit(100, "导出完成 / Export completed")
                self.finished.emit(True, "导出完成 / Export finished")
                return

            if self.format_type == 'technical':
                from bead_pattern.render.technical_panel import (
                    TechnicalPanelConfig,
                    generate_technical_sheet
                )

                self.progress.emit(20, "准备生成工程图 / Preparing technical sheet")
                self.progress.emit(40, "渲染基础图案 / Rendering base pattern")
                self.progress.emit(60, "生成信息面板 / Generating info panel")
                self.progress.emit(80, "合成工程图 / Compositing technical sheet")

                try:
                    if self.pattern_object:
                        config = TechnicalPanelConfig(
                            font_size=12,
                            color_block_size=24,
                            row_height=32,
                            panel_padding=20,
                            margin_from_pattern=20,
                            background_color=(255, 255, 255),
                            text_color=(0, 0, 0),
                            border_width=0,
                            header_font_size=14
                        )

                        tech_sheet = generate_technical_sheet(
                            self.pattern_object,
                            cell_size=0,  # 自动计算，确保色号可读
                            show_grid=True,
                            show_labels=True,  # 显示色号
                            config=config,
                            exclude_background=True
                        )

                        self.progress.emit(90, "保存文件 / Saving")
                        tech_sheet.save(self.file_path, compress_level=1)
                        self.progress.emit(100, "导出完成 / Export completed")
                        self.finished.emit(True, "工程图导出成功 / Technical sheet exported successfully")
                    else:
                        self.progress.emit(60, "错误 / Error")
                        self.finished.emit(False, "没有可导出的图案 / No pattern to export")
                except Exception as exc:
                    import traceback
                    traceback.print_exc()
                    self.progress.emit(60, "错误 / Error")
                    self.finished.emit(False, f"导出失败 / Export failed: {exc}")
                return

            if self.format_type == 'json':
                if not self.pattern_data:
                    self.progress.emit(60, "错误 / Error")
                    self.finished.emit(False, "没有可导出的数据 / No data to export")
                    return
                self.progress.emit(50, "写入JSON文件 / Writing JSON file")
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.pattern_data, f, ensure_ascii=False, indent=2)
                self.progress.emit(100, "导出完成 / Export completed")
                self.finished.emit(True, "导出完成 / Export finished")
                return

            if self.format_type == 'csv':
                if not self.pattern_data:
                    self.progress.emit(60, "错误 / Error")
                    self.finished.emit(False, "没有可导出的数据 / No data to export")
                    return
                self.progress.emit(50, "写入CSV文件 / Writing CSV file")
                with open(self.file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["key", "value"])
                    for key, value in self.pattern_data.items():
                        writer.writerow([key, value])
                self.progress.emit(100, "导出完成 / Export completed")
                self.finished.emit(True, "导出完成 / Export finished")
                return

            self.progress.emit(60, "错误 / Error")
            self.finished.emit(False, f"不支持的导出格式: {self.format_type} / Unsupported format")
            return

        except Exception as exc:
            import traceback
            traceback.print_exc()
            self.finished.emit(False, f"导出失败 / Export failed: {exc}")

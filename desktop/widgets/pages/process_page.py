"""
处理流程页面组件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QGroupBox, QTextEdit,
    QScrollArea, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from enum import Enum
from pathlib import Path
import uuid
from PIL import Image

from core.image_processor import ImageProcessor
from core.color_matcher import ColorMatcher
from core.optimizer import PatternOptimizer
from bead_pattern import BeadPattern


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
        self.image_path = None
        self.params = {}
        self.pattern_object = None
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
        self.start_btn.setAutoFillBackground(True)
        self.start_btn.setFlat(False)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 8px;
                border: none;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5DA3F5;
            }
            QPushButton:pressed {
                background-color: #357ABD;
            }
        """)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹️ 停止 / Stop")
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setProperty("class", "danger")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        self.stop_btn.setAutoFillBackground(True)
        self.stop_btn.setFlat(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border-radius: 8px;
                border: none;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D6453A;
            }
            QPushButton:disabled {
                background: #E1E8F0;
                color: #7F8C8D;
            }
        """)
        btn_layout.addWidget(self.stop_btn)

        layout.addLayout(btn_layout)

        # 一键执行按钮
        execute_all_btn = QPushButton("🚀 一键执行所有步骤 / Execute All Steps")
        execute_all_btn.setMinimumHeight(50)
        execute_all_btn.setProperty("class", "success")
        execute_all_btn.clicked.connect(self.on_execute_all_clicked)
        execute_all_btn.setAutoFillBackground(True)
        execute_all_btn.setFlat(False)
        execute_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border-radius: 8px;
                border: none;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #34D175;
            }
            QPushButton:pressed {
                background-color: #27AE60;
            }
        """)
        layout.addWidget(execute_all_btn)

    def on_start_clicked(self):
        """开始处理按钮点击事件"""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.run_processing()

    def on_execute_all_clicked(self):
        """一键执行所有步骤按钮点击事件"""
        self.log_message("一键执行所有步骤 / Execute all steps...")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.run_processing()

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

    def set_input_image(self, image_path: str) -> None:
        """设置输入图像路径"""
        self.image_path = image_path

    def set_params(self, params: dict) -> None:
        """设置处理参数"""
        self.params = params or {}

    def run_processing(self) -> None:
        """执行实际处理流程"""
        if not self.image_path:
            self.log_message("请先上传图片 / Please upload an image first")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            return

        try:
            self._set_progress(5, "预处理 / Preprocessing", "正在加载图像...")
            image_processor = ImageProcessor()
            color_matcher = ColorMatcher()
            pattern_optimizer = PatternOptimizer(color_matcher)

            bead_size_value = self.params.get('bead_size', '5.0mm')
            bead_size_mm = 2.6 if bead_size_value == '2.6mm' else 5.0
            max_dimension = int(self.params.get('max_dimension', 100))
            target_colors = int(self.params.get('target_colors', 20))
            denoise_strength = float(self.params.get('denoise_strength', 0.3))
            contrast_factor = float(self.params.get('contrast', 1.2))
            sharpness_factor = float(self.params.get('sharpness', 1.0))
            use_custom = bool(self.params.get('use_custom_palette', False))
            brand = self.params.get('brand') or None
            series = self.params.get('series') or None
            match_mode = self.params.get('match_mode', 'nearest')

            image_processor.load_image(self.image_path)
            image_array = image_processor.get_image_array()

            self._set_progress(20, "预处理 / Preprocessing", "应用降噪和对比度调整...")
            optimized_image, (new_width, new_height) = pattern_optimizer.apply_full_optimization(
                image_array,
                target_colors=target_colors,
                max_dimension=max_dimension,
                denoise_strength=denoise_strength,
                contrast_factor=contrast_factor,
                sharpness_factor=sharpness_factor,
                use_custom=use_custom,
                based_on_subject=True,
                background_rgb=(255, 255, 255),
                threshold=5
            )

            output_dir = self._get_output_dir()
            preprocess_path = output_dir / f"preprocess_{uuid.uuid4().hex}.png"
            Image.fromarray(optimized_image).save(preprocess_path)

            self._set_progress(50, "图案生成 / Pattern Generation", "匹配拼豆色板颜色...")
            matched_colors = color_matcher.match_image_colors(
                optimized_image,
                use_custom=use_custom,
                method="cie94",
                brand=brand,
                series=series,
                match_mode=match_mode
            )

            self._set_progress(70, "图案生成 / Pattern Generation", "生成拼豆图案网格...")
            bead_pattern = BeadPattern(new_width, new_height, bead_size_mm=bead_size_mm)
            bead_pattern.from_matched_colors(matched_colors)

            preview_cell_size = 8
            viz_with_labels = bead_pattern.to_image(cell_size=preview_cell_size, show_labels=True, show_grid=True)
            viz_no_labels = bead_pattern.to_image(cell_size=preview_cell_size, show_labels=False, show_grid=True)

            pattern_id = uuid.uuid4().hex
            viz_path_with = output_dir / f"{pattern_id}_viz.png"
            viz_path_no = output_dir / f"{pattern_id}_viz_no_labels.png"
            viz_with_labels.save(viz_path_with)
            viz_no_labels.save(viz_path_no)

            stats = bead_pattern.get_color_statistics(exclude_background=True)
            color_counts = stats.get('color_counts', {})

            color_details = {}
            for color_id, count in color_counts.items():
                color_info = bead_pattern._v2.palette.get_color(color_id)
                if color_info:
                    color_details[color_id] = {
                        'id': color_info.id,
                        'code': color_info.display_code,
                        'name_zh': color_info.name_zh,
                        'name_en': color_info.name_en,
                        'rgb': list(color_info.rgb)
                    }

            subject_size = bead_pattern.get_subject_size()

            result_data = {
                'width': new_width,
                'height': new_height,
                'actual_width_mm': bead_pattern.actual_width_mm,
                'actual_height_mm': bead_pattern.actual_height_mm,
                'color_count': stats.get('unique_colors', 0),
                'total_beads': stats.get('total_beads', new_width * new_height),
                'bead_size': bead_size_value,
                'subject_width': subject_size.get('width', 0) if subject_size else 0,
                'subject_height': subject_size.get('height', 0) if subject_size else 0,
                'subject_width_mm': subject_size.get('width_mm', 0.0) if subject_size else 0.0,
                'subject_height_mm': subject_size.get('height_mm', 0.0) if subject_size else 0.0
            }

            self._set_progress(100, "完成 / Complete", "处理完成！")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

            self.process_completed.emit({
                'pattern_data': result_data,
                'pattern_image_with_labels': str(viz_path_with),
                'pattern_image_no_labels': str(viz_path_no),
                'bead_pattern': bead_pattern,
                'color_counts': color_counts,
                'color_details': color_details
            })
        except Exception as exc:
            self.log_message(f"处理失败 / Failed: {exc}")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    def _set_progress(self, value: int, step_text: str, log_message: str) -> None:
        """更新进度和日志"""
        self.progress_bar.setValue(value)
        self.step_label.setText(step_text)
        self.log_message(log_message)
        QApplication.instance().processEvents()

    def _get_output_dir(self) -> Path:
        """获取输出目录"""
        base_dir = Path(__file__).resolve().parents[3]
        output_dir = base_dir / 'data' / 'output'
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

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

"""
参数设置页面组件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox,
    QPushButton, QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import json
import os

from desktop.config import ConfigManager


class ParameterPage(QWidget):
    """参数设置页面"""

    params_changed = pyqtSignal(dict)  # 参数变更信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.params = self._get_default_params()
        self.brand_series_map = {}
        self.config = ConfigManager()
        self.init_ui()
        self._load_brand_series()

    def _get_default_params(self):
        """获取默认参数"""
        return {
            # 拼豆设置
            'bead_size': '5.0mm',  # 2.6mm 或 5.0mm
            'max_dimension': 100,  # 最大尺寸（拼豆数）

            # 预处理参数
            'preset': 'standard',  # 预设: light, standard, heavy, custom
            'target_colors': 20,  # 目标颜色数
            'denoise_strength': 0.3,  # 降噪强度
            'contrast': 1.2,  # 对比度
            'sharpness': 1.0,  # 锐度

            # AI增强（可选）
            'use_ai': False,
            'ai_prompt': 'pixel art style',
            'ai_size': 512,

            # 其他
            'detect_subject': True,  # 检测主体
            'use_custom_palette': False,  # 使用自定义色板
            'brand': '',  # 拼豆品牌
            'series': ''  # 色数系列
        }

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("⚙️ 参数设置 / Parameter Settings")
        title_label.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # 内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)

        # 拼豆设置
        bead_group = self._create_bead_settings_group()
        content_layout.addWidget(bead_group)

        # 预处理参数
        preprocess_group = self._create_preprocess_group()
        content_layout.addWidget(preprocess_group)

        # AI增强设置
        ai_group = self._create_ai_settings_group()
        content_layout.addWidget(ai_group)

        # 高级选项
        advanced_group = self._create_advanced_group()
        content_layout.addWidget(advanced_group)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # 操作按钮
        btn_layout = QHBoxLayout()

        reset_btn = QPushButton("🔄 重置 / Reset")
        reset_btn.setMinimumHeight(45)
        reset_btn.setProperty("class", "secondary")
        reset_btn.clicked.connect(self.on_reset_clicked)
        btn_layout.addWidget(reset_btn)

        apply_btn = QPushButton("✅ 应用 / Apply")
        apply_btn.setMinimumHeight(45)
        apply_btn.clicked.connect(self.on_apply_clicked)
        btn_layout.addWidget(apply_btn)

        layout.addLayout(btn_layout)

    def _create_bead_settings_group(self) -> QGroupBox:
        """创建拼豆设置分组"""
        group = QGroupBox("拼豆设置 / Bead Settings")
        group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # 拼豆大小
        bead_layout = QHBoxLayout()
        bead_label = QLabel("拼豆种类 / Bead Type:")
        bead_label.setMinimumWidth(150)
        self.bead_size_combo = QComboBox()
        self.bead_size_combo.addItems(["2.6mm (小拼豆 / Small)", "5.0mm (标准拼豆 / Standard)"])
        self.bead_size_combo.setCurrentIndex(1)  # 默认 5.0mm
        self.bead_size_combo.currentIndexChanged.connect(self._on_bead_size_changed)
        bead_layout.addWidget(bead_label)
        bead_layout.addWidget(self.bead_size_combo, 1)
        layout.addLayout(bead_layout)

        # 拼豆品牌
        brand_layout = QHBoxLayout()
        brand_label = QLabel("拼豆厂家 / Brand:")
        brand_label.setMinimumWidth(150)
        self.brand_combo = QComboBox()
        self.brand_combo.addItem("全部品牌 / All Brands", "")
        self.brand_combo.currentIndexChanged.connect(self._on_brand_changed)
        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(self.brand_combo, 1)
        layout.addLayout(brand_layout)

        # 色数系列
        series_layout = QHBoxLayout()
        series_label = QLabel("色数系列 / Series:")
        series_label.setMinimumWidth(150)
        self.series_combo = QComboBox()
        self.series_combo.addItem("全部色数 / All Series", "")
        self.series_combo.setEnabled(False)
        series_layout.addWidget(series_label)
        series_layout.addWidget(self.series_combo, 1)
        layout.addLayout(series_layout)

        # 最大尺寸
        dimension_layout = QHBoxLayout()
        dimension_label = QLabel("最大尺寸 / Max Dimension:")
        dimension_label.setMinimumWidth(150)
        self.max_dimension_spin = QSpinBox()
        self.max_dimension_spin.setMinimum(20)
        self.max_dimension_spin.setMaximum(500)
        self.max_dimension_spin.setValue(100)
        self.max_dimension_spin.setSuffix(" 拼豆 / beads")
        dimension_layout.addWidget(dimension_label)
        dimension_layout.addWidget(self.max_dimension_spin, 1)
        layout.addLayout(dimension_layout)

        return group

    def _create_preprocess_group(self) -> QGroupBox:
        """创建预处理参数分组"""
        group = QGroupBox("预处理参数 / Preprocessing Parameters")
        group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # 预设选择
        preset_layout = QHBoxLayout()
        preset_label = QLabel("预设 / Preset:")
        preset_label.setMinimumWidth(150)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "轻度预处理 / Light",
            "标准预处理 / Standard",
            "重度预处理 / Heavy",
            "自定义 / Custom"
        ])
        self.preset_combo.setCurrentIndex(1)  # 默认标准
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_combo, 1)
        layout.addLayout(preset_layout)

        # 目标颜色数
        colors_layout = QHBoxLayout()
        colors_label = QLabel("拼豆颜色数量 / Bead Colors:")
        colors_label.setMinimumWidth(150)
        self.target_colors_spin = QSpinBox()
        self.target_colors_spin.setMinimum(5)
        self.target_colors_spin.setMaximum(50)
        self.target_colors_spin.setValue(20)
        colors_layout.addWidget(colors_label)
        colors_layout.addWidget(self.target_colors_spin, 1)
        layout.addLayout(colors_layout)

        # 降噪强度
        denoise_layout = QHBoxLayout()
        denoise_label = QLabel("降噪强度 / Denoise Strength:")
        denoise_label.setMinimumWidth(150)
        self.denoise_spin = QDoubleSpinBox()
        self.denoise_spin.setMinimum(0)
        self.denoise_spin.setMaximum(1)
        self.denoise_spin.setSingleStep(0.1)
        self.denoise_spin.setValue(0.3)
        denoise_layout.addWidget(denoise_label)
        denoise_layout.addWidget(self.denoise_spin, 1)
        layout.addLayout(denoise_layout)

        # 对比度
        contrast_layout = QHBoxLayout()
        contrast_label = QLabel("对比度 / Contrast:")
        contrast_label.setMinimumWidth(150)
        self.contrast_spin = QDoubleSpinBox()
        self.contrast_spin.setMinimum(0.5)
        self.contrast_spin.setMaximum(2)
        self.contrast_spin.setSingleStep(0.1)
        self.contrast_spin.setValue(1.2)
        contrast_layout.addWidget(contrast_label)
        contrast_layout.addWidget(self.contrast_spin, 1)
        layout.addLayout(contrast_layout)

        # 锐度
        sharpness_layout = QHBoxLayout()
        sharpness_label = QLabel("锐度 / Sharpness:")
        sharpness_label.setMinimumWidth(150)
        self.sharpness_spin = QDoubleSpinBox()
        self.sharpness_spin.setMinimum(0.5)
        self.sharpness_spin.setMaximum(2)
        self.sharpness_spin.setSingleStep(0.1)
        self.sharpness_spin.setValue(1.0)
        sharpness_layout.addWidget(sharpness_label)
        sharpness_layout.addWidget(self.sharpness_spin, 1)
        layout.addLayout(sharpness_layout)

        return group

    def _load_brand_series(self) -> None:
        """加载品牌与色数系列"""
        colors_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '..',
            '..',
            'data',
            'standard_colors.json'
        )

        if not os.path.exists(colors_path):
            return

        try:
            with open(colors_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            return

        colors = data.get('colors', [])
        brand_series_map = {}

        for color in colors:
            brand = color.get('brand')
            series = color.get('series')
            if not brand:
                continue
            if brand not in brand_series_map:
                brand_series_map[brand] = set()
            if series:
                brand_series_map[brand].add(str(series))

        self.brand_series_map = brand_series_map
        self._populate_brands()

    def _populate_brands(self) -> None:
        """填充品牌下拉框"""
        if not hasattr(self, 'brand_combo'):
            return
        current = self.brand_combo.currentData()
        self.brand_combo.blockSignals(True)
        self.brand_combo.clear()
        self.brand_combo.addItem("全部品牌 / All Brands", "")
        for brand in sorted(self.brand_series_map.keys()):
            self.brand_combo.addItem(brand, brand)
        if current:
            index = self.brand_combo.findData(current)
            if index >= 0:
                self.brand_combo.setCurrentIndex(index)
        self.brand_combo.blockSignals(False)
        self._on_brand_changed(self.brand_combo.currentIndex())

    def _on_brand_changed(self, index: int) -> None:
        """品牌变更事件"""
        if not hasattr(self, 'series_combo'):
            return
        brand = self.brand_combo.itemData(index)
        self.series_combo.blockSignals(True)
        self.series_combo.clear()
        self.series_combo.addItem("全部色数 / All Series", "")

        if not brand:
            self.series_combo.setEnabled(False)
            self.series_combo.blockSignals(False)
            return

        series_list = sorted(
            self.brand_series_map.get(brand, []),
            key=lambda s: int(s) if str(s).isdigit() else str(s)
        )
        for series in series_list:
            self.series_combo.addItem(f"{series} 色", series)
        self.series_combo.setEnabled(True)
        self.series_combo.blockSignals(False)

    def _create_ai_settings_group(self) -> QGroupBox:
        """创建AI增强设置分组"""
        group = QGroupBox("AI增强 / AI Enhancement")
        group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # 启用AI
        self.use_ai_checkbox = QCheckBox("启用AI增强 / Enable AI Enhancement")
        layout.addWidget(self.use_ai_checkbox)

        return group

    def _create_advanced_group(self) -> QGroupBox:
        """创建高级选项分组"""
        group = QGroupBox("高级选项 / Advanced Options")
        group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # 检测主体
        self.detect_subject_checkbox = QCheckBox("检测主体并排除背景 / Detect Subject & Exclude Background")
        self.detect_subject_checkbox.setChecked(True)
        layout.addWidget(self.detect_subject_checkbox)

        # 使用自定义色板
        self.use_custom_palette_checkbox = QCheckBox("使用自定义色板 / Use Custom Palette")
        self.use_custom_palette_checkbox.setChecked(False)
        layout.addWidget(self.use_custom_palette_checkbox)

        return group

    def _on_bead_size_changed(self, index):
        """拼豆大小变更事件"""
        if index == 0:  # 2.6mm
            self.max_dimension_spin.setRange(50, 500)
            self.max_dimension_spin.setValue(200)
        else:  # 5.0mm
            self.max_dimension_spin.setRange(20, 200)
            self.max_dimension_spin.setValue(100)

    def _on_preset_changed(self, index):
        """预设变更事件"""
        presets = {
            0: {  # 轻度
                'target_colors': 15,
                'denoise_strength': 0.2,
                'contrast': 1.1,
                'sharpness': 1.0
            },
            1: {  # 标准
                'target_colors': 20,
                'denoise_strength': 0.3,
                'contrast': 1.2,
                'sharpness': 1.0
            },
            2: {  # 重度
                'target_colors': 25,
                'denoise_strength': 0.5,
                'contrast': 1.3,
                'sharpness': 1.1
            },
            3: {}  # 自定义，不修改
        }

        if index in presets:
            preset = presets[index]
            self.target_colors_spin.setValue(preset.get('target_colors', 20))
            self.denoise_spin.setValue(preset.get('denoise_strength', 0.3))
            self.contrast_spin.setValue(preset.get('contrast', 1.2))
            self.sharpness_spin.setValue(preset.get('sharpness', 1.0))

    def on_reset_clicked(self):
        """重置按钮点击事件"""
        # 重置为默认值
        self.bead_size_combo.setCurrentIndex(1)  # 5.0mm
        if hasattr(self, 'brand_combo'):
            self.brand_combo.setCurrentIndex(0)
        if hasattr(self, 'series_combo'):
            self.series_combo.setCurrentIndex(0)
        self.max_dimension_spin.setValue(100)
        self.preset_combo.setCurrentIndex(1)  # 标准
        self.target_colors_spin.setValue(20)
        self.denoise_spin.setValue(0.3)
        self.contrast_spin.setValue(1.2)
        self.sharpness_spin.setValue(1.0)
        self.use_ai_checkbox.setChecked(False)
        self.detect_subject_checkbox.setChecked(True)
        self.use_custom_palette_checkbox.setChecked(False)

    def on_apply_clicked(self):
        """应用按钮点击事件"""
        self._collect_params()
        if self.config.get('remember_last_params', True):
            self.config.save_last_params(self.params)
        self.params_changed.emit(self.params)

    def _collect_params(self):
        """收集参数"""
        self.params.update({
            'bead_size': '2.6mm' if self.bead_size_combo.currentIndex() == 0 else '5.0mm',
            'max_dimension': self.max_dimension_spin.value(),
            'preset': ['light', 'standard', 'heavy', 'custom'][self.preset_combo.currentIndex()],
            'target_colors': self.target_colors_spin.value(),
            'denoise_strength': self.denoise_spin.value(),
            'contrast': self.contrast_spin.value(),
            'sharpness': self.sharpness_spin.value(),
            'use_ai': self.use_ai_checkbox.isChecked(),
            'detect_subject': self.detect_subject_checkbox.isChecked(),
            'use_custom_palette': self.use_custom_palette_checkbox.isChecked(),
            'brand': self.brand_combo.currentData() if hasattr(self, 'brand_combo') else '',
            'series': self.series_combo.currentData() if hasattr(self, 'series_combo') else ''
        })

    def get_params(self) -> dict:
        """获取参数"""
        self._collect_params()
        return self.params

    def set_params(self, params: dict):
        """设置参数"""
        if 'bead_size' in params:
            self.bead_size_combo.setCurrentIndex(0 if params['bead_size'] == '2.6mm' else 1)
        if 'brand' in params and hasattr(self, 'brand_combo'):
            brand_index = self.brand_combo.findData(params['brand'])
            if brand_index >= 0:
                self.brand_combo.setCurrentIndex(brand_index)
        if 'series' in params and hasattr(self, 'series_combo'):
            series_index = self.series_combo.findData(params['series'])
            if series_index >= 0:
                self.series_combo.setCurrentIndex(series_index)
        if 'max_dimension' in params:
            self.max_dimension_spin.setValue(params['max_dimension'])
        if 'preset' in params:
            preset_map = {'light': 0, 'standard': 1, 'heavy': 2, 'custom': 3}
            self.preset_combo.setCurrentIndex(preset_map.get(params['preset'], 1))
        if 'target_colors' in params:
            self.target_colors_spin.setValue(params['target_colors'])
        if 'denoise_strength' in params:
            self.denoise_spin.setValue(params['denoise_strength'])
        if 'contrast' in params:
            self.contrast_spin.setValue(params['contrast'])
        if 'sharpness' in params:
            self.sharpness_spin.setValue(params['sharpness'])
        if 'use_ai' in params:
            self.use_ai_checkbox.setChecked(params['use_ai'])
        if 'detect_subject' in params:
            self.detect_subject_checkbox.setChecked(params['detect_subject'])
        if 'use_custom_palette' in params:
            self.use_custom_palette_checkbox.setChecked(params['use_custom_palette'])
        self.params.update(params)
    def _load_last_params(self):
        """从配置加载上次使用的参数"""
        if self.config.get('remember_last_params', True):
            last_params = self.config.get_last_params()
            if last_params:
                self.set_params(last_params)
                self.params_changed.emit(self.params)
  
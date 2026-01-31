"""
系统设置页面组件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QGroupBox,
    QCheckBox, QSpinBox, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import os

from desktop.config import ConfigManager


class SettingsPage(QWidget):
    """系统设置页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self.init_ui()
        self._load_settings()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("⚙️ 系统设置 / System Settings")
        title_label.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 语言设置
        language_group = QGroupBox("语言设置 / Language Settings")
        language_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        language_layout = QVBoxLayout(language_group)
        language_layout.setContentsMargins(15, 15, 15, 15)

        lang_layout = QHBoxLayout()
        lang_label = QLabel("语言 / Language:")
        lang_label.setMinimumWidth(150)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文 / Simplified Chinese", "English / 英文"])
        self.language_combo.setCurrentIndex(0)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.language_combo, 1)
        language_layout.addLayout(lang_layout)

        layout.addWidget(language_group)

        # Nano Banana API设置
        api_group = QGroupBox("Nano Banana API 配置 / Nano Banana API Configuration")
        api_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        api_layout = QVBoxLayout(api_group)
        api_layout.setContentsMargins(15, 15, 15, 15)
        api_layout.setSpacing(15)

        # API Key
        key_layout = QHBoxLayout()
        key_label = QLabel("API 密钥 / API Key:")
        key_label.setMinimumWidth(150)
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("请输入API密钥 / Enter API key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setMinimumHeight(36)
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.api_key_input, 1)
        api_layout.addLayout(key_layout)

        # Base URL
        url_layout = QHBoxLayout()
        url_label = QLabel("Base URL:")
        url_label.setMinimumWidth(150)
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://api.grsai.com")
        self.base_url_input.setText("https://api.grsai.com")
        self.base_url_input.setMinimumHeight(36)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.base_url_input, 1)
        api_layout.addLayout(url_layout)

        # Proxy
        proxy_layout = QHBoxLayout()
        proxy_label = QLabel("代理 / Proxy:")
        proxy_label.setMinimumWidth(150)
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://host:port (可选 / optional)")
        self.proxy_input.setMinimumHeight(36)
        proxy_layout.addWidget(proxy_label)
        proxy_layout.addWidget(self.proxy_input, 1)
        api_layout.addLayout(proxy_layout)

        # 测试连接
        test_btn_layout = QHBoxLayout()
        test_btn_layout.addStretch()
        self.test_api_btn = QPushButton("🔍 测试连接 / Test Connection")
        self.test_api_btn.setProperty("class", "secondary")
        self.test_api_btn.setMinimumWidth(180)
        self.test_api_btn.setMinimumHeight(40)
        self.test_api_btn.clicked.connect(self.on_test_api)
        test_btn_layout.addWidget(self.test_api_btn)
        api_layout.addLayout(test_btn_layout)

        layout.addWidget(api_group)

        # 导出设置
        export_group = QGroupBox("导出设置 / Export Settings")
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
        export_layout = QVBoxLayout(export_group)
        export_layout.setContentsMargins(15, 15, 15, 15)
        export_layout.setSpacing(15)

        # 输出目录
        output_layout = QHBoxLayout()
        output_label = QLabel("输出目录 / Output Directory:")
        output_label.setMinimumWidth(150)
        self.output_dir_input = QLineEdit()
        default_output_dir = self.config.get_default_output_dir()
        self.output_dir_input.setPlaceholderText(f"默认: {default_output_dir}")
        self.output_dir_input.setText(default_output_dir)
        self.output_dir_input.setReadOnly(True)
        self.output_dir_input.setMinimumHeight(36)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_dir_input, 1)

        browse_btn = QPushButton("📁 浏览 / Browse")
        browse_btn.setMinimumWidth(100)
        browse_btn.setMinimumHeight(40)
        browse_btn.clicked.connect(self.on_browse_output)
        output_layout.addWidget(browse_btn)

        export_layout.addLayout(output_layout)

        # 图片格式
        format_layout = QHBoxLayout()
        format_label = QLabel("图片格式 / Image Format:")
        format_label.setMinimumWidth(150)
        self.image_format_combo = QComboBox()
        self.image_format_combo.addItems(["PNG", "JPG", "WEBP"])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.image_format_combo, 1)
        export_layout.addLayout(format_layout)

        # DPI设置
        dpi_layout = QHBoxLayout()
        dpi_label = QLabel("打印DPI / Print DPI:")
        dpi_label.setMinimumWidth(150)
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setMinimum(72)
        self.dpi_spin.setMaximum(600)
        self.dpi_spin.setValue(300)
        self.dpi_spin.setSuffix(" DPI")
        dpi_layout.addWidget(dpi_label)
        dpi_layout.addWidget(self.dpi_spin, 1)
        export_layout.addLayout(dpi_layout)

        layout.addWidget(export_group)

        # 高级选项
        advanced_group = QGroupBox("高级选项 / Advanced Options")
        advanced_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        advanced_layout = QVBoxLayout(advanced_group)
        advanced_layout.setContentsMargins(15, 15, 15, 15)

        self.auto_save_checkbox = QCheckBox("自动保存项目 / Auto save project")
        self.auto_save_checkbox.setChecked(True)
        advanced_layout.addWidget(self.auto_save_checkbox)

        self.show_numbers_checkbox = QCheckBox("默认显示色号 / Show color numbers by default")
        self.show_numbers_checkbox.setChecked(False)
        advanced_layout.addWidget(self.show_numbers_checkbox)

        layout.addWidget(advanced_group)

        # 底部弹簧
        layout.addStretch()

        # 操作按钮
        btn_layout = QHBoxLayout()

        reset_btn = QPushButton("🔄 重置默认 / Reset to Default")
        reset_btn.setProperty("class", "secondary")
        reset_btn.setMinimumWidth(180)
        reset_btn.setMinimumHeight(40)
        reset_btn.clicked.connect(self.on_reset)
        btn_layout.addWidget(reset_btn)

        save_btn = QPushButton("💾 保存设置 / Save Settings")
        save_btn.setProperty("class", "success")
        save_btn.setMinimumWidth(180)
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def on_test_api(self):
        """测试API连接"""
        api_key = self.api_key_input.text()
        if not api_key:
            QMessageBox.warning(self, "警告 / Warning", "请输入API密钥 / Please enter API key")
            return

        # TODO: 实际测试API连接
        QMessageBox.information(self, "提示 / Info", "API连接测试功能开发中... / API connection test is under development...")

    def on_browse_output(self):
        """浏览输出目录"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("选择输出目录 / Select Output Directory")
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)

        if file_dialog.exec():
            dirs = file_dialog.selectedFiles()
            if dirs:
                self.output_dir_input.setText(dirs[0])

    def on_reset(self):
        """重置为默认值"""
        reply = QMessageBox.question(
            self,
            "确认 / Confirm",
            "确定重置为默认设置吗? / Are you sure to reset to default settings?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.language_combo.setCurrentIndex(0)
            self.api_key_input.clear()
            self.base_url_input.setText("https://api.grsai.com")
            self.proxy_input.clear()
            self.output_dir_input.setText(self.config.get_default_output_dir())
            self.image_format_combo.setCurrentIndex(0)
            self.dpi_spin.setValue(300)
            self.auto_save_checkbox.setChecked(True)
            self.show_numbers_checkbox.setChecked(False)
            self.on_save()
            QMessageBox.information(self, "成功 / Success", "已重置为默认设置 / Settings reset to default")

    def on_save(self):
        """保存设置"""
        settings = self.get_settings()
        self.config.set_language(settings['language'])
        self.config.set_nano_banana_config(
            settings['api_key'],
            settings['base_url'],
            settings['proxy']
        )
        self.config.set('output_dir', settings['output_dir'])
        self.config.set('image_format', settings['image_format'])
        self.config.set('print_dpi', settings['dpi'])
        self.config.set('auto_save_project', settings['auto_save'])
        self.config.set('show_color_numbers', settings['show_numbers'])
        QMessageBox.information(self, "成功 / Success", "设置已保存 / Settings saved")

    def get_settings(self) -> dict:
        """获取设置"""
        return {
            'language': 'zh_CN' if self.language_combo.currentIndex() == 0 else 'en_US',
            'api_key': self.api_key_input.text(),
            'base_url': self.base_url_input.text(),
            'proxy': self.proxy_input.text(),
            'output_dir': self.output_dir_input.text(),
            'image_format': self.image_format_combo.currentText(),
            'dpi': self.dpi_spin.value(),
            'auto_save': self.auto_save_checkbox.isChecked(),
            'show_numbers': self.show_numbers_checkbox.isChecked()
        }

    def set_settings(self, settings: dict):
        """设置参数"""
        if 'language' in settings:
            self.language_combo.setCurrentIndex(0 if settings['language'] == 'zh_CN' else 1)
        if 'api_key' in settings:
            self.api_key_input.setText(settings['api_key'])
        if 'base_url' in settings:
            self.base_url_input.setText(settings['base_url'])
        if 'proxy' in settings:
            self.proxy_input.setText(settings['proxy'])
        if 'output_dir' in settings:
            self.output_dir_input.setText(settings['output_dir'])
        if 'image_format' in settings:
            index = self.image_format_combo.findText(settings['image_format'])
            if index >= 0:
                self.image_format_combo.setCurrentIndex(index)
        if 'dpi' in settings:
            self.dpi_spin.setValue(settings['dpi'])
        if 'auto_save' in settings:
            self.auto_save_checkbox.setChecked(settings['auto_save'])
        if 'show_numbers' in settings:
            self.show_numbers_checkbox.setChecked(settings['show_numbers'])

    def _load_settings(self):
        """从配置加载设置"""
        settings = {
            'language': self.config.get_language(),
            'api_key': self.config.get('nano_banana_api_key', ''),
            'base_url': self.config.get('nano_banana_base_url', 'https://api.grsai.com'),
            'proxy': self.config.get('nano_banana_proxy', ''),
            'output_dir': self.config.get('output_dir', self.config.get_default_output_dir()),
            'image_format': self.config.get('image_format', 'PNG'),
            'dpi': self.config.get('print_dpi', 300),
            'auto_save': self.config.get('auto_save_project', True),
            'show_numbers': self.config.get('show_color_numbers', False)
        }
        self.set_settings(settings)

"""
色板管理页面组件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QFileDialog, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import json
import os


class PalettePage(QWidget):
    """色板管理页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors = []
        self.init_ui()
        self.load_standard_colors()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("🎨 色板管理 / Palette Management")
        title_label.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 操作按钮区域
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("➕ 添加颜色 / Add Color")
        add_btn.clicked.connect(self.on_add_color)
        btn_layout.addWidget(add_btn)

        import_btn = QPushButton("📥 导入 / Import")
        import_btn.clicked.connect(self.on_import)
        btn_layout.addWidget(import_btn)

        export_btn = QPushButton("📤 导出 / Export")
        export_btn.clicked.connect(self.on_export)
        btn_layout.addWidget(export_btn)

        clear_btn = QPushButton("🗑️ 清空 / Clear")
        clear_btn.setProperty("class", "danger")
        clear_btn.clicked.connect(self.on_clear)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)

        # 颜色表格
        table_group = QGroupBox("颜色列表 / Color List")
        table_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E1E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
                color: #357ABD;
            }
        """)
        table_layout = QVBoxLayout(table_group)

        self.color_table = QTableWidget()
        self.color_table.setColumnCount(7)
        self.color_table.setHorizontalHeaderLabels([
            "预览 / Preview",
            "ID",
            "中文名 / Chinese",
            "英文名 / English",
            "色号 / Code",
            "RGB",
            "分类 / Category"
        ])
        self.color_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.color_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.color_table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked | QTableWidget.EditTrigger.EditKeyPressed)
        table_layout.addWidget(self.color_table)

        # 底部按钮
        bottom_layout = QHBoxLayout()

        delete_btn = QPushButton("🗑️ 删除选中 / Delete Selected")
        delete_btn.setProperty("class", "danger")
        delete_btn.clicked.connect(self.on_delete_selected)
        bottom_layout.addWidget(delete_btn)

        save_btn = QPushButton("💾 保存色板 / Save Palette")
        save_btn.setProperty("class", "success")
        save_btn.clicked.connect(self.on_save)
        bottom_layout.addWidget(save_btn)

        table_layout.addLayout(bottom_layout)
        layout.addWidget(table_group)

    def load_standard_colors(self):
        """加载标准色板"""
        colors_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'data', 'standard_colors.json')

        if os.path.exists(colors_path):
            try:
                with open(colors_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.colors = data.get('colors', [])
                    self.update_table()
            except Exception as e:
                self.colors = []

    def update_table(self):
        """更新表格"""
        self.color_table.setRowCount(len(self.colors))

        for row, color in enumerate(self.colors):
            rgb = color.get('rgb')
            if isinstance(rgb, (list, tuple)) and len(rgb) >= 3:
                r, g, b = rgb[:3]
            else:
                r = color.get('R', 0)
                g = color.get('G', 0)
                b = color.get('B', 0)
            try:
                r = int(r)
                g = int(g)
                b = int(b)
            except (TypeError, ValueError):
                r, g, b = 0, 0, 0

            # 预览颜色
            preview_item = QTableWidgetItem()
            preview_item.setBackground(QColor(r, g, b))
            preview_item.setFlags(preview_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.color_table.setItem(row, 0, preview_item)

            # 其他列
            self.color_table.setItem(row, 1, QTableWidgetItem(str(color.get('id', ''))))
            self.color_table.setItem(row, 2, QTableWidgetItem(color.get('chinese_name') or color.get('name_zh', '')))
            self.color_table.setItem(row, 3, QTableWidgetItem(color.get('english_name') or color.get('name_en', '')))
            self.color_table.setItem(row, 4, QTableWidgetItem(color.get('code', '')))
            self.color_table.setItem(row, 5, QTableWidgetItem(f"RGB({r}, {g}, {b})"))
            self.color_table.setItem(row, 6, QTableWidgetItem(color.get('category', '')))

    def on_add_color(self):
        """添加颜色"""
        # 简单实现：添加一个默认颜色
        new_color = {
            'id': len(self.colors) + 1,
            'chinese_name': '新颜色',
            'english_name': 'New Color',
            'code': 'NEW',
            'R': 128,
            'G': 128,
            'B': 128,
            'category': 'Custom'
        }
        self.colors.append(new_color)
        self.update_table()

    def on_delete_selected(self):
        """删除选中的颜色"""
        selected_rows = set()
        for item in self.color_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.warning(self, "警告 / Warning", "请选择要删除的颜色 / Please select colors to delete")
            return

        reply = QMessageBox.question(
            self,
            "确认 / Confirm",
            f"确定删除 {len(selected_rows)} 个颜色吗? / Are you sure to delete {len(selected_rows)} colors?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for row in sorted(selected_rows, reverse=True):
                del self.colors[row]
            self.update_table()

    def on_clear(self):
        """清空色板"""
        reply = QMessageBox.question(
            self,
            "确认 / Confirm",
            "确定清空所有颜色吗? / Are you sure to clear all colors?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.colors = []
            self.update_table()

    def on_import(self):
        """导入颜色"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("导入颜色 / Import Colors")
        file_dialog.setNameFilter("JSON Files (*.json);;CSV Files (*.csv)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        imported_colors = data.get('colors', [])
                        self.colors.extend(imported_colors)
                        self.update_table()
                        QMessageBox.information(self, "成功 / Success", f"已导入 {len(imported_colors)} 个颜色")
                # TODO: 支持CSV导入
            except Exception as e:
                QMessageBox.warning(self, "错误 / Error", f"导入失败 / Import failed: {str(e)}")

    def on_export(self):
        """导出颜色"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("导出颜色 / Export Colors")
        file_dialog.setNameFilter("JSON Files (*.json);;CSV Files (*.csv)")
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            try:
                data = {'colors': self.colors}
                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    QMessageBox.information(self, "成功 / Success", f"已导出 {len(self.colors)} 个颜色")
                # TODO: 支持CSV导出
            except Exception as e:
                QMessageBox.warning(self, "错误 / Error", f"导出失败 / Export failed: {str(e)}")

    def on_save(self):
        """保存色板"""
        custom_colors_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'data', 'custom_colors.json')

        try:
            data = {'colors': self.colors}
            with open(custom_colors_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "成功 / Success", "色板已保存 / Palette saved")
        except Exception as e:
            QMessageBox.warning(self, "错误 / Error", f"保存失败 / Save failed: {str(e)}")

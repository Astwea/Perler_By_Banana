"""
历史记录页面组件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import os
import json
from datetime import datetime


class HistoryPage(QWidget):
    """历史记录页面"""

    history_selected = pyqtSignal(str)  # 历史记录选中信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_records = []
        self.init_ui()
        self.load_history()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("📜 历史记录 / History")
        title_label.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 统计信息
        self.stats_label = QLabel("暂无记录 / No Records")
        self.stats_label.setStyleSheet("color: #7F8C8D; font-size: 14px;")
        layout.addWidget(self.stats_label)

        # 历史记录表格
        table_group = QGroupBox("项目列表 / Project List")
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

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "时间 / Time",
            "文件名 / Filename",
            "尺寸 / Size",
            "颜色数 / Colors",
            "路径 / Path"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.cellClicked.connect(self.on_history_selected)
        table_layout.addWidget(self.history_table)

        # 操作按钮
        btn_layout = QHBoxLayout()

        self.open_btn = QPushButton("📂 打开项目 / Open Project")
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self.on_open_project)
        btn_layout.addWidget(self.open_btn)

        delete_btn = QPushButton("🗑️ 删除 / Delete")
        delete_btn.setProperty("class", "danger")
        delete_btn.clicked.connect(self.on_delete)
        btn_layout.addWidget(delete_btn)

        clear_btn = QPushButton("🗑️ 清空所有 / Clear All")
        clear_btn.setProperty("class", "danger")
        clear_btn.clicked.connect(self.on_clear_all)
        btn_layout.addWidget(clear_btn)

        table_layout.addLayout(btn_layout)
        layout.addWidget(table_group)

    def load_history(self):
        """加载历史记录"""
        history_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'data', 'history.json')

        if os.path.exists(history_path):
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history_records = data.get('records', [])
                    self.update_table()
            except Exception:
                self.history_records = []

    def update_table(self):
        """更新表格"""
        self.history_table.setRowCount(len(self.history_records))

        for row, record in enumerate(self.history_records):
            self.history_table.setItem(row, 0, QTableWidgetItem(record.get('time', '')))
            self.history_table.setItem(row, 1, QTableWidgetItem(record.get('filename', '')))
            size = f"{record.get('width', 0)}x{record.get('height', 0)}"
            self.history_table.setItem(row, 2, QTableWidgetItem(size))
            self.history_table.setItem(row, 3, QTableWidgetItem(str(record.get('color_count', 0))))
            self.history_table.setItem(row, 4, QTableWidgetItem(record.get('path', '')))

        # 更新统计
        self.stats_label.setText(f"共 {len(self.history_records)} 条记录 / {len(self.history_records)} records")

    def on_history_selected(self, row: int, column: int):
        """历史记录选中事件"""
        self.open_btn.setEnabled(True)
        if row < len(self.history_records):
            record = self.history_records[row]
            self.history_selected.emit(record.get('path', ''))

    def on_open_project(self):
        """打开项目"""
        selected_row = self.history_table.currentRow()
        if selected_row >= 0 and selected_row < len(self.history_records):
            record = self.history_records[selected_row]
            path = record.get('path', '')
            if path and os.path.exists(path):
                self.history_selected.emit(path)
            else:
                QMessageBox.warning(self, "警告 / Warning", "文件不存在 / File does not exist")

    def on_delete(self):
        """删除选中的记录"""
        selected_row = self.history_table.currentRow()
        if selected_row >= 0:
            reply = QMessageBox.question(
                self,
                "确认 / Confirm",
                "确定删除这条记录吗? / Are you sure to delete this record?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                del self.history_records[selected_row]
                self.update_table()
                self.open_btn.setEnabled(False)

    def on_clear_all(self):
        """清空所有记录"""
        reply = QMessageBox.question(
            self,
            "确认 / Confirm",
            "确定清空所有记录吗? / Are you sure to clear all records?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.history_records = []
            self.update_table()
            self.open_btn.setEnabled(False)

    def add_record(self, filename: str, path: str, width: int, height: int, color_count: int):
        """添加历史记录"""
        record = {
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'filename': filename,
            'path': path,
            'width': width,
            'height': height,
            'color_count': color_count
        }

        # 插入到开头
        self.history_records.insert(0, record)

        # 限制最大记录数
        if len(self.history_records) > 100:
            self.history_records = self.history_records[:100]

        self.update_table()
        self.save_history()

    def save_history(self):
        """保存历史记录"""
        history_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'data', 'history.json')

        try:
            data = {'records': self.history_records}
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

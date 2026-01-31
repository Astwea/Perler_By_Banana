#!/usr/bin/env python3
"""
使用threading替代QThread的测试

使用Python标准库的threading，更可靠
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QObject, pyqtSignal
import time
import threading


class ThreadingWorker(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, format_type, pattern_object):
        super().__init__()
        self.format_type = format_type
        self.pattern_object = pattern_object
        print(f"[THREADING TEST] Worker.__init__() - format_type={format_type}")

    def run(self):
        print(f"[THREADING TEST] ========== Worker.run() STARTED ==========")
        print(f"[THREADING TEST] format_type={self.format_type}")
        print(f"[THREADING TEST] pattern_object is None: {self.pattern_object is None}")

        try:
            if self.format_type == 'png':
                print("[THREADING TEST] Processing PNG export...")
                for i in range(10, 101, 10):
                    self.progress.emit(i, f"Step {i//10+1}")
                    print(f"[THREADING TEST] Progress: {i}%")
                    time.sleep(0.2)

                self.progress.emit(100, "导出完成 / Export completed")
                print("[THREADING TEST] Progress: 100% - Completed")
        except Exception as e:
            print(f"[THREADING TEST] Exception: {e}")
            self.finished.emit(False, f"导出失败: {e}")
            return

        print("[THREADING TEST] ========== Worker.run() FINISHED ==========")
        self.finished.emit(True, "导出完成 / Export finished")


class ThreadingTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Threading Test")
        self.resize(600, 400)
        self.worker = None
        self.thread = None

        layout = QVBoxLayout(self)

        self.log_label = QLabel("Ready / 就绪\n准备测试threading方案")
        self.log_label.setWordWrap(True)
        self.log_label.setStyleSheet("""
            QLabel {
                background: #f0f8ff;
                color: #0000ff;
                font-family: monospace;
                font-size: 11px;
                padding: 10px;
                border: 1px solid #333;
            }
        """)
        layout.addWidget(self.log_label)

        btn = QPushButton("Start Threading Test")
        btn.setStyleSheet("padding: 10px; font-size: 12px;")
        btn.clicked.connect(self.start_test)
        layout.addWidget(btn)

    def start_test(self):
        print("\n" + "="*80)
        print("[THREADING TEST] ========== STARTING TEST ==========")
        print("="*80 + "\n")

        if self.thread and self.thread.is_alive():
            print("[THREADING TEST] Thread already running")
            return

        format_type = 'png'
        pattern_object = object()

        print(f"[THREADING TEST] Creating worker...")
        worker = ThreadingWorker(format_type, pattern_object)
        print(f"[THREADING TEST] Worker created: {id(worker)}")

        # 使用Python threading
        print("[THREADING TEST] Creating Python thread...")
        thread = threading.Thread(target=worker.run, daemon=True)
        print(f"[THREADING TEST] Thread created: {id(thread)}")

        # 连接信号（threading不需要连接started信号）
        worker.progress.connect(self.on_progress)
        print("[THREADING TEST]   - progress signal connected")
        worker.finished.connect(self.on_finished)
        print("[THREADING TEST]   - finished signal connected")

        self.worker = worker
        self.thread = thread

        print("\n" + "-"*80)
        print("[THREADING TEST] Starting thread (threading.Thread.start())...")
        print("-"*80 + "\n")
        thread.start()
        print("[THREADING TEST] thread.start() returned")

    def on_progress(self, percent, message):
        print(f"[THREADING TEST UI] Progress: {percent}% - {message}")
        log_text = self.log_label.text()
        self.log_label.setText(f"{log_text}\n\nProgress: {percent}% - {message}")
        QApplication.processEvents()

    def on_finished(self, success, message):
        print("\n" + "="*80)
        print(f"[THREADING TEST] Worker finished: success={success}, message={message}")
        print("="*80 + "\n")

        if success:
            self.log_label.setText(f"{self.log_label.text()}\n\n✓ SUCCESS: {message}")
        else:
            self.log_label.setText(f"{self.log_label.text()}\n\n✗ FAILED: {message}")

        self.worker = None
        self.thread = None


if __name__ == '__main__':
    print("\n" + "="*80)
    print("Threading Test Application")
    print("使用Python threading替代QThread")
    print("="*80 + "\n")

    app = QApplication(sys.argv)
    window = ThreadingTestWindow()
    window.show()

    print("Application ready. Click 'Start Threading Test' button.")
    print("="*80 + "\n")

    sys.exit(app.exec())

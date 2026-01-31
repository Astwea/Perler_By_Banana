#!/usr/bin/env python3
"""
简化测试 - 模拟实际的导出流程

这个测试模仿result_page.py的_start_export方法
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QThread, pyqtSignal, QObject
import time


class TestExportWorker(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, format_type, pattern_object):
        super().__init__()
        self.format_type = format_type
        self.pattern_object = pattern_object

    def run(self):
        print(f"[SIMPLIFIED TEST] Worker.run() STARTED - format_type={self.format_type}")
        print(f"[SIMPLIFIED TEST] pattern_object is None: {self.pattern_object is None}")
        
        try:
            if self.format_type == 'png':
                print("[SIMPLIFIED TEST] Processing PNG export...")
                if self.pattern_object:
                    print("[SIMPLIFIED TEST] Would call pattern_object.to_image() here")
                    # 不实际调用to_image()，只模拟时间
                    for i in range(5):
                        self.progress.emit(20 + i * 10, f"Step {i+1}")
                        print(f"[SIMPLIFIED TEST] Progress: {20 + i * 10}%")
                        time.sleep(0.3)
                    
                    self.progress.emit(80, "保存文件 / Saving")
                    print("[SIMPLIFIED TEST] Progress: 80% - Saving")
                    time.sleep(0.5)
                    
                    self.progress.emit(100, "导出完成 / Export completed")
                    print("[SIMPLIFIED TEST] Progress: 100% - Completed")
                else:
                    print("[SIMPLIFIED TEST] No pattern_object, using fallback")
                    self.progress.emit(50, "使用备用方案 / Using fallback")
                    time.sleep(1)
                    self.progress.emit(100, "导出完成 / Export completed")
        except Exception as e:
            print(f"[SIMPLIFIED TEST] Exception: {e}")
            self.finished.emit(False, f"导出失败: {e}")
            return

        print("[SIMPLIFIED TEST] Worker.run() FINISHED")
        self.finished.emit(True, "导出完成 / Export finished")


class SimplifiedTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simplified Export Test")
        self.resize(600, 400)
        self.worker = None
        self.thread = None

        layout = QVBoxLayout(self)

        self.log_label = QLabel("Ready / 就绪\n准备测试导出流程")
        self.log_label.setWordWrap(True)
        self.log_label.setStyleSheet("""
            QLabel {
                background: #f0f0f0;
                color: #00ff00;
                font-family: monospace;
                font-size: 11px;
                padding: 10px;
                border: 1px solid #333;
            }
        """)
        layout.addWidget(self.log_label)

        btn = QPushButton("Start Simplified Test / 开始简化测试")
        btn.setStyleSheet("padding: 10px; font-size: 12px;")
        btn.clicked.connect(self.start_test)
        layout.addWidget(btn)

    def start_test(self):
        print("\n" + "="*80)
        print("[SIMPLIFIED TEST] ========== STARTING TEST ==========")
        print("="*80 + "\n")

        if self.thread and self.thread.isRunning():
            print("[SIMPLIFIED TEST] Thread already running")
            return

        format_type = 'png'
        pattern_object = object()  # 模拟有一个pattern_object

        print(f"[SIMPLIFIED TEST] Creating worker with format_type={format_type}")
        print(f"[SIMPLIFIED TEST] pattern_object={pattern_object is not None}")

        self.log_label.setText(f"Creating worker...\nformat_type: {format_type}\npattern_object: {pattern_object is not None}")

        worker = TestExportWorker(format_type, pattern_object)

        print("[SIMPLIFIED TEST] Creating thread...")
        thread = QThread(self)

        print("[SIMPLIFIED TEST] Connecting signals...")
        worker.progress.connect(self.on_progress)
        print("[SIMPLIFIED TEST]   - progress signal connected")
        worker.finished.connect(self.on_finished)
        print("[SIMPLIFIED TEST]   - finished signal connected")
        worker.finished.connect(thread.quit)
        print("[SIMPLIFIED TEST]   - thread.quit connected")
        worker.finished.connect(worker.deleteLater)
        print("[SIMPLIFIED TEST]   - worker.deleteLater connected")
        thread.finished.connect(thread.deleteLater)
        print("[SIMPLIFIED TEST]   - thread.deleteLater connected")

        print("[SIMPLIFIED TEST] Connecting thread.started to worker.run...")
        thread.started.connect(worker.run)
        print("[SIMPLIFIED TEST]   - thread.started connected to worker.run")

        print("[SIMPLIFIED TEST] Moving worker to thread...")
        worker.moveToThread(thread)
        print("[SIMPLIFIED TEST]   - worker moved to thread")

        self.worker = worker
        self.thread = thread

        print("\n" + "-"*80)
        print("[SIMPLIFIED TEST] Calling thread.start()...")
        print("-"*80 + "\n")
        thread.start()

    def on_progress(self, percent, message):
        print(f"[SIMPLIFIED TEST UI] Progress: {percent}% - {message}")
        log_text = self.log_label.text()
        self.log_label.setText(f"{log_text}\n\nProgress: {percent}% - {message}")
        QApplication.processEvents()

    def on_finished(self, success, message):
        print("\n" + "="*80)
        print(f"[SIMPLIFIED TEST] Worker finished: success={success}, message={message}")
        print("="*80 + "\n")

        if success:
            self.log_label.setText(f"{self.log_label.text()}\n\n✓ SUCCESS: {message}")
        else:
            self.log_label.setText(f"{self.log_label.text()}\n\n✗ FAILED: {message}")

        self.worker = None
        self.thread = None


if __name__ == '__main__':
    print("\n" + "="*80)
    print("Simplified Export Test")
    print("模仿result_page.py的导出流程")
    print("="*80 + "\n")

    app = QApplication(sys.argv)
    window = SimplifiedTestWindow()
    window.show()

    print("Application ready. Click 'Start Simplified Test' button.")
    print("="*80 + "\n")

    sys.exit(app.exec())

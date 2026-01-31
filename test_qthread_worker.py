#!/usr/bin/env python3
"""
QThread启动测试 - 验证worker.run()是否被调用

使用方法:
    python test_qthread_worker.py
"""

import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QThread, pyqtSignal, QObject


class SimpleWorker(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        print("[TEST WORKER] __init__() called")

    def run(self):
        print("[TEST WORKER] run() method STARTED!")
        print("[TEST WORKER] Emitting progress...")
        
        for i in range(10, 101, 10):
            self.progress.emit(i, f"Step {i}")
            print(f"[TEST WORKER] Progress: {i}%")
            time.sleep(0.2)  # 模拟工作
        
        print("[TEST WORKER] Emitting finished...")
        self.finished.emit(True, "Test completed successfully")
        print("[TEST WORKER] run() method FINISHED!")


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QThread Worker Test")
        self.resize(500, 400)
        self.worker = None
        self.thread = None

        layout = QVBoxLayout(self)

        self.status_label = QLabel("Click button to test worker")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.status_label)

        btn = QPushButton("Start Worker Test")
        btn.setStyleSheet("padding: 10px; font-size: 12px;")
        btn.clicked.connect(self.start_worker)
        layout.addWidget(btn)

    def start_worker(self):
        print("\n" + "="*60)
        print("[TEST] ========== STARTING TEST ==========")
        print("="*60 + "\n")

        if self.thread and self.thread.isRunning():
            print("[TEST] Thread already running!")
            return

        # 1. 创建worker
        print("[TEST] Step 1: Creating worker...")
        worker = SimpleWorker()

        # 2. 创建线程
        print("[TEST] Step 2: Creating thread...")
        thread = QThread(self)

        # 3. 连接信号
        print("[TEST] Step 3: Connecting signals...")
        worker.progress.connect(self.on_progress)
        worker.finished.connect(self.on_finished)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        print("[TEST]   - progress signal connected")
        print("[TEST]   - finished signal connected")
        print("[TEST]   - thread.quit connected")
        print("[TEST]   - thread.deleteLater connected")

        # 4. 连接started信号
        print("[TEST] Step 4: Connecting thread.started...")
        thread.started.connect(worker.run)
        print("[TEST]   - thread.started connected to worker.run")

        # 5. 保存引用
        self.worker = worker
        self.thread = thread

        # 6. 启动线程
        print("[TEST] Step 5: Starting thread...")
        self.status_label.setText("Worker running... / 工作中...")
        thread.start()
        print("[TEST]   - thread.start() called")
        print("[TEST]   - Thread started (or should be)")
        print("\n[TEST] Waiting for worker to run...")
        print("="*60 + "\n")

    def on_progress(self, percent, message):
        print(f"[TEST UI] Progress: {percent}% - {message}")
        self.status_label.setText(f"{percent}% - {message}")

    def on_finished(self, success, message):
        print("\n" + "="*60)
        print(f"[TEST UI] Worker finished: success={success}, message={message}")
        print("="*60 + "\n")
        
        if success:
            self.status_label.setText(f"SUCCESS / 成功: {message}")
        else:
            self.status_label.setText(f"FAILED / 失败: {message}")
        
        self.worker = None
        self.thread = None


if __name__ == '__main__':
    print("\n" + "="*60)
    print("QThread Worker Test Application")
    print("="*60 + "\n")

    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("Application ready. Click 'Start Worker Test' button.")
    print("="*60 + "\n")
    
    sys.exit(app.exec())

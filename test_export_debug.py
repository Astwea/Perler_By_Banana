import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QThread, pyqtSignal, QObject
import time


class TestExportWorker(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()

    def run(self):
        print("[TEST] Worker.run() started")
        self.progress.emit(5, "Test 5%")
        time.sleep(0.5)
        self.progress.emit(20, "Test 20%")
        time.sleep(0.5)
        self.progress.emit(50, "Test 50%")
        time.sleep(0.5)
        self.progress.emit(80, "Test 80%")
        time.sleep(0.5)
        self.progress.emit(100, "Test 100%")
        print("[TEST] Worker.run() completed")
        self.finished.emit(True, "Test completed")


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Export Test")
        self.resize(400, 300)
        self.worker = None
        self.thread = None

        layout = QVBoxLayout(self)

        self.status_label = QLabel("Ready / 就绪")
        layout.addWidget(self.status_label)

        btn = QPushButton("Start Test Export / 开始测试导出")
        btn.clicked.connect(self.start_test)
        layout.addWidget(btn)

    def start_test(self):
        print("[TEST] Starting test export")
        if self.thread and self.thread.isRunning():
            print("[TEST] Thread already running")
            return

        self.status_label.setText("Running... / 运行中...")

        worker = TestExportWorker()
        thread = QThread(self)

        worker.moveToThread(thread)
        worker.progress.connect(self.on_progress)
        worker.finished.connect(self.on_finished)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        thread.started.connect(worker.run)

        self.worker = worker
        self.thread = thread

        print("[TEST] Starting thread")
        thread.start()
        print("[TEST] Thread started")

    def on_progress(self, percent, message):
        print(f"[TEST] Progress: {percent}% - {message}")
        self.status_label.setText(f"{percent}% - {message}")

    def on_finished(self, success, message):
        print(f"[TEST] Finished: success={success}, message={message}")
        if success:
            self.status_label.setText(f"Success / 成功: {message}")
        else:
            self.status_label.setText(f"Failed / 失败: {message}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    print("[TEST] Application started")
    sys.exit(app.exec())

# PNG导出Debug指南

## 问题描述
导出功能卡在"正在导出"状态不动。

## 已添加的Debug日志

### ExportWorker.run() 方法中的日志

#### PNG导出:
```
[DEBUG] ExportWorker.run() - format_type=png, pattern_object=True/False, labeled_path=/path/to/file.png or None
[DEBUG] Using pattern_object for PNG export  (如果使用pattern_object)
[DEBUG] PNG save completed: /path/to/output.png
```
或
```
[DEBUG] Using cached image for PNG export  (如果使用缓存图像)
[DEBUG] PNG copy completed: /path/to/source.png -> /path/to/dest.png
```
或
```
[DEBUG] No valid source for PNG export  (如果两者都不可用)
```

#### JSON/CSV导出:
```
[DEBUG] ExportWorker.run() - format_type=json/csv, pattern_data=True/False
[DEBUG] Writing JSON/CSV to: /path/to/file
[DEBUG] JSON/CSV write completed
```

#### 未知格式:
```
[DEBUG] ExportWorker.run() - format_type=unknown
[DEBUG] Unsupported format: unknown
```

### 异常情况:
```
[DEBUG] Exception in ExportWorker.run(): <异常信息>
<完整堆栈跟踪>
```

### 线程启动:
```
[DEBUG] Starting export thread for format: png/json/csv
```

### 进度更新:
```
[DEBUG] Progress update: 5% - 准备导出 / Preparing
[DEBUG] Progress update: 10% - 正在导出 PNG / Exporting PNG
[DEBUG] Progress update: 20% - 生成基础图像 / Rendering base image
...
```

### 导出完成:
```
[DEBUG] Export finished: success=True/False, message=导出完成 / Export finished
```

## Debug步骤

### 1. 查看控制台输出

运行桌面应用时，观察终端输出：
```bash
cd desktop
python main_window.py
```

点击"导出PNG"按钮，观察输出：
- 如果看到 `[DEBUG] ExportWorker.run() started` → 线程启动成功
- 如果看到 `format_type=png` → 格式正确
- 如果看到 `pattern_object=None` → 这是问题所在！

### 2. 常见问题诊断

#### 问题1: pattern_object为None
**症状**: 进度停在10% "正在导出"

**原因**: 在 `ResultPage.on_export()` 中没有正确设置 `self.pattern_object`

**检查**: 在 `main_window.py` 的 `on_process_completed()` 方法中
```python
if 'bead_pattern' in results and hasattr(self.result_page, 'set_pattern_object'):
    self.result_page.set_pattern_object(results.get('bead_pattern'))
```

**解决**: 确保从 `process_page` 传递了 `bead_pattern` 对象

#### 问题2: 线程没有启动
**症状**: 没有任何debug输出

**原因**: `thread.start()` 没有被调用

**检查**: 查看 `_start_export` 方法末尾是否有 `thread.start()`

#### 问题3: to_image() 方法卡死
**症状**: 看到进度到40%或50%后没有更新

**原因**: `BeadPattern.to_image()` 执行时间过长或死循环

**解决**: 检查 `bead_pattern/render/labels.py` 的 `overlay_labels` 方法

### 3. 运行简单测试

运行独立的测试程序验证基本功能:
```bash
python test_export_debug.py
```

这个测试会：
1. 创建一个简单的worker
2. 启动线程
3. 发出多个进度信号
4. 检查是否正确接收

### 4. 检查pattern_object传递链

在终端中添加日志查看pattern_object何时设置:

```python
# 在 main_window.py 的 on_process_completed 中添加:
print(f"[MAIN] on_process_completed: results keys = {list(results.keys())}")
print(f"[MAIN] bead_pattern in results: {'bead_pattern' in results}")
if 'bead_pattern' in results:
    print(f"[MAIN] bead_pattern type: {type(results['bead_pattern'])}")
```

# 在 result_page.py 的 set_pattern_object 中添加:
def set_pattern_object(self, bead_pattern) -> None:
    print(f"[RESULT] set_pattern_object called: {bead_pattern is not None}")
    self.pattern_object = bead_pattern
```

## 预期输出（正常PNG导出）

```
[DEBUG] Starting export thread for format: png
[DEBUG] ExportWorker.run() - format_type=png, pattern_object=True, labeled_path=/some/path.png
[DEBUG] Using pattern_object for PNG export
[DEBUG] Progress update: 5% - 准备导出 / Preparing
[DEBUG] Progress update: 10% - 正在导出 PNG / Exporting PNG
[DEBUG] Progress update: 20% - 生成基础图像 / Rendering base image
[DEBUG] Progress update: 30% - 添加网格 / Adding grid
[DEBUG] Progress update: 40% - 渲染标签 / Rendering labels
[DEBUG] Progress update: 50% - 合成图像 / Compositing image
[DEBUG] Progress update: 70% - 准备保存 / Preparing save
[DEBUG] Progress update: 80% - 保存文件 / Saving
[DEBUG] Progress update: 90% - 完成保存 / Finishing save
[DEBUG] PNG save completed: /path/to/output.png
[DEBUG] Progress update: 100% - 导出完成 / Export completed
[DEBUG] Export finished: success=True, message=导出完成 / Export finished
```

## 如果仍然卡住

1. 按Ctrl+C强制退出应用
2. 查看最后一条debug消息
3. 根据最后一条消息定位问题

## 可能的修复方案

### 方案A: 修改process_page传递pattern_object

在 `process_page.py` 中，确保在 `process_completed.emit()` 时包含 `bead_pattern`:

```python
self.process_completed.emit({
    'pattern_data': result_data,
    'pattern_image_with_labels': str(viz_path_with),
    'pattern_image_no_labels': str(viz_path_no),
    'bead_pattern': bead_pattern  # 确保这一行存在
})
```

### 方案B: 使用labeled_path作为fallback

如果pattern_object不可用，修改ExportWorker使用已有的缓存图像:

```python
elif self.labeled_path and os.path.exists(self.labeled_path):
    self.progress.emit(60, "使用缓存图像 / Using cached image")
    shutil.copyfile(self.labeled_path, self.file_path)
```

### 方案C: 添加超时机制

在 `_start_export` 中添加超时检测:

```python
def _on_export_timeout(self):
    print("[DEBUG] Export timeout detected!")
    if self._export_thread and self._export_thread.isRunning():
        print("[DEBUG] Force terminating stuck thread")
        self._export_thread.terminate()
        self._export_thread.wait()
        self._on_export_finished(False, "导出超时 / Export timeout")

# 创建进度对话框后添加超时定时器
timeout_timer = QTimer(self)
timeout_timer.timeout.connect(self._on_export_timeout)
timeout_timer.start(60000)  # 60秒超时
```

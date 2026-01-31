# 前端"导出工程图"按钮功能说明

## 修改概述

在"处理结果"页面新增了"导出工程图"按钮，用户可以直接导出带工程说明书风格信息面板的拼豆图。

## 修改文件

### 1. templates/index.html
在"查看结果"部分的导出选项区域添加了新按钮：

```html
<button class="btn btn-primary" id="exportTechnicalSheetBtn">导出工程图</button>
```

按钮样式：
- 使用 `btn-primary` 样式，与普通导出按钮区分
- 位于"导出PNG"按钮之后

### 2. static/js/main.js

#### 按钮绑定 (setupExportButtons函数)
```javascript
const exportTechnicalSheetBtn = document.getElementById('exportTechnicalSheetBtn');
if (exportTechnicalSheetBtn) {
    exportTechnicalSheetBtn.onclick = exportTechnicalSheet;
}
```

#### 导出函数 (exportTechnicalSheet)
```javascript
async function exportTechnicalSheet() {
    if (!currentPatternId) {
        showError('请先生成图案');
        return;
    }

    try {
        const params = {
            font_size: 12,
            color_block_size: 24,
            row_height: 32,
            panel_padding: 20,
            margin_from_pattern: 20,
            show_total_count: true,
            show_dimensions: true,
            show_bead_size: true,
            sort_by_count: true,
            exclude_background: true
        };

        const response = await fetch(`/api/pattern/${currentPatternId}/technical-sheet`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });

        if (!response.ok) {
            throw new Error('导出工程图失败');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pattern_${currentPatternId}_technical_sheet.png`;
        a.click();
        window.URL.revokeObjectURL(url);

        showSuccess('工程图导出成功！');
    } catch (error) {
        showError('导出工程图失败: ' + error.message);
    }
}
```

### 3. static/js/main.js - 语法修复
修复了第9行的JavaScript语法错误，将中文括号改为英文括号：

```javascript
// 修复前
let executionController = null; // 执行控制器（用于AbortController）

// 修复后
let executionController = null; // 执行控制器(用于AbortController)
```

## 功能说明

### 使用流程

1. **上传图片** → 生成拼豆图案
2. **在"查看结果"页面** → 看到生成的图案
3. **点击"导出工程图"按钮** → 下载带信息面板的工程图纸

### 导出参数

默认参数（可在JavaScript中调整）：
- `font_size`: 12 - 正文字体大小
- `color_block_size`: 24 - 颜色方块大小
- `row_height`: 32 - 每行高度
- `panel_padding`: 20 - 面板内边距
- `margin_from_pattern`: 20 - 面板与图案间距
- `show_total_count`: true - 显示总拼豆数量
- `show_dimensions`: true - 显示成品尺寸
- `show_bead_size`: true - 显示拼豆尺寸
- `sort_by_count`: true - 按使用数量排序
- `exclude_background`: true - 排除背景色

### 文件命名

导出文件名格式：`pattern_{pattern_id}_technical_sheet.png`

例如：`pattern_abc123_technical_sheet.png`

### 输出内容

导出的工程图纸包含：
1. **拼豆图案主体**（带网格线）
2. **工程说明书风格信息面板**，包括：
   - COLOR LIST 标题
   - 颜色列表（色块 + 色号 + 数量）
   - 统计信息（总数、尺寸、拼豆规格）

### 错误处理

- **未生成图案**：显示"请先生成图案"错误提示
- **导出失败**：显示"导出工程图失败: {错误信息}"
- **成功**：显示"工程图导出成功！"成功提示

## 测试

### 测试步骤

1. 启动服务器：`python app.py`
2. 访问：http://localhost:8000
3. 上传一张图片
4. 生成拼豆图案
5. 在结果页面点击"导出工程图"按钮
6. 检查下载的文件是否包含信息面板

### 预期结果

- 下载的PNG文件包含完整的拼豆图案和右侧信息面板
- 面板显示颜色统计、数量、尺寸等信息
- 面板风格为工程说明书样式（白色背景、无衬线字体）

## 与其他导出按钮对比

| 按钮 | 文件名 | 内容 |
|------|--------|------|
| 导出JSON | `pattern_{id}.json` | 图案数据（JSON格式） |
| 导出CSV | `pattern_{id}.csv` | 图案数据（CSV格式） |
| 导出PNG | `pattern_{id}.png` | 图案可视化（无信息面板） |
| **导出工程图** | `pattern_{id}_technical_sheet.png` | **图案 + 信息面板** |
| 打印预览 | - | 预览打印效果 |
| 生成PDF | `pattern_{id}.pdf` | 打印文件 |

## 技术细节

### API调用

使用POST方法调用：`/api/pattern/{pattern_id}/technical-sheet`

请求头：
```json
{
    "Content-Type": "application/json"
}
```

请求体：TechnicalPanelParams（JSON格式）

响应：PNG文件（image/png）

### Blob处理

使用标准浏览器API处理文件下载：
1. `response.blob()` - 获取二进制数据
2. `URL.createObjectURL(blob)` - 创建临时URL
3. 动态创建`<a>`元素并点击
4. `URL.revokeObjectURL()` - 释放内存

### 用户反馈

使用现有的通知系统：
- `showError(msg)` - 显示错误提示
- `showSuccess(msg)` - 显示成功提示

## 后续优化建议

1. **参数自定义**：可以添加弹窗让用户自定义面板参数
2. **进度显示**：生成大图时可以显示进度条
3. **格式选择**：支持导出为PDF格式
4. **预览功能**：点击按钮前先预览工程图效果
5. **模板选择**：支持不同的面板布局模板

## 已知问题

无

## 版本历史

- v1.0 (2026-01-31) - 初始版本
  - 添加"导出工程图"按钮
  - 实现导出功能
  - 修复JavaScript语法错误

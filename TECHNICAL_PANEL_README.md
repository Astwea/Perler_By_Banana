# 工程说明书风格信息面板功能说明

## 功能概述

新增了工程说明书风格的信息面板功能，可以在拼豆图的空白区域自动生成包含颜色统计、成品尺寸等信息的专业说明书面板。

## 主要特性

### 1. 智能空白区域检测
- 基于主体bounding box计算空白区域
- 优先在右侧/右下角放置面板
- 空间不足时自动扩展画布

### 2. 工程说明书风格设计
- 白色背景、无装饰
- 无衬线字体（Arial）
- 高可读性、清晰对齐
- 面板与主体图案有明确留白

### 3. 信息面板内容
- **颜色示意块**：24x24像素的色块，带边框
- **颜色色号**：标准化的色号显示
- **使用数量**：按使用数量排序显示
- **总拼豆数量**：排除背景后的总数
- **成品尺寸**：宽×高（毫米）
- **拼豆尺寸**：2.6mm或5.0mm

### 4. 统计数据导出
- **JSON格式**：结构化数据，包含所有颜色信息
- **CSV格式**：表格数据，可在Excel中打开
- 支持排除背景色的统计
- 包含品牌、系列等详细信息

## API接口

### 1. 生成工程图纸

**端点**: `POST /api/pattern/{pattern_id}/technical-sheet`

**请求参数**:
```json
{
  "font_size": 12,
  "color_block_size": 24,
  "row_height": 32,
  "panel_padding": 20,
  "margin_from_pattern": 20,
  "show_total_count": true,
  "show_dimensions": true,
  "show_bead_size": true,
  "sort_by_count": true,
  "exclude_background": true
}
```

**响应**: 返回工程图纸的PNG文件

### 2. 导出统计数据

**端点**: `GET /api/pattern/{pattern_id}/statistics`

**查询参数**:
- `format`: 导出格式（'json' 或 'csv'）
- `exclude_background`: 是否排除背景色（默认true）

**响应**: 返回统计数据文件（JSON或CSV）

## 使用示例

### Python代码示例

```python
from bead_pattern.render.technical_panel import (
    generate_technical_sheet,
    export_statistics,
    TechnicalPanelConfig
)
from bead_pattern import BeadPattern

# 生成工程图纸
config = TechnicalPanelConfig(
    font_size=12,
    color_block_size=24,
    panel_padding=20
)

tech_sheet = generate_technical_sheet(
    pattern,
    cell_size=10,
    show_grid=True,
    show_labels=False,  # 工程图纸通常不显示编号
    config=config
)

tech_sheet.save("technical_sheet.png")

# 导出统计数据
export_statistics(pattern, "stats.json", format="json")
export_statistics(pattern, "stats.csv", format="csv")
```

### cURL示例

```bash
# 生成工程图纸
curl -X POST "http://localhost:8000/api/pattern/{pattern_id}/technical-sheet" \
  -H "Content-Type: application/json" \
  -d '{"font_size": 12, "sort_by_count": true}' \
  --output technical_sheet.png

# 导出JSON统计
curl "http://localhost:8000/api/pattern/{pattern_id}/statistics?format=json" \
  --output stats.json

# 导出CSV统计
curl "http://localhost:8000/api/pattern/{pattern_id}/statistics?format=csv" \
  --output stats.csv
```

## 配置参数说明

### TechnicalPanelConfig

| 参数 | 类型 | 默认值 | 说明 |
|------|------|----------|------|
| font_size | int | 12 | 正文字体大小 |
| color_block_size | int | 24 | 颜色方块大小（像素） |
| row_height | int | 32 | 每行高度（像素） |
| panel_padding | int | 20 | 面板内边距（像素） |
| margin_from_pattern | int | 20 | 面板与图案的间距（像素） |
| background_color | tuple | (255,255,255) | 背景颜色（RGB） |
| text_color | tuple | (0,0,0) | 文本颜色（RGB） |
| border_width | int | 0 | 边框宽度（0表示无边框） |
| header_font_size | int | 14 | 标题字体大小 |

### 显示选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|----------|------|
| show_total_count | bool | true | 是否显示总拼豆数量 |
| show_dimensions | bool | true | 是否显示成品尺寸 |
| show_bead_size | bool | true | 是否显示拼豆尺寸 |
| sort_by_count | bool | true | 是否按使用数量排序 |
| exclude_background | bool | true | 是否排除背景色 |

## 输出格式

### JSON统计格式

```json
{
  "total_beads": 400,
  "unique_colors": 4,
  "bead_size_mm": 2.6,
  "dimensions": {
    "width": 5,
    "height": 5,
    "width_mm": 13.0,
    "height_mm": 13.0
  },
  "colors": [
    {
      "color_id": 1,
      "display_code": "BLK",
      "name_zh": "黑色",
      "name_en": "Black",
      "code": "BLK",
      "rgb": [0, 0, 0],
      "count": 16,
      "brand": null,
      "series": null
    }
  ]
}
```

### CSV统计格式

```csv
颜色ID,色号,中文名称,英文名称,品牌,系列,R,G,B,数量
1,BLK,黑色,Black,,,0,0,0,16
2,RED,红色,Red,,,255,0,0,8

统计信息
总拼豆数,400
颜色数量,4
拼豆尺寸(mm),2.6
成品宽度(mm),13.0
成品高度(mm),13.0
```

## 技术实现

### 核心模块

- **bead_pattern/render/technical_panel.py**: 核心实现模块
  - `TechnicalPanelConfig`: 面板配置类
  - `detect_empty_space()`: 空白区域检测
  - `render_technical_panel()`: 渲染信息面板
  - `composite_pattern_with_panel()`: 合成面板与图案
  - `generate_technical_sheet()`: 生成完整工程图纸
  - `export_statistics()`: 导出统计数据

### 关键算法

1. **空白区域检测**: 基于主体的bounding box，计算四个方向的空白区域
2. **面板尺寸计算**: 根据颜色数量和字体大小动态计算所需尺寸
3. **画布扩展**: 当右侧/下侧空间不足时，自动扩展画布
4. **颜色排序**: 支持按使用数量、色号等维度排序

### 兼容性

- 支持BeadPatternV2和BeadPattern（兼容层）对象
- 正确处理numpy类型与Python原生类型的转换
- 自动检测并使用系统字体

## 测试

运行测试脚本：

```bash
python test_technical_panel.py
```

测试内容：
1. 生成工程图纸
2. 导出JSON统计
3. 导出CSV统计

测试输出保存在`test_output/`目录：
- `technical_sheet_test.png`: 工程图纸
- `stats_test.json`: JSON统计
- `stats_test.csv`: CSV统计

## 文件结构

```
bead_pattern/render/
└── technical_panel.py    # 工程说明书面板模块
```

## 注意事项

1. **字体兼容性**: 代码会自动查找系统字体（Arial），如果找不到则使用默认字体
2. **性能优化**: 所有图像生成操作都在线程池中执行，避免阻塞事件循环
3. **类型安全**: 正确处理numpy的int64类型与Python原生类型的转换
4. **空白背景**: 默认排除白色背景进行统计，可通过参数控制

## 未来扩展

- 支持自定义面板布局（左侧、底部等）
- 支持多语言面板（英文/中文）
- 支持自定义字段（如日期、备注等）
- 支持导出为PDF格式
- 支持批量生成多个面板

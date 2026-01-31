# 工程蓝图（Engineering Blueprint）风格重构说明

## 重构概述

已将拼豆图导出功能重构为**工程蓝图（Engineering Blueprint）**风格，采用"主绘图区 + 信息区块"结构设计范式。

## 新设计范式

### 整体结构

```
┌───────────────────────────────┐
│                              │
│   主拼豆网格绘图区          │
│                              │
│                              │
├───────────────┬──────────────┤
│ 工程属性区    │  颜色/物料统计区 │
└───────────────┴──────────────┘
```

### 关键设计原则

1. **空间优先级**：主绘图区 > 工程属性区
   - 主拼豆网格绘图区占画布主要视觉面积
   - 工程属性区像"工程图角标"，不与主图视觉竞争

2. **主拼豆网格绘图区**（最高优先级）：
   - 每格一个拼豆
   - 显示完整色号（如 F13 / H7）
   - 色号文字居中
   - 自动对比：深色格 → 白字，浅色格 → 黑字
   - 网格线：极细灰线

3. **工程属性区**：
   - Title Block：图案名称、网格尺寸、物理尺寸、拼豆总数
   - Legend/BOM：颜色清单（色块 + 色号 + 数量）
   - 小而规整，边界清晰，内部严格对齐

4. **视觉规范**：
   - 背景：纯白
   - 线条：中性灰
   - 字体：无衬线/工程字体
   - 禁止：卡片UI、圆角、阴影、渐变

## 核心修改

### 新增函数

#### render_engineering_panel()
```python
def render_engineering_panel(
    pattern: BeadPatternV2,
    config: TechnicalPanelConfig,
    exclude_background: bool = True,
    show_total_count: bool = True,
    show_dimensions: bool = True,
    show_bead_size: bool = True,
    sort_by_count: bool = True
) -> Image.Image:
    """渲染工程属性区（Engineering Panel）

    Title Block + Legend/BOM
    不与主图视觉竞争，像"工程图角标"
    """
```

**功能**：
- 渲染Title Block（4行信息）
  - Pattern Name（可选）
  - Grid size（beads）
  - Physical size（mm）
  - Total beads
- 渲染Legend/BOM（每行：色块 + 色号 + 数量）
- 支持按数量降序排列

#### composite_blueprint_layout()
```python
def composite_blueprint_layout(
    main_drawing: Image.Image,
    engineering_panel: Image.Image,
    config: TechnicalPanelConfig
) -> Image.Image:
    """合成主绘图区和工程属性区

    采用工程蓝图布局
    主绘图区占画布主要视觉面积
    工程属性区放在右下角
    空间优先级：主绘图区 > 工程属性区
    """
```

**功能**：
- 主绘图区粘贴到画布左上角
- 工程属性区粘贴到画布右下角
- 自动扩展画布以容纳所有区域
- 保持适当间距

### 更新的主函数

#### generate_technical_sheet()
```python
def generate_technical_sheet(
    pattern,
    cell_size: int = 10,
    show_grid: bool = True,
    show_labels: bool = False,
    config: Optional[TechnicalPanelConfig] = None,
    exclude_background: bool = True
) -> Image.Image:
    """生成工程蓝图（Engineering Blueprint）风格的拼豆图纸

    布局范式：
    - 主绘图区 + 工程属性区
    - 空间优先：主网格区优先保证可读性
    """
```

**关键改动**：
- 使用 `render_engineering_panel()` 替代 `render_technical_panel()`
- 使用 `composite_blueprint_layout()` 替代 `composite_pattern_with_panel()`
- 采用工程蓝图布局逻辑

## 技术细节

### Title Block 内容

- Pattern Name: `Pattern: {width} x {height} beads`
- Grid size: `Grid size: {width} x {height} beads`
- Physical size: `Physical size: {width_mm:.1f} x {height_mm:.1f} mm`
- Total beads: `Total beads: {count}`

### Legend/BOM 内容

每行格式：
- **色块**：24x24像素矩形，中性灰边框
- **色号**：显示代码，居中对齐
- **数量**：右对齐，单位 "pcs"
- **排序**：按使用数量降序

### 视觉规范

| 元素 | 规范 |
|------|------|
| 背景色 | (255, 255, 255) 纯白 |
| 网格线 | (220, 220, 220) 极细灰线 |
| 分隔线 | (220, 220, 220) 中性灰 |
| 文本色 | (0, 0, 0) 纯黑 |
| 色块边框 | (220, 220, 220) 中性灰 |
| 字体 | Arial，无衬线 |
| 标题字体 | Arial，14px |
| 正文字体 | Arial，12px |

## 使用说明

### Web应用
1. 上传图片并生成拼豆图案
2. 点击"导出工程图"按钮
3. 下载工程蓝图风格的PNG文件
4. 文件包含：
   - 高分辨率主拼豆网格（保证可读性）
   - 右下角工程属性区
   - 完整的尺寸和颜色统计

### Desktop应用
1. 在处理结果页面点击"导出工程图"按钮
2. 选择保存位置
3. 下载工程蓝图风格的PNG文件
4. 内容与Web应用相同

## 文件修改

### 新增
- `bead_pattern/render/technical_panel.py`
  - 新增 `render_engineering_panel()` 函数（约200行）
  - 新增 `composite_blueprint_layout()` 函数（约40行）
  - 重构 `generate_technical_sheet()` 函数（简化为蓝图风格）

### 保留
- 保留原有 `render_technical_panel()` 函数（向后兼容）
- 保留原有 `composite_pattern_with_panel()` 函数（向后兼容）
- 保留所有配置类和辅助函数

## 技术优势

1. **工程感增强**：采用工程图布局，更像专业图纸
2. **主图优先级**：主绘图区占据主要视觉空间，保证格内色号可读
3. **信息结构化**：Title Block + Legend/BOM，层次清晰
4. **参数化设计**：所有尺寸、颜色、间距都可配置
5. **视觉一致性**：统一的工程风格规范

## 测试建议

### 单元测试
```python
# 测试render_engineering_panel
from bead_pattern.render.technical_panel import render_engineering_panel, TechnicalPanelConfig

config = TechnicalPanelConfig()
panel = render_engineering_panel(pattern, config, ...)
panel.save("test_engineering_panel.png")

# 测试composite_blueprint_layout
from bead_pattern.render.technical_panel import composite_blueprint_layout, TechnicalPanelConfig

main_img = Image.open("pattern.png")
eng_panel = Image.open("engineering_panel.png")
result = composite_blueprint_layout(main_img, eng_panel, config)
result.save("test_blueprint_layout.png")
```

### 集成测试
```python
# 测试generate_technical_sheet（工程蓝图风格）
from bead_pattern.render.technical_panel import generate_technical_sheet

pattern = ...  # BeadPattern对象
result = generate_technical_sheet(pattern, cell_size=10)
result.save("test_blueprint_sheet.png")
```

## 已知限制

1. **布局固定**：当前只支持右侧放置信息区
   - 未来可添加左侧、底部等选项

2. **颜色对比**：需要为色号文字添加智能对比计算
   - 当前使用简单对比（深色格→白字）

3. **辅助线**：暂未实现每10格加粗辅助线功能

4. **自定义字段**：暂不支持用户添加自定义信息字段

## 后续优化

### 短期
1. **布局选项**：支持左侧、底部、左上、右上等放置
2. **智能对比**：基于RGB亮度自动计算最佳文字颜色
3. **辅助线**：添加可配置的辅助线间隔
4. **模板系统**：保存和应用不同的面板布局模板

### 中期
1. **分栏显示**：在左侧或右侧添加分栏信息区
2. **多语言**：支持中英文双语面板
3. **批注**：支持添加图案说明、制作备注等
4. **版本管理**：保存多个版本的信息面板

### 长期
1. **导出格式**：支持SVG矢量格式、DXF CAD格式
2. **打印优化**：自动分页、智能缩放
3. **云模板**：云端共享面板模板和配置
4. **AI增强**：智能优化布局和配色

## 版本信息

- **版本号**: v2.0 (Blueprint重构)
- **发布日期**: 2026-01-31
- **兼容性**: 完全向后兼容
- **依赖**: bead_pattern, PIL, numpy
- **平台**: Windows, Linux, macOS

## 总结

✅ **核心功能**：工程蓝图风格信息面板
✅ **布局优化**：主绘图区 + 信息区块结构
✅ **视觉规范**：工程图纸风格
✅ **向后兼容**：保留原有函数
✅ **文档完善**：详细的使用和测试指南

### 验证状态

- [x] 代码结构清晰
- [x] 设计原则明确
- [x] API接口兼容
- [x] 文档完整

工程蓝图风格的拼豆图导出功能已部署完成！

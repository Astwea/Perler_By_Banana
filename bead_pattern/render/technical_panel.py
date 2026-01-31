"""
工程蓝图（Engineering Blueprint）风格信息面板渲染模块

设计范式：
- 采用"主绘图区 + 信息区块"结构
- 主拼豆网格绘图区占画布主要视觉面积
- 工程属性区（Title Block + BOM）在底部，不与主图视觉竞争

布局结构（重构后）：
┌──────────────────────────────────────┐
│                                      │
│        主拼豆网格（格内有色号）      │
│        ↑ 绝对主体，占最大面积 ↑      │
│                                      │
├──────────────────────────────────────┤
│ ─────────── 分隔线 ───────────────── │
├───────────────────────┬──────────────┤
│ 工程属性区            │ 颜色统计区   │
│ (Title Block)         │ (BOM/Legend) │
└───────────────────────┴──────────────┘

设计原则：
- 工程蓝图风格（Engineering Blueprint）
- 白色背景、工程规范
- 无衬线工程字体
- 高可读性、严格对齐
- 信息区不与主图视觉竞争
- 色号必须清晰可读（不允许缩小字体）
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from typing import Dict, Tuple, Optional, List
from ..core.pattern import BeadPatternV2

# 导入新的 blueprint 模块
from .blueprint import (
    BlueprintConfig,
    PaperSize,
    generate_engineering_blueprint,
)


class TechnicalPanelConfig:
    """
    工程蓝图面板配置（向后兼容层）

    注意：此类保留用于向后兼容。
    推荐使用 BlueprintConfig 类获得更多配置选项。
    """

    def __init__(
        self,
        font_size: int = 12,
        color_block_size: int = 24,
        row_height: int = 32,
        panel_padding: int = 20,
        margin_from_pattern: int = 20,
        background_color: Tuple[int, int, int] = (255, 255, 255),
        text_color: Tuple[int, int, int] = (0, 0, 0),
        border_width: int = 0,
        header_font_size: int = 14
    ):
        """
        初始化配置

        Args:
            font_size: 正文字体大小
            color_block_size: 颜色方块大小
            row_height: 每行高度
            panel_padding: 面板内边距
            margin_from_pattern: 面板与图案的间距
            background_color: 背景颜色
            text_color: 文本颜色
            border_width: 边框宽度（0表示无边框）
            header_font_size: 标题字体大小
        """
        self.font_size = font_size
        self.color_block_size = color_block_size
        self.row_height = row_height
        self.panel_padding = panel_padding
        self.margin_from_pattern = margin_from_pattern
        self.background_color = background_color
        self.text_color = text_color
        self.border_width = border_width
        self.header_font_size = header_font_size

    def to_blueprint_config(self) -> BlueprintConfig:
        """转换为新的 BlueprintConfig"""
        config = BlueprintConfig()
        config.background_color = self.background_color
        config.text_color = self.text_color
        config.bom_font_size_pt = self.font_size
        config.header_font_size_pt = self.header_font_size
        config.info_panel_padding = self.panel_padding
        return config


def get_pattern_v2(pattern):
    """
    获取BeadPatternV2对象（兼容层支持）
    """
    if hasattr(pattern, '_v2'):
        return pattern._v2
    else:
        return pattern


def generate_technical_sheet(
    pattern,
    cell_size: int = 0,
    show_grid: bool = True,
    show_labels: bool = True,
    config: Optional[TechnicalPanelConfig] = None,
    exclude_background: bool = True,
    paper_size: str = "A4",
    dpi: int = 300
) -> Image.Image:
    """
    生成工程蓝图（Engineering Blueprint）风格的拼豆图纸

    布局范式（重构后）：
    - 主网格在上方，占画布主要面积
    - 信息区在下方（Title Block + BOM）
    - 上下布局，不是左右并排

    Args:
        pattern: 拼豆图案对象（BeadPatternV2或BeadPattern兼容层）
        cell_size: 单元格像素大小（0 = 自动计算，推荐）
        show_grid: 是否显示网格
        show_labels: 是否显示色号（工程图纸建议开启）
        config: 面板配置（None则使用默认配置）
        exclude_background: 是否排除背景色
        paper_size: 纸张尺寸 ("A4", "A3", "A2")
        dpi: 打印 DPI

    Returns:
        完整的工程图纸 PIL Image
    """
    # 转换为新配置
    if config is not None:
        blueprint_config = config.to_blueprint_config()
    else:
        blueprint_config = BlueprintConfig()

    # 调用新的工程蓝图生成函数
    return generate_engineering_blueprint(
        pattern=pattern,
        cell_size=cell_size,
        show_grid=show_grid,
        show_labels=show_labels,
        config=blueprint_config,
        exclude_background=exclude_background,
        paper_size=paper_size,
        dpi=dpi
    )


# ========== 以下保留原有的导出统计功能 ==========

def export_statistics(
    pattern,
    file_path: str,
    format: str = "json",
    exclude_background: bool = True
) -> None:
    """
    导出颜色统计数据

    Args:
        pattern: 拼豆图案对象（BeadPatternV2或BeadPattern兼容层）
        file_path: 导出文件路径
        format: 导出格式（'json' 或 'csv'）
        exclude_background: 是否排除背景色
    """
    if format not in ['json', 'csv']:
        raise ValueError(f"不支持的导出格式: {format}")

    # 获取BeadPatternV2对象
    pattern_v2 = get_pattern_v2(pattern)
    stats = pattern_v2.get_color_statistics(exclude_background=exclude_background)
    subject_size = pattern_v2.get_subject_size()

    if format == 'json':
        import json
        import numpy as np

        color_list = []
        for color_id, count in stats['color_counts'].items():
            color_info = pattern_v2.palette.get_color(color_id)
            if color_info:
                color_list.append({
                    'color_id': int(color_id),
                    'display_code': color_info.display_code,
                    'name_zh': color_info.name_zh,
                    'name_en': color_info.name_en,
                    'code': color_info.code,
                    'rgb': list(color_info.rgb),
                    'count': int(count),
                    'brand': color_info.brand,
                    'series': color_info.series
                })

        # 处理dimensions中的numpy类型
        dimensions = None
        if subject_size:
            dimensions = {
                'width': int(subject_size['width']),
                'height': int(subject_size['height']),
                'width_mm': float(subject_size['width_mm']),
                'height_mm': float(subject_size['height_mm'])
            }

        data = {
            'total_beads': int(stats['total_beads'] - (stats.get('background_beads', 0) if exclude_background else 0)),
            'unique_colors': int(stats['unique_colors']),
            'bead_size_mm': float(pattern_v2.bead_size_mm),
            'dimensions': dimensions,
            'colors': color_list
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    elif format == 'csv':
        import csv

        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                '颜色ID', '色号', '中文名称', '英文名称', '品牌', '系列',
                'R', 'G', 'B', '数量'
            ])

            for color_id, count in stats['color_counts'].items():
                color_info = pattern_v2.palette.get_color(color_id)
                if color_info:
                    writer.writerow([
                        color_id,
                        color_info.display_code,
                        color_info.name_zh,
                        color_info.name_en,
                        color_info.brand if color_info.brand else '',
                        color_info.series if color_info.series else '',
                        color_info.rgb[0],
                        color_info.rgb[1],
                        color_info.rgb[2],
                        count
                    ])

            # 添加统计信息
            writer.writerow([])
            writer.writerow(['统计信息'])
            writer.writerow(['总拼豆数', stats['total_beads'] - (stats.get('background_beads', 0) if exclude_background else 0)])
            writer.writerow(['颜色数量', stats['unique_colors']])
            writer.writerow(['拼豆尺寸(mm)', pattern_v2.bead_size_mm])

            if subject_size:
                writer.writerow(['成品宽度(mm)', subject_size['width_mm']])
                writer.writerow(['成品高度(mm)', subject_size['height_mm']])


# ========== 保留旧函数用于向后兼容（但内部使用新实现） ==========

def render_engineering_panel(
    pattern: BeadPatternV2,
    config: TechnicalPanelConfig,
    exclude_background: bool = True,
    show_total_count: bool = True,
    show_dimensions: bool = True,
    show_bead_size: bool = True,
    sort_by_count: bool = True
) -> Image.Image:
    """
    渲染工程属性区（向后兼容）

    注意：此函数保留用于向后兼容。
    新代码推荐使用 generate_technical_sheet() 或 generate_engineering_blueprint()。
    """
    from .blueprint.title_block import render_title_block
    from .blueprint.bom_table import render_bom_table
    from .blueprint.layout import compute_layout
    from .blueprint.config import BlueprintConfig

    pattern_v2 = get_pattern_v2(pattern)
    stats = pattern_v2.get_color_statistics(exclude_background=exclude_background)

    # 计算最长色号
    max_label_chars = 1
    for color_id in stats['color_counts'].keys():
        color_info = pattern_v2.palette.get_color(color_id)
        if color_info:
            max_label_chars = max(max_label_chars, len(color_info.display_code))

    try:
        pattern_width = pattern_v2.grid.width
        pattern_height = pattern_v2.grid.height
    except AttributeError:
        pattern_width = pattern_v2.width
        pattern_height = pattern_v2.height

    blueprint_config = config.to_blueprint_config() if config else BlueprintConfig()
    layout = compute_layout(pattern_width, pattern_height, max_label_chars, blueprint_config)

    # 创建合并的面板图像
    panel_width = layout.info_width
    panel_height = layout.info_height

    panel_img = Image.new('RGB', (panel_width, panel_height), blueprint_config.background_color)

    # 渲染 Title Block
    title_block = render_title_block(
        layout, blueprint_config, stats,
        pattern_width, pattern_height, pattern_v2.bead_size_mm
    )

    # 渲染 BOM
    bom_table = render_bom_table(
        layout, blueprint_config,
        stats['color_counts'],
        pattern_v2.palette,
        sort_by_count=sort_by_count
    )

    # 合成
    panel_img.paste(title_block, (0, 0))
    panel_img.paste(bom_table, (layout.title_width, 0))

    return panel_img


def composite_blueprint_layout(
    main_drawing: Image.Image,
    engineering_panel: Image.Image,
    config: TechnicalPanelConfig
) -> Image.Image:
    """
    合成主绘图区和工程属性区（向后兼容，使用新的上下布局）

    注意：此函数保留用于向后兼容。
    新代码推荐使用 generate_technical_sheet() 或 generate_engineering_blueprint()。
    """
    main_width, main_height = main_drawing.size
    panel_width, panel_height = engineering_panel.size

    # 使用新的上下布局
    margin = config.margin_from_pattern
    separator_gap = 20

    # 计算画布尺寸
    canvas_width = max(main_width, panel_width) + 2 * margin
    canvas_height = margin + main_height + separator_gap + panel_height + margin

    # 创建画布
    canvas = Image.new(
        'RGB',
        (canvas_width, canvas_height),
        config.background_color
    )

    # 主网格居中
    main_x = (canvas_width - main_width) // 2
    main_y = margin
    canvas.paste(main_drawing, (main_x, main_y))

    # 绘制分隔线
    draw = ImageDraw.Draw(canvas)
    separator_y = margin + main_height + separator_gap // 2
    draw.line(
        [(margin, separator_y), (canvas_width - margin, separator_y)],
        fill=(180, 180, 180),
        width=2
    )

    # 信息面板居中
    panel_x = (canvas_width - panel_width) // 2
    panel_y = margin + main_height + separator_gap
    canvas.paste(engineering_panel, (panel_x, panel_y))

    return canvas

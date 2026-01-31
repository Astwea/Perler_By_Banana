"""
BOM（Bill of Materials）表格渲染模块

BOM 是物料清单，用于显示：
- 每种颜色的色号
- 对应的拼豆数量
- 按数量从多到少排序
"""

from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple
from .config import BlueprintConfig
from .layout import BlueprintLayout
from .title_block import load_font


def render_bom_table(
    layout: BlueprintLayout,
    config: BlueprintConfig,
    color_counts: Dict[int, int],
    palette,  # Palette 对象
    sort_by_count: bool = True
) -> Image.Image:
    """
    渲染 BOM（Bill of Materials）表格

    格式紧凑：■ H7 923  ■ M14 917  ■ G2 696 ...

    Args:
        layout: 布局参数
        config: 蓝图配置
        color_counts: 颜色 ID -> 数量 映射
        palette: Palette 对象（获取颜色信息）
        sort_by_count: 是否按数量降序排列

    Returns:
        BOM 表格图像
    """
    # 创建图像
    img = Image.new('RGB', (layout.bom_width, layout.bom_height), config.background_color)
    draw = ImageDraw.Draw(img)

    # 加载字体
    header_font_px = config.pt_to_px(config.header_font_size_pt)
    body_font_px = config.pt_to_px(config.bom_font_size_pt)

    header_font = load_font(header_font_px, bold=True)
    body_font = load_font(body_font_px, bold=False)

    # 布局参数 - 紧凑设计
    padding = config.info_panel_padding
    block_size = int(body_font_px * 1.0)  # 色块大小（紧凑）
    line_height = int(body_font_px * 1.2)  # 行高（紧凑）
    item_gap = int(body_font_px * 0.3)  # 条目之间的间距

    current_y = padding

    # ========== 标题 ==========
    draw.text(
        (padding, current_y),
        "COLOR LEGEND",
        fill=config.text_color,
        font=header_font
    )
    current_y += int(header_font_px * 1.3)

    # 分隔线
    draw.line(
        [(padding, current_y), (layout.bom_width - padding, current_y)],
        fill=config.separator_color,
        width=1
    )
    current_y += padding // 4

    # ========== 排序颜色 ==========
    color_ids = list(color_counts.keys())
    if sort_by_count:
        color_ids.sort(key=lambda x: -color_counts[x])

    # ========== 计算每个条目的实际宽度 ==========
    # 格式：■ CODE COUNT
    max_code_width = 0
    max_count_width = 0
    for color_id in color_ids:
        color_info = palette.get_color(color_id)
        if color_info:
            code_bbox = draw.textbbox((0, 0), color_info.display_code, font=body_font)
            max_code_width = max(max_code_width, code_bbox[2] - code_bbox[0])

            count_text = f"{color_counts[color_id]:,}"
            count_bbox = draw.textbbox((0, 0), count_text, font=body_font)
            max_count_width = max(max_count_width, count_bbox[2] - count_bbox[0])

    # 单个条目宽度：色块 + 间距 + 色号 + 间距 + 数量 + 条目间距
    item_width = block_size + item_gap + max_code_width + item_gap + max_count_width + item_gap * 2

    # ========== 计算列数和行数 ==========
    available_width = layout.bom_width - 2 * padding
    available_height = layout.bom_height - current_y - padding

    # 根据宽度计算可以放多少列
    max_columns = max(1, available_width // item_width)
    max_rows = max(1, available_height // line_height)

    total_colors = len(color_ids)

    # 计算最优列数：尽量少的列，但能装下所有颜色
    columns = min(max_columns, (total_colors + max_rows - 1) // max_rows)
    columns = max(1, columns)
    colors_per_column = (total_colors + columns - 1) // columns

    # 实际使用的列宽（紧凑排列）
    actual_column_width = item_width

    # ========== 绘制颜色列表 ==========
    for idx, color_id in enumerate(color_ids):
        if idx >= colors_per_column * columns:
            break

        col = idx // colors_per_column
        row = idx % colors_per_column

        x_offset = padding + col * actual_column_width
        y_offset = current_y + row * line_height

        # 获取颜色信息
        color_info = palette.get_color(color_id)
        if not color_info:
            continue

        rgb = color_info.rgb
        display_code = color_info.display_code
        count = color_counts[color_id]

        # 绘制色块
        block_x = x_offset
        block_y = y_offset + (line_height - block_size) // 2
        draw.rectangle(
            [(block_x, block_y), (block_x + block_size, block_y + block_size)],
            fill=rgb,
            outline=config.grid_line_color,
            width=1
        )

        # 绘制色号
        code_x = block_x + block_size + item_gap
        draw.text(
            (code_x, y_offset),
            display_code,
            fill=config.text_color,
            font=body_font
        )

        # 绘制数量（紧跟色号后面）
        count_text = f"{count:,}"
        count_x = code_x + max_code_width + item_gap
        draw.text(
            (count_x, y_offset),
            count_text,
            fill=(120, 120, 120),  # 灰色
            font=body_font
        )

    # ========== 边框 ==========
    draw.rectangle(
        [(0, 0), (layout.bom_width - 1, layout.bom_height - 1)],
        outline=config.title_block_border_color,
        width=2
    )

    return img

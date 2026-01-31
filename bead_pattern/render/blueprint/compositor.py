"""
工程蓝图合成模块

核心功能：
- 合成主网格 + Title Block + BOM
- 实现上下布局（主图在上，信息区在下）
- 自动裁剪白色背景区域
- 提供统一的导出入口
"""

from PIL import Image, ImageDraw
from typing import Optional, Tuple
from .config import BlueprintConfig
from .layout import BlueprintLayout, compute_layout
from .title_block import render_title_block
from .bom_table import render_bom_table


def get_pattern_v2(pattern):
    """
    获取 BeadPatternV2 对象（兼容层支持）

    Args:
        pattern: BeadPatternV2 或 BeadPattern 兼容层对象

    Returns:
        BeadPatternV2 对象
    """
    if hasattr(pattern, '_v2'):
        return pattern._v2
    return pattern


def render_cropped_grid(
    pattern_v2,
    bounds: Tuple[int, int, int, int],
    cell_size: int,
    config: BlueprintConfig
) -> Image.Image:
    """
    渲染裁剪后的主网格（只渲染主体区域）

    Args:
        pattern_v2: BeadPatternV2 对象
        bounds: 主体边界 (min_x, min_y, max_x, max_y)
        cell_size: 单元格大小（像素）
        config: 蓝图配置

    Returns:
        裁剪后的主网格图像
    """
    min_x, min_y, max_x, max_y = bounds
    crop_width = max_x - min_x
    crop_height = max_y - min_y

    # 创建裁剪后尺寸的图像
    img_width = crop_width * cell_size
    img_height = crop_height * cell_size

    img = Image.new('RGB', (img_width, img_height), config.background_color)

    # 使用 LUT 快速渲染
    import numpy as np
    lut = pattern_v2.palette.rgb_lut

    # 获取裁剪区域的网格数据
    grid_ids = pattern_v2.grid.grid_ids[min_y:max_y, min_x:max_x]

    # 转换为紧凑索引
    compact_ids = np.zeros_like(grid_ids, dtype=np.int32)
    for color_id, compact_idx in pattern_v2.palette.index_by_id.items():
        compact_ids[grid_ids == color_id] = compact_idx

    # 使用 LUT 渲染
    rgb_grid = lut[compact_ids]

    # 扩展到像素尺寸
    expanded = np.repeat(np.repeat(rgb_grid, cell_size, axis=0), cell_size, axis=1)
    img = Image.fromarray(expanded.astype(np.uint8), mode='RGB')

    return img


def composite_blueprint(
    pattern,
    config: BlueprintConfig
) -> Image.Image:
    """
    合成完整的工程蓝图

    布局结构：
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

    Args:
        pattern: 拼豆图案对象
        config: 蓝图配置

    Returns:
        完整的工程蓝图 PIL Image
    """
    # 获取 V2 对象
    pattern_v2 = get_pattern_v2(pattern)

    # 获取统计信息
    stats = pattern_v2.get_color_statistics(exclude_background=config.exclude_background)

    # 计算最长色号字符数
    max_label_chars = 1
    for color_id in stats['color_counts'].keys():
        color_info = pattern_v2.palette.get_color(color_id)
        if color_info:
            max_label_chars = max(max_label_chars, len(color_info.display_code))

    # 获取原始图案尺寸
    try:
        full_width = pattern_v2.grid.width
        full_height = pattern_v2.grid.height
    except AttributeError:
        full_width = pattern_v2.width
        full_height = pattern_v2.height

    # ========== 裁剪到主体区域 ==========
    bounds = None
    pattern_width = full_width
    pattern_height = full_height
    offset_x = 0
    offset_y = 0

    if config.crop_to_subject and config.exclude_background:
        bounds = pattern_v2.get_subject_bounds()
        if bounds:
            min_x, min_y, max_x, max_y = bounds
            pattern_width = max_x - min_x
            pattern_height = max_y - min_y
            offset_x = min_x
            offset_y = min_y

    # 计算布局（使用裁剪后的尺寸）
    layout = compute_layout(
        pattern_width,
        pattern_height,
        max_label_chars,
        config
    )

    # ========== 1. 创建画布 ==========
    canvas = Image.new('RGB', (layout.canvas_width, layout.canvas_height), config.background_color)
    draw = ImageDraw.Draw(canvas)

    # ========== 2. 渲染主网格 ==========
    from ..raster import render_grid_lines

    if bounds:
        # 渲染裁剪后的网格
        main_grid = render_cropped_grid(pattern_v2, bounds, layout.cell_size, config)
    else:
        # 渲染完整网格
        from ..raster import render_base
        main_grid = render_base(pattern_v2, layout.cell_size)

    # 添加网格线
    if config.show_grid:
        main_grid = render_grid_lines(
            main_grid,
            pattern_width,
            pattern_height,
            layout.cell_size,
            config.grid_line_color
        )

    # 添加辅助网格线（每 10 格加粗）
    if config.show_major_grid:
        main_grid = render_major_grid_lines(
            main_grid,
            pattern_width,
            pattern_height,
            layout.cell_size,
            config.major_grid_interval,
            config.major_grid_color
        )

    # 添加色号标签
    if config.show_labels:
        from ..labels import overlay_labels
        # 使用固定字体大小，不允许缩小
        font_size = config.pt_to_px(config.label_font_size_pt)

        if bounds:
            # 为裁剪后的网格添加标签
            main_grid = overlay_labels_cropped(
                main_grid,
                pattern_v2,
                bounds,
                cell_size=layout.cell_size,
                font_size=font_size,
                stroke_width=max(1, layout.cell_size // 20)
            )
        else:
            main_grid = overlay_labels(
                main_grid,
                pattern_v2,
                cell_size=layout.cell_size,
                font_size=font_size,
                stroke_width=max(1, layout.cell_size // 20)
            )

    # 粘贴主网格到画布
    canvas.paste(main_grid, (layout.grid_x, layout.grid_y))

    # ========== 3. 绘制分隔线 ==========
    separator_padding = 30
    draw.line(
        [(separator_padding, layout.separator_y),
         (layout.canvas_width - separator_padding, layout.separator_y)],
        fill=config.separator_color,
        width=2
    )

    # ========== 4. 渲染 Title Block ==========
    title_block = render_title_block(
        layout,
        config,
        stats,
        pattern_width,
        pattern_height,
        pattern_v2.bead_size_mm
    )
    canvas.paste(title_block, (layout.title_x, layout.title_y))

    # ========== 5. 渲染 BOM Table ==========
    bom_table = render_bom_table(
        layout,
        config,
        stats['color_counts'],
        pattern_v2.palette,
        sort_by_count=True
    )
    canvas.paste(bom_table, (layout.bom_x, layout.bom_y))

    return canvas


def overlay_labels_cropped(
    img: Image.Image,
    pattern_v2,
    bounds: Tuple[int, int, int, int],
    cell_size: int,
    font_size: int,
    stroke_width: int = 1
) -> Image.Image:
    """
    为裁剪后的网格添加标签

    Args:
        img: 基础图像
        pattern_v2: BeadPatternV2 对象
        bounds: 主体边界 (min_x, min_y, max_x, max_y)
        cell_size: 单元格大小
        font_size: 字体大小
        stroke_width: 描边宽度

    Returns:
        添加标签后的图像
    """
    from ..labels import LabelCache, compute_text_color
    from ...core.grid import BeadGrid

    min_x, min_y, max_x, max_y = bounds
    crop_width = max_x - min_x
    crop_height = max_y - min_y

    result_img = img.copy().convert('RGBA')
    cache = LabelCache()

    grid_ids = pattern_v2.grid.grid_ids

    for y in range(crop_height):
        for x in range(crop_width):
            color_id = grid_ids[min_y + y, min_x + x]
            if color_id != BeadGrid.EMPTY:
                color_info = pattern_v2.palette.get_color(color_id)
                if color_info:
                    rgb = color_info.rgb
                    display_code = color_info.display_code
                    text_color = compute_text_color(rgb)

                    label_img = cache.get_label_image(
                        display_code, cell_size, font_size, text_color, stroke_width
                    )

                    paste_x = x * cell_size
                    paste_y = y * cell_size

                    result_img.alpha_composite(label_img, (paste_x, paste_y))

    return result_img.convert('RGB')


def render_major_grid_lines(
    img: Image.Image,
    width: int,
    height: int,
    cell_size: int,
    interval: int,
    color: tuple
) -> Image.Image:
    """
    渲染辅助网格线（每 N 格加粗）

    Args:
        img: 基础图像
        width: 图案宽度（拼豆数）
        height: 图案高度（拼豆数）
        cell_size: 单元格大小（像素）
        interval: 加粗间隔（如 10）
        color: 线条颜色

    Returns:
        添加辅助线后的图像
    """
    result = img.copy()
    draw = ImageDraw.Draw(result)

    img_width = width * cell_size
    img_height = height * cell_size

    # 竖线
    for x in range(0, width + 1, interval):
        x_pos = x * cell_size
        if x_pos <= img_width:
            draw.line([(x_pos, 0), (x_pos, img_height)], fill=color, width=2)

    # 横线
    for y in range(0, height + 1, interval):
        y_pos = y * cell_size
        if y_pos <= img_height:
            draw.line([(0, y_pos), (img_width, y_pos)], fill=color, width=2)

    return result


def generate_engineering_blueprint(
    pattern,
    cell_size: int = 0,
    show_grid: bool = True,
    show_labels: bool = True,
    config: Optional[BlueprintConfig] = None,
    exclude_background: bool = True,
    paper_size: str = "A4",
    dpi: int = 300,
    crop_to_subject: bool = True
) -> Image.Image:
    """
    生成工程蓝图风格的拼豆图纸（公共入口）

    这是主要的公共 API，用于生成完整的工程蓝图。

    Args:
        pattern: 拼豆图案对象（BeadPatternV2 或 BeadPattern 兼容层）
        cell_size: 单元格像素大小（0 = 自动计算，推荐）
        show_grid: 是否显示网格
        show_labels: 是否显示色号标签
        config: 蓝图配置（可选，None 则使用默认配置）
        exclude_background: 是否排除背景色
        paper_size: 纸张尺寸 ("A4", "A3", "A2")
        dpi: 打印 DPI
        crop_to_subject: 是否裁剪到主体区域（去掉白色背景）

    Returns:
        完整的工程图纸 PIL Image
    """
    from .config import PaperSize

    if config is None:
        config = BlueprintConfig()

    # 更新配置
    config.show_grid = show_grid
    config.show_labels = show_labels
    config.exclude_background = exclude_background
    config.crop_to_subject = crop_to_subject
    config.dpi = dpi

    # 设置纸张尺寸
    paper_map = {
        "A4": PaperSize.A4,
        "A3": PaperSize.A3,
        "A2": PaperSize.A2,
        "LETTER": PaperSize.LETTER,
    }
    config.paper_size = paper_map.get(paper_size.upper(), PaperSize.A4)

    # 如果指定了 cell_size，覆盖自动计算
    if cell_size > 0:
        config.cell_size = cell_size
    else:
        config.cell_size = 0  # 自动计算

    return composite_blueprint(pattern, config)

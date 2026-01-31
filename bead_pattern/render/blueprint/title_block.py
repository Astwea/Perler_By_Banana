"""
工程图纸 Title Block 渲染模块

Title Block 是工程图纸右下角的信息区块，包含：
- 图案尺寸信息
- 实际物理尺寸
- 拼豆总数
- 拼豆规格
- 日期
"""

from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Optional
from datetime import date
from .config import BlueprintConfig
from .layout import BlueprintLayout


def load_font(size_px: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """
    加载字体（跨平台支持）

    Args:
        size_px: 字体大小（像素）
        bold: 是否粗体

    Returns:
        ImageFont 对象
    """
    font_paths = [
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        # Windows
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
    ]

    for path in font_paths:
        try:
            return ImageFont.truetype(path, size_px)
        except (OSError, IOError):
            continue

    return ImageFont.load_default()


def render_title_block(
    layout: BlueprintLayout,
    config: BlueprintConfig,
    pattern_stats: Dict,
    pattern_width: int,
    pattern_height: int,
    bead_size_mm: float
) -> Image.Image:
    """
    渲染工程图纸 Title Block

    格式（工程图纸标准）：
    ┌─────────────────────────────┐
    │ PERLER BEAD PATTERN         │
    ├─────────────────────────────┤
    │ Grid size    │ 50 x 40      │
    │ Physical     │ 130 x 104 mm │
    │ Total beads  │ 2000         │
    │ Bead size    │ 2.6 mm       │
    │ Date         │ 2026-02-01   │
    └─────────────────────────────┘

    Args:
        layout: 布局参数
        config: 蓝图配置
        pattern_stats: 颜色统计信息
        pattern_width: 图案宽度（拼豆数）
        pattern_height: 图案高度（拼豆数）
        bead_size_mm: 拼豆尺寸（毫米）

    Returns:
        Title Block 图像
    """
    # 创建图像
    img = Image.new('RGB', (layout.title_width, layout.title_height), config.background_color)
    draw = ImageDraw.Draw(img)

    # 加载字体
    header_font_px = config.pt_to_px(config.header_font_size_pt)
    body_font_px = config.pt_to_px(config.bom_font_size_pt)

    header_font = load_font(header_font_px, bold=True)
    body_font = load_font(body_font_px, bold=False)

    # 布局参数 - 紧凑设计
    padding = config.info_panel_padding
    line_height = int(body_font_px * 1.3)  # 更紧凑

    current_y = padding

    # ========== 标题 ==========
    draw.text(
        (padding, current_y),
        "PATTERN INFO",
        fill=config.text_color,
        font=header_font
    )
    current_y += int(header_font_px * 1.4)  # 更紧凑

    # 分隔线
    draw.line(
        [(padding, current_y), (layout.title_width - padding, current_y)],
        fill=config.separator_color,
        width=1
    )
    current_y += padding // 3  # 更紧凑

    # ========== 属性列表 ==========
    # 计算物理尺寸
    physical_w = pattern_width * bead_size_mm
    physical_h = pattern_height * bead_size_mm

    # 计算有效拼豆数（排除背景）
    total_beads = pattern_stats.get('total_beads', 0)
    background_beads = pattern_stats.get('background_beads', 0) if config.exclude_background else 0
    effective_beads = total_beads - background_beads

    # 属性数据
    properties = [
        ("Grid size", f"{pattern_width} x {pattern_height} beads"),
    ]

    if config.show_physical_size:
        properties.append(("Physical size", f"{physical_w:.1f} x {physical_h:.1f} mm"))

    properties.append(("Total beads", f"{effective_beads:,}"))

    if config.show_bead_size:
        properties.append(("Bead size", f"{bead_size_mm} mm"))

    if config.show_date:
        properties.append(("Date", date.today().isoformat()))

    # 绘制属性
    label_width = int(layout.title_width * 0.45)

    for label, value in properties:
        # 标签（左对齐）
        draw.text(
            (padding, current_y),
            label,
            fill=config.text_color,
            font=body_font
        )
        # 值（右侧）
        draw.text(
            (label_width, current_y),
            value,
            fill=config.text_color,
            font=body_font
        )
        current_y += line_height

    # ========== 边框 ==========
    draw.rectangle(
        [(0, 0), (layout.title_width - 1, layout.title_height - 1)],
        outline=config.title_block_border_color,
        width=2
    )

    return img

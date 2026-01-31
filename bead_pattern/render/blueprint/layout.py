"""
工程蓝图布局计算模块

核心功能：
- 自适应 cell_size 计算（确保色号可读）
- 完整布局参数计算（主网格区、信息区位置和尺寸）
"""

from dataclasses import dataclass
from typing import Tuple, Optional
from .config import BlueprintConfig, PaperSize


@dataclass
class BlueprintLayout:
    """
    计算后的布局参数

    所有尺寸单位：像素（@ config.dpi）
    """

    # ========== 画布尺寸 ==========
    canvas_width: int
    canvas_height: int

    # ========== 主网格区域 ==========
    grid_x: int          # 主网格左上角 X
    grid_y: int          # 主网格左上角 Y
    grid_width: int      # 主网格像素宽度
    grid_height: int     # 主网格像素高度
    cell_size: int       # 单元格像素大小

    # ========== 信息区域（底部） ==========
    info_x: int          # 信息区左上角 X
    info_y: int          # 信息区左上角 Y
    info_width: int      # 信息区总宽度
    info_height: int     # 信息区总高度

    # ========== Title Block 区域 ==========
    title_x: int
    title_y: int
    title_width: int
    title_height: int

    # ========== BOM 区域 ==========
    bom_x: int
    bom_y: int
    bom_width: int
    bom_height: int

    # ========== 分隔线位置 ==========
    separator_y: int     # 主网格与信息区分隔线 Y 坐标


def compute_adaptive_cell_size(
    pattern_width: int,
    pattern_height: int,
    max_label_chars: int,
    config: BlueprintConfig
) -> int:
    """
    计算满足可读性要求的自适应 cell_size

    约束条件（按优先级）：
    1. 色号文字必须清晰可读（最小 8pt @ dpi）
    2. 主网格不得超出打印区域
    3. 优先保证可读性，不缩小字体

    Args:
        pattern_width: 图案宽度（拼豆数）
        pattern_height: 图案高度（拼豆数）
        max_label_chars: 最长色号字符数（如 "F13" = 3）
        config: 蓝图配置

    Returns:
        cell_size（像素），满足所有约束的最优值
    """
    # 纸张尺寸
    paper_w_mm, paper_h_mm = config.get_paper_size_mm()
    mm_to_px = config.dpi / 25.4
    margin_px = config.get_margin_px()
    info_height_px = config.get_info_panel_height_px()

    # 可用绘图区域（像素）
    draw_w_px = int(paper_w_mm * mm_to_px) - 2 * margin_px
    draw_h_px = int(paper_h_mm * mm_to_px) - 2 * margin_px - info_height_px - 20  # 20px 分隔

    # 1. 计算可读性要求的最小 cell_size
    # 最小字体要求 (pt -> px @ dpi)
    min_font_px = config.pt_to_px(config.label_font_size_pt)

    # 字符宽度估算（无衬线字体约 0.6-0.7em）
    char_width_px = min_font_px * 0.65
    min_text_width_px = max_label_chars * char_width_px

    # cell_size 必须容纳文字（文字占格子的 80%）
    min_cell_for_text = int(min_text_width_px / 0.8)
    min_cell_for_text = max(min_cell_for_text, config.min_cell_size)

    # 2. 计算纸张限制的最大 cell_size
    if pattern_width > 0 and pattern_height > 0:
        max_cell_w = draw_w_px // pattern_width
        max_cell_h = draw_h_px // pattern_height
        max_cell_for_paper = min(max_cell_w, max_cell_h)
    else:
        max_cell_for_paper = config.max_cell_size

    # 3. 确定最终 cell_size
    if max_cell_for_paper < min_cell_for_text:
        # 纸张放不下：使用最小可读尺寸，可能需要裁剪或选择更大纸张
        # 这里选择保证可读性，即使超出纸张
        cell_size = min_cell_for_text
    else:
        # 在可读范围内，取纸张允许的最大值（但不超过 max_cell_size）
        cell_size = min(max_cell_for_paper, config.max_cell_size)

    return cell_size


def compute_layout(
    pattern_width: int,
    pattern_height: int,
    max_label_chars: int,
    config: BlueprintConfig
) -> BlueprintLayout:
    """
    计算完整的蓝图布局

    布局结构：
    ┌──────────────────────────────────────┐
    │  margin                              │
    │  ┌──────────────────────────────┐   │
    │  │                              │   │
    │  │      主拼豆网格（居中）      │   │
    │  │                              │   │
    │  └──────────────────────────────┘   │
    │  ─────────── 分隔线 ───────────────  │
    │  ┌───────────────┬──────────────┐   │
    │  │  Title Block  │     BOM      │   │
    │  └───────────────┴──────────────┘   │
    │  margin                              │
    └──────────────────────────────────────┘

    Args:
        pattern_width: 图案宽度（拼豆数）
        pattern_height: 图案高度（拼豆数）
        max_label_chars: 最长色号字符数
        config: 蓝图配置

    Returns:
        BlueprintLayout 布局参数
    """
    # 1. 计算 cell_size
    if config.cell_size > 0:
        cell_size = config.cell_size
    else:
        cell_size = compute_adaptive_cell_size(
            pattern_width, pattern_height, max_label_chars, config
        )

    # 2. 计算各区域尺寸
    margin_px = config.get_margin_px()
    info_height_px = config.get_info_panel_height_px()
    separator_gap = 20  # 分隔间距（像素）

    # 主网格实际尺寸
    grid_width = pattern_width * cell_size
    grid_height = pattern_height * cell_size

    # 信息区宽度（与主网格同宽，但有最小宽度）
    info_width = max(grid_width, 600)  # 最小 600px 确保信息区可读

    # 画布尺寸
    canvas_width = max(grid_width, info_width) + 2 * margin_px
    canvas_height = margin_px + grid_height + separator_gap + info_height_px + margin_px

    # 3. 计算主网格位置（居中）
    grid_x = (canvas_width - grid_width) // 2
    grid_y = margin_px

    # 4. 计算信息区位置
    info_y = margin_px + grid_height + separator_gap
    info_x = (canvas_width - info_width) // 2

    # 分隔线位置
    separator_y = margin_px + grid_height + separator_gap // 2

    # 5. 计算 Title Block 和 BOM 区域
    title_width = int(info_width * config.title_block_width_ratio)
    bom_width = info_width - title_width

    title_x = info_x
    title_y = info_y
    title_height = info_height_px

    bom_x = info_x + title_width
    bom_y = info_y
    bom_height = info_height_px

    return BlueprintLayout(
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        grid_x=grid_x,
        grid_y=grid_y,
        grid_width=grid_width,
        grid_height=grid_height,
        cell_size=cell_size,
        info_x=info_x,
        info_y=info_y,
        info_width=info_width,
        info_height=info_height_px,
        title_x=title_x,
        title_y=title_y,
        title_width=title_width,
        title_height=title_height,
        bom_x=bom_x,
        bom_y=bom_y,
        bom_width=bom_width,
        bom_height=bom_height,
        separator_y=separator_y,
    )


def check_pattern_fits_paper(
    pattern_width: int,
    pattern_height: int,
    config: BlueprintConfig
) -> Tuple[bool, Optional[PaperSize]]:
    """
    检查图案是否能在当前纸张上可读地显示

    Returns:
        (fits, suggested_paper):
        - fits: 是否能放下
        - suggested_paper: 如果放不下，建议的更大纸张尺寸
    """
    layout = compute_layout(pattern_width, pattern_height, 4, config)  # 假设最长 4 字符

    # 检查主网格是否超出画布（考虑边距）
    paper_w_px, paper_h_px = config.get_paper_size_px()

    if layout.grid_width + 2 * config.get_margin_px() > paper_w_px:
        fits = False
    elif layout.canvas_height > paper_h_px:
        fits = False
    else:
        fits = True

    if not fits:
        # 建议更大的纸张
        paper_order = [PaperSize.A4, PaperSize.A3, PaperSize.A2]
        current_idx = paper_order.index(config.paper_size) if config.paper_size in paper_order else 0
        if current_idx < len(paper_order) - 1:
            return (False, paper_order[current_idx + 1])
        return (False, None)  # 已经是最大纸张

    return (True, None)

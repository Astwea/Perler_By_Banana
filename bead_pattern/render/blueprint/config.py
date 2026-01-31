"""
工程蓝图配置类

定义纸张尺寸、视觉风格、布局参数等配置选项
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum


class PaperSize(Enum):
    """纸张尺寸枚举（宽 x 高，毫米）"""
    A4 = (210, 297)
    A3 = (297, 420)
    A2 = (420, 594)
    LETTER = (216, 279)
    CUSTOM = (0, 0)


# RGB 类型别名
RGB = Tuple[int, int, int]


@dataclass
class BlueprintConfig:
    """
    工程蓝图配置

    设计原则：
    - 主网格优先：确保色号清晰可读
    - 工程图纸风格：纯白背景、无衬线字体、中性灰线条
    - 打印适配：支持 A4/A3 尺寸，300 DPI
    """

    # ========== 纸张设置 ==========
    paper_size: PaperSize = PaperSize.A4
    custom_paper_mm: Tuple[int, int] = (210, 297)  # 自定义纸张尺寸（宽, 高）
    margin_mm: int = 10  # 页边距（毫米）
    dpi: int = 300  # 打印 DPI

    # ========== 主网格设置 ==========
    # cell_size = 0 表示自动计算
    cell_size: int = 0
    min_cell_size: int = 25  # 最小格子尺寸（像素 @ dpi）确保可读
    max_cell_size: int = 60  # 最大格子尺寸（避免过大）

    # ========== 字体设置（不允许缩小） ==========
    label_font_size_pt: int = 8   # 主网格内色号字体（最小 8pt）
    title_font_size_pt: int = 12  # 标题字体
    bom_font_size_pt: int = 10    # BOM 表格字体
    header_font_size_pt: int = 14  # 大标题字体

    # ========== 视觉风格 ==========
    background_color: RGB = (255, 255, 255)    # 纯白背景
    grid_line_color: RGB = (200, 200, 200)     # 网格线颜色（中性灰）
    text_color: RGB = (0, 0, 0)                # 文本颜色（纯黑）
    separator_color: RGB = (180, 180, 180)     # 分隔线颜色
    title_block_border_color: RGB = (100, 100, 100)  # Title Block 边框

    # ========== 信息区设置 ==========
    info_panel_height_mm: int = 35  # 底部信息区高度（毫米）- 紧凑布局
    title_block_width_ratio: float = 0.25  # Title Block 占底部宽度比例
    info_panel_padding: int = 10  # 信息区内边距（像素）

    # ========== 内容选项 ==========
    show_labels: bool = True       # 主网格内显示色号
    show_grid: bool = True         # 显示网格线
    exclude_background: bool = True  # 排除背景色统计
    crop_to_subject: bool = True   # 自动裁剪到主体区域，去掉白色背景
    show_date: bool = True         # 显示日期
    show_physical_size: bool = True  # 显示实际尺寸（mm）
    show_bead_size: bool = True    # 显示拼豆尺寸

    # ========== 辅助网格线 ==========
    show_major_grid: bool = True   # 每 10 格加粗辅助线
    major_grid_interval: int = 10  # 辅助线间隔
    major_grid_color: RGB = (150, 150, 150)  # 辅助线颜色

    def get_paper_size_mm(self) -> Tuple[int, int]:
        """获取纸张尺寸（毫米）"""
        if self.paper_size == PaperSize.CUSTOM:
            return self.custom_paper_mm
        return self.paper_size.value

    def get_paper_size_px(self) -> Tuple[int, int]:
        """获取纸张尺寸（像素 @ dpi）"""
        w_mm, h_mm = self.get_paper_size_mm()
        mm_to_px = self.dpi / 25.4
        return (int(w_mm * mm_to_px), int(h_mm * mm_to_px))

    def get_margin_px(self) -> int:
        """获取页边距（像素）"""
        return int(self.margin_mm * self.dpi / 25.4)

    def get_info_panel_height_px(self) -> int:
        """获取信息区高度（像素）"""
        return int(self.info_panel_height_mm * self.dpi / 25.4)

    def pt_to_px(self, pt: int) -> int:
        """点数转像素"""
        return int(pt / 72 * self.dpi)


def create_default_config() -> BlueprintConfig:
    """创建默认配置"""
    return BlueprintConfig()


def create_a4_print_config() -> BlueprintConfig:
    """创建 A4 打印配置"""
    return BlueprintConfig(
        paper_size=PaperSize.A4,
        dpi=300,
        margin_mm=10,
        show_labels=True,
        show_grid=True,
    )


def create_a3_print_config() -> BlueprintConfig:
    """创建 A3 打印配置（大图案）"""
    return BlueprintConfig(
        paper_size=PaperSize.A3,
        dpi=300,
        margin_mm=15,
        show_labels=True,
        show_grid=True,
        info_panel_height_mm=60,
    )

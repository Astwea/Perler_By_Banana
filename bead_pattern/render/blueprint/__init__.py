"""
工程蓝图（Engineering Blueprint）渲染子模块

设计范式：
- 主拼豆网格在上方，占画布主要面积
- 工程信息区在下方（Title Block + BOM）
- 工程图纸风格：纯白背景、无衬线字体、中性灰线条

布局结构：
┌──────────────────────────────────────┐
│                                      │
│        主拼豆网格（格内有色号）      │
│        ↑ 绝对主体，占最大面积 ↑      │
│                                      │
├───────────────────────┬──────────────┤
│ 工程属性区            │ 颜色统计区   │
│ (Title Block)         │ (BOM/Legend) │
└───────────────────────┴──────────────┘
"""

from .config import BlueprintConfig, PaperSize
from .layout import BlueprintLayout, compute_layout, compute_adaptive_cell_size
from .title_block import render_title_block
from .bom_table import render_bom_table
from .compositor import composite_blueprint, generate_engineering_blueprint

__all__ = [
    'BlueprintConfig',
    'PaperSize',
    'BlueprintLayout',
    'compute_layout',
    'compute_adaptive_cell_size',
    'render_title_block',
    'render_bom_table',
    'composite_blueprint',
    'generate_engineering_blueprint',
]

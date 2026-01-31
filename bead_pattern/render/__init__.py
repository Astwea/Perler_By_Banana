"""
渲染引擎模块

包含：
- raster: 基础光栅化渲染
- labels: 色号标签覆盖
- legend: 图例渲染
- blueprint: 工程蓝图渲染（新增）
- technical_panel: 工程蓝图入口（保持向后兼容）
"""

from .raster import render_base, render_grid_lines
from .labels import LabelCache, overlay_labels
from .legend import render_legend

# 导入工程蓝图模块
from .blueprint import (
    BlueprintConfig,
    PaperSize,
    BlueprintLayout,
    compute_layout,
    compute_adaptive_cell_size,
    render_title_block,
    render_bom_table,
    composite_blueprint,
    generate_engineering_blueprint,
)

# 保持向后兼容的导入
from .technical_panel import (
    TechnicalPanelConfig,
    generate_technical_sheet,
    export_statistics,
)

__all__ = [
    # 基础渲染
    'render_base',
    'render_grid_lines',
    'LabelCache',
    'overlay_labels',
    'render_legend',
    # 工程蓝图（新）
    'BlueprintConfig',
    'PaperSize',
    'BlueprintLayout',
    'compute_layout',
    'compute_adaptive_cell_size',
    'render_title_block',
    'render_bom_table',
    'composite_blueprint',
    'generate_engineering_blueprint',
    # 向后兼容
    'TechnicalPanelConfig',
    'generate_technical_sheet',
    'export_statistics',
]

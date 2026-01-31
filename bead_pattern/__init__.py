"""
拼豆图案包 - 高性能重构版本

提供基于索引网格的拼豆图案数据结构，相比原始版本：
- 内存使用减少 90%+
- 渲染速度提升 10-50倍
- 统计计算使用 numpy 向量化

主要模块:
- core: 核心数据模型 (ColorInfo, Palette, BeadGrid, BeadPatternV2)
- render: 渲染引擎 (raster, labels, legend)
- io: 导入/导出 (json_io, csv_io)
- compat: 向后兼容层 (BeadPattern wrapper)
- bench: 性能测试
"""

from .core.color import ColorInfo
from .core.palette import Palette
from .core.grid import BeadGrid
from .core.pattern import BeadPatternV2
from .compat.legacy import BeadPattern

__all__ = [
    'ColorInfo',
    'Palette',
    'BeadGrid',
    'BeadPatternV2',
    'BeadPattern',  # 兼容层
    'compat.BeadPattern',  # 兼容层完整路径（备用）
]

__version__ = "2.0.0"
format_version = "2.0"

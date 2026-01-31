import numpy as np
from PIL import Image, ImageDraw
from typing import Tuple
from ..core.pattern import BeadPatternV2


def render_base(pattern: BeadPatternV2, cell_size: int) -> Image.Image:
    """
    快速基础渲染 - 使用LUT查找+Image.fromarray
    
    性能优化：
    - 不使用逐格绘制循环
    - 构建索引数组后一次性查找RGB
    - 使用Image.fromarray批量转换
    
    Args:
        pattern: BeadPatternV2对象
        cell_size: 每个拼豆的像素大小
    
    Returns:
        PIL Image对象（RGB模式）
    """
    height, width = pattern.grid.shape
    
    grid_ids = pattern.grid.grid_ids
    
    idx_grid = np.zeros((height, width), dtype=np.int32)
    lut = pattern.palette.rgb_lut
    
    for color_id, compact_idx in pattern.palette.index_by_id.items():
        idx_grid[grid_ids == color_id] = compact_idx
    
    rgb = lut[idx_grid]
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    
    small_img = Image.fromarray(rgb, 'RGB')
    final_img = small_img.resize((width * cell_size, height * cell_size), Image.NEAREST)
    
    return final_img


def render_grid_lines(img: Image.Image, width: int, height: int, 
                  cell_size: int, grid_color: Tuple[int, int, int] = (200, 200, 200)) -> Image.Image:
    """
    渲染网格线（批量绘制）
    
    Args:
        img: 基础图像
        width: 网格宽度（拼豆数）
        height: 网格高度（拼豆数）
        cell_size: 每个拼豆像素大小
        grid_color: 网格线颜色
    
    Returns:
        添加网格线后的图像
    """
    draw = ImageDraw.Draw(img)
    
    for x in range(width + 1):
        x_pos = x * cell_size
        draw.line([(x_pos, 0), (x_pos, height * cell_size)], fill=grid_color, width=1)
    
    for y in range(height + 1):
        y_pos = y * cell_size
        draw.line([(0, y_pos), (width * cell_size, y_pos)], fill=grid_color, width=1)
    
    return img

import json
from typing import Optional, List
from ..core.pattern import BeadPatternV2


def to_json(pattern: BeadPatternV2, file_path: str, format_version: str = "2.0") -> None:
    """
    导出为新JSON格式（palette + grid）
    
    新格式结构：
    - format_version: 版本标识
    - width, height, bead_size_mm: 元数据
    - palette: 颜色列表
    - grid_ids: 2D数组（颜色ID）
    - statistics: 缓存的统计信息
    
    Args:
        pattern: BeadPatternV2对象
        file_path: 输出文件路径
        format_version: 格式版本
    """
    data = {
        'format_version': format_version,
        'width': pattern.width,
        'height': pattern.height,
        'bead_size_mm': pattern.bead_size_mm,
        'palette': [],
        'grid_ids': pattern.grid.grid_ids.tolist(),
        'statistics': pattern.get_color_statistics()
    }
    
    for color_id, color_info in pattern.palette.colors_by_id.items():
        data['palette'].append({
            'id': color_info.id,
            'code': color_info.code,
            'name_zh': color_info.name_zh,
            'name_en': color_info.name_en,
            'rgb': list(color_info.rgb),
            'brand': color_info.brand,
            'series': color_info.series
        })
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def from_json(file_path: str) -> BeadPatternV2:
    """
    从JSON文件加载图案
    
    Args:
        file_path: JSON文件路径
    
    Returns:
        BeadPatternV2对象
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    version = data.get('format_version', '1.0')
    
    if version == '1.0':
        from ..compat.legacy import BeadPattern
        old_pattern = BeadPattern(
            data['width'],
            data['height'],
            data.get('bead_size_mm', 2.6)
        )
        
        import numpy as np
        matched_colors = np.full((old_pattern.height, old_pattern.width), None, dtype=object)
        
        for y, row in enumerate(data['pattern']):
            for x, cell in enumerate(row):
                if cell.get('color_id') is not None:
                    matched_colors[y, x] = {
                        'id': cell['color_id'],
                        'name_zh': cell.get('color_name_zh', ''),
                        'name_en': cell.get('color_name_en', ''),
                        'code': cell.get('color_code', ''),
                        'rgb': cell.get('rgb', [0, 0, 0])
                    }
        
        old_pattern.from_matched_colors(matched_colors)
        
        new_pattern = BeadPatternV2(
            old_pattern.width,
            old_pattern.height,
            old_pattern.bead_size_mm
        )
        new_pattern.from_matched_colors(matched_colors)
        
        return new_pattern
    else:
        from ..core.pattern import BeadPatternV2
        from ..core.palette import Palette
        
        new_pattern = BeadPatternV2(
            data['width'],
            data['height'],
            data.get('bead_size_mm', 2.6)
        )
        
        new_pattern.grid.grid_ids = np.array(data['grid_ids'], dtype=np.int32)
        
        for color_data in data.get('palette', []):
            new_pattern.palette.upsert_from_dict(color_data)
        
        return new_pattern


def to_legacy_json(pattern: BeadPatternV2, file_path: str) -> None:
    """
    导出为旧版JSON格式（兼容旧代码）
    
    Args:
        pattern: BeadPatternV2对象
        file_path: 输出文件路径
    """
    from ..compat.legacy import BeadPattern
    old_pattern = BeadPattern(pattern.width, pattern.height, pattern.bead_size_mm)
    
    height, width = pattern.grid.shape
    matched_colors = np.full((height, width), None, dtype=object)
    
    for y in range(height):
        for x in range(width):
            color_id = pattern.grid.get_id(x, y)
            if color_id != -1:
                color_info = pattern.palette.get_color(color_id)
                if color_info:
                    matched_colors[y, x] = {
                        'id': color_info.id,
                        'name_zh': color_info.name_zh,
                        'name_en': color_info.name_en,
                        'code': color_info.code,
                        'rgb': list(color_info.rgb),
                        'brand': color_info.brand,
                        'series': color_info.series
                    }
    
    old_pattern.from_matched_colors(matched_colors)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(old_pattern.to_dict(), f, ensure_ascii=False, indent=2)

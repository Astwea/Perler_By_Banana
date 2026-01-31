import numpy as np
from typing import Dict, Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont
from ..core.pattern import BeadPatternV2
from ..core.color import ColorInfo
from ..core.grid import BeadGrid
from ..render.raster import render_base, render_grid_lines
from ..render.labels import overlay_labels


class BeadPattern:
    """
    向后兼容包装器 - 保持与旧API的兼容性

    内部使用 BeadPatternV2 实现，提供与旧版本相同的公共接口
    现有调用代码无需修改即可获得性能提升

    Args:
        bead_size_mm: 单个拼豆尺寸（毫米）
    """
    
    def __init__(self, width: int, height: int, bead_size_mm: float = 2.6):
        self._v2 = BeadPatternV2(width, height, bead_size_mm)
        self.width = width
        self.height = height
        self.bead_size_mm = bead_size_mm
        self.actual_width_mm = self._v2.actual_width_mm
        self.actual_height_mm = self._v2.actual_height_mm
    
    def set_bead(self, x: int, y: int, color_info: Dict) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            color_id = color_info.get('id')
            if color_id is not None:
                self._v2.palette.upsert_from_dict(color_info)
                self._v2.grid.set_id(x, y, color_id)
    
    def get_bead(self, x: int, y: int) -> Optional[Dict]:
        if 0 <= x < self.width and 0 <= y < self.height:
            color_id = self._v2.grid.get_id(x, y)
            if color_id != BeadGrid.EMPTY:
                color_info = self._v2.palette.get_color(color_id)
                if color_info:
                    return {
                        'id': color_info.id,
                        'name_zh': color_info.name_zh,
                        'name_en': color_info.name_en,
                        'code': color_info.code,
                        'rgb': list(color_info.rgb),
                        'brand': color_info.brand,
                        'series': color_info.series
                    }
        return None
    
    def from_matched_colors(self, matched_colors: np.ndarray) -> None:
        """
        从匹配的颜色数组生成图案（高性能版本）
        
        优化：批量处理颜色和网格设置，避免重复调用
        
        Args:
            matched_colors: 匹配的颜色数组 (H, W)，
                          每个元素为None或颜色字典
        """
        height, width = matched_colors.shape[:2]

        if width != self.width or height != self.height:
            self._v2.grid.resize(width, height)
            self.actual_width_mm = width * self.bead_size_mm
            self.actual_height_mm = height * self.bead_size_mm
        
        # 批量收集所有唯一颜色
        unique_colors = {}
        flat = matched_colors.flatten()
        
        for cell in flat:
            if cell is not None:
                color_id = cell.get('id')
                if color_id is not None:
                    if color_id not in self._v2.palette.colors_by_id:
                        unique_colors[color_id] = cell
        
        # 批量插入所有颜色
        for color_data in unique_colors.values():
            self._v2.palette.upsert_from_dict(color_data)

        _ = self._v2.palette.rgb_lut

        # 重建grid_ids - 逐个处理单元格
        grid_ids = np.full((height, width), BeadGrid.EMPTY, dtype=np.int32)

        for y in range(height):
            for x in range(width):
                cell = matched_colors[y, x]
                if cell is not None:
                    color_id = cell.get('id')
                    if color_id is not None and color_id in self._v2.palette.colors_by_id:
                        grid_ids[y, x] = color_id

        self._v2.grid.grid_ids = grid_ids
    
    def get_subject_bounds(self, background_colors: Optional[List] = None) -> Optional[Tuple[int, int, int, int]]:
        return self._v2.get_subject_bounds(background_colors)
    
    def get_subject_size(self, background_colors: Optional[List] = None) -> Optional[Dict]:
        return self._v2.get_subject_size(background_colors)
    
    def get_color_statistics(self, exclude_background: bool = False, 
                         background_colors: Optional[List] = None) -> Dict:
        return self._v2.get_color_statistics(exclude_background, background_colors)
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式（保持旧格式）
        
        Returns:
            与旧版本兼容的字典格式
        """
        pattern_list = []
        height, width = self._v2.grid.shape
        
        for y in range(height):
            row = []
            for x in range(width):
                color_id = self._v2.grid.get_id(x, y)
                if color_id != BeadGrid.EMPTY:
                    color_info = self._v2.palette.get_color(color_id)
                    if color_info:
                        row.append({
                            'x': x,
                            'y': y,
                            'color_id': color_info.id,
                            'color_code': color_info.code,
                            'color_name_zh': color_info.name_zh,
                            'color_name_en': color_info.name_en,
                            'rgb': list(color_info.rgb)
                        })
                    else:
                        row.append({
                            'x': x,
                            'y': y,
                            'color_id': None
                        })
                else:
                    row.append({
                        'x': x,
                        'y': y,
                        'color_id': None
                    })
            pattern_list.append(row)
        
        return {
            'width': self.width,
            'height': self.height,
            'bead_size_mm': self.bead_size_mm,
            'actual_width_mm': self.actual_width_mm,
            'actual_height_mm': self.actual_height_mm,
            'pattern': pattern_list,
            'statistics': self.get_color_statistics()
        }
    
    def to_json(self, file_path: str) -> None:
        import json
        data = self.to_dict()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def to_csv(self, file_path: str) -> None:
        import csv
        height, width = self._v2.grid.shape
        
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['行(Y)', '列(X)', '颜色ID', '色号代码', '颜色名称', 'RGB'])
            
            for y in range(height):
                for x in range(width):
                    color_id = self._v2.grid.get_id(x, y)
                    if color_id != BeadGrid.EMPTY:
                        color_info = self._v2.palette.get_color(color_id)
                        if color_info:
                            writer.writerow([
                                y, x,
                                color_info.id,
                                color_info.code,
                                color_info.name_zh,
                                f"{color_info.rgb[0]},{color_info.rgb[1]},{color_info.rgb[2]}"
                            ])
                    else:
                        writer.writerow([y, x, None, '', '', ''])
    
    def to_image(self, cell_size: int = 20, show_labels: bool = True,
                 show_grid: bool = True, grid_color: Tuple[int, int, int] = (200, 200, 200)) -> Image.Image:
        img = render_base(self._v2, cell_size)
        
        if show_grid:
            img = render_grid_lines(img, width=self.width, height=self.height, 
                               cell_size=cell_size, grid_color=grid_color)
        
        if show_labels:
            img = overlay_labels(img, self._v2, cell_size=cell_size)
        
        return img
    
    def save_image(self, file_path: str, cell_size: int = 20,
                   show_labels: bool = True, show_grid: bool = True) -> None:
        img = self.to_image(cell_size, show_labels, show_grid)
        img.save(file_path, compress_level=1)

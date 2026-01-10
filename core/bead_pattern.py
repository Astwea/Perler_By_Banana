"""
拼豆图案生成模块
负责生成拼豆图案数据结构、标记色号和导出功能
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
import json
from PIL import Image, ImageDraw, ImageFont
import os


class BeadPattern:
    """拼豆图案类"""
    
    def __init__(self, width: int, height: int, bead_size_mm: float = 2.6):
        """
        初始化拼豆图案
        
        Args:
            width: 图案宽度（拼豆数量）
            height: 图案高度（拼豆数量）
            bead_size_mm: 单个拼豆的尺寸（毫米）
        """
        self.width = width
        self.height = height
        self.bead_size_mm = bead_size_mm
        self.pattern: np.ndarray = np.full((height, width), None, dtype=object)
        self.actual_width_mm = width * bead_size_mm
        self.actual_height_mm = height * bead_size_mm
    
    def set_bead(self, x: int, y: int, color_info: Dict) -> None:
        """
        设置指定位置的拼豆颜色
        
        Args:
            x: X坐标（列）
            y: Y坐标（行）
            color_info: 颜色信息字典（包含id, name_zh, name_en, code, rgb等）
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pattern[y, x] = color_info.copy()
    
    def get_bead(self, x: int, y: int) -> Optional[Dict]:
        """
        获取指定位置的拼豆颜色
        
        Args:
            x: X坐标（列）
            y: Y坐标（行）
            
        Returns:
            颜色信息字典，如果位置无效返回None
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.pattern[y, x]
        return None
    
    def from_matched_colors(self, matched_colors: np.ndarray) -> None:
        """
        从匹配的颜色数组生成图案
        
        Args:
            matched_colors: 匹配的颜色数组（从color_matcher.match_image_colors获得）
        """
        height, width = matched_colors.shape[:2]
        
        # 调整图案尺寸
        if width != self.width or height != self.height:
            self.width = width
            self.height = height
            self.pattern = np.full((height, width), None, dtype=object)
            self.actual_width_mm = width * self.bead_size_mm
            self.actual_height_mm = height * self.bead_size_mm
        
        # 复制颜色信息
        self.pattern = matched_colors.copy()
    
    def get_subject_bounds(self, background_colors: Optional[List] = None) -> Optional[Tuple[int, int, int, int]]:
        """
        获取主体部分的边界框（排除背景）
        
        Args:
            background_colors: 背景颜色列表，可以是颜色ID列表、RGB值列表或颜色代码列表
                            如果为None，自动检测白色背景 (RGB接近255,255,255)
        
        Returns:
            边界框 (min_x, min_y, max_x, max_y)，如果没有主体部分返回None
        """
        if background_colors is None:
            # 默认背景色：白色 (RGB >= 250, 250, 250)
            background_colors = []
            # 收集所有可能是白色的颜色
            for y in range(self.height):
                for x in range(self.width):
                    bead = self.pattern[y, x]
                    if bead is not None:
                        rgb = bead.get('rgb', [255, 255, 255])
                        if isinstance(rgb, (list, tuple)) and len(rgb) >= 3:
                            if rgb[0] >= 250 and rgb[1] >= 250 and rgb[2] >= 250:
                                color_id = bead.get('id')
                                if color_id and color_id not in background_colors:
                                    background_colors.append(color_id)
        
        # 转换为颜色ID集合以便快速查找
        background_color_ids = set()
        for bg in background_colors:
            if isinstance(bg, int):
                background_color_ids.add(bg)
            elif isinstance(bg, (list, tuple)) and len(bg) >= 3:
                # RGB值，查找匹配的颜色
                for y in range(self.height):
                    for x in range(self.width):
                        bead = self.pattern[y, x]
                        if bead is not None:
                            bead_rgb = bead.get('rgb', [])
                            if isinstance(bead_rgb, (list, tuple)) and len(bead_rgb) >= 3:
                                if abs(bead_rgb[0] - bg[0]) < 5 and abs(bead_rgb[1] - bg[1]) < 5 and abs(bead_rgb[2] - bg[2]) < 5:
                                    color_id = bead.get('id')
                                    if color_id:
                                        background_color_ids.add(color_id)
                                    break
        
        # 找到主体部分的边界
        min_x, min_y = self.width, self.height
        max_x, max_y = -1, -1
        found_subject = False
        
        for y in range(self.height):
            for x in range(self.width):
                bead = self.pattern[y, x]
                if bead is not None:
                    color_id = bead.get('id')
                    # 如果不是背景色，则为主体部分
                    if color_id not in background_color_ids:
                        found_subject = True
                        min_x = min(min_x, x)
                        min_y = min(min_y, y)
                        max_x = max(max_x, x)
                        max_y = max(max_y, y)
        
        if not found_subject:
            return None
        
        return (min_x, min_y, max_x + 1, max_y + 1)
    
    def get_subject_size(self, background_colors: Optional[List] = None) -> Dict:
        """
        获取主体部分的尺寸信息（排除背景）
        
        Args:
            background_colors: 背景颜色列表
        
        Returns:
            主体尺寸字典
        """
        bounds = self.get_subject_bounds(background_colors)
        if bounds is None:
            return {
                'subject_width': 0,
                'subject_height': 0,
                'subject_width_mm': 0.0,
                'subject_height_mm': 0.0,
                'bounds': None
            }
        
        min_x, min_y, max_x, max_y = bounds
        subject_width = max_x - min_x
        subject_height = max_y - min_y
        
        return {
            'subject_width': subject_width,
            'subject_height': subject_height,
            'subject_width_mm': subject_width * self.bead_size_mm,
            'subject_height_mm': subject_height * self.bead_size_mm,
            'bounds': bounds
        }
    
    def get_color_statistics(self, exclude_background: bool = False, background_colors: Optional[List] = None) -> Dict:
        """
        获取颜色统计信息
        
        Args:
            exclude_background: 是否排除背景色
            background_colors: 背景颜色列表
        
        Returns:
            颜色统计字典 {color_id: count}
        """
        color_counts = {}
        color_details = {}
        subject_beads = 0
        background_color_ids = set()
        
        # 如果排除背景，识别背景颜色ID
        if exclude_background and background_colors is not None:
            for bg in background_colors:
                if isinstance(bg, int):
                    background_color_ids.add(bg)
                elif isinstance(bg, (list, tuple)) and len(bg) >= 3:
                    # RGB值，查找匹配的颜色
                    for y in range(self.height):
                        for x in range(self.width):
                            bead = self.pattern[y, x]
                            if bead is not None:
                                bead_rgb = bead.get('rgb', [])
                                if isinstance(bead_rgb, (list, tuple)) and len(bead_rgb) >= 3:
                                    if abs(bead_rgb[0] - bg[0]) < 5 and abs(bead_rgb[1] - bg[1]) < 5 and abs(bead_rgb[2] - bg[2]) < 5:
                                        color_id = bead.get('id')
                                        if color_id:
                                            background_color_ids.add(color_id)
        
        # 如果排除背景且未指定背景色，自动检测白色
        if exclude_background and not background_color_ids:
            for y in range(self.height):
                for x in range(self.width):
                    bead = self.pattern[y, x]
                    if bead is not None:
                        rgb = bead.get('rgb', [255, 255, 255])
                        if isinstance(rgb, (list, tuple)) and len(rgb) >= 3:
                            if rgb[0] >= 250 and rgb[1] >= 250 and rgb[2] >= 250:
                                color_id = bead.get('id')
                                if color_id:
                                    background_color_ids.add(color_id)
        
        for y in range(self.height):
            for x in range(self.width):
                bead = self.pattern[y, x]
                if bead is not None:
                    color_id = bead.get('id')
                    if color_id:
                        # 如果排除背景且当前颜色是背景色，跳过
                        if exclude_background and color_id in background_color_ids:
                            continue
                        
                        color_counts[color_id] = color_counts.get(color_id, 0) + 1
                        subject_beads += 1
                        if color_id not in color_details:
                            color_details[color_id] = bead.copy()
        
        return {
            'total_beads': self.width * self.height,
            'subject_beads': subject_beads if exclude_background else self.width * self.height,
            'background_beads': (self.width * self.height - subject_beads) if exclude_background else 0,
            'color_counts': color_counts,
            'color_details': color_details,
            'unique_colors': len(color_counts)
        }
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            图案字典
        """
        pattern_list = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                bead = self.pattern[y, x]
                if bead is not None:
                    row.append({
                        'x': x,
                        'y': y,
                        'color_id': bead.get('id'),
                        'color_code': bead.get('code'),
                        'color_name_zh': bead.get('name_zh'),
                        'color_name_en': bead.get('name_en'),
                        'rgb': bead.get('rgb')
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
        """
        导出为JSON文件
        
        Args:
            file_path: 输出文件路径
        """
        data = self.to_dict()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def to_csv(self, file_path: str) -> None:
        """
        导出为CSV文件
        
        Args:
            file_path: 输出文件路径
        """
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(['行(Y)', '列(X)', '颜色ID', '色号代码', '颜色名称', 'RGB'])
            
            # 写入数据
            for y in range(self.height):
                for x in range(self.width):
                    bead = self.pattern[y, x]
                    if bead is not None:
                        writer.writerow([
                            y, x,
                            bead.get('id'),
                            bead.get('code'),
                            bead.get('name_zh'),
                            f"{bead.get('rgb')[0]},{bead.get('rgb')[1]},{bead.get('rgb')[2]}"
                        ])
                    else:
                        writer.writerow([y, x, None, '', '', ''])
    
    def to_image(self, cell_size: int = 20, show_labels: bool = True,
                 show_grid: bool = True, grid_color: Tuple[int, int, int] = (200, 200, 200)) -> Image.Image:
        """
        生成可视化图像
        
        Args:
            cell_size: 每个拼豆的像素大小
            show_labels: 是否显示色号标签（默认True，显示编号）
            show_grid: 是否显示网格线
            grid_color: 网格线颜色
            
        Returns:
            PIL Image对象
        """
        img_width = self.width * cell_size
        img_height = self.height * cell_size
        
        image = Image.new('RGB', (img_width, img_height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 尝试加载字体，如果失败则使用默认字体
        try:
            # 根据cell_size调整字体大小
            if cell_size <= 15:
                font_size = max(6, cell_size // 3)
            elif cell_size <= 30:
                font_size = max(8, cell_size // 2)
            else:
                font_size = max(12, cell_size // 2)
            
            # 尝试使用系统字体
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                    except:
                        # 使用默认字体
                        font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 绘制拼豆
        for y in range(self.height):
            for x in range(self.width):
                bead = self.pattern[y, x]
                if bead is not None:
                    rgb = bead.get('rgb', [255, 255, 255])
                    rect = [
                        x * cell_size,
                        y * cell_size,
                        (x + 1) * cell_size,
                        (y + 1) * cell_size
                    ]
                    draw.rectangle(rect, fill=tuple(rgb))
                    
                    # 显示标签（默认显示编号）
                    if show_labels:
                        code = bead.get('code', '')
                        if code:
                            # 使用字体计算文字位置（居中）
                            bbox = draw.textbbox((0, 0), code, font=font)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                            text_x = x * cell_size + (cell_size - text_width) // 2
                            text_y = y * cell_size + (cell_size - text_height) // 2
                            
                            # 计算对比色（确保文字可读）
                            brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
                            if brightness > 128:
                                # 背景较亮，使用深色文字
                                text_color = (0, 0, 0)
                            else:
                                # 背景较暗，使用浅色文字
                                text_color = (255, 255, 255)
                            
                            # 如果对比度不够，添加描边
                            if abs(brightness - 128) < 50:
                                # 添加白色描边
                                for adj_x in [-1, 0, 1]:
                                    for adj_y in [-1, 0, 1]:
                                        if adj_x != 0 or adj_y != 0:
                                            draw.text((text_x + adj_x, text_y + adj_y), code, 
                                                     fill=(255, 255, 255), font=font)
                            
                            draw.text((text_x, text_y), code, fill=text_color, font=font)
        
        # 绘制网格线
        if show_grid:
            for x in range(self.width + 1):
                x_pos = x * cell_size
                draw.line([(x_pos, 0), (x_pos, img_height)], fill=grid_color, width=1)
            
            for y in range(self.height + 1):
                y_pos = y * cell_size
                draw.line([(0, y_pos), (img_width, y_pos)], fill=grid_color, width=1)
        
        return image
    
    def save_image(self, file_path: str, cell_size: int = 20, 
                   show_labels: bool = False, show_grid: bool = True) -> None:
        """
        保存可视化图像
        
        Args:
            file_path: 输出文件路径
            cell_size: 每个拼豆的像素大小
            show_labels: 是否显示色号标签
            show_grid: 是否显示网格线
        """
        image = self.to_image(cell_size, show_labels, show_grid)
        image.save(file_path)


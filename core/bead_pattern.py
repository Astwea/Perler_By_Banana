"""
拼豆图案生成模块
负责生成拼豆图案数据结构、标记色号和导出功能
"""
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
import json
from PIL import Image, ImageDraw, ImageFont
import os
import re


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
                 show_grid: bool = True, grid_color: Tuple[int, int, int] = (200, 200, 200),
                 show_legend: bool = False) -> Image.Image:
        """
        生成可视化图像

        Args:
            cell_size: 每个拼豆的像素大小
            show_labels: 是否显示色号标签（默认True，显示编号）
            show_grid: 是否显示网格线
            grid_color: 网格线颜色
            show_legend: 是否在右侧显示颜色统计信息

        Returns:
            PIL Image对象
        """
        img_width = self.width * cell_size
        img_height = self.height * cell_size

        stats = self.get_color_statistics()
        color_counts = stats['color_counts']
        color_details = stats['color_details']

        legend_width = 0
        if show_legend and color_counts:
            item_width = 30 + 50 + 100 + 50 + 30
            legend_width = 20 + item_width

        total_width = img_width + legend_width
        image = Image.new('RGB', (total_width, img_height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 尝试加载默认字体，如果失败则使用默认字体
        # 基础字体大小根据cell_size调整
        if cell_size <= 15:
            base_font_size = max(7, int(cell_size * 0.6))
        elif cell_size <= 30:
            base_font_size = max(9, int(cell_size * 0.6))
        else:
            base_font_size = max(12, int(cell_size * 0.5))
        
        font_cache: Dict[int, Any] = {}
        text_layout_cache: Dict[str, Tuple[Any, float, float]] = {}
        display_code_cache: Dict[str, str] = {}

        def get_font(size):
            """获取指定大小的字体 - 使用粗体以提高清晰度"""
            cached = font_cache.get(size)
            if cached is not None:
                return cached
            try:
                # 优先使用粗体字体，提高清晰度
                try:
                    font = ImageFont.truetype("arialbd.ttf", size)
                except:
                    try:
                        font = ImageFont.truetype("/System/Library/Fonts/Arial Bold.ttf", size)
                    except:
                        try:
                            font = ImageFont.truetype("arial.ttf", size)
                        except:
                            try:
                                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size)
                            except:
                                try:
                                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
                                except:
                                    try:
                                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
                                    except:
                                        font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            font_cache[size] = font
            return font
        
        base_font = get_font(base_font_size)
        if hasattr(draw, "fontmode"):
            draw.fontmode = "1" if base_font_size <= 10 else "L"
        stroke_width = max(1, cell_size // 15)
        stroke_offsets = [
            (adj_x, adj_y)
            for adj_x in range(-stroke_width, stroke_width + 1)
            for adj_y in range(-stroke_width, stroke_width + 1)
            if adj_x != 0 or adj_y != 0
        ]
        
        def normalize_code_label(label: str) -> str:
            """规范化编号显示（去除前导0）"""
            match = re.match(r"^([A-Za-z]+)(\d+)$", label)
            if match:
                prefix, digits = match.groups()
                return f"{prefix}{int(digits)}"
            match = re.match(r"^(\d+)$", label)
            if match:
                return str(int(match.group(1)))
            return label

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
                        # 优先使用完整的code（包含品牌信息），如果没有则使用color_name
                        code = bead.get('code', '')
                        if not code:
                            # 如果没有code，尝试从品牌和色号构建
                            brand = bead.get('brand', '')
                            series = bead.get('series', '')
                            color_name = bead.get('color_name', '')
                            if brand and series and color_name:
                                code = f"{brand}-{series}-{color_name}"
                            elif color_name:
                                code = color_name
                        
                        if code:
                            # 统一只显示色号编号（最后一部分），不显示品牌和系列信息
                            # 例如：COCO-291-A01 -> A01, Mard-120-B05 -> B05
                            display_code = display_code_cache.get(code)
                            if display_code is None:
                                parts = code.split('-')
                                if len(parts) > 1:
                                    display_code = parts[-1]  # 只显示最后一部分（色号编号）
                                else:
                                    # 如果没有分隔符，直接使用code（可能是自定义色号）
                                    display_code = code
                                display_code = normalize_code_label(display_code)
                                display_code_cache[code] = display_code
                            
                            # 使用基础字体计算文字位置（居中）
                            cached_layout = text_layout_cache.get(display_code)
                            if cached_layout is None:
                                font = base_font
                                bbox = draw.textbbox((0, 0), display_code, font=font)
                                text_width = bbox[2] - bbox[0]
                                text_height = bbox[3] - bbox[1]
                                
                                # 确保文字不超出格子，宽高都需要适配
                                if text_width > cell_size * 0.8 or text_height > cell_size * 0.8:
                                    width_scale = (cell_size * 0.8) / text_width if text_width else 1.0
                                    height_scale = (cell_size * 0.8) / text_height if text_height else 1.0
                                    text_scale = min(width_scale, height_scale)
                                    adjusted_font_size = max(6, int(base_font_size * text_scale))
                                    font = get_font(adjusted_font_size)
                                    # 重新计算
                                    bbox = draw.textbbox((0, 0), display_code, font=font)
                                    text_width = bbox[2] - bbox[0]
                                    text_height = bbox[3] - bbox[1]
                                
                                cached_layout = (font, text_width, text_height)
                                text_layout_cache[display_code] = cached_layout
                            
                            font, text_width, text_height = cached_layout
                            
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
                            
                            # 始终添加描边以确保文字清晰可见
                            # 先绘制描边（四周）
                            stroke_color = (255, 255, 255) if text_color == (0, 0, 0) else (0, 0, 0)
                            for adj_x, adj_y in stroke_offsets:
                                # 描边颜色与文字颜色相反
                                draw.text((text_x + adj_x, text_y + adj_y), display_code, 
                                         fill=stroke_color, font=font)
                            
                            # 再绘制文字
                            draw.text((text_x, text_y), display_code, fill=text_color, font=font)
        
        # 绘制网格线
        if show_grid:
            for x in range(self.width + 1):
                x_pos = x * cell_size
                draw.line([(x_pos, 0), (x_pos, img_height)], fill=grid_color, width=1)

            for y in range(self.height + 1):
                y_pos = y * cell_size
                draw.line([(0, y_pos), (img_width, y_pos)], fill=grid_color, width=1)

        if show_legend and color_counts:
            legend_x = img_width + 20
            legend_y = 20

            try:
                title_font = ImageFont.truetype("arialbd.ttf", 16)
                item_font = ImageFont.truetype("arial.ttf", 12)
            except:
                try:
                    title_font = ImageFont.truetype("/System/Library/Fonts/Arial Bold.ttf", 16)
                    item_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
                except:
                    title_font = ImageFont.load_default()
                    item_font = ImageFont.load_default()

            draw.text((legend_x, legend_y), "颜色统计", fill=(0, 0, 0), font=title_font)
            legend_y += 30

            sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)

            for color_id, count in sorted_colors:
                color_detail = color_details.get(color_id, {})
                rgb = color_detail.get('rgb', [255, 255, 255])
                code = color_detail.get('code', '')
                name_zh = color_detail.get('name_zh', color_detail.get('name_en', ''))

                if code:
                    parts = code.split('-')
                    if len(parts) > 1:
                        display_code = parts[-1]
                    else:
                        display_code = code
                else:
                    display_code = ''

                color_box = [legend_x, legend_y, legend_x + 30, legend_y + 30]
                draw.rectangle(color_box, fill=tuple(rgb), outline=(200, 200, 200), width=1)

                draw.text((legend_x + 35, legend_y + 8), display_code, fill=(0, 0, 0), font=item_font)

                name_x = legend_x + 90
                if name_zh:
                    draw.text((name_x, legend_y + 8), name_zh, fill=(0, 0, 0), font=item_font)

                count_text = f"×{count}"
                draw.text((legend_x + 200, legend_y + 8), count_text, fill=(0, 0, 0), font=item_font)

                legend_y += 40

        return image
    
    def save_image(self, file_path: str, cell_size: int = 20,
                   show_labels: bool = False, show_grid: bool = True, show_legend: bool = False) -> None:
        """
        保存可视化图像

        Args:
            file_path: 输出文件路径
            cell_size: 每个拼豆的像素大小
            show_labels: 是否显示色号标签
            show_grid: 是否显示网格线
            show_legend: 是否在右侧显示颜色统计信息
        """
        image = self.to_image(cell_size, show_labels, show_grid, show_legend=show_legend)
        image.save(file_path)

"""
打印模块
负责生成可打印的PDF和图像文件，支持同比例打印
"""
import os
from typing import Tuple, Optional, Dict
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm as mm_unit
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from core.bead_pattern import BeadPattern


class Printer:
    """打印器"""
    
    # 纸张尺寸（毫米）
    PAPER_SIZES = {
        'A4': (210, 297),
        'Letter': (215.9, 279.4),
        'A3': (297, 420),
        'A5': (148, 210)
    }
    
    # 拼豆标准尺寸（毫米）
    BEAD_SIZE_MM = 5.0
    
    def __init__(self, bead_size_mm: float = 5.0):
        """
        初始化打印器
        
        Args:
            bead_size_mm: 单个拼豆的尺寸（毫米）
        """
        self.bead_size_mm = bead_size_mm
    
    def calculate_print_scale(self, pattern_width_mm: float, pattern_height_mm: float,
                             paper_size: str = 'A4', margin_mm: float = 10.0) -> Tuple[float, float]:
        """
        计算打印比例
        
        Args:
            pattern_width_mm: 图案实际宽度（毫米）
            pattern_height_mm: 图案实际高度（毫米）
            paper_size: 纸张大小（'A4', 'Letter'等）
            margin_mm: 页边距（毫米）
            
        Returns:
            (scale, page_width_mm, page_height_mm)
        """
        if paper_size not in self.PAPER_SIZES:
            paper_size = 'A4'
        
        page_width_mm, page_height_mm = self.PAPER_SIZES[paper_size]
        
        # 减去页边距
        available_width = page_width_mm - 2 * margin_mm
        available_height = page_height_mm - 2 * margin_mm
        
        # 计算缩放比例（确保图案完整显示）
        scale_x = available_width / pattern_width_mm
        scale_y = available_height / pattern_height_mm
        scale = min(scale_x, scale_y, 1.0)  # 不超过100%
        
        return scale, page_width_mm, page_height_mm
    
    def generate_print_image(self, pattern: BeadPattern, paper_size: str = 'A4',
                           margin_mm: float = 10.0, show_grid: bool = True,
                           show_labels: bool = False, dpi: int = 300) -> Image.Image:
        """
        生成打印图像
        
        Args:
            pattern: 拼豆图案对象
            paper_size: 纸张大小
            margin_mm: 页边距（毫米）
            show_grid: 是否显示网格
            show_labels: 是否显示色号标签
            dpi: 图像分辨率
            
        Returns:
            PIL Image对象
        """
        # 计算打印比例
        scale, page_width_mm, page_height_mm = self.calculate_print_scale(
            pattern.actual_width_mm, pattern.actual_height_mm, paper_size, margin_mm
        )
        
        # 计算打印后的图案尺寸（毫米）
        print_width_mm = pattern.actual_width_mm * scale
        print_height_mm = pattern.actual_height_mm * scale
        
        # 转换为像素（基于DPI）
        mm_to_pixel = dpi / 25.4  # 1英寸=25.4毫米
        page_width_px = int(page_width_mm * mm_to_pixel)
        page_height_px = int(page_height_mm * mm_to_pixel)
        margin_px = int(margin_mm * mm_to_pixel)
        
        # 创建画布
        canvas_image = Image.new('RGB', (page_width_px, page_height_px), (255, 255, 255))
        draw = ImageDraw.Draw(canvas_image)
        
        # 计算拼豆单元格大小（像素）
        cell_size_mm = self.bead_size_mm * scale
        cell_size_px = int(cell_size_mm * mm_to_pixel)
        
        # 计算图案在页面中的位置（居中）
        pattern_width_px = pattern.width * cell_size_px
        pattern_height_px = pattern.height * cell_size_px
        start_x = margin_px + (page_width_px - 2 * margin_px - pattern_width_px) // 2
        start_y = margin_px + (page_height_px - 2 * margin_px - pattern_height_px) // 2
        
        # 绘制拼豆图案
        for y in range(pattern.height):
            for x in range(pattern.width):
                bead = pattern.get_bead(x, y)
                if bead is not None:
                    rgb = bead.get('rgb', [255, 255, 255])
                    
                    rect = [
                        start_x + x * cell_size_px,
                        start_y + y * cell_size_px,
                        start_x + (x + 1) * cell_size_px,
                        start_y + (y + 1) * cell_size_px
                    ]
                    draw.rectangle(rect, fill=tuple(rgb))
                    
                    # 显示标签
                    if show_labels:
                        code = bead.get('code', '')
                        if code:
                            try:
                                # 尝试使用系统字体
                                font_size = max(8, cell_size_px // 3)
                                font = ImageFont.truetype("arial.ttf", font_size)
                            except:
                                font = ImageFont.load_default()
                            
                            bbox = draw.textbbox((0, 0), code, font=font)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                            text_x = start_x + x * cell_size_px + (cell_size_px - text_width) // 2
                            text_y = start_y + y * cell_size_px + (cell_size_px - text_height) // 2
                            
                            text_color = (255 - rgb[0], 255 - rgb[1], 255 - rgb[2])
                            draw.text((text_x, text_y), code, fill=text_color, font=font)
        
        # 绘制网格线
        if show_grid:
            grid_color = (200, 200, 200)
            for x in range(pattern.width + 1):
                x_pos = start_x + x * cell_size_px
                draw.line([(x_pos, start_y), (x_pos, start_y + pattern_height_px)],
                         fill=grid_color, width=1)
            
            for y in range(pattern.height + 1):
                y_pos = start_y + y * cell_size_px
                draw.line([(start_x, y_pos), (start_x + pattern_width_px, y_pos)],
                         fill=grid_color, width=1)
        
        # 添加信息文本
        info_text = [
            f"图案尺寸: {pattern.width} × {pattern.height} 拼豆",
            f"实际尺寸: {pattern.actual_width_mm:.1f}mm × {pattern.actual_height_mm:.1f}mm",
            f"打印比例: {scale*100:.1f}%",
            f"打印尺寸: {print_width_mm:.1f}mm × {print_height_mm:.1f}mm"
        ]
        
        try:
            info_font = ImageFont.truetype("arial.ttf", 12)
        except:
            info_font = ImageFont.load_default()
        
        y_offset = margin_px // 2
        for i, text in enumerate(info_text):
            draw.text((margin_px, y_offset + i * 15), text, fill=(0, 0, 0), font=info_font)
        
        return canvas_image
    
    def generate_pdf(self, pattern: BeadPattern, output_path: str,
                    paper_size: str = 'A4', margin_mm: float = 10.0,
                    show_grid: bool = True, show_labels: bool = False,
                    dpi: int = 300) -> None:
        """
        生成PDF打印文件
        
        Args:
            pattern: 拼豆图案对象
            output_path: 输出文件路径
            paper_size: 纸张大小
            margin_mm: 页边距（毫米）
            show_grid: 是否显示网格
            show_labels: 是否显示色号标签
            dpi: 图像分辨率
        """
        # 获取纸张尺寸
        if paper_size not in self.PAPER_SIZES:
            paper_size = 'A4'
        
        page_width_mm, page_height_mm = self.PAPER_SIZES[paper_size]
        
        # 生成打印图像
        print_image = self.generate_print_image(pattern, paper_size, margin_mm,
                                               show_grid, show_labels, dpi)
        
        # 转换为ReportLab可用的格式
        img_buffer = io.BytesIO()
        print_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)
        
        # 创建PDF
        c = canvas.Canvas(output_path, pagesize=(page_width_mm * mm_unit, page_height_mm * mm_unit))
        
        # 绘制图像
        c.drawImage(img_reader, 0, 0, width=page_width_mm * mm_unit,
                   height=page_height_mm * mm_unit, preserveAspectRatio=False)
        
        c.save()
    
    def generate_print_png(self, pattern: BeadPattern, output_path: str,
                          paper_size: str = 'A4', margin_mm: float = 10.0,
                          show_grid: bool = True, show_labels: bool = False,
                          dpi: int = 300) -> None:
        """
        生成PNG打印文件
        
        Args:
            pattern: 拼豆图案对象
            output_path: 输出文件路径
            paper_size: 纸张大小
            margin_mm: 页边距（毫米）
            show_grid: 是否显示网格
            show_labels: 是否显示色号标签
            dpi: 图像分辨率
        """
        print_image = self.generate_print_image(pattern, paper_size, margin_mm,
                                               show_grid, show_labels, dpi)
        print_image.save(output_path, dpi=(dpi, dpi))


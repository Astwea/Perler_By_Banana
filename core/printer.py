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
                           show_labels: bool = True, dpi: int = 300) -> Image.Image:
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
                        # 优先使用完整的code（包含品牌信息），如果没有则构建
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
                            parts = code.split('-')
                            if len(parts) > 1:
                                display_code = parts[-1]  # 只显示最后一部分（色号编号）
                            else:
                                # 如果没有分隔符，直接使用code（可能是自定义色号）
                                display_code = code
                            
                            try:
                                # 尝试使用系统字体
                                font_size = max(8, cell_size_px // 3)
                                try:
                                    font = ImageFont.truetype("arial.ttf", font_size)
                                except:
                                    try:
                                        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
                                    except:
                                        try:
                                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                                        except:
                                            font = ImageFont.load_default()
                            except:
                                font = ImageFont.load_default()
                            
                            bbox = draw.textbbox((0, 0), display_code, font=font)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                            
                            # 确保文字不超出格子，如果太宽则缩小字体
                            if text_width > cell_size_px * 0.9:
                                scale = (cell_size_px * 0.9) / text_width
                                adjusted_font_size = max(6, int(font_size * scale))
                                try:
                                    try:
                                        font = ImageFont.truetype("arial.ttf", adjusted_font_size)
                                    except:
                                        try:
                                            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", adjusted_font_size)
                                        except:
                                            try:
                                                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", adjusted_font_size)
                                            except:
                                                font = ImageFont.load_default()
                                except:
                                    font = ImageFont.load_default()
                                # 重新计算
                                bbox = draw.textbbox((0, 0), display_code, font=font)
                                text_width = bbox[2] - bbox[0]
                                text_height = bbox[3] - bbox[1]
                            
                            text_x = start_x + x * cell_size_px + (cell_size_px - text_width) // 2
                            text_y = start_y + y * cell_size_px + (cell_size_px - text_height) // 2
                            
                            # 计算对比色（确保文字可读）
                            brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
                            if brightness > 128:
                                # 背景较亮，使用深色文字
                                text_color = (0, 0, 0)
                                stroke_color = (255, 255, 255)
                            else:
                                # 背景较暗，使用浅色文字
                                text_color = (255, 255, 255)
                                stroke_color = (0, 0, 0)
                            
                            # 添加描边以确保文字清晰可见
                            stroke_width = max(1, cell_size_px // 30)
                            # 先绘制描边（四周）
                            for adj_x in range(-stroke_width, stroke_width + 1):
                                for adj_y in range(-stroke_width, stroke_width + 1):
                                    if adj_x != 0 or adj_y != 0:
                                        draw.text((text_x + adj_x, text_y + adj_y), display_code, 
                                                 fill=stroke_color, font=font)
                            
                            # 再绘制文字
                            draw.text((text_x, text_y), display_code, fill=text_color, font=font)
        
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
                    show_grid: bool = True, show_labels: bool = True,
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
        
        # 获取图像的实际像素尺寸
        img_width_px, img_height_px = print_image.size
        
        # 转换为ReportLab可用的格式
        img_buffer = io.BytesIO()
        print_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)
        
        # 创建PDF
        # 计算PDF页面尺寸（points）
        # mm_unit 是 reportlab 的毫米转点单位：1mm = 2.834645669291339 points (即 72/25.4)
        page_width_points = page_width_mm * mm_unit
        page_height_points = page_height_mm * mm_unit
        c = canvas.Canvas(output_path, pagesize=(page_width_points, page_height_points))
        
        # 将图像像素尺寸转换为PDF点（points）
        # 转换公式：pixels -> points = pixels * (72 / dpi)
        # 这是因为：1英寸 = 72 points = dpi pixels，所以 1 pixel = 72/dpi points
        img_width_points = img_width_px * (72.0 / dpi)
        img_height_points = img_height_px * (72.0 / dpi)
        
        # 计算缩放比例，确保图像完整显示在PDF页面内（不裁剪）
        # 使用较小的缩放比例，确保图像既适应宽度也适应高度
        scale_x = page_width_points / img_width_points
        scale_y = page_height_points / img_height_points
        scale = min(scale_x, scale_y)  # 使用较小的比例，确保完整显示
        
        # 计算缩放后的图像尺寸
        scaled_width = img_width_points * scale
        scaled_height = img_height_points * scale
        
        # 居中绘制图像
        x_pos = (page_width_points - scaled_width) / 2
        y_pos = (page_height_points - scaled_height) / 2
        
        # 绘制图像，保持宽高比，确保不裁剪
        c.drawImage(img_reader, x_pos, y_pos, 
                   width=scaled_width,
                   height=scaled_height, 
                   preserveAspectRatio=True)
        
        c.save()
    
    def generate_print_png(self, pattern: BeadPattern, output_path: str,
                          paper_size: str = 'A4', margin_mm: float = 10.0,
                          show_grid: bool = True, show_labels: bool = True,
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


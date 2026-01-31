from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
from ..core.pattern import BeadPatternV2


def render_legend(pattern: BeadPatternV2, cell_size: int,
               legend_width_px: int = 300, font_size: int = 12,
               sort_by_count: bool = True) -> Image.Image:
    """
    渲染图例面板
    
    Args:
        pattern: BeadPatternV2对象
        cell_size: 单元格像素大小
        legend_width_px: 图例宽度（像素）
        font_size: 字体大小
        sort_by_count: 是否按使用次数排序
    
    Returns:
        添加图例后的图像
    """
    stats = pattern.get_color_statistics()
    color_ids = list(stats['color_counts'].keys())
    
    if sort_by_count:
        color_ids.sort(key=lambda x: -stats['color_counts'][x])
    
    legend_img = Image.new('RGB', (legend_width_px, len(color_ids) * 40 + 20), (255, 255, 255))
    draw = ImageDraw.Draw(legend_img)
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    for i, color_id in enumerate(color_ids):
        y_pos = 20 + i * 40
        
        color_info = pattern.palette.get_color(color_id)
        if color_info:
            rgb = color_info.rgb
            display_code = color_info.display_code
            count = stats['color_counts'][color_id]
            
            draw.rectangle([(10, y_pos), (30, y_pos + 30)], fill=rgb, outline=(0, 0, 0), width=1)
            
            text = f"{display_code} x{count}"
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            
            text_x = 40
            text_y = y_pos + 15 - (text_bbox[3] - text_bbox[1]) // 2
            
            draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font)
    
    return legend_img

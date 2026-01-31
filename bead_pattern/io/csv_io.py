import csv
from typing import Optional, List
from ..core.pattern import BeadPatternV2


def to_csv_coords(pattern: BeadPatternV2, file_path: str) -> None:
    """
    导出坐标表CSV（每行一个拼豆）
    
    Args:
        pattern: BeadPatternV2对象
        file_path: 输出文件路径
    """
    height, width = pattern.grid.shape
    
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['行(Y)', '列(X)', '颜色ID', '色号代码', '颜色名称', 'RGB'])
        
        for y in range(height):
            for x in range(width):
                color_id = pattern.grid.get_id(x, y)
                if color_id != -1:
                    color_info = pattern.palette.get_color(color_id)
                    if color_info:
                        writer.writerow([
                            y, x,
                            color_info.id,
                            color_info.code,
                            color_info.name_zh,
                            f"{color_info.rgb[0]},{color_info.rgb[1]},{color_info.rgb[2]}"
                        ])
                else:
                    writer.writerow([y, x, '', '', '', ''])


def to_csv_summary(pattern: BeadPatternV2, file_path: str, 
                  exclude_background: bool = False) -> None:
    """
    导出统计摘要CSV（每种颜色的数量）
    
    Args:
        pattern: BeadPatternV2对象
        file_path: 输出文件路径
        exclude_background: 是否排除背景色
    """
    stats = pattern.get_color_statistics(exclude_background=exclude_background)
    
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['颜色ID', '色号代码', '颜色名称', 'RGB', '数量'])
        
        for color_id, count in stats['color_counts'].items():
            color_info = pattern.palette.get_color(color_id)
            if color_info:
                writer.writerow([
                    color_id,
                    color_info.code,
                    color_info.name_zh,
                    f"{color_info.rgb[0]},{color_info.rgb[1]},{color_info.rgb[2]}",
                    count
                ])

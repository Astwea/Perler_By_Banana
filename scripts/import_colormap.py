"""
导入 colorMap.json 中的颜色到标准色板
"""
import json
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def hex_to_rgb(hex_color: str) -> list:
    """将十六进制颜色转换为RGB"""
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

def import_colormap(colormap_path: str, output_path: str = "data/standard_colors.json"):
    """
    导入 colorMap.json 到标准色板
    
    Args:
        colormap_path: colorMap.json 文件路径
        output_path: 输出文件路径
    """
    print(f"正在读取 {colormap_path}...")
    with open(colormap_path, 'r', encoding='utf-8') as f:
        colormap_data = json.load(f)
    
    # 加载现有标准色板
    existing_colors = []
    existing_path = Path(output_path)
    if existing_path.exists():
        with open(existing_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            existing_colors = existing_data.get('colors', [])
            max_id = max([c.get('id', 0) for c in existing_colors], default=0)
    else:
        max_id = 0
    
    print(f"现有颜色数: {len(existing_colors)}")
    print(f"开始处理 {len(colormap_data)} 种颜色值...")
    
    # 用于去重（相同的RGB、品牌和色号只保留一个）
    color_set = set()
    new_colors = []
    
    # 遍历 colorMap.json
    color_id = max_id + 1
    for hex_color, color_list in colormap_data.items():
        if not color_list:
            continue
        
        for color_info in color_list:
            color_name = color_info.get('colorName', '')
            color_title = color_info.get('colorTitle', '')
            
            if not color_name or not color_title:
                continue
            
            # 解析 colorTitle: "COCO-291" -> 品牌="COCO", 系列="291"
            parts = color_title.split('-', 1)
            if len(parts) != 2:
                continue
            
            brand = parts[0]  # 品牌
            series = parts[1]  # 色数系列
            
            # 构建唯一键
            unique_key = (hex_color, brand, series, color_name)
            if unique_key in color_set:
                continue
            color_set.add(unique_key)
            
            # 转换为RGB
            rgb = hex_to_rgb(hex_color)
            
            # 构建颜色信息
            color_entry = {
                'id': color_id,
                'name_zh': f"{brand}-{series} {color_name}",
                'name_en': f"{brand}-{series} {color_name}",
                'code': f"{brand}-{series}-{color_name}",  # 完整色号：品牌-系列-编号
                'rgb': rgb,
                'category': brand,  # 使用品牌作为分类
                'brand': brand,  # 品牌信息
                'series': series,  # 系列信息
                'color_name': color_name  # 原始色号
            }
            
            new_colors.append(color_entry)
            color_id += 1
    
    print(f"新导入颜色数: {len(new_colors)}")
    
    # 合并颜色
    all_colors = existing_colors + new_colors
    
    # 保存更新后的色板
    output_data = {
        'name': 'Perler Beads 标准色板（含多品牌）',
        'bead_size_mm': 5,
        'colors': all_colors
    }
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Successfully imported! Total {len(all_colors)} colors")
    print(f"  - Existing colors: {len(existing_colors)}")
    print(f"  - New colors: {len(new_colors)}")
    print(f"  - Saved to: {output_path}")
    
    # 统计各品牌数量
    brand_counts = {}
    for color in new_colors:
        brand = color.get('brand', '未知')
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
    
    print("\n品牌统计:")
    for brand, count in sorted(brand_counts.items()):
        print(f"  {brand}: {count} 种颜色")

if __name__ == '__main__':
    colormap_path = 'colorMap.json'
    if len(sys.argv) > 1:
        colormap_path = sys.argv[1]
    
    import_colormap(colormap_path)

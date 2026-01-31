#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('.')

from core.bead_pattern import BeadPattern
from PIL import Image, ImageDraw, ImageFont

pattern = BeadPattern(width=10, height=10, bead_size_mm=2.6)

colors = [
    {'id': 1, 'code': 'A01', 'name_zh': '红色', 'name_en': 'Red', 'rgb': [255, 0, 0]},
    {'id': 2, 'code': 'A02', 'name_zh': '绿色', 'name_en': 'Green', 'rgb': [0, 255, 0]},
    {'id': 3, 'code': 'A03', 'name_zh': '蓝色', 'name_en': 'Blue', 'rgb': [0, 0, 255]},
]

for y in range(10):
    for x in range(10):
        color_index = (x + y) % 3
        pattern.set_bead(x, y, colors[color_index])

print("=== 调试信息 ===")
stats = pattern.get_color_statistics()
print(f"color_counts: {stats['color_counts']}")
print(f"color_details keys: {stats['color_details'].keys()}")
print(f"unique_colors: {stats['unique_colors']}")

print("\n=== 测试1: 不显示图例 ===")
image = pattern.to_image(cell_size=30, show_labels=True, show_grid=True, show_legend=False)
print(f"图像尺寸: {image.size}")
image.save("static/output/test_no_legend.png")

print("\n=== 测试2: 显示图例 ===")
image = pattern.to_image(cell_size=30, show_labels=True, show_grid=True, show_legend=True)
print(f"图像尺寸: {image.size}")
image.save("static/output/test_with_legend.png")

print("\n=== 测试3: 简单图例绘制 ===")
test_img = Image.new('RGB', (500, 500), (255, 255, 255))
draw = ImageDraw.Draw(test_img)

try:
    title_font = ImageFont.load_default()
    item_font = ImageFont.load_default()
    print("字体加载成功")
except Exception as e:
    print(f"字体加载失败: {e}")
    title_font = None
    item_font = None

if title_font:
    draw.text((20, 20), "颜色统计", fill=(0, 0, 0), font=title_font)

    test_y = 60
    test_colors = [
        ((255, 0, 0), 'A01', '红色', 34),
        ((0, 255, 0), 'A02', '绿色', 33),
        ((0, 0, 255), 'A03', '蓝色', 33),
    ]

    for rgb, code, name, count in test_colors:
        color_box = [20, test_y, 50, test_y + 30]
        draw.rectangle(color_box, fill=tuple(rgb), outline=(200, 200, 200), width=1)
        draw.text((55, test_y + 8), code, fill=(0, 0, 0), font=item_font)
        draw.text((110, test_y + 8), name, fill=(0, 0, 0), font=item_font)
        draw.text((220, test_y + 8), f"×{count}", fill=(0, 0, 0), font=item_font)
        test_y += 40

test_img.save("static/output/test_simple_legend.png")
print("简单图例已保存")

print("\n测试完成!")

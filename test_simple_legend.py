#!/usr/bin/env python
from PIL import Image, ImageDraw

# 创建图例图像
legend_width = 280
legend_height = 300
legend_image = Image.new('RGB', (legend_width, legend_height), (255, 255, 255))
legend_draw = ImageDraw.Draw(legend_image)

try:
    title_font = ImageFont.truetype("arialbd.ttf", 16)
    item_font = ImageFont.truetype("arial.ttf", 12)
except:
    title_font = ImageFont.load_default()
    item_font = ImageFont.load_default()

legend_draw.text((20, 20), "颜色统计", fill=(0, 0, 0), font=title_font)

legend_y = 50
test_colors = [
    ([255, 0, 0], 'A01', '红色', 34),
    ([0, 255, 0], 'A02', '绿色', 33),
    ([0, 0, 255], 'A03', '蓝色', 33),
]

for rgb, code, name, count in test_colors:
    color_box = [20, legend_y, 50, legend_y + 30]
    legend_draw.rectangle(color_box, fill=tuple(rgb), outline=(0, 0, 0), width=2)

    legend_draw.text((55, legend_y + 8), code, fill=(0, 0, 0), font=item_font)

    name_x = 110
    legend_draw.text((name_x, legend_y + 8), name, fill=(0, 0, 0), font=item_font)

    count_text = f"×{count}"
    legend_draw.text((220, legend_y + 8), count_text, fill=(0, 0, 0), font=item_font)

    legend_y += 40

# 保存图例
legend_image.save("static/output/test_legend_only.png")
print("图例图像已保存到 static/output/test_legend_only.png")
print(f"图例图像尺寸: {legend_image.size}")

# 读取图例图像并检查像素
test_pixel = legend_image.getpixel((30, 30))
print(f"图例图像像素 (30, 30): {test_pixel}")

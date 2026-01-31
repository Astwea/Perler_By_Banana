"""
简化的工程蓝图功能测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image
from bead_pattern import BeadPattern
from bead_pattern.render.technical_panel import (
    generate_technical_sheet,
    TechnicalPanelConfig
)


def test_simple_blueprint():
    """测试简化的工程蓝图导出功能"""
    print("开始测试工程蓝图功能...")

    try:
        # 创建测试图案（5x5）
        pattern = BeadPattern(5, 5, bead_size_mm=2.6)

        # 添加测试颜色
        test_colors = [
            {'id': 1, 'code': 'BLK', 'rgb': [0, 0, 0], 'name_zh': '黑色', 'name_en': 'Black'},
            {'id': 2, 'code': 'RED', 'rgb': [255, 0, 0], 'name_zh': '红色', 'name_en': 'Red'},
            {'id': 3, 'code': 'GRN', 'rgb': [0, 255, 0], 'name_zh': '绿色', 'name_en': 'Green'},
        ]

        # 创建图案（3x3）- 中间是空的
        for y in range(3):
            for x in range(3):
                pattern.set_bead(x, y, 1)

        # 创建配置
        config = TechnicalPanelConfig(
            font_size=12,
            color_block_size=24,
            row_height=32,
            panel_padding=20,
            margin_from_pattern=20
            background_color=(255, 255, 255),
            text_color=(0, 0, 0),
            border_width=0,
            header_font_size=14
        )

        # 生成工程蓝图
        print("生成工程蓝图...")
        tech_sheet = generate_technical_sheet(
            pattern,
            cell_size=10,
            show_grid=True,
            show_labels=False,
            config=config,
            exclude_background=True
        )

        # 保存输出
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)

        sheet_path = os.path.join(output_dir, "blueprint_sheet.png")
        tech_sheet.save(sheet_path)

        print(f"工程蓝图已保存到: {sheet_path}")

        # 验证图像
        if os.path.exists(sheet_path):
            img = Image.open(sheet_path)
            print(f"图像尺寸: {img.size}")

        print("\n测试完成！")
        print(f"查看导出的工程蓝图: {sheet_path}")

        return True

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_simple_blueprint()
    if success:
        print("✅ 工程蓝图功能测试通过")
    else:
        print("✗ 测试失败")

"""
测试工程蓝图风格功能
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


def create_test_pattern():
    """创建一个测试拼豆图案"""
    pattern = BeadPattern(10, 10, bead_size_mm=2.6)

    # 手动设置一些拼豆
    test_colors = [
        {'id': 1, 'code': 'BLK', 'rgb': [0, 0, 0], 'name_zh': '黑色', 'name_en': 'Black'},
        {'id': 2, 'code': 'RED', 'rgb': [255, 0, 0], 'name_zh': '红色', 'name_en': 'Red'},
        {'id': 3, 'code': 'GRN', 'rgb': [0, 255, 0], 'name_zh': '绿色', 'name_en': 'Green'},
        {'id': 4, 'code': 'BLU', 'rgb': [0, 0, 255], 'name_zh': '蓝色', 'name_en': 'Blue'},
    ]

    # 创建一个简单的图案（5x5）
    pattern_map = {
        (0, 0): 1,
        (1, 0): 1,
        (2, 0): 1,
        (3, 0): 1,
        (4, 0): 1,
        (0, 1): 2,
        (1, 1): 2,
        (2, 1): 2,
        (3, 1): 2,
        (4, 1): 2,
    }

    for (x, y), color_id in pattern_map.items():
        if color_id <= len(test_colors):
            pattern.set_bead(x, y, test_colors[color_id - 1])

    return pattern


def test_blueprint_export():
    """测试工程蓝图导出功能"""
    print("开始测试工程蓝图导出功能...")

    try:
        # 创建测试图案
        pattern = create_test_pattern()

        # 创建配置
        config = TechnicalPanelConfig()
        config.font_size = 12
        config.color_block_size = 24
        config.row_height = 32
        config.panel_padding = 20
        config.margin_from_pattern = 20
        config.background_color = (255, 255, 255)
        config.text_color = (0, 0, 0)
        config.border_width = 0
        config.header_font_size = 14

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
    success = test_blueprint_export()
    if success:
        print("✅ 所有测试通过")
    else:
        print("✗ 测试失败")
        sys.exit(1)

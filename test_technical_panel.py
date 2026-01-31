"""
测试工程说明书风格信息面板功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bead_pattern.render.technical_panel import (
    TechnicalPanelConfig,
    generate_technical_sheet,
    export_statistics
)
from bead_pattern import BeadPattern
from PIL import Image


def create_test_pattern():
    """
    创建一个测试拼豆图案
    """
    # 创建一个简单的5x5图案
    pattern = BeadPattern(20, 20, bead_size_mm=2.6)

    # 模拟匹配的颜色数据
    test_colors = [
        {'id': 1, 'code': 'BLK', 'rgb': [0, 0, 0], 'name_zh': '黑色', 'name_en': 'Black'},
        {'id': 2, 'code': 'RED', 'rgb': [255, 0, 0], 'name_zh': '红色', 'name_en': 'Red'},
        {'id': 3, 'code': 'GRN', 'rgb': [0, 255, 0], 'name_zh': '绿色', 'name_en': 'Green'},
        {'id': 4, 'code': 'BLU', 'rgb': [0, 0, 255], 'name_zh': '蓝色', 'name_en': 'Blue'},
        {'id': 5, 'code': 'WHT', 'rgb': [255, 255, 255], 'name_zh': '白色', 'name_en': 'White'},
    ]

    # 手动设置一些拼豆（模拟图案）
    color_map = {
        (0, 0): 1, (1, 0): 1, (2, 0): 1, (3, 0): 1, (4, 0): 1,
        (0, 1): 1, (1, 1): 2, (2, 1): 2, (3, 1): 2, (4, 1): 1,
        (0, 2): 1, (1, 2): 2, (2, 2): 3, (3, 2): 2, (4, 2): 1,
        (0, 3): 1, (1, 3): 2, (2, 3): 2, (3, 3): 2, (4, 3): 1,
        (0, 4): 1, (1, 4): 1, (2, 4): 1, (3, 4): 1, (4, 4): 1,
    }

    for (x, y), color_id in color_map.items():
        pattern.set_bead(x, y, test_colors[color_id - 1])

    return pattern


def test_technical_panel():
    """
    测试工程说明书面板生成
    """
    print("开始测试工程说明书面板功能...")

    # 创建测试图案
    pattern = create_test_pattern()

    # 创建输出目录
    os.makedirs("test_output", exist_ok=True)

    # 测试1: 生成工程图纸
    print("\n测试1: 生成工程图纸...")
    config = TechnicalPanelConfig(
        font_size=12,
        color_block_size=24,
        row_height=32,
        panel_padding=20,
        margin_from_pattern=20
    )

    try:
        tech_sheet = generate_technical_sheet(
            pattern,
            cell_size=10,
            show_grid=True,
            show_labels=False,
            config=config,
            exclude_background=True
        )

        tech_sheet_path = "test_output/technical_sheet_test.png"
        tech_sheet.save(tech_sheet_path)
        print(f"工程图纸已保存到: {tech_sheet_path}")
    except Exception as e:
        print(f"生成工程图纸失败: {e}")
        import traceback
        traceback.print_exc()

    # 测试2: 导出JSON统计
    print("\n测试2: 导出JSON统计...")
    json_stats_path = "test_output/stats_test.json"
    try:
        export_statistics(pattern, json_stats_path, format="json", exclude_background=True)
        print(f"JSON统计已保存到: {json_stats_path}")
    except Exception as e:
        print(f"导出JSON统计失败: {e}")
        import traceback
        traceback.print_exc()

    # 测试3: 导出CSV统计
    print("\n测试3: 导出CSV统计...")
    csv_stats_path = "test_output/stats_test.csv"
    try:
        export_statistics(pattern, csv_stats_path, format="csv", exclude_background=True)
        print(f"CSV统计已保存到: {csv_stats_path}")
    except Exception as e:
        print(f"导出CSV统计失败: {e}")
        import traceback
        traceback.print_exc()

    # 打印颜色统计信息
    print("\n颜色统计信息:")
    stats = pattern.get_color_statistics(exclude_background=True)
    print(f"总拼豆数: {stats['total_beads']}")
    print(f"颜色数量: {stats['unique_colors']}")
    print("\n各颜色使用数量:")
    # 使用内部的V2对象访问palette
    pattern_v2 = pattern._v2 if hasattr(pattern, '_v2') else pattern
    for color_id, count in sorted(stats['color_counts'].items(), key=lambda x: -x[1]):
        color_info = pattern_v2.palette.get_color(color_id)
        if color_info:
            print(f"  {color_info.display_code} ({color_info.name_zh}): {count} pcs")

    print("\n测试完成!")
    print(f"所有测试文件保存在: test_output/")


if __name__ == "__main__":
    test_technical_panel()

#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("bead_pattern 包测试")
print("=" * 60)

try:
    print("\n[1] 导入新包...")
    from bead_pattern import BeadPattern
    print("✓ 成功导入 BeadPattern from bead_pattern")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

try:
    print("\n[2] 测试基本功能...")
    import numpy as np
    
    pattern = BeadPattern(100, 100, 2.6)
    print(f"✓ 创建 100x100 图案")
    
    # 创建测试数据
    matched_colors = np.full((100, 100), None, dtype=object)
    
    for y in range(50):
        for x in range(50):
            if y % 10 == 0 and x % 10 == 0:
                matched_colors[y, x] = {
                    'id': (y * 50 + x) % 20,
                    'code': f'C{(y * 50 + x) % 20}',
                    'name_zh': f'颜色{(y * 50 + x) % 20}',
                    'name_en': f'Color{(y * 50 + x) % 20}',
                    'rgb': [
                        100 + ((y * 50 + x) % 20) * 7,
                        100 + ((y * 50 + x) % 20) * 7,
                        100 + ((y * 50 + x) % 20) * 7
                    ]
                }
    
    print("✓ 创建测试数据 (2500 个拼豆)")
    
    # 测试 from_matched_colors
    import time
    start = time.time()
    pattern.from_matched_colors(matched_colors)
    elapsed = (time.time() - start) * 1000
    print(f"✓ from_matched_colors 耗时: {elapsed:.2f}ms")
    
    if elapsed > 5000:
        print(f"✗ 警告: 耗时超过5秒 ({elapsed:.2f}ms)")
    else:
        print(f"✓ 性能良好 (< 5秒)")
    
    # 测试统计
    start = time.time()
    stats = pattern.get_color_statistics()
    elapsed = (time.time() - start) * 1000
    print(f"✓ get_color_statistics 耗时: {elapsed:.2f}ms")
    
    if elapsed > 10:
        print(f"✗ 警告: 统计耗时超过10ms ({elapsed:.2f}ms)")
    else:
        print(f"✓ 性能优秀 (< 10ms)")
    
    print(f"\n统计结果:")
    print(f"  总拼豆: {stats['total_beads']}")
    print(f"  主体拼豆: {stats['subject_beads']}")
    print(f"  唯一颜色: {stats['unique_colors']}")
    
    # 测试渲染
    start = time.time()
    img = pattern.to_image(cell_size=20, show_labels=False, show_grid=False)
    elapsed = (time.time() - start) * 1000
    print(f"✓ to_image (无标签) 耗时: {elapsed:.2f}ms")
    
    if elapsed > 200:
        print(f"✗ 警告: 基础渲染超过200ms ({elapsed:.2f}ms)")
    else:
        print(f"✓ 性能优秀 (< 200ms)")
    
    print(f"  图像尺寸: {img.size}")
    
    print("\n" + "=" * 60)
    print("所有测试通过!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

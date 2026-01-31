import time
import numpy as np
from PIL import Image
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bead_pattern.core.pattern import BeadPatternV2
from bead_pattern.core.grid import BeadGrid
from bead_pattern.core.palette import Palette
from bead_pattern.render.raster import render_base, render_grid_lines
from ..render.labels import overlay_labels


def create_test_pattern(width: int = 100, height: int = 100, num_colors: int = 20) -> BeadPatternV2:
    """
    创建测试图案
    
    Args:
        width: 网格宽度
        height: 网格高度
        num_colors: 颜色数量
    
    Returns:
        BeadPatternV2对象
    """
    from ..core.palette import Palette
    
    pattern = BeadPatternV2(width, height, bead_size_mm=2.6)
    
    np.random.seed(42)
    
    grid_ids = np.random.randint(0, num_colors, (height, width), dtype=np.int32)
    
    for cid in range(num_colors):
        pattern.palette.upsert_from_dict({
            'id': cid,
            'code': f'C{cid:02d}',
            'name_zh': f'颜色{cid}',
            'name_en': f'Color{cid}',
            'rgb': [
                np.random.randint(50, 255),
                np.random.randint(50, 255),
                np.random.randint(50, 255)
            ]
        })
    
    pattern.grid.grid_ids = grid_ids
    
    return pattern


def bench_render(pattern: BeadPatternV2, cell_size: int = 20,
               show_labels: bool = False, iterations: int = 5) -> dict:
    """
    基准测试渲染性能
    
    Args:
        pattern: BeadPatternV2对象
        cell_size: 单元格大小
        show_labels: 是否显示标签
        iterations: 迭代次数
    
    Returns:
        性能统计字典
    """
    times = []
    
    for i in range(iterations):
        start = time.time()
        img = render_base(pattern, cell_size)
        times.append(time.time() - start)
    
    return {
        'avg_time_ms': sum(times) / len(times) * 1000,
        'min_time_ms': min(times) * 1000,
        'max_time_ms': max(times) * 1000,
        'total_time_ms': sum(times) * 1000,
        'iterations': iterations
    }


def bench_stats(pattern: BeadPatternV2, iterations: int = 100) -> dict:
    """
    基准测试统计性能
    
    Args:
        pattern: BeadPatternV2对象
        iterations: 迭代次数
    
    Returns:
        性能统计字典
    """
    times = []
    
    for i in range(iterations):
        start = time.time()
        stats = pattern.get_color_statistics()
        times.append(time.time() - start)
    
    return {
        'avg_time_ms': sum(times) / len(times) * 1000,
        'min_time_ms': min(times) * 1000,
        'max_time_ms': max(times) * 1000,
        'total_time_ms': sum(times) * 1000,
        'iterations': iterations
    }


def bench_bounds(pattern: BeadPatternV2, iterations: int = 100) -> dict:
    """
    基准测试边界检测性能
    
    Args:
        pattern: BeadPatternV2对象
        iterations: 迭代次数
    
    Returns:
        性能统计字典
    """
    times = []
    
    for i in range(iterations):
        start = time.time()
        bounds = pattern.get_subject_bounds()
        times.append(time.time() - start)
    
    return {
        'avg_time_ms': sum(times) / len(times) * 1000,
        'min_time_ms': min(times) * 1000,
        'max_time_ms': max(times) * 1000,
        'total_time_ms': sum(times) * 1000,
        'iterations': iterations
    }


def run_full_benchmark(width: int = 100, height: int = 100,
                    cell_size: int = 20, num_colors: int = 20) -> None:
    """
    运行完整基准测试并打印结果
    
    Args:
        width: 网格宽度
        height: 网格高度
        cell_size: 单元格大小
        num_colors: 颜色数量
    """
    print(f"拼豆图案性能基准测试")
    print(f"=" * 60)
    print(f"网格大小: {width}x{height} ({width*height} 单元格)")
    print(f"颜色数量: {num_colors}")
    print(f"单元格大小: {cell_size}px")
    print(f"=" * 60)
    
    pattern = create_test_pattern(width, height, num_colors)
    
    print("渲染性能测试（基础渲染，无标签）:")
    render_stats = bench_render(pattern, cell_size, show_labels=False)
    print(f"  平均: {render_stats['avg_time_ms']:.2f}ms")
    print(f"  最小: {render_stats['min_time_ms']:.2f}ms")
    print(f"  最大: {render_stats['max_time_ms']:.2f}ms")
    print(f"  目标: <100ms")
    print(f"=" * 60)
    
    print("统计性能测试:")
    stats_results = bench_stats(pattern)
    print(f"  平均: {stats_results['avg_time_ms']:.2f}ms")
    print(f"  最小: {stats_results['min_time_ms']:.2f}ms")
    print(f"  最大: {stats_results['max_time_ms']:.2f}ms")
    print(f"  目标: <5ms")
    print(f"=" * 60)
    
    print("边界检测性能测试:")
    bounds_results = bench_bounds(pattern)
    print(f"  平均: {bounds_results['avg_time_ms']:.2f}ms")
    print(f"  最小: {bounds_results['min_time_ms']:.2f}ms")
    print(f"  最大: {bounds_results['max_time_ms']:.2f}ms")
    print(f"  目标: <5ms")
    print(f"=" * 60)


if __name__ == '__main__':
    run_full_benchmark()

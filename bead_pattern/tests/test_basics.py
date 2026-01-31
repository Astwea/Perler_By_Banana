import sys
sys.path.insert(0, '.')
try:
    from bead_pattern.compat.legacy import BeadPattern
    bead_pattern_legacy = True
except:
    from bead_pattern import BeadPattern
    bead_pattern_legacy = False


def test_empty_grid():
    grid = BeadGrid(10, 10)
    assert grid.width == 10
    assert grid.height == 10
    assert np.all(grid.grid_ids == BeadGrid.EMPTY)


def test_grid_operations():
    grid = BeadGrid(10, 10)
    
    grid.set_id(5, 5, 1)
    assert grid.get_id(5, 5) == 1
    
    grid.set_id(3, 3, 2)
    coords = grid.get_coords_by_color_id(2)
    assert coords.shape[0] == 1
    assert coords[0, 0] == 3
    assert coords[0, 1] == 3


def test_pattern_stats():
    from bead_pattern.core.color import ColorInfo
    
    pattern = BeadPatternV2(10, 10, 2.6)
    
    for i in range(3):
        pattern.palette.upsert_from_dict({
            'id': i,
            'code': f'C{i}',
            'name_zh': f'颜色{i}',
            'name_en': f'Color{i}',
            'rgb': [100 * i, 100 * i, 100 * i]
        })
    
    pattern.grid.set_id(0, 0, 0)
    pattern.grid.set_id(1, 1, 1)
    pattern.grid.set_id(2, 2, 2)
    
    stats = pattern.get_color_statistics()
    assert stats['total_beads'] == 100
    assert stats['unique_colors'] == 3
    assert stats['color_counts'][0] == 1
    assert stats['color_counts'][1] == 1
    assert stats['color_counts'][2] == 1


def test_bounds_detection():
    from bead_pattern.core.color import ColorInfo
    
    pattern = BeadPatternV2(10, 10, 2.6)
    
    for i in range(5):
        pattern.palette.upsert_from_dict({
            'id': i,
            'code': f'C{i}',
            'name_zh': f'颜色{i}',
            'name_en': f'Color{i}',
            'rgb': [200 + i * 10, 200 + i * 10, 200 + i * 10]
        })
    
    pattern.grid.set_id(0, 0, 0)
    pattern.grid.set_id(1, 1, 1)
    pattern.grid.set_id(2, 2, 1)
    
    bounds = pattern.get_subject_bounds()
    assert bounds is not None
    assert bounds == (0, 0, 3, 2)


if __name__ == '__main__':
    test_empty_grid()
    test_grid_operations()
    test_pattern_stats()
    test_bounds_detection()
    print("All tests passed!")

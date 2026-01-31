#!/usr/bin/env python
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from bead_pattern import BeadPattern
    print('SUCCESS: BeadPattern imported from bead_pattern')
    
    import time
    import numpy as np
    
    pattern = BeadPattern(10, 10)
    matched = np.full((10, 10), None, dtype=object)
    
    # Set some test data
    for i in range(5):
        matched[0, i] = {
            'id': i,
            'code': f'C{i}',
            'name_zh': f'Color{i}',
            'name_en': f'Color{i}',
            'rgb': [100 * i, 100 * i, 100 * i]
        }
    
    start = time.time()
    pattern.from_matched_colors(matched)
    elapsed = (time.time() - start) * 1000
    print(f'from_matched_colors: {elapsed:.2f}ms')
    
    if elapsed < 1000:
        print('PERFORMANCE: Excellent (<1 second)')
    elif elapsed < 5000:
        print('PERFORMANCE: Good (<5 seconds)')
    else:
        print(f'PERFORMANCE: Slow ({elapsed:.2f}ms)')
        
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

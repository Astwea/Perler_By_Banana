# AGENTS.md - Perler By Banana Project Guide

## Project Overview

FastAPI web application converting images to perler bead patterns with AI enhancement, color matching, and printing.

**Tech Stack:** Python 3.7+, FastAPI, Pillow, NumPy, scikit-image, scikit-learn, ReportLab

## Build/Test Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Check environment
python test_env.py

# Start server
python app.py
# Or: uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Build executable (Windows)
pip install pyinstaller && pyinstaller build_exe.spec
```

**Note:** No test framework configured. Use `python test_env.py` for environment checks or create ad-hoc tests.

## Code Style

### Imports
```python
# Standard library → Third-party → Local
import os, json
from typing import Optional, Dict, List

import numpy as np
from fastapi import FastAPI

from core.image_processor import ImageProcessor
```

### Naming
- Classes: `PascalCase` (`ImageProcessor`)
- Functions: `snake_case` (`load_image`)
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_prefix` (`_update_cache`)

### Formatting
- 4 spaces indentation
- Type hints on all functions
- Chinese docstrings for public APIs
- ~100-120 char lines (flexible)

```python
def load_image(self, image_path: str) -> Image.Image:
    """
    加载图像
    
    Args:
        image_path: 图像文件路径
        
    Returns:
        PIL Image对象
    """
    self.current_image = Image.open(image_path)
    return self.current_image
```

### Error Handling
```python
# Internal logic
if self.current_image is None:
    raise ValueError("请先加载图像")

# API endpoints
if pattern_id not in patterns_store:
    raise HTTPException(status_code=404, detail="图案不存在")

# With logging
except Exception as e:
    error_msg = str(e)
    logger.error(f"处理失败: {error_msg}")
    raise HTTPException(status_code=500, detail=f"处理失败: {error_msg}")
```

## NumPy/Image Patterns

```python
# Type safety
if image_array.dtype != np.uint8:
    image_array = image_array.astype(np.uint8)
image_array = np.clip(image_array, 0, 255).astype(np.uint8)

# Pixel operations
height, width = image_array.shape[:2]
pixels_2d = image_array.reshape(-1, 3)
# ... process ...
optimized_image = optimized_pixels.reshape(height, width, 3)

# Color space conversion
from skimage.color import rgb2lab
rgb_normalized = rgb_array / 255.0
lab_array = rgb2lab(rgb_normalized)
```

## Async/Concurrency

CPU-intensive tasks use thread pool:
```python
from concurrent.futures import ThreadPoolExecutor

thread_pool_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="image_processing")

async def process_image():
    result = await run_in_thread_pool(cpu_intensive_function, arg1, arg2)
```

## File I/O

```python
# UTF-8 encoding for Chinese content
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create directories
os.makedirs(output_dir, exist_ok=True)
```

## API Design (FastAPI)

```python
from pydantic import BaseModel

class ProcessParams(BaseModel):
    max_dimension: int = 100
    target_colors: int = 20

@app.post("/api/process")
async def process(params: ProcessParams):
    ...
```

## File Structure

`core/` modules: single responsibility per file
- `image_processor.py` - Image loading, resizing, filtering
- `color_matcher.py` - Color space, matching, palettes
- `optimizer.py` - Pattern optimization, clustering
- `bead_pattern.py` - Pattern data, rendering
- `printer.py` - PDF/image export
- `nano_banana.py` - External API

## Pitfalls

1. Check `.dtype` after NumPy operations
2. Ensure RGB values are 0-255 before saving
3. Use thread pool for CPU tasks in async endpoints
4. Always specify UTF-8 encoding for files
5. Import `Optional, Dict, List` from `typing` for type hints
6. Avoid mutable defaults: `def func(items=None)`

## Notes

- Chinese for user-facing strings and docstrings
- Thread pool: 4 workers
- Static files: `/static` route
- Templates: `templates/` directory (Jinja2)
- Default port: 8000

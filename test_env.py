#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试环境配置"""

try:
    import fastapi
    print(f"[OK] FastAPI {fastapi.__version__}")
except ImportError as e:
    print(f"[FAIL] FastAPI 导入失败: {e}")

try:
    import uvicorn
    print(f"[OK] uvicorn {uvicorn.__version__}")
except ImportError as e:
    print(f"[FAIL] uvicorn 导入失败: {e}")

try:
    from PIL import Image
    print(f"[OK] Pillow {Image.__version__}")
except ImportError as e:
    print(f"[FAIL] Pillow 导入失败: {e}")

try:
    import numpy as np
    print(f"[OK] numpy {np.__version__}")
except ImportError as e:
    print(f"[FAIL] numpy 导入失败: {e}")

try:
    import sklearn
    print(f"[OK] scikit-learn {sklearn.__version__}")
except ImportError as e:
    print(f"[FAIL] scikit-learn 导入失败: {e}")

try:
    import skimage
    print(f"[OK] scikit-image {skimage.__version__}")
except ImportError as e:
    print(f"[FAIL] scikit-image 导入失败: {e}")

try:
    import matplotlib
    print(f"[OK] matplotlib {matplotlib.__version__}")
except ImportError as e:
    print(f"[FAIL] matplotlib 导入失败: {e}")

try:
    import reportlab
    print(f"[OK] reportlab {reportlab.Version}")
except ImportError as e:
    print(f"[FAIL] reportlab 导入失败: {e}")

try:
    import jinja2
    print(f"[OK] jinja2 {jinja2.__version__}")
except ImportError as e:
    print(f"[FAIL] jinja2 导入失败: {e}")

print("\n环境配置完成！")


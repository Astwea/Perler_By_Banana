# 拼豆图案生成系统 - 依赖问题解决指南

## 🔧 pip依赖冲突解决方案

### 问题原因

错误信息显示tensorflow-intel和相关包的版本冲突。这通常发生在：
1. 全局Python环境中安装了多个版本的相同包
2. 不同项目需要不同版本的包
3. 旧版本的pip解析器无法正确处理依赖关系

### ✅ 推荐解决方案

#### 方案1：使用全新虚拟环境（强烈推荐）

**Windows:**
```batch
# 运行环境设置脚本
setup_env.bat
```

**Linux/Mac:**
```bash
# 运行环境设置脚本
chmod +x setup_env.sh
./setup_env.sh
```

**手动步骤:**
```bash
# 1. 创建虚拟环境
python -m venv venv_desktop

# Windows 激活
venv_desktop\Scripts\activate

# Linux/Mac 激活
source venv_desktop/bin/activate

# 2. 升级pip
python -m pip install --upgrade pip

# 3. 安装依赖
pip install -r requirements_desktop.txt

# 4. 运行应用
python desktop/main.py
```

#### 方案2：使用--no-deps参数（不推荐）

如果必须在现有环境中安装，可以尝试：

```bash
pip install --no-deps PyQt6
pip install --no-deps pillow
pip install --no-deps numpy
...
```

#### 方案3：忽略冲突的包

创建一个`requirements_desktop_ignore.txt`，排除冲突的包：

```bash
pip install -r requirements_desktop.txt --ignore-installed tensorflow-intel
```

#### 方案4：清理并重新安装

**Windows PowerShell:**
```powershell
# 卸载冲突的包
pip uninstall -y tensorflow-intel tensorflow keras protobuf tensorboard tensorflow-estimator

# 清理缓存
pip cache purge

# 重新安装
pip install -r requirements_desktop.txt
```

**Linux/Mac:**
```bash
# 卸载冲突的包
pip uninstall -y tensorflow-intel tensorflow keras protobuf tensorboard tensorflow-estimator

# 清理缓存
pip cache purge

# 重新安装
pip install -r requirements_desktop.txt
```

### 📋 完整安装步骤（推荐流程）

```bash
# ========== 第一步：环境准备 ==========

# Windows
setup_env.bat

# Linux/Mac
chmod +x setup_env.sh && ./setup_env.sh

# ========== 第二步：安装依赖 ==========

pip install -r requirements_desktop.txt

# ========== 第三步：运行应用 ==========

# Windows
run_desktop.bat

# Linux/Mac
./run_desktop.sh

# 或直接运行
python desktop/main.py
```

### 🔍 验证安装

安装完成后，运行验证：

```bash
# 验证PyQt6
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"

# 验证numpy
python -c "import numpy as np; print('NumPy OK')"

# 验证PIL
python -c "from PIL import Image; print('PIL OK')"

# 验证scikit-image
python -c "from skimage import io; print('scikit-image OK')"

# 验证scikit-learn
python -c "from sklearn.cluster import KMeans; print('scikit-learn OK')"
```

### 🚀 快速启动（使用虚拟环境）

创建快捷启动脚本`run_isolated.bat`：

```batch
@echo off
call venv_desktop\Scripts\activate.bat
python desktop/main.py
pause
```

### ⚠️ 重要提醒

1. **本项目不需要tensorflow**，所有冲突的包都可以安全卸载
2. **强烈建议使用虚拟环境**，避免全局包冲突
3. 如果继续遇到问题，请删除`venv_desktop`文件夹重新创建
4. 确保Python版本为3.7或更高（推荐3.8+）

### 💾 虚拟环境位置说明

```
pin_dou/
├── venv_desktop/          # 虚拟环境（不提交到git）
│   ├── Scripts/          # Windows可执行文件
│   ├── Lib/              # 安装的包
│   └── pyvenv.cfg       # 配置文件
├── desktop/              # 桌面应用代码
├── core/                 # 核心模块
├── data/                 # 数据文件
└── requirements_desktop.txt
```

### 📞 故障排除

**Q: 即使使用虚拟环境仍有冲突？**
A: 删除并重建虚拟环境：
```bash
rmdir /s /q venv_desktop  # Windows
rm -rf venv_desktop           # Linux/Mac
python -m venv venv_desktop
```

**Q: pip版本过旧？**
A: 升级pip：
```bash
python -m pip install --upgrade pip setuptools wheel
```

**Q: 某些包安装失败？**
A: 使用清华镜像加速：
```bash
pip install -r requirements_desktop.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

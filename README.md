# Perler By Banana - 拼豆图案生成系统

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103.2-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个功能强大的拼豆图案生成工具，支持将任意图像转换为拼豆图案，并提供AI增强、颜色匹配、图案优化和打印功能。

## ✨ 功能特性

### 🎨 核心功能
- **图像处理**: 支持多种图像格式（PNG, JPG, JPEG等）上传和处理
- **AI增强**: 集成Nano Banana AI，可将图像转换为像素艺术风格
- **颜色匹配**: 智能颜色匹配算法（支持CIE76、CIE94、CIEDE2000）
- **图案优化**: 自动优化颜色数量、尺寸和质量
- **拼豆大小支持**: 支持2.6mm（小拼豆）和5.0mm（标准拼豆）两种规格

### 📊 高级功能
- **自定义色板**: 支持添加、删除、导入/导出自定义颜色（CSV/JSON格式）
- **主体检测**: 自动检测图像主体，排除背景进行尺寸计算
- **可视化展示**: 网格化显示拼豆图案，支持色号标注切换
- **实物效果图**: 使用AI生成拼豆工艺品的实物展示效果图
- **打印功能**: 支持生成PDF和PNG打印文件，同比例打印

### 🔧 便捷工具
- **分步骤执行**: 将图像处理流程分为独立的步骤，支持单独刷新
- **一键执行**: 支持一键执行所有步骤，支持中途停止
- **参数预设**: 提供多种预处理预设（轻度、标准、重度）
- **实时预览**: 支持图像缩放和实时预览

## 📋 环境要求

- **Python**: 3.7+
- **操作系统**: Windows / Linux / macOS
- **浏览器**: Chrome / Firefox / Edge（现代浏览器）

### 推荐环境
- **Anaconda/Miniconda**（用于Python环境管理）
- **Python 3.7**（已测试版本）

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Astwea/Perler_By_Banana.git
cd Perler_By_Banana
```

### 2. 创建Conda环境（推荐）

```bash
# 创建Python 3.7环境
conda create -n perler python=3.7 -y

# 激活环境
conda activate perler
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动应用

#### Windows

**方式1 - PowerShell脚本（推荐）：**
```powershell
# 右键点击 run.ps1，选择"使用PowerShell运行"
# 或者在PowerShell中运行：
.\run.ps1
```

如果提示"无法运行脚本"，请先执行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**方式2 - CMD批处理文件：**
```cmd
# 双击 run.bat 文件
# 或在CMD中运行：
run.bat
```

**方式3 - 手动启动：**
```bash
# 激活conda环境
conda activate perler

# 启动服务器
python app.py
```

#### Linux/macOS

```bash
# 添加执行权限
chmod +x run.sh

# 运行启动脚本
./run.sh
```

或者手动启动：
```bash
conda activate perler
python app.py
```

### 5. 访问应用

启动成功后，在浏览器中访问：
```
http://localhost:8000
```

## ⚙️ 配置说明

### Nano Banana AI配置（可选）

如果希望使用AI增强功能，需要配置Nano Banana API：

1. 在应用界面顶部找到"Nano Banana API配置"区域
2. 填写以下信息：
   - **API密钥**: 你的Nano Banana API密钥
   - **Base URL**: `https://api.grsai.com`（默认）
   - **代理**: 如果需要代理访问，填写代理地址（格式：`http://host:port`）
3. 点击"保存配置"

**注意**: 如果不配置Nano Banana API，系统仍可正常使用，但将跳过AI增强步骤。

### 自定义色板配置

系统内置了标准拼豆色板，你还可以：

1. **添加自定义颜色**：
   - 在"自定义色板管理"区域添加新颜色
   - 填写颜色名称、代码、RGB值等信息

2. **导入颜色**：
   - 支持从CSV或JSON文件导入颜色
   - CSV格式：`ID,中文名称,英文名称,色号代码,R,G,B,分类`
   - JSON格式：包含`colors`数组的标准格式

3. **导出颜色**：
   - 可以将自定义色板导出为CSV或JSON文件
   - 方便备份和分享

## 📖 使用教程

### 基本流程

#### 步骤1: 上传图片
- 点击上传区域或拖拽图片文件到上传区域
- 支持PNG、JPG、JPEG等常见图像格式
- 上传成功后，系统会自动显示图片信息

#### 步骤2: 图像预处理（可选）

**Nano Banana AI转换（可选）：**
- 如果配置了Nano Banana API，可以在这一步将图像转换为像素艺术风格
- 设置提示词和模型参数
- 可选择不同的尺寸类型

**图像预处理：**
- **拼豆大小**: 选择2.6mm（小拼豆）或5.0mm（标准拼豆）
- **最大尺寸**: 限制图案的最大拼豆数量（会根据拼豆大小自动调整范围）
  - 2.6mm拼豆：50-500，默认200
  - 5.0mm拼豆：20-200，默认100
- **预处理预设**: 
  - 轻度预处理：适合Nano Banana结果较好的情况
  - 标准预处理：默认配置，适合大多数情况
  - 重度预处理：适合需要大量优化的原始图片
  - 自定义：手动调整所有参数
- **其他参数**:
  - 目标颜色数量: 优化后的颜色数量（5-50）
  - 降噪强度: 减少图像噪点（0-1）
  - 对比度: 增强或降低图像对比度（0.5-2）
  - 锐度: 增强或降低图像锐度（0.5-2）

#### 步骤3: 生成拼豆图案
- 选择是否使用自定义色板
- 系统会自动使用步骤2中选择的拼豆大小
- 生成完成后显示：
  - 图案总尺寸（拼豆数量和毫米）
  - 主体尺寸（排除背景）
  - 颜色统计信息
  - 可视化图案（支持切换编号显示）

#### 步骤4: 生成实物效果图（可选）
- 使用Nano Banana AI生成拼豆工艺品的实物展示效果图
- 可选择不同的风格预设（钥匙扣、摆件、桌面装饰等）
- 支持自定义提示词

### 快捷操作

#### 一键执行所有步骤
- 点击"一键执行所有步骤"按钮，系统会按顺序执行：
  1. Nano Banana AI转换（如果配置）
  2. 图像预处理
  3. 生成拼豆图案
  4. 生成实物效果图（可选）
- 执行过程中可以点击"停止执行"按钮中断

#### 单独刷新步骤
- 每个步骤都有"刷新"按钮，可以单独重新执行该步骤
- 方便调整参数后快速重新生成

### 导出和打印

生成图案后，可以：

- **查看统计信息**: 图案尺寸、颜色数、拼豆总数等
- **切换编号显示**: 点击"切换编号"按钮显示/隐藏色号
- **图像缩放**: 点击图片可放大查看，使用+/-按钮缩放
- **导出JSON**: 导出完整的图案数据（包含所有颜色信息）
- **导出CSV**: 表格格式，方便在Excel中打开
- **导出PNG**: 高质量图像文件
- **打印预览**: 预览打印效果
- **生成PDF**: 生成可打印的PDF文件

## 🏗️ 项目结构

```
Perler_By_Banana/
├── app.py                      # FastAPI主应用
├── requirements.txt            # Python依赖列表
├── build_exe.spec             # PyInstaller打包配置
├── README.md                   # 项目说明文档
├── NANO_BANANA_使用说明.md    # Nano Banana API使用说明
├── core/                       # 核心功能模块
│   ├── __init__.py
│   ├── image_processor.py      # 图像处理模块
│   ├── color_matcher.py        # 颜色匹配模块
│   ├── optimizer.py            # 图案优化模块
│   ├── bead_pattern.py         # 拼豆图案生成模块
│   ├── nano_banana.py          # Nano Banana API客户端
│   └── printer.py              # 打印功能模块
├── data/                       # 数据文件
│   ├── standard_colors.json    # 标准色板数据
│   └── custom_colors.json      # 自定义色板数据（自动生成）
├── static/                     # 静态文件
│   ├── css/
│   │   └── style.css          # 样式文件
│   ├── js/
│   │   └── main.js            # 前端交互逻辑
│   ├── images/                # 上传的图片存储目录
│   └── output/                # 生成的图案和打印文件
├── templates/                  # HTML模板
│   └── index.html             # 主页面模板
├── run.bat                     # Windows批处理启动脚本
├── run.ps1                     # PowerShell启动脚本（推荐）
├── run.sh                      # Linux/macOS启动脚本
└── 启动应用.ps1               # PowerShell启动脚本（中文名）
```

## 🔧 技术栈

### 后端
- **FastAPI**: 现代、快速的Web框架
- **Uvicorn**: ASGI服务器
- **Pillow**: 图像处理
- **NumPy**: 数值计算
- **scikit-image**: 图像处理算法（颜色匹配）
- **scikit-learn**: 机器学习（K-means聚类）
- **ReportLab**: PDF生成
- **Matplotlib**: 图表和可视化

### 前端
- **HTML5**: 页面结构
- **CSS3**: 样式设计
- **JavaScript (ES6+)**: 交互逻辑

### AI集成
- **Nano Banana API**: AI图像转换服务

## 📦 打包为EXE

如果你想将应用打包成独立的Windows可执行文件：

```bash
# 1. 安装PyInstaller
pip install pyinstaller

# 2. 打包应用
pyinstaller build_exe.spec

# 3. 打包后的exe文件在 dist/ 目录中
```

打包后的exe文件是独立的，可以在没有Python环境的Windows系统上运行。

## ❓ 常见问题

### Q: 启动时提示"无法运行脚本"？
A: 这是PowerShell的执行策略限制。在PowerShell中运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q: CMD提示"未找到conda"？
A: 请使用PowerShell脚本（run.ps1），或者确保conda已添加到系统PATH。

### Q: Nano Banana API调用失败？
A: 检查以下几点：
- API密钥是否正确
- Base URL是否正确（默认：`https://api.grsai.com`）
- 是否需要配置代理（在配置界面填写代理地址）
- 网络连接是否正常

### Q: 颜色匹配效果不好？
A: 尝试以下方法：
- 使用自定义色板，添加更多颜色
- 调整预处理参数（增加目标颜色数量）
- 使用Nano Banana AI转换，获得更好的像素艺术效果

### Q: 生成图案时提示"请先执行预处理步骤"？
A: 确保按照步骤顺序执行：
1. 上传图片
2. 图像预处理
3. 生成拼豆图案

### Q: 主体尺寸计算不准确？
A: 系统会自动检测白色背景。如果背景不是白色，可以在代码中调整`background_rgb`参数。

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👤 作者

**Astwea**

- GitHub: [@Astwea](https://github.com/Astwea)

## 🙏 致谢

- 感谢所有贡献者的支持
- 感谢Nano Banana提供的AI图像转换服务

## 📝 更新日志

### v1.0.0 (2024)
- ✨ 初始版本发布
- 🎨 支持图像上传和处理
- 🤖 集成Nano Banana AI
- 🎨 支持自定义色板管理
- 📊 支持分步骤执行
- 🖨️ 支持打印和导出功能
- 📐 支持2.6mm和5.0mm两种拼豆规格
- 🎯 支持主体检测和背景排除

---

如果这个项目对你有帮助，请给个⭐️ Star支持一下！

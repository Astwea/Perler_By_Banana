"""
拼豆图案生成系统 - FastAPI主应用
"""
import os
import uuid
import shutil
import traceback
import logging
import base64
from pathlib import Path
from typing import Optional, Dict, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from core.image_processor import ImageProcessor
from core.color_matcher import ColorMatcher
from core.optimizer import PatternOptimizer
from core.bead_pattern import BeadPattern
from core.printer import Printer
from core.nano_banana import NanoBananaClient, calculate_aspect_ratio


# 创建FastAPI应用
app = FastAPI(title="拼豆图案生成系统")

# 创建必要的目录
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/images/nano_banana", exist_ok=True)
os.makedirs("static/output", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板引擎
templates = Jinja2Templates(directory="templates")

# 全局实例
image_processor = ImageProcessor()
color_matcher = ColorMatcher()
pattern_optimizer = PatternOptimizer(color_matcher)
printer = Printer()
nano_banana_client: Optional[NanoBananaClient] = None

# 存储生成的图案（内存中）
patterns_store: Dict[str, Dict] = {}

# 存储上传的文件信息（用于Nano Banana）
uploaded_files: Dict[str, Dict] = {}

# 存储每个文件的处理步骤结果（用于分步骤处理）
step_results: Dict[str, Dict] = {}


# 请求/响应模型
class ProcessParams(BaseModel):
    max_dimension: int = 100
    target_colors: int = 20
    use_custom: bool = True
    denoise_strength: float = 0.5
    contrast_factor: float = 1.2
    sharpness_factor: float = 1.1


class OptimizeParams(BaseModel):
    max_dimension: int = 100
    target_colors: int = 20
    denoise_strength: float = 0.5
    contrast_factor: float = 1.2
    sharpness_factor: float = 1.1


class CustomColor(BaseModel):
    name_zh: str
    name_en: str
    code: str
    rgb: List[int]
    category: str = "自定义"


class PrintParams(BaseModel):
    paper_size: str = "A4"
    margin_mm: float = 10.0
    show_grid: bool = True
    show_labels: bool = False
    dpi: int = 300


class NanoBananaConfig(BaseModel):
    api_key: str
    base_url: str = "https://api.grsai.com"
    model: str = "nano-banana-fast"
    image_size: str = "1K"
    proxy: Optional[str] = None  # 代理地址（可选）


class NanoBananaParams(BaseModel):
    prompt: str = "拼豆风格，像素艺术，清晰的色块"
    use_nano_banana: bool = False
    model: str = "nano-banana-fast"
    aspect_ratio: str = "auto"
    image_size: str = "1K"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页面"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图像
    """
    try:
        # 生成唯一ID
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix
        file_path = f"static/images/{file_id}{file_ext}"
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 加载图像获取基本信息
        image_processor.load_image(file_path)
        width, height = image_processor.get_image_size()
        
        file_info = {
            "file_id": file_id,
            "filename": file.filename,
            "file_path": file_path,
            "width": width,
            "height": height
        }
        
        # 存储文件信息
        uploaded_files[file_id] = file_info
        
        return file_info
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        logger.error(f"上传图像失败: {error_msg}")
        logger.error(f"详细错误:\n{error_trace}")
        raise HTTPException(status_code=400, detail=f"上传失败: {error_msg}")


@app.post("/api/config/nano-banana")
async def config_nano_banana(config: NanoBananaConfig):
    """
    配置Nano Banana API
    """
    global nano_banana_client
    try:
        nano_banana_client = NanoBananaClient(
            api_key=config.api_key,
            base_url=config.base_url,
            proxy=config.proxy
        )
        # 保存配置到环境变量（可选）
        os.environ["NANO_BANANA_API_KEY"] = config.api_key
        os.environ["NANO_BANANA_BASE_URL"] = config.base_url
        if config.proxy:
            os.environ["HTTPS_PROXY"] = config.proxy
            os.environ["HTTP_PROXY"] = config.proxy
        
        return {"success": True, "message": "Nano Banana API配置成功"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"配置失败: {str(e)}")


# ============ 分步骤处理API ============

@app.post("/api/step/nano-banana")
async def step_nano_banana(
    file_id: str = Form(...),
    prompt: str = Form("拼豆风格，像素艺术，清晰的色块"),
    model: str = Form("nano-banana-fast"),
    image_size: str = Form("1K"),
    max_dimension: int = Form(200)
):
    """
    步骤1: Nano Banana AI转换
    """
    try:
        if not nano_banana_client:
            raise HTTPException(status_code=400, detail="请先配置Nano Banana API")
        
        # 查找上传的文件
        image_files = list(Path("static/images").glob(f"{file_id}.*"))
        if not image_files:
            raise HTTPException(status_code=404, detail="图像文件不存在")
        
        image_path = str(image_files[0])
        file_info = uploaded_files.get(file_id, {})
        original_width = file_info.get("width", 0)
        original_height = file_info.get("height", 0)
        
        # 计算aspectRatio
        if original_width > 0 and original_height > 0:
            aspect_ratio = calculate_aspect_ratio(original_width, original_height)
        else:
            aspect_ratio = "auto"
        
        logger.info(f"开始Nano Banana转换: file_id={file_id}, prompt={prompt}, model={model}")
        
        # 调用Nano Banana API
        result = nano_banana_client.generate_image(
            prompt=prompt,
            image_path=image_path,
            model=model,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            max_dimension=max_dimension,
            timeout=300
        )
        
        # 下载生成的图片
        if result.get("results") and len(result["results"]) > 0:
            generated_image_url = result["results"][0]["url"]
            nano_banana_file_id = str(uuid.uuid4())
            downloaded_path = nano_banana_client.download_image(
                generated_image_url,
                save_path=f"static/images/nano_banana_{nano_banana_file_id}.png"
            )
            
            # 保存步骤结果
            if file_id not in step_results:
                step_results[file_id] = {}
            step_results[file_id]["nano_banana"] = {
                "image_path": downloaded_path,
                "file_id": nano_banana_file_id,
                "url": f"/static/images/nano_banana_{nano_banana_file_id}.png",
                "params": {
                    "prompt": prompt,
                    "model": model,
                    "image_size": image_size,
                    "max_dimension": max_dimension
                }
            }
            
            logger.info(f"Nano Banana转换完成: {downloaded_path}")
            
            return {
                "success": True,
                "image_url": f"/static/images/nano_banana_{nano_banana_file_id}.png",
                "file_id": nano_banana_file_id
            }
        else:
            raise HTTPException(status_code=500, detail="Nano Banana API未返回图片")
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        logger.error(f"Nano Banana转换失败: {error_msg}")
        logger.error(f"详细错误:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"转换失败: {error_msg}")


@app.post("/api/step/preprocess")
async def step_preprocess(
    file_id: str = Form(...),
    max_dimension: int = Form(200),
    target_colors: int = Form(20),
    denoise_strength: float = Form(0.5),
    contrast_factor: float = Form(1.2),
    sharpness_factor: float = Form(1.1),
    use_custom: bool = Form(True),
    use_nano_banana_result: bool = Form(False),
    bead_size_mm: float = Form(2.6)
):
    """
    步骤2: 图像预处理（降噪、对比度、锐度、颜色优化）
    
    Args:
        file_id: 文件ID
        max_dimension: 最大尺寸（拼豆数量）
        target_colors: 目标颜色数量
        denoise_strength: 降噪强度
        contrast_factor: 对比度因子
        sharpness_factor: 锐度因子
        use_custom: 是否使用自定义色板
        use_nano_banana_result: 是否使用Nano Banana结果
        bead_size_mm: 拼豆大小（毫米），2.6或5.0
    """
    try:
        # 确定输入图片路径
        if use_nano_banana_result and file_id in step_results and "nano_banana" in step_results[file_id]:
            # 使用Nano Banana的结果
            input_image_path = step_results[file_id]["nano_banana"]["image_path"]
            logger.info(f"使用Nano Banana转换后的图片: {input_image_path}")
        else:
            # 使用原始上传的图片
            image_files = list(Path("static/images").glob(f"{file_id}.*"))
            if not image_files:
                raise HTTPException(status_code=404, detail="图像文件不存在")
            input_image_path = str(image_files[0])
            logger.info(f"使用原始图片: {input_image_path}")
        
        # 加载图像
        image_processor.load_image(input_image_path)
        image_array = image_processor.get_image_array()
        
        # 应用优化（基于主体尺寸，排除背景）
        optimized_image, (new_width, new_height) = pattern_optimizer.apply_full_optimization(
            image_array,
            target_colors=target_colors,
            max_dimension=max_dimension,
            denoise_strength=denoise_strength,
            contrast_factor=contrast_factor,
            sharpness_factor=sharpness_factor,
            use_custom=use_custom,
            based_on_subject=True,  # 基于主体尺寸计算
            background_rgb=(255, 255, 255),  # 白色背景
            threshold=5  # 颜色判断阈值
        )
        
        # 保存预处理后的图像
        from PIL import Image
        processed_image = Image.fromarray(optimized_image)
        preprocess_file_id = str(uuid.uuid4())
        preprocess_path = f"static/output/preprocess_{preprocess_file_id}.png"
        processed_image.save(preprocess_path)
        
        # 验证拼豆大小
        if bead_size_mm not in [2.6, 5.0]:
            bead_size_mm = 2.6  # 默认使用2.6mm
        
        # 保存步骤结果
        if file_id not in step_results:
            step_results[file_id] = {}
        step_results[file_id]["preprocess"] = {
            "image_path": preprocess_path,
            "file_id": preprocess_file_id,
            "url": f"/static/output/preprocess_{preprocess_file_id}.png",
            "image_array": None,  # 不保存numpy数组，太大
            "width": new_width,
            "height": new_height,
            "bead_size_mm": bead_size_mm,  # 保存拼豆大小
            "params": {
                "max_dimension": max_dimension,
                "target_colors": target_colors,
                "denoise_strength": denoise_strength,
                "contrast_factor": contrast_factor,
                "sharpness_factor": sharpness_factor,
                "use_custom": use_custom,
                "bead_size_mm": bead_size_mm
            }
        }
        
        logger.info(f"预处理完成: {preprocess_path}, 尺寸: {new_width}x{new_height}")
        
        return {
            "success": True,
            "image_url": f"/static/output/preprocess_{preprocess_file_id}.png",
            "width": new_width,
            "height": new_height,
            "file_id": preprocess_file_id,
            "bead_size_mm": bead_size_mm  # 返回拼豆大小
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        logger.error(f"预处理失败: {error_msg}")
        logger.error(f"详细错误:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"预处理失败: {error_msg}")


@app.post("/api/step/generate-pattern")
async def step_generate_pattern(
    file_id: str = Form(...),
    use_custom: bool = Form(True),
    bead_size_mm: float = Form(2.6)
):
    """
    步骤3: 生成拼豆图案
    
    Args:
        file_id: 文件ID
        use_custom: 是否使用自定义色板
        bead_size_mm: 拼豆大小（毫米），2.6或5.0
    """
    try:
        # 验证拼豆大小
        if bead_size_mm not in [2.6, 5.0]:
            bead_size_mm = 2.6  # 默认使用2.6mm
        
        # 检查是否有预处理结果
        if file_id not in step_results or "preprocess" not in step_results[file_id]:
            raise HTTPException(status_code=400, detail="请先执行预处理步骤")
        
        preprocess_result = step_results[file_id]["preprocess"]
        preprocess_path = preprocess_result["image_path"]
        new_width = preprocess_result["width"]
        new_height = preprocess_result["height"]
        
        # 从预处理结果中获取拼豆大小（如果存在），否则使用传入的参数
        if "bead_size_mm" in preprocess_result:
            bead_size_mm = preprocess_result["bead_size_mm"]
        
        # 重新加载预处理后的图像
        image_processor.load_image(preprocess_path)
        optimized_image = image_processor.get_image_array()
        
        # 颜色匹配（使用CIE94算法提高准确性）
        matched_colors = color_matcher.match_image_colors(optimized_image, use_custom=use_custom, method="cie94")
        
        # 生成拼豆图案（使用指定的拼豆大小）
        bead_pattern = BeadPattern(new_width, new_height, bead_size_mm=bead_size_mm)
        bead_pattern.from_matched_colors(matched_colors)
        
        # 保存图案
        pattern_id = str(uuid.uuid4())
        patterns_store[pattern_id] = {
            "pattern": bead_pattern,
            "file_id": file_id,
            "params": preprocess_result["params"]
        }
        
        # 生成可视化图像（显示编号和不显示编号两个版本）
        viz_image_with_labels = bead_pattern.to_image(cell_size=10, show_labels=True, show_grid=True)
        viz_path_with_labels = f"static/output/{pattern_id}_viz.png"
        viz_image_with_labels.save(viz_path_with_labels)
        
        # 生成不显示编号的版本（用于生成实物效果图）
        viz_image_no_labels = bead_pattern.to_image(cell_size=10, show_labels=False, show_grid=True)
        viz_path_no_labels = f"static/output/{pattern_id}_viz_no_labels.png"
        viz_image_no_labels.save(viz_path_no_labels)
        
        # 获取统计信息（包含主体尺寸）
        stats = bead_pattern.get_color_statistics(exclude_background=False)
        stats_without_bg = bead_pattern.get_color_statistics(exclude_background=True)
        subject_size = bead_pattern.get_subject_size()
        
        # 保存步骤结果
        step_results[file_id]["generate_pattern"] = {
            "pattern_id": pattern_id,
            "viz_url": f"/static/output/{pattern_id}_viz.png",
            "viz_url_no_labels": f"/static/output/{pattern_id}_viz_no_labels.png",
            "width": new_width,
            "height": new_height,
            "actual_width_mm": bead_pattern.actual_width_mm,
            "actual_height_mm": bead_pattern.actual_height_mm,
            "subject_width": subject_size['subject_width'],
            "subject_height": subject_size['subject_height'],
            "subject_width_mm": subject_size['subject_width_mm'],
            "subject_height_mm": subject_size['subject_height_mm'],
            "statistics": stats,
            "subject_statistics": stats_without_bg
        }
        
        logger.info(f"图案生成完成: pattern_id={pattern_id}, 主体尺寸: {subject_size['subject_width']}×{subject_size['subject_height']} ({subject_size['subject_width_mm']:.1f}×{subject_size['subject_height_mm']:.1f}mm)")
        
        return {
            "success": True,
            "pattern_id": pattern_id,
            "width": new_width,
            "height": new_height,
            "actual_width_mm": bead_pattern.actual_width_mm,
            "actual_height_mm": bead_pattern.actual_height_mm,
            "subject_width": subject_size['subject_width'],
            "subject_height": subject_size['subject_height'],
            "subject_width_mm": subject_size['subject_width_mm'],
            "subject_height_mm": subject_size['subject_height_mm'],
            "statistics": stats,
            "subject_statistics": stats_without_bg,
            "viz_url": f"/static/output/{pattern_id}_viz.png",
            "viz_url_no_labels": f"/static/output/{pattern_id}_viz_no_labels.png"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        logger.error(f"图案生成失败: {error_msg}")
        logger.error(f"详细错误:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"生成失败: {error_msg}")


@app.get("/api/step/{file_id}/status")
async def get_step_status(file_id: str):
    """
    获取文件的处理步骤状态
    """
    if file_id not in step_results:
        return {"steps": {}}
    
    status = {"steps": {}}
    steps = step_results[file_id]
    
    if "nano_banana" in steps:
        status["steps"]["nano_banana"] = {
            "completed": True,
            "url": steps["nano_banana"]["url"]
        }
    
    if "preprocess" in steps:
        status["steps"]["preprocess"] = {
            "completed": True,
            "url": steps["preprocess"]["url"],
            "width": steps["preprocess"]["width"],
            "height": steps["preprocess"]["height"]
        }
    
    if "generate_pattern" in steps:
        status["steps"]["generate_pattern"] = {
            "completed": True,
            "pattern_id": steps["generate_pattern"]["pattern_id"],
            "viz_url": steps["generate_pattern"]["viz_url"],
            "viz_url_no_labels": steps["generate_pattern"].get("viz_url_no_labels", steps["generate_pattern"]["viz_url"])
        }
    
    if "generate_render" in steps:
        status["steps"]["generate_render"] = {
            "completed": True,
            "render_url": steps["generate_render"]["render_url"],
            "pattern_id": steps["generate_render"]["pattern_id"]
        }
    
    return status


@app.post("/api/process")
async def process_image(
    file_id: str = Form(...),
    max_dimension: int = Form(100),
    target_colors: int = Form(20),
    use_custom: bool = Form(True),
    denoise_strength: float = Form(0.5),
    contrast_factor: float = Form(1.2),
    sharpness_factor: float = Form(1.1),
    use_nano_banana: bool = Form(False),
    nano_banana_prompt: str = Form("像素艺术风格，一格一格的色块，清晰的像素点阵，无网格线，纯色块拼接，像素化处理，马赛克风格，8位像素艺术，移除所有背景，移除所有文字和字幕，只保留角色主体，角色抠图，纯白色背景，小尺寸像素图，控制在有限像素内尽可能还原角色细节，适合拼豆制作的小尺寸像素艺术"),
    nano_banana_model: str = Form("nano-banana-fast"),
    nano_banana_image_size: str = Form("1K")
):
    """
    处理图像生成拼豆图案（旧API，保持向后兼容）
    """
    try:
        # 查找上传的文件
        image_files = list(Path("static/images").glob(f"{file_id}.*"))
        if not image_files:
            raise HTTPException(status_code=404, detail="图像文件不存在")
        
        image_path = str(image_files[0])
        file_info = uploaded_files.get(file_id, {})
        original_width = file_info.get("width", 0)
        original_height = file_info.get("height", 0)
        
        # 调试日志：检查参数和客户端状态
        logger.info(f"处理参数 - use_nano_banana: {use_nano_banana}, nano_banana_client: {nano_banana_client is not None}")
        logger.info(f"Nano Banana参数 - prompt: {nano_banana_prompt}, model: {nano_banana_model}, image_size: {nano_banana_image_size}")
        
        # 如果启用Nano Banana，先调用API转换图片
        if use_nano_banana:
            if not nano_banana_client:
                logger.warning("Nano Banana已启用，但客户端未配置，请先配置API")
            else:
                try:
                    logger.info("开始调用Nano Banana API转换图片...")
                    
                    # 计算aspectRatio
                    if original_width > 0 and original_height > 0:
                        aspect_ratio = calculate_aspect_ratio(original_width, original_height)
                    else:
                        aspect_ratio = "auto"
                    
                    # 调用Nano Banana API
                    # 使用本地图片路径，客户端会自动转换为Base64
                    result = nano_banana_client.generate_image(
                        prompt=nano_banana_prompt,
                        image_path=image_path,  # 使用本地路径，会自动转换为Base64
                        model=nano_banana_model,
                        aspect_ratio=aspect_ratio,
                        image_size=nano_banana_image_size,
                        max_dimension=max_dimension,
                        timeout=300  # 5分钟超时
                    )
                    
                    # 下载生成的图片
                    if result.get("results") and len(result["results"]) > 0:
                        generated_image_url = result["results"][0]["url"]
                        nano_banana_file_id = str(uuid.uuid4())
                        downloaded_path = nano_banana_client.download_image(
                            generated_image_url,
                            save_path=f"static/images/nano_banana_{nano_banana_file_id}.png"
                        )
                        
                        # 使用生成的图片
                        image_path = downloaded_path
                        logger.info(f"Nano Banana转换完成，图片已保存到: {downloaded_path}")
                    else:
                        logger.warning("Nano Banana API未返回图片，使用原始图片")
                except Exception as e:
                    logger.error(f"Nano Banana API调用失败: {str(e)}")
                    logger.warning("将使用原始图片继续处理")
                    # 继续使用原始图片
        else:
            logger.info("未启用Nano Banana，使用原始图片处理")
        
        # 加载图像
        image_processor.load_image(image_path)
        
        # 获取图像数组
        image_array = image_processor.get_image_array()
        
        # 应用优化（基于主体尺寸，排除背景）
        optimized_image, (new_width, new_height) = pattern_optimizer.apply_full_optimization(
            image_array,
            target_colors=target_colors,
            max_dimension=max_dimension,
            denoise_strength=denoise_strength,
            contrast_factor=contrast_factor,
            sharpness_factor=sharpness_factor,
            use_custom=use_custom,
            based_on_subject=True,  # 基于主体尺寸计算
            background_rgb=(255, 255, 255),  # 白色背景
            threshold=5  # 颜色判断阈值
        )
        
        # 颜色匹配（使用CIE94算法提高准确性）
        matched_colors = color_matcher.match_image_colors(optimized_image, use_custom=use_custom, method="cie94")
        
        # 生成拼豆图案
        bead_pattern = BeadPattern(new_width, new_height)
        bead_pattern.from_matched_colors(matched_colors)
        
        # 保存图案
        pattern_id = str(uuid.uuid4())
        patterns_store[pattern_id] = {
            "pattern": bead_pattern,
            "file_id": file_id,
            "params": {
                "max_dimension": max_dimension,
                "target_colors": target_colors,
                "use_custom": use_custom
            }
        }
        
        # 生成可视化图像（显示编号和不显示编号两个版本）
        viz_image_with_labels = bead_pattern.to_image(cell_size=10, show_labels=True, show_grid=True)
        viz_path_with_labels = f"static/output/{pattern_id}_viz.png"
        viz_image_with_labels.save(viz_path_with_labels)
        
        # 生成不显示编号的版本（用于生成实物效果图）
        viz_image_no_labels = bead_pattern.to_image(cell_size=10, show_labels=False, show_grid=True)
        viz_path_no_labels = f"static/output/{pattern_id}_viz_no_labels.png"
        viz_image_no_labels.save(viz_path_no_labels)
        
        # 获取统计信息（包含主体尺寸）
        stats = bead_pattern.get_color_statistics(exclude_background=False)
        stats_without_bg = bead_pattern.get_color_statistics(exclude_background=True)
        subject_size = bead_pattern.get_subject_size()
        
        return {
            "pattern_id": pattern_id,
            "width": new_width,
            "height": new_height,
            "actual_width_mm": bead_pattern.actual_width_mm,
            "actual_height_mm": bead_pattern.actual_height_mm,
            "subject_width": subject_size['subject_width'],
            "subject_height": subject_size['subject_height'],
            "subject_width_mm": subject_size['subject_width_mm'],
            "subject_height_mm": subject_size['subject_height_mm'],
            "statistics": stats,
            "subject_statistics": stats_without_bg,
            "viz_url": f"/static/output/{pattern_id}_viz.png",
            "viz_url_no_labels": f"/static/output/{pattern_id}_viz_no_labels.png"
        }
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        logger.error(f"处理图像失败: {error_msg}")
        logger.error(f"详细错误:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"处理失败: {error_msg}")


@app.get("/api/pattern/{pattern_id}")
async def get_pattern(pattern_id: str):
    """
    获取生成的图案数据
    """
    if pattern_id not in patterns_store:
        raise HTTPException(status_code=404, detail="图案不存在")
    
    pattern = patterns_store[pattern_id]["pattern"]
    return pattern.to_dict()


@app.post("/api/optimize")
async def optimize_pattern(
    pattern_id: str = Form(...),
    max_dimension: int = Form(100),
    target_colors: int = Form(20),
    denoise_strength: float = Form(0.5),
    contrast_factor: float = Form(1.2),
    sharpness_factor: float = Form(1.1)
):
    """
    优化已生成的图案
    """
    if pattern_id not in patterns_store:
        raise HTTPException(status_code=404, detail="图案不存在")
    
    # 获取原始图像
    stored_data = patterns_store[pattern_id]
    file_id = stored_data["file_id"]
    
    # 重新处理（简化：重新加载和优化）
    # 实际应用中可能需要保存原始图像数组
    raise HTTPException(status_code=501, detail="优化功能待实现")


@app.get("/api/colors")
async def get_colors(include_custom: bool = True):
    """
    获取色板列表
    """
    colors = color_matcher.get_all_colors(include_custom=include_custom)
    return {"colors": colors}


@app.post("/api/colors/custom")
async def add_custom_color(color: CustomColor):
    """
    添加自定义颜色
    """
    try:
        new_color = color_matcher.add_custom_color(
            color.name_zh,
            color.name_en,
            color.code,
            color.rgb,
            color.category
        )
        return new_color
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"添加失败: {str(e)}")


@app.delete("/api/colors/custom/{color_id}")
async def delete_custom_color(color_id: int):
    """
    删除自定义颜色
    """
    success = color_matcher.remove_custom_color(color_id)
    if not success:
        raise HTTPException(status_code=404, detail="颜色不存在")
    return {"success": True}


@app.get("/api/colors/custom/export")
async def export_custom_colors(format: str = "csv"):
    """
    导出自定义颜色
    
    Args:
        format: 导出格式 ('csv' 或 'json')
    """
    if format not in ['csv', 'json']:
        raise HTTPException(status_code=400, detail="不支持的导出格式，支持: csv, json")
    
    import uuid
    from pathlib import Path
    
    # 生成临时文件
    file_id = str(uuid.uuid4())
    
    if format == 'csv':
        file_path = f"static/output/custom_colors_{file_id}.csv"
        color_matcher.export_custom_colors_csv(file_path)
        media_type = "text/csv"
        filename = f"custom_colors_{file_id}.csv"
    else:  # json
        file_path = f"static/output/custom_colors_{file_id}.json"
        color_matcher.export_custom_colors_json(file_path)
        media_type = "application/json"
        filename = f"custom_colors_{file_id}.json"
    
    if not Path(file_path).exists():
        raise HTTPException(status_code=500, detail="导出失败")
    
    return FileResponse(
        file_path,
        media_type=media_type,
        filename=filename
    )


@app.post("/api/colors/custom/import")
async def import_custom_colors(
    file: UploadFile = File(...),
    format: str = Form("auto"),
    replace: bool = Form(False)
):
    """
    导入自定义颜色
    
    Args:
        file: 上传的文件
        format: 文件格式 ('csv', 'json', 'auto' 自动检测)
        replace: 是否替换现有颜色
    """
    # 自动检测格式
    if format == "auto":
        filename = file.filename.lower()
        if filename.endswith('.csv'):
            format = 'csv'
        elif filename.endswith('.json'):
            format = 'json'
        else:
            raise HTTPException(status_code=400, detail="无法自动检测文件格式，请指定 format 参数")
    
    if format not in ['csv', 'json']:
        raise HTTPException(status_code=400, detail="不支持的导入格式，支持: csv, json")
    
    import tempfile
    import os
    
    # 保存上传的文件到临时位置
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # 导入颜色
        if format == 'csv':
            result = color_matcher.import_custom_colors_csv(tmp_path, replace=replace)
        else:  # json
            result = color_matcher.import_custom_colors_json(tmp_path, replace=replace)
        
        # 清理临时文件
        os.unlink(tmp_path)
        
        if not result['success']:
            error_msg = "导入失败"
            if result.get('errors'):
                error_msg += ": " + "; ".join(result['errors'][:5])  # 只显示前5个错误
            raise HTTPException(status_code=400, detail=error_msg)
        
        return {
            "success": True,
            "imported": result['imported'],
            "errors": result.get('errors', []),
            "message": f"成功导入 {result['imported']} 种颜色"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # 清理临时文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@app.post("/api/pattern/{pattern_id}/print")
async def generate_print(
    pattern_id: str,
    params: PrintParams
):
    """
    生成打印文件
    """
    if pattern_id not in patterns_store:
        raise HTTPException(status_code=404, detail="图案不存在")
    
    pattern = patterns_store[pattern_id]["pattern"]
    
    # 生成PDF
    pdf_path = f"static/output/{pattern_id}_print.pdf"
    printer.generate_pdf(
        pattern,
        pdf_path,
        paper_size=params.paper_size,
        margin_mm=params.margin_mm,
        show_grid=params.show_grid,
        show_labels=params.show_labels,
        dpi=params.dpi
    )
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"pattern_{pattern_id}.pdf"
    )


@app.get("/api/pattern/{pattern_id}/export")
async def export_pattern(pattern_id: str, format: str = "json"):
    """
    导出图案
    """
    if pattern_id not in patterns_store:
        raise HTTPException(status_code=404, detail="图案不存在")
    
    pattern = patterns_store[pattern_id]["pattern"]
    
    if format == "json":
        json_path = f"static/output/{pattern_id}.json"
        pattern.to_json(json_path)
        return FileResponse(json_path, media_type="application/json",
                          filename=f"pattern_{pattern_id}.json")
    elif format == "csv":
        csv_path = f"static/output/{pattern_id}.csv"
        pattern.to_csv(csv_path)
        return FileResponse(csv_path, media_type="text/csv",
                          filename=f"pattern_{pattern_id}.csv")
    elif format == "png":
        png_path = f"static/output/{pattern_id}_export.png"
        pattern.save_image(png_path, cell_size=20, show_labels=True, show_grid=True)
        return FileResponse(png_path, media_type="image/png",
                          filename=f"pattern_{pattern_id}.png")
    else:
        raise HTTPException(status_code=400, detail="不支持的导出格式")


@app.get("/api/pattern/{pattern_id}/print-preview")
async def print_preview(
    pattern_id: str,
    paper_size: str = "A4",
    margin_mm: float = 10.0,
    show_grid: bool = True,
    show_labels: bool = False
):
    """
    打印预览
    """
    if pattern_id not in patterns_store:
        raise HTTPException(status_code=404, detail="图案不存在")
    
    pattern = patterns_store[pattern_id]["pattern"]
    
    # 生成预览图像
    preview_image = printer.generate_print_image(
        pattern,
        paper_size=paper_size,
        margin_mm=margin_mm,
        show_grid=show_grid,
        show_labels=show_labels
    )
    
    preview_path = f"static/output/{pattern_id}_preview.png"
    preview_image.save(preview_path)
    
    return FileResponse(preview_path, media_type="image/png")


@app.post("/api/step/generate-render")
async def step_generate_render(
    file_id: str = Form(...),
    pattern_id: str = Form(None),
    prompt: str = Form("拼豆实物效果图，真实的拼豆工艺品，近距离拍摄，高清晰度，专业摄影，自然光线"),
    model: str = Form("nano-banana-fast"),
    image_size: str = Form("1K")
):
    """
    步骤4: 生成实物效果图（使用Nano Banana）
    """
    try:
        if not nano_banana_client:
            raise HTTPException(status_code=400, detail="请先配置Nano Banana API")
        
        # 确定使用的pattern_id
        if not pattern_id:
            # 从步骤结果中获取pattern_id
            if file_id not in step_results or "generate_pattern" not in step_results[file_id]:
                raise HTTPException(status_code=400, detail="请先生成拼豆图案")
            pattern_id = step_results[file_id]["generate_pattern"]["pattern_id"]
        
        # 检查图案是否存在
        if pattern_id not in patterns_store:
            raise HTTPException(status_code=404, detail="图案不存在")
        
        # 获取图案的可视化图片路径（使用不显示编号的版本）
        viz_path = f"static/output/{pattern_id}_viz_no_labels.png"
        if not Path(viz_path).exists():
            # 如果可视化图片不存在，重新生成（不显示编号的版本）
            pattern = patterns_store[pattern_id]["pattern"]
            viz_image = pattern.to_image(cell_size=10, show_labels=False, show_grid=True)
            viz_image.save(viz_path)
        
        # 计算aspectRatio（基于图案尺寸）
        pattern = patterns_store[pattern_id]["pattern"]
        aspect_ratio = calculate_aspect_ratio(pattern.width, pattern.height)
        
        logger.info(f"开始生成实物效果图: pattern_id={pattern_id}, prompt={prompt}")
        
        # 调用Nano Banana API生成实物效果图
        result = nano_banana_client.generate_image(
            prompt=prompt,
            image_path=viz_path,  # 使用拼豆图案的可视化图片作为参考
            model=model,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            timeout=300  # 5分钟超时
        )
        
        # 下载生成的图片
        if result.get("results") and len(result["results"]) > 0:
            generated_image_url = result["results"][0]["url"]
            render_file_id = str(uuid.uuid4())
            downloaded_path = nano_banana_client.download_image(
                generated_image_url,
                save_path=f"static/output/render_{render_file_id}.png"
            )
            
            # 保存步骤结果
            if file_id not in step_results:
                step_results[file_id] = {}
            step_results[file_id]["generate_render"] = {
                "render_url": f"/static/output/render_{render_file_id}.png",
                "file_id": render_file_id,
                "pattern_id": pattern_id,
                "params": {
                    "prompt": prompt,
                    "model": model,
                    "image_size": image_size
                }
            }
            
            logger.info(f"实物效果图生成完成: {downloaded_path}")
            
            return {
                "success": True,
                "render_url": f"/static/output/render_{render_file_id}.png",
                "file_id": render_file_id,
                "pattern_id": pattern_id
            }
        else:
            raise HTTPException(status_code=500, detail="Nano Banana API未返回图片")
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        logger.error(f"实物效果图生成失败: {error_msg}")
        logger.error(f"详细错误:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"生成失败: {error_msg}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


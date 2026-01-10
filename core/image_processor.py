"""
图像处理模块
负责图像的加载、格式转换、缩放、裁剪和预处理
"""
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
from typing import Tuple, Optional


class ImageProcessor:
    """图像处理器"""
    
    def __init__(self):
        self.current_image: Optional[Image.Image] = None
        self.processed_image: Optional[Image.Image] = None
    
    def load_image(self, image_path: str) -> Image.Image:
        """
        加载图像
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            PIL Image对象
        """
        self.current_image = Image.open(image_path)
        # 转换为RGB模式（如果是RGBA，先转换为RGB）
        if self.current_image.mode != 'RGB':
            if self.current_image.mode == 'RGBA':
                # 创建白色背景
                background = Image.new('RGB', self.current_image.size, (255, 255, 255))
                background.paste(self.current_image, mask=self.current_image.split()[3])
                self.current_image = background
            else:
                self.current_image = self.current_image.convert('RGB')
        return self.current_image
    
    def resize_image(self, size: Tuple[int, int], resample: int = Image.LANCZOS) -> Image.Image:
        """
        调整图像尺寸
        
        Args:
            size: 目标尺寸 (width, height)
            resample: 重采样方法
            
        Returns:
            调整后的图像
        """
        if self.current_image is None:
            raise ValueError("请先加载图像")
        self.processed_image = self.current_image.resize(size, resample)
        return self.processed_image
    
    def resize_by_max_dimension(self, max_dimension: int) -> Image.Image:
        """
        按最大尺寸等比例缩放
        
        Args:
            max_dimension: 最大尺寸（宽或高的最大值）
            
        Returns:
            缩放后的图像
        """
        if self.current_image is None:
            raise ValueError("请先加载图像")
        
        width, height = self.current_image.size
        if width > height:
            new_width = max_dimension
            new_height = int(height * max_dimension / width)
        else:
            new_height = max_dimension
            new_width = int(width * max_dimension / height)
        
        return self.resize_image((new_width, new_height))
    
    def crop_image(self, box: Tuple[int, int, int, int]) -> Image.Image:
        """
        裁剪图像
        
        Args:
            box: 裁剪区域 (left, top, right, bottom)
            
        Returns:
            裁剪后的图像
        """
        if self.current_image is None:
            raise ValueError("请先加载图像")
        self.processed_image = self.current_image.crop(box)
        return self.processed_image
    
    def apply_noise_reduction(self, strength: float = 0.5) -> Image.Image:
        """
        应用降噪
        
        Args:
            strength: 降噪强度 (0.0 - 1.0)
            
        Returns:
            处理后的图像
        """
        if self.current_image is None:
            raise ValueError("请先加载图像")
        
        image = self.current_image if self.processed_image is None else self.processed_image
        
        # 使用平滑滤波器
        if strength > 0.5:
            image = image.filter(ImageFilter.SMOOTH_MORE)
        else:
            image = image.filter(ImageFilter.SMOOTH)
        
        self.processed_image = image
        return self.processed_image
    
    def enhance_contrast(self, factor: float = 1.2) -> Image.Image:
        """
        增强对比度
        
        Args:
            factor: 对比度因子 (>1.0 增强, <1.0 降低)
            
        Returns:
            处理后的图像
        """
        if self.current_image is None:
            raise ValueError("请先加载图像")
        
        image = self.current_image if self.processed_image is None else self.processed_image
        enhancer = ImageEnhance.Contrast(image)
        self.processed_image = enhancer.enhance(factor)
        return self.processed_image
    
    def enhance_sharpness(self, factor: float = 1.2) -> Image.Image:
        """
        增强锐度
        
        Args:
            factor: 锐度因子 (>1.0 增强, <1.0 降低)
            
        Returns:
            处理后的图像
        """
        if self.current_image is None:
            raise ValueError("请先加载图像")
        
        image = self.current_image if self.processed_image is None else self.processed_image
        enhancer = ImageEnhance.Sharpness(image)
        self.processed_image = enhancer.enhance(factor)
        return self.processed_image
    
    def get_image_array(self) -> np.ndarray:
        """
        获取图像数组
        
        Returns:
            numpy数组 (height, width, 3)，uint8类型
        """
        image = self.processed_image if self.processed_image is not None else self.current_image
        if image is None:
            raise ValueError("请先加载图像")
        # 确保返回uint8类型的数组
        arr = np.array(image)
        if arr.dtype != np.uint8:
            arr = arr.astype(np.uint8)
        # 确保值在有效范围内
        arr = np.clip(arr, 0, 255).astype(np.uint8)
        return arr
    
    def get_image_size(self) -> Tuple[int, int]:
        """
        获取图像尺寸
        
        Returns:
            (width, height)
        """
        image = self.processed_image if self.processed_image is not None else self.current_image
        if image is None:
            raise ValueError("请先加载图像")
        return image.size
    
    def save_image(self, output_path: str) -> None:
        """
        保存图像
        
        Args:
            output_path: 输出路径
        """
        image = self.processed_image if self.processed_image is not None else self.current_image
        if image is None:
            raise ValueError("没有可保存的图像")
        image.save(output_path)
    
    def get_subject_bounds(self, background_rgb: Tuple[int, int, int] = (255, 255, 255), 
                          threshold: int = 5) -> Tuple[int, int, int, int]:
        """
        检测图像中主体部分的边界（排除背景）
        
        Args:
            background_rgb: 背景RGB颜色，默认为白色 (255, 255, 255)
            threshold: 颜色判断阈值，RGB差值小于此值认为是背景
            
        Returns:
            主体边界 (min_x, min_y, max_x, max_y)，如果未找到主体则返回None
        """
        if self.current_image is None:
            raise ValueError("请先加载图像")
        
        image = self.current_image if self.processed_image is None else self.processed_image
        arr = np.array(image)
        
        if arr.dtype != np.uint8:
            arr = arr.astype(np.uint8)
        arr = np.clip(arr, 0, 255).astype(np.uint8)
        
        height, width = arr.shape[:2]
        
        # 检测非背景像素
        bg_mask = np.all(np.abs(arr - np.array(background_rgb)) < threshold, axis=2)
        non_bg_mask = ~bg_mask
        
        # 找到主体边界
        if not np.any(non_bg_mask):
            # 没有找到非背景像素，返回整个图像
            return (0, 0, width, height)
        
        # 找到非背景像素的行和列
        rows = np.where(non_bg_mask.any(axis=1))[0]
        cols = np.where(non_bg_mask.any(axis=0))[0]
        
        if len(rows) == 0 or len(cols) == 0:
            return (0, 0, width, height)
        
        min_y = int(rows[0])
        max_y = int(rows[-1]) + 1
        min_x = int(cols[0])
        max_x = int(cols[-1]) + 1
        
        return (min_x, min_y, max_x, max_y)
    
    def resize_by_subject_max_dimension(self, max_dimension: int, 
                                       background_rgb: Tuple[int, int, int] = (255, 255, 255),
                                       threshold: int = 5) -> Image.Image:
        """
        根据主体部分的最大尺寸进行缩放（排除背景）
        
        Args:
            max_dimension: 主体部分的最大尺寸（宽或高的最大值）
            background_rgb: 背景RGB颜色，默认为白色 (255, 255, 255)
            threshold: 颜色判断阈值
            
        Returns:
            缩放后的图像
        """
        if self.current_image is None:
            raise ValueError("请先加载图像")
        
        # 检测主体边界
        bounds = self.get_subject_bounds(background_rgb, threshold)
        min_x, min_y, max_x, max_y = bounds
        
        # 计算主体尺寸
        subject_width = max_x - min_x
        subject_height = max_y - min_y
        
        if subject_width == 0 or subject_height == 0:
            # 没有找到主体，按整个图像缩放
            return self.resize_by_max_dimension(max_dimension)
        
        # 计算主体需要的缩放比例
        if subject_width > subject_height:
            subject_scale = max_dimension / subject_width
        else:
            subject_scale = max_dimension / subject_height
        
        # 获取原始图像尺寸
        original_image = self.current_image if self.processed_image is None else self.processed_image
        original_width, original_height = original_image.size
        
        # 计算整个图像的新尺寸
        new_width = int(original_width * subject_scale)
        new_height = int(original_height * subject_scale)
        
        # 缩放整个图像
        return self.resize_image((new_width, new_height))


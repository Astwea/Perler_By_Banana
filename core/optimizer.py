"""
图案优化模块
负责颜色数量优化、尺寸优化、图像质量优化和图案简化
"""
import numpy as np
from typing import Tuple, Optional, List
from PIL import Image, ImageFilter, ImageEnhance
from sklearn.cluster import KMeans
from core.color_matcher import ColorMatcher


class PatternOptimizer:
    """图案优化器"""
    
    def __init__(self, color_matcher: ColorMatcher):
        """
        初始化优化器
        
        Args:
            color_matcher: 颜色匹配器实例
        """
        self.color_matcher = color_matcher
    
    def optimize_color_count(self, image_array: np.ndarray, target_colors: int = 20,
                           use_custom: bool = True) -> np.ndarray:
        """
        优化颜色数量（使用K-means聚类减少颜色）
        
        Args:
            image_array: 图像数组 (height, width, 3)
            target_colors: 目标颜色数量
            use_custom: 是否使用自定义色板
            
        Returns:
            优化后的图像数组
        """
        height, width = image_array.shape[:2]
        
        # 确保数组类型正确
        if image_array.dtype != np.uint8:
            image_array = image_array.astype(np.uint8)
        
        # 将图像重塑为2D数组
        pixels = image_array.reshape(-1, 3)
        
        # 确保至少有一个像素
        if len(pixels) == 0:
            return image_array
        
        # 使用K-means聚类（确保聚类数不超过像素数）
        n_clusters = min(target_colors, len(pixels))
        if n_clusters < 1:
            n_clusters = 1
        
        # 性能优化：对大量像素进行采样，只对采样后的像素进行聚类
        # 对于大图像（>50万像素），采样到最多10万像素
        # 确保采样数不少于聚类数，避免KMeans n_samples < n_clusters
        max_sample_size = max(100000, n_clusters)
        if len(pixels) > max_sample_size:
            # 随机采样
            sample_indices = np.random.choice(len(pixels), max_sample_size, replace=False)
            sample_pixels = pixels[sample_indices]
        else:
            sample_pixels = pixels
            sample_indices = None
        
        # 使用K-means聚类，减少n_init以提高速度
        # n_init=1 或 3：减少初始化次数，加快速度
        # max_iter=100：限制最大迭代次数
        # tol=1e-4：收敛阈值，稍微放宽以提高速度
        n_init_value = 1 if n_clusters <= 10 else 3  # 小聚类数用1次初始化，大聚类数用3次
        
        kmeans = KMeans(n_clusters=n_clusters, 
                       random_state=42, 
                       n_init=n_init_value,
                       max_iter=100,
                       tol=1e-4)
        kmeans.fit(sample_pixels)
        
        # 获取聚类中心
        centers = kmeans.cluster_centers_.astype(np.uint8)
        
        # 对原始所有像素进行预测（只预测，不重新训练）
        # 使用批量预测以提高速度
        labels = kmeans.predict(pixels)
        
        # 将每个像素替换为对应的聚类中心
        optimized_pixels = centers[labels]
        
        # 重塑回原始形状
        optimized_image = optimized_pixels.reshape(height, width, 3)
        
        return optimized_image
    
    def optimize_dimensions(self, width: int, height: int, 
                          max_dimension: int = 100,
                          based_on_subject: bool = True,
                          image_array: Optional[np.ndarray] = None,
                          background_rgb: Tuple[int, int, int] = (255, 255, 255),
                          threshold: int = 5) -> Tuple[int, int]:
        """
        优化图案尺寸（确保不超过最大尺寸）
        
        Args:
            width: 原始宽度
            height: 原始高度
            max_dimension: 最大尺寸（宽或高的最大值）
            based_on_subject: 是否基于主体尺寸计算（排除背景）
            image_array: 图像数组（当based_on_subject=True时需要）
            background_rgb: 背景RGB颜色（当based_on_subject=True时需要）
            threshold: 颜色判断阈值
            
        Returns:
            优化后的尺寸 (width, height)
        """
        # 如果基于主体尺寸，先检测主体
        if based_on_subject and image_array is not None:
            # 检测主体边界
            height_arr, width_arr = image_array.shape[:2]
            bg_mask = np.all(np.abs(image_array - np.array(background_rgb)) < threshold, axis=2)
            non_bg_mask = ~bg_mask
            
            if np.any(non_bg_mask):
                # 找到非背景像素的行和列
                rows = np.where(non_bg_mask.any(axis=1))[0]
                cols = np.where(non_bg_mask.any(axis=0))[0]
                
                if len(rows) > 0 and len(cols) > 0:
                    subject_height = int(rows[-1]) - int(rows[0]) + 1
                    subject_width = int(cols[-1]) - int(cols[0]) + 1
                    
                    # 检查主体尺寸是否超过限制
                    if subject_width <= max_dimension and subject_height <= max_dimension:
                        return width, height
                    
                    # 根据主体尺寸计算缩放比例
                    if subject_width > subject_height:
                        subject_scale = max_dimension / subject_width
                    else:
                        subject_scale = max_dimension / subject_height
                    
                    # 计算整个图像的新尺寸
                    new_width = int(width * subject_scale)
                    new_height = int(height * subject_scale)
                    return new_width, new_height
        
        # 如果不基于主体，或未找到主体，按整个图像缩放
        if width <= max_dimension and height <= max_dimension:
            return width, height
        
        # 等比例缩放
        if width > height:
            new_width = max_dimension
            new_height = int(height * max_dimension / width)
        else:
            new_height = max_dimension
            new_width = int(width * max_dimension / height)
        
        return new_width, new_height
    
    def optimize_quality(self, image_array: np.ndarray, 
                        denoise_strength: float = 0.5,
                        contrast_factor: float = 1.2,
                        sharpness_factor: float = 1.1) -> np.ndarray:
        """
        优化图像质量
        
        Args:
            image_array: 图像数组 (height, width, 3)
            denoise_strength: 降噪强度 (0.0 - 1.0)
            contrast_factor: 对比度因子 (>1.0 增强)
            sharpness_factor: 锐度因子 (>1.0 增强)
            
        Returns:
            优化后的图像数组
        """
        # 确保数组类型正确
        if image_array.dtype != np.uint8:
            image_array = image_array.astype(np.uint8)
        
        # 确保数组值在有效范围内
        image_array = np.clip(image_array, 0, 255).astype(np.uint8)
        
        # 转换为PIL Image
        image = Image.fromarray(image_array)
        
        # 降噪
        if denoise_strength > 0:
            if denoise_strength > 0.5:
                image = image.filter(ImageFilter.SMOOTH_MORE)
            else:
                image = image.filter(ImageFilter.SMOOTH)
        
        # 增强对比度
        if contrast_factor != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast_factor)
        
        # 增强锐度
        if sharpness_factor != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(sharpness_factor)
        
        # 转换回numpy数组
        return np.array(image)
    
    def simplify_pattern(self, matched_colors: np.ndarray, 
                        similarity_threshold: float = 10.0) -> np.ndarray:
        """
        简化图案（合并相似颜色）
        
        Args:
            matched_colors: 已匹配的颜色数组（从color_matcher.match_image_colors获得）
            similarity_threshold: 相似度阈值（色差小于此值的颜色将被合并）
            
        Returns:
            简化后的颜色数组
        """
        height, width = matched_colors.shape[:2]
        simplified = np.copy(matched_colors)
        
        # 获取所有唯一的颜色
        unique_colors = {}
        color_groups = []
        
        for y in range(height):
            for x in range(width):
                color = matched_colors[y, x]
                color_id = color['id']
                
                # 查找相似的颜色组
                added_to_group = False
                for group in color_groups:
                    group_color = group[0]
                    if color.get('distance', 0) < similarity_threshold:
                        # 检查是否与组内颜色相似
                        for gc in group:
                            if abs(color_id - gc['id']) == 0:
                                added_to_group = True
                                group.append(color)
                                break
                        if added_to_group:
                            break
                
                if not added_to_group:
                    color_groups.append([color])
        
        # 使用组内最常见的颜色替换
        for group in color_groups:
            if len(group) > 1:
                # 选择组内距离最小的颜色
                best_color = min(group, key=lambda c: c.get('distance', float('inf')))
                for color in group[1:]:
                    # 找到并替换所有使用该颜色的位置
                    for y in range(height):
                        for x in range(width):
                            if simplified[y, x]['id'] == color['id']:
                                simplified[y, x] = best_color
        
        return simplified
    
    def apply_full_optimization(self, image_array: np.ndarray,
                               target_colors: int = 20,
                               max_dimension: int = 100,
                               denoise_strength: float = 0.5,
                               contrast_factor: float = 1.2,
                               sharpness_factor: float = 1.1,
                               use_custom: bool = True,
                               based_on_subject: bool = True,
                               background_rgb: Tuple[int, int, int] = (255, 255, 255),
                               threshold: int = 5) -> Tuple[np.ndarray, Tuple[int, int]]:
        """
        应用完整的优化流程
        
        Args:
            image_array: 图像数组
            target_colors: 目标颜色数量
            max_dimension: 最大尺寸（基于主体部分）
            denoise_strength: 降噪强度
            contrast_factor: 对比度因子
            sharpness_factor: 锐度因子
            use_custom: 是否使用自定义色板
            based_on_subject: 是否基于主体尺寸计算（排除背景）
            background_rgb: 背景RGB颜色
            threshold: 颜色判断阈值
            
        Returns:
            (优化后的图像数组, 优化后的尺寸)
        """
        # 1. 质量优化
        optimized = self.optimize_quality(image_array, denoise_strength, 
                                         contrast_factor, sharpness_factor)
        
        # 2. 颜色数量优化
        if target_colors > 0:
            optimized = self.optimize_color_count(optimized, target_colors, use_custom)
        
        # 3. 尺寸优化（基于主体部分）
        height, width = optimized.shape[:2]
        new_width, new_height = self.optimize_dimensions(
            width, height, max_dimension, 
            based_on_subject=based_on_subject,
            image_array=optimized if based_on_subject else None,
            background_rgb=background_rgb,
            threshold=threshold
        )
        
        # 如果需要调整尺寸
        if new_width != width or new_height != height:
            from PIL import Image
            # 确保数组类型正确
            if optimized.dtype != np.uint8:
                optimized = optimized.astype(np.uint8)
            optimized = np.clip(optimized, 0, 255).astype(np.uint8)
            img = Image.fromarray(optimized)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            optimized = np.array(img)
        
        return optimized, (new_width, new_height)

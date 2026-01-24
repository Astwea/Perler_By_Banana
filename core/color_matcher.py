"""
颜色匹配模块
负责颜色空间转换、颜色距离计算和像素到拼豆颜色的匹配
"""
import json
import os
import csv
import numpy as np
from typing import List, Dict, Tuple, Optional
from skimage.color import rgb2lab, deltaE_cie76

# 尝试导入更精确的色差算法
try:
    from skimage.color import deltaE_cie94
    HAS_CIE94 = True
except ImportError:
    HAS_CIE94 = False

try:
    from skimage.color import deltaE_ciede2000
    HAS_CIE2000 = True
except ImportError:
    HAS_CIE2000 = False


class ColorMatcher:
    """颜色匹配器"""
    
    def __init__(self, standard_colors_path: str = "data/standard_colors.json",
                 custom_colors_path: str = "data/custom_colors.json"):
        """
        初始化颜色匹配器
        
        Args:
            standard_colors_path: 标准色板文件路径
            custom_colors_path: 自定义色板文件路径
        """
        self.standard_colors_path = standard_colors_path
        self.custom_colors_path = custom_colors_path
        self.standard_colors: List[Dict] = []
        self.custom_colors: List[Dict] = []
        self.all_colors: List[Dict] = []
        self.color_lab_cache: Optional[np.ndarray] = None
        
        self.load_colors()
    
    def load_colors(self) -> None:
        """加载色板"""
        # 加载标准色板
        if os.path.exists(self.standard_colors_path):
            with open(self.standard_colors_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.standard_colors = data.get('colors', [])
        
        # 加载自定义色板
        if os.path.exists(self.custom_colors_path):
            with open(self.custom_colors_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.custom_colors = data.get('colors', [])
        
        # 合并所有颜色
        self._update_all_colors()
        self._update_lab_cache()
    
    def _update_all_colors(self) -> None:
        """更新所有颜色列表"""
        self.all_colors = self.standard_colors + self.custom_colors
    
    def _update_lab_cache(self) -> None:
        """更新LAB颜色空间缓存"""
        if not self.all_colors:
            self.color_lab_cache = None
            return
        
        rgb_array = np.array([[c['rgb'][0], c['rgb'][1], c['rgb'][2]] 
                              for c in self.all_colors], dtype=np.float32)
        # 归一化到0-1范围
        rgb_normalized = rgb_array / 255.0
        # 转换为LAB颜色空间
        self.color_lab_cache = rgb2lab(rgb_normalized)
    
    def add_custom_color(self, name_zh: str, name_en: str, code: str, 
                        rgb: List[int], category: str = "自定义") -> Dict:
        """
        添加自定义颜色
        
        Args:
            name_zh: 中文名称
            name_en: 英文名称
            code: 色号代码
            rgb: RGB值 [r, g, b]
            category: 颜色分类
            
        Returns:
            添加的颜色字典
        """
        # 生成新ID
        max_id = max([c.get('id', 0) for c in self.custom_colors], default=1000)
        new_id = max_id + 1
        
        new_color = {
            'id': new_id,
            'name_zh': name_zh,
            'name_en': name_en,
            'code': code,
            'rgb': rgb,
            'category': category
        }
        
        self.custom_colors.append(new_color)
        self._update_all_colors()
        self._update_lab_cache()
        self._save_custom_colors()
        
        return new_color
    
    def remove_custom_color(self, color_id: int) -> bool:
        """
        删除自定义颜色
        
        Args:
            color_id: 颜色ID
            
        Returns:
            是否删除成功
        """
        original_len = len(self.custom_colors)
        self.custom_colors = [c for c in self.custom_colors if c.get('id') != color_id]
        
        if len(self.custom_colors) < original_len:
            self._update_all_colors()
            self._update_lab_cache()
            self._save_custom_colors()
            return True
        return False
    
    def _save_custom_colors(self) -> None:
        """保存自定义色板到文件"""
        data = {
            'name': '用户自定义色板',
            'bead_size_mm': 5,
            'colors': self.custom_colors
        }
        
        os.makedirs(os.path.dirname(self.custom_colors_path), exist_ok=True)
        with open(self.custom_colors_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def match_color(self, rgb: Tuple[int, int, int], use_custom: bool = True) -> Dict:
        """
        匹配最接近的拼豆颜色
        
        Args:
            rgb: RGB值 (r, g, b)
            use_custom: 是否使用自定义色板
            
        Returns:
            最匹配的颜色字典和距离
        """
        if not self.all_colors:
            raise ValueError("色板为空，请先加载色板")
        
        # 选择使用的颜色列表
        colors_to_use = self.all_colors if use_custom else self.standard_colors
        if not colors_to_use:
            raise ValueError("没有可用的颜色")
        
        # 计算距离
        min_distance = float('inf')
        best_match = None
        best_index = -1
        
        # 转换为LAB颜色空间
        # rgb2lab需要形状为 (..., 3) 的数组，输入 (1, 3) 返回 (1, 3)
        rgb_normalized = np.array([[rgb[0], rgb[1], rgb[2]]], dtype=np.float32) / 255.0
        lab_pixel = rgb2lab(rgb_normalized)  # shape: (1, 3)
        
        # 在LAB颜色空间中计算距离
        for i, color in enumerate(colors_to_use):
            color_rgb = color['rgb']
            color_rgb_normalized = np.array([[color_rgb[0], color_rgb[1], color_rgb[2]]], 
                                            dtype=np.float32) / 255.0
            color_lab = rgb2lab(color_rgb_normalized)  # shape: (1, 3)
            
            # 使用CIE76色差公式
            # deltaE_cie76输入 (1, 3) 和 (1, 3)，返回 (1,) 数组或标量
            distance_result = deltaE_cie76(lab_pixel, color_lab)
            
            # 提取标量值
            if isinstance(distance_result, np.ndarray):
                if distance_result.size == 1:
                    distance = float(distance_result.item())
                else:
                    distance = float(distance_result.flat[0])
            else:
                distance = float(distance_result)
            
            if distance < min_distance:
                min_distance = distance
                best_match = color.copy()
                best_index = i
        
        result = best_match.copy()
        result['distance'] = min_distance
        return result
    
    def match_image_colors(self, image_array: np.ndarray, use_custom: bool = True,
                          method: str = "cie94", brand: Optional[str] = None,
                          series: Optional[str] = None,
                          match_mode: str = "nearest") -> np.ndarray:
        """
        匹配图像中所有像素的颜色（优化版本，使用向量化操作）
        
        Args:
            image_array: 图像数组 (height, width, 3)
            use_custom: 是否使用自定义色板
            method: 色差计算方法 ("cie76", "cie94", "cie2000")
            brand: 品牌名称（如"COCO"），如果为"自定义"则只使用自定义色板
            series: 系列名称（如"291"），需要与brand一起使用
            match_mode: 匹配模式 ("nearest", "detail", "dither_fs", "dither_atkinson")
            
        Returns:
            匹配结果数组，每个像素包含匹配的颜色信息
        """
        height, width = image_array.shape[:2]
        
        # 确保数组类型正确
        if image_array.dtype != np.uint8:
            image_array = image_array.astype(np.uint8)
        image_array = np.clip(image_array, 0, 255).astype(np.uint8)
        
        # 根据品牌和系列过滤颜色
        colors_to_use = self.get_all_colors(include_custom=use_custom, brand=brand, series=series)
        if not colors_to_use:
            raise ValueError(f"没有可用的颜色（品牌: {brand}, 系列: {series}）")
        
        # 为过滤后的颜色计算LAB颜色空间（因为过滤后的颜色列表可能不同）
        rgb_array = np.array([[c['rgb'][0], c['rgb'][1], c['rgb'][2]] 
                             for c in colors_to_use], dtype=np.float32)
        # 归一化到0-1范围
        rgb_normalized = rgb_array / 255.0
        # 转换为LAB颜色空间
        color_lab_cache = rgb2lab(rgb_normalized)
        color_indices = list(range(len(colors_to_use)))
        
        match_mode = (match_mode or "nearest").lower()
        if match_mode in ("dither_fs", "dither_atkinson"):
            return self._match_image_colors_dither(image_array, colors_to_use, color_lab_cache, match_mode)
        
        # 将图像转换为LAB颜色空间（批量处理）
        # 重塑为2D数组 (height*width, 3)
        pixels_2d = image_array.reshape(-1, 3).astype(np.float32) / 255.0
        image_lab = rgb2lab(pixels_2d)  # shape: (height*width, 3)
        
        # 批量计算所有像素到所有颜色的距离
        # 使用广播：image_lab (n_pixels, 3) 和 color_lab_cache (n_colors, 3)
        # 需要扩展维度以便批量计算
        
        # 方法：对每个像素计算到所有颜色的距离
        # 为了效率，我们处理一批像素，但如果色板很大，可能需要分批处理
        
        matched_colors = []
        batch_size = 1000  # 每批处理1000个像素
        
        for i in range(0, len(image_lab), batch_size):
            batch_end = min(i + batch_size, len(image_lab))
            
            # 计算距离 - 使用优化的批量计算方法
            # 重新组织数据以便正确计算距离矩阵
            batch_lab = image_lab[i:batch_end]  # (batch_size, 3)
            color_lab = color_lab_cache[color_indices]  # (n_colors, 3)
            
            # 扩展维度以便批量计算
            batch_lab_exp = batch_lab[:, np.newaxis, :]  # (batch_size, 1, 3)
            color_lab_exp = color_lab[np.newaxis, :, :]  # (1, n_colors, 3)
            
            # 计算LAB差值并计算距离
            if match_mode == "detail":
                # 亮度权重更高，优先保留明暗层次
                lab_diff = batch_lab_exp - color_lab_exp  # (batch_size, n_colors, 3)
                weights = np.array([1.5, 1.0, 1.0])
                distances = np.sqrt(np.sum((lab_diff ** 2) * weights, axis=2))
            elif method == "cie94" and HAS_CIE94:
                try:
                    # 对于CIE94，使用scikit-image的实现
                    # 需要配对计算每个像素到所有颜色
                    distances = np.zeros((len(batch_lab), len(color_indices)), dtype=np.float32)
                    for p_idx in range(len(batch_lab)):
                        pixel_lab = batch_lab[p_idx:p_idx+1]  # (1, 3)
                        distances[p_idx] = deltaE_cie94(pixel_lab, color_lab).flatten()
                except Exception as e:
                    # 如果失败，使用改进的CIE76
                    lab_diff = batch_lab_exp - color_lab_exp  # (batch_size, n_colors, 3)
                    # 使用加权欧氏距离（CIE94的近似）
                    weights = np.array([1.0, 1.0, 1.0])  # L*, a*, b*权重
                    distances = np.sqrt(np.sum((lab_diff ** 2) * weights, axis=2))
            elif method == "cie2000" and HAS_CIE2000:
                try:
                    # CIEDE2000最准确但计算较慢
                    distances = np.zeros((len(batch_lab), len(color_indices)), dtype=np.float32)
                    for p_idx in range(len(batch_lab)):
                        pixel_lab = batch_lab[p_idx:p_idx+1]  # (1, 3)
                        distances[p_idx] = deltaE_ciede2000(pixel_lab, color_lab).flatten()
                except Exception as e:
                    # 如果失败，使用改进的CIE76
                    lab_diff = batch_lab_exp - color_lab_exp
                    weights = np.array([1.0, 1.0, 1.0])
                    distances = np.sqrt(np.sum((lab_diff ** 2) * weights, axis=2))
            else:
                # 使用改进的CIE76（加权LAB距离）
                lab_diff = batch_lab_exp - color_lab_exp  # (batch_size, n_colors, 3)
                # 对L*通道使用较小权重（因为人对亮度变化不敏感），对a*, b*使用正常权重
                weights = np.array([0.5, 1.0, 1.0])  # 优化权重以提高感知准确性
                distances = np.sqrt(np.sum((lab_diff ** 2) * weights, axis=2))
            
            # 找到每个像素的最佳匹配颜色
            min_indices = np.argmin(distances, axis=1)  # (batch_size,)
            
            # 创建匹配结果
            for j, idx in enumerate(min_indices):
                best_color = colors_to_use[idx].copy()
                best_color['distance'] = float(distances[j, idx])
                matched_colors.append(best_color)
        
        # 重塑为原始图像尺寸
        matched_colors_array = np.array(matched_colors, dtype=object)
        matched_colors_array = matched_colors_array.reshape(height, width)
        
        return matched_colors_array

    def _match_image_colors_dither(self, image_array: np.ndarray, colors_to_use: List[Dict],
                                   color_lab_cache: np.ndarray, mode: str) -> np.ndarray:
        """使用误差扩散抖动进行颜色匹配，保留细节层次。"""
        height, width = image_array.shape[:2]
        
        # 转为LAB进行误差扩散
        pixels_2d = image_array.reshape(-1, 3).astype(np.float32) / 255.0
        lab_image = rgb2lab(pixels_2d).reshape(height, width, 3)
        
        if mode == "dither_atkinson":
            kernel = [
                (1, 0, 1 / 8),
                (2, 0, 1 / 8),
                (-1, 1, 1 / 8),
                (0, 1, 1 / 8),
                (1, 1, 1 / 8),
                (0, 2, 1 / 8),
            ]
        else:
            # Floyd-Steinberg
            kernel = [
                (1, 0, 7 / 16),
                (-1, 1, 3 / 16),
                (0, 1, 5 / 16),
                (1, 1, 1 / 16),
            ]
        
        min_lab = np.array([0.0, -128.0, -128.0], dtype=np.float32)
        max_lab = np.array([100.0, 127.0, 127.0], dtype=np.float32)
        matched_colors = np.empty((height, width), dtype=object)
        
        for y in range(height):
            for x in range(width):
                pixel_lab = lab_image[y, x]
                diff = color_lab_cache - pixel_lab
                dist = np.sum(diff * diff, axis=1)
                best_idx = int(np.argmin(dist))
                
                best_color = colors_to_use[best_idx].copy()
                best_color['distance'] = float(np.sqrt(dist[best_idx]))
                matched_colors[y, x] = best_color
                
                err = pixel_lab - color_lab_cache[best_idx]
                if err[0] != 0 or err[1] != 0 or err[2] != 0:
                    for dx, dy, weight in kernel:
                        nx = x + dx
                        ny = y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            lab_image[ny, nx] += err * weight
                            lab_image[ny, nx] = np.clip(lab_image[ny, nx], min_lab, max_lab)
        
        return matched_colors
    
    def get_color_by_id(self, color_id: int) -> Optional[Dict]:
        """
        根据ID获取颜色
        
        Args:
            color_id: 颜色ID
            
        Returns:
            颜色字典，如果不存在返回None
        """
        for color in self.all_colors:
            if color.get('id') == color_id:
                return color
        return None
    
    def get_color_by_code(self, code: str) -> Optional[Dict]:
        """
        根据色号代码获取颜色
        
        Args:
            code: 色号代码
            
        Returns:
            颜色字典，如果不存在返回None
        """
        for color in self.all_colors:
            if color.get('code') == code:
                return color
        return None
    
    def get_all_colors(self, include_custom: bool = True, 
                      brand: Optional[str] = None, 
                      series: Optional[str] = None) -> List[Dict]:
        """
        获取所有颜色（支持按品牌和系列过滤）
        
        Args:
            include_custom: 是否包含自定义颜色
            brand: 品牌名称（如"COCO"），如果为"自定义"则只返回自定义色板
            series: 系列名称（如"291"），需要与brand一起使用
            
        Returns:
            颜色列表
        """
        colors = self.all_colors.copy() if include_custom else self.standard_colors.copy()
        
        # 如果选择了"自定义"品牌，只返回自定义色板
        if brand == "自定义":
            return self.custom_colors.copy()
        
        # 如果指定了品牌，进行过滤
        if brand:
            colors = [c for c in colors if c.get('brand') == brand]
        
        # 如果指定了系列，进一步过滤
        if series:
            colors = [c for c in colors if c.get('series') == series]
        
        return colors
    
    def get_brands_and_series(self) -> Dict[str, List[str]]:
        """
        获取所有品牌及其系列列表
        
        Returns:
            字典，键为品牌名，值为该品牌的系列列表
        """
        brands_map = {}
        
        # 从标准色板中提取
        for color in self.standard_colors:
            brand = color.get('brand', '')
            series = color.get('series', '')
            if brand:
                if brand not in brands_map:
                    brands_map[brand] = set()
                if series:
                    brands_map[brand].add(series)
        
        # 转换为列表并排序
        result = {}
        for brand, series_set in brands_map.items():
            result[brand] = sorted(list(series_set), key=lambda x: int(x) if x.isdigit() else 999)
        
        return result
    
    def export_custom_colors_csv(self, file_path: str) -> None:
        """
        导出自定义颜色到CSV文件
        
        Args:
            file_path: 输出文件路径
        """
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(['ID', '中文名称', '英文名称', '色号代码', 'R', 'G', 'B', '分类'])
            # 写入数据
            for color in self.custom_colors:
                rgb = color.get('rgb', [0, 0, 0])
                writer.writerow([
                    color.get('id', ''),
                    color.get('name_zh', ''),
                    color.get('name_en', ''),
                    color.get('code', ''),
                    rgb[0] if len(rgb) > 0 else 0,
                    rgb[1] if len(rgb) > 1 else 0,
                    rgb[2] if len(rgb) > 2 else 0,
                    color.get('category', '自定义')
                ])
    
    def export_custom_colors_json(self, file_path: str) -> None:
        """
        导出自定义颜色到JSON文件
        
        Args:
            file_path: 输出文件路径
        """
        data = {
            'name': '用户自定义色板',
            'bead_size_mm': 5,
            'colors': self.custom_colors
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def import_custom_colors_csv(self, file_path: str, replace: bool = False) -> Dict:
        """
        从CSV文件导入自定义颜色
        
        Args:
            file_path: CSV文件路径
            replace: 是否替换现有颜色（True替换，False追加）
            
        Returns:
            导入结果字典 {'success': bool, 'imported': int, 'errors': List[str]}
        """
        imported_count = 0
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                if replace:
                    self.custom_colors = []
                
                for row_num, row in enumerate(reader, start=2):  # 从第2行开始（第1行是表头）
                    try:
                        # 解析数据
                        name_zh = row.get('中文名称', '').strip()
                        name_en = row.get('英文名称', '').strip()
                        code = row.get('色号代码', '').strip()
                        category = row.get('分类', '自定义').strip() or '自定义'
                        
                        # 解析RGB值
                        try:
                            r = int(row.get('R', '0').strip())
                            g = int(row.get('G', '0').strip())
                            b = int(row.get('B', '0').strip())
                            rgb = [r, g, b]
                        except (ValueError, KeyError) as e:
                            errors.append(f"第{row_num}行: RGB值格式错误 - {str(e)}")
                            continue
                        
                        # 验证数据
                        if not name_zh and not name_en:
                            errors.append(f"第{row_num}行: 中文名称或英文名称至少需要一个")
                            continue
                        
                        if not code:
                            errors.append(f"第{row_num}行: 色号代码不能为空")
                            continue
                        
                        # 检查是否已存在相同代码的颜色
                        existing = [c for c in self.custom_colors if c.get('code') == code]
                        if existing:
                            if replace:
                                # 替换现有颜色
                                for i, c in enumerate(self.custom_colors):
                                    if c.get('code') == code:
                                        self.custom_colors[i] = {
                                            'id': c.get('id', max([c.get('id', 0) for c in self.custom_colors], default=1000) + 1),
                                            'name_zh': name_zh,
                                            'name_en': name_en,
                                            'code': code,
                                            'rgb': rgb,
                                            'category': category
                                        }
                                        imported_count += 1
                                        break
                            else:
                                errors.append(f"第{row_num}行: 色号代码 '{code}' 已存在，跳过")
                                continue
                        else:
                            # 添加新颜色
                            max_id = max([c.get('id', 0) for c in self.custom_colors], default=1000)
                            new_color = {
                                'id': max_id + 1,
                                'name_zh': name_zh,
                                'name_en': name_en,
                                'code': code,
                                'rgb': rgb,
                                'category': category
                            }
                            self.custom_colors.append(new_color)
                            imported_count += 1
                    
                    except Exception as e:
                        errors.append(f"第{row_num}行: 处理错误 - {str(e)}")
                        continue
                
                # 更新颜色列表和缓存
                if imported_count > 0:
                    self._update_all_colors()
                    self._update_lab_cache()
                    self._save_custom_colors()
        
        except Exception as e:
            errors.append(f"文件读取错误: {str(e)}")
        
        return {
            'success': imported_count > 0 or len(errors) == 0,
            'imported': imported_count,
            'errors': errors
        }
    
    def import_custom_colors_json(self, file_path: str, replace: bool = False) -> Dict:
        """
        从JSON文件导入自定义颜色
        
        Args:
            file_path: JSON文件路径
            replace: 是否替换现有颜色（True替换，False追加）
            
        Returns:
            导入结果字典 {'success': bool, 'imported': int, 'errors': List[str]}
        """
        imported_count = 0
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            colors = data.get('colors', [])
            if not isinstance(colors, list):
                errors.append("JSON格式错误: 'colors' 字段应该是数组")
                return {'success': False, 'imported': 0, 'errors': errors}
            
            if replace:
                self.custom_colors = []
            
            for idx, color_data in enumerate(colors):
                try:
                    # 验证必需字段
                    if not isinstance(color_data, dict):
                        errors.append(f"第{idx+1}个颜色: 数据格式错误，应为对象")
                        continue
                    
                    name_zh = color_data.get('name_zh', '').strip()
                    name_en = color_data.get('name_en', '').strip()
                    code = color_data.get('code', '').strip()
                    category = color_data.get('category', '自定义').strip() or '自定义'
                    rgb = color_data.get('rgb', [])
                    
                    # 验证数据
                    if not name_zh and not name_en:
                        errors.append(f"第{idx+1}个颜色: 中文名称或英文名称至少需要一个")
                        continue
                    
                    if not code:
                        errors.append(f"第{idx+1}个颜色: 色号代码不能为空")
                        continue
                    
                    if not isinstance(rgb, list) or len(rgb) != 3:
                        errors.append(f"第{idx+1}个颜色: RGB值格式错误，应为 [r, g, b]")
                        continue
                    
                    try:
                        rgb = [int(rgb[0]), int(rgb[1]), int(rgb[2])]
                    except (ValueError, TypeError):
                        errors.append(f"第{idx+1}个颜色: RGB值必须是整数")
                        continue
                    
                    # 检查是否已存在相同代码的颜色
                    existing = [c for c in self.custom_colors if c.get('code') == code]
                    if existing:
                        if replace:
                            # 替换现有颜色
                            for i, c in enumerate(self.custom_colors):
                                if c.get('code') == code:
                                    self.custom_colors[i] = {
                                        'id': c.get('id', max([c.get('id', 0) for c in self.custom_colors], default=1000) + 1),
                                        'name_zh': name_zh,
                                        'name_en': name_en,
                                        'code': code,
                                        'rgb': rgb,
                                        'category': category
                                    }
                                    imported_count += 1
                                    break
                        else:
                            errors.append(f"第{idx+1}个颜色: 色号代码 '{code}' 已存在，跳过")
                            continue
                    else:
                        # 添加新颜色
                        max_id = max([c.get('id', 0) for c in self.custom_colors], default=1000)
                        new_color = {
                            'id': max_id + 1,
                            'name_zh': name_zh,
                            'name_en': name_en,
                            'code': code,
                            'rgb': rgb,
                            'category': category
                        }
                        self.custom_colors.append(new_color)
                        imported_count += 1
                
                except Exception as e:
                    errors.append(f"第{idx+1}个颜色: 处理错误 - {str(e)}")
                    continue
            
            # 更新颜色列表和缓存
            if imported_count > 0:
                self._update_all_colors()
                self._update_lab_cache()
                self._save_custom_colors()
        
        except json.JSONDecodeError as e:
            errors.append(f"JSON解析错误: {str(e)}")
        except Exception as e:
            errors.append(f"文件读取错误: {str(e)}")
        
        return {
            'success': imported_count > 0 or len(errors) == 0,
            'imported': imported_count,
            'errors': errors
        }

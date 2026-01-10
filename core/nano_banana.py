"""
Nano Banana API客户端模块
用于调用Nano Banana API生成拼豆风格图片
"""
import os
import time
import requests
import logging
import base64
import urllib3
from typing import Optional, Dict, List
from urllib.parse import urlparse
import uuid
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 禁用SSL警告（当使用verify=False时）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class NanoBananaClient:
    """Nano Banana API客户端"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.grsai.com", 
                 proxy: Optional[str] = None):
        """
        初始化Nano Banana客户端
        
        Args:
            api_key: API密钥，如果为None则从环境变量获取
            base_url: API基础URL
            proxy: 代理地址（格式：http://proxy_host:port 或 https://proxy_host:port）
        """
        self.api_key = api_key or os.getenv("NANO_BANANA_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.draw_endpoint = f"{self.base_url}/v1/draw/nano-banana"
        self.result_endpoint = f"{self.base_url}/v1/draw/result"
        
        # 代理设置（优先级：参数 > 环境变量）
        self.proxy = proxy or os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("http_proxy") or os.getenv("https_proxy")
        if self.proxy:
            logger.info(f"使用代理: {self.proxy}")
        
        if not self.api_key:
            logger.warning("Nano Banana API密钥未设置，请在环境变量中设置NANO_BANANA_API_KEY或传入api_key参数")
    
    def generate_image(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        image_path: Optional[str] = None,
        model: str = "nano-banana-fast",
        aspect_ratio: str = "auto",
        image_size: str = "1K",
        max_dimension: Optional[int] = None,
        webhook: str = "-1",
        shut_progress: bool = False,
        timeout: int = 300
    ) -> Dict:
        """
        生成拼豆风格图片
        
        Args:
            prompt: 提示词
            image_url: 参考图片URL（可选）
            model: 使用的模型，默认"nano-banana-fast"
            aspect_ratio: 图像比例，默认"auto"
            image_size: 图像大小，默认"1K"
            max_dimension: 最大尺寸（用于计算aspectRatio），如果提供则自动计算
            webhook: WebHook地址，"-1"表示使用轮询方式
            shut_progress: 是否关闭进度回复
            timeout: 超时时间（秒）
            
        Returns:
            包含生成图片信息的字典
        """
        if not self.api_key:
            raise ValueError("API密钥未设置，无法调用Nano Banana API")
        
        # 根据max_dimension计算aspectRatio
        if max_dimension and aspect_ratio == "auto":
            # 可以根据图像尺寸自动选择合适的比例
            aspect_ratio = "auto"
        
        # 准备请求参数
        payload = {
            "model": model,
            "prompt": prompt,
            "aspectRatio": aspect_ratio,
            "imageSize": image_size,
            "webHook": webhook,
            "shutProgress": shut_progress
        }
        
        # 添加参考图片（优先使用URL，然后是Base64，最后是本地文件路径转换为Base64）
        urls_list = []
        if image_url:
            urls_list.append(image_url)
        elif image_base64:
            # Base64格式：data:image/png;base64,xxx
            if not image_base64.startswith("data:"):
                image_base64 = f"data:image/png;base64,{image_base64}"
            urls_list.append(image_base64)
        elif image_path and os.path.exists(image_path):
            # 读取本地文件并转换为Base64
            with open(image_path, "rb") as f:
                image_data = f.read()
                base64_str = base64.b64encode(image_data).decode("utf-8")
                # 根据文件扩展名确定MIME类型
                ext = os.path.splitext(image_path)[1].lower()
                mime_types = {
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".webp": "image/webp"
                }
                mime_type = mime_types.get(ext, "image/png")
                urls_list.append(f"data:{mime_type};base64,{base64_str}")
        
        if urls_list:
            payload["urls"] = urls_list
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            # 发送请求
            logger.info(f"调用Nano Banana API，模型: {model}, 提示词: {prompt}")
            
            # 尝试使用不同的SSL设置
            session = requests.Session()
            # 添加重试机制
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["POST"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            session.mount("http://", adapter)
            
            # 准备请求参数（包含代理）
            request_kwargs = {
                "url": self.draw_endpoint,
                "json": payload,
                "headers": headers,
                "timeout": 60,  # 增加超时时间
            }
            
            # 添加代理
            if self.proxy:
                request_kwargs["proxies"] = {
                    "http": self.proxy,
                    "https": self.proxy
                }
            
            try:
                # 首先尝试标准SSL验证
                request_kwargs["verify"] = True
                response = session.post(**request_kwargs)
                response.raise_for_status()
            except requests.exceptions.SSLError as ssl_error:
                logger.warning(f"SSL验证失败，尝试禁用SSL验证: {str(ssl_error)}")
                # 如果SSL验证失败，尝试禁用验证（仅用于连接问题）
                # 注意：这会降低安全性，但在某些网络环境下可能是必需的
                request_kwargs["verify"] = False  # 禁用SSL验证
                response = session.post(**request_kwargs)
                response.raise_for_status()
            
            result = response.json()
            
            # 如果使用webhook="-1"，会立即返回id
            if result.get("code") == 0 and "data" in result and "id" in result["data"]:
                task_id = result["data"]["id"]
                logger.info(f"任务已提交，ID: {task_id}")
                
                # 轮询获取结果
                return self._poll_result(task_id, timeout)
            else:
                # 流式响应或直接返回结果
                return result
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Nano Banana API请求失败: {str(e)}")
            raise Exception(f"API请求失败: {str(e)}")
    
    def _poll_result(self, task_id: str, timeout: int = 300) -> Dict:
        """
        轮询获取任务结果
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）
            
        Returns:
            任务结果字典
        """
        start_time = time.time()
        poll_interval = 2  # 轮询间隔（秒）
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        while time.time() - start_time < timeout:
            # 创建带重试的session
            session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["POST"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            session.mount("http://", adapter)
            
            try:
                # 准备请求参数（包含代理）
                request_kwargs = {
                    "url": self.result_endpoint,
                    "json": {"id": task_id},
                    "headers": headers,
                    "timeout": 30,
                }
                
                # 添加代理
                if self.proxy:
                    request_kwargs["proxies"] = {
                        "http": self.proxy,
                        "https": self.proxy
                    }
                
                try:
                    request_kwargs["verify"] = True
                    response = session.post(**request_kwargs)
                    response.raise_for_status()
                except requests.exceptions.SSLError:
                    # SSL验证失败时禁用验证
                    logger.warning("轮询结果时SSL验证失败，禁用验证")
                    request_kwargs["verify"] = False
                    response = session.post(**request_kwargs)
                    response.raise_for_status()
                
                result = response.json()
                
                if result.get("code") == 0 and "data" in result:
                    data = result["data"]
                    status = data.get("status", "running")
                    progress = data.get("progress", 0)
                    
                    logger.info(f"任务进度: {progress}%, 状态: {status}")
                    
                    if status == "succeeded":
                        return data
                    elif status == "failed":
                        error_msg = data.get("error", data.get("failure_reason", "未知错误"))
                        raise Exception(f"生成失败: {error_msg}")
                    
                    # 任务进行中，继续等待
                    time.sleep(poll_interval)
                else:
                    error_msg = result.get("msg", "获取结果失败")
                    raise Exception(f"获取结果失败: {error_msg}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"轮询结果时出错: {str(e)}")
                time.sleep(poll_interval)
                continue
        
        raise Exception(f"任务超时（超过{timeout}秒）")
    
    def download_image(self, image_url: str, save_path: Optional[str] = None) -> str:
        """
        下载生成的图片
        
        Args:
            image_url: 图片URL
            save_path: 保存路径，如果为None则自动生成
            
        Returns:
            保存的文件路径
        """
        if save_path is None:
            # 自动生成保存路径
            os.makedirs("static/images/nano_banana", exist_ok=True)
            file_id = str(uuid.uuid4())
            parsed_url = urlparse(image_url)
            ext = os.path.splitext(parsed_url.path)[1] or ".png"
            save_path = f"static/images/nano_banana/{file_id}{ext}"
        
        try:
            session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            session.mount("http://", adapter)
            
            # 准备请求参数（包含代理）
            request_kwargs = {
                "url": image_url,
                "timeout": 60,
            }
            
            # 添加代理
            if self.proxy:
                request_kwargs["proxies"] = {
                    "http": self.proxy,
                    "https": self.proxy
                }
            
            try:
                request_kwargs["verify"] = True
                response = session.get(**request_kwargs)
                response.raise_for_status()
            except requests.exceptions.SSLError:
                # SSL验证失败时禁用验证
                logger.warning("下载图片时SSL验证失败，禁用验证")
                request_kwargs["verify"] = False
                response = session.get(**request_kwargs)
                response.raise_for_status()
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"图片已下载到: {save_path}")
            return save_path
            
        except requests.exceptions.RequestException as e:
            logger.error(f"下载图片失败: {str(e)}")
            raise Exception(f"下载图片失败: {str(e)}")


def calculate_aspect_ratio(width: int, height: int) -> str:
    """
    根据图像尺寸计算最接近的aspectRatio
    
    Args:
        width: 图像宽度
        height: 图像高度
        
    Returns:
        aspectRatio字符串
    """
    ratio = width / height if height > 0 else 1.0
    
    # 定义标准比例
    ratios = {
        "1:1": 1.0,
        "16:9": 16/9,
        "9:16": 9/16,
        "4:3": 4/3,
        "3:4": 3/4,
        "3:2": 3/2,
        "2:3": 2/3,
        "5:4": 5/4,
        "4:5": 4/5,
        "21:9": 21/9
    }
    
    # 找到最接近的比例
    closest_ratio = "auto"
    min_diff = float('inf')
    
    for ratio_name, ratio_value in ratios.items():
        diff = abs(ratio - ratio_value)
        if diff < min_diff:
            min_diff = diff
            closest_ratio = ratio_name
    
    # 如果差异太大，使用auto
    if min_diff > 0.1:
        return "auto"
    
    return closest_ratio


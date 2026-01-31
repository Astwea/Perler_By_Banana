from typing import Dict, Optional, List, Tuple
import numpy as np
from .color import ColorInfo


class Palette:
    """
    Color palette - manages all colors and establishes index mappings
    
    Core data structures:
    - colors_by_id: {color_id: ColorInfo} - fast ID lookup
    - index_by_id: {color_id: compact_index} - ID to compact index mapping (0..K-1)
    - rgb_lut: np.ndarray(K+1, 3) - RGB lookup table (index=0 is white background)
    
    Design advantages:
    - Single data source, avoiding color duplication
    - RGB LUT for O(1) color lookup
    - Compact indices for fast array operations
    """
    
    def __init__(self) -> None:
        self.colors_by_id: Dict[int, ColorInfo] = {}
        self.index_by_id: Dict[int, int] = {}
        self._lut_dirty = True
        self._rgb_lut: Optional[np.ndarray] = None
    
    @property
    def rgb_lut(self) -> np.ndarray:
        """
        Get RGB lookup table (lazy rebuild)
        
        Returns:
            np.ndarray shape (K+1, 3), uint8 type
            LUT[0] = (255, 255, 255) white background
            LUT[i] = RGB value of (i-1)th color (i >= 1)
        """
        if self._lut_dirty or self._rgb_lut is None:
            self._rebuild_lut()
            self._lut_dirty = False
        return self._rgb_lut
    
    def _rebuild_lut(self) -> None:
        """
        Rebuild RGB lookup table
        
        Rebuilds from colors_by_id:
        - Sort by color_id
        - Create compact indices 0..K-1
        - Build RGB LUT array
        """
        if not self.colors_by_id:
            self._rgb_lut = np.array([[255, 255, 255]], dtype=np.uint8)
            return
        
        sorted_ids = sorted(self.colors_by_id.keys())
        
        self.index_by_id = {cid: idx + 1 for idx, cid in enumerate(sorted_ids)}
        
        self._rgb_lut = np.zeros((len(sorted_ids) + 1, 3), dtype=np.uint8)
        self._rgb_lut[0] = [255, 255, 255]
        
        for idx, color_id in enumerate(sorted_ids):
            color_info = self.colors_by_id[color_id]
            self._rgb_lut[idx + 1] = list(color_info.rgb)
    
    def upsert_from_dict(self, d: dict) -> int:
        """
        Insert or update color from dictionary
        
        Args:
            d: color dict, must contain id, optionally contains:
               - code, name_zh, name_en, rgb, brand, series
        
        Returns:
            Inserted/updated color_id
        
        Raises:
            ValueError: if required fields are missing
        """
        color_id = d.get('id')
        if color_id is None:
            raise ValueError("Color dict must contain 'id' field")
        
        rgb = d.get('rgb')
        if rgb is None or not isinstance(rgb, (list, tuple)) or len(rgb) != 3:
            raise ValueError("Color dict must contain valid 'rgb' field (3 elements list or tuple)")
        
        color_info = ColorInfo(
            id=color_id,
            code=d.get('code', ''),
            name_zh=d.get('name_zh', ''),
            name_en=d.get('name_en', ''),
            rgb=tuple(rgb),
            brand=d.get('brand'),
            series=d.get('series')
        )
        
        self.colors_by_id[color_id] = color_info
        self._lut_dirty = True
        
        return color_id
    
    def get_color(self, color_id: int) -> Optional[ColorInfo]:
        """
        Get color info by ID
        
        Args:
            color_id: color ID
        
        Returns:
            ColorInfo object, None if not exists
        """
        return self.colors_by_id.get(color_id)
    
    def get_rgb(self, color_id: int) -> Optional[Tuple[int, int, int]]:
        """
        Get RGB value by ID
        
        Args:
            color_id: color ID
        
        Returns:
            RGB tuple, None if not exists
        """
        color_info = self.colors_by_id.get(color_id)
        return color_info.rgb if color_info else None
    
    def find_by_rgb(self, rgb: Tuple[int, int, int], threshold: int = 5) -> Optional[int]:
        """
        Find color ID by RGB value (approximate match)
        
        Args:
            rgb: target RGB value
            threshold: color difference threshold
        
        Returns:
            Matching color_id, None if not found
        """
        r, g, b = rgb
        for color_id, color_info in self.colors_by_id.items():
            cr, cg, cb = color_info.rgb
            if (abs(r - cr) < threshold and 
                abs(g - cg) < threshold and 
                abs(b - cb) < threshold):
                return color_id
        return None
    
    def get_background_ids(self, white_threshold: int = 250) -> List[int]:
        """
        Get all background color IDs (white-like)
        
        Args:
            white_threshold: RGB threshold, all above this value considered white
        
        Returns:
            List of background color IDs
        """
        return [
            cid for cid, info in self.colors_by_id.items()
            if info.is_background
        ]
    
    def get_all_colors(self) -> List[ColorInfo]:
        """
        Get all color info
        
        Returns:
            List of ColorInfo objects
        """
        return list(self.colors_by_id.values())
    
    def __len__(self) -> int:
        """Number of colors in palette"""
        return len(self.colors_by_id)
    
    def __contains__(self, color_id: int) -> bool:
        """Check if color exists"""
        return color_id in self.colors_by_id

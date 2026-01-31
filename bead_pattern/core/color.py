from dataclasses import dataclass, field
from typing import Tuple, Optional
import re


@dataclass(frozen=True, slots=True)
class ColorInfo:
    """
    Color information data class - immutable, efficient color storage
    
    Uses @dataclass(frozen=True, slots=True) to ensure:
    - Immutability (thread-safe, hashable)
    - Memory efficiency (no __dict__)
    - Fast attribute access (direct property access)
    
    Args:
        id: color ID
        code: color code (may contain brand prefix like "COCO-291-A01")
        name_zh: Chinese name
        name_en: English name
        rgb: RGB triplet
        brand: brand name (optional)
        series: series name (optional)
    
    Attributes:
        display_code: Normalized display code (remove brand prefix, remove leading zeros from numeric suffix)
    """
    
    id: int
    code: str
    name_zh: str
    name_en: str
    rgb: Tuple[int, int, int]
    brand: Optional[str] = None
    series: Optional[str] = None
    
    @property
    def display_code(self) -> str:
        """
        Get normalized display code
        
        Priority:
        1. If code contains '-', use last part (color number)
        2. Remove leading zeros in numeric part (A01 -> A1, 001 -> 1)
        3. If no code, fallback to name_en/name_zh
        
        Returns:
            Normalized display code string
        """
        if self.code:
            if '-' in self.code:
                code_part = self.code.split('-')[-1]
            else:
                code_part = self.code
            
            num_match = re.match(r'^([A-Za-z]+)(\d+)$', code_part)
            if num_match:
                prefix, digits = num_match.groups()
                return f"{prefix}{int(digits)}"
            
            return code_part
        
        return self.name_en or self.name_zh
    
    @property
    def is_background(self) -> bool:
        """
        Check if this is a background color (white-like)
        
        Returns:
            True if RGB values are all near 255
        """
        r, g, b = self.rgb
        return r >= 250 and g >= 250 and b >= 250

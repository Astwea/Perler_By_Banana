import numpy as np
from typing import Dict, Optional, List, Tuple
from .color import ColorInfo
from .palette import Palette
from .grid import BeadGrid, EMPTY


class BeadPatternV2:
    """
    Bead pattern V2 - high-performance pattern representation

    Core attributes:
    - grid: BeadGrid storing color indices
    - palette: Palette managing color information
    - bead_size_mm: size of individual bead in millimeters

    Performance optimizations:
    - Grid uses int32 array instead of dict
    - Palette uses LUT for O(1) color lookups
    - Vectorized operations for statistics
    """

    def __init__(self, width: int, height: int, bead_size_mm: float = 2.6):
        """
        Initialize pattern

        Args:
            width: pattern width (number of beads)
            height: pattern height (number of beads)
            bead_size_mm: size of individual bead in millimeters
        """
        self.grid = BeadGrid(width, height)
        self.palette = Palette()
        self._bead_size_mm = bead_size_mm

    @property
    def bead_size_mm(self) -> float:
        """Bead size in millimeters"""
        return self._bead_size_mm

    @property
    def actual_width_mm(self) -> float:
        """Actual width in millimeters"""
        return self.grid.width * self._bead_size_mm

    @property
    def actual_height_mm(self) -> float:
        """Actual height in millimeters"""
        return self.grid.height * self._bead_size_mm

    def get_color_statistics(self, exclude_background: bool = False,
                             background_colors: Optional[List[int]] = None) -> Dict:
        """
        Get color statistics (vectorized)

        Args:
            exclude_background: exclude background colors from statistics
            background_colors: explicit background color IDs, None means auto-detect white colors

        Returns:
            {
                'total_beads': total number of beads,
                'unique_colors': number of unique colors,
                'color_counts': {color_id: count} dictionary,
                'background_beads': number of background beads (if exclude_background)
            }
        """
        flat_ids = self.grid.get_color_ids_flat(valid_only=False)

        # Determine background IDs
        background_ids = set()
        if exclude_background:
            if background_colors:
                background_ids = set(background_colors)
            else:
                background_ids = set(self.palette.get_background_ids())

        if exclude_background and background_ids:
            valid_mask = ~np.isin(flat_ids, list(background_ids))
            flat_ids = flat_ids[valid_mask]
            background_count = self.grid.get_color_ids_flat(valid_only=False).size - flat_ids.size
        else:
            background_count = 0

        unique_ids, counts = np.unique(flat_ids, return_counts=True)
        color_counts = dict(zip(unique_ids.tolist(), counts.tolist()))

        return {
            'total_beads': self.grid.width * self.grid.height,
            'unique_colors': len(unique_ids),
            'color_counts': color_counts,
            'background_beads': background_count if exclude_background else None
        }

    def get_subject_bounds(self, background_colors: Optional[List[int]] = None) -> Optional[Tuple[int, int, int, int]]:
        """
        Get bounding box of non-background beads

        Args:
            background_colors: explicit background color IDs, None means auto-detect white colors

        Returns:
            (min_x, min_y, max_x, max_y) tuple, None if no beads
        """
        # Get background IDs
        background_ids = set()
        if background_colors:
            background_ids = set(background_colors)
        else:
            background_ids = set(self.palette.get_background_ids())

        # Get mask of non-background beads
        valid_mask = self.grid.get_background_mask(background_ids)

        if not np.any(valid_mask):
            return None

        # Find bounding box
        rows = np.any(valid_mask, axis=1)
        cols = np.any(valid_mask, axis=0)

        min_y, max_y = np.where(rows)[0][[0, -1]]
        min_x, max_x = np.where(cols)[0][[0, -1]]

        return (min_x, min_y, max_x + 1, max_y + 1)

    def get_subject_size(self, background_colors: Optional[List[int]] = None) -> Optional[Dict]:
        """
        Get size information of non-background region

        Args:
            background_colors: explicit background color IDs, None means auto-detect white colors

        Returns:
            {
                'width': width in beads,
                'height': height in beads,
                'width_mm': width in millimeters,
                'height_mm': height in millimeters
            } or None if no beads
        """
        bounds = self.get_subject_bounds(background_colors)
        if bounds is None:
            return None

        min_x, min_y, max_x, max_y = bounds
        width = max_x - min_x
        height = max_y - min_y

        return {
            'width': width,
            'height': height,
            'width_mm': width * self._bead_size_mm,
            'height_mm': height * self._bead_size_mm
        }

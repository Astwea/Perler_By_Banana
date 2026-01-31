import numpy as np
from typing import Tuple, Optional


EMPTY = -1


class BeadGrid:
    """
    Bead grid - stores color IDs as int32 array

    Uses -1 for blank positions (no bead)
    grid_ids stores color_id or EMPTY
    Memory efficiency: int32 array (4 bytes per element) vs object dict (~150 bytes)
    """

    EMPTY = EMPTY
    
    def __init__(self, width: int, height: int):
        """
        Initialize grid
        
        Args:
            width: grid width (number of columns)
            height: grid height (number of rows)
        """
        self.width = width
        self.height = height
        self.grid_ids = np.full((height, width), EMPTY, dtype=np.int32)
    
    def resize(self, width: int, height: int) -> None:
        """
        Resize grid (preserve existing data)
        
        Args:
            width: new width
            height: new height
        """
        new_grid = np.full((height, width), EMPTY, dtype=np.int32)
        
        h_copy = min(self.height, height)
        w_copy = min(self.width, width)
        
        if h_copy > 0 and w_copy > 0:
            new_grid[:h_copy, :w_copy] = self.grid_ids[:h_copy, :w_copy]
        
        self.width = width
        self.height = height
        self.grid_ids = new_grid
    
    def set_id(self, x: int, y: int, color_id: int) -> None:
        """
        Set bead color ID at position
        
        Args:
            x: X coordinate (column)
            y: Y coordinate (row)
            color_id: color ID (use EMPTY for blank)
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid_ids[y, x] = color_id
    
    def get_id(self, x: int, y: int) -> int:
        """
        Get bead color ID at position
        
        Args:
            x: X coordinate (column)
            y: Y coordinate (row)
        
        Returns:
            color ID, or EMPTY if position invalid
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid_ids[y, x]
        return EMPTY
    
    def get_valid_mask(self) -> np.ndarray:
        """
        Get valid bead positions mask (non-blank)
        
        Returns:
            bool array shape(H, W), True for valid beads
        """
        return self.grid_ids != EMPTY
    
    def get_background_mask(self, background_ids: set) -> np.ndarray:
        """
        Get background mask (exclude specified IDs)
        
        Args:
            background_ids: set of background color IDs
        
        Returns:
            bool array shape(H, W), True for non-background
        """
        valid = self.grid_ids != EMPTY
        if background_ids:
            not_bg = ~np.isin(self.grid_ids, list(background_ids))
            return valid & not_bg
        return valid
    
    def get_color_ids_flat(self, valid_only: bool = False) -> np.ndarray:
        """
        Get flattened color IDs array
        
        Args:
            valid_only: return only valid IDs (exclude EMPTY)
        
        Returns:
            1D int array
        """
        flat = self.grid_ids.flatten()
        if valid_only:
            return flat[flat != EMPTY]
        return flat
    
    def get_coords_by_color_id(self, color_id: int) -> np.ndarray:
        """
        Get all coordinates using specified color ID
        
        Args:
            color_id: color ID to find
        
        Returns:
            (N, 2) array, each row is [y, x]
        """
        mask = self.grid_ids == color_id
        coords = np.argwhere(mask)
        return coords if coords.size > 0 else np.array([]).reshape(0, 2)
    
    def count_color_occurrences(self) -> dict:
        """
        Count color occurrences (vectorized)
        
        Returns:
            {color_id: count} dictionary
        """
        flat = self.grid_ids.flatten()
        valid_flat = flat[flat != EMPTY]
        unique_ids, counts = np.unique(valid_flat, return_counts=True)
        return dict(zip(unique_ids, counts))
    
    def __len__(self) -> int:
        """Total cells"""
        return self.width * self.height
    
    @property
    def shape(self) -> Tuple[int, int]:
        """Grid shape (height, width)"""
        return (self.height, self.width)

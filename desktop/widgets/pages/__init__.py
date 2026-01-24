"""
页面模块
"""

from .upload_page import UploadPage
from .parameter_page import ParameterPage
from .process_page import ProcessPage
from .result_page import ResultPage
from .palette_page import PalettePage
from .history_page import HistoryPage
from .settings_page import SettingsPage

__all__ = [
    'UploadPage',
    'ParameterPage',
    'ProcessPage',
    'ResultPage',
    'PalettePage',
    'HistoryPage',
    'SettingsPage'
]

"""
国际化翻译器
支持中英文双语切换
"""
import os
from PyQt6.QtCore import QTranslator, QLocale, QCoreApplication
from PyQt6.QtWidgets import QApplication


class Translator:
    """翻译器"""

    def __init__(self):
        self.current_language = 'zh_CN'
        self.translator = QTranslator()
        self.translations_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'desktop', 'i18n'
        )

    def load_language(self, language):
        """加载语言包"""
        self.current_language = language

        # 移除旧翻译
        if QApplication.instance():
            QApplication.instance().removeTranslator(self.translator)

        # 加载新翻译
        if language == 'zh_CN':
            qm_file = os.path.join(self.translations_dir, 'zh_CN.qm')
        elif language == 'en_US':
            qm_file = os.path.join(self.translations_dir, 'en_US.qm')
        else:
            return

        if os.path.exists(qm_file):
            self.translator.load(qm_file)
            QApplication.instance().installTranslator(self.translator)

    def get_current_language(self):
        """获取当前语言"""
        return self.current_language

    @staticmethod
    def tr(source_text):
        """翻译函数"""
        return QCoreApplication.translate('@default', source_text)

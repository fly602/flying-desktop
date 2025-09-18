#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际化模块
支持多语言界面
"""

import json
from pathlib import Path


class I18n:
    """国际化管理器"""
    
    def __init__(self, language='zh_CN'):
        self.language = language
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """加载翻译文件"""
        lang_file = Path(f"assets/lang/{self.language}.json")
        
        # 如果指定语言文件不存在，使用默认中文
        if not lang_file.exists():
            lang_file = Path("assets/lang/zh_CN.json")
        
        # 如果中文文件也不存在，使用内置翻译
        if not lang_file.exists():
            self.translations = self.get_default_translations()
            return
        
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception as e:
            print(f"加载语言文件失败 {lang_file}: {e}")
            self.translations = self.get_default_translations()
    
    def get_default_translations(self):
        """获取默认翻译（中文）"""
        return {
            "app_name": "Flying Desktop",
            "settings": "设置",
            "back": "返回",
            "save": "保存",
            "cancel": "取消",
            "resolution": "分辨率",
            "language": "语言",
            "font": "字体",
            "sound_effects": "音效",
            "enabled": "启用",
            "disabled": "禁用",
            "custom": "自定义",
            "default": "默认",
            "instructions": {
                "select": "使用方向键或手柄左摇杆选择",
                "confirm": "按确认键(A键/回车)确认",
                "back": "按返回键(B键/ESC)返回",
                "settings": "按设置键(Y键/Tab)打开设置"
            },
            "resolutions": {
                "auto": "自动检测",
                "1920x1080": "1920×1080 (Full HD)",
                "1366x768": "1366×768 (HD)",
                "1280x720": "1280×720 (HD Ready)",
                "1024x768": "1024×768 (XGA)",
                "800x600": "800×600 (SVGA)"
            },
            "languages": {
                "zh_CN": "简体中文",
                "en_US": "English",
                "ja_JP": "日本語"
            },
            "fonts": {
                "auto": "自动选择",
                "wqy_zenhei": "文泉驿正黑",
                "wqy_microhei": "文泉驿微米黑",
                "noto_cjk": "Noto Sans CJK",
                "source_han": "思源黑体"
            }
        }
    
    def t(self, key, default=None):
        """获取翻译文本"""
        keys = key.split('.')
        value = self.translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default or key
        
        return value
    
    def set_language(self, language):
        """设置语言"""
        self.language = language
        self.load_translations()
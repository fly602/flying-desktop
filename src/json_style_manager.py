#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON样式管理器
使用JSON配置文件替代CSS功能，支持主题、响应式布局和emoji样式配置
"""

import json
import pygame
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import math


class JSONStyleManager:
    """JSON样式管理器"""
    
    def __init__(self, config_file: str = "styles.json"):
        self.config_file = config_file
        self.styles = {}
        self.current_theme = "dark"
        self.screen_width = 1920
        self.screen_height = 1080
        
        # 字体缓存
        self.font_cache = {}
        self.emoji_font_cache = {}
        
        # 设置项配置
        self.settings_config = {}
        
        # 加载样式配置
        self.load_styles()
        # 加载设置项配置
        self.load_settings_config()
    
    def load_styles(self):
        """加载样式配置"""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.styles = json.load(f)
                print(f"样式配置已加载: {self.config_file}")
            else:
                # 使用默认配置
                self.styles = self._get_default_styles()
                print("使用默认样式配置")
        except Exception as e:
            print(f"加载样式配置失败: {e}")
            self.styles = self._get_default_styles()
    
    def load_settings_config(self, config_file: str = "settings.json"):
        """加载设置项配置"""
        try:
            if Path(config_file).exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.settings_config = json.load(f)
                print(f"设置项配置已加载: {config_file}")
            else:
                print(f"设置项配置文件不存在: {config_file}")
        except Exception as e:
            print(f"加载设置项配置失败: {e}")
    
    def get_settings_categories(self) -> List[Dict[str, Any]]:
        """获取设置项分类列表"""
        return self.settings_config.get("categories", [])
    
    def get_settings_items(self, category_id: str = None) -> List[Dict[str, Any]]:
        """获取设置项列表，可选按分类筛选"""
        categories = self.get_settings_categories()
        all_items = []
        
        for category in categories:
            if category_id is None or category["id"] == category_id:
                all_items.extend(category.get("items", []))
        
        return all_items
    
    def get_settings_layout(self) -> Dict[str, Any]:
        """获取设置页面布局配置"""
        return self.settings_config.get("layout", {})
    
    def get_category_by_id(self, category_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取分类配置"""
        for category in self.get_settings_categories():
            if category["id"] == category_id:
                return category
        return None
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取设置项配置"""
        for category in self.get_settings_categories():
            for item in category.get("items", []):
                if item["id"] == item_id:
                    return item
        return None
    
    def calculate_category_position(self, index: int) -> Tuple[int, int]:
        """计算分类卡片位置"""
        layout = self.get_settings_layout()
        categories_per_row = layout.get("categories_per_row", 3)
        category_spacing = layout.get("category_spacing", 30)
        category_padding = layout.get("category_padding", 20)
        
        row = index // categories_per_row
        col = index % categories_per_row
        
        card_width = (self.screen_width - (categories_per_row + 1) * category_spacing) // categories_per_row
        x = category_spacing + col * (card_width + category_spacing)
        y = 150 + row * (200 + category_spacing)  # 假设卡片高度200px
        
        return x, y, card_width
    
    def calculate_item_position(self, category_index: int, item_index: int) -> Tuple[int, int]:
        """计算设置项位置"""
        layout = self.get_settings_layout()
        items_per_row = layout.get("items_per_row", 1)
        item_spacing = layout.get("item_spacing", 20)
        item_padding = layout.get("item_padding", 15)
        
        # 先计算分类位置
        cat_x, cat_y, cat_width = self.calculate_category_position(category_index)
        
        # 计算设置项位置
        if items_per_row == 1:
            # 单列布局
            x = cat_x + item_padding
            y = cat_y + 60 + item_index * (60 + item_spacing)  # 标题高度60px
            width = cat_width - 2 * item_padding
            return x, y, width, 50  # 设置项高度50px
        else:
            # 多列布局
            item_width = (cat_width - (items_per_row + 1) * item_padding) // items_per_row
            row = item_index // items_per_row
            col = item_index % items_per_row
            
            x = cat_x + item_padding + col * (item_width + item_padding)
            y = cat_y + 60 + row * (50 + item_spacing)
            return x, y, item_width, 50
    
    def get_animation_value(self, animation_name: str, progress: float) -> Dict[str, Any]:
        """获取动画效果值"""
        animations = self.styles.get("animations", {})
        animation_config = animations.get(animation_name, {})
        
        if not animation_config:
            return {}
        
        from_values = animation_config.get("from", {})
        to_values = animation_config.get("to", {})
        result = {}
        
        for key in from_values.keys():
            if key in to_values:
                start_val = from_values[key]
                end_val = to_values[key]
                
                # 简单的线性插值
                if isinstance(start_val, (int, float)) and isinstance(end_val, (int, float)):
                    result[key] = start_val + (end_val - start_val) * progress
                # 这里可以添加更多类型的插值支持
        
        return result
    
    def set_screen_size(self, width: int, height: int):
        """设置屏幕尺寸，用于响应式布局"""
        self.screen_width = width
        self.screen_height = height
    
    def set_theme(self, theme: str):
        """设置当前主题"""
        if theme in self.styles.get("themes", {}):
            self.current_theme = theme
            print(f"主题已切换为: {theme}")
        else:
            print(f"主题 {theme} 不存在，使用默认主题")
    
    def get_color(self, color_ref: Union[str, List]) -> Tuple[int, int, int, int]:
        """获取颜色值，支持颜色引用和直接颜色值"""
        if isinstance(color_ref, str):
            # 颜色引用，如 "text_color", "primary_color"
            theme_colors = self.styles.get("themes", {}).get(self.current_theme, {})
            if color_ref in theme_colors:
                color_value = theme_colors[color_ref]
                if isinstance(color_value, list):
                    return tuple(color_value + [255]) if len(color_value) == 3 else tuple(color_value)
            # 默认颜色
            return (255, 255, 255, 255)
        elif isinstance(color_ref, list):
            # 直接颜色值 [r, g, b] 或 [r, g, b, a]
            return tuple(color_ref + [255]) if len(color_ref) == 3 else tuple(color_ref)
        else:
            return (255, 255, 255, 255)
    
    def get_font(self, font_size: int, font_family: str = None) -> pygame.font.Font:
        """获取字体对象"""
        key = f"{font_size}_{font_family}"
        if key not in self.font_cache:
            if font_family:
                try:
                    self.font_cache[key] = pygame.font.Font(font_family, font_size)
                except:
                    self.font_cache[key] = pygame.font.Font(None, font_size)
            else:
                self.font_cache[key] = pygame.font.Font(None, font_size)
        return self.font_cache[key]
    
    def get_emoji_font(self, base_font_size: int) -> pygame.font.Font:
        """获取emoji字体，自动进行大小补偿"""
        # 获取emoji字体大小映射
        size_mapping = self.styles.get("emoji", {}).get("size_compensation", {})
        emoji_size = size_mapping.get(str(base_font_size), base_font_size + 8)
        
        key = f"emoji_{emoji_size}"
        if key not in self.emoji_font_cache:
            # 尝试加载emoji字体
            emoji_font_paths = self.styles.get("emoji", {}).get("font_paths", [])
            emoji_font = None
            
            for font_path in emoji_font_paths:
                if Path(font_path).exists():
                    try:
                        emoji_font = pygame.font.Font(font_path, emoji_size)
                        self.emoji_font_cache[key] = emoji_font
                        print(f"使用emoji字体: {Path(font_path).name}, 大小: {emoji_size}px")
                        break
                    except Exception as e:
                        print(f"无法加载emoji字体 {font_path}: {e}")
            
            if not emoji_font:
                # 回退到默认字体
                emoji_font = pygame.font.Font(None, emoji_size)
                self.emoji_font_cache[key] = emoji_font
                print(f"使用默认字体渲染emoji，大小: {emoji_size}px")
        
        return self.emoji_font_cache[key]
    
    def get_responsive_value(self, section: str, key: str, default_value: Any) -> Any:
        """获取响应式布局的值"""
        responsive_config = self.styles.get("responsive", {})
        
        # 按屏幕宽度降序排序
        breakpoints = sorted([int(bp) for bp in responsive_config.keys()], reverse=True)
        
        for breakpoint in breakpoints:
            if self.screen_width <= breakpoint:
                section_config = responsive_config.get(str(breakpoint), {}).get(section, {})
                if key in section_config:
                    return section_config[key]
        
        # 返回默认值
        return default_value
    
    def get_settings_style(self) -> Dict[str, Any]:
        """获取设置页面样式"""
        settings_config = self.styles.get("settings_page", {})
        
        # 应用响应式布局
        settings_config = self._apply_responsive_layout("settings_page", settings_config)
        
        return {
            "background": {
                "color": self.get_color(settings_config.get("background", {}).get("color", [0, 0, 0, 200])),
                "blur_radius": settings_config.get("background", {}).get("blur_radius", 0)
            },
            "title": {
                "font_size": settings_config.get("title", {}).get("font_size", 36),
                "color": self.get_color(settings_config.get("title", {}).get("color", "text_color")),
                "position": settings_config.get("title", {}).get("position", {"x": "center", "y": 100}),
                "alignment": settings_config.get("title", {}).get("alignment", "center")
            },
            "items": {
                "start_y": settings_config.get("items", {}).get("start_y", 200),
                "item_height": settings_config.get("items", {}).get("item_height", 80),
                "item_width": settings_config.get("items", {}).get("item_width", "80%"),
                "margin_left": settings_config.get("items", {}).get("margin_left", 100),
                "margin_right": settings_config.get("items", {}).get("margin_right", 100),
                "background": {
                    "normal": self.get_color(settings_config.get("items", {}).get("background", {}).get("normal", "secondary_color")),
                    "selected": self.get_color(settings_config.get("items", {}).get("background", {}).get("selected", "primary_color")),
                    "border_radius": settings_config.get("items", {}).get("background", {}).get("border_radius", 10),
                    "border_width": settings_config.get("items", {}).get("background", {}).get("border_width", 0)
                },
                "icon": settings_config.get("items", {}).get("icon", {}),
                "text": settings_config.get("items", {}).get("text", {}),
                "value": settings_config.get("items", {}).get("value", {})
            },
            "dropdown": settings_config.get("dropdown", {}),
            "instructions": settings_config.get("instructions", {})
        }
    
    def get_desktop_style(self) -> Dict[str, Any]:
        """获取桌面样式"""
        desktop_config = self.styles.get("desktop", {})
        
        # 应用响应式布局
        desktop_config = self._apply_responsive_layout("desktop", desktop_config)
        
        return {
            "app_icon": {
                "size": desktop_config.get("app_icon", {}).get("size", 200),
                "spacing": desktop_config.get("app_icon", {}).get("spacing", 100),
                "background": {
                    "normal": self.get_color(desktop_config.get("app_icon", {}).get("background", {}).get("normal", [100, 150, 255])),
                    "selected": self.get_color(desktop_config.get("app_icon", {}).get("background", {}).get("selected", [150, 200, 255])),
                    "border_color": {
                        "normal": self.get_color(desktop_config.get("app_icon", {}).get("background", {}).get("border_color", {}).get("normal", [128, 128, 128])),
                        "selected": self.get_color(desktop_config.get("app_icon", {}).get("background", {}).get("border_color", {}).get("selected", [255, 255, 255]))
                    },
                    "border_width": desktop_config.get("app_icon", {}).get("background", {}).get("border_width", {"normal": 2, "selected": 4}),
                    "border_radius": desktop_config.get("app_icon", {}).get("background", {}).get("border_radius", 20)
                },
                "icon": desktop_config.get("app_icon", {}).get("icon", {}),
                "name": desktop_config.get("app_icon", {}).get("name", {}),
                "description": desktop_config.get("app_icon", {}).get("description", {})
            },
            "title": desktop_config.get("title", {}),
            "instructions": desktop_config.get("instructions", {})
        }
    
    def get_file_browser_style(self) -> Dict[str, Any]:
        """获取文件浏览器样式"""
        file_browser_config = self.styles.get("file_browser", {})
        return {
            "background": file_browser_config.get("background", {}),
            "path_display": file_browser_config.get("path_display", {}),
            "file_item": file_browser_config.get("file_item", {})
        }
    
    def _apply_responsive_layout(self, section: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """应用响应式布局到配置"""
        # 这里可以添加更复杂的响应式逻辑
        # 目前简单返回原始配置，响应式逻辑在get_responsive_value中处理
        return config
    
    def _get_default_styles(self) -> Dict[str, Any]:
        """获取默认样式配置"""
        return {
            "version": "1.0.0",
            "description": "默认样式配置",
            "global": {
                "font_family": "WenQuanYi Micro Hei",
                "default_margin": 0,
                "default_padding": 0,
                "animation_duration": 0.2,
                "transition_speed": 0.1
            },
            "themes": {
                "dark": {
                    "primary_color": [100, 150, 255],
                    "secondary_color": [128, 128, 128],
                    "background_color": [0, 0, 0, 200],
                    "text_color": [255, 255, 255],
                    "highlight_color": [150, 200, 255],
                    "error_color": [255, 100, 100],
                    "success_color": [100, 255, 100]
                }
            },
            "emoji": {
                "font_size_mapping": {
                    "small": 24,
                    "medium": 32,
                    "large": 40
                },
                "font_paths": [
                    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
                ],
                "size_compensation": {
                    "16": 24,
                    "20": 28,
                    "24": 32,
                    "32": 40
                }
            },
            "settings_page": {
                "background": {
                    "color": [0, 0, 0, 200]
                },
                "title": {
                    "font_size": 36,
                    "color": "text_color"
                },
                "items": {
                    "start_y": 200,
                    "item_height": 80
                }
            },
            "desktop": {
                "app_icon": {
                    "size": 200,
                    "spacing": 100
                }
            }
        }


# 全局样式管理器实例
_global_style_manager = None

def get_style_manager(config_file: str = "styles.json") -> JSONStyleManager:
    """获取全局样式管理器实例"""
    global _global_style_manager
    if _global_style_manager is None:
        _global_style_manager = JSONStyleManager(config_file)
    return _global_style_manager

def set_global_style_manager(manager: JSONStyleManager):
    """设置全局样式管理器"""
    global _global_style_manager
    _global_style_manager = manager

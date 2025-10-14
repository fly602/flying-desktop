#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI布局配置系统
提供统一的布局配置管理，支持位置、格式、风格等设置
"""

import pygame
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any


@dataclass
class LayoutConfig:
    """布局配置类"""
    # 通用布局参数
    margin: int = 20           # 边距
    padding: int = 10          # 内边距
    spacing: int = 15          # 元素间距
    border_radius: int = 10     # 边框圆角
    
    # 字体大小配置
    font_large_size: int = 36
    font_medium_size: int = 24
    font_small_size: int = 18
    
    # 颜色配置
    colors: Dict[str, Tuple[int, int, int]] = None
    
    # 动画配置
    animation_duration: float = 0.2  # 动画持续时间（秒）
    transition_speed: float = 0.1   # 过渡速度
    
    def __post_init__(self):
        if self.colors is None:
            self.colors = {
                'black': (0, 0, 0),
                'white': (255, 255, 255),
                'blue': (100, 150, 255),
                'light_blue': (150, 200, 255),
                'gray': (128, 128, 128),
                'green': (100, 255, 100),
                'red': (255, 100, 100),
                'dark_gray': (40, 40, 40),
                'transparent': (0, 0, 0, 0)
            }


@dataclass
class SettingsLayout:
    """设置页面布局配置"""
    # 标题位置
    title_y: int = 100
    title_center: bool = True
    
    # 设置项布局
    items_start_y: int = 200
    item_height: int = 80
    item_width_percent: float = 0.8  # 相对于屏幕宽度的百分比
    item_margin_left: int = 100
    item_margin_right: int = 100
    
    # 图标布局
    icon_width: int = 40
    icon_x: int = 120
    icon_text_spacing: int = 10
    
    # 值显示位置
    value_margin_right: int = 120
    
    # 下拉框布局
    dropdown_min_width: int = 200
    dropdown_max_width: int = 500
    dropdown_item_height: int = 40
    dropdown_padding: int = 8
    dropdown_margin: int = 50
    
    # 操作说明位置
    instructions_y_start: int = -120  # 相对于屏幕底部
    instructions_spacing: int = 25


class UILayoutManager:
    """UI布局管理器"""
    
    def __init__(self, config=None):
        self.config = config or LayoutConfig()
        self.settings_layout = SettingsLayout()
        
        # 缓存的字体对象
        self._fonts = {}
        
    def get_font(self, size: int, font_path: str = None) -> pygame.font.Font:
        """获取字体对象"""
        key = f"{size}_{font_path}"
        if key not in self._fonts:
            if font_path:
                try:
                    self._fonts[key] = pygame.font.Font(font_path, size)
                except:
                    self._fonts[key] = pygame.font.Font(None, size)
            else:
                self._fonts[key] = pygame.font.Font(None, size)
        return self._fonts[key]
    
    def get_color(self, color_name: str) -> Tuple[int, int, int]:
        """获取颜色"""
        return self.config.colors.get(color_name, self.config.colors['white'])
    
    def calculate_item_rect(self, screen_width: int, index: int) -> pygame.Rect:
        """计算设置项矩形区域"""
        layout = self.settings_layout
        y = layout.items_start_y + index * layout.item_height
        width = screen_width - layout.item_margin_left - layout.item_margin_right
        return pygame.Rect(layout.item_margin_left, y - 20, width, 60)
    
    def calculate_icon_position(self, y: int) -> Tuple[int, int]:
        """计算图标位置"""
        layout = self.settings_layout
        return layout.icon_x + layout.icon_width // 2, y
    
    def calculate_text_position(self, y: int) -> int:
        """计算文字起始位置"""
        layout = self.settings_layout
        return layout.icon_x + layout.icon_width + layout.icon_text_spacing
    
    def calculate_value_position(self, screen_width: int, y: int) -> Tuple[int, int]:
        """计算值显示位置"""
        layout = self.settings_layout
        return screen_width - layout.value_margin_right, y
    
    def calculate_dropdown_dimensions(self, screen_width: int, screen_height: int, 
                                    item_count: int, max_text_width: int) -> Tuple[int, int, int, int]:
        """计算下拉框尺寸和位置"""
        layout = self.settings_layout
        config = self.config
        
        # 计算宽度
        min_width = layout.dropdown_min_width
        max_width = min(layout.dropdown_max_width, screen_width - 100)
        list_width = max(min_width, max_text_width + 80)
        list_width = min(list_width, max_width)
        
        # 计算高度
        list_height = item_count * layout.dropdown_item_height + layout.dropdown_padding * 2
        
        # 计算位置
        list_x = (screen_width - list_width) // 2
        
        return list_x, list_width, list_height
    
    def create_overlay(self, screen_width: int, screen_height: int, alpha: int = 120) -> pygame.Surface:
        """创建半透明遮罩"""
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(alpha)
        overlay.fill(self.get_color('black'))
        return overlay
    
    def get_instructions_position(self, screen_height: int, index: int) -> int:
        """获取操作说明位置"""
        layout = self.settings_layout
        return screen_height + layout.instructions_y_start + index * layout.instructions_spacing
    
    def apply_animation(self, current_value: float, target_value: float, delta_time: float) -> float:
        """应用动画效果"""
        speed = self.config.transition_speed
        return current_value + (target_value - current_value) * speed * delta_time
    
    def load_from_config(self, config_data: Dict[str, Any]):
        """从配置数据加载布局设置"""
        if 'layout' in config_data:
            layout_data = config_data['layout']
            
            # 更新通用配置
            if 'margin' in layout_data:
                self.config.margin = layout_data['margin']
            if 'padding' in layout_data:
                self.config.padding = layout_data['padding']
            if 'spacing' in layout_data:
                self.config.spacing = layout_data['spacing']
            if 'border_radius' in layout_data:
                self.config.border_radius = layout_data['border_radius']
            
            # 更新字体大小
            if 'font_sizes' in layout_data:
                font_sizes = layout_data['font_sizes']
                if 'large' in font_sizes:
                    self.config.font_large_size = font_sizes['large']
                if 'medium' in font_sizes:
                    self.config.font_medium_size = font_sizes['medium']
                if 'small' in font_sizes:
                    self.config.font_small_size = font_sizes['small']
            
            # 更新颜色
            if 'colors' in layout_data:
                for color_name, color_value in layout_data['colors'].items():
                    if isinstance(color_value, list) and len(color_value) >= 3:
                        self.config.colors[color_name] = tuple(color_value[:3])
        
        if 'settings_layout' in config_data:
            settings_data = config_data['settings_layout']
            layout = self.settings_layout
            
            # 更新设置页面布局
            for key, value in settings_data.items():
                if hasattr(layout, key):
                    setattr(layout, key, value)


# 默认布局配置实例
default_layout = UILayoutManager()


def create_layout_config(theme: str = "default") -> UILayoutManager:
    """创建主题化的布局配置"""
    if theme == "dark":
        config = LayoutConfig()
        config.colors.update({
            'black': (20, 20, 20),
            'white': (220, 220, 220),
            'blue': (80, 130, 235),
            'gray': (80, 80, 80),
            'dark_gray': (30, 30, 30)
        })
        return UILayoutManager(config)
    elif theme == "light":
        config = LayoutConfig()
        config.colors.update({
            'black': (240, 240, 240),
            'white': (30, 30, 30),
            'blue': (50, 100, 200),
            'gray': (200, 200, 200),
            'dark_gray': (180, 180, 180)
        })
        return UILayoutManager(config)
    else:
        return default_layout

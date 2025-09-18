#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件浏览器模块
用于选择.desktop和.AppImage文件
"""

import pygame
from pathlib import Path
import os


class FileBrowser:
    """文件浏览器"""
    
    def __init__(self, i18n, audio):
        self.i18n = i18n
        self.audio = audio
        
        # 当前路径和文件列表
        self.current_path = Path.home()
        self.files = []
        self.directories = []
        self.selected_index = 0
        self.scroll_offset = 0
        
        # 支持的文件类型
        self.supported_extensions = ['.desktop', '.AppImage']
        
        # 常用路径
        self.common_paths = [
            Path.home(),
            Path.home() / "Downloads",
            Path.home() / "Desktop",
            Path.home() / "Applications",
            Path("/usr/share/applications"),
            Path("/usr/local/share/applications"),
            Path("/opt"),
        ]
        
        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (100, 150, 255)
        self.LIGHT_BLUE = (150, 200, 255)
        self.GRAY = (128, 128, 128)
        self.GREEN = (100, 255, 100)
        self.YELLOW = (255, 255, 100)
        
        # 刷新文件列表
        self.refresh_files()
    
    def refresh_files(self):
        """刷新当前路径的文件列表"""
        try:
            self.directories = []
            self.files = []
            
            # 添加返回上级目录选项
            if self.current_path != self.current_path.parent:
                self.directories.append({
                    'name': '..',
                    'path': self.current_path.parent,
                    'type': 'parent'
                })
            
            # 添加常用路径（仅在根目录显示）
            if self.current_path == Path.home():
                for common_path in self.common_paths:
                    if (common_path != self.current_path and 
                        common_path.exists() and 
                        common_path.is_dir()):
                        self.directories.append({
                            'name': f"📁 {common_path.name}",
                            'path': common_path,
                            'type': 'common'
                        })
            
            # 扫描当前目录
            if self.current_path.exists() and self.current_path.is_dir():
                try:
                    items = list(self.current_path.iterdir())
                    items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
                    
                    for item in items:
                        if item.name.startswith('.'):
                            continue
                            
                        if item.is_dir():
                            self.directories.append({
                                'name': item.name,
                                'path': item,
                                'type': 'directory'
                            })
                        elif item.is_file():
                            # 只显示支持的文件类型
                            if any(item.name.lower().endswith(ext.lower()) 
                                   for ext in self.supported_extensions):
                                self.files.append({
                                    'name': item.name,
                                    'path': item,
                                    'type': 'file',
                                    'extension': item.suffix.lower()
                                })
                
                except PermissionError:
                    print(f"无权限访问目录: {self.current_path}")
            
            # 重置选择索引
            self.selected_index = 0
            self.scroll_offset = 0
            
        except Exception as e:
            print(f"刷新文件列表失败: {e}")
    
    def get_all_items(self):
        """获取所有项目（目录+文件）"""
        return self.directories + self.files
    
    def handle_input(self, event):
        """处理输入事件"""
        if event.type == pygame.KEYDOWN:
            all_items = self.get_all_items()
            
            if event.key == pygame.K_UP:
                if all_items:
                    self.selected_index = (self.selected_index - 1) % len(all_items)
                    self.audio.play('select')
            elif event.key == pygame.K_DOWN:
                if all_items:
                    self.selected_index = (self.selected_index + 1) % len(all_items)
                    self.audio.play('select')
            elif event.key == pygame.K_RETURN:
                if all_items and self.selected_index < len(all_items):
                    selected_item = all_items[self.selected_index]
                    
                    if selected_item['type'] in ['directory', 'parent', 'common']:
                        # 进入目录
                        self.current_path = selected_item['path']
                        self.refresh_files()
                        self.audio.play('confirm')
                    elif selected_item['type'] == 'file':
                        # 选择文件
                        self.audio.play('confirm')
                        return 'file_selected', selected_item['path']
            elif event.key == pygame.K_ESCAPE:
                self.audio.play('back')
                return 'cancel', None
            elif event.key == pygame.K_BACKSPACE:
                # 返回上级目录
                if self.current_path != self.current_path.parent:
                    self.current_path = self.current_path.parent
                    self.refresh_files()
                    self.audio.play('back')
        
        return None, None
    
    def render(self, screen, font_large, font_medium, font_small):
        """渲染文件浏览器"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # 绘制半透明背景
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(220)
        overlay.fill(self.BLACK)
        screen.blit(overlay, (0, 0))
        
        # 绘制标题
        title_text = font_large.render("选择应用文件", True, self.WHITE)
        title_rect = title_text.get_rect(center=(screen_width // 2, 60))
        screen.blit(title_text, title_rect)
        
        # 绘制当前路径
        path_text = f"路径: {self.current_path}"
        if len(path_text) > 80:
            path_text = "..." + path_text[-77:]
        path_surface = font_small.render(path_text, True, self.GRAY)
        screen.blit(path_surface, (50, 100))
        
        # 绘制文件列表
        all_items = self.get_all_items()
        list_start_y = 140
        item_height = 35
        visible_items = (screen_height - list_start_y - 100) // item_height
        
        # 计算滚动偏移
        if self.selected_index >= self.scroll_offset + visible_items:
            self.scroll_offset = self.selected_index - visible_items + 1
        elif self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        
        # 绘制文件项
        for i in range(visible_items):
            item_index = self.scroll_offset + i
            if item_index >= len(all_items):
                break
            
            item = all_items[item_index]
            y = list_start_y + i * item_height
            is_selected = (item_index == self.selected_index)
            
            # 绘制项目背景
            item_rect = pygame.Rect(50, y, screen_width - 100, item_height - 2)
            if is_selected:
                pygame.draw.rect(screen, self.BLUE, item_rect, border_radius=5)
                text_color = self.WHITE
            else:
                text_color = self.WHITE
            
            # 选择图标和颜色
            if item['type'] == 'parent':
                icon = "📁 .."
                name_color = self.YELLOW
            elif item['type'] in ['directory', 'common']:
                icon = "📁"
                name_color = self.YELLOW
            elif item['type'] == 'file':
                if item['extension'] == '.desktop':
                    icon = "🖥️"
                    name_color = self.GREEN
                elif item['extension'] == '.appimage':
                    icon = "📦"
                    name_color = self.LIGHT_BLUE
                else:
                    icon = "📄"
                    name_color = self.WHITE
            else:
                icon = "❓"
                name_color = self.WHITE
            
            # 绘制图标
            icon_surface = font_medium.render(icon, True, text_color)
            screen.blit(icon_surface, (60, y + 5))
            
            # 绘制文件名
            name_text = item['name']
            if len(name_text) > 60:
                name_text = name_text[:57] + "..."
            
            name_surface = font_medium.render(name_text, True, name_color if not is_selected else text_color)
            screen.blit(name_surface, (100, y + 5))
        
        # 绘制滚动条
        if len(all_items) > visible_items:
            scrollbar_height = visible_items * item_height
            scrollbar_x = screen_width - 30
            scrollbar_y = list_start_y
            
            # 滚动条背景
            pygame.draw.rect(screen, self.GRAY, 
                           (scrollbar_x, scrollbar_y, 10, scrollbar_height))
            
            # 滚动条滑块
            thumb_height = max(20, scrollbar_height * visible_items // len(all_items))
            thumb_y = scrollbar_y + (scrollbar_height - thumb_height) * self.scroll_offset // max(1, len(all_items) - visible_items)
            pygame.draw.rect(screen, self.WHITE, 
                           (scrollbar_x, thumb_y, 10, thumb_height))
        
        # 绘制操作说明
        instructions = [
            "↑↓: 选择文件/目录",
            "回车: 进入目录或选择文件",
            "Backspace: 返回上级目录",
            "ESC: 取消"
        ]
        
        y_start = screen_height - 120
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, self.WHITE)
            text_rect = text.get_rect(center=(screen_width // 2, y_start + i * 20))
            screen.blit(text, text_rect)
        
        # 绘制文件类型提示
        file_types = "支持的文件类型: .desktop, .AppImage"
        type_surface = font_small.render(file_types, True, self.GRAY)
        type_rect = type_surface.get_rect(center=(screen_width // 2, screen_height - 30))
        screen.blit(type_surface, type_rect)
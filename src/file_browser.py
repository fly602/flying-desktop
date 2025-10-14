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
                            'name': common_path.name,
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
    
    def handle_long_press_scroll(self, direction):
        """处理长按滚动"""
        all_items = self.get_all_items()
        if not all_items:
            return
            
        if direction == 'up':
            self.selected_index = (self.selected_index - 1) % len(all_items)
            self.audio.play('select')
        elif direction == 'down':
            self.selected_index = (self.selected_index + 1) % len(all_items)
            self.audio.play('select')
    
    def render(self, screen, font_large, font_medium, font_small):
        """渲染现代化文件浏览器 - 完美对齐版本"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # 绘制半透明背景遮罩
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 计算主容器尺寸和位置
        container_width = min(850, screen_width - 80)
        container_height = screen_height - 100
        container_x = (screen_width - container_width) // 2
        container_y = 50
        
        # 绘制主容器背景
        container_bg = pygame.Surface((container_width, container_height), pygame.SRCALPHA)
        container_bg.fill((40, 42, 50, 245))
        screen.blit(container_bg, (container_x, container_y))
        
        # 绘制容器边框和高光
        pygame.draw.rect(screen, (120, 125, 140), (container_x, container_y, container_width, container_height), 2, border_radius=15)
        pygame.draw.rect(screen, (160, 165, 180, 100), (container_x + 1, container_y + 1, container_width - 2, 3), border_radius=12)
        
        # 绘制标题
        title_y = container_y + 35
        title_surface = font_large.render("选择应用文件", True, (255, 255, 255))
        title_x = container_x + (container_width - title_surface.get_width()) // 2
        screen.blit(title_surface, (title_x, title_y))
        
        # 绘制路径显示区域
        path_area_y = title_y + 60
        path_area_height = 40
        path_area_x = container_x + 25
        path_area_width = container_width - 50
        
        # 路径区域背景
        path_bg = pygame.Surface((path_area_width, path_area_height), pygame.SRCALPHA)
        path_bg.fill((55, 58, 65, 200))
        screen.blit(path_bg, (path_area_x, path_area_y))
        pygame.draw.rect(screen, (90, 95, 105), (path_area_x, path_area_y, path_area_width, path_area_height), 1, border_radius=8)
        
        # 路径文字
        path_text = f"当前路径: {self.current_path}"
        if len(str(self.current_path)) > 65:
            path_text = f"当前路径: ...{str(self.current_path)[-62:]}"
        path_surface = font_small.render(path_text, True, (200, 205, 210))
        path_text_y = path_area_y + (path_area_height - path_surface.get_height()) // 2
        screen.blit(path_surface, (path_area_x + 15, path_text_y))
        
        # 计算文件列表区域
        list_area_y = path_area_y + path_area_height + 25
        list_area_height = container_height - (list_area_y - container_y) - 70
        item_height = 48
        visible_items = list_area_height // item_height
        
        # 获取所有文件项
        all_items = self.get_all_items()
        
        # 计算滚动偏移
        if self.selected_index >= self.scroll_offset + visible_items:
            self.scroll_offset = self.selected_index - visible_items + 1
        elif self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        
        # 绘制文件列表项
        for i in range(visible_items):
            item_index = self.scroll_offset + i
            if item_index >= len(all_items):
                break
            
            item = all_items[item_index]
            item_y = list_area_y + i * item_height
            is_selected = (item_index == self.selected_index)
            
            # 计算项目区域
            item_x = container_x + 20
            item_width = container_width - 40
            
            # 绘制项目背景
            if is_selected:
                # 选中项背景 - 渐变效果
                selected_bg = pygame.Surface((item_width, item_height - 6), pygame.SRCALPHA)
                for j in range(item_height - 6):
                    progress = j / (item_height - 6)
                    r = int(65 + progress * 25)
                    g = int(105 + progress * 25)
                    b = int(200 - progress * 30)
                    alpha = int(220 - progress * 40)
                    pygame.draw.line(selected_bg, (r, g, b), (0, j), (item_width, j))
                screen.blit(selected_bg, (item_x, item_y + 3))
                
                # 选中项边框
                pygame.draw.rect(screen, (90, 140, 255), (item_x, item_y + 3, item_width, item_height - 6), 2, border_radius=10)
                text_color = (255, 255, 255)
            else:
                # 未选中项背景
                normal_bg = pygame.Surface((item_width, item_height - 6), pygame.SRCALPHA)
                normal_bg.fill((50, 53, 60, 100))
                screen.blit(normal_bg, (item_x, item_y + 3))
                pygame.draw.rect(screen, (70, 75, 85), (item_x, item_y + 3, item_width, item_height - 6), 1, border_radius=10)
                text_color = (210, 215, 220)
            
            # 绘制文件类型图标
            icon_x = item_x + 25
            icon_y = item_y + item_height // 2
            icon_radius = 10
            
            # 根据文件类型绘制不同图标
            if item['type'] == 'parent':
                # 返回上级 - 左箭头
                arrow_points = [
                    (icon_x + 6, icon_y - 6),
                    (icon_x - 6, icon_y),
                    (icon_x + 6, icon_y + 6)
                ]
                pygame.draw.polygon(screen, (255, 200, 100), arrow_points)
                name_color = (255, 200, 100)
                
            elif item['type'] in ['directory', 'common']:
                # 文件夹 - 文件夹图标
                pygame.draw.rect(screen, (255, 200, 100), (icon_x - 8, icon_y - 4, 16, 8), 2)
                pygame.draw.rect(screen, (255, 200, 100), (icon_x - 4, icon_y - 8, 8, 4), 2)
                name_color = (255, 200, 100)
                
            elif item['type'] == 'file':
                if item['extension'] == '.desktop':
                    # Desktop应用文件 - 应用图标
                    pygame.draw.rect(screen, (100, 255, 150), (icon_x - 6, icon_y - 6, 12, 12), 2)
                    pygame.draw.circle(screen, (100, 255, 150), (icon_x, icon_y), 3)
                    name_color = (100, 255, 150)
                    
                elif item['extension'] == '.appimage':
                    # AppImage文件 - 六边形
                    import math
                    hex_points = []
                    for k in range(6):
                        angle = k * math.pi / 3
                        px = icon_x + 8 * math.cos(angle)
                        py = icon_y + 8 * math.sin(angle)
                        hex_points.append((px, py))
                    pygame.draw.polygon(screen, (100, 180, 255), hex_points, 2)
                    name_color = (100, 180, 255)
                    
                else:
                    # 其他文件 - 文档图标
                    pygame.draw.rect(screen, (200, 200, 200), (icon_x - 5, icon_y - 8, 10, 16), 2)
                    pygame.draw.line(screen, (200, 200, 200), (icon_x - 3, icon_y - 4), (icon_x + 3, icon_y - 4))
                    pygame.draw.line(screen, (200, 200, 200), (icon_x - 3, icon_y), (icon_x + 3, icon_y))
                    pygame.draw.line(screen, (200, 200, 200), (icon_x - 3, icon_y + 4), (icon_x + 3, icon_y + 4))
                    name_color = (200, 200, 200)
            else:
                # 未知类型 - 问号
                pygame.draw.circle(screen, (150, 150, 150), (icon_x, icon_y), 8, 2)
                name_color = (150, 150, 150)
            
            # 绘制文件名 - 使用精确的垂直居中
            name_text = item['name']
            name_x = item_x + 60
            max_text_width = item_width - 80
            
            # 文字截断处理
            if font_small.size(name_text)[0] > max_text_width:
                while font_small.size(name_text + "...")[0] > max_text_width and len(name_text) > 1:
                    name_text = name_text[:-1]
                name_text += "..."
            
            # 渲染文字并精确居中
            name_surface = font_small.render(name_text, True, name_color if not is_selected else text_color)
            name_y = item_y + (item_height - name_surface.get_height()) // 2
            screen.blit(name_surface, (name_x, name_y))
        
        # 绘制滚动条
        if len(all_items) > visible_items:
            scrollbar_x = container_x + container_width - 15
            scrollbar_y = list_area_y
            scrollbar_width = 6
            scrollbar_height = list_area_height
            
            # 滚动条轨道
            track_bg = pygame.Surface((scrollbar_width, scrollbar_height), pygame.SRCALPHA)
            track_bg.fill((70, 75, 85, 150))
            screen.blit(track_bg, (scrollbar_x, scrollbar_y))
            pygame.draw.rect(screen, (90, 95, 105), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), 1, border_radius=3)
            
            # 滚动条滑块
            thumb_height = max(25, scrollbar_height * visible_items // len(all_items))
            thumb_y = scrollbar_y + (scrollbar_height - thumb_height) * self.scroll_offset // max(1, len(all_items) - visible_items)
            
            thumb_bg = pygame.Surface((scrollbar_width - 2, thumb_height), pygame.SRCALPHA)
            thumb_bg.fill((140, 145, 155, 220))
            screen.blit(thumb_bg, (scrollbar_x + 1, thumb_y))
            pygame.draw.rect(screen, (170, 175, 185), (scrollbar_x + 1, thumb_y, scrollbar_width - 2, thumb_height), 1, border_radius=2)
        
        # 绘制底部操作提示
        footer_y = container_y + container_height - 45
        footer_bg = pygame.Surface((container_width - 30, 35), pygame.SRCALPHA)
        footer_bg.fill((30, 32, 38, 200))
        screen.blit(footer_bg, (container_x + 15, footer_y))
        pygame.draw.rect(screen, (60, 65, 75), (container_x + 15, footer_y, container_width - 30, 35), 1, border_radius=8)
        
        # 操作提示文字
        help_text = "↑↓ 选择文件  回车 确认选择  Backspace 返回上级  ESC 取消  支持 .desktop 和 .AppImage 文件"
        help_surface = font_small.render(help_text, True, (160, 165, 175))
        help_x = container_x + (container_width - help_surface.get_width()) // 2
        help_y = footer_y + (35 - help_surface.get_height()) // 2
        screen.blit(help_surface, (help_x, help_y))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置页面模块
"""

import os
import pygame
from pathlib import Path
from .font_detector import FontDetector
from .file_browser import FileBrowser
from .json_style_manager import get_style_manager


class SettingsPage:
    """设置页面"""
    
    def __init__(self, config, i18n, audio_manager, app_config_loader=None):
        self.config = config
        self.i18n = i18n
        self.audio = audio_manager
        self.app_config_loader = app_config_loader
        
        # 初始化样式管理器
        self.style_manager = get_style_manager()
        
        # 文件浏览器状态
        self.file_browser = None
        self.in_file_browser = False
        
        # 初始化字体检测器
        self.font_detector = FontDetector()
        print("正在检测系统字体...")
        available_fonts = self.font_detector.detect_system_fonts()
        font_options = self.font_detector.get_font_options()
        self.font_names = self.font_detector.get_font_names()
        
        print(f"检测到 {len(available_fonts)} 个可用字体:")
        for font in available_fonts:
            print(f"  - {font['name']} ({font['key']})")
        
        # 缓存emoji字体路径
        self.emoji_font_path = self.font_detector.get_emoji_font()
        
        # 设置项列表（增加图标支持）
        self.settings_items = [
            {
                'key': 'add_app',
                'type': 'action',
                'current': None,
                'icon': '➕'  # 添加图标
            },
            {
                'key': 'resolution',
                'type': 'select',
                'options': ['auto', '1920x1080', '1366x768', '1280x720', '1024x768', '800x600'],
                'current': self.get_current_resolution(),
                'icon': '📺'  # 分辨率图标
            },
            {
                'key': 'language',
                'type': 'select', 
                'options': ['zh_CN', 'en_US', 'ja_JP'],
                'current': config.get('ui.language', 'zh_CN'),
                'icon': '🌐'  # 语言图标
            },
            {
                'key': 'font',
                'type': 'select',
                'options': font_options,  # 使用动态检测的字体列表
                'current': self.get_current_font(),
                'icon': '🔤'  # 字体图标
            },
            {
                'key': 'sound_effects',
                'type': 'toggle',
                'current': config.get('audio.sound_effects', True),
                'icon': '🔊'  # 音效图标
            }
        ]
        
        self.selected_item = 0
        self.in_option_select = False
        self.selected_option = 0
        
        # 从样式管理器获取颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = self.style_manager.get_color("text_color")
        self.BLUE = self.style_manager.get_color("primary_color")
        self.LIGHT_BLUE = self.style_manager.get_color("highlight_color")
        self.GRAY = self.style_manager.get_color("secondary_color")
        self.GREEN = self.style_manager.get_color("success_color")
        self.RED = self.style_manager.get_color("error_color")
    
    def get_current_resolution(self):
        """获取当前分辨率设置"""
        width = self.config.get('display.width', 0)
        height = self.config.get('display.height', 0)
        
        if width == 0 or height == 0:
            return 'auto'
        
        return f"{width}x{height}"
    
    def get_current_font(self):
        """获取当前字体设置"""
        font_path = self.config.get('desktop.font_path')
        if not font_path:
            return 'auto'
        
        # 在检测到的字体中查找匹配的字体
        for font in self.font_detector.get_available_fonts_info():
            if font['path'] == font_path:
                return font['key']
        
        # 如果没找到匹配的，返回auto
        return 'auto'
    
    def handle_input(self, event):
        """处理输入事件"""
        if event.type == pygame.KEYDOWN:
            if self.in_file_browser:
                return self.handle_file_browser_input(event)
            elif self.in_option_select:
                return self.handle_option_input(event)
            else:
                return self.handle_menu_input(event)
        
        return None
    
    def handle_menu_input(self, event):
        """处理菜单输入"""
        if event.key == pygame.K_UP:
            self.selected_item = (self.selected_item - 1) % len(self.settings_items)
            self.audio.play('select')
        elif event.key == pygame.K_DOWN:
            self.selected_item = (self.selected_item + 1) % len(self.settings_items)
            self.audio.play('select')
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            # 进入选项选择模式
            item = self.settings_items[self.selected_item]
            if item['type'] == 'action':
                # 执行动作
                if item['key'] == 'add_app':
                    self.in_file_browser = True
                    self.file_browser = FileBrowser(self.i18n, self.audio)
                    self.audio.play('confirm')
            elif item['type'] == 'toggle':
                # 直接切换布尔值
                item['current'] = not item['current']
                self.audio.play('confirm')
            else:
                # 进入选项选择
                self.in_option_select = True
                self.selected_option = item['options'].index(item['current'])
                self.audio.play('confirm')
        elif event.key == pygame.K_ESCAPE:
            self.audio.play('back')
            return 'back'
        elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
            # Ctrl+S 保存设置
            self.save_settings()
            self.audio.play('confirm')
            return 'saved'
        
        return None
    
    def handle_option_input(self, event):
        """处理选项选择输入"""
        item = self.settings_items[self.selected_item]
        
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(item['options'])
            self.audio.play('select')
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(item['options'])
            self.audio.play('select')
        elif event.key == pygame.K_LEFT:
            self.selected_option = (self.selected_option - 1) % len(item['options'])
            self.audio.play('select')
        elif event.key == pygame.K_RIGHT:
            self.selected_option = (self.selected_option + 1) % len(item['options'])
            self.audio.play('select')
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            # 确认选择
            item['current'] = item['options'][self.selected_option]
            self.in_option_select = False
            self.audio.play('confirm')
            
            # 特殊处理语言切换
            if item['key'] == 'language':
                self.i18n.set_language(item['current'])
                
            # 自动保存设置
            self.save_settings()
        elif event.key == pygame.K_ESCAPE:
            # 取消选择
            self.in_option_select = False
            self.selected_option = item['options'].index(item['current'])
            self.audio.play('back')
            return 'back'  # 返回back信号，让上层可以处理退出
        
        return None
    
    def handle_long_press_scroll(self, direction):
        """处理长按滚动（用于设置页面、下拉选择和文件浏览器）"""
        if self.in_file_browser and self.file_browser:
            # 在文件浏览器模式中滚动
            self.file_browser.handle_long_press_scroll(direction)
        elif self.in_option_select:
            # 在下拉选择模式中滚动
            item = self.settings_items[self.selected_item]
            if direction == 'up':
                self.selected_option = (self.selected_option - 1) % len(item['options'])
                self.audio.play('select')
            elif direction == 'down':
                self.selected_option = (self.selected_option + 1) % len(item['options'])
                self.audio.play('select')
        else:
            # 在设置菜单中滚动
            if direction == 'up':
                self.selected_item = (self.selected_item - 1) % len(self.settings_items)
                self.audio.play('select')
            elif direction == 'down':
                self.selected_item = (self.selected_item + 1) % len(self.settings_items)
                self.audio.play('select')
    
    def handle_file_browser_input(self, event):
        """处理文件浏览器输入"""
        if not self.file_browser:
            return None
        
        action, result = self.file_browser.handle_input(event)
        
        if action == 'file_selected':
            # 文件被选中，尝试添加应用
            self.in_file_browser = False
            self.file_browser = None
            
            if self.app_config_loader:
                success, message = self.add_application(result)
                if success:
                    self.audio.play('confirm')
                    return 'app_added'
                else:
                    self.audio.play('error')
                    print(f"添加应用失败: {message}")
            
        elif action == 'cancel':
            # 取消文件选择
            self.in_file_browser = False
            self.file_browser = None
            self.audio.play('back')
        
        return None
    
    def add_application(self, file_path):
        """添加应用"""
        try:
            file_path = Path(file_path)
            
            if file_path.suffix.lower() == '.desktop':
                return self.app_config_loader.add_desktop_file(str(file_path))
            elif file_path.suffix.lower() == '.appimage':
                return self.app_config_loader.add_appimage_file(str(file_path))
            else:
                return False, "不支持的文件类型"
                
        except Exception as e:
            return False, str(e)
    
    def save_settings(self):
        """保存设置到配置文件"""
        # 更新配置
        for item in self.settings_items:
            if item['key'] == 'resolution':
                if item['current'] == 'auto':
                    self.config.config['display'] = {'width': 0, 'height': 0, 'fullscreen': True}
                else:
                    width, height = item['current'].split('x')
                    self.config.config['display'] = {
                        'width': int(width),
                        'height': int(height),
                        'fullscreen': False
                    }
            elif item['key'] == 'language':
                if 'ui' not in self.config.config:
                    self.config.config['ui'] = {}
                self.config.config['ui']['language'] = item['current']
            elif item['key'] == 'font':
                # 使用字体检测器获取字体路径
                font_path = self.font_detector.get_font_path(item['current'])
                self.config.config['desktop']['font_path'] = font_path
            elif item['key'] == 'sound_effects':
                if 'audio' not in self.config.config:
                    self.config.config['audio'] = {}
                self.config.config['audio']['sound_effects'] = item['current']
                self.audio.set_enabled(item['current'])
        
        # 保存到用户配置文件
        self.config.save_user_config()
        print("设置已保存")
    
    def render(self, screen, font_large, font_medium, font_small):
        """渲染设置页面 - 全新设计"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # 绘制半透明背景遮罩
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # 绘制设置标题
        title_text = font_large.render(self.i18n.t('settings'), True, self.WHITE)
        title_rect = title_text.get_rect(center=(screen_width // 2, 80))
        screen.blit(title_text, title_rect)
        
        # 设置项布局参数
        start_y = 160
        item_height = 60
        item_spacing = 8
        content_width = min(800, screen_width - 200)
        content_x = (screen_width - content_width) // 2
        
        # 记录下拉框信息
        dropdown_item = None
        dropdown_y = 0
        
        for i, item in enumerate(self.settings_items):
            y = start_y + i * (item_height + item_spacing)
            is_selected = (i == self.selected_item)
            
            # 绘制设置项卡片
            self._render_setting_item(screen, font_small, item, content_x, y, content_width, item_height, is_selected)
            
            # 记录需要绘制下拉框的项目
            if is_selected and self.in_option_select and item['type'] not in ['toggle', 'action']:
                dropdown_item = item
                dropdown_y = y + item_height + 5
        
        # 绘制操作说明
        self._render_instructions(screen, font_small, screen_width, screen_height)
        
        # 最后绘制下拉框（确保在最上层）
        if dropdown_item:
            self._render_dropdown(screen, font_small, dropdown_item, dropdown_y, content_x, content_width)
        
        # 如果在文件浏览器模式，绘制文件浏览器
        if self.in_file_browser and self.file_browser:
            self.file_browser.render(screen, font_large, font_medium, font_small)
    
    def _render_setting_item(self, screen, font, item, x, y, width, height, is_selected):
        """渲染单个设置项"""
        # 背景颜色
        if is_selected:
            bg_color = (60, 100, 180, 200)  # 半透明蓝色
            border_color = (100, 150, 255)
            text_color = self.WHITE
        else:
            bg_color = (40, 40, 40, 150)  # 半透明深灰
            border_color = (80, 80, 80)
            text_color = (220, 220, 220)
        
        # 绘制背景（使用半透明surface）
        item_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        item_surface.fill(bg_color)
        screen.blit(item_surface, (x, y))
        
        # 绘制边框
        border_width = 2 if is_selected else 1
        pygame.draw.rect(screen, border_color, (x, y, width, height), border_width, border_radius=8)
        
        # 绘制美观的几何图标
        if 'icon' in item:
            icon_x = x + 20
            icon_y = y + height // 2
            icon_size = 8  # 图标尺寸
            
            # 根据不同的emoji绘制对应的几何图标
            if item['icon'] == '➕':  # 添加应用
                # 绘制加号
                pygame.draw.rect(screen, text_color, (icon_x - icon_size//2, icon_y - 1, icon_size, 2))
                pygame.draw.rect(screen, text_color, (icon_x - 1, icon_y - icon_size//2, 2, icon_size))
                
            elif item['icon'] == '📺':  # 分辨率
                # 绘制显示器
                pygame.draw.rect(screen, text_color, (icon_x - icon_size, icon_y - icon_size//2, icon_size*2, icon_size), 2)
                pygame.draw.rect(screen, text_color, (icon_x - 2, icon_y + icon_size//2 + 1, 4, 2))
                
            elif item['icon'] == '🌐':  # 语言
                # 绘制地球
                pygame.draw.circle(screen, text_color, (icon_x, icon_y), icon_size, 2)
                pygame.draw.line(screen, text_color, (icon_x - icon_size, icon_y), (icon_x + icon_size, icon_y))
                pygame.draw.arc(screen, text_color, (icon_x - icon_size//2, icon_y - icon_size, icon_size, icon_size*2), 0, 3.14159, 2)
                pygame.draw.arc(screen, text_color, (icon_x - icon_size//2, icon_y - icon_size, icon_size, icon_size*2), 3.14159, 6.28318, 2)
                
            elif item['icon'] == '🔤':  # 字体
                # 绘制字母A
                points = [
                    (icon_x, icon_y - icon_size),
                    (icon_x - icon_size//2, icon_y + icon_size//2),
                    (icon_x - icon_size//4, icon_y),
                    (icon_x + icon_size//4, icon_y),
                    (icon_x + icon_size//2, icon_y + icon_size//2)
                ]
                pygame.draw.lines(screen, text_color, False, points[:3], 2)
                pygame.draw.lines(screen, text_color, False, points[2:], 2)
                pygame.draw.line(screen, text_color, points[2], points[3], 2)
                
            elif item['icon'] == '🔊':  # 音效
                # 绘制扬声器
                speaker_points = [
                    (icon_x - icon_size//2, icon_y - 3),
                    (icon_x - 2, icon_y - 3),
                    (icon_x + 2, icon_y - 5),
                    (icon_x + 2, icon_y + 5),
                    (icon_x - 2, icon_y + 3),
                    (icon_x - icon_size//2, icon_y + 3)
                ]
                pygame.draw.polygon(screen, text_color, speaker_points)
                # 音波
                pygame.draw.arc(screen, text_color, (icon_x + 1, icon_y - 6, 8, 12), -0.5, 0.5, 2)
                pygame.draw.arc(screen, text_color, (icon_x + 3, icon_y - 8, 10, 16), -0.4, 0.4, 2)
                
            else:
                # 默认圆点
                pygame.draw.circle(screen, text_color, (icon_x, icon_y), 3)
        
        # 绘制设置项名称
        name_x = x + 50
        name_text = font.render(self.i18n.t(item['key']), True, text_color)
        name_rect = name_text.get_rect(centery=y + height // 2)
        name_rect.x = name_x
        screen.blit(name_text, name_rect)
        
        # 绘制当前值
        value_x = x + width - 20
        if item['type'] == 'action':
            value_text = "→"
            value_color = (100, 200, 255)
        elif item['type'] == 'toggle':
            value_text = "开启" if item['current'] else "关闭"
            value_color = (100, 255, 100) if item['current'] else (255, 100, 100)
        else:
            if item['key'] == 'font':
                value_text = self.font_names.get(item['current'], item['current'])
            elif item['key'] in ['resolution', 'language']:
                value_text = self.i18n.t(f"{item['key']}s.{item['current']}")
            else:
                value_text = str(item['current'])
            value_color = text_color
        
        value_surface = font.render(value_text, True, value_color)
        value_rect = value_surface.get_rect(centery=y + height // 2)
        value_rect.right = value_x
        screen.blit(value_surface, value_rect)
    
    def _render_instructions(self, screen, font, screen_width, screen_height):
        """渲染操作说明"""
        if self.in_option_select:
            instructions = ["←→: 选择选项", "回车: 确认", "ESC: 取消"]
        else:
            instructions = ["↑↓: 选择", "回车: 进入", "ESC: 返回", "Ctrl+S: 保存"]
        
        # 背景
        inst_height = len(instructions) * 25 + 20
        inst_y = screen_height - inst_height - 20
        inst_surface = pygame.Surface((screen_width, inst_height), pygame.SRCALPHA)
        inst_surface.fill((0, 0, 0, 100))
        screen.blit(inst_surface, (0, inst_y))
        
        # 文字
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (200, 200, 200))
            text_rect = text.get_rect(center=(screen_width // 2, inst_y + 15 + i * 25))
            screen.blit(text, text_rect)
    
    def _render_dropdown(self, screen, font, item, y, content_x, content_width):
        """渲染现代化下拉选择框"""
        options = item['options']
        option_height = 42  # 增加高度让选项更舒适
        padding = 12
        dropdown_height = len(options) * option_height + padding * 2
        dropdown_width = min(450, content_width - 80)  # 稍微增加宽度
        dropdown_x = content_x + (content_width - dropdown_width) // 2
        
        # 确保不超出屏幕
        screen_height = screen.get_height()
        if y + dropdown_height > screen_height - 50:
            y = screen_height - dropdown_height - 50
        
        # 绘制多层阴影效果
        for i in range(3):
            shadow_alpha = 30 - i * 8
            shadow_offset = 3 + i
            shadow_surface = pygame.Surface((dropdown_width + shadow_offset * 2, dropdown_height + shadow_offset * 2), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, shadow_alpha))
            screen.blit(shadow_surface, (dropdown_x - shadow_offset, y - shadow_offset))
        
        # 绘制主背景（渐变效果）
        dropdown_surface = pygame.Surface((dropdown_width, dropdown_height), pygame.SRCALPHA)
        # 创建渐变背景
        for i in range(dropdown_height):
            alpha = 240 - (i * 20 // dropdown_height)  # 从上到下渐变
            color = (45 + i * 10 // dropdown_height, 45 + i * 10 // dropdown_height, 55 + i * 10 // dropdown_height, alpha)
            pygame.draw.line(dropdown_surface, color[:3], (0, i), (dropdown_width, i))
        screen.blit(dropdown_surface, (dropdown_x, y))
        
        # 绘制边框和高光
        pygame.draw.rect(screen, (140, 140, 140), (dropdown_x, y, dropdown_width, dropdown_height), 2, border_radius=10)
        pygame.draw.rect(screen, (180, 180, 180, 100), (dropdown_x + 1, y + 1, dropdown_width - 2, 2), border_radius=8)  # 顶部高光
        
        # 绘制选项
        for i, option in enumerate(options):
            option_y = y + padding + i * option_height
            is_selected = (i == self.selected_option)
            is_current = (option == item['current'])
            
            # 选项背景
            if is_selected:
                # 选中项：现代化渐变背景
                sel_surface = pygame.Surface((dropdown_width - 16, option_height - 4), pygame.SRCALPHA)
                for j in range(option_height - 4):
                    alpha = 180 - j * 2
                    color = (80 + j, 120 + j, 255 - j * 2, alpha)
                    pygame.draw.line(sel_surface, color[:3], (0, j), (dropdown_width - 16, j))
                screen.blit(sel_surface, (dropdown_x + 8, option_y + 2))
                
                # 选中项边框
                pygame.draw.rect(screen, (120, 160, 255), (dropdown_x + 8, option_y + 2, dropdown_width - 16, option_height - 4), 1, border_radius=6)
                text_color = self.WHITE
                
            elif is_current:
                # 当前值：淡绿色背景
                cur_surface = pygame.Surface((dropdown_width - 16, option_height - 4), pygame.SRCALPHA)
                cur_surface.fill((80, 150, 80, 100))
                screen.blit(cur_surface, (dropdown_x + 8, option_y + 2))
                pygame.draw.rect(screen, (100, 200, 100), (dropdown_x + 8, option_y + 2, dropdown_width - 16, option_height - 4), 1, border_radius=6)
                text_color = (240, 240, 240)
            else:
                text_color = (200, 200, 200)
            
            # 选项文字
            if item['key'] == 'font':
                option_text = self.font_names.get(option, option)
            elif item['key'] in ['resolution', 'language']:
                option_text = self.i18n.t(f"{item['key']}s.{option}")
            else:
                option_text = option
            
            # 限制文字长度，避免溢出
            max_text_width = dropdown_width - 60
            text_surface = font.render(option_text, True, text_color)
            if text_surface.get_width() > max_text_width:
                # 截断文字并添加省略号
                truncated_text = option_text
                while font.render(truncated_text + "...", True, text_color).get_width() > max_text_width and len(truncated_text) > 1:
                    truncated_text = truncated_text[:-1]
                text_surface = font.render(truncated_text + "...", True, text_color)
            
            text_rect = text_surface.get_rect()
            text_rect.x = dropdown_x + 20
            text_rect.centery = option_y + option_height // 2
            screen.blit(text_surface, text_rect)
            
            # 状态指示器
            indicator_x = dropdown_x + dropdown_width - 25
            indicator_y = option_y + option_height // 2
            
            if is_current:
                # 当前值：实心圆
                pygame.draw.circle(screen, (100, 255, 100), (indicator_x, indicator_y), 6)
                pygame.draw.circle(screen, (80, 200, 80), (indicator_x, indicator_y), 6, 2)
                # 添加勾选标记
                pygame.draw.line(screen, (255, 255, 255), (indicator_x - 3, indicator_y), (indicator_x - 1, indicator_y + 2), 2)
                pygame.draw.line(screen, (255, 255, 255), (indicator_x - 1, indicator_y + 2), (indicator_x + 3, indicator_y - 2), 2)
            elif is_selected:
                # 选中项：空心圆
                pygame.draw.circle(screen, (150, 200, 255), (indicator_x, indicator_y), 6, 2)
            
            # 分隔线（除了最后一项）
            if i < len(options) - 1:
                line_y = option_y + option_height - 1
                pygame.draw.line(screen, (80, 80, 80, 150), 
                               (dropdown_x + 15, line_y), (dropdown_x + dropdown_width - 15, line_y))
        
        # 绘制滚动提示（如果选项很多）
        if len(options) > 8:
            # 顶部渐变遮罩
            top_mask = pygame.Surface((dropdown_width, 15), pygame.SRCALPHA)
            for i in range(15):
                alpha = i * 17
                pygame.draw.line(top_mask, (50, 50, 60, alpha), (0, i), (dropdown_width, i))
            screen.blit(top_mask, (dropdown_x, y))
            
            # 底部渐变遮罩
            bottom_mask = pygame.Surface((dropdown_width, 15), pygame.SRCALPHA)
            for i in range(15):
                alpha = (14 - i) * 17
                pygame.draw.line(bottom_mask, (50, 50, 60, alpha), (0, i), (dropdown_width, i))
            screen.blit(bottom_mask, (dropdown_x, y + dropdown_height - 15))
    


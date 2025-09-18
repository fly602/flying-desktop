#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置页面模块
"""

import pygame
from pathlib import Path
from .font_detector import FontDetector
from .file_browser import FileBrowser


class SettingsPage:
    """设置页面"""
    
    def __init__(self, config, i18n, audio_manager, app_config_loader=None):
        self.config = config
        self.i18n = i18n
        self.audio = audio_manager
        self.app_config_loader = app_config_loader
        
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
        
        # 设置项列表
        self.settings_items = [
            {
                'key': 'add_app',
                'type': 'action',
                'current': None
            },
            {
                'key': 'resolution',
                'type': 'select',
                'options': ['auto', '1920x1080', '1366x768', '1280x720', '1024x768', '800x600'],
                'current': self.get_current_resolution()
            },
            {
                'key': 'language',
                'type': 'select', 
                'options': ['zh_CN', 'en_US', 'ja_JP'],
                'current': config.get('ui.language', 'zh_CN')
            },
            {
                'key': 'font',
                'type': 'select',
                'options': font_options,  # 使用动态检测的字体列表
                'current': self.get_current_font()
            },
            {
                'key': 'sound_effects',
                'type': 'toggle',
                'current': config.get('audio.sound_effects', True)
            }
        ]
        
        self.selected_item = 0
        self.in_option_select = False
        self.selected_option = 0
        
        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (100, 150, 255)
        self.LIGHT_BLUE = (150, 200, 255)
        self.GRAY = (128, 128, 128)
        self.GREEN = (100, 255, 100)
        self.RED = (255, 100, 100)
    
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
        
        return None
    
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
        """渲染设置页面"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # 绘制半透明背景
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(200)
        overlay.fill(self.BLACK)
        screen.blit(overlay, (0, 0))
        
        # 绘制设置标题
        title_text = font_large.render(self.i18n.t('settings'), True, self.WHITE)
        title_rect = title_text.get_rect(center=(screen_width // 2, 100))
        screen.blit(title_text, title_rect)
        
        # 绘制设置项
        start_y = 200
        item_height = 80
        dropdown_item = None  # 记录需要绘制下拉框的项目
        dropdown_y = 0
        
        for i, item in enumerate(self.settings_items):
            y = start_y + i * item_height
            is_selected = (i == self.selected_item)
            
            # 绘制设置项背景
            if is_selected:
                bg_color = self.BLUE
                text_color = self.WHITE
            else:
                bg_color = self.GRAY
                text_color = self.WHITE
            
            item_rect = pygame.Rect(100, y - 20, screen_width - 200, 60)
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=10)
            
            # 绘制设置项名称
            name_text = font_medium.render(self.i18n.t(item['key']), True, text_color)
            screen.blit(name_text, (120, y - 10))
            
            # 绘制当前值
            if item['type'] == 'action':
                # 动作类型显示箭头
                value_text = ">"
                color = self.LIGHT_BLUE
            elif item['type'] == 'toggle':
                value_text = self.i18n.t('enabled' if item['current'] else 'disabled')
                color = self.GREEN if item['current'] else self.RED
            else:
                if item['key'] == 'font':
                    # 对于字体选项，使用检测到的字体名称
                    value_text = self.font_names.get(item['current'], item['current'])
                elif item['key'] in ['resolution', 'language']:
                    value_text = self.i18n.t(f"{item['key']}s.{item['current']}")
                else:
                    value_text = str(item['current'])
                color = self.WHITE
            
            value_surface = font_medium.render(value_text, True, color)
            value_rect = value_surface.get_rect()
            value_rect.right = screen_width - 120
            value_rect.centery = y
            screen.blit(value_surface, value_rect)
            
            # 记录需要绘制下拉框的项目（最后绘制以确保在最上层）
            if is_selected and self.in_option_select and item['type'] != 'toggle':
                dropdown_item = item
                dropdown_y = y + 40
        
        # 绘制操作说明
        instructions = []
        if self.in_option_select:
            instructions = [
                f"←→: 选择选项",
                f"回车: 确认选择",
                f"ESC: 取消"
            ]
        else:
            instructions = [
                f"↑↓: {self.i18n.t('instructions.select')}",
                f"回车: 进入选项",
                f"ESC: {self.i18n.t('instructions.back')}",
                f"Ctrl+S: {self.i18n.t('save')}"
            ]
        
        y_start = screen_height - 120
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, self.WHITE)
            text_rect = text.get_rect(center=(screen_width // 2, y_start + i * 25))
            screen.blit(text, text_rect)
        
        # 最后绘制下拉框（确保在最上层）
        if dropdown_item:
            self.render_option_list(screen, font_small, dropdown_item, dropdown_y)
        
        # 如果在文件浏览器模式，绘制文件浏览器
        if self.in_file_browser and self.file_browser:
            self.file_browser.render(screen, font_large, font_medium, font_small)
    
    def render_option_list(self, screen, font, item, y):
        """渲染选项列表"""
        screen_width = screen.get_width()
        
        # 计算下拉框尺寸
        option_height = 35
        padding = 5
        list_height = len(item['options']) * option_height + padding * 2
        list_width = min(400, screen_width - 200)
        list_x = (screen_width - list_width) // 2
        
        # 确保下拉框不超出屏幕
        screen_height = screen.get_height()
        if y + list_height > screen_height - 50:
            y = screen_height - list_height - 50
        
        # 绘制下拉框阴影（使用半透明surface）
        shadow_surface = pygame.Surface((list_width, list_height))
        shadow_surface.set_alpha(100)
        shadow_surface.fill((0, 0, 0))
        screen.blit(shadow_surface, (list_x + 3, y + 3))
        
        # 绘制下拉框背景
        list_rect = pygame.Rect(list_x, y, list_width, list_height)
        pygame.draw.rect(screen, (40, 40, 40), list_rect, border_radius=8)
        pygame.draw.rect(screen, self.WHITE, list_rect, 3, border_radius=8)
        
        # 绘制选项
        for i, option in enumerate(item['options']):
            option_y = y + padding + i * option_height
            is_selected = (i == self.selected_option)
            
            # 绘制选项背景
            option_rect = pygame.Rect(list_x + 5, option_y, list_width - 10, option_height - 2)
            if is_selected:
                pygame.draw.rect(screen, self.LIGHT_BLUE, option_rect, border_radius=5)
                text_color = self.BLACK
            else:
                text_color = self.WHITE
            
            # 绘制选项文本
            if item['key'] == 'font':
                # 对于字体选项，使用检测到的字体名称
                option_text = self.font_names.get(option, option)
            elif item['key'] in ['resolution', 'language']:
                option_text = self.i18n.t(f"{item['key']}s.{option}")
            else:
                option_text = option
            
            text_surface = font.render(option_text, True, text_color)
            text_rect = text_surface.get_rect()
            text_rect.centery = option_y + option_height // 2
            text_rect.x = list_x + 15
            screen.blit(text_surface, text_rect)
            
            # 如果是当前选中的选项，绘制一个小图标
            if option == item['current']:
                check_color = self.GREEN if not is_selected else self.BLACK
                check_x = list_x + list_width - 25
                check_y = option_y + option_height // 2
                # 绘制一个简单的勾选标记
                pygame.draw.circle(screen, check_color, (check_x, check_y), 3)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flying Desktop 主类
整合各个模块，提供主要的桌面功能
"""

import pygame
import sys

from .config import ConfigManager
from .input_handler import InputHandler
from .renderer import Renderer
from .app_launcher import AppLauncher
from .app_config import AppConfigLoader
from .i18n import I18n
from .audio import AudioManager
from .settings import SettingsPage


class FlyingDesktop:
    """Flying Desktop 主类"""
    
    def __init__(self):
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化国际化
        language = self.config_manager.get('ui.language', 'zh_CN')
        self.i18n = I18n(language)
        
        # 初始化音频系统
        self.audio = AudioManager(self.config_manager)
        
        # 加载应用配置
        self.app_config = AppConfigLoader()
        self.apps = self.app_config.get_apps()
        
        if not self.apps:
            print("警告: 没有找到可用的应用")
        
        # 初始化各个模块（注意顺序：先渲染器再输入处理器）
        self.renderer = Renderer(self.config_manager)
        self.input_handler = InputHandler(self.config_manager)
        self.app_launcher = AppLauncher()
        
        # 初始化设置页面
        self.settings = SettingsPage(self.config_manager, self.i18n, self.audio, self.app_config)
        
        # 界面状态
        # 如果没有应用，直接显示设置页面
        if len(self.apps) == 0:
            self.current_view = 'settings'
            print("没有应用，自动打开设置页面")
        else:
            self.current_view = 'desktop'
        
        self.selected_app = 0
        
        # 按键状态跟踪
        self.keys_pressed = set()
        self.last_action_time = 0
    
    def run(self):
        """主运行循环"""
        clock = pygame.time.Clock()
        running = True
        
        print("Flying Desktop 已启动")
        print(f"检测到 {self.input_handler.get_joystick_count()} 个游戏手柄")
        print(f"加载了 {len(self.apps)} 个应用")
        print(f"当前语言: {self.i18n.language}")
        
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.current_view == 'settings':
                    # 设置页面事件处理
                    result = self.settings.handle_input(event)
                    if result == 'back':
                        # 如果没有应用，不允许返回桌面
                        if len(self.apps) > 0:
                            self.current_view = 'desktop'
                            self.audio.play('back')
                        else:
                            self.audio.play('error')
                    elif result == 'saved':
                        self.reload_after_settings()
                        self.audio.play('confirm')
                    elif result == 'app_added':
                        # 应用添加成功，刷新应用列表
                        self.app_config.refresh_apps()
                        self.apps = self.app_config.get_apps()
                        print(f"应用列表已刷新，当前有 {len(self.apps)} 个应用")
                        
                        # 如果这是第一个应用，可以返回桌面
                        if len(self.apps) == 1:
                            self.current_view = 'desktop'
                            print("添加了第一个应用，切换到桌面视图")
                else:
                    # 桌面事件处理 - 只处理按键按下事件
                    if event.type == pygame.KEYDOWN:
                        current_time = pygame.time.get_ticks()
                        
                        # 防抖动：300ms内不重复处理相同动作
                        if current_time - self.last_action_time < 300:
                            continue
                        
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_LEFT and len(self.apps) > 0:
                            self.selected_app = (self.selected_app - 1) % len(self.apps)
                            self.audio.play('select')
                            self.last_action_time = current_time
                        elif event.key == pygame.K_RIGHT and len(self.apps) > 0:
                            self.selected_app = (self.selected_app + 1) % len(self.apps)
                            self.audio.play('select')
                            self.last_action_time = current_time
                        elif event.key == pygame.K_RETURN and self.apps:
                            self.app_launcher.launch_app(self.apps[self.selected_app])
                            self.audio.play('confirm')
                            self.last_action_time = current_time
                        elif event.key == pygame.K_TAB:
                            self.current_view = 'settings'
                            self.audio.play('confirm')
                            self.last_action_time = current_time
            
            # 渲染界面
            if self.current_view == 'settings':
                # 先渲染桌面作为背景（不刷新显示）
                if self.apps:
                    self.renderer.render_background_only(self.apps, self.selected_app)
                else:
                    self._render_no_apps_background()
                
                # 然后渲染设置页面
                self.settings.render(
                    self.renderer.screen,
                    self.renderer.large_font,
                    self.renderer.medium_font,
                    self.renderer.small_font
                )
                # 只在这里刷新一次
                pygame.display.flip()
            else:
                # 渲染桌面
                if self.apps:
                    self.renderer.render_frame(self.apps, self.selected_app, "", show_title=False)
                else:
                    self._render_no_apps()
            
            clock.tick(60)
        
        # 清理资源
        self.renderer.cleanup()
        self.audio.cleanup()
        sys.exit()
    
    def reload_after_settings(self):
        """设置更改后重新加载组件"""
        # 重新加载语言
        language = self.config_manager.get('ui.language', 'zh_CN')
        self.i18n.set_language(language)
        
        # 重新加载音频设置
        self.audio.set_enabled(self.config_manager.get('audio.sound_effects', True))
    
    def _render_no_apps(self):
        """渲染无应用提示"""
        self._render_no_apps_content()
        pygame.display.flip()
    
    def _render_no_apps_background(self):
        """渲染无应用背景（不刷新显示）"""
        self._render_no_apps_content()
    
    def _render_no_apps_content(self):
        """渲染无应用内容（不包含显示刷新）"""
        self.renderer.screen.fill(self.renderer.BLACK)
        
        # 显示提示信息
        text = self.renderer.large_font.render("没有找到可用的应用", True, self.renderer.WHITE)
        text_rect = text.get_rect(center=(
            self.renderer.screen_width // 2, 
            self.renderer.screen_height // 2 - 60
        ))
        self.renderer.screen.blit(text, text_rect)
        
        # 显示设置提示
        hint_text = self.renderer.medium_font.render(
            "已自动打开设置页面", 
            True, 
            self.renderer.GRAY
        )
        hint_rect = hint_text.get_rect(center=(
            self.renderer.screen_width // 2, 
            self.renderer.screen_height // 2
        ))
        self.renderer.screen.blit(hint_text, hint_rect)
        
        # 显示添加应用提示
        add_hint = self.renderer.small_font.render(
            "请在设置中选择 '添加应用' 来添加 .desktop 或 .AppImage 文件", 
            True, 
            self.renderer.WHITE
        )
        add_rect = add_hint.get_rect(center=(
            self.renderer.screen_width // 2, 
            self.renderer.screen_height // 2 + 40
        ))
        self.renderer.screen.blit(add_hint, add_rect)
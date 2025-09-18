#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入处理模块
负责处理键盘和手柄输入
"""

import pygame


class InputHandler:
    """输入处理器"""
    
    def __init__(self, config):
        self.config = config
        self.joysticks = []
        self.last_input_time = 0
        self.input_delay = config.get("controls.input_delay", 300)
        self.last_key_pressed = None
        self.key_press_time = 0
        self.joystick_deadzone = config.get("controls.joystick_deadzone", 0.5)
        
        self.init_joysticks()
        
        # 禁用键盘重复（在pygame初始化后）
        try:
            pygame.key.set_repeat()
        except:
            pass
    
    def init_joysticks(self):
        """初始化游戏手柄"""
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)
            print(f"检测到游戏手柄: {joystick.get_name()}")
    
    def handle_events(self, selected_app, app_count):
        """
        处理输入事件（旧版本，保持兼容性）
        返回: (continue_running, new_selected_app, launch_app)
        """
        current_time = pygame.time.get_ticks()
        launch_app = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, selected_app, False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False, selected_app, False
                elif event.key == pygame.K_LEFT and current_time - self.last_input_time > self.input_delay:
                    selected_app = (selected_app - 1) % app_count
                    self.last_input_time = current_time
                elif event.key == pygame.K_RIGHT and current_time - self.last_input_time > self.input_delay:
                    selected_app = (selected_app + 1) % app_count
                    self.last_input_time = current_time
                elif event.key == pygame.K_RETURN:
                    launch_app = True
                elif event.key == pygame.K_TAB:
                    # 设置键，返回特殊值
                    return True, selected_app, "settings"
            
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A键
                    launch_app = True
                elif event.button == 1:  # B键 (退出)
                    return False, selected_app, False
                elif event.button == 3:  # Y键 (设置)
                    return True, selected_app, "settings"
            
            elif event.type == pygame.JOYAXISMOTION:
                if event.axis == 0 and current_time - self.last_input_time > self.input_delay:  # 左摇杆X轴
                    if event.value < -self.joystick_deadzone:  # 左
                        selected_app = (selected_app - 1) % app_count
                        self.last_input_time = current_time
                    elif event.value > self.joystick_deadzone:  # 右
                        selected_app = (selected_app + 1) % app_count
                        self.last_input_time = current_time
            
            elif event.type == pygame.JOYHATMOTION:
                if current_time - self.last_input_time > self.input_delay:
                    hat_x, hat_y = event.value
                    if hat_x == -1:  # 方向键左
                        selected_app = (selected_app - 1) % app_count
                        self.last_input_time = current_time
                    elif hat_x == 1:  # 方向键右
                        selected_app = (selected_app + 1) % app_count
                        self.last_input_time = current_time
        
        return True, selected_app, launch_app
    
    def handle_single_event(self, event, selected_app, app_count):
        """
        处理单个事件
        返回: (action, new_selected_app)
        action 可能的值: None, 'quit', 'left', 'right', 'confirm', 'settings'
        """
        current_time = pygame.time.get_ticks()
        
        if event.type == pygame.KEYDOWN:
            # 防止按键重复触发
            if (self.last_key_pressed == event.key and 
                current_time - self.key_press_time < self.input_delay):
                return None, selected_app
            
            self.last_key_pressed = event.key
            self.key_press_time = current_time
            

            
            if event.key == pygame.K_ESCAPE:
                return 'quit', selected_app
            elif event.key == pygame.K_LEFT:
                new_selected = (selected_app - 1) % app_count if app_count > 0 else 0
                self.last_input_time = current_time
                return 'left', new_selected
            elif event.key == pygame.K_RIGHT:
                new_selected = (selected_app + 1) % app_count if app_count > 0 else 0
                self.last_input_time = current_time
                return 'right', new_selected
            elif event.key == pygame.K_RETURN:
                return 'confirm', selected_app
            elif event.key == pygame.K_TAB:
                return 'settings', selected_app
        
        elif event.type == pygame.JOYBUTTONDOWN:

            
            if event.button == 0:  # A键
                return 'confirm', selected_app
            elif event.button == 1:  # B键 (退出)
                return 'quit', selected_app
            elif event.button == 3:  # Y键 (设置)
                return 'settings', selected_app
        
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 0 and current_time - self.last_input_time > self.input_delay:  # 左摇杆X轴
                if event.value < -self.joystick_deadzone:  # 左
                    new_selected = (selected_app - 1) % app_count if app_count > 0 else 0
                    self.last_input_time = current_time
                    return 'left', new_selected
                elif event.value > self.joystick_deadzone:  # 右
                    new_selected = (selected_app + 1) % app_count if app_count > 0 else 0
                    self.last_input_time = current_time
                    return 'right', new_selected
        
        elif event.type == pygame.JOYHATMOTION:
            if current_time - self.last_input_time > self.input_delay:
                hat_x, hat_y = event.value
                if hat_x == -1:  # 方向键左
                    new_selected = (selected_app - 1) % app_count if app_count > 0 else 0
                    self.last_input_time = current_time
                    return 'left', new_selected
                elif hat_x == 1:  # 方向键右
                    new_selected = (selected_app + 1) % app_count if app_count > 0 else 0
                    self.last_input_time = current_time
                    return 'right', new_selected
        
        return None, selected_app
    
    def get_joystick_count(self):
        """获取手柄数量"""
        return len(self.joysticks)
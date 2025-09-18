#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flying Desktop - 轻量级桌面环境
支持游戏手柄控制的应用启动器
"""

import pygame
import sys
import subprocess
import json
from pathlib import Path

class SimpleDesktop:
    def __init__(self):
        # 加载配置
        self.load_config()
        
        # 初始化pygame
        pygame.init()
        pygame.joystick.init()
        
        # 隐藏鼠标光标
        if self.config["desktop"]["hide_mouse"]:
            pygame.mouse.set_visible(False)
        
        # 获取屏幕分辨率
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        # 设置显示模式
        if self.config["desktop"]["fullscreen"]:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        pygame.display.set_caption(self.config["desktop"]["title"])
        
        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (100, 150, 255)
        self.LIGHT_BLUE = (150, 200, 255)
        self.GRAY = (128, 128, 128)
        
        # 从配置文件加载应用
        self.apps = [app for app in self.config["apps"] if app.get("enabled", True)]
        
        # 当前选中的应用
        self.selected_app = 0
        
        # 字体设置
        self.large_font = pygame.font.Font(None, 96)
        self.medium_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        
        # 应用图标大小和位置
        self.icon_size = self.config["desktop"]["icon_size"]
        self.icon_spacing = self.config["desktop"]["icon_spacing"]
        self.calculate_positions()
        
        # 游戏手柄
        self.joysticks = []
        self.init_joysticks()
        
        # 按键状态
        self.last_input_time = 0
        self.input_delay = self.config["controls"]["input_delay"]
        
        # 加载背景
        self.load_background()

    def load_config(self):
        """加载配置文件 - 支持系统默认配置和用户自定义配置"""
        
        # 默认配置
        default_config = {
            "desktop": {
                "title": "Flying Desktop",
                "fullscreen": True,
                "hide_mouse": True,
                "background_image": "background.jpg",
                "icon_size": 200,
                "icon_spacing": 100
            },
            "apps": [
                {
                    "name": "应用1",
                    "description": "示例应用1",
                    "command": "echo 'Hello App 1'",
                    "icon_text": "1",
                    "enabled": True
                },
                {
                    "name": "应用2",
                    "description": "示例应用2",
                    "command": "echo 'Hello App 2'",
                    "icon_text": "2",
                    "enabled": True
                }
            ],
            "controls": {
                "input_delay": 300,
                "joystick_deadzone": 0.5
            }
        }
        
        # 配置文件搜索路径（按优先级排序）
        config_paths = [
            # 1. 用户自定义配置（最高优先级）
            Path.home() / ".config" / "flying-desktop" / "config.json",
            # 2. 当前目录配置
            Path("config.json"),
            # 3. 系统安装配置
            Path("/opt/simple_desktop/config.json"),
            Path("/usr/share/flying-desktop/config.json"),
        ]
        
        self.config = default_config.copy()
        loaded_configs = []
        
        # 按优先级加载配置文件
        for config_path in reversed(config_paths):  # 从低优先级到高优先级
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        file_config = json.load(f)
                    
                    # 深度合并配置
                    self._merge_config(self.config, file_config)
                    loaded_configs.append(str(config_path))
                    print(f"加载配置: {config_path}")
                    
                except Exception as e:
                    print(f"配置文件加载失败 {config_path}: {e}")
        
        if loaded_configs:
            print(f"配置加载完成，共加载 {len(loaded_configs)} 个配置文件")
        else:
            print("未找到配置文件，使用默认配置")
            
        # 确保用户配置目录存在
        user_config_dir = Path.home() / ".config" / "flying-desktop"
        user_config_file = user_config_dir / "config.json"
        
        if not user_config_file.exists():
            try:
                user_config_dir.mkdir(parents=True, exist_ok=True)
                with open(user_config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
                print(f"创建用户配置文件: {user_config_file}")
            except Exception as e:
                print(f"创建用户配置文件失败: {e}")
    
    def _merge_config(self, base_config, new_config):
        """深度合并配置字典"""
        for key, value in new_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
        
    def init_joysticks(self):
        """初始化游戏手柄"""
        joystick_count = pygame.joystick.get_count()
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)
            print(f"检测到游戏手柄: {joystick.get_name()}")
    
    def calculate_positions(self):
        """计算应用图标位置"""
        total_width = len(self.apps) * self.icon_size + (len(self.apps) - 1) * self.icon_spacing
        start_x = (self.screen_width - total_width) // 2
        center_y = self.screen_height // 2
        
        self.app_positions = []
        for i in range(len(self.apps)):
            x = start_x + i * (self.icon_size + self.icon_spacing)
            y = center_y - self.icon_size // 2
            self.app_positions.append((x, y))
    
    def load_background(self):
        """加载背景图片，如果没有则创建渐变背景"""
        self.background = pygame.Surface((self.screen_width, self.screen_height))
        
        # 尝试加载背景图片
        bg_path = Path(self.config["desktop"].get("background_image", "background.jpg"))
        if bg_path.exists():
            try:
                bg_image = pygame.image.load(str(bg_path))
                self.background = pygame.transform.scale(bg_image, (self.screen_width, self.screen_height))
                print(f"背景图片加载成功: {bg_path}")
                return
            except Exception as e:
                print(f"背景图片加载失败: {e}")
        
        # 创建渐变背景
        for y in range(self.screen_height):
            color_value = int(20 + (y / self.screen_height) * 60)
            color = (color_value, color_value, color_value + 20)
            pygame.draw.line(self.background, color, (0, y), (self.screen_width, y))

    def draw_app_icon(self, app, position, is_selected):
        """绘制应用图标"""
        x, y = position
        
        # 图标背景
        color = self.LIGHT_BLUE if is_selected else self.BLUE
        border_color = self.WHITE if is_selected else self.GRAY
        border_width = 4 if is_selected else 2
        
        # 绘制圆角矩形
        icon_rect = pygame.Rect(x, y, self.icon_size, self.icon_size)
        pygame.draw.rect(self.screen, color, icon_rect, border_radius=20)
        pygame.draw.rect(self.screen, border_color, icon_rect, border_width, border_radius=20)
        
        # 绘制图标文字
        icon_text = self.large_font.render(app["icon_text"], True, self.WHITE)
        text_rect = icon_text.get_rect(center=(x + self.icon_size // 2, y + self.icon_size // 2))
        self.screen.blit(icon_text, text_rect)
        
        # 绘制应用名称
        name_text = self.medium_font.render(app["name"], True, self.WHITE)
        name_rect = name_text.get_rect(center=(x + self.icon_size // 2, y + self.icon_size + 30))
        self.screen.blit(name_text, name_rect)
        
        # 如果选中，显示描述
        if is_selected:
            desc_text = self.small_font.render(app["description"], True, self.WHITE)
            desc_rect = desc_text.get_rect(center=(x + self.icon_size // 2, y + self.icon_size + 65))
            self.screen.blit(desc_text, desc_rect)
    
    def draw_instructions(self):
        """绘制操作说明"""
        instructions = [
            "使用方向键或手柄左摇杆选择应用",
            "按确认键(A键/回车)启动应用",
            "按ESC键退出桌面"
        ]
        
        y_start = self.screen_height - 120
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.WHITE)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_start + i * 30))
            self.screen.blit(text, text_rect)
    
    def handle_input(self):
        """处理输入事件"""
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_LEFT and current_time - self.last_input_time > self.input_delay:
                    self.selected_app = (self.selected_app - 1) % len(self.apps)
                    self.last_input_time = current_time
                elif event.key == pygame.K_RIGHT and current_time - self.last_input_time > self.input_delay:
                    self.selected_app = (self.selected_app + 1) % len(self.apps)
                    self.last_input_time = current_time
                elif event.key == pygame.K_RETURN:
                    self.launch_app(self.selected_app)
            
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A键
                    self.launch_app(self.selected_app)
                elif event.button == 1:  # B键 (退出)
                    return False
            
            elif event.type == pygame.JOYAXISMOTION:
                deadzone = self.config["controls"]["joystick_deadzone"]
                if event.axis == 0 and current_time - self.last_input_time > self.input_delay:  # 左摇杆X轴
                    if event.value < -deadzone:  # 左
                        self.selected_app = (self.selected_app - 1) % len(self.apps)
                        self.last_input_time = current_time
                    elif event.value > deadzone:  # 右
                        self.selected_app = (self.selected_app + 1) % len(self.apps)
                        self.last_input_time = current_time
            
            elif event.type == pygame.JOYHATMOTION:
                if current_time - self.last_input_time > self.input_delay:
                    hat_x, hat_y = event.value
                    if hat_x == -1:  # 方向键左
                        self.selected_app = (self.selected_app - 1) % len(self.apps)
                        self.last_input_time = current_time
                    elif hat_x == 1:  # 方向键右
                        self.selected_app = (self.selected_app + 1) % len(self.apps)
                        self.last_input_time = current_time
        
        return True
    
    def launch_app(self, app_index):
        """启动应用"""
        app = self.apps[app_index]
        try:
            print(f"启动应用: {app['name']}")
            cmd = app["command"]
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"启动 {app['name']} 失败: {e}")
    
    def run(self):
        """主运行循环"""
        clock = pygame.time.Clock()
        running = True
        
        print("简单桌面已启动")
        print(f"检测到 {len(self.joysticks)} 个游戏手柄")
        
        while running:
            running = self.handle_input()
            
            # 绘制背景
            self.screen.blit(self.background, (0, 0))
            
            # 绘制标题
            title_text = self.large_font.render(self.config["desktop"]["title"], True, self.WHITE)
            title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
            self.screen.blit(title_text, title_rect)
            
            # 绘制应用图标
            for i, app in enumerate(self.apps):
                is_selected = (i == self.selected_app)
                self.draw_app_icon(app, self.app_positions[i], is_selected)
            
            # 绘制操作说明
            self.draw_instructions()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    """主函数"""
    try:
        desktop = SimpleDesktop()
        desktop.run()
    except Exception as e:
        print(f"桌面启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

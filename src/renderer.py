#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
渲染模块
负责界面绘制和显示
"""

import pygame
from pathlib import Path
from .json_style_manager import get_style_manager


class Renderer:
    """渲染器"""
    
    def __init__(self, config):
        self.config = config
        
        # 初始化pygame显示（必须在获取显示信息之前）
        pygame.init()
        
        # 初始化样式管理器
        self.style_manager = get_style_manager()
        self.style_manager.set_screen_size(
            pygame.display.Info().current_w, 
            pygame.display.Info().current_h
        )
        
        # 隐藏鼠标光标
        if config.get("desktop.hide_mouse", True):
            pygame.mouse.set_visible(False)
        
        # 获取屏幕分辨率
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        # 设置显示模式
        if config.get("desktop.fullscreen", True):
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height), 
                pygame.FULLSCREEN
            )
        else:
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height)
            )
        
        pygame.display.set_caption(config.get("desktop.title", "Flying Desktop"))
        
        # 从样式管理器获取颜色定义
        self.BLACK = (0, 0, 0)  # 保留基本黑色
        self.WHITE = self.style_manager.get_color("text_color")
        self.BLUE = self.style_manager.get_color("primary_color")
        self.LIGHT_BLUE = self.style_manager.get_color("highlight_color")
        self.GRAY = self.style_manager.get_color("secondary_color")
        
        # 字体设置 - 使用样式管理器获取字体大小
        desktop_style = self.style_manager.get_desktop_style()
        app_icon_style = desktop_style.get("app_icon", {})
        
        # 获取字体大小配置
        title_font_size = desktop_style.get("title", {}).get("font_size", 96)
        icon_font_size = app_icon_style.get("icon", {}).get("font_size", 96)
        name_font_size = app_icon_style.get("name", {}).get("font_size", 48)
        desc_font_size = app_icon_style.get("description", {}).get("font_size", 32)
        
        self.large_font = self._load_font(title_font_size)
        self.medium_font = self._load_font(name_font_size)
        self.small_font = self._load_font(desc_font_size)
        
        # 图标设置 - 使用样式管理器获取尺寸
        self.icon_size = app_icon_style.get("size", 200)
        self.icon_spacing = app_icon_style.get("spacing", 100)
        
        # 加载背景
        self.load_background()
    
    def _load_font(self, size):
        """加载支持中文的字体"""
        # 尝试加载系统中文字体的优先级列表
        chinese_fonts = [
            # Linux 常见中文字体文件路径
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/source-han-cjk/SourceHanSansSC-Regular.otf",
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/usr/share/fonts/truetype/arphic/ukai.ttc",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
        
        # 系统字体名称
        system_fonts = [
            "WenQuanYi Zen Hei", 
            "WenQuanYi Micro Hei",
            "Noto Sans CJK SC", 
            "Source Han Sans SC",
            "SimHei", 
            "Microsoft YaHei"
        ]
        
        # 首先尝试从配置中获取字体路径
        font_path = self.config.get("desktop.font_path")
        if font_path and Path(font_path).exists():
            try:
                font = pygame.font.Font(font_path, size)
                print(f"成功加载配置字体: {font_path}")
                return font
            except Exception as e:
                print(f"无法加载配置的字体 {font_path}: {e}")
        
        # 尝试加载中文字体文件
        for font_path in chinese_fonts:
            try:
                if Path(font_path).exists():
                    font = pygame.font.Font(font_path, size)
                    print(f"成功加载中文字体文件: {font_path}")
                    return font
            except Exception as e:
                print(f"字体文件加载失败 {font_path}: {e}")
                continue
        
        # 尝试加载系统字体名称
        for font_name in system_fonts:
            try:
                font = pygame.font.SysFont(font_name, size)
                print(f"成功加载系统字体: {font_name}")
                return font
            except Exception as e:
                print(f"系统字体加载失败 {font_name}: {e}")
                continue
        
        # 尝试获取系统默认字体
        try:
            font = pygame.font.SysFont("sans-serif", size)
            print("使用系统默认sans-serif字体")
            return font
        except Exception as e:
            print(f"sans-serif字体加载失败: {e}")
        
        # 最后的备选方案
        try:
            font = pygame.font.Font(None, size)
            print("警告: 使用pygame默认字体，可能不支持中文显示")
            return font
        except Exception as e:
            print(f"默认字体加载失败: {e}")
            raise Exception("无法加载任何字体")
    
    def load_background(self):
        """初始化背景系统，支持轮播和渐变过渡"""
        # 背景轮播相关属性
        self.background_images = []
        self.current_bg_index = 0
        self.next_bg_index = 0
        self.background_transition_time = 0
        self.background_duration = self.config.get("desktop.background_duration", 10000)  # 10秒
        self.transition_duration = self.config.get("desktop.transition_duration", 2000)   # 2秒过渡
        self.last_bg_change = pygame.time.get_ticks()
        
        # 当前背景和下一个背景的Surface
        self.current_background = pygame.Surface((self.screen_width, self.screen_height))
        self.next_background = pygame.Surface((self.screen_width, self.screen_height))
        
        # 加载所有可用的背景图片
        self._load_background_images()
        
        # 设置初始背景
        if self.background_images:
            self._set_background(0)
        else:
            self._create_gradient_background(self.current_background)
    
    def _load_background_images(self):
        """加载所有可用的背景图片"""
        bg_images = self.config.get("desktop.background_images", [])
        
        # 添加默认背景到列表
        default_bg = self.config.get("desktop.background_image", "assets/backgrounds/default.png")
        if default_bg not in bg_images:
            bg_images.insert(0, default_bg)
        
        # 过滤存在的背景图片并加载
        for img_path in bg_images:
            path = Path(img_path)
            if path.exists():
                try:
                    bg_image = pygame.image.load(str(path))
                    scaled_image = pygame.transform.scale(bg_image, (self.screen_width, self.screen_height))
                    self.background_images.append(scaled_image)
                    print(f"背景图片加载成功: {path}")
                except Exception as e:
                    print(f"背景图片加载失败 {path}: {e}")
        
        if not self.background_images:
            print("未找到可用的背景图片，将使用渐变背景")
    
    def _set_background(self, index):
        """设置指定索引的背景"""
        if 0 <= index < len(self.background_images):
            self.current_background.blit(self.background_images[index], (0, 0))
        else:
            self._create_gradient_background(self.current_background)
    
    def _create_gradient_background(self, surface):
        """创建渐变背景"""
        for y in range(self.screen_height):
            color_value = int(20 + (y / self.screen_height) * 60)
            color = (color_value, color_value, color_value + 20)
            pygame.draw.line(surface, color, (0, y), (self.screen_width, y))
    
    def _ease_in_out_cubic(self, t):
        """缓入缓出三次方函数"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            p = 2 * t - 2
            return 1 + p * p * p / 4
    
    def update_background(self):
        """更新背景轮播和过渡效果"""
        if not self.background_images or len(self.background_images) <= 1:
            return self.current_background
        
        current_time = pygame.time.get_ticks()
        time_since_change = current_time - self.last_bg_change
        
        # 检查是否需要开始过渡到下一个背景
        if time_since_change >= self.background_duration and self.background_transition_time == 0:
            # 开始过渡
            self.next_bg_index = (self.current_bg_index + 1) % len(self.background_images)
            self._set_background_to_surface(self.next_background, self.next_bg_index)
            self.background_transition_time = current_time
            print(f"开始背景过渡: {self.current_bg_index} -> {self.next_bg_index}")
        
        # 处理过渡动画
        if self.background_transition_time > 0:
            transition_elapsed = current_time - self.background_transition_time
            
            if transition_elapsed >= self.transition_duration:
                # 过渡完成
                self.current_bg_index = self.next_bg_index
                self.current_background.blit(self.next_background, (0, 0))
                self.background_transition_time = 0
                self.last_bg_change = current_time
                print(f"背景过渡完成，当前背景: {self.current_bg_index}")
            else:
                # 计算过渡进度 (0.0 到 1.0)
                progress = transition_elapsed / self.transition_duration
                eased_progress = self._ease_in_out_cubic(progress)
                
                # 创建混合背景
                blended_bg = self._blend_backgrounds(
                    self.current_background, 
                    self.next_background, 
                    eased_progress
                )
                return blended_bg
        
        return self.current_background
    
    def _set_background_to_surface(self, surface, index):
        """将指定索引的背景设置到指定surface"""
        if 0 <= index < len(self.background_images):
            surface.blit(self.background_images[index], (0, 0))
        else:
            self._create_gradient_background(surface)
    
    def _blend_backgrounds(self, bg1, bg2, alpha):
        """混合两个背景，alpha为0-1之间的值"""
        # 创建临时surface用于混合
        blended = pygame.Surface((self.screen_width, self.screen_height))
        
        # 先绘制第一个背景
        blended.blit(bg1, (0, 0))
        
        # 创建带透明度的第二个背景
        temp_surface = bg2.copy()
        temp_surface.set_alpha(int(255 * alpha))
        
        # 混合绘制
        blended.blit(temp_surface, (0, 0))
        
        return blended
    
    def calculate_positions(self, app_count):
        """计算应用图标位置"""
        total_width = app_count * self.icon_size + (app_count - 1) * self.icon_spacing
        start_x = (self.screen_width - total_width) // 2
        center_y = self.screen_height // 2
        
        positions = []
        for i in range(app_count):
            x = start_x + i * (self.icon_size + self.icon_spacing)
            y = center_y - self.icon_size // 2
            positions.append((x, y))
        return positions
    
    def draw_app_icon(self, app, position, is_selected):
        """绘制应用图标"""
        x, y = position
        
        # 从样式管理器获取桌面样式配置
        desktop_style = self.style_manager.get_desktop_style()
        app_icon_style = desktop_style.get("app_icon", {})
        background_style = app_icon_style.get("background", {})
        
        # 获取颜色配置
        normal_color = background_style.get("normal", [100, 150, 255])
        selected_color = background_style.get("selected", [150, 200, 255])
        border_normal = background_style.get("border_color", {}).get("normal", [128, 128, 128])
        border_selected = background_style.get("border_color", {}).get("selected", [255, 255, 255])
        border_width_normal = background_style.get("border_width", {}).get("normal", 2)
        border_width_selected = background_style.get("border_width", {}).get("selected", 4)
        border_radius = background_style.get("border_radius", 20)
        
        # 图标背景
        color = self.style_manager.get_color(selected_color) if is_selected else self.style_manager.get_color(normal_color)
        border_color = self.style_manager.get_color(border_selected) if is_selected else self.style_manager.get_color(border_normal)
        border_width = border_width_selected if is_selected else border_width_normal
        
        # 绘制圆角矩形背景
        icon_rect = pygame.Rect(x, y, self.icon_size, self.icon_size)
        pygame.draw.rect(self.screen, color, icon_rect, border_radius=border_radius)
        pygame.draw.rect(self.screen, border_color, icon_rect, border_width, border_radius=border_radius)
        
        # 尝试绘制图片图标
        icon_image_path = app.get("icon_image")
        if icon_image_path and self._draw_icon_image(icon_image_path, x, y):
            # 图片图标绘制成功，不需要绘制文字图标
            pass
        else:
            # 绘制文字图标作为备选
            icon_text = self.large_font.render(app["icon_text"], True, self.WHITE)
            text_rect = icon_text.get_rect(center=(x + self.icon_size // 2, y + self.icon_size // 2))
            self.screen.blit(icon_text, text_rect)
        
        # 绘制应用名称（调整位置和字体大小，支持emoji）
        if isinstance(app["name"], str) and app["name"].startswith("️"):
            # 处理emoji占位逻辑
            emoji_text = self.small_font.render(app["name"], True, self.WHITE)
            emoji_rect = emoji_text.get_rect(center=(x + self.icon_size // 2, y + self.icon_size // 2 - 5))
            self.screen.blit(emoji_text, emoji_rect)
        else:
            # 正常文字绘制
            name_text = self.medium_font.render(app["name"], True, self.WHITE)
            name_rect = name_text.get_rect(center=(x + self.icon_size // 2, y + self.icon_size // 2 + 15))
            self.screen.blit(name_text, name_rect)
        
        # 如果选中，显示描述
        if is_selected:
            desc_text = self.small_font.render(app["description"], True, self.WHITE)
            desc_rect = desc_text.get_rect(center=(x + self.icon_size // 2, y + self.icon_size + 65))
            self.screen.blit(desc_text, desc_rect)
    
    def _draw_icon_image(self, icon_path, x, y):
        """绘制图片图标"""
        try:
            icon_surface = None
            
            # 检查是否是SVG文件
            if icon_path.lower().endswith('.svg'):
                icon_surface = self._load_svg_icon(icon_path)
            else:
                # 加载普通图片
                icon_surface = pygame.image.load(icon_path)
            
            if not icon_surface:
                return False
            
            # 计算缩放尺寸，保持图标在背景框内，留出边距
            icon_margin = 20  # 图标与背景框的边距
            target_size = self.icon_size - icon_margin * 2
            
            # 获取原始尺寸
            original_width, original_height = icon_surface.get_size()
            
            # 计算缩放比例，保持宽高比
            scale_x = target_size / original_width
            scale_y = target_size / original_height
            scale = min(scale_x, scale_y)
            
            # 计算新尺寸
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            # 缩放图片
            scaled_icon = pygame.transform.scale(icon_surface, (new_width, new_height))
            
            # 计算居中位置
            icon_x = x + (self.icon_size - new_width) // 2
            icon_y = y + (self.icon_size - new_height) // 2
            
            # 绘制图标
            self.screen.blit(scaled_icon, (icon_x, icon_y))
            
            return True
            
        except Exception as e:
            print(f"加载图标失败 {icon_path}: {e}")
            return False
    
    def _load_svg_icon(self, svg_path):
        """加载SVG图标并转换为pygame surface"""
        try:
            import cairosvg
            import io
            from PIL import Image
            
            # 将SVG转换为PNG数据，设置超时
            png_data = cairosvg.svg2png(
                url=svg_path, 
                output_width=128, 
                output_height=128,
                unsafe=True  # 允许不安全的SVG
            )
            
            # 使用PIL加载PNG数据
            pil_image = Image.open(io.BytesIO(png_data))
            
            # 转换为RGBA模式
            if pil_image.mode != 'RGBA':
                pil_image = pil_image.convert('RGBA')
            
            # 转换为pygame surface
            pygame_image = pygame.image.fromstring(
                pil_image.tobytes(), pil_image.size, 'RGBA'
            )
            
            return pygame_image
            
        except Exception as e:
            print(f"SVG图标加载失败 {svg_path}: {e}")
            # 尝试寻找同名的PNG图标
            png_path = svg_path.replace('.svg', '.png')
            if Path(png_path).exists():
                try:
                    return pygame.image.load(png_path)
                except:
                    pass
            return None
    
    def draw_instructions(self):
        """绘制操作说明"""
        instructions = [
            "使用方向键或手柄左摇杆选择应用",
            "按确认键(A键/回车)启动应用",
            "按Tab键或Y键打开设置",
            "按Del键删除选中的应用",
            "按ESC键退出桌面"
        ]
        
        y_start = self.screen_height - 180
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.WHITE)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_start + i * 25))
            self.screen.blit(text, text_rect)
    
    def render_frame(self, apps, selected_app, title="", show_title=True):
        """渲染一帧"""
        self._render_desktop_content(apps, selected_app, title, show_title)
        
        # 更新显示
        pygame.display.flip()
    
    def render_background_only(self, apps, selected_app, title="", show_title=False):
        """只渲染桌面内容，不刷新显示（用于设置页面背景）"""
        self._render_desktop_content(apps, selected_app, title, show_title)
    
    def _render_desktop_content(self, apps, selected_app, title="", show_title=True):
        """渲染桌面内容（不包含显示刷新）"""
        # 更新并绘制背景（包含轮播和过渡效果）
        current_bg = self.update_background()
        self.screen.blit(current_bg, (0, 0))
        
        # 绘制标题（如果需要）
        if show_title and title:
            title_text = self.large_font.render(title, True, self.WHITE)
            title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
            self.screen.blit(title_text, title_rect)
        
        # 计算图标位置
        positions = self.calculate_positions(len(apps))
        
        # 绘制应用图标
        for i, app in enumerate(apps):
            is_selected = (i == selected_app)
            self.draw_app_icon(app, positions[i], is_selected)
        
        # 绘制操作说明
        self.draw_instructions()
    
    def cleanup(self):
        """清理资源"""
        pygame.quit()

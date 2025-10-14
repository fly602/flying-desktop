#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
确认对话框模块
用于显示删除确认等操作确认
"""

import pygame


class ConfirmDialog:
    """确认对话框"""
    
    def __init__(self, title, message, confirm_text="确认", cancel_text="取消"):
        self.title = title
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.selected_option = 0  # 0: 取消, 1: 确认
        self.visible = False
        
        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (100, 150, 255)
        self.LIGHT_BLUE = (150, 200, 255)
        self.GRAY = (128, 128, 128)
        self.RED = (255, 100, 100)
        self.GREEN = (100, 255, 100)
    
    def show(self, title=None, message=None):
        """显示对话框"""
        if title:
            self.title = title
        if message:
            self.message = message
        self.visible = True
        self.selected_option = 0  # 默认选中取消
    
    def hide(self):
        """隐藏对话框"""
        self.visible = False
    
    def is_visible(self):
        """对话框是否可见"""
        return self.visible
    
    def handle_input(self, event):
        """处理输入事件"""
        if not self.visible:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_option = 0  # 选择取消
                return 'select'
            elif event.key == pygame.K_RIGHT:
                self.selected_option = 1  # 选择确认
                return 'select'
            elif event.key == pygame.K_RETURN:
                if self.selected_option == 0:
                    return 'cancel'
                else:
                    return 'confirm'
            elif event.key == pygame.K_ESCAPE:
                return 'cancel'
        
        return None
    
    def render(self, screen, font_large, font_medium, font_small):
        """渲染对话框"""
        if not self.visible:
            return
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # 计算对话框尺寸
        dialog_width = min(600, screen_width - 100)
        dialog_height = 200
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2
        
        # 绘制半透明背景遮罩
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(180)
        overlay.fill(self.BLACK)
        screen.blit(overlay, (0, 0))
        
        # 绘制对话框背景
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(screen, self.GRAY, dialog_rect, border_radius=15)
        pygame.draw.rect(screen, self.WHITE, dialog_rect, 3, border_radius=15)
        
        # 绘制标题 - 使用中等字体大小，避免太大
        title_surface = font_medium.render(self.title, True, self.WHITE)
        title_rect = title_surface.get_rect(centerx=screen_width // 2, top=dialog_y + 20)
        screen.blit(title_surface, title_rect)
        
        # 绘制消息文本 - 使用小字体，避免字体过大
        # 处理多行消息
        message_lines = self._wrap_text(self.message, font_small, dialog_width - 40)
        message_y = dialog_y + 60
        for line in message_lines:
            message_surface = font_small.render(line, True, self.WHITE)
            message_rect = message_surface.get_rect(centerx=screen_width // 2, top=message_y)
            screen.blit(message_surface, message_rect)
            message_y += 25
        
        # 绘制按钮
        button_width = 120
        button_height = 40
        button_spacing = 40
        total_button_width = 2 * button_width + button_spacing
        start_x = (screen_width - total_button_width) // 2
        button_y = dialog_y + dialog_height - 70
        
        # 取消按钮
        cancel_rect = pygame.Rect(start_x, button_y, button_width, button_height)
        cancel_color = self.LIGHT_BLUE if self.selected_option == 0 else self.BLUE
        pygame.draw.rect(screen, cancel_color, cancel_rect, border_radius=8)
        pygame.draw.rect(screen, self.WHITE, cancel_rect, 2, border_radius=8)
        
        cancel_text = font_medium.render(self.cancel_text, True, self.WHITE)
        cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
        screen.blit(cancel_text, cancel_text_rect)
        
        # 确认按钮
        confirm_rect = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height)
        confirm_color = self.RED if self.selected_option == 1 else self.GREEN
        pygame.draw.rect(screen, confirm_color, confirm_rect, border_radius=8)
        pygame.draw.rect(screen, self.WHITE, confirm_rect, 2, border_radius=8)
        
        confirm_text = font_medium.render(self.confirm_text, True, self.WHITE)
        confirm_text_rect = confirm_text.get_rect(center=confirm_rect.center)
        screen.blit(confirm_text, confirm_text_rect)
        
        # 绘制操作提示
        hint_text = font_small.render("使用方向键选择，回车确认，ESC取消", True, self.WHITE)
        hint_rect = hint_text.get_rect(centerx=screen_width // 2, top=button_y + button_height + 15)
        screen.blit(hint_text, hint_rect)
    
    def _wrap_text(self, text, font, max_width):
        """文本换行处理"""
        words = text.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_surface = font.render(word, True, (255, 255, 255))
            word_width = word_surface.get_width()
            
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width + 5  # 添加空格宽度
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]

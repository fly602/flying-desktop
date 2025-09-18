#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体检测模块
检测系统中可用的中文字体
"""

import subprocess
import pygame
from pathlib import Path


class FontDetector:
    """字体检测器"""
    
    def __init__(self):
        self.available_fonts = []
        self.font_cache = {}
        
    def detect_system_fonts(self):
        """检测系统中可用的中文字体"""
        fonts = []
        
        # 添加自动选择选项
        fonts.append({
            'key': 'auto',
            'name': '自动选择',
            'path': None,
            'priority': 0
        })
        
        # 检测系统字体
        system_fonts = self._get_system_chinese_fonts()
        
        # 按优先级排序并添加到列表
        for font_info in system_fonts:
            if self._test_font_rendering(font_info['path']):
                fonts.append(font_info)
        
        # 按优先级排序
        fonts.sort(key=lambda x: x['priority'])
        
        self.available_fonts = fonts
        return fonts
    
    def _get_system_chinese_fonts(self):
        """获取系统中文字体列表"""
        fonts = []
        
        # 预定义的中文字体列表（按优先级排序）
        known_fonts = [
            {
                'key': 'wqy_zenhei',
                'name': '文泉驿正黑',
                'paths': [
                    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
                    '/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc'
                ],
                'priority': 1
            },
            {
                'key': 'wqy_microhei',
                'name': '文泉驿微米黑',
                'paths': [
                    '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                    '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc'
                ],
                'priority': 2
            },
            {
                'key': 'noto_cjk',
                'name': 'Noto Sans CJK',
                'paths': [
                    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                    '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
                    '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'
                ],
                'priority': 3
            },
            {
                'key': 'source_han',
                'name': '思源黑体',
                'paths': [
                    '/usr/share/fonts/opentype/source-han-cjk/SourceHanSansSC-Regular.otf',
                    '/usr/share/fonts/opentype/source-han-sans/SourceHanSansSC-Regular.otf',
                    '/usr/share/fonts/source-han-sans/SourceHanSansSC-Regular.otf'
                ],
                'priority': 4
            },
            {
                'key': 'droid_fallback',
                'name': 'Droid Sans Fallback',
                'paths': [
                    '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
                    '/usr/share/fonts/droid/DroidSansFallbackFull.ttf'
                ],
                'priority': 5
            },
            {
                'key': 'unifont',
                'name': 'Unifont',
                'paths': [
                    '/usr/share/fonts/truetype/unifont/unifont.ttf',
                    '/usr/share/fonts/unifont/unifont.ttf'
                ],
                'priority': 6
            }
        ]
        
        # 检查预定义字体
        for font_info in known_fonts:
            for path in font_info['paths']:
                if Path(path).exists():
                    fonts.append({
                        'key': font_info['key'],
                        'name': font_info['name'],
                        'path': path,
                        'priority': font_info['priority']
                    })
                    break
        
        # 使用fontconfig查找更多中文字体
        try:
            additional_fonts = self._find_fonts_with_fontconfig()
            fonts.extend(additional_fonts)
        except Exception as e:
            print(f"fontconfig查找字体失败: {e}")
        
        return fonts
    
    def _find_fonts_with_fontconfig(self):
        """使用fontconfig查找中文字体"""
        fonts = []
        
        try:
            # 查找支持中文的字体
            result = subprocess.run(
                ['fc-list', ':lang=zh', 'family', 'file'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                seen_paths = set()
                priority = 10  # 动态发现的字体优先级较低
                
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            font_path = parts[0].strip()
                            font_family = parts[1].strip()
                            
                            # 过滤重复和已知字体
                            if (font_path not in seen_paths and 
                                Path(font_path).exists() and
                                self._is_suitable_font(font_family, font_path)):
                                
                                seen_paths.add(font_path)
                                fonts.append({
                                    'key': f'custom_{len(fonts)}',
                                    'name': font_family,
                                    'path': font_path,
                                    'priority': priority
                                })
                                priority += 1
                                
                                # 限制动态发现的字体数量
                                if len(fonts) >= 5:
                                    break
        
        except Exception as e:
            print(f"fontconfig查找失败: {e}")
        
        return fonts
    
    def _is_suitable_font(self, font_family, font_path):
        """判断字体是否适合用作界面字体"""
        # 过滤掉一些不适合的字体
        unsuitable_keywords = [
            'mono', 'serif', 'italic', 'bold', 'light', 'thin',
            'condensed', 'extended', 'outline', 'shadow'
        ]
        
        family_lower = font_family.lower()
        path_lower = font_path.lower()
        
        # 检查是否包含不适合的关键词
        for keyword in unsuitable_keywords:
            if keyword in family_lower or keyword in path_lower:
                return False
        
        # 检查文件扩展名
        valid_extensions = ['.ttf', '.ttc', '.otf']
        if not any(font_path.lower().endswith(ext) for ext in valid_extensions):
            return False
        
        return True
    
    def _test_font_rendering(self, font_path):
        """测试字体是否能正确渲染中文"""
        if not font_path or not Path(font_path).exists():
            return True  # 自动选择选项
        
        # 如果已经测试过，直接返回缓存结果
        if font_path in self.font_cache:
            return self.font_cache[font_path]
        
        try:
            # 尝试加载字体
            font = pygame.font.Font(font_path, 24)
            
            # 测试渲染中文文本
            test_text = "测试中文字体"
            surface = font.render(test_text, True, (255, 255, 255))
            
            # 检查渲染结果是否有效
            if surface.get_width() > 0 and surface.get_height() > 0:
                self.font_cache[font_path] = True
                return True
            else:
                self.font_cache[font_path] = False
                return False
                
        except Exception as e:
            print(f"字体测试失败 {font_path}: {e}")
            self.font_cache[font_path] = False
            return False
    
    def get_font_options(self):
        """获取字体选项列表（用于设置界面）"""
        if not self.available_fonts:
            self.detect_system_fonts()
        
        return [font['key'] for font in self.available_fonts]
    
    def get_font_names(self):
        """获取字体名称映射"""
        if not self.available_fonts:
            self.detect_system_fonts()
        
        return {font['key']: font['name'] for font in self.available_fonts}
    
    def get_font_path(self, font_key):
        """根据字体键获取字体路径"""
        if not self.available_fonts:
            self.detect_system_fonts()
        
        for font in self.available_fonts:
            if font['key'] == font_key:
                return font['path']
        
        return None
    
    def get_available_fonts_info(self):
        """获取所有可用字体信息"""
        if not self.available_fonts:
            self.detect_system_fonts()
        
        return self.available_fonts.copy()
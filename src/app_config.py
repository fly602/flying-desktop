#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置加载器
支持从desktop文件和AppImage加载应用配置
"""

from pathlib import Path
from .desktop_parser import DesktopParser


class AppConfigLoader:
    """应用配置加载器"""
    
    def __init__(self):
        self.apps = []
        self.desktop_parser = DesktopParser()
        self.load_apps()
    
    def load_apps(self):
        """加载应用配置"""
        # 从注册表加载应用
        try:
            desktop_apps = self.desktop_parser.get_all_applications()
            self.apps = self._convert_desktop_apps(desktop_apps)
            print(f"从注册表加载了 {len(self.apps)} 个应用")
            
            if len(self.apps) == 0:
                print("注册表为空，请使用 'python manage_apps.py add-desktop' 或 'python manage_apps.py add-appimage' 添加应用")
                
        except Exception as e:
            print(f"从注册表加载应用失败: {e}")
            self.apps = []
    
    def _convert_desktop_apps(self, desktop_apps):
        """将desktop应用转换为内部格式"""
        converted_apps = []
        
        # 过滤和排序应用
        filtered_apps = []
        for app in desktop_apps:
            # 跳过一些系统应用
            if self._should_skip_app(app):
                continue
            filtered_apps.append(app)
        
        # 按名称排序
        filtered_apps.sort(key=lambda x: x['name'].lower())
        
        # 限制应用数量，避免界面过于拥挤
        max_apps = 12
        if len(filtered_apps) > max_apps:
            # 优先选择常用应用
            priority_categories = ['Network', 'Office', 'Graphics', 'AudioVideo', 'Development', 'Game']
            priority_apps = []
            other_apps = []
            
            for app in filtered_apps:
                categories = app.get('categories', [])
                if any(cat in priority_categories for cat in categories):
                    priority_apps.append(app)
                else:
                    other_apps.append(app)
            
            # 选择优先应用和部分其他应用
            selected_apps = priority_apps[:max_apps//2] + other_apps[:max_apps//2]
            filtered_apps = selected_apps[:max_apps]
        
        for app in filtered_apps:
            # 获取图标路径
            icon_path = None
            icon_name = app.get('icon', '')
            if icon_name:
                # 如果已经是完整路径，直接使用
                if Path(icon_name).is_absolute() and Path(icon_name).exists():
                    icon_path = icon_name
                else:
                    # 否则搜索图标
                    icon_path = self.desktop_parser.get_icon_path(icon_name)
            
            converted_app = {
                'name': app['name'],
                'description': app['description'],
                'command': app['exec'],
                'icon_text': self._get_icon_text(app),
                'icon_image': icon_path,
                'enabled': True,
                'category': self._get_main_category(app.get('categories', [])),
                'desktop_file': app.get('desktop_file', ''),
                'type': app.get('type', 'desktop')
            }
            
            # 调试信息
            if icon_path:
                print(f"应用 {app['name']} 图标路径: {icon_path}")
            else:
                print(f"应用 {app['name']} 未找到图标: {icon_name}")
            converted_apps.append(converted_app)
        
        return converted_apps
    
    def _should_skip_app(self, app):
        """判断是否应该跳过某个应用"""
        # 对于手动添加的应用，不进行过滤
        return False
    
    def _get_icon_text(self, app):
        """获取应用的图标文字"""
        name = app['name']
        
        # 对于中文应用名，取第一个字符
        if any('\u4e00' <= char <= '\u9fff' for char in name):
            return name[0]
        
        # 对于英文应用名，取首字母
        words = name.split()
        if len(words) >= 2:
            return ''.join(word[0].upper() for word in words[:2])
        else:
            return name[0].upper()
    
    def _get_main_category(self, categories):
        """获取主要分类"""
        category_map = {
            'Network': 'internet',
            'WebBrowser': 'internet',
            'Email': 'internet',
            'Office': 'office',
            'TextEditor': 'office',
            'WordProcessor': 'office',
            'Spreadsheet': 'office',
            'Graphics': 'multimedia',
            'Photography': 'multimedia',
            'AudioVideo': 'multimedia',
            'Audio': 'multimedia',
            'Video': 'multimedia',
            'Development': 'development',
            'IDE': 'development',
            'Game': 'game',
            'Utility': 'utility',
            'Accessories': 'utility',
            'System': 'system',
            'FileManager': 'system',
            'TerminalEmulator': 'system'
        }
        
        for category in categories:
            if category in category_map:
                return category_map[category]
        
        return 'other'
    

    
    def get_apps(self):
        """获取应用列表"""
        return self.apps
    
    def get_apps_by_category(self, category=None):
        """按分类获取应用"""
        if category is None:
            return self.apps
        
        return [app for app in self.apps if app.get('category') == category]
    
    def get_categories(self):
        """获取所有分类"""
        categories = set()
        for app in self.apps:
            categories.add(app.get('category', 'other'))
        return sorted(list(categories))
    
    def refresh_apps(self):
        """刷新应用列表"""
        self.load_apps()
    
    def add_desktop_file(self, desktop_file_path):
        """添加desktop文件"""
        try:
            app = self.desktop_parser.add_desktop_file(desktop_file_path)
            self.refresh_apps()
            return True, f"成功添加应用: {app['name']}"
        except Exception as e:
            return False, str(e)
    
    def add_appimage_file(self, appimage_file_path):
        """添加AppImage文件"""
        try:
            app = self.desktop_parser.add_appimage_file(appimage_file_path)
            self.refresh_apps()
            return True, f"成功添加应用: {app['name']}"
        except Exception as e:
            return False, str(e)
    
    def remove_application(self, app_name):
        """移除应用"""
        try:
            if self.desktop_parser.remove_application(app_name):
                self.refresh_apps()
                return True, f"成功移除应用: {app_name}"
            else:
                return False, "应用不存在"
        except Exception as e:
            return False, str(e)
    
    def list_registered_apps(self):
        """列出所有已注册的应用"""
        return self.desktop_parser.list_applications()
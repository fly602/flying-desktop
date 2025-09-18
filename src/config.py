#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责加载和管理分层配置系统
"""

import json
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config = {}
        self.load_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "desktop": {
                "title": "Flying Desktop",
                "fullscreen": True,
                "hide_mouse": True,
                "background_image": "assets/backgrounds/default.png",
                "background_duration": 10000,  # 背景显示时长(毫秒)
                "transition_duration": 2000,   # 过渡动画时长(毫秒)
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
    
    def get_config_paths(self):
        """获取配置文件搜索路径（按优先级排序）"""
        return [
            # 1. 用户自定义配置（最高优先级）
            Path.home() / ".config" / "flying-desktop" / "config.json",
            # 2. 当前目录配置
            Path("config.json"),
            # 3. 系统安装配置
            Path("/opt/simple_desktop/config.json"),
            Path("/usr/share/flying-desktop/config.json"),
        ]
    
    def load_config(self):
        """加载配置文件 - 支持系统默认配置和用户自定义配置"""
        self.config = self.get_default_config().copy()
        loaded_configs = []
        
        # 按优先级加载配置文件
        for config_path in reversed(self.get_config_paths()):  # 从低优先级到高优先级
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
        self._ensure_user_config()
    
    def _merge_config(self, base_config, new_config):
        """深度合并配置字典"""
        for key, value in new_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
    
    def _ensure_user_config(self):
        """确保用户配置目录存在"""
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
    
    def get(self, key, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def get_apps(self):
        """获取启用的应用列表"""
        return [app for app in self.config.get("apps", []) if app.get("enabled", True)]
    
    def save_user_config(self):
        """保存用户配置"""
        user_config_file = Path.home() / ".config" / "flying-desktop" / "config.json"
        
        try:
            user_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(user_config_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"用户配置已保存: {user_config_file}")
        except Exception as e:
            print(f"保存用户配置失败: {e}")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flying Desktop 应用管理工具
用于手动添加和管理desktop文件和AppImage文件
"""

import sys
import argparse
from pathlib import Path
from src.app_config import AppConfigLoader


def main():
    parser = argparse.ArgumentParser(description='Flying Desktop 应用管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 添加desktop文件
    add_desktop_parser = subparsers.add_parser('add-desktop', help='添加desktop文件')
    add_desktop_parser.add_argument('file', help='desktop文件路径')
    
    # 添加AppImage文件
    add_appimage_parser = subparsers.add_parser('add-appimage', help='添加AppImage文件')
    add_appimage_parser.add_argument('file', help='AppImage文件路径')
    
    # 列出应用
    list_parser = subparsers.add_parser('list', help='列出所有已注册的应用')
    
    # 移除应用
    remove_parser = subparsers.add_parser('remove', help='移除应用')
    remove_parser.add_argument('name', help='应用名称')
    
    # 清空所有应用
    clear_parser = subparsers.add_parser('clear', help='清空所有应用')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 初始化应用配置加载器
    app_loader = AppConfigLoader()
    
    if args.command == 'add-desktop':
        success, message = app_loader.add_desktop_file(args.file)
        print(message)
        sys.exit(0 if success else 1)
    
    elif args.command == 'add-appimage':
        success, message = app_loader.add_appimage_file(args.file)
        print(message)
        sys.exit(0 if success else 1)
    
    elif args.command == 'list':
        apps = app_loader.list_registered_apps()
        if not apps:
            print("没有已注册的应用")
        else:
            print(f"已注册的应用 ({len(apps)} 个):")
            print("-" * 60)
            for name, app_type, exec_cmd, desktop_file in apps:
                print(f"名称: {name}")
                print(f"类型: {app_type}")
                print(f"命令: {exec_cmd}")
                if desktop_file:
                    print(f"文件: {desktop_file}")
                print("-" * 60)
    
    elif args.command == 'remove':
        success, message = app_loader.remove_application(args.name)
        print(message)
        sys.exit(0 if success else 1)
    
    elif args.command == 'clear':
        # 清空注册表
        cache_dir = Path.home() / ".cache" / "flying-desktop" / "applications"
        registry_file = cache_dir / "registry.json"
        
        if registry_file.exists():
            registry_file.unlink()
            print("已清空所有应用注册")
        
        # 清空缓存目录
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
            print("已清空应用缓存")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用启动模块
负责启动外部应用程序
"""

import subprocess
import shlex
import os
from pathlib import Path


class AppLauncher:
    """应用启动器"""
    
    def __init__(self):
        pass
    
    def launch_app(self, app):
        """启动应用"""
        try:
            print(f"启动应用: {app['name']}")
            
            # 获取启动命令
            cmd = app.get("command", "")
            if not cmd:
                print(f"应用 {app['name']} 没有启动命令")
                return False
            
            # 根据应用类型处理启动命令
            app_type = app.get('type', 'desktop')
            
            if app_type == 'appimage':
                # AppImage文件直接执行
                return self._launch_appimage(cmd, app)
            elif app_type == 'desktop':
                # Desktop文件中的Exec命令
                return self._launch_desktop_command(cmd, app)
            else:
                # 传统的shell命令
                return self._launch_shell_command(cmd, app)
                
        except Exception as e:
            print(f"启动 {app['name']} 失败: {e}")
            return False
    
    def _launch_appimage(self, appimage_path, app):
        """启动AppImage应用"""
        appimage_file = Path(appimage_path)
        
        if not appimage_file.exists():
            print(f"AppImage文件不存在: {appimage_path}")
            return False
        
        if not os.access(appimage_file, os.X_OK):
            print(f"AppImage文件没有执行权限: {appimage_path}")
            return False
        
        # 直接执行AppImage
        subprocess.Popen(
            [str(appimage_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return True
    
    def _launch_desktop_command(self, exec_cmd, app):
        """启动desktop文件中的Exec命令"""
        # 解析Exec命令
        try:
            # 使用shlex安全地分割命令
            cmd_parts = shlex.split(exec_cmd)
            
            if not cmd_parts:
                print(f"无效的Exec命令: {exec_cmd}")
                return False
            
            # 检查命令是否存在
            executable = cmd_parts[0]
            if not self._command_exists(executable):
                print(f"命令不存在: {executable}")
                return False
            
            # 启动应用
            subprocess.Popen(
                cmd_parts,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return True
            
        except Exception as e:
            print(f"解析Exec命令失败: {exec_cmd}, 错误: {e}")
            # 回退到shell执行
            return self._launch_shell_command(exec_cmd, app)
    
    def _launch_shell_command(self, cmd, app):
        """使用shell启动命令"""
        subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return True
    
    def _command_exists(self, command):
        """检查命令是否存在"""
        # 如果是绝对路径，直接检查文件是否存在
        if os.path.isabs(command):
            return os.path.isfile(command) and os.access(command, os.X_OK)
        
        # 在PATH中查找命令
        for path in os.environ.get("PATH", "").split(os.pathsep):
            if path:
                full_path = os.path.join(path, command)
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    return True
        
        return False
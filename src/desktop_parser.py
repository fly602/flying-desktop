#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Desktop文件解析器
支持解析.desktop文件和AppImage文件
"""

import os
import configparser
import subprocess
import shutil
import json
import hashlib
from pathlib import Path
import tempfile


class DesktopParser:
    """Desktop文件解析器"""
    
    def __init__(self):
        self.cache_dir = Path.home() / ".cache" / "flying-desktop" / "applications"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 应用注册表文件
        self.registry_file = self.cache_dir / "registry.json"
        self.applications = self._load_registry()
    
    def _load_registry(self):
        """加载应用注册表"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载应用注册表失败: {e}")
        return []
    
    def _save_registry(self):
        """保存应用注册表"""
        try:
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.applications, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存应用注册表失败: {e}")
    
    def get_all_applications(self):
        """获取所有已注册的应用程序"""
        # 验证应用是否仍然存在
        valid_apps = []
        for app in self.applications:
            if self._validate_application(app):
                valid_apps.append(app)
        
        # 如果有应用被移除，更新注册表
        if len(valid_apps) != len(self.applications):
            self.applications = valid_apps
            self._save_registry()
        
        return self.applications
    
    def _validate_application(self, app):
        """验证应用是否仍然有效"""
        app_type = app.get('type', 'desktop')
        
        if app_type == 'appimage':
            # 检查AppImage文件是否存在
            return Path(app['exec']).exists()
        elif app_type == 'desktop':
            # 检查desktop文件是否存在
            desktop_file = app.get('desktop_file', '')
            if desktop_file and Path(desktop_file).exists():
                return True
            # 或者检查执行命令是否存在
            exec_cmd = app.get('exec', '').split()[0] if app.get('exec') else ''
            return self._command_exists(exec_cmd) if exec_cmd else False
        
        return False
    
    def _command_exists(self, command):
        """检查命令是否存在"""
        import shutil
        return shutil.which(command) is not None
    
    def _parse_desktop_directory(self, directory):
        """解析目录中的所有desktop文件"""
        applications = []
        
        for desktop_file in directory.glob("*.desktop"):
            try:
                app = self._parse_desktop_file(desktop_file)
                if app:
                    applications.append(app)
            except Exception as e:
                print(f"解析desktop文件失败 {desktop_file}: {e}")
        
        return applications
    
    def _parse_desktop_file(self, desktop_file):
        """解析单个desktop文件"""
        config = configparser.RawConfigParser()  # 使用RawConfigParser避免插值问题
        config.read(desktop_file, encoding='utf-8')
        
        if 'Desktop Entry' not in config:
            return None
        
        entry = config['Desktop Entry']
        
        # 跳过隐藏的应用
        if entry.getboolean('Hidden', False) or entry.getboolean('NoDisplay', False):
            return None
        
        # 检查应用类型
        if entry.get('Type', '') != 'Application':
            return None
        
        # 获取本地化名称
        name = self._get_localized_value(entry, 'Name')
        if not name:
            return None
        
        # 获取执行命令
        exec_cmd = entry.get('Exec', '')
        if not exec_cmd:
            return None
        
        # 清理Exec命令（移除%f, %F, %u, %U等参数）
        exec_cmd = self._clean_exec_command(exec_cmd)
        
        return {
            'name': name,
            'description': self._get_localized_value(entry, 'Comment', ''),
            'exec': exec_cmd,
            'icon': entry.get('Icon', ''),
            'categories': entry.get('Categories', '').split(';'),
            'desktop_file': str(desktop_file),
            'type': 'desktop'
        }
    
    def add_desktop_file(self, desktop_file_path):
        """手动添加desktop文件"""
        desktop_path = Path(desktop_file_path)
        
        if not desktop_path.exists():
            raise FileNotFoundError(f"Desktop文件不存在: {desktop_file_path}")
        
        if not desktop_path.suffix.lower() == '.desktop':
            raise ValueError("文件必须是.desktop文件")
        
        # 解析desktop文件
        app = self._parse_desktop_file(desktop_path)
        if not app:
            raise ValueError("无法解析desktop文件")
        
        # 检查是否已经存在
        for existing_app in self.applications:
            if existing_app.get('desktop_file') == str(desktop_path):
                raise ValueError("该desktop文件已经添加")
        
        # 创建缓存的desktop文件
        cache_filename = f"{desktop_path.stem}_{hashlib.md5(str(desktop_path).encode()).hexdigest()[:8]}.desktop"
        cache_path = self.cache_dir / cache_filename
        
        # 复制desktop文件到缓存目录
        shutil.copy2(desktop_path, cache_path)
        
        # 更新应用信息
        app['desktop_file'] = str(cache_path)
        app['original_file'] = str(desktop_path)
        
        # 添加到注册表
        self.applications.append(app)
        self._save_registry()
        
        print(f"成功添加desktop应用: {app['name']}")
        return app
    
    def add_appimage_file(self, appimage_file_path):
        """手动添加AppImage文件"""
        appimage_path = Path(appimage_file_path)
        
        if not appimage_path.exists():
            raise FileNotFoundError(f"AppImage文件不存在: {appimage_file_path}")
        
        if not appimage_path.suffix.lower() == '.appimage':
            raise ValueError("文件必须是.AppImage文件")
        
        if not os.access(appimage_path, os.X_OK):
            raise ValueError("AppImage文件没有执行权限")
        
        # 检查是否已经存在
        for existing_app in self.applications:
            if existing_app.get('exec') == str(appimage_path):
                raise ValueError("该AppImage文件已经添加")
        
        # 解析AppImage
        app = self._parse_appimage(appimage_path)
        if not app:
            raise ValueError("无法解析AppImage文件")
        
        # 添加到注册表
        self.applications.append(app)
        self._save_registry()
        
        print(f"成功添加AppImage应用: {app['name']}")
        return app
    
    def remove_application(self, app_id):
        """移除应用"""
        # app_id可以是应用名称或desktop文件路径
        for i, app in enumerate(self.applications):
            if (app.get('name') == app_id or 
                app.get('desktop_file') == app_id or
                app.get('exec') == app_id):
                
                # 删除缓存的desktop文件
                desktop_file = app.get('desktop_file', '')
                if desktop_file and desktop_file.startswith(str(self.cache_dir)):
                    try:
                        Path(desktop_file).unlink()
                    except:
                        pass
                
                # 从注册表移除
                self.applications.pop(i)
                self._save_registry()
                
                print(f"成功移除应用: {app.get('name', app_id)}")
                return True
        
        return False
    
    def list_applications(self):
        """列出所有已注册的应用"""
        return [(app.get('name', '未知'), app.get('type', 'unknown'), 
                app.get('exec', ''), app.get('desktop_file', '')) 
                for app in self.applications]
    
    def _parse_appimage(self, appimage_file):
        """解析AppImage文件"""
        # 生成缓存文件名
        file_hash = hashlib.md5(str(appimage_file).encode()).hexdigest()[:8]
        cache_file = self.cache_dir / f"{appimage_file.stem}_{file_hash}.desktop"
        
        # 如果缓存存在且AppImage没有更新，直接使用缓存
        if (cache_file.exists() and 
            cache_file.stat().st_mtime > appimage_file.stat().st_mtime):
            return self._parse_desktop_file(cache_file)
        
        # 尝试从AppImage提取desktop文件
        desktop_content = self._extract_appimage_desktop(appimage_file)
        extracted_icon_path = None
        
        if desktop_content:
            # 保存到缓存
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(desktop_content)
            
            # 解析缓存的desktop文件
            app = self._parse_desktop_file(cache_file)
            if app:
                # 更新Exec命令为AppImage路径
                app['exec'] = str(appimage_file)
                app['type'] = 'appimage'
                
                # 如果提取了图标，更新图标路径
                icon_name = app.get('icon', '')
                if icon_name:
                    # 查找提取的图标文件
                    for cached_file in self.cache_dir.glob(f"{appimage_file.stem}_*"):
                        if cached_file.suffix.lower() in ['.png', '.svg', '.xpm', '.ico']:
                            app['icon'] = str(cached_file)
                            break
                
                return app
        
        # 如果无法提取desktop文件，创建基本信息
        return {
            'name': appimage_file.stem,
            'description': f'AppImage应用: {appimage_file.stem}',
            'exec': str(appimage_file),
            'icon': '',
            'categories': ['Other'],
            'desktop_file': str(cache_file),
            'type': 'appimage'
        }
    
    def _extract_appimage_desktop(self, appimage_file):
        """从AppImage提取desktop文件内容"""
        extract_dir = None
        try:
            # 创建临时提取目录
            extract_dir = Path(tempfile.mkdtemp())
            
            # 方法1: 使用--appimage-extract
            result = subprocess.run([
                str(appimage_file), '--appimage-extract'
            ], capture_output=True, text=True, timeout=30, cwd=extract_dir)
            
            if result.returncode == 0:
                # 查找提取的desktop文件
                squashfs_dir = extract_dir / "squashfs-root"
                if squashfs_dir.exists():
                    for desktop_file in squashfs_dir.rglob("*.desktop"):
                        if desktop_file.is_file():
                            content = desktop_file.read_text(encoding='utf-8')
                            
                            # 同时提取图标文件
                            self._extract_appimage_icon(squashfs_dir, appimage_file)
                            
                            return content
        except Exception as e:
            print(f"AppImage desktop提取失败: {e}")
        finally:
            # 清理提取目录
            if extract_dir and extract_dir.exists():
                shutil.rmtree(extract_dir, ignore_errors=True)
        
        return None
    
    def _extract_appimage_icon(self, squashfs_dir, appimage_file):
        """从AppImage提取图标文件"""
        try:
            # 查找图标文件
            icon_extensions = ['.png', '.svg', '.xpm', '.ico']
            icon_dirs = ['usr/share/icons', 'usr/share/pixmaps', 'share/icons', 'share/pixmaps']
            
            for icon_dir in icon_dirs:
                icon_path = squashfs_dir / icon_dir
                if icon_path.exists():
                    for icon_file in icon_path.rglob("*"):
                        if (icon_file.is_file() and 
                            icon_file.suffix.lower() in icon_extensions):
                            
                            # 复制图标到缓存目录
                            cache_icon_name = f"{appimage_file.stem}_{icon_file.name}"
                            cache_icon_path = self.cache_dir / cache_icon_name
                            
                            shutil.copy2(icon_file, cache_icon_path)
                            print(f"提取AppImage图标: {cache_icon_path}")
                            return str(cache_icon_path)
            
            # 如果没有找到标准图标，查找任何图片文件
            for icon_file in squashfs_dir.rglob("*"):
                if (icon_file.is_file() and 
                    icon_file.suffix.lower() in icon_extensions and
                    icon_file.stat().st_size < 1024 * 1024):  # 小于1MB的图片
                    
                    cache_icon_name = f"{appimage_file.stem}_{icon_file.name}"
                    cache_icon_path = self.cache_dir / cache_icon_name
                    
                    shutil.copy2(icon_file, cache_icon_path)
                    print(f"提取AppImage图标: {cache_icon_path}")
                    return str(cache_icon_path)
                    
        except Exception as e:
            print(f"提取AppImage图标失败: {e}")
        
        return None
    
    def _get_localized_value(self, entry, key, default=''):
        """获取本地化的值"""
        # 尝试获取中文本地化
        for locale in ['zh_CN', 'zh', 'zh_TW']:
            localized_key = f"{key}[{locale}]"
            if localized_key in entry:
                return entry[localized_key]
        
        # 返回默认值
        return entry.get(key, default)
    
    def _clean_exec_command(self, exec_cmd):
        """清理Exec命令，移除desktop文件参数"""
        # 移除常见的desktop文件参数
        replacements = [
            '%f', '%F', '%u', '%U', '%d', '%D', '%n', '%N', '%i', '%c', '%k', '%v', '%m'
        ]
        
        for replacement in replacements:
            exec_cmd = exec_cmd.replace(replacement, '').strip()
        
        return exec_cmd
    
    def get_icon_path(self, icon_name):
        """获取图标路径"""
        if not icon_name:
            return None
        
        # 如果是绝对路径，直接返回
        if Path(icon_name).is_absolute() and Path(icon_name).exists():
            return str(icon_name)
        
        # 常见的图标扩展名，按优先级排序（pygame支持的格式优先）
        extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tga', '.xpm', '.ico', '.svg']
        
        # 如果图标名已经包含扩展名，直接搜索
        if any(icon_name.lower().endswith(ext) for ext in extensions):
            return self._search_icon_file(icon_name)
        
        # 尝试添加不同扩展名搜索，优先PNG
        for ext in extensions:
            icon_file = self._search_icon_file(f"{icon_name}{ext}")
            if icon_file:
                # 如果找到SVG，尝试寻找同名PNG
                if ext == '.svg':
                    png_file = self._search_icon_file(f"{icon_name}.png")
                    if png_file:
                        return png_file
                return icon_file
        
        # 最后尝试模糊搜索
        return self._fuzzy_search_icon(icon_name)
    
    def _search_icon_file(self, filename):
        """在系统图标目录中搜索指定文件名"""
        # 系统图标目录
        icon_paths = [
            Path("/usr/share/icons"),
            Path("/usr/share/pixmaps"),
            Path.home() / ".local/share/icons",
            Path.home() / ".icons",
            Path("/opt/apps"),  # 深度系统应用图标
        ]
        
        for icon_path in icon_paths:
            if not icon_path.exists():
                continue
            
            # 直接查找
            icon_file = icon_path / filename
            if icon_file.exists():
                return str(icon_file)
            
            # 在子目录中递归查找
            for icon_file in icon_path.rglob(filename):
                if icon_file.is_file():
                    return str(icon_file)
        
        return None
    
    def _fuzzy_search_icon(self, icon_name):
        """模糊搜索图标"""
        icon_paths = [
            Path("/usr/share/icons"),
            Path("/usr/share/pixmaps"),
        ]
        
        extensions = ['.png', '.svg', '.xpm', '.ico']
        
        for icon_path in icon_paths:
            if not icon_path.exists():
                continue
            
            # 搜索包含图标名的文件
            for ext in extensions:
                pattern = f"*{icon_name}*{ext}"
                for icon_file in icon_path.rglob(pattern):
                    if icon_file.is_file():
                        return str(icon_file)
                
                # 反向搜索：图标名包含在文件名中
                pattern = f"*{ext}"
                for icon_file in icon_path.rglob(pattern):
                    if icon_file.is_file() and icon_name.lower() in icon_file.stem.lower():
                        return str(icon_file)
        
        return None
    
    def create_desktop_file(self, app_info, target_path):
        """创建desktop文件"""
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={app_info['name']}
Comment={app_info.get('description', '')}
Exec={app_info['exec']}
Icon={app_info.get('icon', '')}
Categories={';'.join(app_info.get('categories', ['Other']))};
Terminal=false
"""
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(desktop_content)
        
        # 设置可执行权限
        os.chmod(target_path, 0o755)
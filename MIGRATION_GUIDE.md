# Flying Desktop 应用管理系统迁移指南

## 变更概述

Flying Desktop 已从基于 `apps.conf` 配置文件的应用管理系统迁移到基于注册表的手动应用管理系统。

## 主要变更

### 🗑️ 已移除

- `apps.conf` 配置文件
- 自动应用搜索功能
- 基于配置文件的应用管理

### ✨ 新增功能

- 手动应用管理系统
- Desktop文件解析和缓存
- AppImage文件支持
- 应用图标显示
- 智能图标搜索
- SVG图标支持

## 迁移步骤

### 1. 清理旧配置

如果你之前使用过 `apps.conf`，现在可以删除它：

```bash
rm apps.conf
rm ~/.config/flying-desktop/apps.conf  # 如果存在
```

### 2. 添加应用

使用新的应用管理工具添加你需要的应用：

```bash
# 添加常用应用
python manage_apps.py add-desktop /usr/share/applications/firefox.desktop
python manage_apps.py add-desktop /usr/share/applications/dde-file-manager.desktop
python manage_apps.py add-desktop /usr/share/applications/deepin-terminal.desktop

# 添加AppImage应用
python manage_apps.py add-appimage ~/Downloads/MyApp.AppImage
```

### 3. 验证应用

检查应用是否正确添加：

```bash
python manage_apps.py list
```

### 4. 启动程序

```bash
python main.py
```

## 新系统优势

### 🎯 精确控制
- 只显示你明确添加的应用
- 避免系统应用混乱
- 更清洁的界面

### 🖼️ 图标支持
- 自动解析应用图标
- 支持多种图标格式
- 智能图标搜索

### 📦 AppImage支持
- 完整的AppImage支持
- 自动提取图标和信息
- 便携应用管理

### 💾 缓存系统
- 高效的应用信息缓存
- 快速启动
- 离线工作

## 故障排除

### 应用不显示

1. 检查注册表：
   ```bash
   python manage_apps.py list
   ```

2. 重新添加应用：
   ```bash
   python manage_apps.py add-desktop /path/to/app.desktop
   ```

### 图标不显示

1. 检查图标路径（程序启动时会显示）
2. 确认图标文件存在
3. 尝试重新添加应用

### 清空重新开始

```bash
python manage_apps.py clear
# 然后重新添加应用
```

## 技术细节

### 注册表格式

应用信息存储在 `~/.cache/flying-desktop/applications/registry.json`：

```json
[
  {
    "name": "Firefox",
    "description": "Browse the World Wide Web",
    "exec": "/usr/lib/firefox/firefox",
    "icon": "firefox",
    "categories": ["Network", "WebBrowser"],
    "desktop_file": "/home/user/.cache/flying-desktop/applications/firefox_hash.desktop",
    "type": "desktop",
    "original_file": "/usr/share/applications/firefox.desktop"
  }
]
```

### 缓存结构

```
~/.cache/flying-desktop/applications/
├── registry.json              # 应用注册表
├── firefox_12345678.desktop   # 缓存的desktop文件
├── myapp_87654321.desktop     # AppImage提取的desktop文件
└── myapp_icon.png             # AppImage提取的图标
```

## 开发者信息

如果你在开发或定制Flying Desktop，新的应用管理API：

```python
from src.app_config import AppConfigLoader

loader = AppConfigLoader()

# 添加应用
success, message = loader.add_desktop_file("/path/to/app.desktop")
success, message = loader.add_appimage_file("/path/to/app.AppImage")

# 移除应用
success, message = loader.remove_application("应用名称")

# 获取应用列表
apps = loader.get_apps()
```
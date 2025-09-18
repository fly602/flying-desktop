# Flying Desktop 应用管理指南

## 概述

Flying Desktop 现在支持手动添加和管理desktop文件和AppImage文件，所有应用都会缓存到用户的 `.cache` 目录下。

## 应用管理工具

使用 `manage_apps.py` 工具来管理应用：

### 添加Desktop文件

```bash
python manage_apps.py add-desktop /path/to/app.desktop
```

示例：
```bash
python manage_apps.py add-desktop /usr/share/applications/firefox.desktop
python manage_apps.py add-desktop /usr/share/applications/dde-file-manager.desktop
python manage_apps.py add-desktop /usr/share/applications/deepin-terminal.desktop
```

### 添加AppImage文件

```bash
python manage_apps.py add-appimage /path/to/app.AppImage
```

示例：
```bash
python manage_apps.py add-appimage ~/Downloads/MyApp.AppImage
```

### 列出所有应用

```bash
python manage_apps.py list
```

### 移除应用

```bash
python manage_apps.py remove "应用名称"
```

### 清空所有应用

```bash
python manage_apps.py clear
```

## 图标支持

- **PNG图标**: 完全支持，推荐格式
- **SVG图标**: 支持，但可能有兼容性问题
- **其他格式**: 支持JPG、BMP、XPM、ICO等pygame支持的格式

### 图标搜索路径

程序会在以下路径搜索图标：
- `/usr/share/icons/`
- `/usr/share/pixmaps/`
- `~/.local/share/icons/`
- `~/.icons/`
- `/opt/apps/` (深度系统)

### 图标优先级

1. PNG格式图标优先
2. 如果找到SVG图标，会尝试寻找同名PNG图标
3. 如果没有图标，显示文字图标

## AppImage支持

### 自动提取

- 自动从AppImage提取desktop文件
- 自动提取图标文件到缓存目录
- 支持直接执行AppImage文件

### 缓存位置

所有缓存文件存储在：
```
~/.cache/flying-desktop/applications/
├── registry.json          # 应用注册表
├── app1_hash.desktop      # 缓存的desktop文件
├── app2_icon.png          # 提取的图标文件
└── ...
```

## 使用流程

1. **添加应用**：
   ```bash
   python manage_apps.py add-desktop /usr/share/applications/firefox.desktop
   ```

2. **验证添加**：
   ```bash
   python manage_apps.py list
   ```

3. **启动Flying Desktop**：
   ```bash
   python main.py
   ```

4. **使用界面**：
   - 左右方向键选择应用
   - 回车键启动应用
   - Tab键打开设置
   - ESC键退出

## 故障排除

### 图标不显示

1. 检查图标路径是否正确：
   ```bash
   python manage_apps.py list
   ```

2. 手动检查图标文件是否存在：
   ```bash
   ls -la /usr/share/icons/hicolor/*/apps/appname.*
   ```

3. 查看程序启动时的图标路径输出

### AppImage无法启动

1. 检查AppImage文件权限：
   ```bash
   chmod +x /path/to/app.AppImage
   ```

2. 手动测试AppImage：
   ```bash
   /path/to/app.AppImage --help
   ```

### 应用启动失败

1. 检查desktop文件中的Exec命令
2. 确认应用程序已安装
3. 查看程序启动时的错误信息

## 高级功能

### 批量添加应用

```bash
# 添加常用应用
for app in firefox dde-file-manager deepin-terminal code; do
    if [ -f "/usr/share/applications/$app.desktop" ]; then
        python manage_apps.py add-desktop "/usr/share/applications/$app.desktop"
    fi
done
```

### 备份和恢复

备份应用配置：
```bash
cp ~/.cache/flying-desktop/applications/registry.json ~/flying-desktop-backup.json
```

恢复应用配置：
```bash
cp ~/flying-desktop-backup.json ~/.cache/flying-desktop/applications/registry.json
```
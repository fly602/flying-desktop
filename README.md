# Flying Desktop

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

一个基于Python和pygame的轻量级桌面环境，支持游戏手柄控制。专为Linux系统设计的快速应用启动器。

## 功能特性

- 🎮 游戏手柄支持
- 🖥️ 全屏显示
- 🎨 自定义背景，支持轮播和渐变过渡
- 🖼️ 应用图标显示支持
- 📱 Desktop文件和AppImage支持
- ⚡ 轻量级设计

## 快速开始

### 添加应用

首次使用需要手动添加应用：

```bash
# 添加系统应用
python manage_apps.py add-desktop /usr/share/applications/firefox.desktop
python manage_apps.py add-desktop /usr/share/applications/dde-file-manager.desktop

# 添加AppImage应用
python manage_apps.py add-appimage ~/Downloads/MyApp.AppImage

# 查看已添加的应用
python manage_apps.py list
```

### 构建和运行

```bash
# 构建二进制
make build

# 运行程序
make run
# 或直接运行
python main.py
```

### 打包

```bash
# 构建DEB包（使用debian目录）
make deb

# 构建AppImage
make appimage

# 清理构建文件
make clean
make clean-deb  # 清理DEB构建文件
```

### 安装

```bash
# DEB包安装
sudo dpkg -i ../flying-desktop_*.deb

# AppImage直接运行
./dist/SimpleDesktop-*.AppImage
```

## 控制方式

- **方向键/左摇杆**: 选择应用
- **回车/A键**: 启动应用
- **ESC/B键**: 退出

## 配置系统

程序支持分层配置加载，按以下优先级顺序：

1. **用户配置** (最高优先级): `~/.config/flying-desktop/config.json`
2. **当前目录配置**: `./config.json`
3. **系统配置**: `/usr/share/flying-desktop/config.json` 或 `/opt/simple_desktop/config.json`

### 配置文件

- 首次运行时会自动在用户目录创建配置文件
- 可以只覆盖需要修改的部分，其他部分会使用默认值
- 参考 `config.user.example.json` 查看用户配置示例

### 自定义配置

```bash
# 方法1: 使用Makefile安装示例配置
make install-user-config

# 方法2: 手动创建用户配置
mkdir -p ~/.config/flying-desktop
cp config.user.example.json ~/.config/flying-desktop/config.json
nano ~/.config/flying-desktop/config.json
```

### 配置文件说明

- **desktop**: 桌面设置
  - `title`: 桌面标题
  - `fullscreen`: 是否全屏显示
  - `background_image`: 默认背景图片
  - `background_images`: 背景轮播列表
  - `background_duration`: 每个背景显示时长(毫秒)
  - `transition_duration`: 背景切换过渡时长(毫秒)
- **apps**: 应用列表（名称、命令、图标等）
- **controls**: 控制设置（输入延迟、手柄死区等）

用户配置会与系统默认配置合并，只需要定义要修改的部分。

### 背景轮播功能

- 支持多背景自动轮播
- 缓入缓出的渐变过渡效果
- 可配置显示时长和过渡时长
- 如果只有一张背景图片，则不会轮播

## 中文字体支持

程序内置智能中文字体检测，会自动加载系统中可用的中文字体。

### 自动字体检测
程序会按优先级尝试加载以下字体：
- 文泉驿正黑 (WenQuanYi Zen Hei)
- 文泉驿微米黑 (WenQuanYi Micro Hei)  
- Noto Sans CJK SC
- 思源黑体 (Source Han Sans SC)

### 安装中文字体
如果遇到中文乱码问题，可以运行字体安装脚本：

```bash
chmod +x install_fonts.sh
./install_fonts.sh
```

或手动安装：
```bash
# Ubuntu/Debian
sudo apt install fonts-wqy-zenhei fonts-wqy-microhei fonts-noto-cjk

# CentOS/RHEL  
sudo yum install wqy-zenhei-fonts wqy-microhei-fonts google-noto-cjk-fonts

# Fedora
sudo dnf install wqy-zenhei-fonts wqy-microhei-fonts google-noto-cjk-fonts

# Arch Linux
sudo pacman -S wqy-zenhei wqy-microhei noto-fonts-cjk
```

### 自定义字体
在配置文件中指定特定字体：
```json
{
    "desktop": {
        "font_path": "/path/to/your/chinese/font.ttf"
    }
}
```

详细的字体问题解决方案请参考 [FONT_TROUBLESHOOTING.md](FONT_TROUBLESHOOTING.md)

## 应用管理

Flying Desktop 使用手动应用管理系统，支持Desktop文件和AppImage文件。

### 应用管理命令

```bash
# 添加Desktop文件
python manage_apps.py add-desktop /path/to/app.desktop

# 添加AppImage文件  
python manage_apps.py add-appimage /path/to/app.AppImage

# 列出所有应用
python manage_apps.py list

# 移除应用
python manage_apps.py remove "应用名称"

# 清空所有应用
python manage_apps.py clear
```

### 图标支持

- **PNG图标**: 完全支持，推荐格式
- **SVG图标**: 支持，自动转换为PNG
- **其他格式**: 支持JPG、BMP、XPM、ICO等

### 缓存位置

所有应用信息和图标缓存在：
```
~/.cache/flying-desktop/applications/
├── registry.json          # 应用注册表
├── app_hash.desktop       # 缓存的desktop文件
└── app_icon.png           # 提取的图标文件
```

详细的应用管理指南请参考 [APP_MANAGEMENT.md](APP_MANAGEMENT.md)

## 系统要求

### 构建环境
- Python 3.6+
- python3-venv, python3-pip
- debhelper (用于DEB包构建)

### 运行环境
- Linux系统 (任何发行版)
- X11显示服务器 (推荐)
- 中文字体 (用于正确显示中文界面)
- 音频系统 (可选，用于应用音频)

详细依赖分析请参考 [DEPENDENCIES.md](DEPENDENCIES.md)

## 目录结构

```
flying_desktop/
├── src/                     # 源代码目录
│   ├── __init__.py         # 包初始化
│   ├── config.py           # 配置管理模块
│   ├── input_handler.py    # 输入处理模块
│   ├── renderer.py         # 渲染模块
│   ├── app_launcher.py     # 应用启动模块
│   └── desktop.py          # 主桌面类
├── assets/                 # 资源文件目录
│   └── backgrounds/        # 背景图片
│       ├── default.png     # 默认背景
│       ├── cosmic_waves.png # 宇宙波浪
│       ├── space_nebula.png # 太空星云
│       ├── digital_grid.png # 数字网格
│       └── abstract_flow.png # 抽象流动
├── main.py                 # 程序入口
├── config.json             # 系统默认配置
├── config.user.example.json # 用户配置示例
├── requirements.txt        # Python依赖
├── Makefile               # 构建脚本
├── build_appimage.sh      # AppImage打包脚本
├── debian/                # Debian打包配置
│   ├── control           # 包信息和依赖
│   ├── rules             # 构建规则
│   ├── changelog         # 变更日志
│   ├── copyright         # 版权信息
│   ├── postinst          # 安装后脚本
│   └── prerm             # 卸载前脚本
└── README.md             # 说明文档
```

## Debian打包

项目使用标准的Debian打包方式，通过`debian/`目录控制构建过程：

- `debian/control`: 定义包信息、依赖关系
- `debian/rules`: 定义构建和安装规则
- `debian/changelog`: 版本变更记录
- `debian/postinst`: 安装后执行的脚本
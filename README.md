# Flying Desktop

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

一个基于Python和pygame的轻量级桌面环境，支持游戏手柄控制。专为Linux系统设计的快速应用启动器。

## 功能特性

- 🎮 游戏手柄支持
- 🖥️ 全屏显示
- 🎨 自定义背景
- ⚡ 轻量级设计

## 快速开始

### 构建和运行

```bash
# 构建二进制
make build

# 运行程序
make run
# 或直接运行
./dist/simple-desktop
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

- **desktop**: 桌面设置（标题、全屏、背景等）
- **apps**: 应用列表（名称、命令、图标等）
- **controls**: 控制设置（输入延迟、手柄死区等）

用户配置会与系统默认配置合并，只需要定义要修改的部分。

## 系统要求

### 构建环境
- Python 3.6+
- python3-venv, python3-pip
- debhelper (用于DEB包构建)

### 运行环境
- Linux系统 (任何发行版)
- X11显示服务器 (推荐)
- 音频系统 (可选，用于应用音频)

详细依赖分析请参考 [DEPENDENCIES.md](DEPENDENCIES.md)

## 目录结构

```
flying_desktop/
├── simple_desktop.py           # 主程序
├── config.json                # 系统默认配置
├── config.user.example.json   # 用户配置示例
├── requirements.txt           # Python依赖
├── Makefile                  # 构建脚本
├── build_appimage.sh         # AppImage打包脚本
├── debian/                   # Debian打包配置
│   ├── control              # 包信息和依赖
│   ├── rules                # 构建规则
│   ├── changelog            # 变更日志
│   ├── copyright            # 版权信息
│   ├── postinst             # 安装后脚本
│   └── prerm                # 卸载前脚本
└── README.md                # 说明文档
```

## Debian打包

项目使用标准的Debian打包方式，通过`debian/`目录控制构建过程：

- `debian/control`: 定义包信息、依赖关系
- `debian/rules`: 定义构建和安装规则
- `debian/changelog`: 版本变更记录
- `debian/postinst`: 安装后执行的脚本
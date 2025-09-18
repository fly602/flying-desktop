# 依赖分析文档

## 构建依赖 (Build-Depends)

| 包名 | 版本要求 | 用途 | 必需性 |
|------|----------|------|--------|
| debhelper-compat | = 13 | Debian打包工具 | 必需 |
| python3 | >= 3.6 | Python解释器 | 必需 |
| python3-venv | - | 创建虚拟环境 | 必需 |
| python3-pip | - | 安装Python包 | 必需 |

### 构建过程说明

1. 使用`python3-venv`创建隔离的虚拟环境
2. 使用`python3-pip`安装PyInstaller和pygame
3. PyInstaller自动打包所有Python依赖到单一二进制文件
4. 不需要安装系统级的pygame或其他Python库

## 运行时依赖

### 强制依赖 (Depends)

| 包名 | 版本要求 | 用途 | 检测方式 |
|------|----------|------|----------|
| libc6 | >= 2.14 | C标准库 | 自动检测 |
| zlib1g | >= 1:1.1.4 | 压缩库 | 自动检测 |

### 推荐依赖 (Recommends)

| 包名 | 用途 | 说明 |
|------|------|------|
| xorg | X11显示服务器 | 图形界面必需 |
| pulseaudio | 音频系统 | 应用音频支持 |

### 建议依赖 (Suggests)

| 包名 | 用途 | 说明 |
|------|------|------|
| joystick | 手柄支持工具 | 手柄设备管理 |
| jstest-gtk | 手柄测试工具 | 手柄配置和测试 |

## PyInstaller打包优势

1. **最小运行时依赖**: 只需要基本系统库
2. **无Python环境要求**: 目标系统不需要安装Python
3. **自包含**: 所有Python库都打包在二进制中
4. **跨发行版兼容**: 减少了发行版特定的依赖问题

## 依赖验证

```bash
# 检查DEB包依赖
dpkg -I simple-desktop_*.deb

# 检查二进制文件依赖
ldd /opt/simple_desktop/simple-desktop

# 验证运行时依赖
apt-cache depends simple-desktop
```

## 故障排除

### 构建时问题

1. **缺少python3-venv**: `sudo apt install python3-venv`
2. **缺少python3-pip**: `sudo apt install python3-pip`
3. **网络问题**: PyInstaller需要下载包，确保网络连接

### 运行时问题

1. **图形界面问题**: 确保安装了xorg
2. **音频问题**: 确保安装了pulseaudio
3. **手柄问题**: 安装joystick和jstest-gtk包
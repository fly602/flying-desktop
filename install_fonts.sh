#!/bin/bash
# 中文字体安装脚本

echo "Flying Desktop 中文字体安装脚本"
echo "================================"

# 检测系统类型
if command -v apt-get >/dev/null 2>&1; then
    # Debian/Ubuntu 系统
    echo "检测到 Debian/Ubuntu 系统"
    echo "安装中文字体包..."
    
    sudo apt-get update
    sudo apt-get install -y \
        fonts-wqy-zenhei \
        fonts-wqy-microhei \
        fonts-arphic-uming \
        fonts-arphic-ukai \
        fonts-noto-cjk \
        fonts-liberation
    
elif command -v yum >/dev/null 2>&1; then
    # CentOS/RHEL 系统
    echo "检测到 CentOS/RHEL 系统"
    echo "安装中文字体包..."
    
    sudo yum install -y \
        wqy-zenhei-fonts \
        wqy-microhei-fonts \
        google-noto-cjk-fonts \
        liberation-fonts
    
elif command -v dnf >/dev/null 2>&1; then
    # Fedora 系统
    echo "检测到 Fedora 系统"
    echo "安装中文字体包..."
    
    sudo dnf install -y \
        wqy-zenhei-fonts \
        wqy-microhei-fonts \
        google-noto-cjk-fonts \
        liberation-fonts
    
elif command -v pacman >/dev/null 2>&1; then
    # Arch Linux 系统
    echo "检测到 Arch Linux 系统"
    echo "安装中文字体包..."
    
    sudo pacman -S --noconfirm \
        wqy-zenhei \
        wqy-microhei \
        noto-fonts-cjk \
        ttf-liberation
    
else
    echo "未识别的系统类型，请手动安装中文字体"
    echo "推荐字体："
    echo "- WenQuanYi Zen Hei (文泉驿正黑)"
    echo "- WenQuanYi Micro Hei (文泉驿微米黑)"
    echo "- Noto Sans CJK"
    echo "- Liberation Sans"
    exit 1
fi

echo ""
echo "字体安装完成！"
echo "重新启动 Flying Desktop 应该能正确显示中文了。"
echo ""
echo "如果仍有问题，可以在 config.json 中设置 font_path 指定字体文件："
echo '  "font_path": "/path/to/your/chinese/font.ttf"'
#!/bin/bash
set -e

APP_NAME="FlyingDesktop"
VERSION=${VERSION:-"1.0.0"}
ARCH=$(uname -m)

echo "构建AppImage: $APP_NAME $VERSION"

# 创建AppDir结构
APPDIR="build/${APP_NAME}.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"

# 复制程序文件
cp dist/flying-desktop "$APPDIR/usr/bin/"
cp config.json "$APPDIR/usr/bin/"
chmod +x "$APPDIR/usr/bin/simple-desktop"

# 创建AppRun
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
cd "$HERE/usr/bin"
exec ./flying-desktop "$@"
EOF
chmod +x "$APPDIR/AppRun"

# 创建desktop文件
cat > "$APPDIR/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Flying Desktop
Exec=flying-desktop
Icon=flying-desktop
Terminal=false
Categories=Utility;
EOF

# 创建简单图标
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" | base64 -d > "$APPDIR/flying-desktop.png"

# 下载appimagetool
TOOLS_DIR="tools"
mkdir -p "$TOOLS_DIR"
APPIMAGETOOL="$TOOLS_DIR/appimagetool"

if [ ! -x "$APPIMAGETOOL" ]; then
    echo "下载appimagetool..."
    curl -L "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-$(uname -m).AppImage" -o "$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
fi

# 生成AppImage
OUT="dist/${APP_NAME}-${VERSION}-${ARCH}.AppImage"
mkdir -p dist
ARCH=$ARCH "$APPIMAGETOOL" "$APPDIR" "$OUT" 2>/dev/null || {
    # 如果直接运行失败，尝试解包运行
    "$APPIMAGETOOL" --appimage-extract >/dev/null 2>&1
    ARCH=$ARCH squashfs-root/AppRun "$APPDIR" "$OUT"
}

chmod +x "$OUT"
echo "AppImage构建完成: $OUT"
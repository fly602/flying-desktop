# Flying Desktop - 简化版 Makefile
PYTHON ?= python3
VERSION ?= 1.0.0

.PHONY: build run deb appimage clean

# 构建二进制
build:
	@echo "构建二进制文件..."
	$(PYTHON) -m venv .venv || true
	.venv/bin/pip install -U pip pyinstaller pygame
	.venv/bin/pyinstaller --name flying-desktop --onefile --clean --noconfirm simple_desktop.py
	@echo "构建完成: dist/flying-desktop"

# 运行程序
run: build
	./dist/flying-desktop

# 构建DEB包
deb:
	@echo "构建DEB包..."
	dpkg-buildpackage -us -uc -b

# 构建AppImage
appimage: build
	@echo "构建AppImage..."
	VERSION=$(VERSION) bash build_appimage.sh

# 清理
clean:
	rm -rf build dist .venv *.spec __pycache__
	dh_clean || true

# 清理DEB构建文件
clean-deb:
	rm -rf debian/flying-desktop debian/.debhelper debian/files debian/debhelper-build-stamp
	rm -f ../flying-desktop_*.deb ../flying-desktop_*.buildinfo ../flying-desktop_*.changes

# 安装用户配置示例
install-user-config:
	@echo "安装用户配置示例..."
	mkdir -p ~/.config/flying-desktop
	cp config.user.example.json ~/.config/flying-desktop/config.json
	@echo "用户配置已安装到: ~/.config/flying-desktop/config.json"
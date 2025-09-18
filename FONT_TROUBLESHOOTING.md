# Flying Desktop 中文字体问题解决方案

## 问题描述
Flying Desktop 界面中文显示为乱码或方块。

## 解决方案

### 1. 自动字体检测和加载
程序已经内置了智能字体检测功能，会自动尝试加载以下中文字体：

**字体文件路径（按优先级）：**
- `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc` (文泉驿正黑)
- `/usr/share/fonts/truetype/wqy/wqy-microhei.ttc` (文泉驿微米黑)
- `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc` (Noto Sans CJK)
- `/usr/share/fonts/opentype/source-han-cjk/SourceHanSansSC-Regular.otf` (思源黑体)

**系统字体名称：**
- WenQuanYi Zen Hei
- WenQuanYi Micro Hei
- Noto Sans CJK SC
- Source Han Sans SC

### 2. 检查系统中文字体
运行以下命令检查系统中可用的中文字体：

```bash
fc-list :lang=zh
```

### 3. 安装中文字体
如果系统缺少中文字体，可以运行安装脚本：

```bash
chmod +x install_fonts.sh
./install_fonts.sh
```

或者手动安装：

**Ubuntu/Debian:**
```bash
sudo apt install fonts-wqy-zenhei fonts-wqy-microhei fonts-noto-cjk
```

**CentOS/RHEL:**
```bash
sudo yum install wqy-zenhei-fonts wqy-microhei-fonts google-noto-cjk-fonts
```

**Fedora:**
```bash
sudo dnf install wqy-zenhei-fonts wqy-microhei-fonts google-noto-cjk-fonts
```

**Arch Linux:**
```bash
sudo pacman -S wqy-zenhei wqy-microhei noto-fonts-cjk
```

### 4. 自定义字体配置
在配置文件中指定特定的字体文件：

```json
{
    "desktop": {
        "font_path": "/path/to/your/chinese/font.ttf"
    }
}
```

### 5. 测试字体加载
运行字体测试脚本：

```bash
python3 test_font.py
```

### 6. 调试信息
程序启动时会在控制台输出字体加载信息：
- `成功加载中文字体文件: /path/to/font` - 字体加载成功
- `成功加载系统字体: FontName` - 系统字体加载成功
- `警告: 使用pygame默认字体，可能不支持中文显示` - 需要安装中文字体

## 常见问题

### Q: 程序启动正常但中文仍显示为方块
A: 检查控制台输出的字体加载信息，如果显示"使用pygame默认字体"，说明需要安装中文字体。

### Q: 已安装中文字体但仍然乱码
A: 尝试在配置文件中手动指定字体路径，或者重启系统让字体缓存生效。

### Q: 不同Linux发行版字体路径不同
A: 程序会自动搜索常见的字体路径，如果仍有问题，可以使用`fc-list :lang=zh`找到字体路径并在配置中指定。

## 验证解决方案
1. 运行 `python3 test_font.py` 确认字体加载正常
2. 启动程序查看控制台输出的字体加载信息
3. 检查界面中文显示是否正常

如果问题仍然存在，请提供：
- 系统信息 (`uname -a`)
- 字体列表 (`fc-list :lang=zh`)
- 程序启动时的控制台输出
# Flying Desktop 字体管理指南

## 动态字体检测

Flying Desktop 现在支持动态检测系统中可用的中文字体，并在设置页面中显示。

### 字体检测过程

程序启动时会自动：

1. **检测预定义字体**：
   - 文泉驿正黑 (WenQuanYi Zen Hei)
   - 文泉驿微米黑 (WenQuanYi Micro Hei)
   - Noto Sans CJK
   - 思源黑体 (Source Han Sans)
   - Droid Sans Fallback
   - Unifont

2. **使用fontconfig查找**：
   - 自动发现系统中其他中文字体
   - 过滤不适合的字体类型
   - 按优先级排序

3. **字体渲染测试**：
   - 测试每个字体是否能正确渲染中文
   - 缓存测试结果提高性能

### 字体选择

在设置页面的字体选项中，你会看到：

- **自动选择**：让系统选择最佳字体（推荐）
- **系统检测到的字体**：按优先级排序显示
- **动态发现的字体**：fontconfig找到的其他字体

### 字体优先级

1. **自动选择** - 系统智能选择
2. **文泉驿正黑** - 最常用的中文字体
3. **文泉驿微米黑** - 轻量级中文字体
4. **Noto Sans CJK** - Google开源字体
5. **思源黑体** - Adobe开源字体
6. **其他系统字体** - 按发现顺序排列

## 字体配置

### 自动配置

选择字体后，程序会自动：
- 保存字体路径到配置文件
- 重新加载渲染器字体
- 立即生效，无需重启

### 手动配置

你也可以手动编辑配置文件：

```json
{
  "desktop": {
    "font_path": "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
  }
}
```

### 配置文件位置

- 用户配置：`~/.config/flying-desktop/config.json`
- 系统配置：`config.json`

## 字体安装

### 安装新字体

如果需要安装新的中文字体：

```bash
# Ubuntu/Debian
sudo apt install fonts-wqy-zenhei fonts-wqy-microhei fonts-noto-cjk

# 手动安装字体文件
sudo cp font.ttf /usr/share/fonts/truetype/
sudo fc-cache -fv
```

### 重新检测字体

安装新字体后：
1. 重启Flying Desktop
2. 新字体会自动出现在设置列表中

## 故障排除

### 字体不显示

1. **检查字体文件**：
   ```bash
   ls -la /usr/share/fonts/truetype/wqy/
   ```

2. **检查fontconfig**：
   ```bash
   fc-list :lang=zh
   ```

3. **重建字体缓存**：
   ```bash
   sudo fc-cache -fv
   ```

### 字体渲染异常

1. **使用自动选择**：最安全的选项
2. **检查字体文件完整性**
3. **尝试其他字体选项**

### 性能问题

字体检测可能需要几秒时间，这是正常的：
- 首次启动会检测所有字体
- 后续启动会使用缓存结果
- 检测结果会显示在控制台

## 开发者信息

### FontDetector API

```python
from src.font_detector import FontDetector

detector = FontDetector()

# 检测系统字体
fonts = detector.detect_system_fonts()

# 获取字体选项
options = detector.get_font_options()

# 获取字体名称映射
names = detector.get_font_names()

# 获取字体路径
path = detector.get_font_path('wqy_zenhei')
```

### 字体信息结构

```python
{
    'key': 'wqy_zenhei',           # 字体键
    'name': '文泉驿正黑',           # 显示名称
    'path': '/usr/share/fonts/...',  # 字体文件路径
    'priority': 1                   # 优先级
}
```

### 扩展字体支持

要添加新的预定义字体，编辑 `src/font_detector.py` 中的 `known_fonts` 列表。

## 最佳实践

1. **推荐使用自动选择**：适合大多数用户
2. **文泉驿字体**：Linux系统最常见的中文字体
3. **Noto字体**：现代化设计，支持多语言
4. **定期更新字体**：保持系统字体库最新

## 技术细节

- 字体检测使用fontconfig和pygame
- 支持TTF、TTC、OTF格式
- 自动过滤不适合的字体类型
- 缓存机制提高性能
- 实时渲染测试确保兼容性
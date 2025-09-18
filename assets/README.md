# Assets 资源目录

这个目录包含Flying Desktop的所有资源文件。

## 目录结构

```
assets/
├── backgrounds/           # 背景图片
│   ├── default.png       # 默认背景
│   ├── cosmic_waves.png  # 宇宙波浪
│   ├── space_nebula.png  # 太空星云
│   ├── digital_grid.png  # 数字网格
│   └── abstract_flow.png # 抽象流动
└── README.md             # 本说明文件
```

## 背景图片

- **default.png**: 默认背景图片，当背景列表为空时使用
- **cosmic_waves.png**: 宇宙波浪主题背景
- **space_nebula.png**: 太空星云主题背景  
- **digital_grid.png**: 数字网格主题背景
- **abstract_flow.png**: 抽象流动主题背景

## 背景轮播功能

Flying Desktop支持背景自动轮播，具有以下特性：

- **自动轮播**: 按配置的时间间隔自动切换背景
- **渐变过渡**: 使用缓入缓出的渐变效果平滑切换
- **可配置时长**: 可以设置每个背景的显示时间和过渡时间
- **智能回退**: 如果只有一张背景或加载失败，会自动使用渐变背景

## 自定义背景

你可以添加自己的背景图片到这个目录，然后在配置文件中引用：

```json
{
    "desktop": {
        "background_image": "assets/backgrounds/my_background.png",
        "background_images": [
            "assets/backgrounds/my_background1.png",
            "assets/backgrounds/my_background2.png"
        ],
        "background_duration": 8000,
        "transition_duration": 1500
    }
}
```

配置说明：
- `background_duration`: 每个背景显示的时长（毫秒）
- `transition_duration`: 背景切换的过渡时长（毫秒）

## 图片要求

- 支持格式: PNG, JPG, JPEG
- 推荐分辨率: 1920x1080 或更高
- 文件大小: 建议小于5MB以确保快速加载
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文字体检查脚本
快速检查系统是否支持中文显示
"""

import subprocess
import sys
from pathlib import Path

def check_system_fonts():
    """检查系统中文字体"""
    print("检查系统中文字体...")
    
    try:
        result = subprocess.run(['fc-list', ':lang=zh'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            fonts = result.stdout.strip().split('\n')
            print(f"✓ 找到 {len(fonts)} 个中文字体")
            
            # 显示前几个字体
            print("主要中文字体:")
            for font in fonts[:5]:
                font_name = font.split(':')[1].split(',')[0] if ':' in font else font
                print(f"  - {font_name}")
            
            if len(fonts) > 5:
                print(f"  ... 还有 {len(fonts) - 5} 个字体")
            
            return True
        else:
            print("✗ 未找到中文字体")
            return False
    except FileNotFoundError:
        print("✗ fontconfig 未安装，无法检查字体")
        return False

def check_pygame_fonts():
    """检查pygame字体支持"""
    print("\n检查pygame字体支持...")
    
    try:
        import pygame
        pygame.init()
        
        # 测试字体路径
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
        
        loaded_fonts = 0
        for font_path in font_paths:
            if Path(font_path).exists():
                try:
                    font = pygame.font.Font(font_path, 24)
                    # 测试中文渲染
                    surface = font.render("测试中文", True, (255, 255, 255))
                    print(f"✓ {Path(font_path).name}")
                    loaded_fonts += 1
                except Exception as e:
                    print(f"✗ {Path(font_path).name}: {e}")
        
        # 测试系统字体
        system_fonts = ["WenQuanYi Zen Hei", "Noto Sans CJK SC"]
        for font_name in system_fonts:
            try:
                font = pygame.font.SysFont(font_name, 24)
                surface = font.render("测试中文", True, (255, 255, 255))
                print(f"✓ {font_name}")
                loaded_fonts += 1
            except Exception as e:
                print(f"✗ {font_name}: {e}")
        
        pygame.quit()
        
        if loaded_fonts > 0:
            print(f"✓ pygame可以加载 {loaded_fonts} 个中文字体")
            return True
        else:
            print("✗ pygame无法加载任何中文字体")
            return False
            
    except ImportError:
        print("✗ pygame 未安装")
        return False

def main():
    """主函数"""
    print("Flying Desktop 中文字体检查")
    print("=" * 30)
    
    system_ok = check_system_fonts()
    pygame_ok = check_pygame_fonts()
    
    print("\n" + "=" * 30)
    
    if system_ok and pygame_ok:
        print("🎉 中文字体支持正常！")
        print("Flying Desktop 应该能正确显示中文界面。")
        return 0
    elif system_ok and not pygame_ok:
        print("⚠️  系统有中文字体，但pygame无法加载。")
        print("请检查pygame安装或尝试安装其他中文字体。")
        return 1
    else:
        print("❌ 缺少中文字体支持。")
        print("请运行 ./install_fonts.sh 安装中文字体。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
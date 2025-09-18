#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flying Desktop 主入口文件
"""

import sys
from src.desktop import FlyingDesktop


def main():
    """主函数"""
    try:
        desktop = FlyingDesktop()
        desktop.run()
    except Exception as e:
        print(f"桌面启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
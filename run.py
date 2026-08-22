#!/usr/bin/env python
"""
BOSS直聘数据采集系统 - 启动脚本

便捷入口，无需输入完整模块路径。
使用方式：
  python run.py serve
  python run.py setup
  python run.py check
  python run.py crawl --keyword "AI Agent" --city 上海 --pages 3
  python run.py cities
"""

import sys
import os

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == "__main__":
    main()

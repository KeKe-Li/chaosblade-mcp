"""
ChaosBlade YAML Generator - 重构后的主入口
混沌工程YAML配置生成工具
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chaosblade.cli import main

if __name__ == "__main__":
    main()
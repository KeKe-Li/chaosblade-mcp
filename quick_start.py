#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChaosBlade MCP 支持跨平台一键启动
"""

import os
import sys
import subprocess
import platform
import socket
from pathlib import Path

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

def print_colored(message, color=Colors.WHITE):
    """打印带颜色的消息"""
    if platform.system() == "Windows":
        print(message)  # Windows下不使用颜色
    else:
        print(f"{color}{message}{Colors.NC}")

def print_title():
    """打印标题"""
    print()
    print_colored("=" * 45, Colors.CYAN)
    print_colored("   🚀 ChaosBlade MCP 快速启动工具", Colors.CYAN)
    print_colored("=" * 45, Colors.CYAN)
    print()

def check_python():
    """检查Python环境"""
    print_colored("🐍 检查Python环境...", Colors.BLUE)
    
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print_colored("❌ 需要Python 3.8+，当前版本: {}.{}.{}".format(
            python_version.major, python_version.minor, python_version.micro), Colors.RED)
        return False
    
    print_colored(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}", Colors.GREEN)
    return True

def setup_venv():
    """设置虚拟环境"""
    print_colored("🔧 设置虚拟环境...", Colors.BLUE)
    
    project_dir = Path(__file__).parent
    venv_dir = project_dir / ".venv"
    
    if not venv_dir.exists():
        print_colored("创建虚拟环境...", Colors.YELLOW)
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    
    # 获取虚拟环境中的Python路径
    if platform.system() == "Windows":
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"
    
    print_colored("✅ 虚拟环境准备完成", Colors.GREEN)
    return python_exe, pip_exe

def install_dependencies(pip_exe):
    """安装依赖"""
    print_colored("📦 安装依赖包...", Colors.BLUE)
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print_colored("❌ requirements.txt 文件不存在", Colors.RED)
        return False
    
    try:
        subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], 
                      check=True, capture_output=True, text=True)
        print_colored("✅ 依赖包安装完成", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ 依赖安装失败: {e}", Colors.RED)
        return False

def find_available_port(start_port=5001):
    """查找可用端口"""
    for port in range(start_port, start_port + 10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return start_port

def start_web_app(python_exe):
    """启动Web应用"""
    print_colored("🌐 启动Web服务...", Colors.BLUE)
    
    port = find_available_port()
    
    print_colored("🚀 ChaosBlade Web Interface 启动中...", Colors.GREEN)
    print_colored(f"📱 访问地址: http://localhost:{port}", Colors.CYAN)
    print_colored("💡 按 Ctrl+C 停止服务", Colors.YELLOW)
    print()
    
    try:
        # 启动Web应用
        subprocess.run([str(python_exe), "web_app.py", str(port)], check=True)
    except KeyboardInterrupt:
        print_colored("\n🛑 服务已停止", Colors.YELLOW)
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ 启动失败: {e}", Colors.RED)

def start_cli_mode(python_exe):
    """启动CLI模式"""
    print_colored("🖥️  启动命令行模式...", Colors.BLUE)
    print_colored("输入指令进行交互，输入 'quit' 退出", Colors.CYAN)
    print()
    
    try:
        subprocess.run([str(python_exe), "chat.py", "--interactive"], check=True)
    except KeyboardInterrupt:
        print_colored("\n🛑 CLI模式已退出", Colors.YELLOW)
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ CLI启动失败: {e}", Colors.RED)

def show_help():
    """显示帮助信息"""
    print()
    print_colored("用法: python quick_start.py [选项]", Colors.CYAN)
    print()
    print_colored("选项:", Colors.YELLOW)
    print("  -h, --help     显示此帮助信息")
    print("  --cli          启动命令行模式")
    print("  --web          启动Web服务（默认）")
    print("  --check        只检查环境")
    print()
    print_colored("示例:", Colors.YELLOW)
    print("  python quick_start.py        # 启动Web服务")
    print("  python quick_start.py --cli  # 启动CLI模式")
    print("  python quick_start.py --check # 检查环境")
    print()

def main():
    """主函数"""
    print_title()
    
    # 处理命令行参数
    args = sys.argv[1:]
    
    if "-h" in args or "--help" in args:
        show_help()
        return
    
    # 检查Python环境
    if not check_python():
        return
    
    # 设置虚拟环境
    try:
        python_exe, pip_exe = setup_venv()
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ 虚拟环境设置失败: {e}", Colors.RED)
        return
    
    # 安装依赖
    if not install_dependencies(pip_exe):
        return
    
    # 检查模式
    if "--check" in args:
        print_colored("✅ 环境检查完成！", Colors.GREEN)
        return
    
    # 切换到项目目录
    os.chdir(Path(__file__).parent)
    
    # 启动模式选择
    if "--cli" in args:
        start_cli_mode(python_exe)
    else:
        start_web_app(python_exe)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n👋 再见！", Colors.GREEN)
    except Exception as e:
        print_colored(f"❌ 发生错误: {e}", Colors.RED)
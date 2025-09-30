#!/bin/bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="ChaosBlade MCP"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_FILE="$PROJECT_DIR/startup.log"

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 打印标题
print_title() {
    echo ""
    print_message $CYAN "========================================="
    print_message $CYAN "   🚀 $PROJECT_NAME 一键启动工具"
    print_message $CYAN "========================================="
    echo ""
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_message $RED "❌ $1 未安装，请先安装 $1"
        return 1
    else
        print_message $GREEN "✅ $1 已安装"
        return 0
    fi
}

# 检查系统依赖
check_dependencies() {
    print_message $BLUE "🔍 检查系统依赖..."
    
    local all_good=true
    
    if ! check_command "python3"; then
        all_good=false
    fi
    
    if ! check_command "pip3"; then
        all_good=false
    fi
    
    if [ "$all_good" = false ]; then
        print_message $RED "❌ 系统依赖检查失败，请先安装必需的软件"
        exit 1
    fi
    
    print_message $GREEN "✅ 系统依赖检查通过"
    echo ""
}

# 创建虚拟环境
setup_venv() {
    print_message $BLUE "🐍 设置Python虚拟环境..."
    
    if [ ! -d "$VENV_DIR" ]; then
        print_message $YELLOW "创建虚拟环境: $VENV_DIR"
        python3 -m venv "$VENV_DIR"
    else
        print_message $GREEN "✅ 虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"
    print_message $GREEN "✅ 虚拟环境已激活"
    echo ""
}

# 安装依赖
install_dependencies() {
    print_message $BLUE "📦 安装Python依赖包..."
    
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        pip3 install -r "$PROJECT_DIR/requirements.txt" >> "$LOG_FILE" 2>&1
        print_message $GREEN "✅ 依赖包安装完成"
    else
        print_message $RED "❌ 未找到 requirements.txt 文件"
        exit 1
    fi
    echo ""
}

# 检查配置文件
check_config() {
    print_message $BLUE "⚙️  检查配置文件..."
    
    if [ -f "$PROJECT_DIR/config.py" ]; then
        print_message $GREEN "✅ 配置文件存在"
        
        # 检查是否需要配置LLM
        if grep -q "LLM_API_KEY.*\"\"" "$PROJECT_DIR/config.py"; then
            print_message $YELLOW "⚠️  警告: LLM_API_KEY 为空，可能需要配置"
        fi
    else
        print_message $RED "❌ 配置文件不存在"
        exit 1
    fi
    echo ""
}

# 创建必要目录
create_directories() {
    print_message $BLUE "📁 创建必要目录..."
    
    mkdir -p "$PROJECT_DIR/generated-yamls"
    mkdir -p "$PROJECT_DIR/logs"
    
    print_message $GREEN "✅ 目录创建完成"
    echo ""
}

# 检查端口是否可用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

# 查找可用端口
find_available_port() {
    local start_port=$1
    local port=$start_port
    
    while [ $port -le $(($start_port + 10)) ]; do
        if check_port $port; then
            echo $port
            return
        fi
        port=$((port + 1))
    done
    
    echo $start_port
}

# 启动Web服务
start_web_service() {
    print_message $BLUE "🌐 启动Web服务..."
    
    # 查找可用端口
    local port=$(find_available_port 5001)
    
    print_message $GREEN "🚀 启动 ChaosBlade Web Interface..."
    print_message $CYAN "📱 访问地址: http://localhost:$port"
    print_message $CYAN "📱 本地网络: http://$(ipconfig getifaddr en0 2>/dev/null || echo '127.0.0.1'):$port"
    print_message $YELLOW "💡 按 Ctrl+C 停止服务"
    echo ""
    
    # 启动服务
    cd "$PROJECT_DIR"
    python3 web_app.py $port
}

# 显示使用帮助
show_help() {
    echo ""
    print_message $CYAN "用法: $0 [选项]"
    echo ""
    print_message $YELLOW "选项:"
    print_message $WHITE "  -h, --help     显示此帮助信息"
    print_message $WHITE "  -c, --check    只检查环境，不启动服务"
    print_message $WHITE "  -i, --install  只安装依赖，不启动服务"
    print_message $WHITE "  --cli          启动命令行模式"
    echo ""
    print_message $YELLOW "示例:"
    print_message $WHITE "  $0              # 完整启动流程"
    print_message $WHITE "  $0 --check      # 只检查环境"
    print_message $WHITE "  $0 --cli        # 启动CLI模式"
    echo ""
}

# 启动CLI模式
start_cli_mode() {
    print_message $BLUE "🖥️  启动命令行模式..."
    print_message $CYAN "输入 'python3 chat.py --help' 查看CLI帮助"
    echo ""
    
    cd "$PROJECT_DIR"
    python3 chat.py --interactive
}

# 主函数
main() {
    # 记录启动时间
    echo "启动时间: $(date)" > "$LOG_FILE"
    
    print_title
    
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--check)
            check_dependencies
            setup_venv
            check_config
            print_message $GREEN "✅ 环境检查完成！"
            exit 0
            ;;
        -i|--install)
            check_dependencies
            setup_venv
            install_dependencies
            check_config
            create_directories
            print_message $GREEN "✅ 依赖安装完成！"
            exit 0
            ;;
        --cli)
            check_dependencies
            setup_venv
            install_dependencies
            check_config
            create_directories
            start_cli_mode
            exit 0
            ;;
        "")
            # 完整启动流程
            check_dependencies
            setup_venv
            install_dependencies
            check_config
            create_directories
            start_web_service
            ;;
        *)
            print_message $RED "❌ 未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 信号处理
cleanup() {
    print_message $YELLOW "🛑 正在停止服务..."
    print_message $GREEN "👋 再见！"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 执行主函数
main "$@"
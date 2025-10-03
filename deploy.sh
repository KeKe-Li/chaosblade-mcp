#!/bin/bash

# ChaosBlade Web Interface 一键部署启动脚本
# 一键安装依赖并启动Web界面

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示欢迎信息
show_welcome() {
    echo -e "${BLUE}"
    echo "================================================"
    echo "    ChaosBlade Web Interface 一键部署启动"
    echo "================================================"
    echo -e "${NC}"
}

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."
    
    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装，请先安装Python3"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    log_info "Python版本: $PYTHON_VERSION"
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装，请先安装pip3"
        exit 1
    fi
    
    # 检查git（可选）
    if ! command -v git &> /dev/null; then
        log_warning "git 未安装，某些功能可能受限"
    fi
    
    log_success "系统要求检查完成"
}

# 创建虚拟环境
create_venv() {
    log_info "创建Python虚拟环境..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "虚拟环境创建成功"
    else
        log_info "虚拟环境已存在，跳过创建"
    fi
}

# 激活虚拟环境
activate_venv() {
    log_info "激活虚拟环境..."
    source venv/bin/activate
    log_success "虚拟环境已激活"
}

# 升级pip
upgrade_pip() {
    log_info "升级pip..."
    pip install --upgrade pip
    log_success "pip升级完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        log_success "依赖安装完成"
    else
        log_error "requirements.txt 文件不存在"
        exit 1
    fi
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "端口 $port 已被占用"
        return 1
    else
        log_info "端口 $port 可用"
        return 0
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    mkdir -p templates
    mkdir -p static/css
    mkdir -p static/js
    mkdir -p generated-yamls
    mkdir -p logs
    
    log_success "目录创建完成"
}

# 设置权限
set_permissions() {
    log_info "设置文件权限..."
    
    chmod +x start_web.sh 2>/dev/null || true
    chmod +x test_web_api.py 2>/dev/null || true
    chmod +x deploy.sh 2>/dev/null || true
    
    log_success "权限设置完成"
}

# 创建配置文件
create_config() {
    log_info "创建配置文件..."
    
    cat > config.py << 'EOF'
# ChaosBlade Web Interface Configuration

# Web服务器配置
WEB_HOST = '0.0.0.0'
WEB_PORT = 5001
WEB_DEBUG = True

# API配置
API_BASE_URL = 'http://localhost:5001'
API_TIMEOUT = 30

# 文件配置
GENERATED_DIR = 'generated-yamls'
LOG_DIR = 'logs'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# 安全配置
SECRET_KEY = 'your-secret-key-change-in-production'
CORS_ORIGINS = ['*']

# ChaosBlade配置
CHAOSBLADE_DEFAULT_TIMEOUT = '300s'
CHAOSBLADE_SAFE_MODE = True
EOF

    log_success "配置文件创建完成"
}

# 创建systemd服务文件（可选）
create_systemd_service() {
    log_info "创建systemd服务文件..."
    
    cat > chaosblade-web.service << 'EOF'
[Unit]
Description=ChaosBlade Web Interface
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python web_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    log_info "systemd服务文件已创建: chaosblade-web.service"
    log_info "如需启用系统服务，请运行:"
    log_info "  sudo cp chaosblade-web.service /etc/systemd/system/"
    log_info "  sudo systemctl daemon-reload"
    log_info "  sudo systemctl enable chaosblade-web"
    log_info "  sudo systemctl start chaosblade-web"
}

# 创建启动脚本
create_startup_script() {
    log_info "创建启动脚本..."
    
    cat > quick_start.sh << 'EOF'
#!/bin/bash

# ChaosBlade Web Interface 快速启动脚本

echo "🚀 启动 ChaosBlade Web Interface..."

# 激活虚拟环境
source venv/bin/activate

# 启动Web应用
python web_app.py
EOF

    chmod +x quick_start.sh
    log_success "快速启动脚本创建完成: quick_start.sh"
}

# 运行测试
run_tests() {
    log_info "运行系统测试..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 检查模块导入
    python -c "from chaosblade import quick_generate; print('✅ 模块导入成功')" || {
        log_error "模块导入失败"
        return 1
    }
    
    log_success "系统测试完成"
}

# 启动Web应用
start_web_app() {
    log_info "启动Web应用..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 检查端口
    if ! check_port 5001; then
        log_warning "端口5001被占用，尝试使用端口5002"
        # 修改web_app.py中的端口
        sed -i '' 's/port=5001/port=5002/g' web_app.py 2>/dev/null || sed -i 's/port=5001/port=5002/g' web_app.py
        WEB_PORT=5002
    else
        WEB_PORT=5001
    fi
    
    # 启动应用
    log_info "Web应用启动中..."
    log_info "访问地址: http://localhost:$WEB_PORT"
    log_info "按 Ctrl+C 停止服务"
    
    # 在后台启动应用
    nohup python web_app.py > logs/web_app.log 2>&1 &
    WEB_PID=$!
    
    # 保存PID
    echo $WEB_PID > web_app.pid
    
    # 等待应用启动
    sleep 3
    
    # 检查应用是否正常启动
    if curl -s http://localhost:$WEB_PORT/api/health > /dev/null; then
        log_success "Web应用启动成功！"
        log_info "访问地址: http://localhost:$WEB_PORT"
        log_info "进程ID: $WEB_PID"
        log_info "日志文件: logs/web_app.log"
    else
        log_error "Web应用启动失败"
        log_info "请检查日志: logs/web_app.log"
        exit 1
    fi
}

# 显示使用说明
show_usage() {
    echo -e "${BLUE}"
    echo "================================================"
    echo "                使用说明"
    echo "================================================"
    echo -e "${NC}"
    echo "🎯 访问Web界面:"
    echo "   打开浏览器访问: http://localhost:$WEB_PORT"
    echo ""
    echo "📝 常用命令:"
    echo "   查看状态: curl http://localhost:$WEB_PORT/api/health"
    echo "   查看日志: tail -f logs/web_app.log"
    echo "   停止服务: ./stop.sh"
    echo "   重启服务: ./restart.sh"
    echo ""
    echo "🔧 管理命令:"
    echo "   测试API: python test_web_api.py"
    echo "   快速启动: ./quick_start.sh"
    echo ""
    echo "📚 更多帮助:"
    echo "   查看: WEB_INTERFACE_GUIDE.md"
    echo ""
}

# 创建停止脚本
create_stop_script() {
    log_info "创建停止脚本..."
    
    cat > stop.sh << 'EOF'
#!/bin/bash

# ChaosBlade Web Interface 停止脚本

echo "🛑 停止 ChaosBlade Web Interface..."

# 检查PID文件
if [ -f "web_app.pid" ]; then
    PID=$(cat web_app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "✅ 进程 $PID 已停止"
    else
        echo "⚠️  进程 $PID 不存在"
    fi
    rm -f web_app.pid
else
    # 通过端口查找进程
    PID=$(lsof -ti:5001 2>/dev/null || lsof -ti:5002 2>/dev/null)
    if [ ! -z "$PID" ]; then
        kill $PID
        echo "✅ 进程 $PID 已停止"
    else
        echo "⚠️  未找到运行中的进程"
    fi
fi

echo "🛑 服务已停止"
EOF

    chmod +x stop.sh
    log_success "停止脚本创建完成: stop.sh"
}

# 创建重启脚本
create_restart_script() {
    log_info "创建重启脚本..."
    
    cat > restart.sh << 'EOF'
#!/bin/bash

# ChaosBlade Web Interface 重启脚本

echo "🔄 重启 ChaosBlade Web Interface..."

# 停止服务
./stop.sh

# 等待进程完全停止
sleep 2

# 启动服务
./quick_start.sh
EOF

    chmod +x restart.sh
    log_success "重启脚本创建完成: restart.sh"
}

# 主函数
main() {
    show_welcome
    
    # 检查是否在正确的目录
    if [ ! -f "web_app.py" ]; then
        log_error "请在包含web_app.py的目录中运行此脚本"
        exit 1
    fi
    
    # 执行部署步骤
    check_requirements
    create_venv
    activate_venv
    upgrade_pip
    install_dependencies
    create_directories
    set_permissions
    create_config
    create_startup_script
    create_stop_script
    create_restart_script
    create_systemd_service
    run_tests
    start_web_app
    show_usage
    
    log_success "🎉 部署完成！"
    log_info "Web界面已启动，请访问 http://localhost:$WEB_PORT"
}

# 检查命令行参数
case "${1:-}" in
    "help"|"-h"|"--help")
        echo "用法: $0 [选项]"
        echo "选项:"
        echo "  help, -h, --help    显示此帮助信息"
        echo "  install-only       仅安装依赖，不启动服务"
        echo "  test-only          仅运行测试"
        exit 0
        ;;
    "install-only")
        check_requirements
        create_venv
        activate_venv
        upgrade_pip
        install_dependencies
        create_directories
        set_permissions
        create_config
        log_success "仅安装模式完成"
        exit 0
        ;;
    "test-only")
        activate_venv
        run_tests
        exit 0
        ;;
    *)
        main
        ;;
esac
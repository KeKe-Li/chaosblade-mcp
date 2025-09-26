@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ChaosBlade MCP Windows 一键启动脚本
REM 作者: ChaosBlade Team  
REM 版本: 1.0.0

set "PROJECT_NAME=ChaosBlade MCP"
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%.venv"
set "LOG_FILE=%PROJECT_DIR%startup.log"

REM 颜色代码
set "RED=[31m"
set "GREEN=[32m" 
set "YELLOW=[33m"
set "BLUE=[34m"
set "PURPLE=[35m"
set "CYAN=[36m"
set "NC=[0m"

:print_title
echo.
echo %CYAN%==========================================%NC%
echo %CYAN%   🚀 %PROJECT_NAME% 一键启动工具%NC%
echo %CYAN%==========================================%NC%
echo.
goto :eof

:check_command
where %1 >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%❌ %1 未安装，请先安装 %1%NC%
    exit /b 1
) else (
    echo %GREEN%✅ %1 已安装%NC%
    exit /b 0
)
goto :eof

:check_dependencies
echo %BLUE%🔍 检查系统依赖...%NC%

call :check_command python
if %errorlevel% neq 0 (
    call :check_command python3
    if !errorlevel! neq 0 (
        echo %RED%❌ Python未安装，请先安装Python%NC%
        pause
        exit /b 1
    )
    set "PYTHON_CMD=python3"
) else (
    set "PYTHON_CMD=python"
)

call :check_command pip
if %errorlevel% neq 0 (
    echo %RED%❌ pip未安装，请先安装pip%NC%
    pause
    exit /b 1
)

echo %GREEN%✅ 系统依赖检查通过%NC%
echo.
goto :eof

:setup_venv
echo %BLUE%🐍 设置Python虚拟环境...%NC%

if not exist "%VENV_DIR%" (
    echo %YELLOW%创建虚拟环境: %VENV_DIR%%NC%
    %PYTHON_CMD% -m venv "%VENV_DIR%"
) else (
    echo %GREEN%✅ 虚拟环境已存在%NC%
)

REM 激活虚拟环境
call "%VENV_DIR%\Scripts\activate.bat"
echo %GREEN%✅ 虚拟环境已激活%NC%
echo.
goto :eof

:install_dependencies
echo %BLUE%📦 安装Python依赖包...%NC%

if exist "%PROJECT_DIR%requirements.txt" (
    pip install -r "%PROJECT_DIR%requirements.txt" >> "%LOG_FILE%" 2>&1
    echo %GREEN%✅ 依赖包安装完成%NC%
) else (
    echo %RED%❌ 未找到 requirements.txt 文件%NC%
    pause
    exit /b 1
)
echo.
goto :eof

:check_config
echo %BLUE%⚙️  检查配置文件...%NC%

if exist "%PROJECT_DIR%config.py" (
    echo %GREEN%✅ 配置文件存在%NC%
    
    REM 检查是否需要配置LLM
    findstr /C:"LLM_API_KEY.*\"\"" "%PROJECT_DIR%config.py" >nul 2>&1
    if !errorlevel! equ 0 (
        echo %YELLOW%⚠️  警告: LLM_API_KEY 为空，可能需要配置%NC%
    )
) else (
    echo %RED%❌ 配置文件不存在%NC%
    pause
    exit /b 1
)
echo.
goto :eof

:create_directories
echo %BLUE%📁 创建必要目录...%NC%

if not exist "%PROJECT_DIR%generated-yamls" mkdir "%PROJECT_DIR%generated-yamls"
if not exist "%PROJECT_DIR%logs" mkdir "%PROJECT_DIR%logs"

echo %GREEN%✅ 目录创建完成%NC%
echo.
goto :eof

:check_port
netstat -an | find ":%~1 " | find "LISTENING" >nul 2>&1
exit /b %errorlevel%

:find_available_port
set /a "port=%~1"
set /a "max_port=%~1+10"

:port_loop
call :check_port !port!
if %errorlevel% neq 0 (
    echo !port!
    goto :eof
)
set /a "port+=1"
if !port! leq !max_port! goto port_loop

echo %~1
goto :eof

:start_web_service
echo %BLUE%🌐 启动Web服务...%NC%

REM 查找可用端口
call :find_available_port 5001
set "PORT=%errorlevel%"

echo %GREEN%🚀 启动 ChaosBlade Web Interface...%NC%
echo %CYAN%📱 访问地址: http://localhost:!PORT!%NC%
echo %CYAN%📱 本地网络: http://127.0.0.1:!PORT!%NC%
echo %YELLOW%💡 按 Ctrl+C 停止服务%NC%
echo.

REM 启动服务
cd /d "%PROJECT_DIR%"
%PYTHON_CMD% web_app.py !PORT!
goto :eof

:start_cli_mode
echo %BLUE%🖥️  启动命令行模式...%NC%
echo %CYAN%输入 'python chat.py --help' 查看CLI帮助%NC%
echo.

cd /d "%PROJECT_DIR%"
%PYTHON_CMD% chat.py --interactive
goto :eof

:show_help
echo.
echo %CYAN%用法: %~nx0 [选项]%NC%
echo.
echo %YELLOW%选项:%NC%
echo   -h, --help     显示此帮助信息
echo   -c, --check    只检查环境，不启动服务  
echo   -i, --install  只安装依赖，不启动服务
echo   --cli          启动命令行模式
echo.
echo %YELLOW%示例:%NC%
echo   %~nx0              # 完整启动流程
echo   %~nx0 --check      # 只检查环境
echo   %~nx0 --cli        # 启动CLI模式
echo.
goto :eof

:main
REM 记录启动时间
echo 启动时间: %date% %time% > "%LOG_FILE%"

call :print_title

if "%~1"=="-h" goto help_mode
if "%~1"=="--help" goto help_mode
if "%~1"=="-c" goto check_mode
if "%~1"=="--check" goto check_mode
if "%~1"=="-i" goto install_mode
if "%~1"=="--install" goto install_mode
if "%~1"=="--cli" goto cli_mode
if "%~1"=="" goto full_mode

echo %RED%❌ 未知选项: %~1%NC%
call :show_help
pause
exit /b 1

:help_mode
call :show_help
pause
exit /b 0

:check_mode
call :check_dependencies
call :setup_venv
call :check_config
echo %GREEN%✅ 环境检查完成！%NC%
pause
exit /b 0

:install_mode
call :check_dependencies
call :setup_venv
call :install_dependencies
call :check_config
call :create_directories
echo %GREEN%✅ 依赖安装完成！%NC%
pause
exit /b 0

:cli_mode
call :check_dependencies
call :setup_venv
call :install_dependencies
call :check_config
call :create_directories
call :start_cli_mode
pause
exit /b 0

:full_mode
call :check_dependencies
call :setup_venv
call :install_dependencies
call :check_config
call :create_directories
call :start_web_service
goto :eof

REM 主入口
call :main %*
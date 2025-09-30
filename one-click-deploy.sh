#!/bin/bash
# ChaosBlade MCP 一键docker部署脚本

set -e

echo "🚀 开始部署 ChaosBlade MCP 应用..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo "❌ Docker 服务未启动，请先启动 Docker"
    exit 1
fi

# 设置变量
IMAGE_NAME="chaosblade-mcp"
CONTAINER_NAME="chaosblade-web"
PORT=${PORT:-5001}

echo "📦 构建 Docker 镜像..."
docker build -t $IMAGE_NAME .

echo "🧹 清理旧容器..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

echo "🔄 启动新容器..."
docker run -d \
  --name $CONTAINER_NAME \
  -p $PORT:5001 \
  -v $(pwd)/generated-yamls:/app/generated-yamls \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  $IMAGE_NAME


#sudo chmod -R 777 "$(pwd)"/generated-yamls
#sudo chmod -R 777 "$(pwd)"/logs

# 等待应用启动
echo "⏳ 等待应用启动..."
for i in {1..30}; do
    if curl -f http://localhost:$PORT/api/health &>/dev/null; then
        echo "✅ 应用启动成功！"
        echo "🌐 访问地址: http://localhost:$PORT"

        echo "📝 日志查看: docker logs $CONTAINER_NAME"
        echo "🛑 停止服务: docker stop $CONTAINER_NAME"
        exit 0
    fi
    sleep 2
done

echo "❌ 应用启动失败，请检查日志:"
docker logs $CONTAINER_NAME
exit 1
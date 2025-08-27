# ChaosBlade YAML生成故障注入

### 显示效果

<p align="center">
<img width="100%" align="center" src="images/1.jpg" />
</p>

### 使用配置
```bash
配置 config.py中的大模型 LLM_BASE_URL和Authorization，如果自己大模型没有配置Authorization，就不需要配置
```

## 基本命令

### 1. 直接生成 YAML
```bash
python chat.py "自然语言描述"
```

### 2. 交互式模式
```bash
python chat.py --interactive
# 或
python chat.py -i
```

### 3. 批量测试
```bash
python chat.py --test
```

## 快速示例

### Node 作用域
```bash
# 文件操作
python chat.py "在节点 node-1 上添加文件 /root/test.log，内容为 hello world"

# 网络实验
python chat.py "在节点 node-1 上创建网络延迟，延迟 3000ms，网卡 eth0"

# CPU 负载
python chat.py "在节点 node-1 上创建 CPU 负载，负载 90%，使用 CPU 0-3"
```

### Pod 作用域
```bash
# 文件操作
python3 chat.py "在 Pod nginx-pod-12345 中添加文件 /app/test.log，内容为 test content"

# 网络实验
python3 chat.py "在 Pod web-app-pod 上创建网络延迟，延迟 100ms"

# 进程控制
python chat.py "在 Pod app-pod 中杀死 nginx 进程，使用信号 9"
```

### Container 作用域
```bash
# 文件操作
python chat.py "在容器 app-container 中添加文件 /root/test.sh，启用 Base64 编码"

# 资源负载
python chat.py "在容器 web-container 中创建 CPU 负载，负载 60%，核心数 2"
```

### Host 作用域
```bash
# 文件操作
python chat.py "在主机 192.168.1.100 上创建文件 /tmp/host-test.log"

# 系统服务
python chat.py "在主机 server-01 上停止 nginx 服务"
```

### CRI 作用域
```bash
# 容器控制
python chat.py "暂停容器 container-id-12345，运行时为 docker"
```

## 常用参数模式

### 文件操作
- 基本格式: `在[目标]上添加文件[路径]，内容为[内容]`
- 示例: `在节点 node-1 上添加文件 /root/test.log，内容为 hello world`

### 网络实验
- 延迟: `创建网络延迟，延迟[时间]ms，网卡[网卡名]`
- 丢包: `创建网络丢包，丢包率[百分比]%`
- 示例: `在节点 node-1 上创建网络延迟，延迟 3000ms，网卡 eth0`

### CPU 负载
- 基本格式: `创建 CPU 负载，负载[百分比]%，使用 CPU[核心范围]`
- 示例: `在节点 node-1 上创建 CPU 负载，负载 90%，使用 CPU 0-3`

### 进程控制
- 终止: `杀死[进程名]进程，使用信号[信号号]`
- 示例: `在 Pod app-pod 中杀死 nginx 进程，使用信号 9`

### 多 Scope 生成
- 在交互式模式中选择 "all" 可生成所有 5 个作用域的配置



###



### 需要改进

* 确保目标资源存在且可访问
* 设置合理的超时时间
* 生产环境建议启用安全模式
* 避免在控制平面节点上执行实验
* 监控节点资源使用情况
* 确保有足够的节点副本
* 检查文件路径权限
* 考虑磁盘空间使用
* 确保文件操作可回滚









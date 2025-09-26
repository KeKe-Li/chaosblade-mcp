# AI模型配置指南

本指南说明如何配置各种AI模型的API密钥和连接参数。

## 🔑 快速配置

编辑 `config.py` 文件中的 `MODEL_API_CONFIGS` 部分，为你要使用的模型填入相应的API密钥。

## 📋 支持的模型及配置方法

### 1. DeepSeek 系列

**模型:** `deepseek-r1`, `deepseek-v3`

```python
"deepseek-r1": {
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "sk-xxxxxxxxxxxxxxxx",  # 你的DeepSeek API密钥
    "headers": {}
},
```

**获取方式:**
1. 访问 [DeepSeek开放平台](https://platform.deepseek.com/)
2. 注册账号并创建API密钥
3. 将密钥填入配置

---

### 2. OpenAI GPT 系列

**模型:** `gpt-4.1-mini`, `gpt-4.1-nano`, `gpt-5`, `gpt-4o-mini`

```python
"gpt-5": {
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-xxxxxxxxxxxxxxxx",  # 你的OpenAI API密钥
    "headers": {}
},
```

**获取方式:**
1. 访问 [OpenAI平台](https://platform.openai.com/)
2. 创建账号并生成API密钥
3. 将密钥填入配置

---

### 3. Google Gemini 系列

**模型:** `gemini-2.0-flash`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.5-pro`

```python
"gemini-2.5-pro": {
    "base_url": "https://generativelanguage.googleapis.com/v1",
    "api_key": "AIxxxxxxxxxxxxxxxx",  # 你的Google AI API密钥
    "headers": {}
},
```

**获取方式:**
1. 访问 [Google AI Studio](https://aistudio.google.com/)
2. 创建项目并获取API密钥
3. 将密钥填入配置

---

### 4. Moonshot Kimi 系列

**模型:** `kimi-k2`

```python
"kimi-k2": {
    "base_url": "https://api.moonshot.cn/v1",
    "api_key": "sk-xxxxxxxxxxxxxxxx",  # 你的Kimi API密钥
    "headers": {}
},
```

**获取方式:**
1. 访问 [Moonshot AI平台](https://platform.moonshot.cn/)
2. 注册并创建API密钥
3. 将密钥填入配置

---

### 5. 阿里云通义千问系列

**模型:** `qwen3-coder`, `qwen3-coder-480b`

```python
"qwen3-coder": {
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "sk-xxxxxxxxxxxxxxxx",  # 你的阿里云API密钥
    "headers": {}
},
```

**获取方式:**
1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
2. 开通服务并创建API密钥
3. 将密钥填入配置

---

### 6. 智谱GLM系列

**模型:** `glm-4.5`

```python
"glm-4.5": {
    "base_url": "https://open.bigmodel.cn/api/paas/v4",
    "api_key": "xxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxx",  # 你的智谱AI API密钥
    "headers": {}
},
```

**获取方式:**
1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册并创建API密钥
3. 将密钥填入配置

---

### 7. Llama3.1 (默认已配置)

**模型:** `llama3.1`

```python
"llama3.1": {
    "base_url": "https://ollama.web3ai.icu/v1",
    "api_key": "",
    "headers": {
        "Authorization": "Basic YWk6b2xsYW1hX3dlYjNhaQ=="
    }
},
```

**说明:** 此模型已预配置，无需额外设置。

---

## 🛠️ 配置示例

完整的配置示例：

```python
MODEL_API_CONFIGS = {
    "deepseek-r1": {
        "base_url": "https://api.deepseek.com/v1",
        "api_key": "sk-1234567890abcdef",  # 替换为你的密钥
        "headers": {}
    },
    "gpt-5": {
        "base_url": "https://api.openai.com/v1", 
        "api_key": "sk-proj-1234567890abcdef",  # 替换为你的密钥
        "headers": {}
    },
    # ... 其他模型配置
}
```

## 🔍 配置验证

启动应用后，在Web界面中：

1. ✅ **已配置** - 模型显示绿色"已配置"标签，可正常使用
2. ⚠️ **需要配置** - 模型显示黄色"需要配置"标签，选项被禁用

## 📝 注意事项

1. **API密钥安全**: 不要将包含真实API密钥的配置文件提交到代码仓库
2. **费用控制**: 大多数AI服务按使用量计费，请注意控制使用频率
3. **网络访问**: 某些API服务可能需要特定的网络环境才能访问
4. **配置生效**: 修改配置后需要重启应用才能生效

## 🚀 快速测试

配置完成后，启动应用：

```bash
python3 quick_start.py
```

访问 http://localhost:5001，选择已配置的模型进行测试。

## 💡 故障排除

**问题**: 模型显示"需要配置"
**解决**: 检查API密钥是否正确填入，确保没有多余的空格或换行符

**问题**: API调用失败
**解决**: 
1. 验证API密钥是否有效
2. 检查网络连接
3. 确认API服务商的使用配额

**问题**: 配置修改不生效
**解决**: 重启应用程序

---

更多问题请查看项目文档或提交Issue。
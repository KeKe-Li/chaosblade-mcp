import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from openai import OpenAI
import sys
import os

# 添加父目录到路径以导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

from .models import ParsedResult, ScopeConfig, TargetConfig


logger = logging.getLogger(__name__)


class NaturalLanguageParser:
    """自然语言解析器"""
    
    def __init__(self, base_url: str = None, model: str = None):
        # 设置模型
        self.model_key = model or "llama3.1"
        self.model_name = config.get_model_name(self.model_key)
        self.model_config = config.get_model_config(self.model_key)
        
        # 获取模型特定的API配置
        api_config = config.get_effective_api_config(self.model_key)
        
        # 如果传入了base_url，优先使用
        if base_url:
            api_config["base_url"] = base_url
            
        # 创建OpenAI客户端，使用模型特定的配置
        self.client = OpenAI(
            base_url=api_config["base_url"], 
            api_key=api_config["api_key"],
            default_headers=api_config["headers"]
        )
        
        self.specifications = self._load_yaml_specifications()
    
    def _load_yaml_specifications(self) -> Dict[str, Any]:
        """加载YAML规格说明"""
        # 这里应该从文件加载，暂时返回空字典
        return {}
    
    def parse_instruction(self, instruction: str) -> ParsedResult:
        """解析自然语言指令"""
        logger.info(f"解析指令: {instruction}")
        
        # 1. 提取基本信息
        scope = self._extract_scope(instruction)
        target = self._extract_target(instruction)
        action = self._extract_action(instruction)
        
        # 2. 生成实验名称
        name = self._generate_name(instruction, scope, target, action)
        
        # 3. 提取参数
        parameters = self._extract_parameters(instruction, target, action)
        
        # 4. 生成描述
        description = self._generate_description(instruction, scope, target, action)
        
        # 5. 计算置信度
        confidence = self._calculate_confidence(scope, target, action, parameters)
        
        # 6. 生成警告
        warnings = self._generate_warnings(scope, target, action, parameters)
        
        return ParsedResult(
            name=name,
            scope=scope,
            target=target,
            action=action,
            parameters=parameters,
            description=description,
            confidence=confidence,
            warnings=warnings
        )
    
    def _extract_scope(self, instruction: str) -> str:
        """提取作用域"""
        scopes = ScopeConfig.get_scope_by_keywords(instruction)
        return scopes[0] if scopes else "host"
    
    def _extract_target(self, instruction: str) -> str:
        """提取目标"""
        instruction_lower = instruction.lower()
        
        # 目标关键词映射
        target_keywords = {
            "cpu": ["cpu", "处理器", "中央处理器", "核心"],
            "network": ["网络", "network", "网卡", "端口", "延迟", "丢包", "带宽"],
            "process": ["进程", "process", "杀死", "停止", "进程名"],
            "disk": ["磁盘", "disk", "硬盘", "io", "读写", "占用"],
            "mem": ["内存", "memory", "ram", "内存负载"],
            "file": ["文件", "file", "创建文件", "修改文件", "删除文件"],
            "script": ["脚本", "script", "shell", "bash"],
            "strace": ["系统调用", "strace", "syscall"],
            "systemd": ["服务", "service", "systemd", "守护进程"],
            "time": ["时间", "time", "时钟", "ntp"]
        }
        
        for target, keywords in target_keywords.items():
            for keyword in keywords:
                if keyword in instruction_lower:
                    return target
        
        return "file"  # 默认目标
    
    def _extract_action(self, instruction: str) -> str:
        """提取动作"""
        instruction_lower = instruction.lower()
        
        # 动作关键词映射 - 优先级从高到低
        action_keywords = {
            "delay": ["延迟", "delay", "慢", "网络延迟"],
            "loss": ["丢包", "loss", "丢失"],
            "load": ["负载", "load", "满载"],
            "kill": ["杀死", "kill", "停止", "终止"],
            "occupy": ["占用", "occupy", "使用"],
            "pause": ["暂停", "pause"],
            "restart": ["重启", "restart", "重新启动"],
            "add": ["添加", "创建", "新增", "add", "create"],
            "delete": ["删除", "移除", "delete", "remove"],
            "modify": ["修改", "更改", "modify", "change"]
        }
        
        for action, keywords in action_keywords.items():
            for keyword in keywords:
                if keyword in instruction_lower:
                    return action
        
        return "add"  # 默认动作
    
    def _generate_name(self, instruction: str, scope: str, target: str, action: str) -> str:
        """生成实验名称"""
        # 简化的名称生成逻辑
        timestamp = self._get_timestamp()
        return f"{scope}-{target}-{action}-{timestamp}"
    
    def _extract_parameters(self, instruction: str, target: str, action: str) -> Dict[str, Any]:
        """提取参数"""
        parameters = {}
        
        # 提取文件路径
        file_path_match = re.search(r'[/][^\s]+', instruction)
        if file_path_match:
            parameters["filepath"] = file_path_match.group()
        
        # 提取内容
        content_match = re.search(r'内容为[\"\'"]?(.+?)[\"\'"]?$', instruction)
        if content_match:
            parameters["content"] = content_match.group(1)
        
        # 提取数字参数
        if "延迟" in instruction or "delay" in instruction.lower():
            # 特殊处理延迟参数，查找延迟关键词附近的数字
            delay_match = re.search(r'延迟[^\d]*(\d+)', instruction)
            if not delay_match:
                delay_match = re.search(r'delay[^\d]*(\d+)', instruction.lower())
            if delay_match:
                parameters["delay"] = delay_match.group(1)
        elif "负载" in instruction or "load" in instruction.lower():
            # 特殊处理负载参数，查找负载关键词附近的数字
            load_match = re.search(r'负载[^\d]*(\d+)', instruction)
            if not load_match:
                load_match = re.search(r'load[^\d]*(\d+)', instruction.lower())
            if load_match:
                parameters["load"] = load_match.group(1)
        
        # 提取网卡参数
        if "网卡" in instruction or "interface" in instruction.lower():
            interface_match = re.search(r'网卡\s+(\w+)', instruction)
            if not interface_match:
                interface_match = re.search(r'interface\s+(\w+)', instruction.lower())
            if interface_match:
                parameters["interface"] = interface_match.group(1)
        
        # 提取节点/容器名称
        names = self._extract_names(instruction)
        if names:
            parameters["names"] = names
        
        # 提取命名空间
        namespace_match = re.search(r'命名空间[为是]?[\"\'"]?([a-zA-Z0-9-]+)[\"\'"]?', instruction)
        if namespace_match:
            parameters["namespace"] = [namespace_match.group(1)]
        
        return parameters
    
    def _extract_names(self, instruction: str) -> List[str]:
        """提取名称列表"""
        # 匹配IP地址
        ip_matches = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', instruction)
        if ip_matches:
            return ip_matches
        
        # 匹配Pod名称格式
        pod_matches = re.findall(r'[a-zA-Z0-9-]+-[a-zA-Z0-9]{5,10}', instruction)
        if pod_matches:
            return pod_matches
        
        # 匹配普通名称
        name_matches = re.findall(r'[a-zA-Z0-9-]+', instruction)
        return name_matches[:1] if name_matches else []
    
    def _generate_description(self, instruction: str, scope: str, target: str, action: str) -> str:
        """生成描述"""
        return f"{scope}级别{target}{action}实验"
    
    def _calculate_confidence(self, scope: str, target: str, action: str, parameters: Dict[str, Any]) -> float:
        """计算置信度"""
        confidence = 0.5  # 基础置信度
        
        # 根据参数完整性提升置信度
        if parameters:
            confidence += 0.2
        
        # 根据目标匹配度提升置信度
        if target != "file":  # 不是默认目标
            confidence += 0.2
        
        # 根据动作匹配度提升置信度
        if action != "add":  # 不是默认动作
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_warnings(self, scope: str, target: str, action: str, parameters: Dict[str, Any]) -> List[str]:
        """生成警告信息"""
        warnings = []
        
        # 检查必需参数
        required_params = ScopeConfig.get_scope_config(scope).get("required_matchers", [])
        for param in required_params:
            if param not in parameters:
                warnings.append(f"缺少必需参数: {param}")
        
        # 检查参数格式
        if "timeout" in parameters:
            timeout_pattern = r"^\d+[smh]$"
            if not re.match(timeout_pattern, str(parameters["timeout"])):
                warnings.append("超时时间格式建议使用 '300s', '5m', '1h' 格式")
        
        return warnings
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        import datetime
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


class ScopeDetector:
    """作用域检测器"""
    
    @staticmethod
    def detect_scope(instruction: str) -> str:
        """检测作用域"""
        return ScopeConfig.get_scope_by_keywords(instruction)[0] if ScopeConfig.get_scope_by_keywords(instruction) else "host"
    
    @staticmethod
    def get_scope_priority(scope: str) -> int:
        """获取作用域优先级"""
        config = ScopeConfig.get_scope_config(scope)
        return config.get("priority", 99)
    
    @staticmethod
    def is_scope_compatible(scope: str, target: str) -> bool:
        """检查作用域与目标是否兼容"""
        if TargetConfig.is_multi_scope_target(target):
            return True
        
        expected_scope = TargetConfig.get_target_scope(target)
        return scope == expected_scope
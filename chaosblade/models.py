from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union


@dataclass
class ParsedResult:
    """解析结果数据类"""
    name: str
    scope: str
    target: str
    action: str
    parameters: Dict[str, Any]
    description: str
    confidence: float = 0.0
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class ValidationResult:
    """验证结果数据类"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_required: List[str] = field(default_factory=list)
    invalid_parameters: List[str] = field(default_factory=list)


@dataclass
class ScopeConfig:
    """作用域配置"""
    keywords: List[str]
    description: str
    priority: int
    required_matchers: List[str] = field(default_factory=list)
    optional_matchers: List[str] = field(default_factory=list)
    default_flags: Dict[str, Any] = field(default_factory=dict)
    
    def get_required_params(self) -> List[str]:
        """获取必需参数"""
        return self.required_matchers
    
    def get_optional_params(self) -> List[str]:
        """获取可选参数"""
        return self.optional_matchers
    
    @staticmethod
    def get_all_scopes() -> List[str]:
        """获取所有可用的作用域"""
        return ["node", "pod", "container", "host", "cri"]
    
    @staticmethod
    def get_scope_by_keywords(instruction: str) -> List[str]:
        """根据关键词检测作用域"""
        scopes = []
        instruction_lower = instruction.lower()
        
        if any(keyword in instruction_lower for keyword in ["节点", "node"]):
            scopes.append("node")
        if any(keyword in instruction_lower for keyword in ["pod", "容器组"]):
            scopes.append("pod")
        if any(keyword in instruction_lower for keyword in ["容器", "container"]):
            scopes.append("container")
        if any(keyword in instruction_lower for keyword in ["主机", "host", "服务器"]):
            scopes.append("host")
        if any(keyword in instruction_lower for keyword in ["cri", "运行时"]):
            scopes.append("cri")
            
        return scopes or ["host"]  # 默认返回host
    
    @staticmethod
    def get_scope_config(scope: str) -> Dict[str, Any]:
        """获取作用域配置"""
        configs = {
            "node": {
                "description": "Kubernetes节点作用域",
                "required_matchers": ["names"],
                "optional_matchers": ["labels"],
                "priority": 1
            },
            "pod": {
                "description": "Kubernetes Pod作用域", 
                "required_matchers": ["names"],
                "optional_matchers": ["labels", "namespace"],
                "priority": 2
            },
            "container": {
                "description": "容器作用域",
                "required_matchers": ["names"],
                "optional_matchers": ["labels"],
                "priority": 3
            },
            "host": {
                "description": "主机作用域",
                "required_matchers": [],
                "optional_matchers": ["names"],
                "priority": 4
            },
            "cri": {
                "description": "容器运行时作用域",
                "required_matchers": ["names"],
                "optional_matchers": [],
                "priority": 5
            }
        }
        return configs.get(scope, configs["host"])


@dataclass
class TargetConfig:
    """目标配置"""
    name: str
    description: str
    supported_scopes: List[str]
    actions: Dict[str, Dict[str, Any]]
    default_scope: str = "host"
    
    @staticmethod
    def is_multi_scope_target(target: str) -> bool:
        """检查目标是否支持多个作用域"""
        multi_scope_targets = ["file", "process", "network", "cpu", "memory", "disk"]
        return target in multi_scope_targets
    
    @staticmethod
    def get_target_scope(target: str) -> str:
        """获取目标的默认作用域"""
        target_scopes = {
            "file": "host",
            "process": "host", 
            "network": "host",
            "cpu": "host",
            "memory": "host",
            "disk": "host"
        }
        return target_scopes.get(target, "host")


@dataclass
class ValidationConfig:
    """验证配置"""
    
    def __init__(self):
        self.rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """加载验证规则"""
        return {
            "timeout": {
                "pattern": r"^\d+[smh]?$",
                "description": "超时时间格式: 数字+单位(s/m/h)"
            },
            "percentage": {
                "pattern": r"^\d{1,3}$",
                "range": [0, 100],
                "description": "百分比: 0-100的整数"
            },
            "size": {
                "pattern": r"^\d+[KMGT]?B?$",
                "description": "大小格式: 数字+单位(K/M/G/T)B"
            },
            "ip": {
                "pattern": r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",
                "description": "IP地址格式: xxx.xxx.xxx.xxx"
            }
        }
    
    @staticmethod 
    def get_validation_rules(param_name: str) -> Dict[str, Any]:
        """获取参数验证规则"""
        config = ValidationConfig()
        return config.rules.get(param_name, {})


@dataclass
class TemplateConfig:
    """模板配置"""
    
    @staticmethod
    def create_experiment_template(scope: str, target: str, action: str, 
                                 matchers: List[Dict], flags: List[Dict],
                                 timeout: str = "300s", namespace: str = "default") -> Dict[str, Any]:
        """创建实验模板"""
        template = {
            "apiVersion": "chaosblade.io/v1alpha1",
            "kind": "ChaosBlade",
            "metadata": {
                "name": f"{scope}-{target}-{action}",
                "namespace": namespace
            },
            "spec": {
                "experiments": [
                    {
                        "scope": scope,
                        "target": target,
                        "action": action,
                        "desc": f"{scope} {target} {action} experiment",
                        "matchers": matchers,
                        "flags": flags
                    }
                ]
            }
        }
        
        # 添加超时配置
        if timeout:
            template["spec"]["experiments"][0]["flags"].append({
                "name": "timeout",
                "value": timeout
            })
            
        return template


@dataclass
class ExperimentConfig:
    """实验配置"""
    name: str
    scope: str
    target: str
    action: str
    description: str
    matchers: List[Dict[str, Any]] = field(default_factory=list)
    flags: List[Dict[str, Any]] = field(default_factory=list)
    timeout: str = "300s"
    namespace: str = "default"


@dataclass
class GenerationResult:
    """生成结果"""
    success: bool
    yaml_content: str = ""
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)
    generated_files: List[str] = field(default_factory=list)
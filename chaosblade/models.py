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


@dataclass
class TargetConfig:
    """目标配置"""
    name: str
    description: str
    supported_scopes: List[str]
    actions: Dict[str, Dict[str, Any]]
    default_scope: str = "host"


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
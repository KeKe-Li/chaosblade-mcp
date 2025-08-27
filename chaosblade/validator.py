import re
import socket
import subprocess
import logging
from typing import Dict, List, Any, Optional, Tuple

from .models import ValidationResult, ParsedResult
from .config import ScopeConfig, ValidationConfig


logger = logging.getLogger(__name__)


class ParameterValidator:
    """参数验证器"""
    
    def __init__(self):
        self.validation_rules = ValidationConfig()
    
    def validate_parameters(self, params: Dict[str, Any], scope: str) -> ValidationResult:
        """验证参数"""
        result = ValidationResult(is_valid=True)
        
        # 获取作用域配置
        scope_config = ScopeConfig.get_scope_config(scope)
        required_matchers = scope_config.get("required_matchers", [])
        
        # 检查必需参数
        missing_required = []
        for param in required_matchers:
            if param not in params:
                missing_required.append(param)
        
        if missing_required:
            result.missing_required = missing_required
            result.errors.append(f"缺少必需参数: {', '.join(missing_required)}")
            result.is_valid = False
        
        # 检查参数格式
        invalid_params = []
        for param_name, param_value in params.items():
            validation_result = self._validate_single_parameter(param_name, param_value)
            if not validation_result["is_valid"]:
                invalid_params.append(param_name)
                result.errors.append(validation_result["message"])
        
        if invalid_params:
            result.invalid_parameters = invalid_params
            result.is_valid = False
        
        # 检查参数冲突
        conflicts = self._check_parameter_conflicts(params, scope)
        if conflicts:
            result.errors.extend(conflicts)
            result.is_valid = False
        
        # 生成警告
        result.warnings = self._generate_warnings(params, scope)
        
        return result
    
    def _validate_single_parameter(self, param_name: str, param_value: Any) -> Dict[str, Any]:
        """验证单个参数"""
        rules = ValidationConfig.get_validation_rules(param_name)
        
        if not rules:
            return {"is_valid": True}
        
        # 检查必填项
        if rules.get("required") and not param_value:
            return {
                "is_valid": False,
                "message": rules.get("message", f"参数 {param_name} 不能为空")
            }
        
        # 检查格式
        pattern = rules.get("pattern")
        if pattern and param_value:
            if not re.match(pattern, str(param_value)):
                return {
                    "is_valid": False,
                    "message": rules.get("message", f"参数 {param_name} 格式无效")
                }
        
        return {"is_valid": True}
    
    def _check_parameter_conflicts(self, params: Dict[str, Any], scope: str) -> List[str]:
        """检查参数冲突"""
        conflicts = []
        
        # 检查作用域特定冲突
        if scope == "container":
            if "container-names" not in params:
                conflicts.append("容器作用域必须指定 container-names 参数")
        
        # 检查超时时间合理性
        if "timeout" in params:
            timeout_str = str(params["timeout"])
            timeout_match = re.match(r"^(\d+)([smh])$", timeout_str)
            if timeout_match:
                timeout_value = int(timeout_match.group(1))
                timeout_unit = timeout_match.group(2)
                
                if timeout_unit == "s" and timeout_value > 3600:
                    conflicts.append("超时时间过长，建议使用分钟或小时单位")
        
        return conflicts
    
    def _generate_warnings(self, params: Dict[str, Any], scope: str) -> List[str]:
        """生成警告信息"""
        warnings = []
        
        # 检查安全参数
        if scope == "host" and params.get("safe-mode") != "true":
            warnings.append("主机实验建议启用安全模式")
        
        # 检查Base64编码
        if scope == "container" and "content" in params:
            content = str(params["content"])
            if len(content) > 100 and params.get("enable-base64") != "true":
                warnings.append("复杂内容建议启用Base64编码")
        
        return warnings


class SmartParameterOptimizer:
    """智能参数优化器"""
    
    def __init__(self):
        self.validator = ParameterValidator()
    
    def apply_smart_defaults(self, params: Dict[str, Any], scope: str) -> Dict[str, Any]:
        """应用智能默认值"""
        optimized_params = params.copy()
        
        # 获取作用域默认标志
        scope_config = ScopeConfig.get_scope_config(scope)
        default_flags = scope_config.get("default_flags", {})
        
        # 应用默认值
        for key, value in default_flags.items():
            if key not in optimized_params:
                optimized_params[key] = value
                logger.info(f"应用默认值: {key} = {value}")
        
        # 智能检测参数
        optimized_params.update(self._smart_detect_parameters(scope, params))
        
        return optimized_params
    
    def _smart_detect_parameters(self, scope: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """智能检测参数"""
        detected_params = {}
        
        # 检测节点名称
        if scope == "node" and "names" not in params:
            node_name = self._detect_current_node()
            if node_name:
                detected_params["names"] = [node_name]
                logger.info(f"智能检测到节点: {node_name}")
        
        # 检测命名空间
        if scope in ["pod", "container"] and "namespace" not in params:
            namespace = self._detect_current_namespace()
            if namespace:
                detected_params["namespace"] = [namespace]
                logger.info(f"智能检测到命名空间: {namespace}")
        
        # 检测容器名称
        if scope == "container" and "container-names" not in params:
            container_names = self._detect_container_names()
            if container_names:
                detected_params["container-names"] = container_names
                logger.info(f"智能检测到容器: {container_names}")
        
        # 检测主机名
        if scope == "host" and "names" not in params:
            hostname = self._detect_hostname()
            if hostname:
                detected_params["names"] = [hostname]
                logger.info(f"智能检测到主机: {hostname}")
        
        return detected_params
    
    def _detect_current_node(self) -> Optional[str]:
        """检测当前节点"""
        try:
            # 尝试使用kubectl获取节点信息
            result = subprocess.run(
                ["kubectl", "get", "nodes", "-o", "jsonpath={.items[0].metadata.name}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # 回退到本地主机名
        try:
            return socket.gethostname()
        except:
            return "localhost"
    
    def _detect_current_namespace(self) -> Optional[str]:
        """检测当前命名空间"""
        try:
            # 尝试获取当前命名空间
            result = subprocess.run(
                ["kubectl", "config", "view", "--minify", "-o", "jsonpath={..namespace}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                namespace = result.stdout.strip()
                return namespace if namespace else "default"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return "default"
    
    def _detect_container_names(self) -> Optional[List[str]]:
        """检测容器名称"""
        try:
            # 尝试获取当前pod的容器信息
            result = subprocess.run(
                ["kubectl", "get", "pods", "-o", "jsonpath={.items[0].spec.containers[*].name}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def _detect_hostname(self) -> Optional[str]:
        """检测主机名"""
        try:
            return socket.gethostname()
        except:
            return None
    
    def optimize_parameters(self, params: Dict[str, Any], scope: str) -> Tuple[Dict[str, Any], List[str]]:
        """优化参数"""
        warnings = []
        
        # 应用智能默认值
        optimized_params = self.apply_smart_defaults(params, scope)
        
        # 验证参数
        validation_result = self.validator.validate_parameters(optimized_params, scope)
        warnings.extend(validation_result.warnings)
        
        # 自动修复参数
        if not validation_result.is_valid:
            fixed_params = self._auto_fix_parameters(optimized_params, scope, validation_result)
            if fixed_params:
                optimized_params.update(fixed_params)
                warnings.append("已自动修复部分参数问题")
        
        return optimized_params, warnings
    
    def _auto_fix_parameters(self, params: Dict[str, Any], scope: str, 
                            validation_result: ValidationResult) -> Dict[str, Any]:
        """自动修复参数"""
        fixed_params = {}
        
        # 修复缺失的必需参数
        for missing_param in validation_result.missing_required:
            if missing_param == "names":
                if scope == "node":
                    fixed_params["names"] = ["localhost"]
                elif scope == "host":
                    fixed_params["names"] = ["127.0.0.1"]
            
            elif missing_param == "namespace":
                fixed_params["namespace"] = ["default"]
            
            elif missing_param == "container-names":
                fixed_params["container-names"] = ["main"]
        
        # 修复格式问题
        for invalid_param in validation_result.invalid_parameters:
            if invalid_param == "timeout":
                # 修复超时时间格式
                timeout_value = str(params.get("timeout", "300"))
                if timeout_value.isdigit():
                    fixed_params["timeout"] = f"{timeout_value}s"
            
            elif invalid_param == "enable-base64":
                # 修复Base64参数
                fixed_params["enable-base64"] = "false"
        
        return fixed_params


class BestPracticesAdvisor:
    """最佳实践建议器"""
    
    @staticmethod
    def get_best_practices(scope: str, target: str, action: str) -> List[str]:
        """获取最佳实践建议"""
        practices = []
        
        # 通用最佳实践
        practices.extend([
            # "🔍 确保目标资源存在且可访问",
            # "⏱️ 设置合理的超时时间",
            # "🛡️ 生产环境建议启用安全模式"
        ])
        
        # 作用域特定建议
        if scope == "node":
            practices.extend([
                # "🎯 避免在控制平面节点上执行实验",
                # "📊 监控节点资源使用情况",
                # "🔄 确保有足够的节点副本"
            ])
        
        elif scope == "pod":
            practices.extend([
                # "🏷️ 确认Pod标签和选择器",
                # "🔄 考虑Pod的重启策略",
                # "📈 监控Pod状态和应用健康"
            ])
        
        elif scope == "container":
            practices.extend([
                # "🏷️ 确保容器名称准确无误",
                # "📁 注意容器的文件系统权限",
                # "🔐 对于多容器Pod，明确指定目标容器"
            ])
        
        elif scope == "host":
            practices.extend([
                # "🔒 始终启用安全模式",
                # "🚫 避免修改系统关键文件",
                # "👥 确保有主机访问权限"
            ])
        
        elif scope == "cri":
            practices.extend([
                # "🏗️ 了解容器运行时类型",
                # "🚫 避免影响运行时核心功能",
                # "📊 监控容器状态变化"
            ])
        
        # 目标特定建议
        if target == "network":
            practices.extend([
                # "🌐 测试网络连通性",
                # "📡 考虑网络拓扑结构",
                # "🔍 验证端口可用性"
            ])
        
        elif target == "cpu":
            practices.extend([
                # "💹 监控CPU使用率",
                # "⚡ 避免过高的CPU负载",
                # "🎯 考虑CPU核心分配"
            ])
        
        elif target == "file":
            practices.extend([
                # "📁 检查文件路径权限",
                # "💾 考虑磁盘空间使用",
                # "🔄 确保文件操作可回滚"
            ])
        
        return practices
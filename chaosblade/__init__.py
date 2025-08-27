from .models import (
    ParsedResult, 
    ValidationResult, 
    ScopeConfig, 
    TargetConfig, 
    ExperimentConfig,
    GenerationResult
)

from .parser import NaturalLanguageParser, ScopeDetector
from .generator import YAMLGenerator, FileGenerator, BatchGenerator, TemplateRenderer
from .validator import ParameterValidator, SmartParameterOptimizer, BestPracticesAdvisor
from .cli import ChaosBladeCLI

__version__ = "1.0.0"
__author__ = ""
__email__ = ""

__all__ = [
    # Models
    "ParsedResult",
    "ValidationResult", 
    "ScopeConfig",
    "TargetConfig",
    "ExperimentConfig",
    "GenerationResult",
    
    # Parser
    "NaturalLanguageParser",
    "ScopeDetector",
    
    # Generator
    "YAMLGenerator",
    "FileGenerator", 
    "BatchGenerator",
    "TemplateRenderer",
    
    # Validator
    "ParameterValidator",
    "SmartParameterOptimizer",
    "BestPracticesAdvisor",
    
    # CLI
    "ChaosBladeCLI"
]


def create_parser(base_url: str = None) -> NaturalLanguageParser:
    """创建解析器实例"""
    return NaturalLanguageParser(base_url)

def create_generator() -> YAMLGenerator:
    """创建生成器实例"""
    return YAMLGenerator()


def create_cli() -> ChaosBladeCLI:
    """创建CLI实例"""
    return ChaosBladeCLI()


def quick_generate(instruction: str, output_file: str = None) -> str:
    """快速生成YAML
    
    Args:
        instruction: 自然语言指令
        output_file: 输出文件路径（可选）
    
    Returns:
        生成的YAML内容
    """
    parser = create_parser()
    generator = create_generator()
    
    parsed_data = parser.parse_instruction(instruction)
    result = generator.generate_yaml(parsed_data)
    
    if result.success:
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.yaml_content)
        
        return result.yaml_content
    else:
        raise Exception(f"生成失败: {result.error_message}")


def batch_generate(instructions: list, output_dir: str = "./generated-yamls") -> list:
    """批量生成YAML
    
    Args:
        instructions: 指令列表
        output_dir: 输出目录
    
    Returns:
        生成结果列表
    """
    batch_gen = BatchGenerator()
    return batch_gen.generate_from_instructions(instructions)
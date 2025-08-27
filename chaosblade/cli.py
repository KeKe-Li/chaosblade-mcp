import sys
import logging
from typing import List, Optional

from .parser import NaturalLanguageParser, ScopeDetector
from .generator import YAMLGenerator, FileGenerator, BatchGenerator
from .models import ParsedResult
from .config import ScopeConfig


logger = logging.getLogger(__name__)


class ChaosBladeCLI:
    """ChaosBlade命令行接口"""
    
    def __init__(self):
        self.parser = NaturalLanguageParser()
        self.generator = YAMLGenerator()
        self.file_generator = FileGenerator()
        self.batch_generator = BatchGenerator()
    
    def run(self, args: List[str]):
        """运行CLI"""
        if not args:
            self.show_help()
            return
        
        command = args[0]
        
        if command in ["--help", "-h", "help"]:
            self.show_help()
        
        elif command in ["--test", "test"]:
            self.run_tests()
        
        elif command in ["--interactive", "-i"]:
            self.interactive_mode()
        
        elif command in ["--generate", "gen"]:
            self.generate_from_file(args[1:])
        
        elif command in ["--batch", "batch"]:
            self.batch_mode(args[1:])
        
        elif command in ["--demo", "demo"]:
            self.demo_mode()
        
        elif command.startswith("--"):
            self.show_help()
        
        else:
            # 直接处理指令
            instruction = " ".join(args)
            self.process_instruction(instruction)
    
    def process_instruction(self, instruction: str):
        """处理单个指令"""
        print(f"🚀 解析指令: {instruction}")
        
        try:
            # 解析指令
            parsed_data = self.parser.parse_instruction(instruction)
            
            # 显示解析结果
            self.show_parsed_result(parsed_data)
            
            # 检查是否需要scope选择
            selected_scope = self.interactive_scope_selection(instruction, parsed_data.target)
            
            if selected_scope == "all":
                # 生成所有scope
                self.generate_all_scopes(parsed_data)
            else:
                # 使用选择的scope
                if selected_scope:
                    parsed_data.scope = selected_scope
                
                # 生成单个YAML
                self.generate_single_yaml(parsed_data)
        
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            logger.error(f"处理指令失败: {e}")
    
    def show_parsed_result(self, parsed_data: ParsedResult):
        """显示解析结果"""
        print(f"\n📋 解析结果:")
        print(f"  名称: {parsed_data.name}")
        print(f"  作用域: {parsed_data.scope}")
        print(f"  目标: {parsed_data.target}")
        print(f"  动作: {parsed_data.action}")
        print(f"  置信度: {parsed_data.confidence:.2f}")
        print(f"  描述: {parsed_data.description}")
        
        if parsed_data.parameters:
            print(f"  参数:")
            for key, value in parsed_data.parameters.items():
                print(f"    {key}: {value}")
        
        if parsed_data.warnings:
            print(f"  ⚠️  警告: {', '.join(parsed_data.warnings)}")
    
    def interactive_scope_selection(self, instruction: str, target: str) -> Optional[str]:
        """交互式scope选择"""
        # 检查scope是否明确
        detected_scopes = ScopeConfig.get_scope_by_keywords(instruction)
        
        if len(detected_scopes) == 1:
            print(f"✅ 自动检测到作用域: {detected_scopes[0]}")
            return detected_scopes[0]
        
        # 如果不明确，提供选择
        print(f"\n🎯 检测到多个可能的作用域: {', '.join(detected_scopes)}")
        print("请选择实验作用域:")
        
        scopes = ScopeConfig.get_all_scopes()
        for i, scope in enumerate(scopes, 1):
            config = ScopeConfig.get_scope_config(scope)
            print(f"  {i}. {scope.upper()} - {config.get('description', '')}")
        
        print(f"  {len(scopes) + 1}. ALL - 生成所有作用域")
        print(f"  {len(scopes) + 2}. EXIT - 退出")
        
        while True:
            try:
                choice = input("\n请输入选择 (1-{}): ".format(len(scopes) + 2))
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(scopes):
                    return scopes[choice_num - 1]
                elif choice_num == len(scopes) + 1:
                    return "all"
                elif choice_num == len(scopes) + 2:
                    return None
                else:
                    print("❌ 无效选择，请重新输入")
            
            except (ValueError, KeyboardInterrupt, EOFError):
                # 非交互环境或用户中断，返回默认选择
                if detected_scopes:
                    return detected_scopes[0]  # 返回第一个检测到的scope
                print("❌ 输入无效，使用默认作用域")
                return None
    
    def generate_single_yaml(self, parsed_data: ParsedResult):
        """生成单个YAML"""
        result = self.generator.generate_yaml(parsed_data)
        
        if result.success:
            print(f"\n✅ YAML生成成功:")
            print(result.yaml_content)
            
            # 检查是否在交互环境中
            try:
                # 询问是否保存
                save_choice = input("\n💾 是否保存到文件? (y/n): ").lower()
                if save_choice == 'y':
                    filename = self.file_generator.generate_filename(
                        parsed_data.scope, parsed_data.target, parsed_data.action
                    )
                    filepath = self.file_generator.save_yaml(result.yaml_content, filename)
                    print(f"📁 文件已保存: {filepath}")
            except (EOFError, KeyboardInterrupt):
                # 非交互环境，默认不保存
                pass
        else:
            print(f"❌ YAML生成失败: {result.error_message}")
    
    def generate_all_scopes(self, parsed_data: ParsedResult):
        """生成所有作用域的YAML"""
        scopes = ScopeConfig.get_all_scopes()
        results = self.generator.generate_multiple_yamls(parsed_data, scopes)
        
        print(f"\n📦 生成了 {len(results)} 个不同作用域的YAML配置:")
        
        for i, (result, scope) in enumerate(zip(results, scopes), 1):
            print(f"\n--- YAML {i} ({scope.upper()} Scope) ---")
            
            if result.success:
                print(result.yaml_content)
                
                # 保存文件
                filename = f"{parsed_data.name}-{scope}.yaml"
                filepath = self.file_generator.save_yaml(result.yaml_content, filename)
                print(f"📁 已保存: {filepath}")
            else:
                print(f"❌ 生成失败: {result.error_message}")
    
    def interactive_mode(self):
        """交互式模式"""
        print("🎮 ChaosBlade YAML 生成器 - 交互式模式")
        print("输入 'quit' 或 'exit' 退出")
        print("=" * 50)
        
        while True:
            try:
                instruction = input("\n🔧 请输入实验描述: ").strip()
                
                if instruction.lower() in ['quit', 'exit', '退出']:
                    print("👋 再见!")
                    break
                
                if not instruction:
                    continue
                
                self.process_instruction(instruction)
                
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
    
    def run_tests(self):
        """运行测试"""
        print("🧪 运行测试用例...")
        
        test_cases = [
            "在节点 node-1 上添加文件 /root/test.log，内容为 test content",
            "在 Pod nginx-pod 上创建网络延迟，延迟 100ms",
            "在容器 app-container 中创建 CPU 负载，负载 60%",
            "在主机 192.168.1.100 上停止 nginx 服务",
            "暂停容器 container-id-12345，运行时为 docker"
        ]
        
        results = self.batch_generator.generate_from_instructions(test_cases)
        
        print(f"\n📊 测试结果:")
        success_count = sum(1 for r in results if r.success)
        print(f"✅ 成功: {success_count}/{len(results)}")
        
        for i, (test_case, result) in enumerate(zip(test_cases, results), 1):
            status = "✅" if result.success else "❌"
            print(f"  {status} 测试 {i}: {test_case[:50]}...")
            if not result.success:
                print(f"      错误: {result.error_message}")
    
    def generate_from_file(self, args: List[str]):
        """从文件生成"""
        if not args:
            print("❌ 请指定输入文件")
            return
        
        input_file = args[0]
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                instructions = [line.strip() for line in f if line.strip()]
            
            print(f"📖 从文件 {input_file} 读取到 {len(instructions)} 条指令")
            
            results = self.batch_generator.generate_from_instructions(instructions)
            
            success_count = sum(1 for r in results if r.success)
            print(f"✅ 成功生成 {success_count} 个配置文件")
            
        except FileNotFoundError:
            print(f"❌ 文件不存在: {input_file}")
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
    
    def batch_mode(self, args: List[str]):
        """批量模式"""
        print("📦 批量生成模式")
        
        if not args:
            print("使用默认测试用例...")
            test_cases = [
                "在节点上添加文件 /tmp/test.log",
                "在Pod上创建网络延迟 100ms",
                "在容器中创建CPU负载 50%",
                "在主机上停止nginx服务"
            ]
        else:
            test_cases = [" ".join(args)]
        
        results = self.batch_generator.generate_from_instructions(test_cases)
        
        print(f"\n📊 批量生成结果:")
        for i, (test_case, result) in enumerate(zip(test_cases, results), 1):
            status = "✅" if result.success else "❌"
            print(f"  {status} {i}: {test_case}")
            
            if result.success and result.generated_files:
                for file_path in result.generated_files:
                    print(f"      📁 {file_path}")
            elif not result.success:
                print(f"      错误: {result.error_message}")
    
    def demo_mode(self):
        """演示模式"""
        print("🎬 ChaosBlade YAML 生成器演示")
        print("=" * 50)
        
        demo_instructions = [
            "在节点 node-1 上添加文件 /root/test.log，内容为 hello world",
            "在 Pod web-app-pod 上创建网络延迟，延迟 100ms，网卡 eth0",
            "在容器 app-container 中创建 CPU 负载，负载 60%，核心数 2",
            "在主机 192.168.1.100 上停止 nginx 服务"
        ]
        
        print("📝 演示指令列表:")
        for i, instruction in enumerate(demo_instructions, 1):
            print(f"  {i}. {instruction}")
        
        print(f"\n🚀 开始生成 {len(demo_instructions)} 个演示配置...")
        
        results = self.batch_generator.generate_from_instructions(demo_instructions)
        
        print(f"\n📊 演示结果:")
        success_count = sum(1 for r in results if r.success)
        print(f"✅ 成功: {success_count}/{len(results)}")
        
        for i, (instruction, result) in enumerate(zip(demo_instructions, results), 1):
            print(f"\n--- 演示 {i} ---")
            print(f"指令: {instruction}")
            
            if result.success:
                print("✅ 生成成功:")
                print(result.yaml_content[:200] + "..." if len(result.yaml_content) > 200 else result.yaml_content)
                
                if result.generated_files:
                    print(f"📁 保存位置: {result.generated_files[0]}")
            else:
                print(f"❌ 生成失败: {result.error_message}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
🚀 ChaosBlade YAML 生成器 - 命令行工具

📖 使用方法:
  python chat.py "自然语言描述"           # 直接生成YAML
  python chat.py --interactive           # 交互式模式
  python chat.py --test                  # 运行测试
  python chat.py --demo                  # 演示模式
  python chat.py --generate <文件>        # 从文件批量生成
  python chat.py --batch [指令...]        # 批量模式

🎯 支持的作用域:
  - node: Kubernetes节点
  - pod: Kubernetes Pod
  - container: 容器
  - host: 主机
  - cri: 容器运行时接口

🎯 支持的目标:
  - file: 文件操作
  - network: 网络实验
  - cpu: CPU负载
  - mem: 内存负载
  - process: 进程控制
  - disk: 磁盘操作
  - script: 脚本执行
  - systemd: 系统服务

📝 示例指令:
  python chat.py "在节点 node-1 上添加文件 /root/test.log，内容为 hello world"
  python chat.py "在 Pod nginx-pod 上创建网络延迟，延迟 100ms"
  python chat.py "在容器 app-container 中创建 CPU 负载，负载 60%"
  python chat.py "在主机 192.168.1.100 上停止 nginx 服务"

📚 更多帮助:
  查看文档: COMMAND_LINE_YAML_GENERATION_GUIDE.md
  快速参考: QUICK_REFERENCE.md
"""
        print(help_text)


def main():
    """主函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    cli = ChaosBladeCLI()
    cli.run(sys.argv[1:])


if __name__ == "__main__":
    main()
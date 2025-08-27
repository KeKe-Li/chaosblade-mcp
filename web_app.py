from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chaosblade import quick_generate, batch_generate, create_parser, create_generator

app = Flask(__name__)
CORS(app)

# 配置
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['GENERATED_DIR'] = 'generated-yamls'

# 确保生成目录存在
os.makedirs(app.config['GENERATED_DIR'], exist_ok=True)

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_yaml():
    """生成YAML API"""
    try:
        data = request.get_json()
        instruction = data.get('instruction', '').strip()
        
        if not instruction:
            return jsonify({
                'success': False,
                'error': '请输入指令'
            }), 400
        
        # 生成YAML
        yaml_content = quick_generate(instruction)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'generated_{timestamp}.yaml'
        filepath = os.path.join(app.config['GENERATED_DIR'], filename)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        return jsonify({
            'success': True,
            'yaml_content': yaml_content,
            'filename': filename,
            'filepath': filepath,
            'timestamp': timestamp
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/batch-generate', methods=['POST'])
def batch_generate_yaml():
    """批量生成YAML API"""
    try:
        data = request.get_json()
        instructions = data.get('instructions', [])
        
        if not instructions:
            return jsonify({
                'success': False,
                'error': '请输入指令列表'
            }), 400
        
        # 批量生成
        results = batch_generate(instructions, app.config['GENERATED_DIR'])
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """获取模板列表"""
    templates = [
        {
            'name': '节点文件添加',
            'instruction': '在节点 node-1 上添加文件 /root/test.log，内容为 hello world',
            'description': '在指定节点上创建文件'
        },
        {
            'name': 'Pod网络延迟',
            'instruction': '在 Pod nginx-pod 上创建网络延迟，延迟 100ms',
            'description': '为指定Pod添加网络延迟'
        },
        {
            'name': '容器CPU负载',
            'instruction': '在容器 app-container 中创建 CPU 负载，负载 60%',
            'description': '为指定容器添加CPU负载'
        },
        {
            'name': '主机进程停止',
            'instruction': '在主机 192.168.1.100 上停止 nginx 服务',
            'description': '停止指定主机上的进程'
        },
        {
            'name': '内存负载',
            'instruction': '在节点 node-2 上创建内存负载，负载 80%',
            'description': '为指定节点添加内存负载'
        },
        {
            'name': '磁盘填充',
            'instruction': '在节点 node-3 上填充磁盘，路径 /tmp/test，大小 1GB',
            'description': '在指定节点上填充磁盘空间'
        }
    ]
    
    return jsonify({
        'success': True,
        'templates': templates
    })

@app.route('/api/files', methods=['GET'])
def get_generated_files():
    """获取已生成的文件列表"""
    try:
        files = []
        for filename in os.listdir(app.config['GENERATED_DIR']):
            if filename.endswith('.yaml'):
                filepath = os.path.join(app.config['GENERATED_DIR'], filename)
                stat = os.stat(filepath)
                files.append({
                    'name': filename,
                    'path': filepath,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # 按修改时间排序
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'success': True,
            'files': files
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/files/<filename>', methods=['GET'])
def get_file_content(filename):
    """获取文件内容"""
    try:
        filepath = os.path.join(app.config['GENERATED_DIR'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'content': content,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    import os
    print("🚀 ChaosBlade Web Interface starting...")
    print("📱 Access at: http://localhost:5001")
    
    # 检查是否在容器环境中运行
    is_container = os.path.exists('/.dockerenv') or os.environ.get('FLASK_ENV') == 'production'
    
    if is_container:
        # 容器环境使用 gunicorn (通过 CMD 启动)
        print("🐳 Running in container mode with gunicorn")
    else:
        # 开发环境使用 Flask 开发服务器
        app.run(debug=True, host='0.0.0.0', port=5001)
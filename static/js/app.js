// ChaosBlade Web Interface JavaScript

class ChaosBladeApp {
    constructor() {
        this.currentYAML = '';
        this.currentFilename = '';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadTemplates();
        this.loadFiles();
    }

    bindEvents() {
        // 生成按钮
        document.getElementById('generateBtn').addEventListener('click', () => {
            this.generateYAML();
        });

        // 清空按钮
        document.getElementById('clearBtn').addEventListener('click', () => {
            this.clearInput();
        });

        // 批量生成按钮
        document.getElementById('batchBtn').addEventListener('click', () => {
            this.showBatchModal();
        });

        // 批量生成确认按钮
        document.getElementById('batchGenerateBtn').addEventListener('click', () => {
            this.batchGenerate();
        });

        // 复制按钮
        document.getElementById('copyBtn').addEventListener('click', () => {
            this.copyToClipboard();
        });

        // 下载按钮
        document.getElementById('downloadBtn').addEventListener('click', () => {
            this.downloadYAML();
        });

        // 新建按钮
        document.getElementById('newBtn').addEventListener('click', () => {
            this.createNew();
        });

        // 输入框回车事件
        document.getElementById('instructionInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.generateYAML();
            }
        });
    }

    async generateYAML() {
        const instruction = document.getElementById('instructionInput').value.trim();
        
        if (!instruction) {
            this.showError('请输入指令');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ instruction })
            });

            const result = await response.json();

            if (result.success) {
                this.currentYAML = result.yaml_content;
                this.currentFilename = result.filename;
                this.showResult(result.yaml_content);
                this.showSuccess('YAML 生成成功！');
                this.loadFiles(); // 刷新文件列表
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    async batchGenerate() {
        const instructionsText = document.getElementById('batchInstructions').value.trim();
        
        if (!instructionsText) {
            this.showError('请输入指令列表');
            return;
        }

        const instructions = instructionsText.split('\n').filter(i => i.trim());
        
        if (instructions.length === 0) {
            this.showError('请输入有效的指令列表');
            return;
        }

        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('batchModal'));
        modal.hide();

        this.showLoading(true);

        try {
            const response = await fetch('/api/batch-generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ instructions })
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccess(`批量生成成功！共生成 ${result.total} 个 YAML 文件`);
                this.loadFiles(); // 刷新文件列表
                
                // 显示最后一个结果
                if (result.results.length > 0) {
                    const lastResult = result.results[result.results.length - 1];
                    if (lastResult.success) {
                        this.currentYAML = lastResult.yaml_content;
                        this.currentFilename = lastResult.filename;
                        this.showResult(lastResult.yaml_content);
                    }
                }
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    async loadTemplates() {
        try {
            const response = await fetch('/api/templates');
            const result = await response.json();

            if (result.success) {
                this.renderTemplates(result.templates);
            }
        } catch (error) {
            console.error('加载模板失败:', error);
        }
    }

    renderTemplates(templates) {
        const templateList = document.getElementById('templateList');
        templateList.innerHTML = '';

        templates.forEach(template => {
            const templateItem = document.createElement('div');
            templateItem.className = 'template-item';
            templateItem.innerHTML = `
                <h6>${template.name}</h6>
                <p>${template.description}</p>
            `;
            templateItem.addEventListener('click', () => {
                this.useTemplate(template.instruction);
            });
            templateList.appendChild(templateItem);
        });
    }

    useTemplate(instruction) {
        document.getElementById('instructionInput').value = instruction;
        document.getElementById('instructionInput').focus();
    }

    async loadFiles() {
        try {
            const response = await fetch('/api/files');
            const result = await response.json();

            if (result.success) {
                this.renderFiles(result.files);
            }
        } catch (error) {
            console.error('加载文件列表失败:', error);
        }
    }

    renderFiles(files) {
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = '';

        files.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-name">${file.name}</div>
                <div class="file-meta">
                    ${this.formatFileSize(file.size)} • ${this.formatDate(file.modified)}
                </div>
            `;
            fileItem.addEventListener('click', () => {
                this.loadFileContent(file.name);
            });
            fileList.appendChild(fileItem);
        });
    }

    async loadFileContent(filename) {
        try {
            const response = await fetch(`/api/files/${filename}`);
            const result = await response.json();

            if (result.success) {
                this.currentYAML = result.content;
                this.currentFilename = filename;
                this.showResult(result.content);
                this.showSuccess('文件加载成功');
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('加载文件失败: ' + error.message);
        }
    }

    showResult(yamlContent) {
        const resultContainer = document.getElementById('resultContainer');
        const yamlContentElement = document.getElementById('yamlContent');
        
        yamlContentElement.textContent = yamlContent;
        resultContainer.style.display = 'block';
        
        // 重新渲染语法高亮
        Prism.highlightElement(yamlContentElement);
        
        // 滚动到结果区域
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }

    showLoading(show) {
        const loadingContainer = document.getElementById('loadingContainer');
        const generateBtn = document.getElementById('generateBtn');
        
        if (show) {
            loadingContainer.style.display = 'block';
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 生成中...';
        } else {
            loadingContainer.style.display = 'none';
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic"></i> 生成 YAML';
        }
    }

    showError(message) {
        const errorAlert = document.getElementById('errorAlert');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorAlert.style.display = 'block';
        
        // 3秒后自动隐藏
        setTimeout(() => {
            errorAlert.style.display = 'none';
        }, 3000);
    }

    showSuccess(message) {
        const successToast = document.getElementById('successToast');
        const successMessage = document.getElementById('successMessage');
        
        successMessage.textContent = message;
        
        const toast = new bootstrap.Toast(successToast);
        toast.show();
    }

    clearInput() {
        document.getElementById('instructionInput').value = '';
        document.getElementById('instructionInput').focus();
    }

    showBatchModal() {
        const modal = new bootstrap.Modal(document.getElementById('batchModal'));
        modal.show();
    }

    copyToClipboard() {
        if (!this.currentYAML) {
            this.showError('没有可复制的内容');
            return;
        }

        navigator.clipboard.writeText(this.currentYAML).then(() => {
            this.showSuccess('已复制到剪贴板');
        }).catch(err => {
            this.showError('复制失败: ' + err.message);
        });
    }

    downloadYAML() {
        if (!this.currentYAML) {
            this.showError('没有可下载的内容');
            return;
        }

        const blob = new Blob([this.currentYAML], { type: 'text/yaml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = this.currentFilename || 'chaosblade.yaml';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showSuccess('文件下载成功');
    }

    createNew() {
        this.currentYAML = '';
        this.currentFilename = '';
        document.getElementById('resultContainer').style.display = 'none';
        document.getElementById('instructionInput').value = '';
        document.getElementById('instructionInput').focus();
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new ChaosBladeApp();
});

// 添加一些实用功能
function showTooltip(element, message) {
    const tooltip = new bootstrap.Tooltip(element, {
        title: message,
        placement: 'top',
        trigger: 'hover'
    });
    return tooltip;
}

// 添加键盘快捷键
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K: 聚焦到输入框
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('instructionInput').focus();
    }
    
    // Ctrl/Cmd + N: 新建
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        document.getElementById('newBtn').click();
    }
    
    // Ctrl/Cmd + D: 下载
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        document.getElementById('downloadBtn').click();
    }
    
    // Escape: 关闭模态框
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
});
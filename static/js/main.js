// 拼豆图案生成系统 - 前端交互逻辑

let currentFileId = null;
let currentPatternId = null;
let currentPattern = null;
let stepStatus = {}; // 存储每个步骤的状态
let isExecuting = false; // 是否正在执行
let shouldStopExecution = false; // 是否应该停止执行
let executionController = null; // 执行控制器(用于AbortController)

// DOM元素
const uploadArea = document.querySelector('.upload-area') || createUploadArea();
const fileInput = document.getElementById('fileInput') || createFileInput();
const processBtn = document.getElementById('processBtn') || null;
const previewArea = document.querySelector('.preview-area') || null;

// 创建上传区域（如果不存在）
function createUploadArea() {
    const area = document.createElement('div');
    area.className = 'upload-area';
    area.innerHTML = `
        <p>点击或拖拽图片到此处上传</p>
        <input type="file" id="fileInput" accept="image/*" style="display: none;">
    `;
    document.body.appendChild(area);
    return area;
}

// 创建文件输入（如果不存在）
function createFileInput() {
    const input = document.createElement('input');
    input.type = 'file';
    input.id = 'fileInput';
    input.accept = 'image/*';
    input.style.display = 'none';
    document.body.appendChild(input);
    return input;
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeUI();
    setupEventListeners();
});

// 初始化UI
function initializeUI() {
    const app = document.getElementById('app') || document.body;
    
    if (!document.querySelector('.container')) {
        app.innerHTML = `
            <div class="container">
                <h1>拼豆图案生成系统</h1>
                
                <div class="section">
                    <h2>1. 上传图片</h2>
                    <div class="upload-area" id="uploadArea">
                        <p>点击或拖拽图片到此处上传</p>
                        <input type="file" id="fileInput" accept="image/*" style="display: none;">
                    </div>
                </div>
                
                <div class="section">
                    <h2>2. 设置参数</h2>
                    <div class="controls" id="controls">
                        <div class="control-group">
                            <label>最大尺寸 (拼豆数量) 
                                <span class="range-value" id="maxDimensionValue">100</span>
                            </label>
                            <input type="range" id="maxDimension" min="20" max="200" value="100" step="5">
                        </div>
                        
                        <div class="control-group">
                            <label>目标颜色数量 
                                <span class="range-value" id="targetColorsValue">20</span>
                            </label>
                            <input type="range" id="targetColors" min="0" max="100" value="20" step="1">
                        </div>
                        
                        <div class="control-group">
                            <label>
                                <input type="checkbox" id="disableKMeans"> 不进行K-means（保留原图颜色细节）
                            </label>
                        </div>
                        
                        <div class="control-group">
                            <label>降噪强度 
                                <span class="range-value" id="denoiseValue">0.5</span>
                            </label>
                            <input type="range" id="denoiseStrength" min="0" max="1" value="0.5" step="0.1">
                        </div>
                        
                        <div class="control-group">
                            <label>对比度 
                                <span class="range-value" id="contrastValue">1.2</span>
                            </label>
                            <input type="range" id="contrastFactor" min="0.5" max="2" value="1.2" step="0.1">
                        </div>
                        
                        <div class="control-group">
                            <label>锐度 
                                <span class="range-value" id="sharpnessValue">1.1</span>
                            </label>
                            <input type="range" id="sharpnessFactor" min="0.5" max="2" value="1.1" step="0.1">
                        </div>
                        
                        <div class="control-group">
                            <label>
                                <input type="checkbox" id="useCustomColors" checked> 使用自定义色板
                            </label>
                        </div>
                        
                        <div class="control-group">
                            <label>颜色匹配模式</label>
                            <select id="colorMatchMode">
                                <option value="nearest">标准（最近色）</option>
                                <option value="detail">细节优先（亮度权重）</option>
                                <option value="dither_fs">抖动（Floyd-Steinberg）</option>
                                <option value="dither_atkinson">抖动（Atkinson）</option>
                            </select>
                        </div>
                        
                        <div class="control-group" style="grid-column: 1 / -1;">
                            <label>
                                <input type="checkbox" id="useNanoBanana"> 使用Nano Banana AI转换（先转换为拼豆风格）
                            </label>
                            <div id="nanoBananaSettings" class="hidden" style="margin-top: 10px; padding: 10px; background: #f0f0f0; border-radius: 5px;">
                                <div class="control-group">
                                    <label>提示词</label>
                                    <input type="text" id="nanoBananaPrompt" value="拼豆风格，像素艺术，清晰的色块" style="width: 100%;">
                                </div>
                                <div class="control-group">
                                    <label>模型</label>
                                    <select id="nanoBananaModel" style="width: 100%;">
                                        <option value="nano-banana-fast">nano-banana-fast (快速)</option>
                                        <option value="nano-banana">nano-banana (标准)</option>
                                        <option value="nano-banana-pro">nano-banana-pro (专业)</option>
                                    </select>
                                </div>
                                <div class="control-group">
                                    <label>图像大小</label>
                                    <select id="nanoBananaImageSize" style="width: 100%;">
                                        <option value="1K">1K</option>
                                        <option value="2K">2K</option>
                                        <option value="4K">4K</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="button-group">
                        <button class="btn btn-primary" id="processBtn" disabled>生成图案</button>
                    </div>
                </div>
                
                <div class="section hidden" id="resultSection">
                    <h2>3. 查看结果</h2>
                    <div class="stats" id="stats"></div>
                    <div class="preview-area" id="previewArea"></div>
                    <div class="export-options">
                        <button class="btn btn-success" id="exportJsonBtn">导出JSON</button>
                        <button class="btn btn-success" id="exportCsvBtn">导出CSV</button>
                        <button class="btn btn-success" id="exportPngBtn">导出PNG</button>
                        <button class="btn btn-secondary" id="printPreviewBtn">打印预览</button>
                        <button class="btn btn-secondary" id="printBtn">生成PDF</button>
                    </div>
                    <div class="print-preview hidden" id="printPreviewArea"></div>
                </div>
            </div>
        `;
    }
    
    setupEventListeners();
}

// 设置事件监听
function setupEventListeners() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const processBtn = document.getElementById('processBtn');
    
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    if (processBtn) {
        processBtn.addEventListener('click', handleProcess);
    }
    
    // 分步骤按钮
    setupStepButtons();
    
    // 范围滑块事件
    setupRangeInputs();
    setupKMeansToggle();
    
    // Nano Banana设置
    setupNanoBananaToggle();
    setupNanoBananaConfig();
    
    // 实物效果图预设风格
    const renderStylePreset = document.getElementById('renderStylePreset');
    if (renderStylePreset) {
        renderStylePreset.addEventListener('change', updateRenderPrompt);
    }
    
    // 尺寸类型选择
    const nanoBananaSizeType = document.getElementById('nanoBananaSizeType');
    if (nanoBananaSizeType) {
        nanoBananaSizeType.addEventListener('change', updatePromptBySizeType);
        // 初始化提示词
        updatePromptBySizeType();
    }
    
    // 预处理预设选择
    const preprocessPreset = document.getElementById('preprocessPreset');
    if (preprocessPreset) {
        preprocessPreset.addEventListener('change', applyPreprocessPreset);
    }
    
    // 拼豆大小选择器
    const beadSizeSelect = document.getElementById('beadSize');
    if (beadSizeSelect) {
        beadSizeSelect.addEventListener('change', updateBeadSizeMaxDimension);
        // 初始化时更新一次
        updateBeadSizeMaxDimension();
    }
    
    // 当选择使用Nano Banana结果时，建议使用轻度预处理
    const useNanoBananaResult = document.getElementById('useNanoBananaResult');
    if (useNanoBananaResult && preprocessPreset) {
        useNanoBananaResult.addEventListener('change', function() {
            if (this.checked && preprocessPreset.value === 'standard') {
                // 如果当前是标准预设，提示用户可以使用轻度预处理
                const presetSelect = preprocessPreset;
                // 不自动切换，只提示（让用户自己选择）
                console.log('提示：使用Nano Banana结果时，建议选择"轻度预处理"预设');
            }
        });
    }
    
    // 导出按钮
    setupExportButtons();
}

    // 设置分步骤按钮（现在只有刷新按钮）
function setupStepButtons() {
    // 步骤1: Nano Banana
    const refreshNanoBananaBtn = document.getElementById('refreshNanoBananaBtn');
    if (refreshNanoBananaBtn) {
        refreshNanoBananaBtn.addEventListener('click', runNanoBanana);
    }
    
    // 步骤2: 预处理
    const refreshPreprocessBtn = document.getElementById('refreshPreprocessBtn');
    if (refreshPreprocessBtn) {
        refreshPreprocessBtn.addEventListener('click', runPreprocess);
    }
    
    // 步骤3: 生成图案
    const refreshGeneratePatternBtn = document.getElementById('refreshGeneratePatternBtn');
    if (refreshGeneratePatternBtn) {
        refreshGeneratePatternBtn.addEventListener('click', runGeneratePattern);
    }
    
    // 步骤4: 生成实物效果图
    const refreshGenerateRenderBtn = document.getElementById('refreshGenerateRenderBtn');
    if (refreshGenerateRenderBtn) {
        refreshGenerateRenderBtn.addEventListener('click', runGenerateRender);
    }
    
    // Nano Banana最大尺寸滑块
    const nanoBananaMaxDimension = document.getElementById('nanoBananaMaxDimension');
    const nanoBananaMaxDimensionValue = document.getElementById('nanoBananaMaxDimensionValue');
    if (nanoBananaMaxDimension && nanoBananaMaxDimensionValue) {
        nanoBananaMaxDimension.addEventListener('input', (e) => {
            nanoBananaMaxDimensionValue.textContent = e.target.value;
        });
    }
    
    // 一键执行全部步骤按钮
    const executeAllBtn = document.getElementById('executeAllBtn');
    const stopExecutionBtn = document.getElementById('stopExecutionBtn');
    const refreshAllBtn = document.getElementById('refreshAllBtn');
    
    if (executeAllBtn) {
        executeAllBtn.addEventListener('click', executeAllSteps);
    }
    // 终止按钮的事件监听在DOMContentLoaded中设置（因为按钮在进度条区域）
    if (refreshAllBtn) {
        refreshAllBtn.addEventListener('click', refreshAllSteps);
    }
}

// 设置Nano Banana选项
function setupNanoBananaToggle() {
    const useNanoBanana = document.getElementById('useNanoBanana');
    const nanoBananaSettings = document.getElementById('nanoBananaSettings');
    
    if (useNanoBanana && nanoBananaSettings) {
        useNanoBanana.addEventListener('change', (e) => {
            if (e.target.checked) {
                nanoBananaSettings.classList.remove('hidden');
            } else {
                nanoBananaSettings.classList.add('hidden');
            }
        });
    }
}

// 根据拼豆大小更新最大尺寸范围
function updateBeadSizeMaxDimension() {
    const beadSizeSelect = document.getElementById('beadSize');
    const maxDimensionInput = document.getElementById('maxDimension');
    const maxDimensionValue = document.getElementById('maxDimensionValue');
    
    if (!beadSizeSelect || !maxDimensionInput || !maxDimensionValue) return;
    
    const beadSize = parseFloat(beadSizeSelect.value);
    
    if (beadSize === 2.6) {
        // 2.6mm小拼豆：更大的范围
        maxDimensionInput.min = 50;
        maxDimensionInput.max = 500;
        maxDimensionInput.step = 10;
        if (parseInt(maxDimensionInput.value) < 200) {
            maxDimensionInput.value = 200; // 如果当前值小于200，设置为200
            maxDimensionValue.textContent = '200';
        }
    } else {
        // 5.0mm标准拼豆：较小的范围
        maxDimensionInput.min = 20;
        maxDimensionInput.max = 200;
        maxDimensionInput.step = 5;
        if (parseInt(maxDimensionInput.value) > 200) {
            maxDimensionInput.value = 100; // 如果当前值大于200，设置为100
            maxDimensionValue.textContent = '100';
        }
    }
    
    // 更新显示值
    maxDimensionValue.textContent = maxDimensionInput.value;
}

// 应用预处理预设
function applyPreprocessPreset() {
    const preset = document.getElementById('preprocessPreset').value;
    const beadSize = parseFloat(document.getElementById('beadSize').value);
    
    // 根据拼豆大小调整默认最大尺寸
    const maxDimensionFor26mm = {
        'light': 300,
        'standard': 200,
        'heavy': 150
    };
    const maxDimensionFor5mm = {
        'light': 150,
        'standard': 100,
        'heavy': 80
    };
    
    const presets = {
        'light': {
            maxDimension: beadSize === 2.6 ? maxDimensionFor26mm.light : maxDimensionFor5mm.light,
            targetColors: 30,
            denoiseStrength: 0.2,
            contrastFactor: 1.05,
            sharpnessFactor: 1.0
        },
        'standard': {
            maxDimension: beadSize === 2.6 ? maxDimensionFor26mm.standard : maxDimensionFor5mm.standard,
            targetColors: 20,
            denoiseStrength: 0.5,
            contrastFactor: 1.2,
            sharpnessFactor: 1.1
        },
        'heavy': {
            maxDimension: beadSize === 2.6 ? maxDimensionFor26mm.heavy : maxDimensionFor5mm.heavy,
            targetColors: 15,
            denoiseStrength: 0.8,
            contrastFactor: 1.5,
            sharpnessFactor: 1.3
        },
        'custom': null // 自定义时不自动更新
    };
    
    if (preset !== 'custom' && presets[preset]) {
        const params = presets[preset];
        
        // 更新滑块值（先更新范围，再设置值）
        updateBeadSizeMaxDimension(); // 确保范围正确
        document.getElementById('maxDimension').value = params.maxDimension;
        document.getElementById('targetColors').value = params.targetColors;
        document.getElementById('denoiseStrength').value = params.denoiseStrength;
        document.getElementById('contrastFactor').value = params.contrastFactor;
        document.getElementById('sharpnessFactor').value = params.sharpnessFactor;
        
        // 更新显示值
        document.getElementById('maxDimensionValue').textContent = params.maxDimension;
        document.getElementById('targetColorsValue').textContent = params.targetColors;
        document.getElementById('denoiseValue').textContent = params.denoiseStrength.toFixed(1);
        document.getElementById('contrastValue').textContent = params.contrastFactor.toFixed(1);
        document.getElementById('sharpnessValue').textContent = params.sharpnessFactor.toFixed(1);
        updateKMeansToggle();
    }
}

// 根据尺寸类型更新提示词
function updatePromptBySizeType() {
    const sizeType = document.getElementById('nanoBananaSizeType').value;
    const promptInput = document.getElementById('nanoBananaPrompt');
    
    if (!promptInput) return;
    
    // 尺寸描述映射
    const sizeDescriptions = {
        'small': '小尺寸像素图，控制在有限像素内尽可能还原角色细节，适合拼豆制作的小尺寸像素艺术，迷你拼豆',
        'medium': '中等尺寸像素图，在合适的像素范围内还原角色细节，适合标准拼豆制作的像素艺术',
        'large': '大尺寸像素图，在较大的像素范围内精细还原角色细节，适合大型拼豆制作的像素艺术',
        'xlarge': '超大尺寸像素图，在最大像素范围内高度还原角色细节，适合巨型拼豆制作的像素艺术',
        'custom': '' // 自定义时不清除，让用户自己编辑
    };
    
    // 基础提示词（移除尺寸相关的部分）
    const basePrompt = '像素艺术风格，一格一格的色块，清晰的像素点阵，无网格线，纯色块拼接，像素化处理，马赛克风格，8位像素艺术，移除所有背景，移除所有文字和字幕，只保留角色主体，角色抠图，纯白色背景';
    
    if (sizeType === 'custom') {
        // 自定义模式：不自动更新，保持用户当前输入
        return;
    } else {
        // 根据尺寸类型更新提示词
        const sizeDesc = sizeDescriptions[sizeType];
        promptInput.value = basePrompt + '，' + sizeDesc;
    }
}

// 更新实物效果图提示词（根据预设风格）
function updateRenderPrompt() {
    const presetSelect = document.getElementById('renderStylePreset');
    const promptInput = document.getElementById('renderPrompt');
    
    if (!presetSelect || !promptInput) return;
    
    const preset = presetSelect.value;
    const prompts = {
        'custom': promptInput.value, // 保持当前值
        'keychain': '拼豆钥匙扣实物效果图，真实的拼豆工艺品，钥匙扣配件，金属扣环，近距离拍摄，高清晰度，专业产品摄影，自然光线，背景虚化，细节清晰，产品展示风格',
        'ornament': '拼豆摆件装饰品实物效果图，真实的拼豆工艺品，桌面摆件，装饰品，近距离拍摄，高清晰度，专业摄影，自然光线，温馨场景，细节清晰',
        'keychain_hanging': '拼豆钥匙扣悬挂展示效果图，真实的拼豆工艺品，钥匙扣配件，悬挂状态，动态展示，近距离拍摄，高清晰度，专业产品摄影，自然光线，背景虚化',
        'desk_ornament': '拼豆桌面摆件实物效果图，真实的拼豆工艺品，办公桌装饰，桌面摆件，近距离拍摄，高清晰度，专业摄影，自然光线，温馨办公场景，细节清晰',
        'wall_art': '拼豆墙面装饰实物效果图，真实的拼豆工艺品，墙面挂件，装饰画，近距离拍摄，高清晰度，专业摄影，自然光线，家居场景，细节清晰',
        'product_photo': '拼豆产品摄影效果图，真实的拼豆工艺品，专业产品摄影，白色背景，高清晰度，商业级拍摄，均匀光线，细节清晰，产品展示风格',
        'lifestyle': '拼豆生活场景效果图，真实的拼豆工艺品，日常生活场景，自然摆放，近距离拍摄，高清晰度，专业摄影，自然光线，温馨氛围，细节清晰'
    };
    
    if (preset !== 'custom' && prompts[preset]) {
        promptInput.value = prompts[preset];
    }
}

// 设置Nano Banana配置保存
function setupNanoBananaConfig() {
    const saveConfigBtn = document.getElementById('saveNanoBananaConfig');
    
    if (saveConfigBtn) {
        saveConfigBtn.addEventListener('click', async () => {
            const apiKey = document.getElementById('nanoBananaApiKey').value;
            const baseUrl = document.getElementById('nanoBananaBaseUrl').value || 'https://api.grsai.com';
            const proxy = document.getElementById('nanoBananaProxy')?.value || '';
            
            if (!apiKey) {
                showError('请输入API密钥');
                return;
            }
            
            try {
                showLoading('正在保存配置...');
                
                const configData = {
                    api_key: apiKey,
                    base_url: baseUrl,
                    model: 'nano-banana-fast',
                    image_size: '1K'
                };
                
                // 如果提供了代理，添加到配置
                if (proxy.trim()) {
                    configData.proxy = proxy.trim();
                }
                
                const response = await fetch('/api/config/nano-banana', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(configData)
                });
                
                if (!response.ok) {
                    throw new Error('保存配置失败');
                }
                
                showSuccess('配置保存成功！');
                localStorage.setItem('nanoBananaConfigSaved', 'true');
                
                // 自动收起配置界面
                setTimeout(() => {
                    const content = document.getElementById('nanoBananaConfigContent');
                    const icon = document.getElementById('configToggleIcon');
                    if (content && !content.classList.contains('collapsed')) {
                        content.classList.add('collapsed');
                        if (icon) icon.textContent = '▶';
                    }
                }, 500); // 延迟500ms收起，让用户看到成功提示
            } catch (error) {
                showError('保存配置失败: ' + error.message);
            }
        });
    }
}

// 设置范围输入
function setupRangeInputs() {
    const ranges = {
        'maxDimension': 'maxDimensionValue',
        'targetColors': 'targetColorsValue',
        'denoiseStrength': 'denoiseValue',
        'contrastFactor': 'contrastValue',
        'sharpnessFactor': 'sharpnessValue',
        'nanoBananaMaxDimension': 'nanoBananaMaxDimensionValue'
    };
    
    Object.entries(ranges).forEach(([inputId, outputId]) => {
        const input = document.getElementById(inputId);
        const output = document.getElementById(outputId);
        if (input && output) {
            // 设置初始值
            if (output) {
                output.textContent = input.value;
            }
            input.addEventListener('input', (e) => {
                if (output) {
                    output.textContent = e.target.value;
                }
            });
        }
    });
}

function updateKMeansToggle() {
    const disableKMeans = document.getElementById('disableKMeans');
    const targetColors = document.getElementById('targetColors');
    const targetColorsValue = document.getElementById('targetColorsValue');
    
    if (!disableKMeans || !targetColors || !targetColorsValue) return;
    
    if (disableKMeans.checked) {
        if (targetColors.value !== '0') {
            targetColors.dataset.prevValue = targetColors.value;
        }
        targetColors.value = '0';
        targetColors.disabled = true;
        targetColorsValue.textContent = '0';
    } else {
        const restored = targetColors.dataset.prevValue || targetColors.value || '20';
        targetColors.value = restored;
        targetColors.disabled = false;
        targetColorsValue.textContent = restored;
    }
}

function setupKMeansToggle() {
    const disableKMeans = document.getElementById('disableKMeans');
    if (!disableKMeans) return;
    
    disableKMeans.addEventListener('change', updateKMeansToggle);
    updateKMeansToggle();
}

function getTargetColorsValue() {
    const targetColors = document.getElementById('targetColors');
    const disableKMeans = document.getElementById('disableKMeans');
    
    if (!targetColors) return '0';
    if (disableKMeans && disableKMeans.checked) return '0';
    
    return targetColors.value;
}

function getMatchModeValue() {
    const matchMode = document.getElementById('colorMatchMode');
    if (!matchMode) return 'nearest';
    return matchMode.value || 'nearest';
}

// 设置导出按钮
function setupExportButtons() {
    const exportJsonBtn = document.getElementById('exportJsonBtn');
    const exportCsvBtn = document.getElementById('exportCsvBtn');
    const exportPngBtn = document.getElementById('exportPngBtn');
    const exportTechnicalSheetBtn = document.getElementById('exportTechnicalSheetBtn');
    const printPreviewBtn = document.getElementById('printPreviewBtn');
    const printBtn = document.getElementById('printBtn');

    // 使用 onclick 属性，避免重复绑定问题
    if (exportJsonBtn) {
        exportJsonBtn.onclick = () => exportPattern('json');
    }
    if (exportCsvBtn) {
        exportCsvBtn.onclick = () => exportPattern('csv');
    }
    if (exportPngBtn) {
        exportPngBtn.onclick = () => exportPattern('png');
    }
    if (exportTechnicalSheetBtn) {
        exportTechnicalSheetBtn.onclick = exportTechnicalSheet;
    }
    if (printPreviewBtn) {
        printPreviewBtn.onclick = showPrintPreview;
    }
    if (printBtn) {
        printBtn.onclick = generatePrint;
        console.log('PDF按钮事件已绑定:', printBtn);
    }
}

// 拖拽处理
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
}

// 处理文件上传
async function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showError('请上传图片文件');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showLoading('正在上传图片...');
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            // 尝试获取详细错误信息
            let errorMsg = '上传失败';
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMsg = errorData.detail;
                }
            } catch (e) {
                errorMsg = `上传失败 (HTTP ${response.status})`;
            }
            throw new Error(errorMsg);
        }
        
        const data = await response.json();
        currentFileId = data.file_id;
        
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.innerHTML = `
                <p style="color: #059669; font-weight: 700; font-size: 18px; margin-bottom: 12px;">✓ 图片上传成功！</p>
                <img src="${data.image_url}" alt="上传的图片" style="max-width: 100%; max-height: 300px; display: block; margin: 0 auto 12px auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                <p style="color: #1f2937; font-weight: 500;">文件名: ${data.filename}</p>
                <p style="color: #1f2937; font-weight: 500;">尺寸: ${data.width} × ${data.height} 像素</p>
                <p style="color: #5a67d8; margin-top: 12px; font-weight: 600;">点击下方"一键执行全部步骤"开始处理</p>
                <input type="file" id="fileInput" accept="image/*" style="display: none;">
            `;
            const newFileInput = uploadArea.querySelector('#fileInput');
            if (newFileInput) {
                newFileInput.addEventListener('change', handleFileSelect);
            }
        }
        
        // 启用步骤按钮
        enableStepButtons();
        showSuccess('图片上传成功！可以开始处理步骤了');
        
        // 显示一键执行按钮
        const autoExecuteGroup = document.getElementById('autoExecuteGroup');
        if (autoExecuteGroup) {
            autoExecuteGroup.style.display = 'flex';
            autoExecuteGroup.style.gap = '10px';
        }
        
        // 清除之前的结果
        resetSteps();
    } catch (error) {
        showError('上传失败: ' + error.message);
    }
}

// 处理图像生成图案
async function handleProcess() {
    
    if (!currentFileId) {
        showError('请先上传图片');
        return;
    }
    
    const formData = new FormData();
    formData.append('file_id', currentFileId);
    formData.append('max_dimension', document.getElementById('maxDimension').value);
    formData.append('target_colors', getTargetColorsValue());
    formData.append('use_custom', document.getElementById('useCustomColors').checked);
    formData.append('match_mode', getMatchModeValue());
    formData.append('denoise_strength', document.getElementById('denoiseStrength').value);
    formData.append('contrast_factor', document.getElementById('contrastFactor').value);
    formData.append('sharpness_factor', document.getElementById('sharpnessFactor').value);
    
    // Nano Banana参数
    const useNanoBanana = document.getElementById('useNanoBanana')?.checked || false;
    // FastAPI可以直接接收布尔值
    formData.append('use_nano_banana', useNanoBanana);
    console.log('Nano Banana选项:', useNanoBanana); // 调试日志
    if (useNanoBanana) {
        formData.append('nano_banana_prompt', document.getElementById('nanoBananaPrompt')?.value || '像素艺术风格，移除背景，移除文字，只保留角色，小尺寸像素图');
        formData.append('nano_banana_model', document.getElementById('nanoBananaModel')?.value || 'nano-banana-fast');
        formData.append('nano_banana_image_size', document.getElementById('nanoBananaImageSize')?.value || '1K');
        console.log('Nano Banana参数已添加:', {
            prompt: document.getElementById('nanoBananaPrompt')?.value,
            model: document.getElementById('nanoBananaModel')?.value,
            image_size: document.getElementById('nanoBananaImageSize')?.value
        }); // 调试日志
    }
    
    try {
        showLoading('正在处理图像，请稍候...');
        
        const response = await fetch('/api/process', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            // 尝试获取详细错误信息
            let errorMsg = '处理失败';
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMsg = errorData.detail;
                }
            } catch (e) {
                errorMsg = `处理失败 (HTTP ${response.status})`;
            }
            throw new Error(errorMsg);
        }
        
        const data = await response.json();
        currentPatternId = data.pattern_id;
        currentPattern = data;
        
        displayResult(data);
        showSuccess('图案生成成功！');
    } catch (error) {
        showError('处理失败: ' + error.message);
    }
}

// 显示结果
function displayResult(data) {
    const resultSection = document.getElementById('resultSection');
    const statsDiv = document.getElementById('stats');
    const previewArea = document.getElementById('previewArea');
    
    resultSection.classList.remove('hidden');
    
    // 显示统计信息
    statsDiv.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${data.width} × ${data.height}</div>
            <div class="stat-label">图案尺寸 (拼豆)</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${data.actual_width_mm.toFixed(1)} × ${data.actual_height_mm.toFixed(1)} mm</div>
            <div class="stat-label">实际尺寸</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${data.statistics.unique_colors}</div>
            <div class="stat-label">使用颜色数</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${data.statistics.total_beads}</div>
            <div class="stat-label">总拼豆数</div>
        </div>
    `;
    
    // 显示预览
    previewArea.innerHTML = `
        <div class="pattern-display">
            <img src="${data.viz_url}" alt="拼豆图案预览" class="pattern-canvas">
        </div>
    `;
    
    // 滚动到结果区域
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

// 导出图案
async function exportPattern(format) {
    if (!currentPatternId) {
        showError('请先生成图案');
        return;
    }
    
    try {
        const response = await fetch(`/api/pattern/${currentPatternId}/export?format=${format}`);
        if (!response.ok) {
            throw new Error('导出失败');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pattern_${currentPatternId}.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);
        
        showSuccess('导出成功！');
    } catch (error) {
        showError('导出失败: ' + error.message);
    }
}

// 导出工程图（含信息面板）
async function exportTechnicalSheet() {
    if (!currentPatternId) {
        showError('请先生成图案');
        return;
    }

    try {
        const params = {
            font_size: 12,
            color_block_size: 24,
            row_height: 32,
            panel_padding: 20,
            margin_from_pattern: 20,
            show_total_count: true,
            show_dimensions: true,
            show_bead_size: true,
            sort_by_count: true,
            exclude_background: true
        };

        const response = await fetch(`/api/pattern/${currentPatternId}/technical-sheet`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });

        if (!response.ok) {
            throw new Error('导出工程图失败');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pattern_${currentPatternId}_technical_sheet.png`;
        a.click();
        window.URL.revokeObjectURL(url);

        showSuccess('工程图导出成功！');
    } catch (error) {
        showError('导出工程图失败: ' + error.message);
    }
}

// 显示打印预览
async function showPrintPreview() {
    if (!currentPatternId) {
        showError('请先生成图案');
        return;
    }
    
    try {
        const params = new URLSearchParams({
            paper_size: 'A4',
            margin_mm: '10.0',
            show_grid: 'true',
            show_labels: 'true'  // 默认显示色号
        });
        
        const response = await fetch(`/api/pattern/${currentPatternId}/print-preview?${params}`);
        if (!response.ok) {
            throw new Error('生成预览失败');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        const previewArea = document.getElementById('printPreviewArea');
        previewArea.innerHTML = `<img src="${url}" alt="打印预览">`;
        previewArea.classList.remove('hidden');
        
        showSuccess('预览生成成功！');
    } catch (error) {
        showError('生成预览失败: ' + error.message);
    }
}

// 生成打印PDF
async function generatePrint() {
    if (!currentPatternId) {
        showError('请先生成图案');
        return;
    }
    
    try {
        const params = {
            paper_size: 'A4',
            margin_mm: 10.0,
            show_grid: true,
            show_labels: true,  // 默认显示色号
            dpi: 300
        };
        
        const response = await fetch(`/api/pattern/${currentPatternId}/print`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });
        
        if (!response.ok) {
            throw new Error('生成PDF失败');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pattern_${currentPatternId}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
        
        showSuccess('PDF生成成功！');
    } catch (error) {
        showError('生成PDF失败: ' + error.message);
    }
}

// 工具函数
function showLoading(message) {
    // 只删除固定位置的错误提示，不要删除步骤区域的错误状态
    const errorDiv = document.getElementById('globalErrorMessage');
    if (errorDiv) errorDiv.remove();
    
    const loading = document.createElement('div');
    loading.className = 'loading';
    loading.textContent = message;
    loading.id = 'loadingMessage';
    
    const container = document.querySelector('.container');
    if (container) {
        const existing = document.getElementById('loadingMessage');
        if (existing) existing.remove();
        container.appendChild(loading);
    }
}

function showError(message) {
    const loading = document.getElementById('loadingMessage');
    if (loading) loading.remove();
    
    // 只删除固定位置的错误提示，不要删除步骤区域的错误状态
    const existingError = document.getElementById('globalErrorMessage');
    if (existingError) existingError.remove();
    
    const error = document.createElement('div');
    error.id = 'globalErrorMessage'; // 添加ID以便后续识别
    error.className = 'error';
    error.textContent = message;
    error.style.position = 'fixed';
    error.style.top = '20px';
    error.style.left = '50%';
    error.style.transform = 'translateX(-50%)';
    error.style.zIndex = '9999';
    error.style.maxWidth = '90%';
    error.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
    
    document.body.appendChild(error);
    
    // 5秒后自动消失
    setTimeout(() => {
        if (error.parentNode) {
            error.remove();
        }
    }, 5000);
}

function showSuccess(message) {
    const loading = document.getElementById('loadingMessage');
    if (loading) loading.remove();
    
    // 可以添加成功提示
    console.log(message);
}

// ============ 分步骤处理功能 ============

// 启用步骤按钮（现在只启用刷新按钮）
function enableStepButtons() {
    const refreshNanoBananaBtn = document.getElementById('refreshNanoBananaBtn');
    const refreshPreprocessBtn = document.getElementById('refreshPreprocessBtn');
    const refreshGeneratePatternBtn = document.getElementById('refreshGeneratePatternBtn');
    const refreshGenerateRenderBtn = document.getElementById('refreshGenerateRenderBtn');
    
    if (refreshNanoBananaBtn) refreshNanoBananaBtn.disabled = false;
    if (refreshPreprocessBtn) refreshPreprocessBtn.disabled = false;
    if (refreshGeneratePatternBtn) refreshGeneratePatternBtn.disabled = false;
    if (refreshGenerateRenderBtn) refreshGenerateRenderBtn.disabled = false;
}

// 重置步骤
function resetSteps() {
    stepStatus = {};
    const stepSections = document.querySelectorAll('.step-section');
    stepSections.forEach(section => {
        section.classList.remove('completed', 'running', 'error');
        const resultDiv = section.querySelector('.step-result');
        if (resultDiv) resultDiv.innerHTML = '';
    });
}

// 步骤1: Nano Banana AI转换
async function runNanoBanana() {
    if (!currentFileId) {
        showError('请先上传图片');
        return;
    }
    
    const stepSection = document.getElementById('stepNanoBanana');
    const resultDiv = document.getElementById('nanoBananaResult');
    const refreshBtn = document.getElementById('refreshNanoBananaBtn');
    
    // 检查元素是否存在
    if (!stepSection || !resultDiv || !refreshBtn) {
        console.error('无法找到步骤元素:', {
            stepSection: !!stepSection,
            resultDiv: !!resultDiv,
            refreshBtn: !!refreshBtn
        });
        showError('页面元素缺失，请刷新页面重试');
        return;
    }
    
    try {
        // 确保步骤区域可见
        console.log('开始执行Nano Banana步骤，步骤区域:', stepSection);
        stepSection.style.display = 'block'; // 使用 block 确保可见
        stepSection.style.visibility = 'visible';
        stepSection.style.opacity = '1';
        stepSection.classList.remove('error', 'completed', 'hidden');
        stepSection.classList.add('running');
        // 确保父元素也可见
        const parent = stepSection.parentElement;
        if (parent) {
            parent.style.display = '';
            parent.style.visibility = 'visible';
        }
        refreshBtn.disabled = true;
        resultDiv.innerHTML = '<div class="loading">正在调用Nano Banana API转换图片...</div>';
        console.log('步骤区域状态 - display:', stepSection.style.display, 'visibility:', stepSection.style.visibility, 'classList:', stepSection.classList.toString());
        
        const formData = new FormData();
        formData.append('file_id', currentFileId);
        formData.append('prompt', document.getElementById('nanoBananaPrompt').value);
        formData.append('model', document.getElementById('nanoBananaModel').value);
        formData.append('image_size', document.getElementById('nanoBananaImageSize').value);
        formData.append('max_dimension', document.getElementById('nanoBananaMaxDimension').value);
        
        const requestOptions = {
            method: 'POST',
            body: formData
        };
        
        // 如果在自动执行模式，添加AbortSignal
        if (isExecuting && executionController) {
            requestOptions.signal = executionController.signal;
        }
        
        const response = await fetch('/api/step/nano-banana', requestOptions);
        
        // 检查是否被中止
        if (response.status === 0 || shouldStopExecution) {
            throw new Error('执行已停止');
        }
        
        if (!response.ok) {
            let errorMsg = '转换失败';
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMsg = errorData.detail;
                }
            } catch (e) {
                errorMsg = `转换失败 (HTTP ${response.status})`;
            }
            throw new Error(errorMsg);
        }
        
        const data = await response.json();
        stepStatus.nano_banana = data;
        
        // 显示结果
        resultDiv.innerHTML = `
            <div class="result-info">
                <h3>✓ 转换完成</h3>
                <img src="${data.image_url}" alt="Nano Banana转换结果" style="max-width: 100%; margin-top: 10px;">
                <p style="margin-top: 10px; color: #666;">文件ID: ${data.file_id}</p>
            </div>
        `;
        
        stepSection.classList.remove('running');
        stepSection.classList.add('completed');
        stepSection.style.display = ''; // 确保可见
        stepSection.style.visibility = 'visible';
        console.log('Nano Banana步骤完成，步骤区域状态 - display:', stepSection.style.display, 'visibility:', stepSection.style.visibility);
        refreshBtn.disabled = false;
        
        // 刷新步骤状态，更新后续步骤的可用性
        await checkStepStatus();
        
        // 如果不在自动执行流程中，显示成功消息
        if (!isExecuting) {
            showSuccess('Nano Banana转换完成！');
        }
    } catch (error) {
        console.error('Nano Banana步骤出错:', error);
        if (stepSection) {
            // 强制确保步骤区域可见
            stepSection.classList.remove('running', 'completed', 'hidden');
            stepSection.classList.add('error');
            stepSection.style.display = 'block'; // 使用 block 而不是空字符串
            stepSection.style.visibility = 'visible';
            stepSection.style.opacity = '1';
            // 确保父元素也可见
            const parent = stepSection.parentElement;
            if (parent) {
                parent.style.display = '';
                parent.style.visibility = 'visible';
            }
            console.log('错误处理后的步骤区域状态 - display:', stepSection.style.display, 'visibility:', stepSection.style.visibility, 'classList:', stepSection.classList.toString());
        }
        if (resultDiv) {
            resultDiv.innerHTML = `<div class="error" style="padding: 15px; background: #fee; border: 1px solid #fcc; border-radius: 5px; color: #c33;">
                <strong>错误:</strong> ${error.message}<br>
                <small style="color: #999; margin-top: 5px; display: block;">提示: 请先配置Nano Banana API才能使用此功能</small>
            </div>`;
        }
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.style.display = ''; // 确保刷新按钮可见
        }
        showError('Nano Banana转换失败: ' + error.message);
    }
}

// 步骤2: 图像预处理
async function runPreprocess() {
    if (!currentFileId) {
        showError('请先上传图片');
        return;
    }
    
    const stepSection = document.getElementById('stepPreprocess');
    const resultDiv = document.getElementById('preprocessResult');
    const refreshBtn = document.getElementById('refreshPreprocessBtn');
    
    try {
        stepSection.classList.remove('error', 'completed');
        stepSection.classList.add('running');
        refreshBtn.disabled = true;
        resultDiv.innerHTML = '<div class="loading">正在预处理图像...</div>';
        
        const formData = new FormData();
        formData.append('file_id', currentFileId);
        formData.append('max_dimension', document.getElementById('maxDimension').value);
        formData.append('target_colors', getTargetColorsValue());
        formData.append('denoise_strength', document.getElementById('denoiseStrength').value);
        formData.append('contrast_factor', document.getElementById('contrastFactor').value);
        formData.append('sharpness_factor', document.getElementById('sharpnessFactor').value);
        formData.append('use_custom', document.getElementById('useCustomColors').checked);
        formData.append('use_nano_banana_result', document.getElementById('useNanoBananaResult').checked);
        const beadSize = document.getElementById('beadSize').value;
        formData.append('bead_size_mm', parseFloat(beadSize));
        
        const requestOptions = {
            method: 'POST',
            body: formData
        };
        
        // 如果在自动执行模式，添加AbortSignal
        if (isExecuting && executionController) {
            requestOptions.signal = executionController.signal;
        }
        
        const response = await fetch('/api/step/preprocess', requestOptions);
        
        // 检查是否被中止
        if (response.status === 0 || shouldStopExecution) {
            throw new Error('执行已停止');
        }
        
        if (!response.ok) {
            let errorMsg = '预处理失败';
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMsg = errorData.detail;
                }
            } catch (e) {
                errorMsg = `预处理失败 (HTTP ${response.status})`;
            }
            throw new Error(errorMsg);
        }
        
        const data = await response.json();
        stepStatus.preprocess = data;
        
        // 显示结果（支持缩放）
        resultDiv.innerHTML = `
            <div class="result-info">
                <h3>✓ 预处理完成</h3>
                <div class="image-viewer" onclick="toggleImageZoom(this)">
                    <img src="${data.image_url}" alt="预处理结果" style="max-width: 100%; margin-top: 10px;">
                    <div class="zoom-controls">
                        <button class="zoom-btn" onclick="event.stopPropagation(); zoomImage(this.parentElement.parentElement, 1.2)">+</button>
                        <button class="zoom-btn" onclick="event.stopPropagation(); zoomImage(this.parentElement.parentElement, 0.8)">-</button>
                        <button class="zoom-btn" onclick="event.stopPropagation(); resetImageZoom(this.parentElement.parentElement)">重置</button>
                    </div>
                </div>
                <p style="margin-top: 10px; color: #666;">
                    尺寸: ${data.width} × ${data.height} 拼豆<br>
                    文件ID: ${data.file_id}<br>
                    <small>点击图片可放大查看，使用+/-按钮可缩放</small>
                </p>
            </div>
        `;
        
        stepSection.classList.remove('running');
        stepSection.classList.add('completed');
        refreshBtn.disabled = false;
        
        // 刷新步骤状态
        await checkStepStatus();
        
        // 如果不在自动执行流程中，显示成功消息
        if (!isExecuting) {
            showSuccess('预处理完成！');
        }
        
        // 检查是否应该停止
        if (shouldStopExecution) {
            throw new Error('执行已停止');
        }
    } catch (error) {
        stepSection.classList.remove('running');
        stepSection.classList.add('error');
        resultDiv.innerHTML = `<div class="error">错误: ${error.message}</div>`;
        refreshBtn.disabled = false;
        showError('预处理失败: ' + error.message);
    }
}

// 步骤3: 生成拼豆图案
async function runGeneratePattern() {
    if (!currentFileId) {
        showError('请先上传图片');
        return;
    }
    
    const stepSection = document.getElementById('stepGeneratePattern');
    const resultDiv = document.getElementById('generatePatternResult');
    const refreshBtn = document.getElementById('refreshGeneratePatternBtn');
    
    try {
        stepSection.classList.remove('error', 'completed');
        stepSection.classList.add('running');
        refreshBtn.disabled = true;
        resultDiv.innerHTML = '<div class="loading">正在生成拼豆图案...</div>';
        
        const formData = new FormData();
        formData.append('file_id', currentFileId);
        formData.append('use_custom', document.getElementById('useCustomColorsPattern').checked);
        formData.append('match_mode', getMatchModeValue());
        // 从步骤2的选择器获取拼豆大小（步骤2已经设置了拼豆大小）
        const beadSizeSelect = document.getElementById('beadSize');
        const beadSize = beadSizeSelect ? parseFloat(beadSizeSelect.value) : 2.6;
        formData.append('bead_size_mm', beadSize);
        // 添加品牌和系列参数
        const brandSelect = document.getElementById('colorBrand');
        const seriesSelect = document.getElementById('colorSeries');
        if (brandSelect && brandSelect.value) {
            formData.append('brand', brandSelect.value);
        }
        if (seriesSelect && seriesSelect.value) {
            formData.append('series', seriesSelect.value);
        }
        
        const requestOptions = {
            method: 'POST',
            body: formData
        };
        
        // 如果在自动执行模式，添加AbortSignal
        if (isExecuting && executionController) {
            requestOptions.signal = executionController.signal;
        }
        
        const response = await fetch('/api/step/generate-pattern', requestOptions);
        
        // 检查是否被中止
        if (response.status === 0 || shouldStopExecution) {
            throw new Error('执行已停止');
        }
        
        if (!response.ok) {
            let errorMsg = '生成失败';
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMsg = errorData.detail;
                }
            } catch (e) {
                errorMsg = `生成失败 (HTTP ${response.status})`;
            }
            throw new Error(errorMsg);
        }
        
        const data = await response.json();
        stepStatus.generate_pattern = data;
        currentPatternId = data.pattern_id;
        currentPattern = data;
        
        // 保存两个版本的URL（如果有）
        const vizUrlWithLabels = data.viz_url || data.viz_url_with_labels;
        const vizUrlNoLabels = data.viz_url_no_labels || null; // 必须存在无编号版本
        
        // 显示结果（支持缩放，网格图显示编号）
        const stats = data.statistics;
        const showLabels = true; // 默认显示编号
        
        resultDiv.innerHTML = `
            <div class="result-info">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h3 style="margin: 0;">✓ 图案生成完成</h3>
                    <button class="btn btn-secondary" id="toggleLabelsBtn" style="padding: 8px 16px; font-size: 14px;">
                        ${showLabels ? '隐藏编号' : '显示编号'}
                    </button>
                </div>
                <div class="image-viewer" onclick="toggleImageZoom(this)">
                    <img id="patternImage" src="${showLabels ? vizUrlWithLabels : vizUrlNoLabels}" alt="拼豆图案" style="max-width: 100%; margin-top: 10px;">
                    <div class="zoom-controls">
                        <button class="zoom-btn" onclick="event.stopPropagation(); zoomImage(this.parentElement.parentElement, 1.2)">+</button>
                        <button class="zoom-btn" onclick="event.stopPropagation(); zoomImage(this.parentElement.parentElement, 0.8)">-</button>
                        <button class="zoom-btn" onclick="event.stopPropagation(); resetImageZoom(this.parentElement.parentElement)">重置</button>
                    </div>
                </div>
                <div style="margin-top: 15px; padding: 10px; background: white; border-radius: 5px;">
                    ${(() => {
                        const sw = data.subject_width || 0;
                        const sh = data.subject_height || 0;
                        const swmm = data.subject_width_mm || 0;
                        const shmm = data.subject_height_mm || 0;
                        const tw = data.width || 0;
                        const th = data.height || 0;
                        const twmm = data.actual_width_mm || 0;
                        const thmm = data.actual_height_mm || 0;

                        const patternW = (sw > 0 && sh > 0) ? sw : tw;
                        const patternH = (sw > 0 && sh > 0) ? sh : th;
                        const beadW = (swmm > 0 && shmm > 0) ? swmm / 10 : twmm / 10;
                        const beadH = (swmm > 0 && shmm > 0) ? shmm / 10 : thmm / 10;

                        return `
                        <p><strong>图案尺寸:</strong> ${patternW} × ${patternH} 拼豆</p>
                        <p style="color: #667eea; font-weight: 600; margin-top: 8px;">
                            <strong>拼豆尺寸:</strong> ${beadW.toFixed(1)} × ${beadH.toFixed(1)} cm
                            ${sw > 0 && sh > 0 ? '<span style="font-size: 0.85em; color: #666; margin-left: 10px;">※ 已排除背景</span>' : ''}
                        </p>`;
                    })()}
                    <p><strong>使用颜色数:</strong> ${stats.unique_colors}</p>
                    <p><strong>总拼豆数:</strong> ${stats.total_beads} 
                    ${data.subject_statistics && data.subject_statistics.subject_beads ? `
                        (主体: ${data.subject_statistics.subject_beads}, 背景: ${data.subject_statistics.background_beads})
                    ` : ''}
                    </p>
                    <small style="color: #666;">点击图片可放大查看，使用+/-按钮可缩放，点击"切换编号"按钮可显示/隐藏色号</small>
                </div>

                <!-- 色号使用清单 -->
                <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3 style="margin: 0; font-size: 1.2em; color: #495057;">📋 色号使用清单</h3>
                        <button class="btn btn-secondary" id="toggleColorListBtn" style="padding: 6px 12px; font-size: 14px;">
                            收起
                        </button>
                    </div>
                    <div id="colorListContainer" style="max-height: 400px; overflow-y: auto;">
                        <!-- 颜色清单表格 -->
                        <table style="width: 100%; border-collapse: collapse; font-family: 'Segoe UI', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif; font-size: 15px; background: white; border-radius: 5px; overflow: hidden;">
                            <thead>
                                <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; position: sticky; top: 0; z-index: 10;">
                                    <th style="padding: 12px 10px; text-align: left; font-weight: 700; font-size: 16px;">颜色</th>
                                    <th style="padding: 12px 10px; text-align: left; font-weight: 700; font-size: 16px;">色号</th>
                                    <th style="padding: 12px 10px; text-align: right; font-weight: 700; font-size: 16px;">数量</th>
                                    <th style="padding: 12px 10px; text-align: right; font-weight: 700; font-size: 16px;">占比</th>
                                </tr>
                            </thead>
                            <tbody id="colorListBody">
                                <!-- 动态生成 -->
                            </tbody>
                        </table>
                    </div>
                    <div id="colorListSummary" style="margin-top: 10px; padding: 10px; background: white; border-radius: 5px; font-family: 'Segoe UI', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif; font-size: 15px; color: #6c757d;">
                        <!-- 统计摘要 -->
                    </div>
                </div>
            </div>
        `;
        
        // 保存URL到全局变量以便切换（确保使用完整路径）
        // 确保vizUrlWithLabels和vizUrlNoLabels都存在且不同
        const baseUrl = window.location.origin;
        
        // 标准化URL（确保使用完整路径）
        const fullVizUrlWithLabels = vizUrlWithLabels.startsWith('http') ? vizUrlWithLabels : baseUrl + vizUrlWithLabels;
        const fullVizUrlNoLabels = (vizUrlNoLabels && vizUrlNoLabels !== vizUrlWithLabels) 
            ? (vizUrlNoLabels.startsWith('http') ? vizUrlNoLabels : baseUrl + vizUrlNoLabels)
            : null;
        
        // 保存到全局变量（确保在图片加载前就设置好）
        window.currentPatternVizUrlWithLabels = fullVizUrlWithLabels;
        window.currentPatternVizUrlNoLabels = fullVizUrlNoLabels;
        window.currentPatternShowLabels = showLabels;
        
        // 保存当前pattern_id以便后续使用
        window.currentPatternId = data.pattern_id;
        
        console.log('保存图案URL:', {
            patternId: data.pattern_id,
            withLabels: window.currentPatternVizUrlWithLabels,
            noLabels: window.currentPatternVizUrlNoLabels,
            showLabels: window.currentPatternShowLabels,
            vizUrlWithLabels: vizUrlWithLabels,
            vizUrlNoLabels: vizUrlNoLabels
        });
        
        stepSection.classList.remove('running');
        stepSection.classList.add('completed');
        stepSection.style.display = '';
        stepSection.style.visibility = 'visible';
        refreshBtn.disabled = false;
        
        // 确保切换编号按钮的事件正确绑定（使用onclick属性，避免重复绑定）
        setTimeout(() => {
            const toggleLabelsBtn = document.getElementById('toggleLabelsBtn');
            if (toggleLabelsBtn) {
                toggleLabelsBtn.onclick = togglePatternLabels;
                console.log('切换编号按钮事件已绑定:', toggleLabelsBtn);
            }
        }, 100);

        // 生成色号清单
        if (stats && stats.color_counts && stats.color_details) {
            generateColorList(stats.color_counts, stats.color_details, stats.total_beads);

            // 绑定收起/展开按钮事件
            const toggleColorListBtn = document.getElementById('toggleColorListBtn');
            if (toggleColorListBtn) {
                toggleColorListBtn.onclick = toggleColorList;
            }
        }
        
        // 启用生成实物效果图的刷新按钮
        const refreshGenerateRenderBtn = document.getElementById('refreshGenerateRenderBtn');
        if (refreshGenerateRenderBtn) {
            refreshGenerateRenderBtn.disabled = false;
        }
        
        // 显示导出选项（如果存在）并确保按钮事件绑定
        const resultSection = document.getElementById('resultSection');
        if (resultSection) {
            resultSection.classList.remove('hidden');
            // 确保导出按钮事件已绑定（以防在显示后才绑定）
            setupExportButtons();
        }
        
        // 如果不在自动执行流程中，显示成功消息
        if (!isExecuting) {
            showSuccess('图案生成完成！');
        }
        
        // 检查是否应该停止
        if (shouldStopExecution) {
            throw new Error('执行已停止');
        }
    } catch (error) {
        stepSection.classList.remove('running');
        stepSection.classList.add('error');
        stepSection.style.display = '';
        stepSection.style.visibility = 'visible';
        resultDiv.innerHTML = `<div class="error">错误: ${error.message}</div>`;
        refreshBtn.disabled = false;
        showError('图案生成失败: ' + error.message);
    }
}

/**
 * 生成色号使用清单
 * @param {Object} colorCounts - 颜色数量映射 {color_id: count}
 * @param {Object} colorDetails - 颜色详细信息映射 {color_id: {code, name_zh, name_en, rgb, ...}}
 * @param {number} totalBeads - 总拼豆数
 */
function generateColorList(colorCounts, colorDetails, totalBeads) {
    const tbody = document.getElementById('colorListBody');
    const summaryDiv = document.getElementById('colorListSummary');

    if (!tbody || !summaryDiv) {
        console.warn('颜色清单容器未找到');
        return;
    }

    if (!colorCounts || Object.keys(colorCounts).length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="padding: 20px; text-align: center; color: #6c757d;">暂无颜色数据</td></tr>';
        summaryDiv.innerHTML = '';
        return;
    }

    // 按使用数量降序排列
    const sortedColors = Object.entries(colorCounts)
        .sort((a, b) => b[1] - a[1])
        .map(([colorId, count]) => {
            const colorInfo = colorDetails[colorId] || {
                code: colorId,
                name_zh: '未知颜色',
                name_en: 'Unknown',
                rgb: [128, 128, 128]
            };
            return {
                colorId,
                code: colorInfo.code || colorId,
                name_zh: colorInfo.name_zh || '未知',
                name_en: colorInfo.name_en || 'Unknown',
                rgb: colorInfo.rgb || [128, 128, 128],
                count,
                percentage: ((count / totalBeads) * 100).toFixed(1)
            };
        });

    // 生成表格行
    tbody.innerHTML = sortedColors.map((item, index) => `
        <tr style="border-bottom: 1px solid #dee2e6; transition: background-color 0.2s;">
            <td style="padding: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 28px; height: 28px; background: rgb(${item.rgb.join(',')});
                               border: 2px solid #dee2e6; border-radius: 4px; display: inline-block;
                               vertical-align: middle; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    </div>
                    <div>
                        <div style="font-family: 'Segoe UI', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 700; font-size: 15px; color: #212529;">${item.name_zh}</div>
                        <div style="font-family: 'Segoe UI', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif; font-size: 13px; color: #6c757d;">${item.name_en}</div>
                    </div>
                </div>
            </td>
            <td style="padding: 10px; font-family: 'Segoe UI', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 700; font-size: 15px; color: #667eea;">${item.code}</td>
            <td style="padding: 10px; text-align: right; font-family: 'Segoe UI', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 700; font-size: 15px; color: #212529;">${item.count}</td>
            <td style="padding: 10px; text-align: right; font-family: 'Segoe UI', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif; color: #6c757d;">
                <span style="display: inline-block; min-width: 50px; font-size: 15px;">${item.percentage}%</span>
                <!-- 简单的进度条 -->
                <div style="width: 60px; height: 4px; background: #e9ecef; border-radius: 2px; display: inline-block; margin-left: 8px; vertical-align: middle;">
                    <div style="width: ${item.percentage}%; height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 2px;"></div>
                </div>
            </td>
        </tr>
    `).join('');

    // 生成统计摘要
    const topColors = sortedColors.slice(0, 5);
    const topPercentage = topColors.reduce((sum, item) => sum + parseFloat(item.percentage), 0).toFixed(1);

    summaryDiv.innerHTML = `
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px; font-weight: 600;">
            <span style="color: #495057;"><strong>颜色种类:</strong> <span style="color: #667eea;">${sortedColors.length}</span></span>
            <span style="color: #495057;"><strong>总拼豆数:</strong> <span style="color: #667eea;">${totalBeads}</span></span>
            <span style="color: #495057;"><strong>最常用色号:</strong> <span style="color: #667eea; font-weight: 700;">${sortedColors[0].code}</span> (<span style="color: #667eea;">${sortedColors[0].count}</span>个)</span>
            <span style="color: #495057;"><strong>前5色占比:</strong> <span style="color: #667eea;">${topPercentage}%</span></span>
        </div>
    `;

    console.log('颜色清单生成完成，共', sortedColors.length, '种颜色');
}

/**
 * 收起/展开颜色清单
 */
function toggleColorList() {
    const container = document.getElementById('colorListContainer');
    const btn = document.getElementById('toggleColorListBtn');

    if (!container || !btn) {
        return;
    }

    if (container.style.display === 'none') {
        container.style.display = 'block';
        btn.textContent = '收起';
    } else {
        container.style.display = 'none';
        btn.textContent = '展开';
    }
}

// 步骤4: 生成实物效果图
async function runGenerateRender() {
    if (!currentFileId) {
        showError('请先上传图片');
        return;
    }
    
    // 检查是否已生成图案
    if (!currentPatternId) {
        // 尝试从步骤结果中获取
        if (currentFileId in stepStatus && stepStatus[currentFileId] && stepStatus[currentFileId].generate_pattern) {
            currentPatternId = stepStatus[currentFileId].generate_pattern.pattern_id;
        } else if (stepStatus.generate_pattern) {
            currentPatternId = stepStatus.generate_pattern.pattern_id;
        } else {
            showError('请先生成拼豆图案');
            return;
        }
    }
    
    const stepSection = document.getElementById('stepGenerateRender');
    const resultDiv = document.getElementById('generateRenderResult');
    const refreshBtn = document.getElementById('refreshGenerateRenderBtn');
    
    // 检查元素是否存在
    if (!stepSection || !resultDiv || !refreshBtn) {
        console.error('无法找到步骤元素:', {
            stepSection: !!stepSection,
            resultDiv: !!resultDiv,
            refreshBtn: !!refreshBtn
        });
        showError('页面元素缺失，请刷新页面重试');
        return;
    }
    
    try {
        // 确保步骤区域可见
        console.log('开始执行生成实物效果图步骤，步骤区域:', stepSection);
        stepSection.style.display = 'block'; // 使用 block 确保可见
        stepSection.style.visibility = 'visible';
        stepSection.style.opacity = '1';
        stepSection.classList.remove('error', 'completed', 'hidden');
        stepSection.classList.add('running');
        // 确保父元素也可见
        const parent = stepSection.parentElement;
        if (parent) {
            parent.style.display = '';
            parent.style.visibility = 'visible';
        }
        refreshBtn.disabled = true;
        resultDiv.innerHTML = '<div class="loading">正在使用Nano Banana生成实物效果图...</div>';
        
        const formData = new FormData();
        formData.append('file_id', currentFileId);
        if (currentPatternId) {
            formData.append('pattern_id', currentPatternId);
        }
        formData.append('prompt', document.getElementById('renderPrompt').value);
        formData.append('model', document.getElementById('renderModel').value);
        formData.append('image_size', document.getElementById('renderImageSize').value);
        
        const requestOptions = {
            method: 'POST',
            body: formData
        };
        
        // 如果在自动执行模式，添加AbortSignal
        if (isExecuting && executionController) {
            requestOptions.signal = executionController.signal;
        }
        
        const response = await fetch('/api/step/generate-render', requestOptions);
        
        // 检查是否被中止
        if (response.status === 0 || shouldStopExecution) {
            throw new Error('执行已停止');
        }
        
        if (!response.ok) {
            let errorMsg = '生成失败';
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMsg = errorData.detail;
                }
            } catch (e) {
                errorMsg = `生成失败 (HTTP ${response.status})`;
            }
            throw new Error(errorMsg);
        }
        
        const data = await response.json();
        stepStatus.generate_render = data;
        
        // 显示结果
        resultDiv.innerHTML = `
            <div class="result-info">
                <h3>✓ 实物效果图生成完成</h3>
                <img src="${data.render_url}" alt="实物效果图" style="max-width: 100%; margin-top: 10px; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <p style="margin-top: 10px; color: #666;">
                    文件ID: ${data.file_id}<br>
                    图案ID: ${data.pattern_id}
                </p>
            </div>
        `;
        
        stepSection.classList.remove('running');
        stepSection.classList.add('completed');
        stepSection.style.display = 'block'; // 使用 block 确保可见
        stepSection.style.visibility = 'visible';
        refreshBtn.disabled = false;
        
        // 刷新步骤状态
        await checkStepStatus();
        
        // 如果不在自动执行流程中，显示成功消息
        if (!isExecuting) {
            showSuccess('实物效果图生成完成！');
        }
    } catch (error) {
        console.error('生成实物效果图出错:', error);
        if (stepSection) {
            // 强制确保步骤区域可见
            stepSection.classList.remove('running', 'completed', 'hidden');
            stepSection.classList.add('error');
            stepSection.style.display = 'block'; // 使用 block 而不是空字符串
            stepSection.style.visibility = 'visible';
            stepSection.style.opacity = '1';
            // 确保父元素也可见
            const parent = stepSection.parentElement;
            if (parent) {
                parent.style.display = '';
                parent.style.visibility = 'visible';
            }
            console.log('错误处理后的步骤区域状态 - display:', stepSection.style.display, 'visibility:', stepSection.style.visibility, 'classList:', stepSection.classList.toString());
        }
        if (resultDiv) {
            resultDiv.innerHTML = `<div class="error" style="padding: 15px; background: #fee; border: 1px solid #fcc; border-radius: 5px; color: #c33;">
                <strong>错误:</strong> ${error.message}<br>
                <small style="color: #999; margin-top: 5px; display: block;">提示: 请先配置Nano Banana API才能使用此功能</small>
            </div>`;
        }
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.style.display = ''; // 确保刷新按钮可见
        }
        showError('实物效果图生成失败: ' + error.message);
    }
}

// 刷新步骤状态
async function checkStepStatus() {
    if (!currentFileId) return;
    
    try {
        const response = await fetch(`/api/step/${currentFileId}/status`);
        if (response.ok) {
            const status = await response.json();
            // 可以根据状态更新UI
            console.log('步骤状态:', status);
        }
    } catch (error) {
        console.error('获取步骤状态失败:', error);
    }
}

// 一键执行全部步骤
async function executeAllSteps() {
    if (!currentFileId) {
        showError('请先上传图片');
        return;
    }
    
    if (isExecuting) {
        showError('正在执行中，请稍候...');
        return;
    }
    
    // 初始化执行状态
    isExecuting = true;
    shouldStopExecution = false;
    executionController = new AbortController();
    
    const executeAllBtn = document.getElementById('executeAllBtn');
    const stopExecutionBtn = document.getElementById('stopExecutionBtn');
    const refreshAllBtn = document.getElementById('refreshAllBtn');
    const executionProgress = document.getElementById('executionProgress');
    const currentStepText = document.getElementById('currentStepText');
    const stepProgress = document.getElementById('stepProgress');
    const progressBar = document.getElementById('progressBar');
    
    // 更新UI
    if (executeAllBtn) executeAllBtn.style.display = 'none';
    if (refreshAllBtn) refreshAllBtn.style.display = 'none';
    if (executionProgress) {
        executionProgress.style.display = 'block';
        // 显示终止按钮
        if (stopExecutionBtn) stopExecutionBtn.style.display = 'inline-block';
    }
    
    // 禁用所有单独的执行按钮
    disableAllStepButtons();
    
    try {
        // 重置步骤状态
        resetSteps();
        stepStatus = {};
        currentPatternId = null;
        currentPattern = null;
        
        // 步骤1: Nano Banana AI转换（可选，根据配置决定是否执行）
        if (shouldStopExecution) {
            throw new Error('执行已停止');
        }
        
        updateProgress(1, 4, '步骤1: Nano Banana AI转换...');
        
        try {
            await runNanoBanana();
            if (shouldStopExecution) {
                throw new Error('执行已停止');
            }
        } catch (error) {
            // Nano Banana步骤失败不影响后续步骤（如果用户选择不使用）
            console.warn('Nano Banana步骤失败，继续执行:', error);
            if (shouldStopExecution) {
                throw new Error('执行已停止');
            }
        }
        
        // 步骤2: 图像预处理
        if (shouldStopExecution) {
            throw new Error('执行已停止');
        }
        
        updateProgress(2, 4, '步骤2: 图像预处理...');
        await runPreprocess();
        
        if (shouldStopExecution) {
            throw new Error('执行已停止');
        }
        
        // 步骤3: 生成拼豆图案
        updateProgress(3, 4, '步骤3: 生成拼豆图案...');
        await runGeneratePattern();
        
        if (shouldStopExecution) {
            throw new Error('执行已停止');
        }
        
        // 步骤4: 生成实物效果图（可选，如果配置了Nano Banana API）
        const useRender = true; // 可以添加配置项来控制是否执行
        if (useRender) {
            updateProgress(4, 4, '步骤4: 生成实物效果图...');
            try {
                await runGenerateRender();
            } catch (error) {
                // 实物效果图失败不影响整体流程
                console.warn('实物效果图生成失败，但不影响整体流程:', error);
            }
        }
        
        // 执行完成
        if (!shouldStopExecution) {
            updateProgress(4, 4, '✓ 全部步骤执行完成！');
            showSuccess('所有步骤执行完成！');
            
            // 隐藏执行按钮，显示刷新按钮
            if (executeAllBtn) executeAllBtn.style.display = 'none';
            if (stopExecutionBtn) stopExecutionBtn.style.display = 'none';
            if (refreshAllBtn) refreshAllBtn.style.display = 'inline-block';
            
            // 延迟隐藏进度条
            setTimeout(() => {
                if (executionProgress) {
                    executionProgress.style.display = 'none';
                }
            }, 3000);
        }
        
    } catch (error) {
        console.error('执行过程中出错:', error);
        if (shouldStopExecution) {
            showError('执行已停止');
        } else {
            showError('执行失败: ' + error.message);
        }
        
        updateProgress(0, 4, '执行失败或已停止');
    } finally {
        // 恢复UI状态
        isExecuting = false;
        shouldStopExecution = false;
        
        if (executeAllBtn) executeAllBtn.style.display = 'inline-block';
        if (stopExecutionBtn) stopExecutionBtn.style.display = 'none';
        
        // 重新启用所有步骤按钮
        enableStepButtons();
    }
}

// 停止执行
function stopExecution() {
    shouldStopExecution = true;
    if (executionController) {
        executionController.abort();
    }
    
    const stopExecutionBtn = document.getElementById('stopExecutionBtn');
    const executeAllBtn = document.getElementById('executeAllBtn');
    
    if (stopExecutionBtn) stopExecutionBtn.style.display = 'none';
    if (executeAllBtn) executeAllBtn.style.display = 'inline-block';
    
    showError('正在停止执行...');
}


// 刷新所有步骤（重新执行）
async function refreshAllSteps() {
    if (!currentFileId) {
        showError('请先上传图片');
        return;
    }
    
    // 重置状态
    stepStatus = {};
    currentPatternId = null;
    currentPattern = null;
    
    // 重新执行
    await executeAllSteps();
}

// 更新进度条
function updateProgress(current, total, text) {
    const currentStepText = document.getElementById('currentStepText');
    const stepProgress = document.getElementById('stepProgress');
    const progressBar = document.getElementById('progressBar');
    
    if (currentStepText) {
        currentStepText.textContent = text;
    }
    if (stepProgress) {
        stepProgress.textContent = `${current}/${total}`;
    }
    if (progressBar) {
        const percentage = (current / total) * 100;
        progressBar.style.width = percentage + '%';
    }
}

// 禁用所有步骤按钮（现在只禁用刷新按钮）
function disableAllStepButtons() {
    const refreshNanoBananaBtn = document.getElementById('refreshNanoBananaBtn');
    const refreshPreprocessBtn = document.getElementById('refreshPreprocessBtn');
    const refreshGeneratePatternBtn = document.getElementById('refreshGeneratePatternBtn');
    const refreshGenerateRenderBtn = document.getElementById('refreshGenerateRenderBtn');
    
    if (refreshNanoBananaBtn) refreshNanoBananaBtn.disabled = true;
    if (refreshPreprocessBtn) refreshPreprocessBtn.disabled = true;
    if (refreshGeneratePatternBtn) refreshGeneratePatternBtn.disabled = true;
    if (refreshGenerateRenderBtn) refreshGenerateRenderBtn.disabled = true;
}

// 配置收起/展开功能
function toggleConfigSection() {
    const content = document.getElementById('nanoBananaConfigContent');
    const icon = document.getElementById('configToggleIcon');
    if (content && icon) {
        content.classList.toggle('collapsed');
        icon.textContent = content.classList.contains('collapsed') ? '▶' : '▼';
    }
}

// 自定义色板收起/展开功能
function toggleColorPaletteSection() {
    const content = document.getElementById('colorPaletteContent');
    const icon = document.getElementById('colorPaletteToggleIcon');
    if (content && icon) {
        content.classList.toggle('collapsed');
        icon.textContent = content.classList.contains('collapsed') ? '▶' : '▼';
    }
}

// 图片缩放功能
function toggleImageZoom(viewer) {
    if (!viewer) return;
    viewer.classList.toggle('zoomed');
    if (viewer.classList.contains('zoomed')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
}

let imageZoomLevel = 1;

function zoomImage(viewer, factor) {
    if (!viewer) return;
    const img = viewer.querySelector('img');
    if (!img) return;
    
    imageZoomLevel *= factor;
    imageZoomLevel = Math.max(0.5, Math.min(3, imageZoomLevel)); // 限制缩放范围
    
    img.style.transform = `scale(${imageZoomLevel})`;
    img.style.transformOrigin = 'center center';
}

function resetImageZoom(viewer) {
    if (!viewer) return;
    const img = viewer.querySelector('img');
    if (!img) return;
    
    imageZoomLevel = 1;
    img.style.transform = 'scale(1)';
}

// 加载色板信息
async function loadColorPalette() {
    try {
        // 获取标准色板数量（不包含自定义）
        const standardResponse = await fetch('/api/colors?include_custom=false');
        let standardCount = 0;
        if (standardResponse.ok) {
            const standardData = await standardResponse.json();
            standardCount = standardData.colors ? standardData.colors.length : 0;
        }
        
        // 直接获取自定义色板（使用专门的API端点，只返回用户自定义的颜色）
        const customResponse = await fetch('/api/colors/custom');
        let customColors = [];
        if (customResponse.ok) {
            const customData = await customResponse.json();
            customColors = customData.colors || [];
        }
        
        // 更新统计信息
        const standardColorCountEl = document.getElementById('standardColorCount');
        const customColorCountEl = document.getElementById('customColorCount');
        const totalColorCountEl = document.getElementById('totalColorCount');
        
        if (standardColorCountEl) standardColorCountEl.textContent = standardCount;
        if (customColorCountEl) customColorCountEl.textContent = customColors.length;
        if (totalColorCountEl) totalColorCountEl.textContent = standardCount + customColors.length;
        
        // 显示自定义色板（只显示真正的自定义颜色）
        const grid = document.getElementById('colorPaletteGrid');
        const customColorListSection = document.getElementById('customColorListSection');
        
        if (!grid || !customColorListSection) return;
        
        if (customColors.length === 0) {
            // 没有自定义颜色，隐藏列表区域
            customColorListSection.style.display = 'none';
            grid.innerHTML = '';
        } else {
            // 有自定义颜色，显示列表区域
            customColorListSection.style.display = 'block';
            grid.innerHTML = customColors.map(color => `
                <div class="color-item" style="background: white; border-radius: 5px; padding: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div class="color-preview" style="width: 100%; height: 60px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 8px; background: rgb(${color.rgb.join(',')}); cursor: pointer;" 
                         onclick="toggleColorZoom(this)" title="点击放大"></div>
                    <div class="color-info" style="font-size: 0.85em;">
                        <div class="color-code" style="font-weight: 600; margin-bottom: 4px;">${color.code}</div>
                        <div class="color-name" style="color: #666; margin-bottom: 4px;">${color.name_zh || color.name_en || ''}</div>
                        <div class="color-rgb" style="color: #999; font-size: 0.9em; margin-bottom: 8px;">RGB: ${color.rgb.join(', ')}</div>
                        <button class="delete-color-btn" onclick="deleteCustomColor(${color.id})" style="width: 100%; padding: 5px; background: #ff4444; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 0.9em;">删除</button>
                    </div>
                </div>
            `).join('');
        }
        
    } catch (error) {
        console.error('加载色板失败:', error);
    }
}

// 颜色预览缩放
function toggleColorZoom(preview) {
    if (!preview) return;
    preview.style.transform = preview.style.transform === 'scale(2)' ? 'scale(1)' : 'scale(2)';
    preview.style.transition = 'transform 0.3s';
}

// 删除自定义颜色
async function deleteCustomColor(colorId) {
    if (!confirm('确定要删除这个颜色吗？')) return;
    
    try {
        const response = await fetch(`/api/colors/custom/${colorId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showSuccess('颜色已删除');
            await loadColorPalette();
        } else {
            const error = await response.json();
            showError('删除失败: ' + (error.detail || '未知错误'));
        }
    } catch (error) {
        showError('删除失败: ' + error.message);
    }
}

// 添加自定义颜色
async function addCustomColor() {
    const nameZh = document.getElementById('newColorNameZh').value.trim();
    const nameEn = document.getElementById('newColorNameEn').value.trim();
    const code = document.getElementById('newColorCode').value.trim();
    const rgbStr = document.getElementById('newColorRgb').value.trim();
    const category = document.getElementById('newColorCategory').value.trim() || '自定义';
    
    if (!nameZh || !code || !rgbStr) {
        showError('请填写完整信息');
        return;
    }
    
    // 解析RGB值
    const rgb = rgbStr.split(',').map(v => parseInt(v.trim()));
    if (rgb.length !== 3 || rgb.some(v => isNaN(v) || v < 0 || v > 255)) {
        showError('RGB值格式错误，应为：R,G,B（例如：255,0,0）');
        return;
    }
    
    try {
        const response = await fetch('/api/colors/custom', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name_zh: nameZh,
                name_en: nameEn || nameZh,
                code: code,
                rgb: rgb,
                category: category
            })
        });
        
        if (response.ok) {
            showSuccess('颜色已添加');
            // 清空表单
            document.getElementById('newColorNameZh').value = '';
            document.getElementById('newColorNameEn').value = '';
            document.getElementById('newColorCode').value = '';
            document.getElementById('newColorRgb').value = '';
            document.getElementById('newColorCategory').value = '自定义';
            updateColorPreview();
            await loadColorPalette();
        } else {
            const error = await response.json();
            showError('添加失败: ' + (error.detail || '未知错误'));
        }
    } catch (error) {
        showError('添加失败: ' + error.message);
    }
}

// 切换图案编号显示
function togglePatternLabels() {
    const patternImage = document.getElementById('patternImage');
    const toggleBtn = document.getElementById('toggleLabelsBtn');
    
    if (!patternImage) {
        console.error('找不到patternImage元素');
        return;
    }
    
    // 获取当前图片的完整URL（移除查询参数）
    const currentSrc = patternImage.src.split('?')[0];
    
    // 优先使用全局变量，如果不存在，尝试从当前图片URL推断
    if (!window.currentPatternVizUrlWithLabels || !window.currentPatternVizUrlNoLabels) {
        console.warn('全局变量未设置，尝试从当前URL推断');
        
        // 尝试从当前图片URL推断
        if (currentSrc.includes('_viz.png') && !currentSrc.includes('_viz_no_labels')) {
            // 当前是有编号版本
            const baseUrl = window.location.origin;
            window.currentPatternVizUrlWithLabels = currentSrc.startsWith('http') ? currentSrc : baseUrl + currentSrc;
            window.currentPatternVizUrlNoLabels = currentSrc.replace('_viz.png', '_viz_no_labels.png');
            window.currentPatternVizUrlNoLabels = window.currentPatternVizUrlNoLabels.startsWith('http') 
                ? window.currentPatternVizUrlNoLabels 
                : baseUrl + window.currentPatternVizUrlNoLabels;
            window.currentPatternShowLabels = true;
        } else if (currentSrc.includes('_viz_no_labels')) {
            // 当前是无编号版本
            const baseUrl = window.location.origin;
            window.currentPatternVizUrlNoLabels = currentSrc.startsWith('http') ? currentSrc : baseUrl + currentSrc;
            window.currentPatternVizUrlWithLabels = currentSrc.replace('_viz_no_labels.png', '_viz.png');
            window.currentPatternVizUrlWithLabels = window.currentPatternVizUrlWithLabels.startsWith('http')
                ? window.currentPatternVizUrlWithLabels
                : baseUrl + window.currentPatternVizUrlWithLabels;
            window.currentPatternShowLabels = false;
        } else {
            console.error('无法推断图片URL，切换功能暂时不可用。当前URL:', currentSrc);
            showError('切换编号功能暂时不可用，请重新生成图案');
            return;
        }
    }
    
    // 初始化状态（如果未定义）
    if (window.currentPatternShowLabels === undefined) {
        window.currentPatternShowLabels = currentSrc.includes('_viz_no_labels') ? false : true;
    }
    
    // 切换显示状态
    const newShowLabels = !window.currentPatternShowLabels;
    window.currentPatternShowLabels = newShowLabels;
    
    // 更新图片源（添加时间戳防止缓存）
    const timestamp = new Date().getTime();
    
    if (newShowLabels) {
        // 显示编号
        if (window.currentPatternVizUrlWithLabels) {
            const separator = window.currentPatternVizUrlWithLabels.includes('?') ? '&' : '?';
            patternImage.src = window.currentPatternVizUrlWithLabels + separator + '_t=' + timestamp;
            if (toggleBtn) toggleBtn.textContent = '隐藏编号';
            console.log('切换到有编号版本:', patternImage.src);
        } else {
            console.error('有编号版本URL不存在');
            showError('无法切换到有编号版本');
            window.currentPatternShowLabels = false; // 恢复状态
        }
    } else {
        // 隐藏编号
        if (window.currentPatternVizUrlNoLabels && window.currentPatternVizUrlNoLabels !== window.currentPatternVizUrlWithLabels) {
            const separator = window.currentPatternVizUrlNoLabels.includes('?') ? '&' : '?';
            patternImage.src = window.currentPatternVizUrlNoLabels + separator + '_t=' + timestamp;
            if (toggleBtn) toggleBtn.textContent = '显示编号';
            console.log('切换到无编号版本:', patternImage.src);
        } else {
            // 如果无编号版本不存在，显示警告
            console.error('无编号版本不存在，URL:', window.currentPatternVizUrlNoLabels, 'withLabels:', window.currentPatternVizUrlWithLabels);
            showError('无编号版本不存在，请重新生成图案');
            window.currentPatternShowLabels = true; // 恢复状态
            if (toggleBtn) toggleBtn.textContent = '隐藏编号';
        }
    }
    
    console.log('切换编号完成:', {
        showLabels: window.currentPatternShowLabels,
        withLabelsUrl: window.currentPatternVizUrlWithLabels,
        noLabelsUrl: window.currentPatternVizUrlNoLabels,
        newImageSrc: patternImage.src
    });
}

// 更新颜色预览
function updateColorPreview() {
    const rgbStr = document.getElementById('newColorRgb').value.trim();
    const preview = document.getElementById('newColorPreview');
    if (!preview) return;
    
    if (rgbStr) {
        const rgb = rgbStr.split(',').map(v => parseInt(v.trim()));
        if (rgb.length === 3 && !rgb.some(v => isNaN(v) || v < 0 || v > 255)) {
            preview.style.background = `rgb(${rgb.join(',')})`;
        } else {
            preview.style.background = '#fff';
        }
    } else {
        preview.style.background = '#fff';
    }
}

// 初始化色板管理
// 导出自定义颜色（CSV）
async function exportCustomColorsCsv() {
    try {
        const response = await fetch('/api/colors/custom/export?format=csv');
        if (!response.ok) {
            throw new Error('导出失败');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `custom_colors_${new Date().getTime()}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
        
        showSuccess('CSV导出成功！');
    } catch (error) {
        showError('导出失败: ' + error.message);
    }
}

// 导出自定义颜色（JSON）
async function exportCustomColorsJson() {
    try {
        const response = await fetch('/api/colors/custom/export?format=json');
        if (!response.ok) {
            throw new Error('导出失败');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `custom_colors_${new Date().getTime()}.json`;
        a.click();
        window.URL.revokeObjectURL(url);
        
        showSuccess('JSON导出成功！');
    } catch (error) {
        showError('导出失败: ' + error.message);
    }
}

// 导入自定义颜色
async function importCustomColors(file) {
    if (!file) {
        showError('请选择文件');
        return;
    }
    
    const filename = file.name.toLowerCase();
    let format = 'auto';
    
    if (filename.endsWith('.csv')) {
        format = 'csv';
    } else if (filename.endsWith('.json')) {
        format = 'json';
    } else {
        showError('不支持的文件格式，请选择CSV或JSON文件');
        return;
    }
    
    const replace = document.getElementById('replaceColorsOnImport')?.checked || false;
    
    try {
        showLoading('正在导入颜色...');
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('format', format);
        formData.append('replace', replace);
        
        const response = await fetch('/api/colors/custom/import', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '导入失败');
        }
        
        const result = await response.json();
        
        if (result.success) {
            let message = `成功导入 ${result.imported} 种颜色`;
            if (result.errors && result.errors.length > 0) {
                message += `\n警告: ${result.errors.length} 个错误`;
                console.warn('导入错误:', result.errors);
            }
            showSuccess(message);
            
            // 重新加载色板
            await loadColorPalette();
        } else {
            let errorMsg = '导入失败';
            if (result.errors && result.errors.length > 0) {
                errorMsg += ': ' + result.errors.slice(0, 3).join('; ');
                if (result.errors.length > 3) {
                    errorMsg += ` (还有 ${result.errors.length - 3} 个错误)`;
                }
            }
            showError(errorMsg);
        }
    } catch (error) {
        showError('导入失败: ' + error.message);
    }
}

function initColorPaletteManager() {
    loadColorPalette();
    
    // RGB输入实时预览
    const rgbInput = document.getElementById('newColorRgb');
    if (rgbInput) {
        rgbInput.addEventListener('input', updateColorPreview);
    }
    
    // 添加颜色按钮
    const addColorBtn = document.getElementById('addColorBtn');
    if (addColorBtn) {
        addColorBtn.addEventListener('click', addCustomColor);
    }
    
    // 导出按钮
    const exportCsvBtn = document.getElementById('exportColorsCsvBtn');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', exportCustomColorsCsv);
    }
    
    const exportJsonBtn = document.getElementById('exportColorsJsonBtn');
    if (exportJsonBtn) {
        exportJsonBtn.addEventListener('click', exportCustomColorsJson);
    }
    
    // 导入文件选择
    const importFileInput = document.getElementById('importColorFile');
    if (importFileInput) {
        importFileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                importCustomColors(file);
                // 清空input，以便可以重复选择同一文件
                e.target.value = '';
            }
        });
    }
}

// 加载品牌和系列列表
async function loadBrandsAndSeries() {
    try {
        const response = await fetch('/api/colors/brands');
        if (!response.ok) return;
        
        const data = await response.json();
        const brandsMap = data.brands || {};
        
        const brandSelect = document.getElementById('colorBrand');
        const seriesSelect = document.getElementById('colorSeries');
        
        if (!brandSelect || !seriesSelect) return;
        
        // 清空现有选项（保留"全部品牌"和"自定义"）
        brandSelect.innerHTML = '<option value="">全部品牌</option><option value="自定义">自定义色板</option>';
        
        // 添加品牌选项
        const brands = Object.keys(brandsMap).sort();
        brands.forEach(brand => {
            const option = document.createElement('option');
            option.value = brand;
            option.textContent = brand;
            brandSelect.appendChild(option);
        });
        
        // 更新可用颜色数
        updateColorCount();
        
    } catch (error) {
        console.error('加载品牌列表失败:', error);
    }
}

// 更新系列列表
async function updateColorSeries() {
    const brandSelect = document.getElementById('colorBrand');
    const seriesSelect = document.getElementById('colorSeries');
    
    if (!brandSelect || !seriesSelect) return;
    
    const selectedBrand = brandSelect.value;
    
    // 清空系列选项
    seriesSelect.innerHTML = '<option value="">请先选择品牌</option>';
    seriesSelect.disabled = true;
    
    if (!selectedBrand) {
        updateColorCount();
        return;
    }
    
    // 如果选择"自定义"，不需要系列
    if (selectedBrand === '自定义') {
        seriesSelect.innerHTML = '<option value="">自定义色板（无系列）</option>';
        seriesSelect.disabled = true;
        updateColorCount();
        return;
    }
    
    // 获取该品牌的系列列表
    try {
        const response = await fetch('/api/colors/brands');
        if (!response.ok) return;
        
        const data = await response.json();
        const brandsMap = data.brands || {};
        const series = brandsMap[selectedBrand] || [];
        
        if (series.length === 0) {
            seriesSelect.innerHTML = '<option value="">该品牌暂无系列</option>';
            seriesSelect.disabled = true;
        } else {
            seriesSelect.innerHTML = '<option value="">全部系列</option>';
            series.forEach(s => {
                const option = document.createElement('option');
                option.value = s;
                option.textContent = `${s}色`;
                seriesSelect.appendChild(option);
            });
            seriesSelect.disabled = false;
        }
        
        updateColorCount();
    } catch (error) {
        console.error('加载系列列表失败:', error);
    }
}

// 更新可用颜色数
async function updateColorCount() {
    const brandSelect = document.getElementById('colorBrand');
    const seriesSelect = document.getElementById('colorSeries');
    const infoDiv = document.getElementById('colorPaletteInfo');
    const countSpan = document.getElementById('selectedColorCount');
    
    if (!brandSelect || !infoDiv || !countSpan) return;
    
    const brand = brandSelect.value || null;
    const series = (seriesSelect && seriesSelect.value) ? seriesSelect.value : null;
    
    try {
        const params = new URLSearchParams();
        if (brand) params.append('brand', brand);
        if (series) params.append('series', series);
        
        const response = await fetch(`/api/colors?include_custom=true&${params.toString()}`);
        if (!response.ok) return;
        
        const data = await response.json();
        const count = data.colors ? data.colors.length : 0;
        
        countSpan.textContent = count;
        infoDiv.style.display = 'block';
    } catch (error) {
        console.error('获取颜色数失败:', error);
    }
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeUI();
    setupEventListeners();
    initColorPaletteManager();
    loadBrandsAndSeries();
    
    // 绑定品牌选择器事件
    const brandSelect = document.getElementById('colorBrand');
    const seriesSelect = document.getElementById('colorSeries');
    if (brandSelect) {
        brandSelect.addEventListener('change', updateColorSeries);
    }
    if (seriesSelect) {
        seriesSelect.addEventListener('change', updateColorCount);
    }
    
    // 绑定终止按钮事件（按钮在进度条区域，需要延迟绑定）
    setTimeout(() => {
        const stopExecutionBtn = document.getElementById('stopExecutionBtn');
        if (stopExecutionBtn) {
            stopExecutionBtn.addEventListener('click', stopExecution);
        }
    }, 100);
    
    // 如果配置已保存，收起配置区域
    if (localStorage.getItem('nanoBananaConfigSaved')) {
        setTimeout(() => {
            toggleConfigSection();
        }, 500);
    }
});

// 管理员后台JavaScript逻辑
const API_BASE_URL = window.location.origin;

// DOM元素
const webUrlInput = document.getElementById('webUrl');
const webContentInput = document.getElementById('webContent');
const fileNameInput = document.getElementById('fileName');
const generateBtn = document.getElementById('generateBtn');
const btnText = document.getElementById('btnText');
const btnLoading = document.getElementById('btnLoading');
const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');
const filePath = document.getElementById('filePath');
const createTime = document.getElementById('createTime');
const markdownPreview = document.getElementById('markdownPreview');
const errorMessage = document.getElementById('errorMessage');

// 生成按钮点击事件
generateBtn.addEventListener('click', handleGenerate);

async function handleGenerate() {
    // 获取输入内容
    const url = webUrlInput.value.trim();
    const content = webContentInput.value.trim();
    const fileName = fileNameInput.value.trim();

    // 验证输入
    if (!url && !content) {
        showError('请输入网页URL或粘贴网页内容');
        return;
    }

    // 显示加载状态
    setLoading(true);
    hideResults();

    try {
        // 调用后端API
        const response = await fetch(`${API_BASE_URL}/api/admin/generate-doc`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url || null,
                content: content || null,
                fileName: fileName || null
            })
        });

        const data = await response.json();

        if (data.success) {
            showResult(data);
        } else {
            showError(data.error || '生成失败,请重试');
        }
    } catch (error) {
        console.error('请求失败:', error);
        showError('网络错误,请检查后端服务是否正常运行');
    } finally {
        setLoading(false);
    }
}

function setLoading(isLoading) {
    generateBtn.disabled = isLoading;
    if (isLoading) {
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline-block';
    } else {
        btnText.style.display = 'inline-block';
        btnLoading.style.display = 'none';
    }
}

function showResult(data) {
    errorSection.style.display = 'none';
    resultSection.style.display = 'block';
    
    filePath.textContent = data.filePath;
    createTime.textContent = data.createTime;
    markdownPreview.textContent = data.markdown;
    
    // 滚动到结果区域
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showError(message) {
    resultSection.style.display = 'none';
    errorSection.style.display = 'block';
    errorMessage.textContent = message;
    
    // 滚动到错误区域
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideResults() {
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
}

// 输入框变化时隐藏结果
webUrlInput.addEventListener('input', hideResults);
webContentInput.addEventListener('input', hideResults);
fileNameInput.addEventListener('input', hideResults);

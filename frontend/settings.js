/**
 * 系统设置页面 - JavaScript逻辑
 * 功能: 日志清理策略管理
 */

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('[设置页面] 页面加载完成');
    
    // 初始化页面
    initPage();
    
    // 绑定事件监听
    bindEvents();
    
    // 加载当前设置
    loadCurrentSettings();
    
    // 加载日志状态
    loadLogStatus();
});

/**
 * 初始化页面
 */
function initPage() {
    console.log('[设置页面] 初始化页面');
}

/**
 * 绑定事件监听
 */
function bindEvents() {
    // 单选框变化事件
    const radioInputs = document.querySelectorAll('input[name="cleanupStrategy"]');
    radioInputs.forEach(radio => {
        radio.addEventListener('change', onStrategyChange);
    });
    
    // 保存按钮点击事件
    const saveBtn = document.getElementById('saveBtn');
    saveBtn.addEventListener('click', saveSettings);
}

/**
 * 策略选择变化事件
 */
function onStrategyChange(event) {
    const strategy = event.target.value;
    const timeSelector = document.getElementById('timeSelector');
    
    // 显示/隐藏时间选择器
    if (strategy === 'daily' || strategy === 'weekly') {
        timeSelector.style.display = 'block';
    } else {
        timeSelector.style.display = 'none';
    }
    
    console.log('[设置页面] 策略变更:', strategy);
}

/**
 * 加载当前设置
 */
async function loadCurrentSettings() {
    try {
        console.log('[设置页面] 加载当前设置');
        
        const response = await fetch('/api/settings/log-cleanup');
        const data = await response.json();
        
        if (data.success) {
            // 设置单选框
            const radio = document.querySelector(`input[name="cleanupStrategy"][value="${data.strategy}"]`);
            if (radio) {
                radio.checked = true;
                // 触发变化事件以显示/隐藏时间选择器
                radio.dispatchEvent(new Event('change'));
            }
            
            // 设置清理时间
            if (data.cleanupTime) {
                document.getElementById('cleanupTime').value = data.cleanupTime;
            }
            
            console.log('[设置页面] 当前策略:', data.strategy);
        }
    } catch (error) {
        console.error('[设置页面] 加载设置失败:', error);
    }
}

/**
 * 保存设置
 */
async function saveSettings() {
    const saveBtn = document.getElementById('saveBtn');
    const saveBtnText = document.getElementById('saveBtnText');
    const saveBtnLoading = document.getElementById('saveBtnLoading');
    const successSection = document.getElementById('successSection');
    const errorSection = document.getElementById('errorSection');
    
    try {
        // 隐藏之前的提示
        successSection.style.display = 'none';
        errorSection.style.display = 'none';
        
        // 显示加载状态
        saveBtn.disabled = true;
        saveBtnText.style.display = 'none';
        saveBtnLoading.style.display = 'inline-block';
        
        // 获取选中的策略
        const selectedRadio = document.querySelector('input[name="cleanupStrategy"]:checked');
        const strategy = selectedRadio.value;
        
        // 获取清理时间
        const cleanupTime = document.getElementById('cleanupTime').value;
        
        console.log('[设置页面] 保存设置:', { strategy, cleanupTime });
        
        // 发送请求
        const response = await fetch('/api/settings/log-cleanup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                strategy: strategy,
                cleanupTime: cleanupTime
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 显示成功提示
            document.getElementById('successMessage').textContent = data.message || '设置已保存成功';
            successSection.style.display = 'block';
            
            // 如果是立即清理,刷新日志状态
            if (strategy === 'immediate') {
                setTimeout(() => {
                    loadLogStatus();
                }, 500);
            }
            
            console.log('[设置页面] 设置保存成功');
        } else {
            throw new Error(data.error || '保存失败');
        }
    } catch (error) {
        console.error('[设置页面] 保存设置失败:', error);
        
        // 显示错误提示
        document.getElementById('errorMessage').textContent = error.message || '保存设置失败,请重试';
        errorSection.style.display = 'block';
    } finally {
        // 恢复按钮状态
        saveBtn.disabled = false;
        saveBtnText.style.display = 'inline-block';
        saveBtnLoading.style.display = 'none';
    }
}

/**
 * 加载日志状态
 */
async function loadLogStatus() {
    try {
        console.log('[设置页面] 加载日志状态');
        
        const response = await fetch('/api/logs/status');
        const data = await response.json();
        
        if (data.success) {
            // 更新日志状态显示
            document.getElementById('logPath').textContent = data.logPath || '-';
            document.getElementById('logCount').textContent = data.logCount || '0';
            document.getElementById('logSize').textContent = formatFileSize(data.logSize || 0);
            document.getElementById('lastUpdate').textContent = data.lastUpdate || '-';
            
            console.log('[设置页面] 日志状态:', data);
        }
    } catch (error) {
        console.error('[设置页面] 加载日志状态失败:', error);
    }
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

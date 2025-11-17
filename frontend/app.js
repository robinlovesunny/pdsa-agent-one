/**
 * PDSA数字分身智能体 - 前端交互逻辑
 * 
 * 功能说明:
 * 1. 处理用户输入和发送消息
 * 2. 调用后端API获取AI回复
 * 3. 管理对话历史(内存存储)
 * 4. 渲染消息到界面
 * 5. 处理错误和加载状态
 */

// ========================================
// 全局变量
// ========================================

// 对话历史数组 - 存储在内存中
// 格式: [{"user": "问题", "bot": "回答"}, ...]
let chatHistory = [];

// DOM元素引用
let messagesContainer;
let userInput;
let sendBtn;

// API配置
const API_BASE_URL = '';  // 空字符串表示使用当前域名
const CHAT_API = '/api/chat';

// ========================================
// 页面加载完成后初始化
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    messagesContainer = document.getElementById('messagesContainer');
    userInput = document.getElementById('userInput');
    sendBtn = document.getElementById('sendBtn');
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 聚焦输入框
    userInput.focus();
});

// ========================================
// 事件监听器绑定
// ========================================
function bindEventListeners() {
    // 发送按钮点击事件
    sendBtn.addEventListener('click', handleSendMessage);
    
    // 输入框回车事件
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
}

// ========================================
// 发送消息处理函数
// ========================================
async function handleSendMessage() {
    // 获取用户输入
    const message = userInput.value.trim();
    
    // 验证输入非空
    if (!message) {
        return;
    }
    
    // 禁用输入控件,防止重复发送
    setInputsDisabled(true);
    
    // 清空输入框
    userInput.value = '';
    
    // 显示用户消息
    addMessage(message, 'user');
    
    // 显示AI思考中的占位消息
    const thinkingMsg = addMessage('AI思考中...', 'bot');
    
    try {
        // 调用后端API
        const reply = await callChatAPI(message);
        
        // 移除占位消息
        removeMessage(thinkingMsg);
        
        // 显示AI回复
        addMessage(reply, 'bot');
        
        // 更新对话历史
        chatHistory.push({
            user: message,
            bot: reply
        });
        
    } catch (error) {
        // 移除占位消息
        removeMessage(thinkingMsg);
        
        // 显示错误消息
        addMessage(`错误: ${error.message}`, 'error');
    } finally {
        // 重新启用输入控件
        setInputsDisabled(false);
        
        // 聚焦输入框
        userInput.focus();
    }
}

// ========================================
// 调用后端API
// ========================================
async function callChatAPI(message) {
    /**
     * 调用后端/api/chat接口获取AI回复
     * 
     * 参数:
     *   message (string): 用户当前问题
     * 
     * 返回:
     *   string: AI回复内容
     * 
     * 异常:
     *   抛出Error对象,包含错误描述
     */
    try {
        const response = await fetch(CHAT_API, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: chatHistory  // 传递完整对话历史
            })
        });
        
        // 检查HTTP状态码
        if (!response.ok) {
            throw new Error(`HTTP错误! 状态码: ${response.status}`);
        }
        
        // 解析JSON响应
        const data = await response.json();
        
        // 检查业务逻辑是否成功
        if (!data.success) {
            throw new Error(data.error || '未知错误');
        }
        
        return data.reply;
        
    } catch (error) {
        // 网络错误或其他异常
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('网络连接失败,请检查服务器是否运行');
        }
        throw error;
    }
}

// ========================================
// 消息渲染函数
// ========================================
function addMessage(text, type) {
    /**
     * 添加消息到消息列表
     * 
     * 参数:
     *   text (string): 消息文本
     *   type (string): 消息类型 - 'user'用户 | 'bot'AI | 'error'错误
     * 
     * 返回:
     *   HTMLElement: 创建的消息DOM元素
     */
    
    // 创建消息容器
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    // 创建消息内容
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // 处理引用标记并渲染
    if (type === 'bot') {
        try {
            let processedText = text;
            
            // 先处理引用标记，避免被转义
            processedText = processedText.replace(
                /<ref>\[(\d+)\]<\/ref>/g,
                '<sup class="reference" title="点击查看引用来源">[$1]</sup>'
            );
            
            // 使用marked渲染Markdown (兼容判断)
            if (typeof marked !== 'undefined') {
                // 兼容marked v11+和v10-的版本
                if (typeof marked.parse === 'function') {
                    contentDiv.innerHTML = marked.parse(processedText);
                } else if (typeof marked === 'function') {
                    contentDiv.innerHTML = marked(processedText);
                } else {
                    throw new Error('marked库加载异常');
                }
            } else {
                // 降级方案：如果marked未加载，使用原有逻辑
                console.warn('[Markdown] marked库未加载，使用降级渲染');
                contentDiv.innerHTML = formatReferences(escapeHTML(processedText));
            }
        } catch (error) {
            // 错误处理：如果Markdown渲染失败，使用原有逻辑
            console.error('[Markdown] 渲染失败:', error);
            contentDiv.innerHTML = formatReferences(escapeHTML(text));
        }
    } else {
        contentDiv.textContent = text;
    }
    
    // 组装DOM结构
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    
    // 滚动到底部
    scrollToBottom();
    
    return messageDiv;
}

// ========================================
// 移除消息函数
// ========================================
function removeMessage(messageElement) {
    /**
     * 从DOM中移除指定的消息元素
     * 
     * 参数:
     *   messageElement (HTMLElement): 要移除的消息元素
     */
    if (messageElement && messageElement.parentNode) {
        messageElement.parentNode.removeChild(messageElement);
    }
}

// ========================================
// 滚动到底部
// ========================================
function scrollToBottom() {
    /**
     * 将消息列表滚动到最底部
     * 使用smooth平滑滚动效果
     */
    messagesContainer.scrollTo({
        top: messagesContainer.scrollHeight,
        behavior: 'smooth'
    });
}

// ========================================
// 控制输入状态
// ========================================
function setInputsDisabled(disabled) {
    /**
     * 启用或禁用输入控件
     * 
     * 参数:
     *   disabled (boolean): true禁用, false启用
     */
    userInput.disabled = disabled;
    sendBtn.disabled = disabled;
    
    // 更新按钮文本
    if (disabled) {
        sendBtn.textContent = '发送中...';
    } else {
        sendBtn.textContent = '发送';
    }
}

// ========================================
// 工具函数 - 转义HTML
// ========================================
function escapeHTML(text) {
    /**
     * 转义HTML特殊字符,防止XSS攻击
     * 
     * 参数:
     *   text (string): 原始文本
     * 
     * 返回:
     *   string: 转义后的文本
     */
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========================================
// 工具函数 - 格式化引用标记
// ========================================
function formatReferences(text) {
    /**
     * 将<ref>[数字]</ref>格式的引用标记转换为上标样式
     * 
     * 参数:
     *   text (string): 已转义的HTML文本
     * 
     * 返回:
     *   string: 处理后的HTML文本
     * 
     * 示例:
     *   输入: "这是内容&lt;ref&gt;[1]&lt;/ref&gt;"
     *   输出: "这是内容<sup class='reference'>[1]</sup>"
     */
    // 匹配 &lt;ref&gt;[数字]&lt;/ref&gt; 格式
    return text.replace(
        /&lt;ref&gt;\[(\d+)\]&lt;\/ref&gt;/g,
        '<sup class="reference" title="点击查看引用来源">[$1]</sup>'
    );
}

// ========================================
// 调试函数 - 查看对话历史
// ========================================
function debugHistory() {
    /**
     * 在控制台打印当前对话历史
     * 用于调试,可在浏览器控制台调用
     */
    console.log('=== 当前对话历史 ===');
    console.log(JSON.stringify(chatHistory, null, 2));
    console.log(`总计 ${chatHistory.length} 轮对话`);
}

// 将调试函数暴露到全局作用域
window.debugHistory = debugHistory;

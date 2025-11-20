"""
PDSA数字分身智能体 - Flask后端主程序

功能说明:
1. 提供Web聊天界面的后端API服务
2. 集成阿里云百炼RAG应用进行智能对话
3. 记录对话日志到本地文件
4. 服务静态前端文件

作者: PDSA Team
版本: v1.0
"""

import os
import json
import re
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from http import HTTPStatus
from dashscope import Application
import requests
from bs4 import BeautifulSoup
import threading
import schedule

# ========================================
# 配置加载区域
# ========================================
# 从.env文件加载环境变量
# 请确保.env文件存在且包含必需的配置项
# 配置模板参见: backend/.env.example

# 加载.env文件
load_dotenv()

# ========================================
# 阿里云AccessKey配置
# ========================================
# 用途: 调用阿里云百炼API的身份认证凭证
# 获取: 阿里云控制台 -> AccessKey管理 -> 创建AccessKey
# 链接: https://ram.console.aliyun.com/manage/ak
ACCESS_KEY_ID = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
ACCESS_KEY_SECRET = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')

# ========================================
# 百炼应用ID配置
# ========================================
# 用途: 指定要调用的百炼应用(需预先在百炼平台创建并关联知识库)
# 获取: 百炼控制台 -> 应用中心 -> 选择应用 -> 复制应用ID
# 链接: https://bailian.console.aliyun.com/
APP_ID = os.getenv('BAILIAN_APP_ID')

# ========================================
# Flask应用配置
# ========================================
# FLASK_ENV: 运行环境(development/production)
# FLASK_PORT: 服务监听端口,默认5000
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

# ========================================
# 配置验证
# ========================================
# 验证必需的配置项是否已正确设置
# 如果缺失关键配置,抛出明确的错误提示指引用户

if not ACCESS_KEY_ID or ACCESS_KEY_ID == 'your_access_key_id_here':
    raise ValueError(
        "❌ 缺少配置: ALIBABA_CLOUD_ACCESS_KEY_ID\n"
        "请在backend/.env文件中配置阿里云AccessKey ID\n"
        "获取方式: https://ram.console.aliyun.com/manage/ak\n"
        "参考文件: backend/.env.example"
    )

if not ACCESS_KEY_SECRET or ACCESS_KEY_SECRET == 'your_access_key_secret_here':
    raise ValueError(
        "❌ 缺少配置: ALIBABA_CLOUD_ACCESS_KEY_SECRET\n"
        "请在backend/.env文件中配置阿里云AccessKey Secret\n"
        "获取方式: https://ram.console.aliyun.com/manage/ak\n"
        "参考文件: backend/.env.example"
    )

if not APP_ID or APP_ID == 'your_bailian_app_id_here':
    raise ValueError(
        "❌ 缺少配置: BAILIAN_APP_ID\n"
        "请在backend/.env文件中配置百炼应用ID\n"
        "获取方式: https://bailian.console.aliyun.com/ -> 应用中心\n"
        "参考文件: backend/.env.example"
    )

# ========================================
# Flask应用初始化
# ========================================
app = Flask(__name__, static_folder='../frontend')
CORS(app)  # 启用跨域支持,允许前端访问API

# 设置日志文件路径
LOG_FILE = os.path.join(os.path.dirname(__file__), 'chat_logs.txt')

# 设置配置文件路径
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

# 设置文档存储目录
DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')

# 确保docs目录存在
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)

# 百炼文档整理应用配置
# 注意: 如果下面的APP_ID无法使用,将会降级使用现有的百炼应用
DOC_APP_ID = os.getenv('DOC_APP_ID', 'af2071542ff0433c92d8c0d3f18595ce')
DOC_API_KEY = os.getenv('DOC_API_KEY', 'sk-2b88c624bb4748e8b058f49a9d4c33f1')

# 默认设置
DEFAULT_SETTINGS = {
    'logCleanup': {
        'strategy': 'never',  # never, daily, weekly, immediate
        'cleanupTime': '02:00'  # 清理时间
    }
}


# ========================================
# 工具函数
# ========================================

def fetch_web_content(url):
    """
    爬取网页内容
    
    参数:
        url (str): 网页URL
    
    返回:
        str: 提取的文本内容
    """
    try:
        print(f"[DEBUG] 开始爬取网页: {url}")
        
        # 设置请求头,模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 发送请求
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除script和style标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 提取文本内容
        text = soup.get_text()
        
        # 清理空白字符
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        print(f"[DEBUG] 成功提取内容,长度: {len(text)}")
        return text
        
    except requests.RequestException as e:
        error_msg = f"网页爬取失败: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"内容解析失败: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise Exception(error_msg)


def generate_unique_filename(base_name, docs_dir):
    """
    生成唯一的文件名,如果文件已存在则递增编号
    
    参数:
        base_name (str): 基础文件名
        docs_dir (str): 文档目录路径
    
    返回:
        str: 唯一的文件名
    """
    # 清理文件名,移除特殊字符
    base_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5_-]', '', base_name)
    if not base_name:
        base_name = 'document'
    
    # 添加时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{timestamp}.md"
    
    # 检查文件是否存在,如果存在则递增编号
    counter = 1
    while os.path.exists(os.path.join(docs_dir, filename)):
        filename = f"{base_name}_{timestamp}_{counter}.md"
        counter += 1
    
    print(f"[DEBUG] 生成唯一文件名: {filename}")
    return filename


# ========================================
# 百炼API调用函数
# ========================================

def call_doc_generation_api(prompt):
    """
    调用百炼文档整理API
    
    参数:
        prompt (str): 提示词
    
    返回:
        str: 生成的Markdown内容
    """
    try:
        print("[DEBUG] 开始调用Application.call...")
        print(f"[DEBUG] 使用API Key: {DOC_API_KEY[:20]}...")
        print(f"[DEBUG] 使用APP ID: {DOC_APP_ID}")
        
        # 调用DashScope Application API
        # Application.call返回ApplicationResponse对象或生成器(取决于stream参数)
        response = Application.call(
            api_key=DOC_API_KEY,
            app_id=DOC_APP_ID,
            prompt=prompt
        )
        
        print(f"[DEBUG] 响应类型: {type(response)}")
        
        # 直接访问ApplicationResponse对象
        if hasattr(response, 'status_code'):
            print(f"[DEBUG] API响应状态码: {response.status_code}")  # type: ignore
            
            # 检查响应状态
            if response.status_code != HTTPStatus.OK:  # type: ignore
                error_msg = f"request_id={response.request_id}, code={response.status_code}, message={response.message}"  # type: ignore
                print(f"[ERROR] API调用失败: {error_msg}")
                raise Exception(f"API调用失败: {response.message}")  # type: ignore
            
            # 直接从response.output.text获取内容
            if hasattr(response, 'output') and hasattr(response.output, 'text'):  # type: ignore
                markdown_content = response.output.text  # type: ignore
                print(f"[DEBUG] AI生成内容长度: {len(markdown_content)}")
                return markdown_content
            else:
                print(f"[ERROR] 响应对象结构: {vars(response)}")
                raise Exception("response.output.text不存在")
        else:
            raise Exception(f"未知的响应类型: {type(response)}")
            
    except Exception as e:
        error_msg = f"百炼文档API调用失败: {str(e)}"
        print(f"[ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        raise


def call_bailian_api(user_message, chat_history):
    """
    调用阿里云百炼应用API获取智能回复
    
    参数说明:
        user_message (str): 用户当前输入的问题
        chat_history (list): 历史对话列表,格式: [{"user": "...", "bot": "..."}]
    
    返回值:
        str: AI生成的回复内容
    
    配置依赖:
        - ACCESS_KEY_SECRET: 百炼API Key (从环境变量加载)
        - APP_ID: 百炼应用ID (从环境变量加载)
    
    异常处理:
        - 网络错误: 返回友好提示信息
        - 认证失败: 检查API Key配置
        - 应用不存在: 检查APP_ID配置
    
    DashScope API文档:
        https://help.aliyun.com/zh/model-studio/call-single-agent-application/
    """
    try:
        # 确保配置存在
        if not ACCESS_KEY_SECRET or not APP_ID:
            return "配置错误: 缺少API Key或应用ID"
        
        print(f"[DEBUG] 调用百炼API - APP_ID: {APP_ID}")
        print(f"[DEBUG] 用户问题: {user_message}")
        print(f"[DEBUG] 历史对话数量: {len(chat_history)}")
        
        # 调用DashScope Application API
        print("[DEBUG] 开始调用Application.call...")
        response = Application.call(
            api_key=ACCESS_KEY_SECRET,
            app_id=APP_ID,
            prompt=user_message
        )
        
        print(f"[DEBUG] 响应类型: {type(response)}")
        
        # 直接访问ApplicationResponse对象
        if hasattr(response, 'status_code'):
            print(f"[DEBUG] API响应状态码: {response.status_code}")  # type: ignore
            
            # 检查响应状态
            if response.status_code != HTTPStatus.OK:  # type: ignore
                error_msg = f"request_id={response.request_id}, code={response.status_code}, message={response.message}"  # type: ignore
                print(f"[ERROR] API调用失败: {error_msg}")
                return f"抱歉,AI服务暂时不可用。\n错误信息: {response.message}"  # type: ignore
            
            # 提取AI回复
            if hasattr(response, 'output') and hasattr(response.output, 'text'):  # type: ignore
                ai_reply = response.output.text  # type: ignore
                print(f"[DEBUG] AI回复: {ai_reply}")
                return ai_reply
            else:
                return "AI服务返回格式异常"
        else:
            return "AI服务返回类型异常"
            
    except Exception as e:
        # 记录错误日志
        error_msg = f"百炼API调用失败: {str(e)}"
        log_chat("[ERROR]", error_msg, "")
        
        # 返回友好的错误提示
        return f"抱歉,AI服务暂时不可用。错误信息: {str(e)}"


# ========================================
# 日志记录函数
# ========================================
def log_chat(user_message, bot_reply, prefix=""):
    """
    记录对话内容到本地日志文件
    
    参数:
        user_message (str): 用户消息
        bot_reply (str): AI回复
        prefix (str): 日志前缀,用于标记特殊日志(如错误)
    
    日志格式:
        [时间戳]
        用户: 问题内容
        AI: 回复内容
        ---
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{prefix}[{timestamp}]\n用户: {user_message}\nAI: {bot_reply}\n---\n\n"
        
        # 追加写入日志文件
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"日志记录失败: {e}")


def load_settings():
    """
    加载系统设置
    
    返回:
        dict: 设置字典
    """
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return DEFAULT_SETTINGS.copy()
    except Exception as e:
        print(f"加载设置失败: {e}")
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """
    保存系统设置
    
    参数:
        settings (dict): 设置字典
    """
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存设置失败: {e}")
        return False


def clear_log_file():
    """
    清空日志文件
    """
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write('')
        print(f"[日志清理] 日志文件已清空")
        return True
    except Exception as e:
        print(f"[日志清理] 清空日志失败: {e}")
        return False


def get_log_stats():
    """
    获取日志文件统计信息
    
    返回:
        dict: 日志统计信息
    """
    try:
        if not os.path.exists(LOG_FILE):
            return {
                'logPath': LOG_FILE,
                'logCount': 0,
                'logSize': 0,
                'lastUpdate': '-'
            }
        
        # 获取文件大小
        file_size = os.path.getsize(LOG_FILE)
        
        # 获取最后修改时间
        last_update_timestamp = os.path.getmtime(LOG_FILE)
        last_update = datetime.fromtimestamp(last_update_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        # 统计日志条数(通过分隔符"---"计数)
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            log_count = content.count('---')
        
        return {
            'logPath': LOG_FILE,
            'logCount': log_count,
            'logSize': file_size,
            'lastUpdate': last_update
        }
    except Exception as e:
        print(f"获取日志统计失败: {e}")
        return {
            'logPath': LOG_FILE,
            'logCount': 0,
            'logSize': 0,
            'lastUpdate': '-'
        }


def schedule_log_cleanup():
    """
    定时任务:根据设置执行日志清理
    """
    settings = load_settings()
    strategy = settings.get('logCleanup', {}).get('strategy', 'never')
    cleanup_time = settings.get('logCleanup', {}).get('cleanupTime', '02:00')
    
    # 清除之前的所有任务
    schedule.clear()
    
    if strategy == 'daily':
        # 每天定时清理
        schedule.every().day.at(cleanup_time).do(clear_log_file)
        print(f"[定时任务] 已设置每天{cleanup_time}清理日志")
    elif strategy == 'weekly':
        # 每周一定时清理
        schedule.every().monday.at(cleanup_time).do(clear_log_file)
        print(f"[定时任务] 已设置每周一{cleanup_time}清理日志")
    elif strategy == 'never':
        print(f"[定时任务] 日志清理已禁用")


def run_schedule():
    """
    在后台线程中运行定时任务
    """
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


# ========================================
# API路由定义
# ========================================

@app.route('/')
def index():
    """
    主页路由 - 返回前端HTML页面
    """
    if app.static_folder:
        return send_from_directory(app.static_folder, 'index.html')
    return "Static folder not configured", 500


@app.route('/<path:path>')
def static_files(path):
    """
    静态文件路由 - 提供前端资源(CSS, JS等)
    """
    if app.static_folder:
        return send_from_directory(app.static_folder, path)
    return "Static folder not configured", 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    
    用途: 检查服务是否正常运行
    响应: {"status": "ok", "message": "Service is running"}
    """
    return jsonify({
        "status": "ok",
        "message": "Service is running"
    })


@app.route('/api/admin/generate-doc', methods=['POST'])
def generate_doc():
    """
    管理员文档生成接口
    
    请求格式:
        POST /api/admin/generate-doc
        Content-Type: application/json
        {
            "url": "网页URL(可选)",
            "content": "网页内容(可选)",
            "fileName": "文件名(可选)"
        }
    
    响应格式:
        成功: {
            "success": true,
            "filePath": "docs/xxx.md",
            "markdown": "生成的Markdown内容",
            "createTime": "2024-01-01 12:00:00"
        }
        失败: {"success": false, "error": "错误描述"}
    """
    try:
        data = request.get_json()
        
        # 获取输入参数,处理None情况
        url = (data.get('url') or '').strip()
        content = (data.get('content') or '').strip()
        file_name = (data.get('fileName') or '').strip()
        
        # 验证输入
        if not url and not content:
            return jsonify({
                "success": False,
                "error": "请提供URL或内容"
            }), 400
        
        # 获取网页内容
        if url:
            print(f"[DEBUG] 用户提供URL: {url}")
            try:
                # 爬取网页内容
                content = fetch_web_content(url)
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"网页爬取失败: {str(e)}"
                }), 400
        
        # 构建提示词
        prompt = f"""请帮我将以下内容整理为标准的Markdown格式文档:

{content}

要求:
1. 提取核心内容,去除广告和无关信息
2. 使用标准Markdown语法格式化
3. 保持内容层级结构清晰
4. 包含标题、段落、列表等元素
5. 直接输出Markdown内容,不需要额外说明
"""
        
        # 调用百炼API生成Markdown
        print(f"[DEBUG] 调用文档整理API - APP_ID: {DOC_APP_ID}")
        print(f"[DEBUG] Prompt内容长度: {len(prompt)}字符")
        
        markdown_content = call_doc_generation_api(prompt)
        
        # 生成文件名
        if not file_name:
            # 从URL提取标题作为文件名
            if url:
                # 尝试从URL路径提取有意义的部分
                url_path = url.rstrip('/').split('/')[-1]
                if url_path and url_path != url:
                    file_name = url_path.split('?')[0].split('#')[0]
                else:
                    file_name = 'document'
            else:
                # 从内容第一行提取
                first_line = content.split('\n')[0][:30]
                file_name = first_line or 'document'
        
        # 生成唯一文件名
        final_file_name = generate_unique_filename(file_name, DOCS_DIR)
        
        # 保存到docs目录
        file_path = os.path.join(DOCS_DIR, final_file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"[DEBUG] 文档已保存: {file_path}")
        
        # 记录日志
        create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{create_time}] 文档生成成功: {final_file_name}\n"
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # 返回成功响应
        return jsonify({
            "success": True,
            "filePath": f"docs/{final_file_name}",
            "markdown": markdown_content,
            "createTime": create_time
        })
        
    except Exception as e:
        error_msg = f"生成文档失败: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500


@app.route('/api/settings/log-cleanup', methods=['GET', 'POST'])
def log_cleanup_settings():
    """
    日志清理设置接口
    
    GET: 获取当前设置
    POST: 保存新设置
    
    请求格式(POST):
        {
            "strategy": "never|daily|weekly|immediate",
            "cleanupTime": "HH:MM"
        }
    
    响应格式:
        成功: {"success": true, "strategy": "...", "cleanupTime": "..."}
        失败: {"success": false, "error": "..."}
    """
    try:
        if request.method == 'GET':
            # 获取当前设置
            settings = load_settings()
            log_cleanup = settings.get('logCleanup', DEFAULT_SETTINGS['logCleanup'])
            
            return jsonify({
                "success": True,
                "strategy": log_cleanup.get('strategy', 'never'),
                "cleanupTime": log_cleanup.get('cleanupTime', '02:00')
            })
        
        else:  # POST
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "success": False,
                    "error": "缺少请求数据"
                }), 400
            
            strategy = data.get('strategy')
            cleanup_time = data.get('cleanupTime', '02:00')
            
            # 验证策略
            if strategy not in ['never', 'daily', 'weekly', 'immediate']:
                return jsonify({
                    "success": False,
                    "error": "无效的清理策略"
                }), 400
            
            # 加载当前设置
            settings = load_settings()
            
            # 更新设置
            settings['logCleanup'] = {
                'strategy': strategy,
                'cleanupTime': cleanup_time
            }
            
            # 保存设置
            if not save_settings(settings):
                return jsonify({
                    "success": False,
                    "error": "保存设置失败"
                }), 500
            
            # 如果是立即清理,执行清理操作
            if strategy == 'immediate':
                clear_log_file()
                message = "日志已立即清空"
                # 清空后将策略重置为never
                settings['logCleanup']['strategy'] = 'never'
                save_settings(settings)
            else:
                message = "设置已保存"
                # 重新安排定时任务
                schedule_log_cleanup()
            
            return jsonify({
                "success": True,
                "message": message,
                "strategy": strategy,
                "cleanupTime": cleanup_time
            })
    
    except Exception as e:
        error_msg = f"处理请求失败: {str(e)}"
        print(error_msg)
        return jsonify({
            "success": False,
            "error": "服务器错误"
        }), 500


@app.route('/api/logs/status', methods=['GET'])
def log_status():
    """
    日志状态查询接口
    
    响应格式:
        {
            "success": true,
            "logPath": "路径",
            "logCount": 数量,
            "logSize": 字节数,
            "lastUpdate": "时间"
        }
    """
    try:
        stats = get_log_stats()
        
        return jsonify({
            "success": True,
            **stats
        })
    
    except Exception as e:
        error_msg = f"获取日志状态失败: {str(e)}"
        print(error_msg)
        return jsonify({
            "success": False,
            "error": "服务器错误"
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    对话接口 - 核心API
    
    请求格式:
        POST /api/chat
        Content-Type: application/json
        {
            "message": "用户问题",
            "history": [
                {"user": "历史问题1", "bot": "历史回答1"},
                {"user": "历史问题2", "bot": "历史回答2"}
            ]
        }
    
    响应格式:
        成功: {"success": true, "reply": "AI回复内容"}
        失败: {"success": false, "error": "错误描述"}
    
    HTTP状态码:
        200: 成功返回AI回复
        400: 请求参数错误
        500: 服务器内部错误
    """
    try:
        # 1. 解析请求参数
        data = request.get_json()
        
        # 验证必需参数
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "缺少必需参数: message"
            }), 400
        
        user_message = data['message']
        chat_history = data.get('history', [])  # 历史对话,默认为空列表
        
        # 验证消息非空
        if not user_message or not user_message.strip():
            return jsonify({
                "success": False,
                "error": "消息内容不能为空"
            }), 400
        
        # 2. 调用百炼API获取回复
        bot_reply = call_bailian_api(user_message, chat_history)
        
        # 3. 记录对话日志
        log_chat(user_message, bot_reply)
        
        # 4. 返回成功响应
        return jsonify({
            "success": True,
            "reply": bot_reply
        })
        
    except Exception as e:
        # 记录错误
        error_msg = f"处理请求时出错: {str(e)}"
        print(error_msg)
        log_chat("", error_msg, "[ERROR] ")
        
        # 返回错误响应
        return jsonify({
            "success": False,
            "error": "服务器错误,请稍后重试"
        }), 500


# ========================================
# 应用启动入口
# ========================================
if __name__ == '__main__':
    print("=" * 60)
    print("🤖 PDSA数字分身智能体启动中...")
    print("=" * 60)
    print(f"📌 运行环境: {FLASK_ENV}")
    print(f"📌 监听端口: {FLASK_PORT}")
    print(f"📌 访问地址: http://localhost:{FLASK_PORT}")
    print(f"📌 百炼应用ID: {APP_ID}")
    print("=" * 60)
    print("✅ 配置验证通过,服务器启动中...")
    print("=" * 60)
    
    # 启动定时任务线程
    schedule_log_cleanup()
    schedule_thread = threading.Thread(target=run_schedule, daemon=True)
    schedule_thread.start()
    print("✅ 定时任务线程已启动")
    
    # 启动Flask应用
    # debug: 开发模式下启用调试和热加载
    # host: 0.0.0.0允许外部访问,127.0.0.1仅本地访问
    # port: 监听端口
    app.run(
        debug=(FLASK_ENV == 'development'),
        host='127.0.0.1',
        port=FLASK_PORT
    )

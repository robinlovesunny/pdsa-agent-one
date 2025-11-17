#!/bin/bash

# ============================================
# PDSA数字分身智能体 - 快速启动脚本
# ============================================

echo "============================================"
echo "🤖 PDSA数字分身智能体"
echo "============================================"
echo ""

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3,请先安装Python 3.8+"
    exit 1
fi

echo "✅ Python环境检查通过"
echo ""

# 检查.env文件
if [ ! -f "backend/.env" ]; then
    echo "⚠️  未找到.env配置文件"
    echo "📝 正在从.env.example创建.env文件..."
    cp backend/.env.example backend/.env
    echo ""
    echo "✅ .env文件已创建"
    echo "⚠️  请编辑 backend/.env 文件,填入真实的配置信息:"
    echo "   - ALIBABA_CLOUD_ACCESS_KEY_ID"
    echo "   - ALIBABA_CLOUD_ACCESS_KEY_SECRET"
    echo "   - BAILIAN_APP_ID"
    echo ""
    echo "📚 配置说明请参考: docs/README.md"
    echo ""
    read -p "按回车键继续(配置完成后)..."
fi

echo "============================================"
echo "📦 检查Python依赖..."
echo "============================================"
echo ""

# 进入backend目录
cd backend

# 检查并安装依赖
if pip3 show Flask &> /dev/null; then
    echo "✅ 依赖已安装"
else
    echo "📥 正在安装依赖包(使用清华镜像源)..."
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    
    if [ $? -eq 0 ]; then
        echo "✅ 依赖安装成功"
    else
        echo "❌ 依赖安装失败,请检查网络或手动安装"
        exit 1
    fi
fi

echo ""
echo "============================================"
echo "🚀 启动服务..."
echo "============================================"
echo ""

# 启动Flask应用
python3 app.py

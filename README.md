# 🤖 PDSA数字分身智能体

> 基于阿里云百炼RAG能力的轻量级个人知识库问答系统

## 📖 快速导航

- **完整使用文档**: [docs/README.md](docs/README.md)
- **产品需求文档**: [prd.md](prd.md)
- **技术设计文档**: [.qoder/quests/prd-analysis-web-app-development.md](.qoder/quests/prd-analysis-web-app-development.md)

## 🚀 快速启动

### 方式1: 使用启动脚本(推荐)

```bash
./start.sh
```

### 方式2: 手动启动

```bash
# 1. 配置环境变量
cd backend
cp .env.example .env
# 编辑.env文件,填入真实配置

# 2. 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 3. 启动服务
python app.py
```

### 方式3: 一键安装依赖

```bash
cd backend
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

然后访问: 
- **主页面**: http://localhost:5000
- **管理后台**: http://localhost:5000/admin.html
- **设置页面**: http://localhost:5000/settings.html

## ✅ 配置检查清单

在启动前,请确保完成以下配置:

- [ ] 已在阿里云百炼平台创建应用
- [ ] 已上传知识库文件到百炼平台
- [ ] 已获取百炼应用ID
- [ ] 已获取阿里云AccessKey
- [ ] 已创建 `backend/.env` 文件
- [ ] 已在 `.env` 文件中填入真实配置
- [ ] 已安装Python依赖包

详细配置步骤请参考: [docs/README.md](docs/README.md)

## 📁 项目结构

```
pdsa-agent-one/
├── backend/              # 后端服务
│   ├── app.py           # Flask主程序 ⭐核心文件
│   ├── requirements.txt # Python依赖
│   ├── settings.json    # 后台配置文件
│   └── .env.example     # 环境变量模板
│
├── frontend/             # 前端资源
│   ├── index.html       # 主页面
│   ├── style.css        # 主页样式
│   ├── app.js           # 主页交互逻辑
│   ├── admin.html       # 管理后台页面
│   ├── admin.js         # 后台交互逻辑
│   ├── admin-style.css  # 后台样式
│   ├── settings.html    # 设置页面
│   ├── settings.js      # 设置交互逻辑
│   └── settings-style.css # 设置样式
│
├── knowledge/            # 知识库示例文件
│   ├── about_me.md      # 个人介绍
│   ├── skills.md        # 技能清单
│   └── projects.md      # 项目经历
│
├── docs/                # 文档
│   └── README.md        # 完整使用文档 ⭐必读
│
├── start.sh             # 快速启动脚本
└── README.md            # 本文件
```

## 🔧 核心功能

- ✅ 智能对话 - 基于知识库的问答
- ✅ 多轮对话 - 上下文记忆
- ✅ 日志记录 - 自动保存对话历史
- ✅ 设置管理 - 可视化配置后台参数
- ✅ 管理后台 - 查看对话日志和系统状态
- ✅ 深色主题 - 科技感UI设计
- ✅ 响应式布局 - 适配多种设备

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | HTML/CSS/JavaScript |
| 后端 | Python Flask |
| AI | 阿里云百炼RAG |
| 配置 | python-dotenv |

## 📚 重要说明

### 知识库文件

`knowledge/` 目录下的Markdown文件是**示例文件**,请替换为你自己的真实信息:

1. 编辑这些文件,填入你的个人信息
2. 将修改后的文件上传到阿里云百炼平台
3. 在百炼平台创建应用并关联知识库

### API密钥安全

- ❌ **绝不要**将 `.env` 文件提交到Git仓库
- ✅ `.env` 文件已在 `.gitignore` 中
- ✅ 仅提交 `.env.example` 模板文件

## ❓ 遇到问题?

1. **查看文档**: [docs/README.md](docs/README.md) 中的常见问题部分
2. **检查配置**: 确保 `.env` 文件配置正确
3. **查看日志**: 查看 `backend/chat_logs.txt` 文件
4. **控制台输出**: 查看Flask启动时的输出信息

## 📊 开发进度

- [x] 项目结构搭建
- [x] 后端API开发
- [x] 前端界面开发
- [x] 阿里云百炼集成
- [x] 配置文件和文档
- [x] 知识库示例
- [x] 启动脚本
- [x] 设置管理功能
- [x] 管理后台页面
- [ ] 单元测试
- [ ] 部署到云端

## 🎯 下一步

1. **配置百炼平台** - 上传知识库,创建应用
2. **填写配置文件** - 设置 `.env` 文件
3. **启动应用** - 运行 `./start.sh`
4. **开始对话** - 访问 http://localhost:5000

## 📄 许可证

MIT License

---

**准备好了吗? 让我们开始吧! 🚀**

详细使用说明请查看: [docs/README.md](docs/README.md)

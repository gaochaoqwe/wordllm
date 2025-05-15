# WordLLM Flask

这是一个使用Flask框架开发的WordLLM应用后端，整合了原`wordllm-proxy`和`wordllm-backend`的功能。

## 功能特点

- 文档管理：创建、编辑、删除和下载文档
- 模板管理：创建和使用文档模板
- AI生成：集成OpenAI API进行内容生成
- WebSocket实时通信：支持流式AI响应和实时文档协作
- 文件上传与管理：支持上传和管理文档文件

## 项目结构

```
wordllm-flask/
├── app/                    # 应用主目录
│   ├── api/                # API路由和控制器
│   ├── models/             # 数据库模型
│   ├── services/           # 业务服务
│   ├── utils/              # 工具函数和辅助类
│   ├── websocket/          # WebSocket处理
│   ├── static/             # 静态资源
│   ├── templates/          # 模板文件
│   └── __init__.py         # 应用初始化
├── migrations/             # 数据库迁移文件
├── storage/                # 存储目录
├── uploads/                # 上传文件目录
├── logs/                   # 日志目录
├── config.py               # 配置文件
├── .env                    # 环境变量（本地开发）
├── .env.example            # 环境变量示例
├── requirements.txt        # 依赖包列表
├── run.py                  # 应用入口
└── README.md               # 项目说明
```

## 安装与设置

1. 克隆项目并进入项目目录
```bash
git clone [仓库URL]
cd wordllm-flask
```

2. 创建并激活虚拟环境（可选但推荐）
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/MacOS
source venv/bin/activate
```

3. 安装依赖包
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
# 复制示例环境变量文件
cp .env.example .env
# 编辑.env文件，填入所需的配置
```

5. 初始化数据库
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 运行应用

```bash
python run.py
```

服务器默认运行在 http://localhost:5000

## API文档

### 文档API

- `GET /api/documents` - 获取所有文档
- `GET /api/documents/{id}` - 获取特定文档
- `POST /api/documents` - 创建新文档
- `PUT /api/documents/{id}` - 更新文档
- `DELETE /api/documents/{id}` - 删除文档
- `POST /api/documents/upload` - 上传文档文件
- `GET /api/documents/{id}/download` - 下载文档文件

### 模板API

- `GET /api/templates` - 获取所有模板
- `GET /api/templates/{id}` - 获取特定模板
- `POST /api/templates` - 创建新模板
- `PUT /api/templates/{id}` - 更新模板
- `DELETE /api/templates/{id}` - 删除模板
- `GET /api/templates/default` - 获取默认模板

### AI API

- `GET /api/ai/models` - 获取可用的AI模型
- `POST /api/ai/generate` - 生成AI内容（非流式）
- `POST /api/ai/generate/stream` - 生成AI内容（流式）
- `GET /api/ai/sessions/{sessionId}` - 获取AI会话历史

## WebSocket

### 命名空间

- `/ws` - 一般WebSocket连接
- `/ws/generate/{sessionId}` - AI生成流式响应
- `/ws/document` - 文档实时协作

### 事件

- `connect` - 客户端连接
- `disconnect` - 客户端断开连接
- `subscribe` - 订阅主题
- `unsubscribe` - 取消订阅主题
- `document_update` - 文档更新事件

## 环境变量

请参考`.env.example`文件查看所有可配置的环境变量。

## 许可

[指定许可证类型]

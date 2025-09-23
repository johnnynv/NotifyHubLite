# NotifyHubLite 架构设计文档

## 📋 概述

NotifyHubLite 是一个基于 Python FastAPI 的富文本邮件发送 API 服务，支持发送包含 HTML 内容、内嵌图片、文件附件和 PDF 预览的邮件。

### 🎯 设计目标

- **简单易用**: 提供简洁的 RESTful API 接口
- **功能完整**: 支持富文本、附件、PDF 预览等功能
- **安全可靠**: HTML 安全清理、文件类型验证
- **高性能**: 基于 FastAPI 的异步框架
- **易部署**: 最小化依赖，支持容器化部署

## 🏗️ 技术栈

### 核心框架
- **Web 框架**: FastAPI 0.104+ (异步支持，自动文档生成)
- **ASGI 服务器**: Uvicorn (生产环境配合 Gunicorn)
- **数据库**: PostgreSQL 12+ (企业级数据库)
- **ORM**: SQLAlchemy 2.0 (同步版本)
- **数据库迁移**: Alembic (版本控制和迁移管理)

### 邮件处理
- **SMTP 客户端**: Python 标准库 `smtplib`
- **邮件构建**: Python 标准库 `email.mime`
- **HTML 处理**: `bleach` (安全清理)
- **PDF 处理**: `pdf2image` + `PyPDF2`
- **图片处理**: `Pillow` (压缩、格式转换)

### 其他组件
- **配置管理**: `pydantic-settings`
- **文件上传**: `python-multipart`
- **认证**: 简单 API Key 认证

## 🏛️ 项目结构

```
NotifyHubLite/
├── app/                        # 主应用代码
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库连接
│   │
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   ├── email.py           # 邮件模型
│   │   └── attachment.py      # 附件模型
│   │
│   ├── schemas/               # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── email.py           # 邮件 Schema
│   │   └── attachment.py      # 附件 Schema
│   │
│   ├── api/                   # API 路由
│   │   ├── __init__.py
│   │   ├── emails.py          # 邮件发送 API
│   │   └── attachments.py     # 附件管理 API
│   │
│   ├── services/              # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── email_service.py   # 邮件服务
│   │   ├── html_service.py    # HTML 处理
│   │   ├── attachment_service.py # 附件服务
│   │   └── pdf_service.py     # PDF 处理服务
│   │
│   └── utils/                 # 工具函数
│       ├── __init__.py
│       ├── smtp_client.py     # SMTP 客户端
│       ├── file_utils.py      # 文件工具
│       └── image_utils.py     # 图片工具
│
├── uploads/                   # 文件存储目录
│   ├── images/               # 图片文件
│   ├── attachments/          # 普通附件
│   ├── pdfs/                # PDF 文件
│   └── temp/                # 临时文件
│
├── docs/                     # 项目文档
├── tests/                    # 测试代码
├── requirements.txt          # 依赖列表
├── .env.example             # 环境变量示例
└── README.md                # 项目说明
```

## 🔧 核心服务设计

### 1. EmailService (邮件服务)

**职责**: 邮件发送的核心业务逻辑

**主要方法**:
- `send_email()`: 发送邮件
- `get_email_status()`: 查询邮件状态
- `build_mime_message()`: 构建 MIME 消息

**处理流程**:
```
接收请求 → 处理附件 → 清理HTML → 构建MIME → 发送邮件 → 更新状态
```

### 2. AttachmentService (附件服务)

**职责**: 文件上传、存储和管理

**主要方法**:
- `upload_file()`: 通用文件上传
- `upload_image()`: 图片上传（支持内嵌）
- `get_attachment()`: 获取附件信息
- `delete_attachment()`: 删除附件

**存储策略**:
```
uploads/
├── attachments/2025/09/23/uuid-123_document.pdf
├── images/2025/09/23/uuid-456_logo.png
└── temp/pdf_page_1_uuid-789.png
```

### 3. PDFService (PDF 处理服务)

**职责**: PDF 文件处理和预览生成

**主要方法**:
- `process_pdf()`: 处理 PDF 文件
- `convert_pages_to_images()`: PDF 页面转图片
- `generate_preview_html()`: 生成预览 HTML

**处理流程**:
```
上传PDF → 获取页数 → 转换预览页 → 生成HTML → 保存记录
```

### 4. HTMLService (HTML 处理服务)

**职责**: HTML 内容安全清理和处理

**主要方法**:
- `clean_html()`: HTML 安全清理
- `process_attachments()`: 处理附件引用

## 🗄️ 数据存储设计

### 数据库表

1. **emails** - 邮件记录
2. **attachments** - 附件信息
3. **pdf_previews** - PDF 预览记录

### 文件系统

- **本地存储**: 按日期和类型分类存储
- **文件命名**: UUID + 原始文件名
- **临时文件**: PDF 转换图片的临时存储

## 🔒 安全设计

### 1. 文件安全
- **类型验证**: 严格限制上传文件类型
- **大小限制**: 防止超大文件上传
- **路径安全**: 防止路径遍历攻击

### 2. HTML 安全
- **内容清理**: 使用 `bleach` 库清理 HTML
- **标签白名单**: 只允许安全的 HTML 标签
- **属性过滤**: 移除危险的 HTML 属性

### 3. 认证授权
- **API Key**: 简单的 API Key 认证机制
- **请求验证**: 严格的请求参数验证

## 📧 邮件处理机制

### 1. MIME 消息结构

```
multipart/related
├── text/html (邮件正文)
├── image/png (内嵌图片1) - Content-ID: <cid1>
├── image/jpeg (内嵌图片2) - Content-ID: <cid2>
└── application/pdf (附件)
```

### 2. 内嵌图片机制

**原理**: 图片数据直接嵌入邮件，通过 CID 引用

**流程**:
1. HTML 中使用 `<img src="cid:image1">`
2. 图片作为 MIME 部分添加到邮件
3. 设置 `Content-ID: <image1>`
4. 邮件客户端解析并显示图片

### 3. PDF 预览机制

**策略**: 前 N 页转图片 + 完整 PDF 附件

**处理**:
1. 使用 `pdf2image` 转换前几页
2. 压缩优化图片大小
3. 图片作为内嵌图片发送
4. 原始 PDF 作为附件

## ⚡ 性能考虑

### 1. 文件处理优化
- **图片压缩**: 自动压缩图片以减小邮件大小
- **PDF 优化**: 控制预览页数和 DPI
- **临时文件清理**: 定期清理过期的临时文件

### 2. 数据库优化
- **索引设计**: 为常用查询字段建立索引
- **连接管理**: 使用连接池管理数据库连接

### 3. 错误处理
- **重试机制**: SMTP 发送失败自动重试
- **错误记录**: 详细记录错误信息便于排查

## 🔄 扩展性设计

### MVP 版本特点
- **简单直接**: 避免过早优化
- **功能完整**: 满足基本需求
- **易于维护**: 代码结构清晰

### 后续扩展方向
1. **异步处理**: 引入消息队列处理大量邮件
2. **模板系统**: 支持邮件模板和变量替换
3. **用户管理**: 多用户和权限管理
4. **监控分析**: 发送统计和性能监控
5. **云存储**: 支持 AWS S3 等云存储

## 📊 监控和日志

### 日志策略
- **业务日志**: 邮件发送记录、用户操作
- **错误日志**: 系统错误和异常情况
- **访问日志**: API 访问记录

### 关键指标
- **发送成功率**: 邮件发送成功的比例
- **响应时间**: API 接口响应时间
- **文件大小**: 附件和邮件大小统计

## 🚀 部署架构

### 开发环境
```
FastAPI + PostgreSQL + 本地文件存储
```

### 生产环境
```
FastAPI + PostgreSQL + 本地/云存储 + Nginx + 负载均衡
```

### 容器化部署
```
Docker + Docker Compose
```

---

这个架构设计确保了系统的可维护性、可扩展性和安全性，同时保持了 MVP 版本的简洁性。

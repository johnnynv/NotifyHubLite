# NotifyHubLite 文档

NotifyHubLite 是一个基于 Python FastAPI 的富文本邮件发送 API 服务。

## 📚 文档目录

- [📋 架构设计](architecture.md) - 系统整体架构设计
- [🔌 API 接口文档](api.md) - RESTful API 接口说明
- [🗄️ 数据模型](data-models.md) - 数据库表结构设计
- [🔄 数据库迁移](database-migration.md) - Alembic 迁移管理
- [🤔 数据库必要性](database-necessity.md) - 为什么需要数据库
- [🚀 部署指南](deployment.md) - 环境配置和部署说明
- [📧 Mailu 集成](mailu-integration.md) - Mailu SMTP 服务器集成
- [🏗️ Mailu 架构说明](mailu-architecture.md) - 为什么不需要外部邮件服务
- [⚡ Mailu MVP部署](mailu-mvp.md) - 15分钟快速部署指南
- [📝 实施方案](implementation.md) - 7天完整实施计划
- [💡 使用示例](examples.md) - 实际使用场景示例

## ✨ 核心功能

- ✅ **富文本邮件**: 支持 HTML 内容、表格、样式等
- ✅ **内嵌图片**: 图片直接显示在邮件正文中
- ✅ **文件附件**: 支持各种格式的文件附件
- ✅ **PDF 预览**: PDF 前几页转为图片预览 + 完整 PDF 附件
- ✅ **安全清理**: HTML 内容安全过滤，防止 XSS
- ✅ **状态跟踪**: 邮件发送状态实时查询

## 🎯 MVP 版本

当前设计为 MVP (最小可行产品) 版本，专注于核心功能实现：

- 基于 FastAPI 的高性能 API
- SQLite/PostgreSQL 数据存储
- 本地文件系统存储
- 同步邮件发送处理
- 简单 API Key 认证

## 🔄 后续版本规划

- **V2**: 邮件模板系统
- **V3**: 异步队列处理
- **V4**: 用户管理和权限控制
- **V5**: 监控和分析功能

## 🚀 快速开始

详细的部署和使用说明请参考 [部署指南](deployment.md)。

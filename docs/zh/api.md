# API 接口文档

## 🔌 接口概览

NotifyHubLite 提供 RESTful API 接口，支持邮件发送、附件管理和状态查询功能。

### 基础信息
- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: API Key (Header: `X-API-Key`)
- **数据格式**: JSON
- **字符编码**: UTF-8

## 🔐 认证

所有 API 请求都需要在 Header 中包含 API Key：

```http
X-API-Key: your-api-key-here
```

## 📧 邮件发送接口

### 发送邮件

发送富文本邮件，支持 HTML 内容、内嵌图片和附件。

```http
POST /api/v1/emails/send
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| to | array[string] | ✅ | 收件人邮箱列表 |
| cc | array[string] | ❌ | 抄送邮箱列表 |
| bcc | array[string] | ❌ | 密送邮箱列表 |
| subject | string | ✅ | 邮件主题 |
| text_content | string | ❌ | 纯文本邮件内容 |
| html_content | string | ❌ | HTML 邮件内容 |
| attachments | array[object] | ❌ | 附件列表 |
| pdf_settings | object | ❌ | PDF 处理配置 |

**注意**: `text_content` 和 `html_content` 至少需要提供一个

**attachments 对象结构:**

| 参数 | 类型 | 说明 |
|------|------|------|
| file_id | string | 附件文件 ID |
| type | string | 附件类型: `attachment` / `inline_image` / `pdf_preview` |
| filename | string | 文件名（用于附件显示） |
| cid | string | 内嵌图片的 CID（仅 inline_image 类型需要） |

**pdf_settings 对象结构:**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| preview_pages | integer | 3 | 转换为图片的页数 |
| preview_dpi | integer | 150 | 图片 DPI 质量 |
| include_full_pdf | boolean | true | 是否包含完整 PDF 作为附件 |

**请求示例:**

**纯文本邮件:**
```json
{
  "to": ["user@example.com"],
  "subject": "重要通知",
  "text_content": "亲爱的用户，\n\n这是一封重要通知邮件。\n\n请注意以下事项：\n- 事项1\n- 事项2\n- 事项3\n\n感谢您的配合！\n\n此致\n敬礼"
}
```

**HTML邮件:**
```json
{
  "to": ["user@example.com", "manager@example.com"],
  "cc": ["team@example.com"],
  "subject": "月度工作报告",
  "html_content": "<h1>月度报告</h1><p>请查看以下内容:</p><img src='cid:chart1' style='width:100%;'/><p>详细数据请见附件。</p>",
  "attachments": [
    {
      "file_id": "uuid-123",
      "type": "inline_image",
      "cid": "chart1"
    },
    {
      "file_id": "uuid-456", 
      "type": "attachment",
      "filename": "详细报告.pdf"
    }
  ]
}
```

**多格式邮件（推荐）:**
```json
{
  "to": ["user@example.com"],
  "subject": "产品发布通知",
  "text_content": "新产品已发布！\n\n产品特点：\n- 功能强大\n- 易于使用\n- 性价比高\n\n详情请访问官网。",
  "html_content": "<h1>🎉 新产品已发布！</h1><ul><li><strong>功能强大</strong></li><li><strong>易于使用</strong></li><li><strong>性价比高</strong></li></ul><p><a href='#'>点击查看详情</a></p>"
}
```

**响应示例:**

```json
{
  "success": true,
  "data": {
    "email_id": "email-uuid-789",
    "status": "sent",
    "message": "邮件发送成功",
    "sent_at": "2025-09-23T10:30:00Z",
    "recipients": {
      "to": ["user@example.com", "manager@example.com"],
      "cc": ["team@example.com"],
      "total": 3
    }
  }
}
```

**错误响应:**

```json
{
  "success": false,
  "error": {
    "code": "INVALID_EMAIL",
    "message": "邮箱地址格式不正确: invalid-email",
    "details": {
      "field": "to",
      "value": "invalid-email"
    }
  }
}
```

### 查询邮件状态

查询指定邮件的发送状态和详细信息。

```http
GET /api/v1/emails/{email_id}
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| email_id | string | 邮件 ID |

**响应示例:**

```json
{
  "success": true,
  "data": {
    "email_id": "email-uuid-789",
    "status": "sent",
    "subject": "月度工作报告",
    "recipients": {
      "to": ["user@example.com"],
      "cc": ["team@example.com"],
      "bcc": []
    },
    "attachments": [
      {
        "file_id": "uuid-123",
        "filename": "chart.png",
        "type": "inline_image",
        "file_size": 245760
      }
    ],
    "created_at": "2025-09-23T10:29:45Z",
    "sent_at": "2025-09-23T10:30:00Z",
    "error_message": null
  }
}
```

**状态说明:**

| 状态 | 说明 |
|------|------|
| pending | 等待发送 |
| sending | 发送中 |
| sent | 发送成功 |
| failed | 发送失败 |

## 📎 附件管理接口

### 上传普通附件

上传图片、文档等普通附件文件。

```http
POST /api/v1/attachments/upload
Content-Type: multipart/form-data
```

**表单参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | ✅ | 上传的文件 |
| type | string | ✅ | 文件类型: `image` / `document` |
| is_inline | boolean | ❌ | 是否用作内嵌图片 (默认 false) |

**支持的文件类型:**

- **图片**: JPG, PNG, GIF, WebP (最大 5MB)
- **文档**: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX (最大 25MB)

**响应示例:**

```json
{
  "success": true,
  "data": {
    "file_id": "uuid-123",
    "filename": "logo.png",
    "original_filename": "公司Logo.png",
    "file_size": 245760,
    "mime_type": "image/png",
    "upload_type": "image",
    "is_inline": true,
    "cid": "logo_image",
    "created_at": "2025-09-23T10:15:00Z",
    "expires_at": "2025-10-23T10:15:00Z"
  }
}
```

### 上传 PDF 文件

上传 PDF 文件并自动生成预览图片。

```http
POST /api/v1/attachments/upload-pdf
Content-Type: multipart/form-data
```

**表单参数:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| file | file | ✅ | - | PDF 文件 |
| preview_pages | integer | ❌ | 3 | 转换为图片的页数 |
| preview_dpi | integer | ❌ | 150 | 图片 DPI 质量 |

**响应示例:**

```json
{
  "success": true,
  "data": {
    "file_id": "uuid-456",
    "filename": "report.pdf",
    "total_pages": 8,
    "preview_images": [
      {
        "page": 1,
        "image_id": "uuid-111",
        "cid": "pdf_page_1",
        "file_size": 180432
      },
      {
        "page": 2,
        "image_id": "uuid-222", 
        "cid": "pdf_page_2",
        "file_size": 165890
      },
      {
        "page": 3,
        "image_id": "uuid-333",
        "cid": "pdf_page_3", 
        "file_size": 201245
      }
    ],
    "generated_html": "<div class='pdf-preview'>...</div>",
    "created_at": "2025-09-23T10:20:00Z"
  }
}
```

### 获取附件信息

获取指定附件的详细信息。

```http
GET /api/v1/attachments/{file_id}
```

**响应示例:**

```json
{
  "success": true,
  "data": {
    "file_id": "uuid-123",
    "filename": "document.pdf",
    "original_filename": "工作报告.pdf",
    "file_size": 1048576,
    "mime_type": "application/pdf",
    "upload_type": "document", 
    "is_inline": false,
    "created_at": "2025-09-23T10:15:00Z",
    "expires_at": "2025-10-23T10:15:00Z"
  }
}
```

### 删除附件

删除指定的附件文件。

```http
DELETE /api/v1/attachments/{file_id}
```

**响应示例:**

```json
{
  "success": true,
  "data": {
    "file_id": "uuid-123",
    "message": "附件删除成功"
  }
}
```

## 🏥 系统接口

### 健康检查

检查系统运行状态。

```http
GET /health
```

**响应示例:**

```json
{
  "status": "healthy",
  "timestamp": "2025-09-23T10:45:00Z",
  "version": "1.0.0",
  "components": {
    "database": "healthy",
    "smtp": "healthy",
    "storage": "healthy"
  }
}
```

## 🚨 错误处理

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 404 | 资源不存在 |
| 413 | 文件过大 |
| 415 | 不支持的文件类型 |
| 422 | 参数验证失败 |
| 500 | 服务器内部错误 |

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {
      "field": "错误字段",
      "value": "错误值"
    }
  }
}
```

### 常见错误码

| 错误码 | 说明 |
|--------|------|
| INVALID_API_KEY | API Key 无效 |
| INVALID_EMAIL | 邮箱格式不正确 |
| FILE_TOO_LARGE | 文件过大 |
| UNSUPPORTED_FILE_TYPE | 不支持的文件类型 |
| ATTACHMENT_NOT_FOUND | 附件不存在 |
| SMTP_ERROR | SMTP 发送失败 |
| INTERNAL_ERROR | 系统内部错误 |

## 📝 使用示例

### 示例 1: 发送纯文本邮件

```bash
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["user@example.com"],
    "subject": "测试邮件",
    "html_content": "<h1>Hello World</h1><p>这是一封测试邮件。</p>"
  }'
```

### 示例 2: 发送带图片的邮件

```bash
# 1. 上传图片
curl -X POST "http://localhost:8000/api/v1/attachments/upload" \
  -H "X-API-Key: your-api-key" \
  -F "file=@logo.png" \
  -F "type=image" \
  -F "is_inline=true"

# 响应获得 file_id 和 cid

# 2. 发送邮件
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["user@example.com"],
    "subject": "带图片的邮件",
    "html_content": "<h1>公司Logo</h1><img src=\"cid:logo_image\" style=\"width:200px;\"/>",
    "attachments": [
      {
        "file_id": "uuid-123",
        "type": "inline_image",
        "cid": "logo_image"
      }
    ]
  }'
```

### 示例 3: 发送 PDF 预览邮件

```bash
# 1. 上传 PDF
curl -X POST "http://localhost:8000/api/v1/attachments/upload-pdf" \
  -H "X-API-Key: your-api-key" \
  -F "file=@report.pdf" \
  -F "preview_pages=2"

# 2. 使用返回的 generated_html 和附件信息发送邮件
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["user@example.com"],
    "subject": "PDF报告",
    "html_content": "返回的generated_html内容",
    "attachments": [
      // 预览图片和原始PDF的附件配置
    ]
  }'
```

## 📊 限制说明

### 文件大小限制
- **内嵌图片**: 最大 5MB
- **普通附件**: 最大 25MB
- **PDF 文件**: 最大 20MB

### 数量限制
- **收件人总数**: 最大 100 个
- **附件数量**: 最大 10 个
- **PDF 预览页数**: 最大 10 页

### 其他限制
- **邮件主题**: 最大 200 字符
- **HTML 内容**: 最大 1MB
- **文件保存**: 30 天后自动清理

---

此 API 文档涵盖了 NotifyHubLite 的所有接口功能，更多技术细节请参考 [架构设计文档](architecture.md)。

# 数据模型文档

## 🗄️ 数据库设计

NotifyHubLite 使用 PostgreSQL 数据库存储邮件记录、附件信息和相关元数据。数据库在系统中承担以下关键作用：

- **邮件状态跟踪**：记录邮件发送状态，支持状态查询
- **附件管理**：存储文件元信息，支持文件引用和清理
- **PDF预览记录**：存储PDF转换结果，避免重复处理
- **系统审计**：记录操作日志，支持数据分析
- **数据一致性**：保证多并发环境下的数据完整性

## 📋 表结构设计

### 1. emails 表 - 邮件记录

存储邮件的基本信息和发送状态。

```sql
CREATE TABLE emails (
    id TEXT PRIMARY KEY,                    -- 邮件唯一标识 (UUID)
    to_addresses TEXT NOT NULL,             -- 收件人列表 (JSON数组)
    cc_addresses TEXT,                      -- 抄送列表 (JSON数组)
    bcc_addresses TEXT,                     -- 密送列表 (JSON数组)
    subject TEXT NOT NULL,                  -- 邮件主题
    text_content TEXT,                      -- 纯文本邮件内容
    html_content TEXT,                      -- HTML邮件内容
    attachment_ids TEXT,                    -- 关联附件ID列表 (JSON数组)
    status TEXT DEFAULT 'pending',          -- 发送状态
    error_message TEXT,                     -- 错误信息
    smtp_message_id TEXT,                   -- SMTP消息ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    sent_at TIMESTAMP,                      -- 发送时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- 更新时间
);

-- 索引
CREATE INDEX idx_emails_status ON emails(status);
CREATE INDEX idx_emails_created_at ON emails(created_at);
CREATE INDEX idx_emails_to_addresses ON emails(to_addresses);
```

**字段说明:**

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| id | TEXT | 邮件唯一标识 | `"email-123e4567-e89b-12d3-a456-426614174000"` |
| to_addresses | TEXT | 收件人邮箱JSON数组 | `["user1@example.com", "user2@example.com"]` |
| cc_addresses | TEXT | 抄送邮箱JSON数组 | `["manager@example.com"]` |
| bcc_addresses | TEXT | 密送邮箱JSON数组 | `["admin@example.com"]` |
| subject | TEXT | 邮件主题 | `"月度工作报告"` |
| text_content | TEXT | 纯文本邮件内容 | `"月度报告\n\n本月完成..."` |
| html_content | TEXT | HTML邮件内容 | `"<h1>报告</h1><p>内容...</p>"` |
| attachment_ids | TEXT | 附件ID列表JSON数组 | `["att-uuid-1", "att-uuid-2"]` |
| status | TEXT | 发送状态 | `pending/sending/sent/failed` |
| error_message | TEXT | 错误信息 | `"SMTP连接超时"` |
| smtp_message_id | TEXT | SMTP消息ID | `"<123@mail.example.com>"` |

**状态枚举:**
- `pending`: 等待发送
- `sending`: 发送中  
- `sent`: 发送成功
- `failed`: 发送失败

### 2. attachments 表 - 附件信息

存储所有上传文件的元数据信息。

```sql
CREATE TABLE attachments (
    id TEXT PRIMARY KEY,                    -- 附件唯一标识 (UUID)
    filename TEXT NOT NULL,                 -- 存储文件名
    original_filename TEXT NOT NULL,        -- 原始文件名
    file_path TEXT NOT NULL,               -- 文件存储路径
    file_size INTEGER NOT NULL,            -- 文件大小 (字节)
    mime_type TEXT NOT NULL,               -- MIME类型
    file_hash TEXT,                        -- 文件哈希值 (SHA256)
    upload_type TEXT NOT NULL,             -- 上传类型
    is_inline BOOLEAN DEFAULT FALSE,       -- 是否内嵌
    cid TEXT,                             -- 内嵌图片的Content-ID
    metadata TEXT,                        -- 扩展元数据 (JSON)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    expires_at TIMESTAMP,                  -- 过期时间
    is_deleted BOOLEAN DEFAULT FALSE       -- 软删除标记
);

-- 索引
CREATE INDEX idx_attachments_upload_type ON attachments(upload_type);
CREATE INDEX idx_attachments_created_at ON attachments(created_at);
CREATE INDEX idx_attachments_expires_at ON attachments(expires_at);
CREATE INDEX idx_attachments_file_hash ON attachments(file_hash);
CREATE INDEX idx_attachments_is_deleted ON attachments(is_deleted);
```

**字段说明:**

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| id | TEXT | 附件唯一标识 | `"att-123e4567-e89b-12d3-a456-426614174000"` |
| filename | TEXT | 存储文件名 | `"uuid-123_logo.png"` |
| original_filename | TEXT | 原始文件名 | `"公司Logo.png"` |
| file_path | TEXT | 相对存储路径 | `"uploads/images/2025/09/23/uuid-123_logo.png"` |
| file_size | INTEGER | 文件大小(字节) | `245760` |
| mime_type | TEXT | MIME类型 | `"image/png"` |
| file_hash | TEXT | SHA256哈希 | `"abc123def456..."` |
| upload_type | TEXT | 上传类型 | `image/document/pdf` |
| is_inline | BOOLEAN | 是否内嵌显示 | `true/false` |
| cid | TEXT | Content-ID | `"logo_image"` |
| metadata | TEXT | 扩展信息JSON | `{"width": 800, "height": 600}` |

**upload_type 枚举:**
- `image`: 图片文件
- `document`: 文档文件  
- `pdf`: PDF文件

### 3. pdf_previews 表 - PDF预览记录

存储PDF文件的预览处理记录。

```sql
CREATE TABLE pdf_previews (
    id TEXT PRIMARY KEY,                    -- 预览记录唯一标识
    pdf_attachment_id TEXT NOT NULL,        -- 关联的PDF附件ID
    total_pages INTEGER NOT NULL,           -- PDF总页数
    preview_pages INTEGER NOT NULL,         -- 转换的预览页数
    preview_image_ids TEXT NOT NULL,        -- 预览图片ID列表 (JSON数组)
    generated_html TEXT,                    -- 生成的HTML预览内容
    processing_settings TEXT,               -- 处理参数 (JSON)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (pdf_attachment_id) REFERENCES attachments(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_pdf_previews_pdf_attachment_id ON pdf_previews(pdf_attachment_id);
CREATE INDEX idx_pdf_previews_created_at ON pdf_previews(created_at);
```

**字段说明:**

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| id | TEXT | 预览记录ID | `"prev-123e4567-e89b-12d3-a456-426614174000"` |
| pdf_attachment_id | TEXT | PDF附件ID | `"att-456e7890-e89b-12d3-a456-426614174000"` |
| total_pages | INTEGER | PDF总页数 | `8` |
| preview_pages | INTEGER | 转换页数 | `3` |
| preview_image_ids | TEXT | 预览图片ID列表 | `["img-uuid-1", "img-uuid-2", "img-uuid-3"]` |
| generated_html | TEXT | 生成的HTML | `"<div class='pdf-preview'>...</div>"` |
| processing_settings | TEXT | 处理参数JSON | `{"dpi": 150, "format": "PNG"}` |

## 🔗 表关系图

```
emails
├── attachment_ids ──→ attachments.id (一对多)

attachments
├── id ←── pdf_previews.pdf_attachment_id (一对一)
└── id ←── pdf_previews.preview_image_ids (一对多)
```

## 📊 数据模型类定义

### SQLAlchemy 模型示例

```python
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(String, primary_key=True, default=lambda: f"email-{uuid.uuid4()}")
    to_addresses = Column(Text, nullable=False)  # JSON string
    cc_addresses = Column(Text)
    bcc_addresses = Column(Text)  
    subject = Column(String(500), nullable=False)
    html_content = Column(Text, nullable=False)
    attachment_ids = Column(Text)  # JSON string
    status = Column(String(20), default="pending")
    error_message = Column(Text)
    smtp_message_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Attachment(Base):
    __tablename__ = "attachments"
    
    id = Column(String, primary_key=True, default=lambda: f"att-{uuid.uuid4()}")
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64))
    upload_type = Column(String(20), nullable=False)
    is_inline = Column(Boolean, default=False)
    cid = Column(String(100))
    metadata = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_deleted = Column(Boolean, default=False)

class PDFPreview(Base):
    __tablename__ = "pdf_previews"
    
    id = Column(String, primary_key=True, default=lambda: f"prev-{uuid.uuid4()}")
    pdf_attachment_id = Column(String, ForeignKey("attachments.id"), nullable=False)
    total_pages = Column(Integer, nullable=False)
    preview_pages = Column(Integer, nullable=False)
    preview_image_ids = Column(Text, nullable=False)  # JSON string
    generated_html = Column(Text)
    processing_settings = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    pdf_attachment = relationship("Attachment", backref="pdf_preview")
```

## 📝 Pydantic Schema 模型

### 请求/响应模型

```python
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class EmailStatus(str, Enum):
    PENDING = "pending"
    SENDING = "sending" 
    SENT = "sent"
    FAILED = "failed"

class UploadType(str, Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    PDF = "pdf"

class AttachmentType(str, Enum):
    ATTACHMENT = "attachment"
    INLINE_IMAGE = "inline_image"
    PDF_PREVIEW = "pdf_preview"

# 请求模型
class AttachmentRef(BaseModel):
    file_id: str = Field(..., description="附件文件ID")
    type: AttachmentType = Field(..., description="附件类型")
    filename: Optional[str] = Field(None, description="显示文件名")
    cid: Optional[str] = Field(None, description="内嵌图片CID")

class PDFSettings(BaseModel):
    preview_pages: int = Field(3, ge=1, le=10, description="预览页数")
    preview_dpi: int = Field(150, ge=72, le=300, description="图片DPI")
    include_full_pdf: bool = Field(True, description="是否包含完整PDF")

class EmailSendRequest(BaseModel):
    to: List[EmailStr] = Field(..., max_items=100, description="收件人列表")
    cc: Optional[List[EmailStr]] = Field(None, max_items=50, description="抄送列表")
    bcc: Optional[List[EmailStr]] = Field(None, max_items=50, description="密送列表")
    subject: str = Field(..., max_length=200, description="邮件主题")
    html_content: str = Field(..., max_length=1048576, description="HTML内容")
    attachments: Optional[List[AttachmentRef]] = Field(None, max_items=10, description="附件列表")
    pdf_settings: Optional[PDFSettings] = Field(None, description="PDF处理设置")

# 响应模型
class AttachmentInfo(BaseModel):
    file_id: str
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    upload_type: UploadType
    is_inline: bool
    cid: Optional[str] = None
    created_at: datetime

class EmailInfo(BaseModel):
    email_id: str
    status: EmailStatus
    subject: str
    recipients: dict
    attachments: List[AttachmentInfo]
    created_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

class EmailSendResponse(BaseModel):
    success: bool
    data: Optional[EmailInfo] = None
    error: Optional[dict] = None
```

## 🔍 查询示例

### 常用 SQL 查询

```sql
-- 1. 查询最近发送的邮件
SELECT id, subject, status, created_at 
FROM emails 
WHERE status = 'sent' 
ORDER BY sent_at DESC 
LIMIT 10;

-- 2. 查询发送失败的邮件
SELECT id, subject, error_message, created_at
FROM emails 
WHERE status = 'failed'
ORDER BY created_at DESC;

-- 3. 查询包含附件的邮件
SELECT e.id, e.subject, e.attachment_ids
FROM emails e
WHERE e.attachment_ids IS NOT NULL 
  AND e.attachment_ids != '[]';

-- 4. 查询大文件附件
SELECT id, original_filename, file_size, created_at
FROM attachments 
WHERE file_size > 5242880  -- 5MB
ORDER BY file_size DESC;

-- 5. 查询过期的临时文件
SELECT id, file_path, expires_at
FROM attachments 
WHERE expires_at < CURRENT_TIMESTAMP
  AND is_deleted = FALSE;

-- 6. 统计邮件发送情况
SELECT 
    status,
    COUNT(*) as count,
    DATE(created_at) as date
FROM emails 
WHERE created_at >= DATE('now', '-7 days')
GROUP BY status, DATE(created_at)
ORDER BY date DESC;
```

## 🧹 数据维护

### 清理策略

```sql
-- 1. 清理30天前的已发送邮件附件
UPDATE attachments 
SET is_deleted = TRUE
WHERE id IN (
    SELECT a.id FROM attachments a
    JOIN emails e ON JSON_EXTRACT(e.attachment_ids, '$') LIKE '%' || a.id || '%'
    WHERE e.status = 'sent' 
      AND e.sent_at < DATE('now', '-30 days')
);

-- 2. 清理过期的临时文件
DELETE FROM attachments 
WHERE expires_at < CURRENT_TIMESTAMP
  AND upload_type = 'temp';

-- 3. 清理失败邮件记录（保留7天）
DELETE FROM emails 
WHERE status = 'failed' 
  AND created_at < DATE('now', '-7 days');
```

### 备份建议

```sql
-- 重要数据备份
CREATE TABLE emails_backup AS SELECT * FROM emails WHERE status = 'sent';
CREATE TABLE attachments_backup AS SELECT * FROM attachments WHERE is_deleted = FALSE;
```

## 📈 性能优化

### 索引优化建议

```sql
-- 复合索引
CREATE INDEX idx_emails_status_created ON emails(status, created_at);
CREATE INDEX idx_attachments_type_created ON attachments(upload_type, created_at);

-- 部分索引（PostgreSQL）
CREATE INDEX idx_emails_failed ON emails(created_at) WHERE status = 'failed';
CREATE INDEX idx_attachments_large ON attachments(file_size) WHERE file_size > 1048576;
```

### 查询优化

- 使用分页查询避免大结果集
- JSON 字段查询时使用适当的索引
- 定期 VACUUM 和 ANALYZE（PostgreSQL）
- 考虑分区表（大数据量场景）

---

此数据模型设计支持了 NotifyHubLite 的所有核心功能，具有良好的扩展性和维护性。

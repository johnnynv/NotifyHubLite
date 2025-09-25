# NotifyHubLite 富文本邮件实现计划

## 📊 工作量总结

| 功能模块 | 复杂度 | 预估工作量 | 优先级 |
|----------|--------|------------|--------|
| 核心富文本支持 | 中等 | 2-3人天 | 高 |
| HTML安全处理 | 简单 | 1-2人天 | 高 |
| 附件支持 | 复杂 | 3-4人天 | 中 |
| 高级功能 | 中等 | 2-3人天 | 低 |
| **总计** | - | **8-12人天** | - |

## 🎯 最小可行版本 (MVP)

如果只需要基本的富文本邮件支持，最小工作量为 **3-5人天**：

### Phase 1: 基础HTML邮件支持 (3-5人天)

#### 1. 扩展Schema (30分钟)
```python
# app/schemas/email.py 修改
class EmailSendRequest(BaseModel):
    recipients: List[EmailStr]
    subject: str
    body: Optional[str] = None  # 纯文本内容
    html_body: Optional[str] = None  # HTML内容
    email_type: str = Field(default="plain", regex="^(plain|html|multipart)$")
    
    @validator('body', 'html_body')
    def validate_content(cls, v, values):
        if not values.get('body') and not values.get('html_body'):
            raise ValueError('Either body or html_body must be provided')
        return v
```

#### 2. 修改SMTP客户端 (2小时)
```python
# app/utils/smtp_client.py 添加方法
async def send_html_email(self, recipients, subject, html_body, sender_email=None, sender_name=None):
    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = f"{sender_name or self.smtp_from_name} <{sender_email or self.smtp_from_email}>"
    msg["To"] = ", ".join(recipients)
    
    # 发送逻辑同send_plain_email

async def send_multipart_email(self, recipients, subject, text_body, html_body, sender_email=None, sender_name=None):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{sender_name or self.smtp_from_name} <{sender_email or self.smtp_from_email}>"
    msg["To"] = ", ".join(recipients)
    
    # 添加纯文本和HTML部分
    part1 = MIMEText(text_body, "plain", "utf-8")
    part2 = MIMEText(html_body, "html", "utf-8")
    
    msg.attach(part1)
    msg.attach(part2)
    
    # 发送逻辑
```

#### 3. 更新API端点 (2小时)
```python
# app/api/emails.py 添加端点
@router.post("/send-html")
async def send_html_email_api(email_request: EmailSendRequest):
    if email_request.email_type == "html":
        result = await email_service.send_html_email(email_request)
    elif email_request.email_type == "multipart":
        result = await email_service.send_multipart_email(email_request)
    else:
        result = await email_service.send_plain_text_email(email_request)
    
    return result
```

#### 4. HTML安全处理 (4小时)
```python
# 添加依赖到 requirements.txt
bleach>=6.0.0

# 创建 app/utils/html_cleaner.py
import bleach

ALLOWED_TAGS = [
    'p', 'div', 'span', 'br', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'b', 'em', 'i', 'u', 'a', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th',
    'img', 'font'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'width', 'height'],
    'font': ['color', 'size'],
    '*': ['style', 'class', 'id']
}

def clean_html(html_content: str) -> str:
    """清理HTML内容，移除危险标签和属性"""
    return bleach.clean(html_content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
```

### Phase 2: 附件支持 (可选，额外3-4人天)

```python
# 文件上传API
@router.post("/attachments/upload")
async def upload_attachment(file: UploadFile = File(...)):
    # 文件验证和存储逻辑
    
# 带附件的邮件发送
async def send_email_with_attachments(self, recipients, subject, body, attachments=None):
    msg = MIMEMultipart()
    # 添加邮件内容和附件
```

## 🚀 快速实现方案

如果需要快速实现，我推荐以下**最快路径** (1-2人天)：

### 1. 简单HTML支持 (4小时)
- 只添加`html_body`字段
- 修改SMTP客户端支持HTML
- 不做HTML清理(生产环境需要)

### 2. 基础API扩展 (2小时)
- 添加`/send-html`端点
- 更新文档

### 3. 简单测试 (2小时)
- 基本功能测试
- API文档验证

## 📋 实现优先级建议

1. **立即实现** (1周内): 基础HTML邮件支持
2. **短期实现** (2-3周): HTML安全处理
3. **中期实现** (1个月): 基础附件支持
4. **长期规划** (2-3个月): 高级功能(模板、数据库记录等)

## 🔧 技术风险评估

| 风险 | 影响 | 缓解方案 |
|------|------|----------|
| HTML注入攻击 | 高 | 使用bleach进行HTML清理 |
| 邮件体积过大 | 中 | 限制HTML长度和附件大小 |
| 兼容性问题 | 中 | 测试多种邮件客户端 |
| 性能问题 | 低 | HTML处理可以异步化 |

## 💡 建议

1. **先实现MVP**: 基础HTML支持，快速验证需求
2. **渐进式开发**: 按优先级逐步添加功能
3. **安全第一**: HTML清理必须在生产环境实现
4. **测试驱动**: 每个功能都要有对应的测试用例

总的来说，**最小可行的富文本邮件支持需要3-5人天**，完整功能需要8-12人天。

# 使用示例

## 📝 概述

本文档提供了 NotifyHubLite 的详细使用示例，涵盖从简单文本邮件到复杂富文本邮件的各种场景。

## 🔑 前置准备

### 1. 获取 API Key

```bash
# 在 .env 文件中配置 API Key
API_KEY=your-secure-api-key-here
```

### 2. 基础请求格式

所有请求都需要在 Header 中包含 API Key：

```bash
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json"
```

## 📧 基础邮件示例

### 示例 1: 纯文本邮件

发送最简单的纯文本邮件。

```bash
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["user@example.com"],
    "subject": "测试邮件",
    "text_content": "Hello World\n\n这是一封纯文本测试邮件。\n\n感谢您的使用！"
  }'
```

### 示例 1.5: HTML邮件

发送包含HTML格式的邮件。

```bash
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["user@example.com"],
    "subject": "HTML测试邮件",
    "html_content": "<h1>Hello World</h1><p>这是一封<strong>HTML</strong>测试邮件。</p>"
  }'
```

**响应:**
```json
{
  "success": true,
  "data": {
    "email_id": "email-123e4567-e89b-12d3-a456-426614174000",
    "status": "sent",
    "message": "邮件发送成功",
    "sent_at": "2025-09-23T10:30:00Z"
  }
}
```

### 示例 2: 兼容性最佳的多格式邮件

同时提供文本和HTML版本，确保在所有邮件客户端中都能正常显示。

```bash
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["user@example.com"],
    "subject": "重要系统升级通知",
    "text_content": "系统升级通知\n\n亲爱的用户，\n\n我们将于2025年9月25日凌晨2:00-4:00进行系统升级维护。\n\n升级内容：\n- 提升系统性能\n- 修复已知问题\n- 增加新功能\n\n维护期间系统将暂停服务，请提前做好准备。\n\n如有疑问，请联系技术支持。\n\n谢谢！\n技术团队",
    "html_content": "<div style=\"font-family: Arial, sans-serif; max-width: 600px;\"><h2 style=\"color: #333;\">🔧 系统升级通知</h2><p>亲爱的用户，</p><p>我们将于 <strong>2025年9月25日凌晨2:00-4:00</strong> 进行系统升级维护。</p><div style=\"background: #f0f8ff; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;\"><h3 style=\"margin-top: 0;\">升级内容：</h3><ul><li>🚀 提升系统性能</li><li>🐛 修复已知问题</li><li>✨ 增加新功能</li></ul></div><div style=\"background: #fff3cd; padding: 15px; border: 1px solid #ffeaa7; border-radius: 4px;\"><p><strong>⚠️ 注意：</strong>维护期间系统将暂停服务，请提前做好准备。</p></div><p>如有疑问，请联系技术支持。</p><p>谢谢！<br><em>技术团队</em></p></div>"
  }'
```

### 示例 3: 多收件人邮件

发送给多个收件人，包含抄送和密送。

```bash
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["user1@example.com", "user2@example.com"],
    "cc": ["manager@example.com"],
    "bcc": ["admin@example.com"],
    "subject": "团队通知",
    "text_content": "团队重要通知\n\n请所有团队成员注意以下事项：\n\n1. 下周一开始新项目\n2. 请及时更新项目进度\n3. 有问题及时沟通\n\n谢谢配合！",
    "html_content": "<h2>📢 团队重要通知</h2><p>请所有团队成员注意以下事项：</p><ol><li>下周一开始新项目</li><li>请及时更新项目进度</li><li>有问题及时沟通</li></ol><p>谢谢配合！</p>"
  }'
```

## 🎨 富文本邮件示例

### 示例 4: 包含表格的邮件

发送包含数据表格的富文本邮件。

```bash
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["manager@example.com"],
    "subject": "销售数据报告",
    "html_content": "
      <h1>本月销售数据</h1>
      <p>以下是本月的销售统计：</p>
      <table border=\"1\" style=\"border-collapse: collapse; width: 100%;\">
        <thead>
          <tr style=\"background-color: #f2f2f2;\">
            <th style=\"padding: 8px; text-align: left;\">产品</th>
            <th style=\"padding: 8px; text-align: right;\">销量</th>
            <th style=\"padding: 8px; text-align: right;\">收入</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style=\"padding: 8px;\">产品A</td>
            <td style=\"padding: 8px; text-align: right;\">150</td>
            <td style=\"padding: 8px; text-align: right;\">¥15,000</td>
          </tr>
          <tr>
            <td style=\"padding: 8px;\">产品B</td>
            <td style=\"padding: 8px; text-align: right;\">230</td>
            <td style=\"padding: 8px; text-align: right;\">¥23,000</td>
          </tr>
          <tr style=\"background-color: #f9f9f9; font-weight: bold;\">
            <td style=\"padding: 8px;\">总计</td>
            <td style=\"padding: 8px; text-align: right;\">380</td>
            <td style=\"padding: 8px; text-align: right;\">¥38,000</td>
          </tr>
        </tbody>
      </table>
      <p>感谢团队的努力！</p>
    "
  }'
```

### 示例 5: 样式丰富的邮件

使用 CSS 样式创建美观的邮件。

```bash
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["customer@example.com"],
    "subject": "欢迎加入我们",
    "html_content": "
      <div style=\"font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;\">
        <div style=\"background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;\">
          <h1 style=\"color: white; margin: 0;\">欢迎加入</h1>
        </div>
        <div style=\"padding: 20px; background-color: #f8f9fa;\">
          <h2 style=\"color: #333;\">感谢您的注册！</h2>
          <p style=\"color: #666; line-height: 1.6;\">
            我们很高兴您加入我们的平台。您现在可以：
          </p>
          <ul style=\"color: #666;\">
            <li>访问所有高级功能</li>
            <li>获得24/7技术支持</li>
            <li>享受专属优惠</li>
          </ul>
          <div style=\"text-align: center; margin: 30px 0;\">
            <a href=\"#\" style=\"background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;\">
              开始使用
            </a>
          </div>
        </div>
        <div style=\"background-color: #333; padding: 15px; text-align: center;\">
          <p style=\"color: #ccc; margin: 0; font-size: 12px;\">
            © 2025 Your Company. All rights reserved.
          </p>
        </div>
      </div>
    "
  }'
```

## 🖼️ 图片邮件示例

### 示例 5: 内嵌图片邮件

发送包含内嵌图片的邮件。

**步骤 1: 上传图片**
```bash
curl -X POST "http://localhost:8000/api/v1/attachments/upload" \
  -H "X-API-Key: your-api-key" \
  -F "file=@company-logo.png" \
  -F "type=image" \
  -F "is_inline=true"
```

**响应:**
```json
{
  "success": true,
  "data": {
    "file_id": "att-123e4567-e89b-12d3-a456-426614174000",
    "filename": "company-logo.png",
    "cid": "logo_image",
    "file_size": 245760
  }
}
```

**步骤 2: 发送邮件**
```bash
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["customer@example.com"],
    "subject": "公司介绍",
    "html_content": "
      <div style=\"text-align: center;\">
        <img src=\"cid:logo_image\" alt=\"公司Logo\" style=\"width: 200px; margin: 20px 0;\"/>
        <h1>关于我们</h1>
        <p>我们是一家专注于创新的科技公司...</p>
      </div>
    ",
    "attachments": [
      {
        "file_id": "att-123e4567-e89b-12d3-a456-426614174000",
        "type": "inline_image",
        "cid": "logo_image"
      }
    ]
  }'
```

### 示例 6: 多图片邮件

发送包含多张内嵌图片的邮件。

```bash
# 假设已上传多张图片，获得了对应的 file_id 和 cid

curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["client@example.com"],
    "subject": "产品展示",
    "html_content": "
      <h1>最新产品展示</h1>
      <div style=\"display: flex; flex-wrap: wrap; gap: 20px;\">
        <div style=\"flex: 1; min-width: 250px; text-align: center;\">
          <img src=\"cid:product1\" alt=\"产品1\" style=\"width: 100%; max-width: 250px;\"/>
          <h3>产品A</h3>
          <p>功能强大，性价比高</p>
        </div>
        <div style=\"flex: 1; min-width: 250px; text-align: center;\">
          <img src=\"cid:product2\" alt=\"产品2\" style=\"width: 100%; max-width: 250px;\"/>
          <h3>产品B</h3>
          <p>设计精美，用户友好</p>
        </div>
      </div>
      <div style=\"text-align: center; margin-top: 30px;\">
        <img src=\"cid:chart\" alt=\"销售图表\" style=\"width: 100%; max-width: 500px;\"/>
        <p>销售趋势图</p>
      </div>
    ",
    "attachments": [
      {
        "file_id": "product1-file-id",
        "type": "inline_image",
        "cid": "product1"
      },
      {
        "file_id": "product2-file-id", 
        "type": "inline_image",
        "cid": "product2"
      },
      {
        "file_id": "chart-file-id",
        "type": "inline_image",
        "cid": "chart"
      }
    ]
  }'
```

## 📎 附件邮件示例

### 示例 7: 普通文档附件

发送包含文档附件的邮件。

**步骤 1: 上传文档**
```bash
curl -X POST "http://localhost:8000/api/v1/attachments/upload" \
  -H "X-API-Key: your-api-key" \
  -F "file=@project-proposal.docx" \
  -F "type=document"
```

**步骤 2: 发送邮件**
```bash
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["client@example.com"],
    "cc": ["manager@example.com"],
    "subject": "项目提案",
    "html_content": "
      <h2>项目提案</h2>
      <p>亲爱的客户，</p>
      <p>感谢您对我们服务的关注。请查看附件中的详细项目提案。</p>
      <ul>
        <li>项目概述</li>
        <li>技术方案</li>
        <li>时间计划</li>
        <li>费用预算</li>
      </ul>
      <p>如有任何疑问，请随时联系我们。</p>
      <p>最诚挚的问候，<br>项目团队</p>
    ",
    "attachments": [
      {
        "file_id": "document-file-id",
        "type": "attachment",
        "filename": "项目提案.docx"
      }
    ]
  }'
```

### 示例 8: 多种附件

发送包含多种类型附件的邮件。

```bash
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["team@example.com"],
    "subject": "会议资料包",
    "html_content": "
      <h2>明日会议资料</h2>
      <p>各位同事，</p>
      <p>请查看附件中的会议资料：</p>
      <ol>
        <li><strong>会议议程.pdf</strong> - 详细议程安排</li>
        <li><strong>数据分析.xlsx</strong> - 最新数据报告</li>
        <li><strong>产品展示.pptx</strong> - 产品演示文稿</li>
      </ol>
      <p>请提前阅读，准时参会。</p>
    ",
    "attachments": [
      {
        "file_id": "agenda-file-id",
        "type": "attachment", 
        "filename": "会议议程.pdf"
      },
      {
        "file_id": "excel-file-id",
        "type": "attachment",
        "filename": "数据分析.xlsx"
      },
      {
        "file_id": "ppt-file-id",
        "type": "attachment",
        "filename": "产品展示.pptx"
      }
    ]
  }'
```

## 📄 PDF 预览示例

### 示例 9: PDF 预览邮件

上传 PDF 并发送带预览的邮件。

**步骤 1: 上传 PDF**
```bash
curl -X POST "http://localhost:8000/api/v1/attachments/upload-pdf" \
  -H "X-API-Key: your-api-key" \
  -F "file=@monthly-report.pdf" \
  -F "preview_pages=3" \
  -F "preview_dpi=150"
```

**响应:**
```json
{
  "success": true,
  "data": {
    "file_id": "pdf-123e4567-e89b-12d3-a456-426614174000",
    "filename": "monthly-report.pdf",
    "total_pages": 8,
    "preview_images": [
      {
        "page": 1,
        "image_id": "img-111",
        "cid": "pdf_page_1"
      },
      {
        "page": 2,
        "image_id": "img-222",
        "cid": "pdf_page_2"
      },
      {
        "page": 3,
        "image_id": "img-333",
        "cid": "pdf_page_3"
      }
    ],
    "generated_html": "<div class='pdf-preview'>...</div>"
  }
}
```

**步骤 2: 发送邮件**
```bash
curl -X POST "http://localhost:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["boss@example.com"],
    "subject": "月度工作报告",
    "html_content": "
      <h1>月度工作报告</h1>
      <p>尊敬的领导，</p>
      <p>以下是本月的工作报告预览，完整版请查看附件：</p>
      <div class=\"pdf-preview\" style=\"font-family: Arial, sans-serif;\">
        <h3>📄 PDF文档预览</h3>
        <div style=\"margin: 20px 0; text-align: center;\">
          <p><strong>第 1 页</strong></p>
          <img src=\"cid:pdf_page_1\" style=\"max-width: 100%; border: 1px solid #ddd;\"/>
        </div>
        <div style=\"margin: 20px 0; text-align: center;\">
          <p><strong>第 2 页</strong></p>
          <img src=\"cid:pdf_page_2\" style=\"max-width: 100%; border: 1px solid #ddd;\"/>
        </div>
        <div style=\"margin: 20px 0; text-align: center;\">
          <p><strong>第 3 页</strong></p>
          <img src=\"cid:pdf_page_3\" style=\"max-width: 100%; border: 1px solid #ddd;\"/>
        </div>
        <div style=\"background: #f8f9fa; padding: 15px; margin: 20px 0; border-left: 4px solid #007bff;\">
          <p><strong>📎 还有 5 页内容</strong></p>
          <p>完整PDF文档请查看邮件附件</p>
        </div>
      </div>
      <p>请审阅，如有问题请及时沟通。</p>
    ",
    "attachments": [
      {
        "file_id": "img-111",
        "type": "inline_image",
        "cid": "pdf_page_1"
      },
      {
        "file_id": "img-222", 
        "type": "inline_image",
        "cid": "pdf_page_2"
      },
      {
        "file_id": "img-333",
        "type": "inline_image", 
        "cid": "pdf_page_3"
      },
      {
        "file_id": "pdf-123e4567-e89b-12d3-a456-426614174000",
        "type": "attachment",
        "filename": "月度工作报告.pdf"
      }
    ]
  }'
```

## 🔧 高级用法示例

### 示例 10: 自动化报告邮件

使用脚本自动生成和发送报告邮件。

**Python 脚本示例:**
```python
import requests
import json
from datetime import datetime

class NotifyHubLiteClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def upload_file(self, file_path, file_type):
        """上传文件"""
        url = f"{self.base_url}/api/v1/attachments/upload"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'type': file_type}
            
            response = requests.post(
                url, 
                headers={'X-API-Key': self.headers['X-API-Key']},
                files=files, 
                data=data
            )
        
        return response.json()
    
    def send_email(self, email_data):
        """发送邮件"""
        url = f"{self.base_url}/api/v1/emails/send"
        
        response = requests.post(
            url,
            headers=self.headers,
            data=json.dumps(email_data)
        )
        
        return response.json()

# 使用示例
def send_daily_report():
    client = NotifyHubLiteClient(
        "http://localhost:8000", 
        "your-api-key"
    )
    
    # 1. 上传报告图表
    chart_result = client.upload_file("daily_chart.png", "image")
    chart_file_id = chart_result['data']['file_id']
    chart_cid = chart_result['data']['cid']
    
    # 2. 上传详细报告
    report_result = client.upload_file("daily_report.pdf", "document")
    report_file_id = report_result['data']['file_id']
    
    # 3. 构建邮件内容
    today = datetime.now().strftime("%Y年%m月%d日")
    
    email_data = {
        "to": ["manager@example.com", "team@example.com"],
        "subject": f"{today} 日报",
        "html_content": f"""
        <h1>{today} 工作日报</h1>
        
        <h2>📊 关键指标</h2>
        <div style="text-align: center;">
            <img src="cid:{chart_cid}" alt="日报图表" style="max-width: 100%;"/>
        </div>
        
        <h2>📋 今日总结</h2>
        <ul>
            <li>完成任务数：15</li>
            <li>新增用户：230</li>
            <li>系统运行时间：99.9%</li>
        </ul>
        
        <h2>📎 详细报告</h2>
        <p>完整的数据分析和详细信息请查看附件中的PDF报告。</p>
        
        <p><small>此邮件由系统自动发送，请勿回复。</small></p>
        """,
        "attachments": [
            {
                "file_id": chart_file_id,
                "type": "inline_image",
                "cid": chart_cid
            },
            {
                "file_id": report_file_id,
                "type": "attachment",
                "filename": f"{today}_详细报告.pdf"
            }
        ]
    }
    
    # 4. 发送邮件
    result = client.send_email(email_data)
    
    if result['success']:
        print(f"日报发送成功！邮件ID: {result['data']['email_id']}")
    else:
        print(f"发送失败: {result['error']['message']}")

# 执行发送
if __name__ == "__main__":
    send_daily_report()
```

### 示例 11: 批量邮件处理

处理批量邮件发送的示例。

**Node.js 脚本示例:**
```javascript
const axios = require('axios');
const fs = require('fs');

class NotifyHubLiteClient {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json'
        };
    }

    async sendEmail(emailData) {
        try {
            const response = await axios.post(
                `${this.baseUrl}/api/v1/emails/send`,
                emailData,
                { headers: this.headers }
            );
            return response.data;
        } catch (error) {
            throw new Error(`发送失败: ${error.response?.data?.error?.message || error.message}`);
        }
    }

    async getEmailStatus(emailId) {
        try {
            const response = await axios.get(
                `${this.baseUrl}/api/v1/emails/${emailId}`,
                { headers: this.headers }
            );
            return response.data;
        } catch (error) {
            throw new Error(`查询失败: ${error.response?.data?.error?.message || error.message}`);
        }
    }
}

// 批量发送客户通知
async function sendCustomerNotifications() {
    const client = new NotifyHubLiteClient(
        'http://localhost:8000',
        'your-api-key'
    );

    // 客户列表
    const customers = [
        { email: 'customer1@example.com', name: '张三', amount: 1500 },
        { email: 'customer2@example.com', name: '李四', amount: 2300 },
        { email: 'customer3@example.com', name: '王五', amount: 1800 }
    ];

    const results = [];

    for (const customer of customers) {
        try {
            const emailData = {
                to: [customer.email],
                subject: '账单通知',
                html_content: `
                    <div style="font-family: Arial, sans-serif; max-width: 600px;">
                        <h2>账单通知</h2>
                        <p>尊敬的 ${customer.name}，</p>
                        <p>您的本月账单金额为：<strong style="color: #e74c3c;">¥${customer.amount}</strong></p>
                        <div style="background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px;">
                            <h3>缴费方式：</h3>
                            <ul>
                                <li>在线支付：登录官网进行缴费</li>
                                <li>银行转账：账号 123456789</li>
                                <li>现金缴费：到营业厅办理</li>
                            </ul>
                        </div>
                        <p>请在本月底前完成缴费，感谢您的使用！</p>
                    </div>
                `
            };

            const result = await client.sendEmail(emailData);
            results.push({
                customer: customer.name,
                email: customer.email,
                status: 'success',
                emailId: result.data.email_id
            });

            console.log(`✅ ${customer.name} (${customer.email}) - 发送成功`);
            
            // 避免发送过快
            await new Promise(resolve => setTimeout(resolve, 1000));

        } catch (error) {
            results.push({
                customer: customer.name,
                email: customer.email,
                status: 'failed',
                error: error.message
            });

            console.log(`❌ ${customer.name} (${customer.email}) - 发送失败: ${error.message}`);
        }
    }

    // 生成发送报告
    const summary = {
        total: results.length,
        success: results.filter(r => r.status === 'success').length,
        failed: results.filter(r => r.status === 'failed').length,
        details: results
    };

    console.log('\n📊 发送汇总:');
    console.log(`总数: ${summary.total}`);
    console.log(`成功: ${summary.success}`);
    console.log(`失败: ${summary.failed}`);

    // 保存结果到文件
    fs.writeFileSync(
        `send_results_${Date.now()}.json`,
        JSON.stringify(summary, null, 2)
    );
}

// 执行批量发送
sendCustomerNotifications().catch(console.error);
```

## ❓ 错误处理示例

### 示例 12: 错误处理最佳实践

```python
import requests
import time
from typing import Optional

def send_email_with_retry(
    api_key: str,
    email_data: dict,
    max_retries: int = 3,
    base_url: str = "http://localhost:8000"
) -> Optional[dict]:
    """
    带重试机制的邮件发送
    """
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{base_url}/api/v1/emails/send",
                headers=headers,
                json=email_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"✅ 邮件发送成功: {result['data']['email_id']}")
                    return result
                else:
                    print(f"❌ 业务错误: {result['error']['message']}")
                    return None
            
            elif response.status_code == 401:
                print("❌ API Key 无效")
                return None
            
            elif response.status_code == 413:
                print("❌ 文件过大")
                return None
            
            elif response.status_code == 422:
                error_info = response.json()
                print(f"❌ 参数错误: {error_info['error']['message']}")
                return None
            
            elif response.status_code >= 500:
                print(f"⚠️ 服务器错误 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    print("❌ 多次重试后仍然失败")
                    return None
            
            else:
                print(f"❌ 未知错误: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"⚠️ 请求超时 (尝试 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                print("❌ 多次超时后放弃")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"⚠️ 连接错误 (尝试 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                print("❌ 无法连接到服务器")
                return None
                
        except Exception as e:
            print(f"❌ 未知异常: {e}")
            return None
    
    return None

# 使用示例
email_data = {
    "to": ["test@example.com"],
    "subject": "测试邮件",
    "html_content": "<h1>Hello</h1>"
}

result = send_email_with_retry("your-api-key", email_data)
if result:
    print("邮件发送流程完成")
else:
    print("邮件发送失败，请检查配置和网络")
```

---

这些示例展示了 NotifyHubLite 的各种使用场景，从简单的文本邮件到复杂的富文本邮件，以及如何处理错误和进行批量操作。根据实际需求选择合适的示例进行参考和修改。

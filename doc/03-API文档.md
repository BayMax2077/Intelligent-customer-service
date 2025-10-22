# 智能客服系统API文档

## 概述

智能客服系统提供完整的RESTful API接口，支持用户认证、店铺管理、消息处理、知识库管理、审核队列等核心功能。

## 基础信息

- **Base URL**: `http://localhost:5002`
- **API版本**: v1
- **认证方式**: Session-based (Flask-Login)
- **数据格式**: JSON
- **字符编码**: UTF-8

## 通用响应格式

### 成功响应
```json
{
  "ok": true,
  "data": {...},
  "message": "操作成功"
}
```

### 错误响应
```json
{
  "ok": false,
  "error": "错误代码",
  "message": "错误描述",
  "detail": "详细错误信息"
}
```

## 认证接口

### 用户登录
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**响应示例**:
```json
{
  "ok": true,
  "user": {
    "id": 1,
    "username": "admin",
    "role": "superadmin"
  }
}
```

### 用户登出
```http
POST /auth/logout
```

**响应示例**:
```json
{
  "ok": true
}
```

## 店铺管理接口

### 获取店铺列表
```http
GET /shops
```

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "测试店铺",
    "qianniu_title": "千牛-测试店铺",
    "ocr_region": [800, 200, 600, 300],
    "unread_threshold": 0.02,
    "ai_model": "stub",
    "auto_mode": false,
    "blacklist": [],
    "whitelist": [],
    "business_hours": "09:00-18:00",
    "reply_delay": 2
  }
]
```

### 创建店铺
```http
POST /shops
Content-Type: application/json

{
  "name": "新店铺",
  "qianniu_title": "千牛-新店铺",
  "ocr_region": [800, 200, 600, 300],
  "unread_threshold": 0.02,
  "ai_model": "stub",
  "auto_mode": false,
  "blacklist": [],
  "whitelist": [],
  "business_hours": "09:00-18:00",
  "reply_delay": 2
}
```

**响应示例**:
```json
{
  "id": 2,
  "name": "新店铺",
  "qianniu_title": "千牛-新店铺"
}
```

### 更新店铺
```http
PUT /shops/{shop_id}
Content-Type: application/json

{
  "name": "更新后的店铺名",
  "ocr_region": [900, 250, 700, 350],
  "unread_threshold": 0.03
}
```

### 删除店铺
```http
DELETE /shops/{shop_id}
```

**权限要求**: 仅超级管理员

### 获取店铺配置
```http
GET /shops/{shop_id}/config
```

**响应示例**:
```json
{
  "ocr_region": [800, 200, 600, 300],
  "unread_threshold": 0.02,
  "title_kw": "千牛",
  "auto_mode": false,
  "ai_model": "stub",
  "blacklist": [],
  "whitelist": [],
  "business_hours": "09:00-18:00",
  "reply_delay": 2
}
```

### 更新店铺配置
```http
PUT /shops/{shop_id}/config
Content-Type: application/json

{
  "ocr_region": [900, 250, 700, 350],
  "unread_threshold": 0.03,
  "auto_mode": true,
  "ai_model": "openai"
}
```

### 获取OCR模板
```http
GET /shops/ocr_templates
```

**响应示例**:
```json
[
  {
    "name": "1920×1080 (标准)",
    "description": "1920×1080 分辨率，适合大多数显示器",
    "ocr_region": [800, 200, 600, 300],
    "chat_region": [800, 200, 600, 400],
    "unread_threshold": 0.02
  },
  {
    "name": "1366×768 (笔记本)",
    "description": "1366×768 分辨率，适合笔记本屏幕",
    "ocr_region": [780, 180, 520, 360],
    "chat_region": [780, 180, 520, 450],
    "unread_threshold": 0.04
  }
]
```

## 消息管理接口

### 获取消息列表
```http
GET /messages
```

**响应示例**:
```json
[
  {
    "id": 1,
    "shop_id": 1,
    "customer_id": "customer_001",
    "content": "你好，我想咨询一下产品信息",
    "content_preview": "你好，我想咨询一下产品信息",
    "source": "qianniu",
    "status": "new",
    "handled_by": null,
    "created_at": "2025-01-21T10:30:00"
  }
]
```

### 处理消息
```http
POST /messages/process
Content-Type: application/json

{
  "message_id": 1
}
```

**响应示例**:
```json
{
  "reply": "您好！很高兴为您服务，请问您想了解哪个产品的信息呢？",
  "source": "ai",
  "auto_send": false,
  "confidence": 0.85
}
```

## 审核队列接口

### 获取审核队列
```http
GET /audit
```

**响应示例**:
```json
[
  {
    "id": 1,
    "message_id": 1,
    "status": "pending",
    "assigned_to": null,
    "note": null,
    "created_at": "2025-01-21T10:30:00",
    "message": {
      "id": 1,
      "shop_id": 1,
      "customer_id": "customer_001",
      "content": "你好，我想咨询一下产品信息",
      "status": "new",
      "created_at": "2025-01-21T10:30:00"
    },
    "ai_reply": {
      "id": 1,
      "model": "openai",
      "reply": "您好！很高兴为您服务，请问您想了解哪个产品的信息呢？",
      "confidence": 0.85,
      "review_status": "pending",
      "created_at": "2025-01-21T10:30:00"
    }
  }
]
```

### 通过审核
```http
POST /audit/approve
Content-Type: application/json

{
  "id": 1,
  "title_kw": "千牛",
  "edited_reply": "您好！很高兴为您服务，请问您想了解哪个产品的信息呢？"
}
```

### 拒绝审核
```http
POST /audit/reject
Content-Type: application/json

{
  "id": 1
}
```

### 撤回审核
```http
POST /audit/recall
Content-Type: application/json

{
  "id": 1
}
```

### 重新审核
```http
POST /audit/review_again
Content-Type: application/json

{
  "id": 1
}
```

### 获取审核上下文
```http
GET /audit/{item_id}/context
```

**响应示例**:
```json
{
  "current_message": {
    "id": 1,
    "content": "你好，我想咨询一下产品信息",
    "status": "new",
    "created_at": "2025-01-21T10:30:00"
  },
  "context_messages": [
    {
      "id": 2,
      "content": "之前的问题",
      "status": "answered",
      "created_at": "2025-01-21T09:30:00"
    }
  ]
}
```

## 知识库管理接口

### 获取知识库条目
```http
GET /kb?shop_id=1&category=客服咨询&page=1&per_page=20
```

**查询参数**:
- `shop_id`: 店铺ID（可选）
- `category`: 分类（可选）
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认20）

**响应示例**:
```json
{
  "items": [
    {
      "id": 1,
      "shop_id": 1,
      "question": "如何联系客服？",
      "answer": "您可以通过以下方式联系我们的客服：1. 在线客服（工作时间9:00-18:00）2. 客服电话：400-123-4567",
      "category": "客服咨询",
      "keywords": "联系,客服,电话",
      "created_at": "2025-01-21T10:30:00",
      "updated_at": "2025-01-21T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

### 创建知识库条目
```http
POST /kb
Content-Type: application/json

{
  "shop_id": 1,
  "question": "如何联系客服？",
  "answer": "您可以通过以下方式联系我们的客服：1. 在线客服（工作时间9:00-18:00）2. 客服电话：400-123-4567",
  "category": "客服咨询",
  "keywords": "联系,客服,电话"
}
```

### 更新知识库条目
```http
PUT /kb/{item_id}
Content-Type: application/json

{
  "question": "如何联系客服？",
  "answer": "您可以通过以下方式联系我们的客服：1. 在线客服（工作时间9:00-18:00）2. 客服电话：400-123-4567",
  "category": "客服咨询",
  "keywords": "联系,客服,电话"
}
```

### 删除知识库条目
```http
DELETE /kb/{item_id}
```

### 获取分类列表
```http
GET /kb/categories
```

**响应示例**:
```json
["客服咨询", "物流配送", "支付相关", "售后服务"]
```

### 批量导入知识库
```http
POST /kb/import
Content-Type: multipart/form-data

file: [Excel文件]
```

**Excel文件格式**:
| 条目归属 | 问题 | 答案 | 分类 | 关键词 |
|---------|------|------|------|--------|
| 全局知识库 | 如何联系客服？ | 您可以通过以下方式联系我们的客服... | 客服咨询 | 联系,客服,电话 |

**响应示例**:
```json
{
  "ok": true,
  "message": "导入完成！成功: 10条, 失败: 0条",
  "success_count": 10,
  "error_count": 0,
  "total_rows": 10,
  "success_rate": 100.0,
  "task_id": 1
}
```

### 导出知识库
```http
GET /kb/export?shop_id=1
```

**查询参数**:
- `shop_id`: 店铺ID（可选，不传则导出全局知识库）

**响应**: Excel文件下载

### 下载导入模板
```http
GET /kb/template
```

**响应**: Excel模板文件下载

### 批量删除知识库条目
```http
POST /kb/batch-delete
Content-Type: application/json

{
  "item_ids": [1, 2, 3],
  "confirm": true
}
```

## 千牛自动化接口

### 获取千牛窗口列表
```http
GET /qianniu/windows
```

**响应示例**:
```json
[
  {
    "title": "千牛-测试店铺",
    "hwnd": 123456,
    "visible": true,
    "rect": [100, 100, 800, 600]
  }
]
```

### 发送测试消息
```http
POST /qianniu/send_test
Content-Type: application/json

{
  "title_kw": "千牛",
  "text": "这是一条测试消息"
}
```

### 未读检测
```http
POST /qianniu/unread_probe
Content-Type: application/json

{
  "region": [800, 200, 300, 300]
}
```

**响应示例**:
```json
{
  "score": 0.85
}
```

### OCR采集
```http
POST /qianniu/ocr_capture
Content-Type: application/json

{
  "region": [800, 200, 600, 300],
  "shop_id": 1,
  "customer_id": "customer_001"
}
```

**响应示例**:
```json
{
  "id": 1,
  "content_len": 50,
  "empty": false
}
```

## 统计接口

### 获取统计数据
```http
GET /statistics
```

**响应示例**:
```json
{
  "total_messages": 100,
  "answered_messages": 85,
  "pending_messages": 15,
  "kb_hit_rate": 0.75,
  "ai_accuracy": 0.82,
  "daily_stats": [
    {
      "date": "2025-01-21",
      "messages": 20,
      "answered": 18,
      "kb_hits": 12
    }
  ]
}
```

## 用户管理接口

### 获取用户列表
```http
GET /users
```

**响应示例**:
```json
[
  {
    "id": 1,
    "username": "admin",
    "role": "superadmin",
    "shop_id": null,
    "created_at": "2025-01-21T10:30:00"
  }
]
```

### 创建用户
```http
POST /users
Content-Type: application/json

{
  "username": "newuser",
  "password": "password123",
  "role": "admin",
  "shop_id": 1
}
```

### 更新用户
```http
PUT /users/{user_id}
Content-Type: application/json

{
  "role": "admin",
  "shop_id": 1
}
```

### 删除用户
```http
DELETE /users/{user_id}
```

## 导入任务接口

### 获取导入任务列表
```http
GET /import-tasks
```

**响应示例**:
```json
[
  {
    "id": 1,
    "task_name": "知识库导入_20250121_103000",
    "file_name": "knowledge_base.xlsx",
    "file_size": 1024,
    "status": "completed",
    "progress": 100,
    "total_rows": 10,
    "processed_rows": 10,
    "success_count": 10,
    "error_count": 0,
    "started_at": "2025-01-21T10:30:00",
    "completed_at": "2025-01-21T10:31:00"
  }
]
```

### 获取导入任务详情
```http
GET /import-tasks/{task_id}
```

### 取消导入任务
```http
POST /import-tasks/{task_id}/cancel
```

## 错误码说明

| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| `invalid_credentials` | 401 | 用户名或密码错误 |
| `unauthorized` | 401 | 未登录 |
| `forbidden` | 403 | 权限不足 |
| `not_found` | 404 | 资源不存在 |
| `name_required` | 400 | 店铺名称必填 |
| `message_id_required` | 400 | 消息ID必填 |
| `id_required` | 400 | ID必填 |
| `database_error` | 500 | 数据库错误 |
| `internal_error` | 500 | 内部服务器错误 |

## 权限说明

### 角色权限
- **superadmin**: 超级管理员，可管理所有资源
- **admin**: 店铺管理员，可管理所属店铺
- **agent**: 客服代理，只能处理消息和审核

### 接口权限
- 所有接口都需要登录认证
- 创建、更新、删除操作需要相应权限
- 审核相关操作需要admin或superadmin权限

## 使用示例

### cURL示例

#### 登录
```bash
curl -X POST http://localhost:5002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  -c cookies.txt
```

#### 获取店铺列表
```bash
curl -X GET http://localhost:5002/shops \
  -b cookies.txt
```

#### 创建店铺
```bash
curl -X POST http://localhost:5002/shops \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "测试店铺",
    "qianniu_title": "千牛-测试店铺",
    "ocr_region": [800, 200, 600, 300],
    "unread_threshold": 0.02,
    "ai_model": "stub",
    "auto_mode": false
  }'
```

### JavaScript示例

```javascript
// 登录
const loginResponse = await fetch('/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});

const loginData = await loginResponse.json();
console.log('登录结果:', loginData);

// 获取店铺列表
const shopsResponse = await fetch('/shops', {
  credentials: 'include'
});

const shops = await shopsResponse.json();
console.log('店铺列表:', shops);
```

## 注意事项

1. **认证**: 所有API调用都需要先登录获取session
2. **跨域**: 前端需要配置CORS，后端已支持
3. **文件上传**: 知识库导入使用multipart/form-data格式
4. **分页**: 列表接口支持分页，默认每页20条
5. **错误处理**: 所有错误都会返回统一的错误格式
6. **权限**: 不同角色有不同的操作权限
7. **数据验证**: 所有输入数据都会进行验证

---

**文档版本**: v1.0  
**最后更新**: 2025-01-21  
**维护人员**: API团队

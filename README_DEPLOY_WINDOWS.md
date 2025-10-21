# 智能客服系统 - Windows 部署指南

## 系统要求

- **操作系统**: Windows 10/11
- **Python**: 3.12+ (推荐使用官方安装包)
- **Node.js**: 18+ (推荐使用LTS版本)
- **内存**: 至少4GB RAM
- **磁盘空间**: 至少2GB可用空间

## 快速部署

### 1. 下载项目

```bash
git clone <项目地址>
cd 智能客服
```

### 2. 运行部署脚本

双击运行 `deploy_windows.bat` 脚本，或命令行执行：

```cmd
deploy_windows.bat
```

部署脚本会自动完成以下操作：
- 创建Python虚拟环境
- 安装后端依赖
- 初始化数据库
- 安装前端依赖
- 构建前端项目
- 创建启动脚本

### 3. 启动系统

部署完成后，有以下启动选项：

#### 选项1：一键启动（推荐）
```cmd
start_all.bat
```
同时启动后端和前端服务。

#### 选项2：分别启动
```cmd
# 启动后端
start_backend.bat

# 启动前端（新开命令行窗口）
start_frontend.bat
```

## 配置说明

### 1. 环境变量配置

复制 `.env.example` 为 `.env` 并修改配置：

```bash
# 数据库配置
DATABASE_URL=sqlite:///data/sqlite.db
# 生产环境建议使用MySQL
# DATABASE_URL=mysql://user:password@localhost/smart_cs

# AI模型配置（至少配置一个）
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

# 通义千问配置
QWEN_API_KEY=your_qwen_api_key
QWEN_MODEL=qwen-turbo

# 文心一言配置
ERNIE_API_KEY=your_ernie_api_key
ERNIE_SECRET_KEY=your_ernie_secret_key
ERNIE_MODEL=ernie-bot-turbo

# 告警配置（可选）
ALERT_SMTP_SERVER=smtp.gmail.com
ALERT_SMTP_PORT=587
ALERT_EMAIL_USERNAME=your_email@gmail.com
ALERT_EMAIL_PASSWORD=your_app_password
ALERT_EMAIL_TO=admin@example.com,alert@example.com
ALERT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key
ALERT_WEBHOOK_TYPE=wechat
```

### 2. 数据库配置

#### SQLite（默认）
无需额外配置，系统自动创建 `data/sqlite.db` 文件。

#### MySQL（生产环境推荐）
1. 安装MySQL 8.0+
2. 创建数据库：
```sql
CREATE DATABASE smart_cs CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
3. 配置环境变量：
```bash
DATABASE_URL=mysql://username:password@localhost:3306/smart_cs
```

### 3. AI模型配置

系统支持多种AI模型，至少需要配置一个：

#### OpenAI GPT
1. 注册OpenAI账号并获取API Key
2. 配置环境变量：
```bash
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini
```

#### 通义千问
1. 注册阿里云账号并开通DashScope服务
2. 配置环境变量：
```bash
QWEN_API_KEY=sk-xxx
QWEN_MODEL=qwen-turbo
```

#### 文心一言
1. 注册百度智能云账号并开通千帆平台
2. 配置环境变量：
```bash
ERNIE_API_KEY=xxx
ERNIE_SECRET_KEY=xxx
ERNIE_MODEL=ernie-bot-turbo
```

## 访问系统

### 1. 前端管理界面
- 地址：http://localhost:5174
- 功能：店铺配置、消息管理、审核队列、知识库管理、统计报表、用户管理

### 2. 后端API接口
- 地址：http://localhost:5002
- 健康检查：http://localhost:5002/health
- API文档：http://localhost:5002/api

### 3. 首次使用

1. 访问前端界面
2. 系统会自动跳转到登录页面
3. 使用默认管理员账户登录：
   - 用户名：admin
   - 密码：admin123
4. 登录后立即修改密码

## 服务管理

### 启动服务
```cmd
# 完整系统
start_all.bat

# 仅后端
start_backend.bat

# 仅前端
start_frontend.bat
```

### 停止服务
在对应的命令行窗口中按 `Ctrl+C` 停止服务。

### 重启服务
1. 停止当前服务（Ctrl+C）
2. 重新运行对应的启动脚本

## 故障排除

### 1. Python环境问题
```cmd
# 检查Python版本
python --version

# 如果版本过低，请安装Python 3.12+
```

### 2. Node.js环境问题
```cmd
# 检查Node.js版本
node --version

# 如果版本过低，请安装Node.js 18+
```

### 3. 端口占用问题
```cmd
# 检查端口占用
netstat -ano | findstr :5002
netstat -ano | findstr :5174

# 如果端口被占用，可以修改配置
# 后端端口：修改 start_backend.bat 中的 --port=5002
# 前端端口：修改 start_frontend.bat 中的 --port 5174
```

### 4. 数据库连接问题
```cmd
# 重新初始化数据库
python -m flask db upgrade

# 如果使用MySQL，检查数据库连接配置
```

### 5. 前端构建问题
```cmd
# 清理并重新构建
cd qianduan
rm -rf node_modules dist
npm install
npm run build
```

### 6. 权限问题
- 确保以管理员身份运行命令行
- 检查防火墙设置，允许5002和5174端口

## 生产环境部署

### 1. 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5174;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://localhost:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 使用Windows服务
可以使用 `nssm` 工具将应用注册为Windows服务：

```cmd
# 下载nssm工具
# 注册后端服务
nssm install SmartCS-Backend
nssm set SmartCS-Backend Application C:\path\to\your\project\.venv\Scripts\python.exe
nssm set SmartCS-Backend AppParameters -m flask run --host=0.0.0.0 --port=5002
nssm set SmartCS-Backend AppDirectory C:\path\to\your\project
nssm start SmartCS-Backend
```

### 3. 数据备份
```cmd
# SQLite备份
copy data\sqlite.db backup\sqlite_%date%.db

# MySQL备份
mysqldump -u username -p smart_cs > backup\smart_cs_%date%.sql
```

## 性能优化

### 1. 系统资源
- 推荐配置：8GB RAM，4核CPU
- 定期清理日志文件
- 监控磁盘空间使用

### 2. 数据库优化
- 定期清理过期数据
- 为常用查询字段添加索引
- 考虑使用数据库连接池

### 3. 前端优化
- 启用Gzip压缩
- 使用CDN加速静态资源
- 定期清理浏览器缓存

## 安全建议

### 1. 网络安全
- 使用HTTPS协议
- 配置防火墙规则
- 定期更新系统补丁

### 2. 数据安全
- 定期备份数据库
- 加密敏感配置信息
- 限制数据库访问权限

### 3. 访问控制
- 修改默认管理员密码
- 创建专用用户账户
- 定期审查用户权限

## 技术支持

如遇到问题，请检查：
1. 系统日志文件
2. 浏览器控制台错误
3. 网络连接状态
4. 服务运行状态

更多技术支持请参考项目文档或联系开发团队。

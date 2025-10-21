# 智能客服系统 - Linux Docker 部署指南

## 系统要求

- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **内存**: 至少4GB RAM
- **磁盘空间**: 至少10GB可用空间

## 快速部署

### 1. 安装Docker和Docker Compose

#### Ubuntu/Debian
```bash
# 更新包管理器
sudo apt update

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker
```

#### CentOS/RHEL
```bash
# 安装Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 下载项目

```bash
git clone <项目地址>
cd 智能客服
```

### 3. 配置环境变量

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的环境变量：
```bash
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

### 4. 构建前端

```bash
cd qianduan
npm install
npm run build
cd ..
```

### 5. 启动服务

#### 生产环境（推荐）
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 开发环境
```bash
# 启动开发环境（包含前端热重载）
docker-compose --profile dev up -d

# 仅启动后端和数据库
docker-compose up -d backend mysql redis
```

### 6. 初始化数据库

```bash
# 等待MySQL启动完成
sleep 30

# 运行数据库迁移
docker-compose exec backend python -m flask db upgrade

# 创建管理员用户（可选）
docker-compose exec backend python -c "
from houduan.app import create_app, db
from houduan.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        password_hash=generate_password_hash('admin123'),
        role='superadmin'
    )
    db.session.add(admin)
    db.session.commit()
    print('管理员用户创建成功')
"
```

## 服务管理

### 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 启动特定服务
docker-compose up -d backend mysql
```

### 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend

# 查看最近100行日志
docker-compose logs --tail=100 backend
```

### 进入容器
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入MySQL容器
docker-compose exec mysql mysql -u smartcs -p smart_cs
```

## 配置说明

### 1. 数据库配置

#### MySQL（默认）
- 数据库名：smart_cs
- 用户名：smartcs
- 密码：smartcs123
- 端口：3306

#### 使用外部MySQL
修改 `docker-compose.yml` 中的 `DATABASE_URL`：
```yaml
environment:
  - DATABASE_URL=mysql://username:password@host:port/database
```

### 2. Redis配置
- 端口：6379
- 数据持久化：已配置
- 内存限制：可配置

### 3. Nginx配置
- HTTP端口：80
- HTTPS端口：443（需要SSL证书）
- 静态文件：自动服务前端构建产物
- API代理：自动代理到后端服务

### 4. 环境变量

#### 必需配置
```bash
# 数据库连接
DATABASE_URL=mysql://smartcs:smartcs123@mysql:3306/smart_cs

# 应用密钥
SECRET_KEY=your-secret-key-change-in-production
```

#### AI模型配置（至少一个）
```bash
# OpenAI
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini

# 通义千问
QWEN_API_KEY=sk-xxx
QWEN_MODEL=qwen-turbo

# 文心一言
ERNIE_API_KEY=xxx
ERNIE_SECRET_KEY=xxx
ERNIE_MODEL=ernie-bot-turbo
```

#### 告警配置（可选）
```bash
# 邮件告警
ALERT_SMTP_SERVER=smtp.gmail.com
ALERT_SMTP_PORT=587
ALERT_EMAIL_USERNAME=your_email@gmail.com
ALERT_EMAIL_PASSWORD=your_app_password
ALERT_EMAIL_TO=admin@example.com,alert@example.com

# Webhook告警
ALERT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key
ALERT_WEBHOOK_TYPE=wechat
```

## 访问系统

### 1. 前端管理界面
- 地址：http://your-server-ip
- 功能：店铺配置、消息管理、审核队列、知识库管理、统计报表、用户管理

### 2. 后端API接口
- 地址：http://your-server-ip/api
- 健康检查：http://your-server-ip/health
- 直接访问：http://your-server-ip:5002

### 3. 数据库管理
- 地址：your-server-ip:3306
- 用户名：smartcs
- 密码：smartcs123
- 数据库：smart_cs

## 生产环境配置

### 1. 使用HTTPS

#### 获取SSL证书
```bash
# 使用Let's Encrypt（推荐）
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# 或使用自签名证书
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /path/to/ssl/key.pem \
    -out /path/to/ssl/cert.pem
```

#### 配置Nginx HTTPS
编辑 `nginx/conf.d/smart-cs.conf`，取消注释HTTPS配置部分。

### 2. 数据持久化

#### 数据库备份
```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec mysql mysqldump -u smartcs -psmartcs123 smart_cs > backup/smart_cs_$DATE.sql
echo "数据库备份完成: backup/smart_cs_$DATE.sql"
EOF

chmod +x backup.sh

# 设置定时备份
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

#### 数据恢复
```bash
# 恢复数据库
docker-compose exec -T mysql mysql -u smartcs -psmartcs123 smart_cs < backup/smart_cs_20240101_120000.sql
```

### 3. 监控和日志

#### 日志管理
```bash
# 查看日志大小
docker system df

# 清理日志
docker system prune -f

# 设置日志轮转
cat > /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
```

#### 系统监控
```bash
# 安装监控工具
sudo apt install htop iotop nethogs

# 监控容器资源使用
docker stats

# 监控磁盘使用
df -h
du -sh /var/lib/docker/volumes/*
```

### 4. 安全加固

#### 防火墙配置
```bash
# 安装UFW
sudo apt install ufw

# 配置防火墙规则
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

#### Docker安全
```bash
# 限制容器资源
# 在docker-compose.yml中添加：
# deploy:
#   resources:
#     limits:
#       memory: 1G
#       cpus: '0.5'

# 使用非root用户运行
# 在Dockerfile中添加：
# RUN adduser --disabled-password --gecos '' appuser
# USER appuser
```

## 故障排除

### 1. 容器启动失败
```bash
# 查看容器状态
docker-compose ps

# 查看错误日志
docker-compose logs backend

# 检查端口占用
netstat -tlnp | grep :5002
```

### 2. 数据库连接问题
```bash
# 检查MySQL状态
docker-compose exec mysql mysqladmin ping

# 检查数据库连接
docker-compose exec backend python -c "
from houduan.app import create_app, db
app = create_app()
with app.app_context():
    db.session.execute('SELECT 1')
    print('数据库连接正常')
"
```

### 3. 前端访问问题
```bash
# 检查Nginx状态
docker-compose exec nginx nginx -t

# 检查静态文件
docker-compose exec nginx ls -la /usr/share/nginx/html/

# 重新构建前端
cd qianduan
npm run build
cd ..
docker-compose restart nginx
```

### 4. 性能问题
```bash
# 监控资源使用
docker stats

# 检查日志大小
docker-compose logs --tail=1000 backend | wc -l

# 优化数据库
docker-compose exec mysql mysql -u smartcs -psmartcs123 smart_cs -e "
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Threads_connected';
"
```

## 升级和维护

### 1. 应用升级
```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build

# 滚动更新
docker-compose up -d --no-deps backend
```

### 2. 数据库迁移
```bash
# 运行迁移
docker-compose exec backend python -m flask db upgrade

# 检查迁移状态
docker-compose exec backend python -m flask db current
```

### 3. 清理和维护
```bash
# 清理未使用的镜像
docker image prune -f

# 清理未使用的容器
docker container prune -f

# 清理未使用的卷
docker volume prune -f

# 系统清理
docker system prune -f
```

## 性能优化

### 1. 数据库优化
```sql
-- 添加索引
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_shop_id ON messages(shop_id);
CREATE INDEX idx_ai_replies_message_id ON ai_replies(message_id);

-- 分析表
ANALYZE TABLE messages;
ANALYZE TABLE ai_replies;
```

### 2. 应用优化
```bash
# 增加工作进程
# 在docker-compose.yml中修改：
# command: ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5002", "houduan.app:create_app()"]
```

### 3. 缓存优化
```bash
# 启用Redis缓存
# 在应用中使用Redis进行缓存
```

## 技术支持

如遇到问题，请检查：
1. 容器日志：`docker-compose logs -f`
2. 系统资源：`docker stats`
3. 网络连接：`docker network ls`
4. 数据卷状态：`docker volume ls`

更多技术支持请参考项目文档或联系开发团队。

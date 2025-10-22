# 智能客服系统常见问题FAQ

## 概述

本文档收集了智能客服系统开发和使用过程中的常见问题及解决方案，帮助开发者和用户快速解决遇到的问题。

## 环境配置问题

### 1. Python环境问题

#### 问题: Python版本不兼容
**症状**: 安装依赖时出现版本错误
```
ERROR: Package 'xxx' requires a different Python: 3.8.0 not in '>=3.9,<4.0'
```

**解决方案**:
```bash
# 检查Python版本
python --version

# 安装Python 3.12+
# Windows: 从官网下载安装包
# Linux: 
sudo apt install python3.12 python3.12-pip python3.12-venv

# 创建虚拟环境
python3.12 -m venv venv
source venv/bin/activate  # Linux
venv\Scripts\activate     # Windows
```

#### 问题: pip安装失败
**症状**: pip install时出现网络错误或权限错误

**解决方案**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 使用代理
pip install -r requirements.txt --proxy http://proxy.company.com:8080
```

### 2. Node.js环境问题

#### 问题: Node.js版本过低
**症状**: npm install时出现版本错误
```
error: The engine "node" is incompatible with this module
```

**解决方案**:
```bash
# 检查Node.js版本
node --version

# 安装Node.js 18+
# 使用nvm管理版本
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

#### 问题: npm install失败
**症状**: npm install时出现网络错误或依赖冲突

**解决方案**:
```bash
# 清理npm缓存
npm cache clean --force

# 删除node_modules和package-lock.json
rm -rf node_modules package-lock.json

# 重新安装
npm install

# 使用国内镜像
npm install --registry https://registry.npmmirror.com
```

## 数据库问题

### 1. 数据库连接问题

#### 问题: 数据库文件不存在
**症状**: 启动时出现数据库错误
```
sqlite3.OperationalError: no such table: users
```

**解决方案**:
```bash
# 初始化数据库
cd houduan
python -m flask db upgrade

# 检查数据库文件
ls -la data/sqlite.db

# 如果文件不存在，创建目录
mkdir -p data
```

#### 问题: 数据库权限问题
**症状**: 无法写入数据库文件
```
sqlite3.OperationalError: database is locked
```

**解决方案**:
```bash
# 检查文件权限
ls -la data/sqlite.db

# 修复权限
chmod 664 data/sqlite.db
chown www-data:www-data data/sqlite.db

# 检查进程占用
lsof data/sqlite.db
```

### 2. 数据库迁移问题

#### 问题: 迁移失败
**症状**: flask db upgrade时出现错误
```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxx'
```

**解决方案**:
```bash
# 查看迁移历史
flask db history

# 重置迁移
flask db stamp head

# 重新生成迁移
flask db revision --autogenerate -m "init"

# 应用迁移
flask db upgrade
```

## 前端开发问题

### 1. 构建问题

#### 问题: Vite构建失败
**症状**: npm run build时出现错误
```
Error: Failed to resolve import "xxx" from "src/main.ts"
```

**解决方案**:
```bash
# 检查依赖
npm list

# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 检查TypeScript配置
npx tsc --noEmit

# 检查Vite配置
cat vite.config.ts
```

#### 问题: 端口冲突
**症状**: 启动时端口被占用
```
Error: listen EADDRINUSE: address already in use :5174
```

**解决方案**:
```bash
# 查找占用端口的进程
netstat -tulpn | grep :5174
lsof -i :5174

# 杀死进程
kill -9 <PID>

# 使用其他端口
npm run dev -- --port 5175
```

### 2. 路由问题

#### 问题: 路由404错误
**症状**: 访问页面时出现404错误

**解决方案**:
```typescript
// 检查路由配置
// router.ts
const routes = [
  {
    path: '/',
    redirect: '/shops'
  },
  {
    path: '/shops',
    name: 'Shops',
    component: () => import('./views/Shops.vue')
  }
]

// 检查路由守卫
router.beforeEach((to, from, next) => {
  // 路由守卫逻辑
  next()
})
```

### 3. API调用问题

#### 问题: CORS错误
**症状**: 前端调用API时出现CORS错误
```
Access to fetch at 'http://localhost:5002/api/shops' from origin 'http://localhost:5174' has been blocked by CORS policy
```

**解决方案**:
```python
# 后端CORS配置
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://localhost:5174"],
        "supports_credentials": True
    }
})
```

```typescript
// 前端HTTP配置
const http = axios.create({
  baseURL: 'http://localhost:5002',
  withCredentials: true
})
```

## 后端开发问题

### 1. Flask应用问题

#### 问题: 应用启动失败
**症状**: 启动时出现导入错误
```
ModuleNotFoundError: No module named 'houduan'
```

**解决方案**:
```bash
# 检查Python路径
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 使用模块方式启动
python -m houduan.app

# 检查__init__.py文件
touch houduan/__init__.py
```

#### 问题: 端口冲突
**症状**: 启动时端口被占用
```
OSError: [Errno 98] Address already in use
```

**解决方案**:
```bash
# 查找占用端口的进程
netstat -tulpn | grep :5002
lsof -i :5002

# 杀死进程
kill -9 <PID>

# 使用其他端口
python -m houduan.app --port 5003
```

### 2. 任务调度问题

#### 问题: APScheduler启动失败
**症状**: 启动时出现上下文错误
```
RuntimeError: Working outside of application context
```

**解决方案**:
```python
# 修复APScheduler上下文问题
def start_scheduler(app):
    with app.app_context():
        scheduler.add_job(
            func=check_unread_messages,
            trigger=IntervalTrigger(seconds=10),
            id='unread_check'
        )
        scheduler.start()
```

### 3. 数据库操作问题

#### 问题: 数据库连接超时
**症状**: 操作数据库时出现超时错误
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 20 overflow 0 reached
```

**解决方案**:
```python
# 优化数据库连接池
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 10,
    'max_overflow': 20,
    'pool_timeout': 30
}
```

## 部署问题

### 1. Windows部署问题

#### 问题: 批处理脚本执行失败
**症状**: 运行deploy_windows.bat时出现错误

**解决方案**:
```batch
@echo off
echo 检查环境...

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python未安装
    pause
    exit /b 1
)

REM 检查Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Node.js未安装
    pause
    exit /b 1
)

echo 环境检查通过
```

#### 问题: 服务启动失败
**症状**: 启动服务时出现错误

**解决方案**:
```batch
REM 检查端口占用
netstat -an | findstr :5002
netstat -an | findstr :5174

REM 清理进程
taskkill /f /im python.exe
taskkill /f /im node.exe

REM 重新启动
start_all.bat
```

### 2. Linux部署问题

#### 问题: Docker构建失败
**症状**: docker-compose up时出现构建错误

**解决方案**:
```bash
# 检查Docker版本
docker --version
docker-compose --version

# 清理Docker缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

#### 问题: 权限问题
**症状**: 文件权限错误
```
Permission denied: '/var/lib/smart-cs/sqlite.db'
```

**解决方案**:
```bash
# 检查文件权限
ls -la /var/lib/smart-cs/

# 修复权限
sudo chown -R www-data:www-data /var/lib/smart-cs/
sudo chmod -R 755 /var/lib/smart-cs/
```

## 性能问题

### 1. 响应慢问题

#### 问题: API响应慢
**症状**: 前端调用API时响应很慢

**解决方案**:
```python
# 优化数据库查询
def get_shops_optimized():
    return db.session.query(Shop).options(
        db.joinedload(Shop.users)
    ).all()

# 添加缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def get_shop_config(shop_id):
    shop = Shop.query.get(shop_id)
    return json.loads(shop.config_json) if shop.config_json else {}
```

#### 问题: 前端加载慢
**症状**: 页面加载很慢

**解决方案**:
```typescript
// 组件懒加载
const Shops = defineAsyncComponent(() => import('./views/Shops.vue'))

// 路由懒加载
const routes = [
  {
    path: '/shops',
    component: () => import('./views/Shops.vue')
  }
]
```

### 2. 内存问题

#### 问题: 内存泄漏
**症状**: 长时间运行后内存占用过高

**解决方案**:
```python
# 优化数据库连接
def get_db_connection():
    session = get_db_connection()
    try:
        yield session
    finally:
        session.close()

# 清理缓存
import gc
gc.collect()
```

## 调试技巧

### 1. 日志调试

#### 启用详细日志
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

# 使用日志
logger = logging.getLogger(__name__)
logger.debug('调试信息')
logger.info('信息')
logger.warning('警告')
logger.error('错误')
```

#### 前端调试
```typescript
// 启用Vue DevTools
if (process.env.NODE_ENV === 'development') {
  app.config.devtools = true
}

// 添加调试信息
console.log('API响应:', response.data)
console.log('组件状态:', { loading, data })
```

### 2. 网络调试

#### 检查网络连接
```bash
# 检查端口是否开放
telnet localhost 5002
telnet localhost 5174

# 检查防火墙
sudo ufw status
sudo firewall-cmd --list-all

# 检查进程
ps aux | grep python
ps aux | grep node
```

#### 使用curl测试API
```bash
# 测试健康检查
curl http://localhost:5002/health

# 测试登录
curl -X POST http://localhost:5002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 测试获取店铺列表
curl http://localhost:5002/api/shops
```

### 3. 数据库调试

#### 检查数据库状态
```python
# 检查数据库连接
from app import db
try:
    db.session.execute('SELECT 1')
    print('数据库连接正常')
except Exception as e:
    print(f'数据库连接失败: {e}')

# 检查表结构
from app import db
print(db.metadata.tables.keys())
```

#### 使用SQLite命令行
```bash
# 打开数据库
sqlite3 data/sqlite.db

# 查看表
.tables

# 查看表结构
.schema users

# 查询数据
SELECT * FROM users LIMIT 5;

# 退出
.quit
```

## 应急处理

### 1. 服务无法启动

#### 检查步骤
1. 检查环境变量
2. 检查端口占用
3. 检查文件权限
4. 检查依赖安装
5. 查看错误日志

#### 快速恢复
```bash
# 停止所有服务
pkill -f python
pkill -f node

# 清理临时文件
rm -rf __pycache__/
rm -rf node_modules/.cache/

# 重新启动
./start_all.sh
```

### 2. 数据丢失

#### 备份恢复
```bash
# 备份数据库
cp data/sqlite.db data/sqlite.db.backup.$(date +%Y%m%d_%H%M%S)

# 恢复数据库
cp data/sqlite.db.backup.20250121_120000 data/sqlite.db

# 检查数据完整性
sqlite3 data/sqlite.db "PRAGMA integrity_check;"
```

### 3. 性能问题

#### 快速诊断
```bash
# 检查系统资源
top
htop
free -h
df -h

# 检查网络连接
netstat -tulpn | grep :5002
netstat -tulpn | grep :5174

# 检查进程状态
ps aux | grep python
ps aux | grep node
```

## 总结

智能客服系统常见问题FAQ包含：

1. **环境配置问题**: Python、Node.js环境配置和依赖安装
2. **数据库问题**: 数据库连接、迁移、权限问题
3. **前端开发问题**: 构建、路由、API调用问题
4. **后端开发问题**: Flask应用、任务调度、数据库操作问题
5. **部署问题**: Windows、Linux部署问题
6. **性能问题**: 响应慢、内存泄漏问题
7. **调试技巧**: 日志、网络、数据库调试方法
8. **应急处理**: 服务恢复、数据恢复、性能诊断

该FAQ为智能客服系统提供了全面的问题解决方案，帮助开发者和用户快速解决遇到的问题。

---

**文档版本**: v1.0  
**最后更新**: 2025-01-21  
**维护人员**: 技术支持团队

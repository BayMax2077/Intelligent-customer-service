# 智能客服系统开发规范与指导文档

## 项目概述

### 系统简介
智能客服系统是一个基于UI自动化的淘宝千牛客服自动回复系统，采用四层架构设计：
- **UI自动化层**：监控千牛工作台消息，OCR识别，自动发送回复
- **知识库引擎**：向量检索+语义匹配，智能问答
- **Python服务**：Flask后端，处理业务逻辑
- **Web管理后台**：Vue 3前端，管理配置和审核

### 技术栈
- **后端**：Flask 3.0 + SQLAlchemy 2.0 + APScheduler
- **前端**：Vue 3 + Element Plus + Vite
- **数据库**：SQLite（开发）/ MySQL（生产）
- **AI模型**：OpenAI GPT / 通义千问 / 文心一言
- **OCR**：PaddleOCR / Tesseract
- **部署**：Docker + Nginx

## 开发环境配置

### 环境要求
- **Python**: 3.12+ (推荐使用官方安装包)
- **Node.js**: 18+ (推荐使用LTS版本)
- **操作系统**: Windows 10/11 (开发) / Linux (生产)
- **内存**: 至少4GB RAM
- **磁盘空间**: 至少2GB可用空间

### 本地开发环境搭建

#### 1. 克隆项目
```bash
git clone <项目地址>
cd 智能客服
```

#### 2. 后端环境配置
```bash
# 创建Python虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 激活虚拟环境 (Linux/macOS)
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -m flask db upgrade
```

#### 3. 前端环境配置
```bash
cd qianduan
npm install
npm run dev
```

#### 4. 启动服务
```bash
# 后端服务 (端口5002)
python -m houduan.app

# 前端服务 (端口5174)
cd qianduan && npm run dev
```

## 项目结构说明

### 目录结构
```
智能客服/
├── houduan/                    # 后端服务
│   ├── app.py                  # Flask应用入口
│   ├── config.py              # 配置管理
│   ├── models/                 # 数据模型
│   │   ├── __init__.py        # 模型定义
│   │   └── ...
│   ├── api/                    # API接口
│   │   ├── auth.py            # 认证接口
│   │   ├── shops.py           # 店铺管理
│   │   ├── messages.py        # 消息处理
│   │   ├── kb.py              # 知识库管理
│   │   ├── audit.py           # 审核队列
│   │   └── simple/            # 简化版API
│   ├── services/              # 业务逻辑
│   │   ├── qianniu_monitor.py # 千牛监控
│   │   ├── ai_adapter.py      # AI适配器
│   │   ├── message_handler.py # 消息处理
│   │   ├── knowledge_base.py  # 知识库服务
│   │   └── scheduler.py       # 任务调度
│   └── utils/                 # 工具函数
│       ├── db_manager.py      # 数据库管理
│       ├── cache_manager.py   # 缓存管理
│       └── security.py        # 安全工具
├── qianduan/                  # 前端应用
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   ├── components/        # 通用组件
│   │   ├── api/               # API客户端
│   │   └── store/             # 状态管理
│   └── dist/                  # 构建产物
├── tests/                     # 测试文件
├── data/                      # 数据目录
├── logs/                      # 日志目录
├── migrations/                # 数据库迁移
└── 项目文档/                  # 项目文档
```

## 开发规范

### 代码质量标准

#### 1. 可读性与结构性
- **命名规范**：使用有意义的变量、函数和类名
- **代码风格**：遵循PEP 8 (Python) 和 Google Style (JavaScript)
- **函数设计**：保持函数简短，功能单一
- **模块化**：按功能划分模块，避免循环依赖

#### 2. 注释与文档
- **文件头注释**：在重要文件开头说明功能、作者和修改历史
- **函数注释**：使用清晰的注释说明目的、参数、返回值和异常
- **关键逻辑注释**：在复杂算法前用中文解释"为什么这么做"

#### 3. 错误处理
- **异常捕获**：合理使用try-catch，避免静默失败
- **日志记录**：关键操作和错误都要记录日志
- **用户反馈**：错误信息要用户友好

### 数据库设计规范

#### 1. 表设计原则
- **主键**：每个表必须有主键，优先使用自增ID
- **外键**：合理使用外键约束，保证数据一致性
- **索引**：为常用查询字段添加索引
- **字段类型**：选择合适的字段类型，避免浪费空间

#### 2. 命名规范
- **表名**：使用复数形式，下划线分隔 (如: users, shop_configs)
- **字段名**：使用下划线分隔 (如: created_at, user_id)
- **索引名**：idx_表名_字段名 (如: idx_messages_created_at)

#### 3. 数据模型示例
```python
class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
```

### API设计规范

#### 1. RESTful设计
- **资源命名**：使用名词，复数形式
- **HTTP方法**：GET(查询)、POST(创建)、PUT(更新)、DELETE(删除)
- **状态码**：正确使用HTTP状态码
- **响应格式**：统一的JSON响应格式

#### 2. 响应格式标准
```python
# 成功响应
{
    "ok": True,
    "data": {...},
    "message": "操作成功"
}

# 错误响应
{
    "ok": False,
    "error": "错误信息",
    "code": "ERROR_CODE"
}
```

#### 3. API版本管理
- **URL版本**：/api/v1/endpoint
- **向后兼容**：新版本不破坏旧版本
- **废弃通知**：提前通知API废弃

### 前端开发规范

#### 1. Vue 3 组件规范
- **组件命名**：使用PascalCase (如: UserList.vue)
- **Props定义**：明确类型和默认值
- **事件命名**：使用kebab-case (如: @user-updated)
- **插槽使用**：合理使用具名插槽和作用域插槽

#### 2. 代码组织
```vue
<template>
  <!-- 模板内容 -->
</template>

<script setup lang="ts">
// 导入
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const loading = ref(false)
const items = ref([])

// 计算属性
const filteredItems = computed(() => {
  return items.value.filter(item => item.active)
})

// 方法
const loadData = async () => {
  loading.value = true
  try {
    // API调用
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
/* 组件样式 */
</style>
```

#### 3. 状态管理
- **Pinia使用**：合理使用Pinia进行状态管理
- **数据流**：明确数据流向，避免状态混乱
- **持久化**：需要持久化的状态使用localStorage

### 测试规范

#### 1. 测试分层
- **单元测试**：测试单个函数或方法
- **集成测试**：测试模块间交互
- **端到端测试**：测试完整业务流程

#### 2. 测试用例设计
```python
def test_user_login_success():
    """测试用户登录成功"""
    # 准备测试数据
    user = create_test_user()
    
    # 执行测试
    response = client.post('/api/auth/login', json={
        'username': user.username,
        'password': 'test_password'
    })
    
    # 验证结果
    assert response.status_code == 200
    assert response.json['ok'] is True
    assert 'token' in response.json['data']
```

#### 3. 测试覆盖率
- **目标覆盖率**：80%以上
- **关键路径**：100%覆盖
- **边界条件**：充分测试

## 开发流程

### 1. 功能开发流程
1. **需求分析**：明确功能需求和技术方案
2. **设计评审**：数据库设计、API设计评审
3. **编码实现**：按照规范编写代码
4. **单元测试**：编写并运行单元测试
5. **集成测试**：测试模块间交互
6. **代码审查**：同事审查代码质量
7. **部署测试**：在测试环境验证功能

### 2. 代码审查要点
- **功能正确性**：代码是否实现预期功能
- **代码质量**：是否遵循开发规范
- **性能考虑**：是否有性能问题
- **安全性**：是否有安全漏洞
- **可维护性**：代码是否易于维护

### 3. 版本控制规范
- **分支策略**：使用Git Flow
- **提交信息**：使用规范的提交信息格式
- **代码合并**：通过Pull Request合并代码

## 部署与运维

### 1. 环境配置

#### 开发环境
- **数据库**：SQLite (data/sqlite.db)
- **端口**：后端5002，前端5174
- **日志级别**：DEBUG

#### 生产环境
- **数据库**：MySQL 8.0+
- **端口**：80 (HTTP), 443 (HTTPS)
- **日志级别**：INFO
- **反向代理**：Nginx

### 2. 部署方式

#### Windows部署
```bash
# 运行部署脚本
deploy_windows.bat

# 启动服务
start_all.bat
```

#### Linux Docker部署
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 初始化数据库
docker-compose exec backend python -m flask db upgrade
```

### 3. 监控与告警
- **健康检查**：/health接口监控服务状态
- **日志监控**：关键错误和异常监控
- **性能监控**：响应时间和资源使用监控
- **告警机制**：邮件和Webhook告警

## 性能优化

### 1. 数据库优化
- **索引优化**：为常用查询字段添加索引
- **查询优化**：避免N+1查询，使用JOIN
- **连接池**：使用数据库连接池
- **缓存策略**：合理使用Redis缓存

### 2. 应用优化
- **异步处理**：耗时操作使用异步处理
- **资源管理**：及时释放资源
- **内存优化**：避免内存泄漏
- **并发控制**：合理控制并发数量

### 3. 前端优化
- **代码分割**：按需加载组件
- **资源压缩**：压缩CSS和JavaScript
- **缓存策略**：合理使用浏览器缓存
- **CDN加速**：使用CDN加速静态资源

## 安全规范

### 1. 数据安全
- **密码加密**：使用bcrypt加密密码
- **敏感数据**：加密存储敏感信息
- **SQL注入**：使用参数化查询
- **XSS防护**：对用户输入进行转义

### 2. 接口安全
- **认证机制**：使用JWT或Session认证
- **权限控制**：基于角色的访问控制
- **API限流**：防止API滥用
- **HTTPS**：生产环境使用HTTPS

### 3. 系统安全
- **防火墙**：配置防火墙规则
- **定期更新**：及时更新依赖包
- **安全扫描**：定期进行安全扫描
- **备份策略**：定期备份重要数据

## 故障排除

### 1. 常见问题
- **端口冲突**：检查端口占用情况
- **数据库连接**：检查数据库配置和连接
- **依赖问题**：检查Python和Node.js版本
- **权限问题**：检查文件权限和用户权限

### 2. 调试技巧
- **日志分析**：查看应用日志定位问题
- **断点调试**：使用IDE断点调试
- **网络抓包**：使用抓包工具分析网络请求
- **性能分析**：使用性能分析工具

### 3. 问题排查流程
1. **收集信息**：收集错误信息和日志
2. **分析原因**：分析问题根本原因
3. **制定方案**：制定解决方案
4. **实施修复**：实施修复方案
5. **验证结果**：验证修复效果
6. **总结经验**：总结问题和解决方案

## 最佳实践

### 1. 开发最佳实践
- **小步快跑**：频繁提交代码
- **测试驱动**：先写测试再写代码
- **代码复用**：提取公共代码
- **文档更新**：及时更新文档

### 2. 团队协作
- **沟通机制**：建立有效的沟通机制
- **知识分享**：定期进行技术分享
- **代码审查**：建立代码审查机制
- **持续改进**：持续改进开发流程

### 3. 项目管理
- **需求管理**：明确需求优先级
- **进度跟踪**：定期跟踪开发进度
- **风险控制**：识别和控制项目风险
- **质量保证**：建立质量保证体系

## 技术债务管理

### 1. 技术债务识别
- **代码质量**：代码复杂度、重复代码
- **架构问题**：架构不合理、耦合度高
- **性能问题**：响应慢、资源消耗大
- **安全问题**：安全漏洞、权限问题

### 2. 技术债务处理
- **优先级排序**：按影响程度排序
- **分期处理**：分阶段处理技术债务
- **重构计划**：制定重构计划
- **监控机制**：建立技术债务监控机制

### 3. 预防措施
- **代码规范**：严格执行代码规范
- **定期审查**：定期进行代码审查
- **自动化检查**：使用自动化工具检查
- **培训提升**：提升团队技术水平

## 总结

本开发规范文档为智能客服系统的开发工作提供了全面的指导，包括：

1. **技术架构**：明确了系统的技术选型和架构设计
2. **开发规范**：制定了代码质量、数据库、API、前端等开发规范
3. **开发流程**：建立了完整的开发流程和协作机制
4. **部署运维**：提供了部署和运维的最佳实践
5. **性能优化**：给出了性能优化的具体建议
6. **安全规范**：建立了安全开发的标准
7. **故障排除**：提供了问题排查的方法和技巧

遵循这些规范，可以确保项目的代码质量、开发效率和系统稳定性。建议团队成员认真学习并严格执行这些规范，同时根据项目实际情况不断完善和优化。

---

**文档版本**: v1.0  
**最后更新**: 2025-01-21  
**维护人员**: 开发团队  
**联系方式**: 项目组内部沟通渠道

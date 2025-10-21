# 智能客服系统测试文档

## 概述

本文档描述了智能客服系统的测试策略、测试用例和测试运行方法。

## 测试结构

```
tests/
├── conftest.py              # pytest 配置和共享 fixtures
├── test_api.py             # API 单元测试
├── test_frontend.py        # 前端组件测试
├── test_integration.py     # 集成测试
├── run_tests.py            # 测试运行脚本
├── README.md               # 测试文档
└── reports/                 # 测试报告目录
    ├── test_report.html    # HTML 测试报告
    ├── coverage_html/      # 覆盖率报告
    └── pytest_results.log # 测试日志
```

## 测试分类

### 1. 单元测试 (Unit Tests)
- **文件**: `test_api.py`
- **范围**: 单个API端点的功能测试
- **标记**: `@pytest.mark.unit`
- **目标**: 验证每个API端点的输入输出正确性

#### 测试用例包括：
- 健康检查接口
- 用户认证和授权
- 店铺CRUD操作
- 店铺配置管理
- 知识库CRUD操作
- 知识库搜索功能
- 消息处理流程
- 审核队列操作
- 统计API
- 用户管理
- 千牛自动化接口

### 2. 前端测试 (Frontend Tests)
- **文件**: `test_frontend.py`
- **范围**: 前端组件和用户界面测试
- **标记**: `@pytest.mark.frontend`
- **目标**: 验证前端功能正确性

#### 测试用例包括：
- 前端路由访问
- API CORS头设置
- 前端构建产物集成
- API响应格式一致性
- 错误处理
- 数据验证
- 分页功能
- 搜索功能
- 批量操作
- 性能指标
- 并发请求处理
- 内存使用情况
- 数据库连接池
- 日志功能
- 配置加载
- 安全头设置
- API版本控制
- 数据一致性

### 3. 集成测试 (Integration Tests)
- **文件**: `test_integration.py`
- **范围**: 端到端业务流程测试
- **标记**: `@pytest.mark.integration`
- **目标**: 验证完整业务流程的正确性

#### 测试用例包括：
- 完整工作流程（登录→配置→知识库→消息处理→审核）
- 多店铺工作流程
- 知识库完整工作流程
- 审核工作流程
- 统计工作流程
- 用户管理工作流程
- 错误恢复工作流程
- 性能工作流程
- 数据一致性工作流程

## 测试运行

### 1. 基本运行

```bash
# 运行所有测试
python tests/run_tests.py

# 运行单元测试
python tests/run_tests.py --unit

# 运行集成测试
python tests/run_tests.py --integration

# 运行前端测试
python tests/run_tests.py --frontend
```

### 2. 高级运行选项

```bash
# 运行测试并生成覆盖率报告
python tests/run_tests.py --coverage

# 生成HTML测试报告
python tests/run_tests.py --html

# 运行性能测试
python tests/run_tests.py --performance

# 运行快速测试（排除慢测试）
python tests/run_tests.py --quick

# 运行特定测试模式
python tests/run_tests.py --pattern "test_api.py"
```

### 3. 直接使用pytest

```bash
# 运行所有测试
pytest tests/

# 运行特定文件
pytest tests/test_api.py

# 运行特定测试
pytest tests/test_api.py::test_login_success

# 运行带标记的测试
pytest -m "unit"
pytest -m "integration"
pytest -m "not slow"

# 运行测试并生成覆盖率报告
pytest --cov=houduan --cov-report=html

# 运行测试并生成HTML报告
pytest --html=reports/test_report.html --self-contained-html
```

## 测试配置

### 1. pytest.ini
- 测试发现配置
- 输出选项
- 标记定义
- 过滤选项
- 超时设置

### 2. conftest.py
- 共享fixtures
- 测试配置
- 环境设置
- 数据准备

### 3. 环境变量
测试环境支持以下环境变量：
- `DATABASE_URL`: 测试数据库连接
- `SECRET_KEY`: 测试密钥
- `TESTING`: 测试模式标识

## 测试数据

### 1. 测试用户
- 默认管理员: `admin/admin`
- 测试用户: `test_user_*/test_password_*`

### 2. 测试店铺
- 名称: `测试店铺*`
- 千牛标题: `千牛测试*`

### 3. 测试知识库
- 问题: `如何退款？`、`如何发货？`、`如何联系客服？`
- 答案: 对应的标准回复
- 分类: `售后`、`发货`、`联系`

### 4. 测试消息
- 客户ID: `customer_*`
- 内容: `测试消息*`
- 状态: `new`、`answered`、`review`、`queued`

## 测试报告

### 1. HTML报告
- 位置: `reports/test_report.html`
- 内容: 测试结果、失败详情、执行时间

### 2. 覆盖率报告
- 位置: `reports/coverage_html/index.html`
- 内容: 代码覆盖率统计、未覆盖代码

### 3. 日志文件
- 位置: `reports/pytest_results.log`
- 内容: 详细测试执行日志

## 测试最佳实践

### 1. 测试命名
- 测试函数: `test_功能描述`
- 测试类: `Test类名`
- 测试文件: `test_模块名.py`

### 2. 测试结构
- 准备 (Arrange): 设置测试数据
- 执行 (Act): 执行被测试的功能
- 断言 (Assert): 验证结果

### 3. 测试隔离
- 每个测试独立运行
- 测试间不共享状态
- 使用临时数据库

### 4. 测试数据
- 使用fixtures管理测试数据
- 测试后自动清理
- 避免硬编码数据

### 5. 错误处理
- 测试异常情况
- 验证错误消息
- 检查错误状态码

## 持续集成

### 1. GitHub Actions
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - name: Install dependencies
        run: |
          pip install -r houduan/requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: python tests/run_tests.py --coverage
```

### 2. 测试矩阵
- Python版本: 3.8, 3.9, 3.10, 3.11, 3.12
- 操作系统: Windows, Linux, macOS
- 数据库: SQLite, MySQL, PostgreSQL

## 故障排除

### 1. 常见问题

#### 测试失败
- 检查数据库连接
- 验证环境变量
- 查看测试日志

#### 依赖问题
- 更新pip: `pip install --upgrade pip`
- 重新安装依赖: `pip install -r houduan/requirements.txt`
- 检查虚拟环境

#### 权限问题
- 检查文件权限
- 验证数据库权限
- 确认端口可用性

### 2. 调试技巧

#### 详细输出
```bash
pytest -v -s tests/test_api.py
```

#### 调试特定测试
```bash
pytest --pdb tests/test_api.py::test_login_success
```

#### 查看测试收集
```bash
pytest --collect-only tests/
```

## 测试维护

### 1. 定期更新
- 更新测试用例
- 添加新功能测试
- 修复过时测试

### 2. 性能优化
- 优化慢测试
- 并行执行测试
- 减少测试数据

### 3. 代码质量
- 保持测试代码简洁
- 使用有意义的断言
- 添加适当的注释

## 贡献指南

### 1. 添加新测试
1. 在相应测试文件中添加测试函数
2. 使用适当的fixtures
3. 添加必要的断言
4. 更新测试文档

### 2. 修改现有测试
1. 确保修改不会破坏现有功能
2. 更新相关文档
3. 运行完整测试套件

### 3. 测试审查
1. 检查测试覆盖率
2. 验证测试逻辑
3. 确保测试可重复性

## 联系信息

如有测试相关问题，请联系开发团队或提交Issue。

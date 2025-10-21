@echo off
chcp 65001 >nul
echo ========================================
echo 智能客服系统 - Windows 部署脚本
echo ========================================
echo.

REM 检查Python版本
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.12+
    pause
    exit /b 1
)

echo [信息] 检测到Python环境
python --version

REM 检查Node.js版本
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js，请先安装Node.js 18+
    pause
    exit /b 1
)

echo [信息] 检测到Node.js环境
node --version

echo.
echo [步骤1] 创建Python虚拟环境...
if not exist ".venv" (
    python -m venv .venv
    echo [成功] 虚拟环境创建完成
) else (
    echo [信息] 虚拟环境已存在
)

echo.
echo [步骤2] 激活虚拟环境并安装后端依赖...
call .venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [步骤3] 初始化数据库...
python -m flask db upgrade
echo [成功] 数据库初始化完成

echo.
echo [步骤4] 安装前端依赖...
cd qianduan
if not exist "node_modules" (
    npm install
    echo [成功] 前端依赖安装完成
) else (
    echo [信息] 前端依赖已存在
)

echo.
echo [步骤5] 构建前端...
npm run build
if errorlevel 1 (
    echo [错误] 前端构建失败
    pause
    exit /b 1
)
echo [成功] 前端构建完成

cd ..

echo.
echo [步骤6] 创建启动脚本...
echo @echo off > start_backend.bat
echo chcp 65001 ^>nul >> start_backend.bat
echo echo 启动智能客服后端服务... >> start_backend.bat
echo call .venv\Scripts\activate.bat >> start_backend.bat
echo python -m flask run --host=0.0.0.0 --port=5002 >> start_backend.bat
echo pause >> start_backend.bat

echo @echo off > start_frontend.bat
echo chcp 65001 ^>nul >> start_frontend.bat
echo echo 启动智能客服前端服务... >> start_frontend.bat
echo cd qianduan >> start_frontend.bat
echo npm run preview -- --port 5174 --strictPort >> start_frontend.bat
echo pause >> start_frontend.bat

echo @echo off > start_all.bat
echo chcp 65001 ^>nul >> start_all.bat
echo echo 启动智能客服系统... >> start_all.bat
echo start "后端服务" cmd /k "call .venv\Scripts\activate.bat ^&^& python -m flask run --host=0.0.0.0 --port=5002" >> start_all.bat
echo timeout /t 3 /nobreak ^>nul >> start_all.bat
echo start "前端服务" cmd /k "cd qianduan ^&^& npm run preview -- --port 5174 --strictPort" >> start_all.bat
echo echo 系统启动完成！ >> start_all.bat
echo echo 后端地址: http://localhost:5002 >> start_all.bat
echo echo 前端地址: http://localhost:5174 >> start_all.bat
echo pause >> start_all.bat

echo [成功] 启动脚本创建完成

echo.
echo [步骤7] 创建环境变量配置文件...
echo # 智能客服系统环境配置 > .env.example
echo # 复制此文件为 .env 并修改相应配置 >> .env.example
echo. >> .env.example
echo # 数据库配置 >> .env.example
echo # DATABASE_URL=sqlite:///data/sqlite.db >> .env.example
echo # DATABASE_URL=mysql://user:password@localhost/smart_cs >> .env.example
echo. >> .env.example
echo # AI模型配置 >> .env.example
echo # OPENAI_API_KEY=your_openai_api_key >> .env.example
echo # OPENAI_MODEL=gpt-4o-mini >> .env.example
echo # QWEN_API_KEY=your_qwen_api_key >> .env.example
echo # QWEN_MODEL=qwen-turbo >> .env.example
echo # ERNIE_API_KEY=your_ernie_api_key >> .env.example
echo # ERNIE_SECRET_KEY=your_ernie_secret_key >> .env.example
echo # ERNIE_MODEL=ernie-bot-turbo >> .env.example
echo. >> .env.example
echo # 告警配置 >> .env.example
echo # ALERT_SMTP_SERVER=smtp.gmail.com >> .env.example
echo # ALERT_SMTP_PORT=587 >> .env.example
echo # ALERT_EMAIL_USERNAME=your_email@gmail.com >> .env.example
echo # ALERT_EMAIL_PASSWORD=your_app_password >> .env.example
echo # ALERT_EMAIL_TO=admin@example.com,alert@example.com >> .env.example
echo # ALERT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key >> .env.example
echo # ALERT_WEBHOOK_TYPE=wechat >> .env.example

echo [成功] 环境配置文件创建完成

echo.
echo ========================================
echo 部署完成！
echo ========================================
echo.
echo 使用方法：
echo 1. 双击 start_all.bat 启动完整系统
echo 2. 双击 start_backend.bat 仅启动后端
echo 3. 双击 start_frontend.bat 仅启动前端
echo.
echo 访问地址：
echo - 前端管理界面: http://localhost:5174
echo - 后端API接口: http://localhost:5002
echo - 健康检查: http://localhost:5002/health
echo.
echo 配置说明：
echo - 复制 .env.example 为 .env 并配置AI模型密钥
echo - 默认使用SQLite数据库，生产环境建议使用MySQL
echo - 首次使用请访问前端界面创建管理员账户
echo.
pause

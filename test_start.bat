@echo off
chcp 65001 >nul
echo 测试启动智能客服系统...

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 设置环境变量
set FLASK_APP=houduan.app
set FLASK_ENV=development

echo 启动后端服务...
echo 后端地址: http://localhost:5002
echo 健康检查: http://localhost:5002/health
echo.
echo 按 Ctrl+C 停止服务
echo.

REM 启动Flask应用
python -m flask run --host=0.0.0.0 --port=5002

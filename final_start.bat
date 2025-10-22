@echo off
chcp 65001 >nul
echo ========================================
echo 智能客服系统 - 最终启动脚本
echo ========================================

echo 1. 停止现有服务...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 3 /nobreak >nul

echo 2. 启动后端服务...
start "智能客服后端" cmd /k "call .venv\Scripts\activate.bat && python -c \"from houduan.app import create_app; app = create_app(); app.run(host='0.0.0.0', port=5002, debug=True)\""

echo 3. 等待后端启动...
timeout /t 10 /nobreak >nul

echo 4. 启动前端服务...
start "智能客服前端" cmd /k "cd qianduan && npm run preview -- --port 5174 --strictPort"

echo 5. 启动调试服务器...
start "调试服务器" cmd /k "python -m http.server 8080"

echo.
echo ========================================
echo 启动完成！
echo ========================================
echo.
echo 访问地址：
echo - 前端管理界面: http://localhost:5174
echo - 后端API接口: http://localhost:5002
echo - 健康检查: http://localhost:5002/health
echo - 调试工具: http://localhost:8080/test_edit_fix.html
echo.
echo 登录信息：
echo - 用户名: admin
echo - 密码: admin123
echo.
echo 功能说明：
echo - OCR混合检测优化已启用
echo - 店铺编辑功能已修复
echo - 缓存清理机制已集成
echo.
echo 按任意键关闭此窗口...
pause >nul

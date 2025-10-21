@echo off
setlocal

REM --- 智能客服系统测试运行脚本 ---
REM 使用方法：
REM   run_tests.bat                    # 运行所有测试
REM   run_tests.bat --unit             # 只运行单元测试
REM   run_tests.bat --integration      # 只运行集成测试
REM   run_tests.bat --frontend         # 只运行前端测试
REM   run_tests.bat --coverage         # 运行测试并生成覆盖率报告
REM   run_tests.bat --html             # 生成HTML测试报告

echo.
echo --- 智能客服系统测试运行器 ---
echo.

REM --- 检查环境 ---
echo 检查测试环境...

REM 检查Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python。请安装 Python 3.8+ 或更高版本。
    goto :eof
)

REM 检查虚拟环境
if not exist .venv (
    echo 错误: 虚拟环境不存在。请先运行部署脚本。
    goto :eof
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 错误: 无法激活虚拟环境。
    goto :eof
)

REM 检查pytest
python -c "import pytest" >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: pytest未安装。请先安装依赖。
    goto :eof
)

echo 环境检查通过。
echo.

REM --- 创建报告目录 ---
if not exist reports mkdir reports

REM --- 运行测试 ---
echo 开始运行测试...
echo.

REM 检查参数
if "%1"=="" (
    REM 默认运行所有测试
    python tests/run_tests.py
) else (
    REM 运行指定测试
    python tests/run_tests.py %*
)

REM --- 检查结果 ---
if %errorlevel% equ 0 (
    echo.
    echo ✅ 测试完成！
    echo.
    echo 测试报告位置：
    echo   - HTML报告: reports\test_report.html
    echo   - 覆盖率报告: reports\coverage_html\index.html
    echo   - 测试日志: reports\pytest_results.log
    echo.
) else (
    echo.
    echo ❌ 测试失败！
    echo 请检查错误信息并修复问题。
    echo.
)

echo 按任意键退出...
pause >nul

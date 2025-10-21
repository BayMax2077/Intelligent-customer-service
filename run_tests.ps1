# 智能客服系统测试运行脚本 (PowerShell)
# 使用方法：
#   .\run_tests.ps1                    # 运行所有测试
#   .\run_tests.ps1 -Unit              # 只运行单元测试
#   .\run_tests.ps1 -Integration       # 只运行集成测试
#   .\run_tests.ps1 -Frontend          # 只运行前端测试
#   .\run_tests.ps1 -Coverage          # 运行测试并生成覆盖率报告
#   .\run_tests.ps1 -Html              # 生成HTML测试报告

param(
    [switch]$Unit,
    [switch]$Integration,
    [switch]$Frontend,
    [switch]$Coverage,
    [switch]$Html,
    [switch]$Performance,
    [switch]$Quick,
    [string]$Pattern,
    [switch]$Verbose
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 检查环境函数
function Test-Environment {
    Write-ColorOutput "检查测试环境..." "Yellow"
    
    # 检查Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python未安装或不在PATH中"
        }
        Write-ColorOutput "✅ Python版本: $pythonVersion" "Green"
    }
    catch {
        Write-ColorOutput "❌ Python检查失败: $_" "Red"
        return $false
    }
    
    # 检查虚拟环境
    if (-not (Test-Path ".venv")) {
        Write-ColorOutput "❌ 虚拟环境不存在，请先运行部署脚本" "Red"
        return $false
    }
    
    # 激活虚拟环境
    try {
        & ".venv\Scripts\Activate.ps1"
        if ($LASTEXITCODE -ne 0) {
            throw "无法激活虚拟环境"
        }
        Write-ColorOutput "✅ 虚拟环境已激活" "Green"
    }
    catch {
        Write-ColorOutput "❌ 虚拟环境激活失败: $_" "Red"
        return $false
    }
    
    # 检查pytest
    try {
        python -c "import pytest" 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "pytest未安装"
        }
        Write-ColorOutput "✅ pytest已安装" "Green"
    }
    catch {
        Write-ColorOutput "❌ pytest检查失败: $_" "Red"
        return $false
    }
    
    Write-ColorOutput "✅ 环境检查通过" "Green"
    return $true
}

# 运行测试函数
function Invoke-Tests {
    param(
        [string]$TestType,
        [string]$Description,
        [string[]]$Arguments = @()
    )
    
    Write-ColorOutput "`n$('='*60)" "Cyan"
    Write-ColorOutput "运行: $Description" "Cyan"
    Write-ColorOutput "类型: $TestType" "Cyan"
    Write-ColorOutput "$('='*60)" "Cyan"
    
    try {
        $cmd = @("python", "tests/run_tests.py") + $Arguments
        if ($Verbose) {
            $cmd += @("-v")
        }
        
        Write-ColorOutput "命令: $($cmd -join ' ')" "Gray"
        
        $result = & $cmd[0] $cmd[1..($cmd.Length-1)]
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ 测试成功完成" "Green"
            return $true
        } else {
            Write-ColorOutput "❌ 测试失败" "Red"
            return $false
        }
    }
    catch {
        Write-ColorOutput "❌ 测试执行出错: $_" "Red"
        return $false
    }
}

# 创建报告目录
function New-ReportDirectory {
    if (-not (Test-Path "reports")) {
        New-Item -ItemType Directory -Path "reports" -Force | Out-Null
        Write-ColorOutput "✅ 创建报告目录: reports" "Green"
    }
}

# 主函数
function Main {
    Write-ColorOutput "智能客服系统测试运行器 (PowerShell)" "Cyan"
    Write-ColorOutput "=" * 60 "Cyan"
    
    # 检查环境
    if (-not (Test-Environment)) {
        Write-ColorOutput "环境检查失败，退出测试" "Red"
        exit 1
    }
    
    # 创建报告目录
    New-ReportDirectory
    
    $success = $true
    
    try {
        # 根据参数运行相应测试
        if ($Unit) {
            $success = Invoke-Tests "单元测试" "API单元测试" @("--unit")
        }
        elseif ($Integration) {
            $success = Invoke-Tests "集成测试" "端到端集成测试" @("--integration")
        }
        elseif ($Frontend) {
            $success = Invoke-Tests "前端测试" "前端组件测试" @("--frontend")
        }
        elseif ($Coverage) {
            $success = Invoke-Tests "覆盖率测试" "测试覆盖率分析" @("--coverage")
        }
        elseif ($Html) {
            $success = Invoke-Tests "HTML报告" "生成HTML测试报告" @("--html")
        }
        elseif ($Performance) {
            $success = Invoke-Tests "性能测试" "性能基准测试" @("--performance")
        }
        elseif ($Quick) {
            $success = Invoke-Tests "快速测试" "快速测试套件" @("--quick")
        }
        elseif ($Pattern) {
            $success = Invoke-Tests "特定测试" "特定测试模式: $Pattern" @("--pattern", $Pattern)
        }
        else {
            # 默认运行所有测试
            $success = Invoke-Tests "全部测试" "完整测试套件" @()
        }
        
        if ($success) {
            Write-ColorOutput "`n🎉 所有测试通过！" "Green"
            Write-ColorOutput "`n测试报告位置：" "Yellow"
            Write-ColorOutput "  - HTML报告: reports\test_report.html" "White"
            Write-ColorOutput "  - 覆盖率报告: reports\coverage_html\index.html" "White"
            Write-ColorOutput "  - 测试日志: reports\pytest_results.log" "White"
            Write-ColorOutput ""
        } else {
            Write-ColorOutput "`n❌ 测试失败！" "Red"
            Write-ColorOutput "请检查错误信息并修复问题。" "Yellow"
        }
    }
    catch {
        Write-ColorOutput "`n💥 测试运行出错: $_" "Red"
        $success = $false
    }
    
    # 退出
    if ($success) {
        Write-ColorOutput "`n按任意键退出..." "Gray"
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 0
    } else {
        Write-ColorOutput "`n按任意键退出..." "Gray"
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
}

# 运行主函数
Main

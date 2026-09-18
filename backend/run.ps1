# 启动后端（PowerShell）。等价于：
# .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000
Set-Location $PSScriptRoot

if (-not (Test-Path .\.venv)) {
  python -m venv .venv
  .\.venv\Scripts\python.exe -m pip install --upgrade pip
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
}

if (-not (Test-Path .\.env)) {
  Copy-Item .\.env.example .env
  Write-Host "已从 .env.example 创建 .env，请先填写 LLM / Embedding 的密钥与模型名后重新运行本脚本。" -ForegroundColor Yellow
  exit 0
}

.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

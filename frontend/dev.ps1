# 启动前端开发服务器（PowerShell）。
# 注意：当项目绝对路径含空格或 "&" 字符时，`npm run dev` 在部分 Windows 环境会被
# cmd 截断路径，因此这里用 node 直接调用 vite，效果与 `npm run dev` 完全一致。
Set-Location $PSScriptRoot

if (-not (Test-Path .\node_modules)) {
  npm install
}

node .\node_modules\vite\bin\vite.js

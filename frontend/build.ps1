# 生产构建（PowerShell），等价于 npm run build，但可在含 "&" 的路径下正常工作。
Set-Location $PSScriptRoot
node .\node_modules\vite\bin\vite.js build

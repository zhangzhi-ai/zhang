# 启动前端（PowerShell）
Set-Location -LiteralPath "$PSScriptRoot"
if (-Not (Test-Path 'node_modules')) {
  npm install
}
npm run serve

# 启动后端（PowerShell）
Set-Location -LiteralPath "$PSScriptRoot"
if (-Not (Test-Path .venv)) {
  python -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python manage.py migrate
Start-Process -NoNewWindow -FilePath '.\.venv\Scripts\python.exe' -ArgumentList 'manage.py','runserver','0.0.0.0:8000' -WorkingDirectory $PWD

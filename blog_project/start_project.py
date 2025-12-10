#!/usr/bin/env python
"""
Django博客项目启动脚本
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """执行命令"""
    print(f"执行命令: {command}")
    if cwd:
        print(f"工作目录: {cwd}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_python():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")

def install_requirements():
    """安装Python依赖"""
    print("\n安装Python依赖...")
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        run_command("pip install -r requirements.txt")
    else:
        print("requirements.txt文件不存在，跳过依赖安装")

def setup_database():
    """设置数据库"""
    print("\n设置数据库...")
    
    # 检查是否需要创建迁移文件
    print("创建数据库迁移文件...")
    run_command("python manage.py makemigrations")
    
    # 执行迁移
    print("执行数据库迁移...")
    run_command("python manage.py migrate")
    
    # 检查是否需要创建超级用户
    print("\n检查超级用户...")
    result = run_command("python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); print('exists' if User.objects.filter(is_superuser=True).exists() else 'none')\"", check=False)
    
    if result.returncode == 0 and 'none' in result.stdout:
        print("创建超级用户...")
        print("请按提示输入超级用户信息:")
        run_command("python manage.py createsuperuser")

def collect_static():
    """收集静态文件"""
    print("\n收集静态文件...")
    run_command("python manage.py collectstatic --noinput", check=False)

def start_django_server():
    """启动Django服务器"""
    print("\n启动Django开发服务器...")
    print("Django服务器将在 http://127.0.0.1:8000 启动")
    print("按 Ctrl+C 停止服务器")
    
    try:
        subprocess.run("python manage.py runserver", shell=True)
    except KeyboardInterrupt:
        print("\n服务器已停止")

def main():
    """主函数"""
    print("=" * 50)
    print("Django博客项目启动脚本")
    print("=" * 50)
    
    # 检查当前目录
    if not Path("manage.py").exists():
        print("错误: 请在Django项目根目录下运行此脚本")
        sys.exit(1)
    
    try:
        # 1. 检查Python版本
        check_python()
        
        # 2. 安装依赖
        install_requirements()
        
        # 3. 设置数据库
        setup_database()
        
        # 4. 收集静态文件
        collect_static()
        
        # 5. 启动服务器
        start_django_server()
        
    except KeyboardInterrupt:
        print("\n\n项目启动被用户中断")
    except Exception as e:
        print(f"\n启动过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
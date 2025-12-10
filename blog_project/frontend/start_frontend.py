#!/usr/bin/env python
"""
Vue.js前端启动脚本
"""
import os
import sys
import subprocess
import json
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

def check_node():
    """检查Node.js和npm"""
    print("检查Node.js和npm...")
    
    try:
        # 检查Node.js
        result = run_command("node --version")
        print(f"Node.js版本: {result.stdout.strip()}")
        
        # 检查npm
        result = run_command("npm --version")
        print(f"npm版本: {result.stdout.strip()}")
        
    except:
        print("错误: 未找到Node.js或npm，请先安装Node.js")
        print("下载地址: https://nodejs.org/")
        sys.exit(1)

def install_dependencies():
    """安装前端依赖"""
    print("\n安装前端依赖...")
    
    package_json = Path("package.json")
    if not package_json.exists():
        print("错误: package.json文件不存在")
        sys.exit(1)
    
    # 检查node_modules是否存在
    node_modules = Path("node_modules")
    if not node_modules.exists():
        print("首次运行，安装依赖包...")
        run_command("npm install")
    else:
        print("依赖包已存在，跳过安装")

def create_vue_config():
    """创建Vue配置文件"""
    print("\n创建Vue配置文件...")
    
    vue_config = """const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  publicPath: process.env.NODE_ENV === 'production' ? '/static/' : '/'
})
"""
    
    with open("vue.config.js", "w", encoding="utf-8") as f:
        f.write(vue_config)
    
    print("Vue配置文件已创建")

def start_dev_server():
    """启动开发服务器"""
    print("\n启动Vue.js开发服务器...")
    print("前端服务器将在 http://localhost:8080 启动")
    print("请确保Django后端服务器已在 http://localhost:8000 启动")
    print("按 Ctrl+C 停止服务器")
    
    try:
        subprocess.run("npm run serve", shell=True)
    except KeyboardInterrupt:
        print("\n前端服务器已停止")

def main():
    """主函数"""
    print("=" * 50)
    print("Vue.js前端启动脚本")
    print("=" * 50)
    
    # 检查当前目录
    if not Path("package.json").exists():
        print("错误: 请在前端项目目录下运行此脚本")
        sys.exit(1)
    
    try:
        # 1. 检查Node.js环境
        check_node()
        
        # 2. 安装依赖
        install_dependencies()
        
        # 3. 创建配置文件
        create_vue_config()
        
        # 4. 启动开发服务器
        start_dev_server()
        
    except KeyboardInterrupt:
        print("\n\n前端服务器启动被用户中断")
    except Exception as e:
        print(f"\n启动过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
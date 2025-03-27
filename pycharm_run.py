"""
PyCharm项目运行脚本

此脚本用于在PyCharm中设置和运行智能教育辅助平台项目。
它提供了设置Python解释器、配置项目路径和启动应用的功能。
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def select_python_interpreter():
    """选择Python解释器路径"""
    root = tk.Tk()
    root.withdraw()
    
    print("请选择Python解释器路径...")
    python_path = filedialog.askopenfilename(
        title="选择Python解释器",
        filetypes=[("Python解释器", "python*.exe"), ("所有文件", "*.*")],
        initialdir="C:/Program Files/Python"
    )
    
    if not python_path:
        print("未选择Python解释器，将使用系统默认的Python")
        return sys.executable
        
    return python_path

def setup_project():
    """设置项目环境"""
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"项目根目录: {project_dir}")
    
    # 确保项目路径在Python路径中
    if project_dir not in sys.path:
        sys.path.append(project_dir)
        
    # 检查项目结构
    aigc_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"AIGC项目目录: {aigc_dir}")
    
    required_dirs = ["speech_to_scratch", "code_visualization", "utils"]
    missing_dirs = [d for d in required_dirs if not os.path.exists(os.path.join(aigc_dir, d))]
    
    if missing_dirs:
        print(f"警告: 项目缺少以下目录: {', '.join(missing_dirs)}")
        return False
        
    print("项目结构检查完成")
    return True

def run_app_in_pycharm():
    """在PyCharm环境中运行应用"""
    # 获取当前脚本目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 应用主文件路径
    app_path = os.path.join(current_dir, "app.py")
    
    if not os.path.exists(app_path):
        print(f"错误: 找不到应用主文件 {app_path}")
        return False
    
    print("\n设置PyCharm运行配置:")
    print("1. 打开PyCharm的'运行/调试配置'")
    print("2. 添加一个新的Python配置")
    print("3. 设置脚本路径为:", app_path)
    print("4. 设置工作目录为:", current_dir)
    print("5. 保存配置并运行\n")
    
    # 询问是否使用streamlit直接运行
    run_now = input("是否立即使用streamlit运行应用? (y/n): ").lower() == 'y'
    
    if run_now:
        try:
            print("\n正在启动应用...")
            subprocess.check_call([sys.executable, "-m", "streamlit", "run", app_path])
            return True
        except subprocess.CalledProcessError as e:
            print(f"应用启动失败: {str(e)}")
            return False
    
    return True

def setup_pycharm_project():
    """设置PyCharm项目"""
    print("===== PyCharm项目设置助手 =====")
    
    # 选择Python解释器
    python_path = select_python_interpreter()
    print(f"已选择Python解释器: {python_path}")
    
    # 设置项目环境
    if not setup_project():
        print("项目设置遇到问题，请检查目录结构")
        return
    
    # 打印PyCharm配置指南
    print("\nPyCharm项目配置指南:")
    print("1. 打开PyCharm并选择'打开'")
    print("2. 导航到AIGC_Project目录并选择")
    print("3. 在PyCharm中，转到'文件 > 设置 > 项目 > Python解释器'")
    print(f"4. 添加解释器，选择路径: {python_path}")
    print("5. 确保所有依赖已安装(可以使用PyCharm的包管理器安装)")
    
    # 询问是否继续运行应用
    continue_run = input("\n是否配置运行应用? (y/n): ").lower() == 'y'
    
    if continue_run:
        run_app_in_pycharm()
    
    print("\n===== PyCharm设置完成 =====")
    print("您现在可以在PyCharm中打开和运行项目了")

if __name__ == "__main__":
    setup_pycharm_project() 
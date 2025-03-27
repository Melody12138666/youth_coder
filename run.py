import os
import sys
import subprocess
import argparse
from pathlib import Path
import io
import codecs

def install_dependencies():
    """安装项目依赖"""
    print("正在检查并安装依赖...")
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    
    # 读取requirements.txt文件内容，确保使用UTF-8编码
    try:
        with codecs.open(requirements_path, 'r', encoding='utf-8') as f:
            requirements = f.read()
        
        # 创建临时requirements文件，使用utf-8编码
        temp_requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.temp.txt")
        with codecs.open(temp_requirements_path, 'w', encoding='utf-8') as f:
            f.write(requirements)
        
        # 使用subprocess安装依赖
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", temp_requirements_path])
        print("依赖安装完成！")
        
        # 删除临时文件
        try:
            os.remove(temp_requirements_path)
        except:
            pass
    except UnicodeDecodeError:
        print("文件编码问题。尝试手动安装主要依赖...")
        try:
            # 直接安装主要依赖
            subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit==1.27.0", "numpy==1.26.0", "matplotlib==3.8.0"])
            print("基本依赖安装完成，但建议手动安装其他依赖。")
        except subprocess.CalledProcessError as e:
            print(f"依赖安装失败: {str(e)}")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {str(e)}")
        sys.exit(1)

def generate_examples():
    """生成示例项目和可视化"""
    print("\n准备生成示例内容...")
    
    # 导入相关模块
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # 生成Scratch项目示例
        print("\n生成Scratch项目示例...")
        try:
            from speech_to_scratch.examples import generate_scratch_examples, print_example_info
            examples_dir = generate_scratch_examples()
            print_example_info()
        except Exception as e:
            print(f"生成Scratch示例失败: {str(e)}")
        
        # 生成代码可视化示例
        print("\n生成代码可视化示例...")
        try:
            from code_visualization.examples import generate_visualization_examples, print_available_examples
            visualization_examples = generate_visualization_examples()
            print_available_examples()
        except Exception as e:
            print(f"生成可视化示例失败: {str(e)}")
            
        print("\n所有示例生成完成！")
    except ImportError as e:
        print(f"导入模块失败: {str(e)}")
        sys.exit(1)

def run_app():
    """启动Streamlit应用"""
    print("\n正在启动Streamlit应用...")
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    
    try:
        subprocess.check_call([sys.executable, "-m", "streamlit", "run", app_path])
    except subprocess.CalledProcessError as e:
        print(f"应用启动失败: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n应用已关闭")

def run_api():
    """启动API服务"""
    print("\n正在启动API服务...")
    api_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api.py")
    
    try:
        # 安装Flask依赖（如果尚未安装）
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask==2.0.1"])
            print("Flask依赖安装完成！")
        except subprocess.CalledProcessError:
            print("Flask依赖安装失败，但仍将尝试启动API...")
            
        # 启动Flask服务
        print("API服务将在 http://localhost:5000 上运行")
        print("Android应用可以通过修改APP_API_BASE_URL连接到此API")
        print("\n按Ctrl+C停止服务\n")
        
        subprocess.check_call([sys.executable, api_path])
    except subprocess.CalledProcessError as e:
        print(f"API服务启动失败: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAPI服务已关闭")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能教育辅助平台启动脚本")
    parser.add_argument("--skip-deps", action="store_true", help="跳过依赖安装")
    parser.add_argument("--skip-examples", action="store_true", help="跳过示例生成")
    parser.add_argument("--api", action="store_true", help="启动API服务（供Android应用调用）")
    args = parser.parse_args()
    
    # 打印欢迎信息
    print("=" * 60)
    print("             智能教育辅助平台 - AIGC创新赛             ")
    print("=" * 60)
    
    # 安装依赖
    if not args.skip_deps:
        install_dependencies()
    else:
        print("跳过依赖安装...")
    
    # 生成示例
    if not args.skip_examples:
        generate_examples()
    else:
        print("跳过示例生成...")
    
    # 运行应用或API
    if args.api:
        run_api()
    else:
        run_app()

if __name__ == "__main__":
    main() 
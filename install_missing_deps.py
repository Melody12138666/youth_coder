import subprocess
import sys

print("正在安装缺失的依赖...")
dependencies = [
    "SpeechRecognition==3.10.0",
    "pyaudio==0.2.13",
    "pydub==0.25.1",
    "streamlit==1.27.0",
    "streamlit-webrtc==0.47.0",
    "av==10.0.0",
    "numpy==1.26.0",
    "matplotlib==3.8.0",
    "uuid==1.30"
]

for dep in dependencies:
    print(f"安装 {dep}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        print(f"✓ {dep} 安装成功")
    except Exception as e:
        print(f"✗ {dep} 安装失败: {str(e)}")

print("\n完成！现在您可以运行应用了：python run.py --skip-deps") 
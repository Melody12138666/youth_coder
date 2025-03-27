import os
import sys
import tempfile
import time
import json
from pathlib import Path

import av
import streamlit as st
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode
    webrtc_available = True
except ImportError:
    print("警告: streamlit_webrtc 模块未安装，麦克风录音功能将不可用")
    webrtc_available = False

# 添加项目路径到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 导入自定义模块
from speech_to_scratch.speech_recognition import SpeechRecognizer
from speech_to_scratch.text_to_scratch import TextToScratchConverter
from speech_to_scratch.examples import load_example as load_scratch_example
from code_visualization.code_animator import CodeAnimator
from scratch_player import ScratchPlayer  # 导入Scratch播放器模块

# 确保存在assets目录
os.makedirs(os.path.join(os.path.dirname(__file__), 'assets', 'scratch_examples'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'assets', 'visualization_examples'), exist_ok=True)

# 初始化组件
try:
    speech_recognizer = SpeechRecognizer()
    text_to_scratch_converter = TextToScratchConverter(use_gpu=False)
    code_animator = CodeAnimator()
    scratch_player = ScratchPlayer()
except Exception as e:
    st.error(f"组件初始化失败: {str(e)}")
    speech_recognizer = None
    text_to_scratch_converter = None
    code_animator = None
    scratch_player = None

# 设置页面配置
st.set_page_config(
    page_title="智能教育辅助平台",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .feature-card {
        background-color: #f5f5f5;
        border-radius: 5px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .info-text {
        color: #424242;
        font-size: 1rem;
    }
    .success-text {
        color: #4CAF50;
        font-weight: bold;
    }
    .warning-text {
        color: #FFC107;
        font-weight: bold;
    }
    .error-text {
        color: #F44336;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
        padding: 10px 16px;
        background-color: #f0f2f6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border-bottom: 2px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# 侧边栏导航
st.sidebar.title("导航")
app_mode = st.sidebar.selectbox("选择功能", ["主页", "语音转Scratch项目", "代码可视化演示"])

# 创建临时目录用于保存文件
try:
    temp_dir = tempfile.mkdtemp()
    # 测试临时目录权限
    test_file = os.path.join(temp_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("test")
    os.remove(test_file)
except Exception as e:
    st.error(f"临时目录创建失败: {str(e)}")
    # 使用当前目录下的temp文件夹作为备选
    temp_dir = os.path.join(os.path.dirname(__file__), "temp")
    os.makedirs(temp_dir, exist_ok=True)

# 主页
if app_mode == "主页":
    st.markdown('<h1 class="main-header">智能教育辅助平台</h1>', unsafe_allow_html=True)
    st.markdown('<p class="info-text">欢迎使用智能教育辅助平台，这是一个面向编程教育的创新工具</p>', unsafe_allow_html=True)
    
    st.image("https://www.cst.zju.edu.cn/2023/1218/c67018a2868583/pimg/@/b90e7e36-5c53-4e90-a6ec-c7a3cb6f56df.jpg", use_column_width=True)
    
    st.markdown('<h2 class="sub-header">核心功能</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<h3>💬 语音转Scratch项目</h3>', unsafe_allow_html=True)
        st.markdown("""
        * 通过自然语言指令生成Scratch项目
        * 支持语音输入或文本输入
        * 自动创建游戏、动画和交互式故事
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<h3>📊 代码可视化演示</h3>', unsafe_allow_html=True)
        st.markdown("""
        * 将Python代码转化为动画
        * 直观展示代码执行过程
        * 支持算法和数据结构可视化
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<h2 class="sub-header">关于项目</h2>', unsafe_allow_html=True)
    st.markdown("""
    本项目是为**第二届中国高校计算机大赛——AIGC创新赛**开发的应用作品。我们的目标是通过人工智能技术，
    提升编程教育的效果和体验，帮助学生更好地理解编程概念和算法逻辑。
    
    项目采用BlueLM大语言模型实现自然语言处理，结合Scratch可视化编程和Manim动画引擎，
    打造了一个全面的编程教育助手。
    """)

# 语音转Scratch项目
elif app_mode == "语音转Scratch项目":
    st.markdown('<h1 class="main-header">语音转Scratch项目生成</h1>', unsafe_allow_html=True)
    st.markdown('<p class="info-text">通过自然语言描述，自动生成可运行的Scratch项目</p>', unsafe_allow_html=True)
    
    # 初始化Scratch播放器
    scratch_player = ScratchPlayer()
    
    input_method = st.radio("选择输入方式", ["文本输入", "语音输入", "示例项目"])
    
    if input_method == "文本输入":
        user_input = st.text_area("请输入你想创建的Scratch项目描述", height=150, 
                                 placeholder="例如：创建一个小猫移动的游戏，按空格键可以让小猫跳起来，碰到障碍物游戏结束")
        submit_button = st.button("生成项目")
        
        if submit_button and user_input:
            with st.spinner("正在生成Scratch项目..."):
                try:
                    # 初始化转换器
                    converter = TextToScratchConverter(use_gpu=False)
                    
                    # 生成项目
                    project = converter.convert(user_input)
                    
                    # 保存项目
                    output_file = os.path.join(temp_dir, "scratch_project.json")
                    success = converter.save_project(project, output_file)
                    
                    if success:
                        st.success("Scratch项目生成成功!")
                        
                        # 展示项目信息
                        sprite_count = sum(1 for target in project["targets"] if not target.get("isStage", False))
                        st.markdown(f"**项目包含:** {sprite_count} 个角色")
                        
                        # 嵌入Scratch播放器
                        st.subheader("📺 项目预览 - 直接运行")
                        scratch_player.embed_project(project, height=600)
                        
                        st.markdown("""
                        **玩法说明：**
                        - 点击绿旗开始运行项目
                        - 使用键盘和鼠标与项目互动
                        - 项目运行过程中可以随时停止和重新开始
                        """)
                        
                        # 提供下载选项（作为次要选项）
                        with st.expander("下载项目"):
                            st.write("您也可以下载此项目，在Scratch官方编辑器中打开：")
                            with open(output_file, "r") as f:
                                st.download_button(
                                    label="下载Scratch项目文件",
                                    data=f,
                                    file_name="scratch_project.json",
                                    mime="application/json"
                                )
                            st.write("[打开Scratch官方编辑器](https://scratch.mit.edu/projects/editor/)")
                    else:
                        st.error("项目生成失败，请重试")
                except Exception as e:
                    st.error(f"出错了: {str(e)}")
    
    elif input_method == "语音输入":
        st.warning("请确保您的麦克风可用，清晰地描述您想要的Scratch项目")
        
        duration = st.slider("录音时长(秒)", min_value=3, max_value=15, value=5)
        record_button = st.button("开始录音")
        
        if record_button:
            with st.spinner(f"正在录音，请说出您想创建的Scratch项目... ({duration}秒)"):
                try:
                    recognizer = SpeechRecognizer()
                    text = recognizer.recognize_from_microphone(duration=duration)
                    
                    if text and text != "无法识别语音，请重新尝试":
                        st.success("语音识别成功!")
                        st.markdown(f"**识别结果:** {text}")
                        
                        # 转换为Scratch项目
                        with st.spinner("正在生成Scratch项目..."):
                            converter = TextToScratchConverter(use_gpu=False)
                            project = converter.convert(text)
                            
                            # 保存项目
                            output_file = os.path.join(temp_dir, "scratch_project.json")
                            success = converter.save_project(project, output_file)
                            
                            if success:
                                st.success("Scratch项目生成成功!")
                                
                                # 展示项目信息
                                sprite_count = sum(1 for target in project["targets"] if not target.get("isStage", False))
                                st.markdown(f"**项目包含:** {sprite_count} 个角色")
                                
                                # 嵌入Scratch播放器
                                st.subheader("📺 项目预览 - 直接运行")
                                scratch_player.embed_project(project, height=600)
                                
                                st.markdown("""
                                **少儿编程小贴士:**
                                - 点击绿旗 🏁 开始运行项目
                                - 尝试不同的按键和鼠标操作与角色互动
                                - 观察项目是如何根据你的指令构建的
                                """)
                                
                                # 提供下载选项（作为次要选项）
                                with st.expander("下载项目"):
                                    st.write("您也可以下载此项目，在Scratch官方编辑器中打开：")
                                    with open(output_file, "r") as f:
                                        st.download_button(
                                            label="下载Scratch项目文件",
                                            data=f,
                                            file_name="scratch_project.json",
                                            mime="application/json"
                                        )
                            else:
                                st.error("项目生成失败，请重试")
                    else:
                        st.error("语音识别失败，请重新尝试")
                except Exception as e:
                    st.error(f"出错了: {str(e)}")
    
    elif input_method == "示例项目":
        st.info("以下是预先生成的Scratch项目示例，可以直接运行学习")
        
        example_options = [
            "1: 小猫捉老鼠游戏",
            "2: 太空冒险动画",
            "3: 交互式音乐创作"
        ]
        
        selected_example = st.selectbox("选择一个示例项目", example_options)
        example_number = int(selected_example.split(":")[0])
        
        if st.button("加载示例"):
            with st.spinner("加载示例项目..."):
                try:
                    # 加载示例项目
                    project = load_scratch_example(example_number)
                    
                    if project:
                        st.success(f"示例项目 {selected_example} 加载成功!")
                        
                        # 保存项目
                        output_file = os.path.join(temp_dir, f"example_{example_number}.json")
                        with open(output_file, "w") as f:
                            json.dump(project, f)
                        
                        # 展示项目信息
                        sprite_count = sum(1 for target in project["targets"] if not target.get("isStage", False))
                        st.markdown(f"**项目包含:** {sprite_count} 个角色")
                        
                        # 项目描述
                        descriptions = [
                            "一个小猫捉老鼠的游戏。玩家控制小猫移动，碰到老鼠得分，碰到障碍物扣分。",
                            "一个宇航员在太空中冒险的动画。宇航员从地球出发，经过月球，最后到达火星。",
                            "一个可以创作音乐的互动程序。点击不同的按钮会播放不同的音符，可以录制音乐作品并回放。"
                        ]
                        
                        st.markdown(f"**项目描述:** {descriptions[example_number-1]}")
                        
                        # 嵌入Scratch播放器
                        st.subheader("📺 项目预览 - 直接运行")
                        scratch_player.embed_project(project, height=600)
                        
                        # 提供少儿编程引导提示
                        st.markdown(f"""
                        **少儿编程学习指南:**
                        1. 点击绿旗 🏁 运行项目
                        2. 探索这个 {selected_example.split(':')[1].strip()} 是如何工作的
                        3. 尝试不同的交互方式（鼠标点击、键盘按键）
                        4. 思考：你能想到如何改进这个项目吗？
                        """)
                        
                        # 提供下载选项（作为次要选项）
                        with st.expander("下载项目"):
                            with open(output_file, "r") as f:
                                st.download_button(
                                    label="下载Scratch项目文件",
                                    data=f,
                                    file_name=f"example_{example_number}.json",
                                    mime="application/json"
                                )
                    else:
                        st.error("加载示例失败，请重试")
                except Exception as e:
                    st.error(f"出错了: {str(e)}")

# 代码可视化演示
elif app_mode == "代码可视化演示":
    st.markdown('<h1 class="main-header">代码可视化演示</h1>', unsafe_allow_html=True)
    st.markdown('<p class="info-text">将Python代码转化为动画，直观展示执行过程</p>', unsafe_allow_html=True)
    
    visualization_method = st.radio("选择方式", ["输入代码", "选择示例"])
    
    if visualization_method == "输入代码":
        code = st.text_area("请输入Python代码", height=300, 
                           value="""
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# 测试
data = [64, 34, 25, 12, 22, 11, 90]
sorted_data = bubble_sort(data)
print("排序后:", sorted_data)
""")
        
        show_code = st.checkbox("在动画中显示代码", value=True)
        
        if st.button("生成可视化"):
            if code:
                with st.spinner("正在生成可视化动画..."):
                    try:
                        # 初始化动画生成器
                        animator = CodeAnimator(show_code=show_code)
                        
                        # 创建临时文件
                        output_file = os.path.join(temp_dir, "code_animation.mp4")
                        
                        # 生成动画
                        animation_path = animator.create_animation(code, output_file)
                        
                        if animation_path and os.path.exists(animation_path):
                            st.success("可视化动画生成成功!")
                            
                            # 显示视频
                            st.video(animation_path)
                            
                            # 提供下载按钮
                            with open(animation_path, "rb") as f:
                                st.download_button(
                                    label="下载动画",
                                    data=f,
                                    file_name="code_animation.mp4",
                                    mime="video/mp4"
                                )
                        else:
                            st.error("动画生成失败，请重试")
                    except Exception as e:
                        st.error(f"出错了: {str(e)}")
            else:
                st.warning("请输入Python代码")
    
    elif visualization_method == "选择示例":
        st.info("以下是预设的代码可视化示例，可直接查看")
        
        example_options = [
            "冒泡排序算法",
            "二分查找算法",
            "变量计算示例"
        ]
        
        selected_example = st.selectbox("选择一个示例", example_options)
        
        # 根据选择显示代码
        if selected_example == "冒泡排序算法":
            st.code("""
def bubble_sort(arr):
    n = len(arr)
    # 遍历所有数组元素
    for i in range(n):
        # 最后i个元素已经就位
        for j in range(0, n-i-1):
            # 遍历数组从0到n-i-1
            # 如果当前元素大于下一个元素，交换它们
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# 测试数据
data = [64, 34, 25, 12, 22, 11, 90]
sorted_data = bubble_sort(data)
print("排序后:", sorted_data)
""", language="python")
            
            st.markdown("""
            **算法说明**:
            - 冒泡排序是最简单的排序算法之一
            - 它通过重复遍历要排序的列表，比较相邻元素并交换位置
            - 每次遍历结束后，最大的元素会"冒泡"到列表末尾
            """)
            
        elif selected_example == "二分查找算法":
            st.code("""
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        # 检查中间元素
        if arr[mid] == target:
            return mid
        
        # 如果目标大于中间元素，忽略左半部分
        elif arr[mid] < target:
            left = mid + 1
            
        # 如果目标小于中间元素，忽略右半部分
        else:
            right = mid - 1
            
    # 如果找不到目标元素
    return -1

# 测试
sorted_array = [2, 3, 4, 10, 40, 50, 70]
target = 10
result = binary_search(sorted_array, target)
print(f"元素在索引: {result}" if result != -1 else "元素不在数组中")
""", language="python")
            
            st.markdown("""
            **算法说明**:
            - 二分查找是一种高效的搜索算法
            - 它要求数组已排序
            - 通过将目标值与数组中间元素比较，根据结果缩小搜索范围
            - 时间复杂度为O(log n)，远优于线性搜索的O(n)
            """)
            
        elif selected_example == "变量计算示例":
            st.code("""
# 初始化变量
a = 5
b = 10

# 基本计算
sum_result = a + b
product = a * b
difference = b - a

# 更新变量
a = a + 1
b = b * 2

# 最终结果
final_result = a + b
print(f"最终结果: {final_result}")
""", language="python")
            
            st.markdown("""
            **代码说明**:
            - 这个示例展示了简单的变量定义和运算
            - 包括加法、乘法、减法
            - 演示变量的值如何随着代码执行而变化
            """)
        
        # 显示动画按钮（实际部署时会连接到预生成的动画）
        if st.button("显示动画"):
            with st.spinner("加载动画..."):
                # 模拟加载延迟
                time.sleep(2)
                
                # 这里应该从预先生成的位置加载视频
                # 在实际部署时，这些视频应该已经生成好
                st.info("动画加载完成！实际部署时，这里会显示预生成的代码执行动画。")
                
                # 显示静态图片作为示例
                if selected_example == "冒泡排序算法":
                    st.image("https://miro.medium.com/v2/resize:fit:1400/1*hmvNvv5qzIjRbYh3Z1ErAg.gif", use_column_width=True)
                elif selected_example == "二分查找算法":
                    st.image("https://www.tutorialspoint.com/data_structures_algorithms/images/binary_search_working.jpg", use_column_width=True)
                else:
                    st.image("https://miro.medium.com/v2/resize:fit:1400/1*TtzpJuehLLW6fNjK6KuHiA.gif", use_column_width=True)
                
                st.markdown("""
                **注意**: 在完整实现中，这里将显示通过Manim生成的代码执行动画视频，
                能够直观展示代码的逐步执行过程、变量的变化和算法的工作原理。
                """)

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>© 2024 智能教育辅助平台 - 基于BlueLM大语言模型</p>
    <p>中国高校计算机大赛——AIGC创新赛 参赛作品</p>
</div>
""", unsafe_allow_html=True) 
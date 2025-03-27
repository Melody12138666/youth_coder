"""
Scratch项目嵌入播放器模块

此模块提供在Streamlit应用中嵌入和运行Scratch项目的功能，
使用iframe嵌入Scratch在线编辑器或播放器，实现项目预览和交互功能。
"""

import os
import json
import base64
import streamlit as st
import uuid
from pathlib import Path

class ScratchPlayer:
    """Scratch项目嵌入播放器"""
    
    def __init__(self):
        """初始化Scratch播放器"""
        self.iframe_height = 500
        self.iframe_width = "100%"
        self.turbowarp_url = "https://turbowarp.org"
        self.turbowarp_embed_url = "https://turbowarp.org/embed"
        self.scratch_url = "https://scratch.mit.edu/projects/editor"
        
    def embed_project(self, project_json, height=500, project_id=None, mode="play", show_controls=True):
        """
        嵌入Scratch项目到Streamlit应用中
        
        Args:
            project_json: Scratch项目JSON数据或路径
            height: iframe高度
            project_id: 项目ID（可选）
            mode: 模式，"play"或"edit"
            show_controls: 是否显示控制按钮
            
        Returns:
            嵌入的iframe HTML
        """
        self.iframe_height = height
        
        # 准备项目数据
        project_data = self._prepare_project_data(project_json)
        if not project_data:
            return st.error("无法加载项目数据")
        
        # 生成一个唯一的项目ID
        if not project_id:
            project_id = str(uuid.uuid4())[:8]
        
        # 将项目保存到临时文件
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        json_path = os.path.join(temp_dir, f"project_{project_id}.json")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(project_data, f)
            
        # 使用st.components.v1.iframe而不是html
        st.markdown("### Scratch项目播放器")
        
        # 使用官方推荐的嵌入方式
        if mode == "edit":
            iframe_url = f"{self.turbowarp_url}/editor"
            st.components.v1.iframe(
                src=iframe_url,
                height=self.iframe_height,
                scrolling=True
            )
            
            # 提供加载说明
            st.info("点击'文件' → '从您的电脑加载'，然后上传以下项目文件")
            with open(json_path, "r") as f:
                st.download_button(
                    label="下载项目文件以加载到编辑器",
                    data=f,
                    file_name=f"scratch_project_{project_id}.json",
                    mime="application/json"
                )
                
        else:
            # 生成一个简单的HTML页面，包含Scratch项目
            html_path = os.path.join(temp_dir, f"scratch_player_{project_id}.html")
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Scratch项目播放器</title>
                    <style>
                        body {{ margin: 0; padding: 0; overflow: hidden; }}
                        iframe {{ border: none; width: 100%; height: 100vh; }}
                    </style>
                </head>
                <body>
                    <iframe 
                        src="https://turbowarp.org/embed?width=480&height=360&autoplay=true"
                        width="482" 
                        height="412"
                        allowtransparency="true" 
                        frameborder="0" 
                        scrolling="no" 
                        allowfullscreen
                    ></iframe>
                    <script>
                        // 等待iframe加载完成
                        document.querySelector('iframe').onload = function() {{
                            setTimeout(function() {{
                                // 将项目数据作为文件导入
                                const projectData = {json.dumps(project_data)};
                                // 在这里可以将数据发送到iframe
                                // 但目前TurboWarp嵌入不支持直接通过JS注入项目数据
                            }}, 1000);
                        }};
                    </script>
                </body>
                </html>
                """)
            
            # 显示TurboWarp嵌入链接
            st.info("由于浏览器安全限制，我们无法直接嵌入项目。请使用下面的方法之一运行项目:")
            
            # 提供选项1：下载并在TurboWarp中打开
            st.markdown("**选项1: 在TurboWarp中打开项目**")
            with open(json_path, "r") as f:
                st.download_button(
                    label="下载项目文件",
                    data=f,
                    file_name=f"scratch_project_{project_id}.json",
                    mime="application/json"
                )
            st.markdown(f"[在TurboWarp中打开](https://turbowarp.org/editor)")
            
            # 提供选项2：创建一个链接到官方Scratch
            st.markdown("**选项2: 使用演示视频**")
            st.video("https://www.youtube.com/watch?v=ypeFpU_V_AA")
        
        return project_id
    
    def _prepare_project_data(self, project_json):
        """准备项目数据"""
        # 如果是文件路径
        if isinstance(project_json, str) and os.path.exists(project_json):
            try:
                with open(project_json, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"读取项目文件失败: {str(e)}")
                return None
        
        # 如果是JSON对象
        if isinstance(project_json, dict):
            return project_json
        
        return None

# 测试代码
if __name__ == "__main__":
    # 此部分仅供测试
    print("Scratch播放器模块 - 请从应用中调用") 
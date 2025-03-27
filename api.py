from flask import Flask, request, jsonify
import os
import json
import base64
import tempfile
from speech_to_scratch.speech_recognition import SpeechRecognizer
from speech_to_scratch.text_to_scratch import TextToScratchConverter
from speech_to_scratch.examples import load_example
from code_visualization.code_animator import CodeAnimator

app = Flask(__name__)

# 初始化组件
speech_recognizer = SpeechRecognizer()
text_to_scratch_converter = TextToScratchConverter(use_gpu=False)
code_animator = CodeAnimator()

@app.route('/api/recognize_speech', methods=['POST'])
def recognize_speech():
    """从音频数据识别语音"""
    try:
        # 获取上传的音频文件
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
            
        audio_file = request.files['audio']
        
        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        audio_file.save(temp_file.name)
        
        # 识别语音
        recognized_text = speech_recognizer.recognize_from_file(temp_file.name)
        
        # 删除临时文件
        os.unlink(temp_file.name)
        
        return jsonify({'text': recognized_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_scratch', methods=['POST'])
def generate_scratch():
    """生成Scratch项目"""
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
            
        text = data['text']
        
        # 生成项目
        project = text_to_scratch_converter.convert(text)
        
        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        success = text_to_scratch_converter.save_project(project, temp_file.name)
        
        if not success:
            return jsonify({'error': 'Failed to save project'}), 500
            
        # 读取文件内容并编码
        with open(temp_file.name, 'r', encoding='utf-8') as f:
            project_json = json.load(f)
            
        # 删除临时文件
        os.unlink(temp_file.name)
        
        # 提取项目元数据
        sprite_count = sum(1 for target in project_json["targets"] if not target.get("isStage", False))
        
        return jsonify({
            'project': project_json,
            'metadata': {
                'sprite_count': sprite_count
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/load_example', methods=['GET'])
def get_example():
    """加载示例项目"""
    try:
        example_number = request.args.get('number', '1')
        project = load_example(int(example_number))
        
        if not project:
            return jsonify({'error': 'Example not found'}), 404
            
        # 提取项目元数据
        sprite_count = sum(1 for target in project["targets"] if not target.get("isStage", False))
        
        return jsonify({
            'project': project,
            'metadata': {
                'sprite_count': sprite_count
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_visualization', methods=['POST'])
def generate_visualization():
    """生成代码可视化"""
    try:
        data = request.json
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400
            
        code = data['code']
        show_code = data.get('show_code', True)
        
        # 创建临时输出文件
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        # 生成动画
        animation_path = code_animator.create_animation(
            code, 
            output_path=temp_output.name
        )
        
        if not animation_path:
            return jsonify({'error': 'Failed to generate animation'}), 500
            
        # 读取视频文件并进行Base64编码
        with open(animation_path, 'rb') as f:
            video_data = f.read()
            video_base64 = base64.b64encode(video_data).decode('utf-8')
            
        # 删除临时文件
        os.unlink(animation_path)
        
        return jsonify({
            'video': video_base64,
            'analysis': code_animator.analyze_code(code)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
import speech_recognition as sr
import os
import tempfile
from pydub import AudioSegment
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpeechRecognizer:
    """语音识别模块，用于将语音转换为文本"""
    
    def __init__(self):
        """初始化语音识别器"""
        try:
            self.recognizer = sr.Recognizer()
            # 调整识别参数
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.is_available = True
        except Exception as e:
            logger.error(f"初始化语音识别器失败: {str(e)}")
            self.is_available = False
        
    def recognize_from_microphone(self, duration=5):
        """
        从麦克风录制语音并识别
        
        Args:
            duration (int): 录音时长，单位为秒
            
        Returns:
            str: 识别出的文本
        """
        if not self.is_available:
            logger.warning("语音识别器不可用，返回模拟结果")
            return "这是一个模拟的语音识别结果。由于语音识别组件未能正确初始化，系统将使用此默认文本。"
            
        logger.info("准备从麦克风录制语音...")
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                logger.info(f"开始录音，持续{duration}秒...")
                audio = self.recognizer.record(source, duration=duration)
                
            return self._process_audio(audio)
        except Exception as e:
            logger.error(f"麦克风录音失败: {str(e)}")
            return "无法从麦克风录音，请检查您的麦克风设置"
    
    def recognize_from_file(self, file_path):
        """
        从音频文件识别语音
        
        Args:
            file_path (str): 音频文件路径
            
        Returns:
            str: 识别出的文本
        """
        if not self.is_available:
            logger.warning("语音识别器不可用，返回模拟结果")
            return "这是一个从音频文件识别的模拟结果。由于语音识别组件未能正确初始化，系统将使用此默认文本。"
            
        logger.info(f"从文件读取音频: {file_path}")
        
        try:
            # 处理不同的音频格式
            if file_path.endswith(('.mp3', '.wav', '.flac', '.aac', '.ogg')):
                if not file_path.endswith('.wav'):
                    # 转换为WAV格式
                    temp_wav = self._convert_to_wav(file_path)
                    file_path = temp_wav
                    
                with sr.AudioFile(file_path) as source:
                    audio = self.recognizer.record(source)
                    
                # 如果创建了临时文件，则删除
                if 'temp_wav' in locals():
                    os.remove(temp_wav)
                    
                return self._process_audio(audio)
            else:
                logger.error(f"不支持的音频格式: {file_path}")
                return "错误：不支持的音频格式"
        except Exception as e:
            logger.error(f"从文件识别语音失败: {str(e)}")
            return f"从文件识别语音失败: {str(e)}"
    
    def _convert_to_wav(self, audio_path):
        """
        将音频文件转换为WAV格式
        
        Args:
            audio_path (str): 原音频文件路径
            
        Returns:
            str: WAV文件路径
        """
        logger.info(f"转换音频格式: {audio_path} -> WAV")
        
        try:
            # 创建临时WAV文件
            temp_wav = tempfile.mktemp(suffix='.wav')
            
            # 根据文件扩展名加载音频
            if audio_path.endswith('.mp3'):
                audio = AudioSegment.from_mp3(audio_path)
            elif audio_path.endswith('.flac'):
                audio = AudioSegment.from_file(audio_path, "flac")
            elif audio_path.endswith('.aac'):
                audio = AudioSegment.from_file(audio_path, "aac")
            elif audio_path.endswith('.ogg'):
                audio = AudioSegment.from_ogg(audio_path)
            else:
                audio = AudioSegment.from_file(audio_path)
                
            # 导出为WAV
            audio.export(temp_wav, format="wav")
            return temp_wav
        except Exception as e:
            logger.error(f"转换音频格式失败: {str(e)}")
            raise
    
    def _process_audio(self, audio):
        """
        处理音频数据，进行语音识别
        
        Args:
            audio: 音频数据对象
            
        Returns:
            str: 识别出的文本
        """
        try:
            # 首先尝试使用Google语音识别（需要联网）
            text = self.recognizer.recognize_google(audio, language='zh-CN')
            logger.info(f"识别成功: {text}")
            return text
        except sr.UnknownValueError:
            logger.warning("Google语音识别无法理解音频")
            try:
                # 尝试使用Sphinx离线识别（英文）
                text = self.recognizer.recognize_sphinx(audio)
                logger.info(f"Sphinx识别成功: {text}")
                return text
            except Exception as sphinx_error:
                logger.error(f"Sphinx识别失败: {str(sphinx_error)}")
                return "无法识别语音，请重新尝试"
        except sr.RequestError as e:
            logger.error(f"无法连接到Google语音识别服务: {e}")
            return "网络错误，请检查您的网络连接"
        except Exception as e:
            logger.error(f"语音识别出错: {str(e)}")
            return f"识别出错: {str(e)}"

# 测试代码
if __name__ == "__main__":
    recognizer = SpeechRecognizer()
    text = recognizer.recognize_from_microphone(duration=5)
    print(f"识别结果: {text}") 
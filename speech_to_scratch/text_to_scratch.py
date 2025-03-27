import json
import os
import logging
import requests
from pathlib import Path
import sys

# 修复导入路径问题
model_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'BlueLM-main'))
if os.path.exists(model_path):
    sys.path.append(model_path)
else:
    logging.warning(f"BlueLM模型路径不存在: {model_path}，将使用模拟模式")

# 尝试导入模型
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    transformers_available = True
except ImportError:
    logging.error("无法导入transformers库，请确保已安装依赖")
    transformers_available = False

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextToScratchConverter:
    """将自然语言文本转换为Scratch项目的转换器"""
    
    def __init__(self, model_path="vivo-ai/BlueLM-7B-Chat", use_gpu=True):
        """
        初始化转换器
        
        Args:
            model_path (str): 语言模型路径
            use_gpu (bool): 是否使用GPU
        """
        self.model_path = model_path
        self.use_gpu = use_gpu
        self.device = "cuda:0" if use_gpu else "cpu"
        self.using_simulation = False
        
        # 加载模型
        if transformers_available:
            logger.info(f"加载语言模型: {model_path}")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True, use_fast=False)
                self.model = AutoModelForCausalLM.from_pretrained(model_path, device_map=self.device, trust_remote_code=True)
                self.model = self.model.eval()
                logger.info("模型加载成功")
            except Exception as e:
                logger.error(f"模型加载失败: {str(e)}")
                logger.warning("使用替代方法: 将使用预定义模板生成Scratch项目")
                self.tokenizer = None
                self.model = None
                self.using_simulation = True
        else:
            logger.warning("Transformers库不可用，使用预定义模板")
            self.tokenizer = None
            self.model = None
            self.using_simulation = True
    
    def convert(self, text):
        """
        将自然语言文本转换为Scratch项目
        
        Args:
            text (str): 自然语言描述
            
        Returns:
            dict: Scratch项目JSON数据
        """
        logger.info(f"开始处理文本: {text}")
        
        # 使用LLM生成Scratch项目描述
        project_description = self._generate_project_description(text)
        
        # 根据描述生成Scratch项目
        scratch_project = self._create_scratch_project(project_description)
        
        return scratch_project
    
    def _generate_project_description(self, text):
        """
        使用LLM生成项目描述
        
        Args:
            text (str): 用户输入的文本
            
        Returns:
            dict: 项目描述，包含角色、事件、脚本等
        """
        if self.model and self.tokenizer and not self.using_simulation:
            # 构建提示
            prompt = f"""[|Human|]:我想创建一个Scratch项目，内容是：{text}。
请生成一个详细的项目描述，包括角色、背景、事件和脚本。以JSON格式输出，包含以下字段：
1. projectName: 项目名称
2. sprites: 角色列表，每个角色包含name（名称）和scripts（脚本列表）
3. backgrounds: 背景列表
4. events: 事件列表

请确保生成的JSON格式正确，可以直接解析。[|AI|]:"""
            
            # 生成回复
            logger.info("正在生成项目描述...")
            try:
                inputs = self.tokenizer(prompt, return_tensors="pt")
                inputs = inputs.to(self.device)
                
                outputs = self.model.generate(
                    **inputs, 
                    max_new_tokens=1024,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                )
                
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # 提取AI回复部分
                json_str = response.split("[|AI|]:")[-1].strip()
                # 查找JSON部分
                start_index = json_str.find('{')
                end_index = json_str.rfind('}') + 1
                
                if start_index != -1 and end_index != -1:
                    json_str = json_str[start_index:end_index]
                
                project_description = json.loads(json_str)
                logger.info("成功生成项目描述")
                return project_description
            except Exception as e:
                logger.error(f"解析生成的项目描述失败: {str(e)}")
                logger.error(f"原始输出: {locals().get('response', '未生成')}")
                # 使用默认模板
                return self._get_default_project_template(text)
        else:
            # 如果模型未加载或使用模拟模式，使用默认模板
            return self._get_default_project_template(text)
    
    def _get_default_project_template(self, text):
        """
        获取默认项目模板
        
        Args:
            text (str): 用户输入的文本
            
        Returns:
            dict: 默认项目描述
        """
        # 简单解析文本，提取关键信息
        keywords = text.lower()
        
        # 根据关键词选择不同的模板
        if "游戏" in keywords or "game" in keywords:
            return {
                "projectName": "简单游戏",
                "sprites": [
                    {
                        "name": "主角",
                        "scripts": [
                            "当绿旗被点击时，移到x:0 y:0",
                            "当按下[空格键]，改变y坐标(10)",
                            "当按下[左箭头]，将x坐标减少(10)",
                            "当按下[右箭头]，将x坐标增加(10)"
                        ]
                    },
                    {
                        "name": "障碍物",
                        "scripts": [
                            "当绿旗被点击时，移到x:200 y:0",
                            "当绿旗被点击时，重复执行[将x坐标减少(5)，如果碰到边缘就反弹]",
                            "当碰到[主角]，广播[游戏结束]"
                        ]
                    }
                ],
                "backgrounds": ["蓝天"],
                "events": ["当绿旗被点击", "当按下按键", "当碰到边缘"]
            }
        elif "动画" in keywords or "animation" in keywords:
            return {
                "projectName": "简单动画",
                "sprites": [
                    {
                        "name": "角色1",
                        "scripts": [
                            "当绿旗被点击时，移到x:0 y:0",
                            "当绿旗被点击时，重复执行[移动(10)步，如果碰到边缘就反弹]",
                            "当绿旗被点击时，重复执行[下一个造型，等待(0.5)秒]"
                        ]
                    }
                ],
                "backgrounds": ["城市"],
                "events": ["当绿旗被点击", "当碰到边缘"]
            }
        elif "故事" in keywords or "story" in keywords:
            return {
                "projectName": "故事讲述",
                "sprites": [
                    {
                        "name": "讲述者",
                        "scripts": [
                            "当绿旗被点击时，说[从前有一个...]",
                            "当绿旗被点击时，等待(3)秒后，说[他遇到了...]",
                            "当绿旗被点击时，等待(6)秒后，说[最后...]"
                        ]
                    }
                ],
                "backgrounds": ["森林", "城堡"],
                "events": ["当绿旗被点击", "当背景切换到"]
            }
        else:
            # 通用项目模板
            return {
                "projectName": "我的项目",
                "sprites": [
                    {
                        "name": "精灵1",
                        "scripts": [
                            "当绿旗被点击时，移到x:0 y:0",
                            "当绿旗被点击时，说[Hello!]",
                            "当被点击时，播放声音[喵]直到播放完毕"
                        ]
                    }
                ],
                "backgrounds": ["白色背景"],
                "events": ["当绿旗被点击", "当被点击"]
            }
    
    def _create_scratch_project(self, project_description):
        """
        根据描述创建Scratch项目
        
        Args:
            project_description (dict): 项目描述
            
        Returns:
            dict: Scratch项目JSON
        """
        logger.info("开始创建Scratch项目")
        
        # Scratch项目模板
        scratch_project = {
            "targets": [],
            "monitors": [],
            "extensions": [],
            "meta": {
                "semver": "3.0.0",
                "vm": "0.2.0",
                "agent": "Python Scratch Converter"
            }
        }
        
        # 添加舞台和精灵
        stage = self._create_stage(project_description.get("backgrounds", []))
        scratch_project["targets"].append(stage)
        
        # 添加角色
        for sprite_desc in project_description.get("sprites", []):
            sprite = self._create_sprite(sprite_desc)
            scratch_project["targets"].append(sprite)
        
        logger.info(f"Scratch项目创建完成: {project_description.get('projectName', '未命名项目')}")
        return scratch_project
    
    def _create_stage(self, backgrounds):
        """创建舞台对象"""
        # 这里简化处理，实际应用中需要更复杂的转换逻辑
        stage = {
            "isStage": True,
            "name": "Stage",
            "variables": {},
            "lists": {},
            "broadcasts": {},
            "blocks": {},
            "comments": {},
            "currentCostume": 0,
            "costumes": [
                {
                    "assetId": "cd21514d0531fdffb22204e0ec5ed84a",
                    "name": "背景1",
                    "md5ext": "cd21514d0531fdffb22204e0ec5ed84a.svg",
                    "dataFormat": "svg",
                    "rotationCenterX": 240,
                    "rotationCenterY": 180
                }
            ],
            "sounds": [],
            "volume": 100,
            "layerOrder": 0,
            "tempo": 60,
            "videoTransparency": 50,
            "videoState": "on",
            "textToSpeechLanguage": None
        }
        return stage
    
    def _create_sprite(self, sprite_desc):
        """创建精灵对象"""
        # 这里简化处理，实际应用中需要更复杂的转换逻辑
        sprite = {
            "isStage": False,
            "name": sprite_desc.get("name", "Sprite"),
            "variables": {},
            "lists": {},
            "broadcasts": {},
            "blocks": self._create_blocks(sprite_desc.get("scripts", [])),
            "comments": {},
            "currentCostume": 0,
            "costumes": [
                {
                    "assetId": "bcf454acf82e4504149f7ffe07081dbc",
                    "name": "造型1",
                    "bitmapResolution": 1,
                    "md5ext": "bcf454acf82e4504149f7ffe07081dbc.svg",
                    "dataFormat": "svg",
                    "rotationCenterX": 48,
                    "rotationCenterY": 50
                }
            ],
            "sounds": [],
            "volume": 100,
            "visible": True,
            "x": 0,
            "y": 0,
            "size": 100,
            "direction": 90,
            "draggable": False,
            "rotationStyle": "all around"
        }
        return sprite
    
    def _create_blocks(self, scripts):
        """根据脚本创建代码块"""
        # 这里简化处理，实际使用时需更复杂的解析和转换逻辑
        blocks = {}
        
        # 生成唯一ID的简单方法
        block_id = lambda i: f"block_{i}"
        
        for i, script in enumerate(scripts):
            # 这里仅作示例，实际需要更复杂的解析
            blocks[block_id(i)] = {
                "opcode": "event_whenflagclicked" if "绿旗" in script else "event_whenkeypressed",
                "next": None,
                "parent": None,
                "inputs": {},
                "fields": {},
                "shadow": False,
                "topLevel": True,
                "x": 0,
                "y": i * 100
            }
        
        return blocks
    
    def save_project(self, project, file_path):
        """
        保存Scratch项目到文件
        
        Args:
            project (dict): Scratch项目数据
            file_path (str): 保存路径
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project, f, ensure_ascii=False, indent=2)
            logger.info(f"项目已保存到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存项目失败: {str(e)}")
            return False

# 测试代码
if __name__ == "__main__":
    converter = TextToScratchConverter(use_gpu=False)  # 测试时可以使用CPU
    project = converter.convert("创建一个小猫跳跃的游戏")
    converter.save_project(project, "cat_game.json") 
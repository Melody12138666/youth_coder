import os
import json
from pathlib import Path
import sys

# 修复相对导入问题
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from speech_to_scratch.text_to_scratch import TextToScratchConverter
except ImportError:
    from text_to_scratch import TextToScratchConverter

# 配置示例项目保存目录
EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets/scratch_examples")
os.makedirs(EXAMPLES_DIR, exist_ok=True)

def generate_scratch_examples():
    """生成Scratch项目示例"""
    print("开始生成Scratch项目示例...")
    
    # 初始化转换器
    try:
        converter = TextToScratchConverter(use_gpu=False)
    except Exception as e:
        print(f"初始化转换器失败: {str(e)}")
        return EXAMPLES_DIR
    
    # 示例描述列表
    examples = [
        {
            "name": "小猫捉老鼠游戏",
            "description": "创建一个小猫捉老鼠的游戏。玩家控制小猫移动，碰到老鼠得分，碰到障碍物扣分。游戏有倒计时功能，时间到或分数达到目标则游戏结束。"
        },
        {
            "name": "太空冒险动画",
            "description": "制作一个宇航员在太空中冒险的动画。宇航员从地球出发，经过月球，最后到达火星。每到一个星球，宇航员都会说不同的台词。背景会随着故事发展而变化。"
        },
        {
            "name": "交互式音乐创作",
            "description": "设计一个可以创作音乐的互动程序。点击不同的按钮会播放不同的音符，可以录制自己的音乐作品并回放。不同的角色代表不同的乐器，如钢琴、鼓和吉他。"
        }
    ]
    
    # 为每个示例生成Scratch项目
    for i, example in enumerate(examples):
        print(f"\n生成示例 {i+1}/{len(examples)}: {example['name']}")
        try:
            project = converter.convert(example["description"])
            
            # 保存项目文件
            file_name = f"{i+1}_{example['name'].replace(' ', '_')}.json"
            file_path = os.path.join(EXAMPLES_DIR, file_name)
            
            success = converter.save_project(project, file_path)
            if success:
                print(f"✓ 示例 '{example['name']}' 已生成并保存到 {file_path}")
            else:
                print(f"✗ 示例 '{example['name']}' 生成失败")
        except Exception as e:
            print(f"生成示例 '{example['name']}' 时出错: {str(e)}")
            
    print("\n所有示例生成完成！")
    return EXAMPLES_DIR

def load_example(example_number):
    """
    加载指定编号的示例项目
    
    Args:
        example_number (int): 示例编号（1, 2, 3...）
        
    Returns:
        dict: 加载的Scratch项目
    """
    # 确保目录存在
    if not os.path.exists(EXAMPLES_DIR):
        os.makedirs(EXAMPLES_DIR, exist_ok=True)
        print(f"警告: 示例目录不存在，已创建 {EXAMPLES_DIR}")
        
    # 获取所有示例文件
    example_files = [f for f in os.listdir(EXAMPLES_DIR) if f.startswith(f"{example_number}_") and f.endswith('.json')]
    
    if not example_files:
        print(f"找不到编号为 {example_number} 的示例，将创建一个默认示例")
        # 创建默认示例
        try:
            converter = TextToScratchConverter(use_gpu=False)
            descriptions = [
                "创建一个小猫捉老鼠的游戏。",
                "制作一个宇航员在太空中冒险的动画。",
                "设计一个可以创作音乐的互动程序。"
            ]
            if 1 <= example_number <= 3:
                project = converter.convert(descriptions[example_number-1])
                # 保存项目
                file_name = f"{example_number}_default_example.json"
                file_path = os.path.join(EXAMPLES_DIR, file_name)
                converter.save_project(project, file_path)
                return project
            else:
                return None
        except Exception as e:
            print(f"创建默认示例失败: {str(e)}")
            return None
        
    # 加载第一个匹配的文件
    example_path = os.path.join(EXAMPLES_DIR, example_files[0])
    try:
        with open(example_path, 'r', encoding='utf-8') as f:
            project = json.load(f)
        print(f"已加载示例: {example_files[0]}")
        return project
    except Exception as e:
        print(f"加载示例失败: {str(e)}")
        return None

def print_example_info():
    """打印所有可用示例的信息"""
    print("\n可用的Scratch项目示例:")
    
    if not os.path.exists(EXAMPLES_DIR):
        print("示例目录不存在，请先生成示例")
        return
        
    example_files = sorted([f for f in os.listdir(EXAMPLES_DIR) if f.endswith('.json')])
    
    if not example_files:
        print("没有找到示例文件，请先生成示例")
        return
        
    for file in example_files:
        try:
            with open(os.path.join(EXAMPLES_DIR, file), 'r', encoding='utf-8') as f:
                project = json.load(f)
                
            # 提取项目信息
            project_name = file.split('_', 1)[1].replace('_', ' ').replace('.json', '')
            sprite_count = sum(1 for target in project["targets"] if not target.get("isStage", False))
            
            print(f"- {file.split('_')[0]}: {project_name}")
            print(f"  角色数量: {sprite_count}")
            print(f"  文件: {file}")
            print()
        except Exception as e:
            print(f"读取 {file} 失败: {str(e)}")

if __name__ == "__main__":
    # 生成示例项目
    examples_dir = generate_scratch_examples()
    
    # 打印示例信息
    print_example_info()
    
    # 测试加载示例
    project = load_example(1)
    if project:
        print(f"项目目标数量: {len(project.get('targets', []))}") 
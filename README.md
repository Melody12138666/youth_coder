# 智能教育辅助平台 - AIGC创新赛项目

## 项目概述

本项目是为第二届"中国高校计算机大赛——AIGC创新赛"应用赛道开发的智能教育辅助平台。该平台旨在通过人工智能技术，帮助学生和教育者更好地进行编程学习和教学。

## 核心功能

### 1. 语音转Scratch项目生成

通过自然语言指令（语音或文本输入），自动生成对应的Scratch项目。用户只需描述他们想要创建的项目，系统就能自动生成可运行的Scratch代码。

- 支持多种类型的Scratch项目生成，如游戏、动画、交互式故事等
- 自动处理角色、背景、动作和交互逻辑
- 生成的项目可以直接在Scratch平台运行

### 2. 代码可视化演示

将Python代码转化为直观的动画演示，帮助学习者理解代码执行的过程和结果。

- 支持基本数据结构和算法的可视化（如数组操作、排序算法等）
- 代码执行流程的动态展示
- 变量状态和内存变化的实时显示

## 技术架构

- 前端：Streamlit Web界面
- 后端：Python服务，集成BlueLM大语言模型
- 语音处理：SpeechRecognition库
- 可视化：Manim库
- Scratch项目生成：自定义转换引擎

## 安装与运行

### 环境要求
- Python 3.8+
- 依赖库安装：`pip install -r requirements.txt`

### 启动应用
```bash
cd AIGC_Project
streamlit run app.py
```

## 项目结构

```
AIGC_Project/
├── speech_to_scratch/   # 语音转Scratch功能模块
├── code_visualization/  # 代码可视化功能模块
├── assets/              # 静态资源文件
├── utils/               # 工具函数
├── app.py               # 主应用入口
└── requirements.txt     # 项目依赖
```

## 开发团队

[团队成员信息]

## 许可证

本项目使用 MIT 许可证 
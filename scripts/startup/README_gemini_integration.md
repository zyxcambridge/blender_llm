# Blender AI助手 - Google Gemini API集成

## 概述

此功能允许Blender AI助手使用Google Gemini API将用户的自然语言描述转换为可执行的Blender Python代码，从而实现更精确的3D模型生成。

## 依赖项

此功能依赖于`requests`库与Google Gemini API进行通信。如果您的Blender Python环境中尚未安装此库，请按照以下步骤安装：

```bash
# 找到您的Blender Python可执行文件路径
# 通常位于Blender安装目录下的python/bin文件夹中

# 使用Blender的Python安装requests库
/path/to/blender/python/bin/python -m pip install requests
```

## 配置API密钥

要使用Google Gemini API，您需要一个有效的API密钥。API密钥已在`ai_assistant_config.py`文件中配置：

```python
# Google API Key for AI services
GOOGLE_API_KEY = "您的API密钥"
```

## 使用方法

1. 启动Blender
2. 打开AI助手面板（位于属性面板中的场景选项卡下）
3. 确保选择了"Agent"模式
4. 在文本框中输入您想要创建的3D模型的自然语言描述
5. 点击"发送"按钮
6. 系统将使用Google Gemini API生成Blender Python代码并执行，创建您描述的3D模型

## 示例输入

```
设计一个鼻炎吸鼻器：三部分组成，一个盒子是洗鼻器的主体，包含电机等，可拆卸的部分1，能加入0.9%的生理盐水胶囊，像装子弹一样装上，可拆卸的部分2，带走废液，倒掉；像卸载子弹一样卸载；
```

## 故障排除

如果遇到问题：

1. 确保您的API密钥有效且已正确配置
2. 检查网络连接是否正常
3. 查看Blender控制台输出的错误信息
4. 如果API调用失败，系统将自动回退到基于关键词的匹配方法

## 开发说明

- `ai_gemini_integration.py` - 包含与Google Gemini API通信的核心功能
- `space_ai_sidebar.py` - 包含AI助手UI和操作符的实现
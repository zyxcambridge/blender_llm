import os
from openai import OpenAI

token = os.environ.get("GITHUB_TOKEN", "")
endpoint = os.environ.get("OPENAI_API_BASE", "https://models.github.ai/inference")
model = os.environ.get("OPENAI_MODEL", "openai/gpt-4.1")

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

def generate_blender_code(prompt_text):
    if not token:
        return False, "未配置 GITHUB_TOKEN 环境变量，无法访问 OpenAI API。"
    system_prompt = (
        "将以下自然语言描述转换为可在Blender中执行的Python代码。"
        "代码必须使用Blender Python API (bpy)创建可见的3D模型对象。"
        "添加日志输出以跟踪执行过程。\n"
        "生成的代码必须满足如下要求：\n"
        "1. 必须创建至少一个可见的3D对象。\n"
        "2. 必须为创建的对象设置合理的尺寸、位置和材质。\n"
        "3. 力学原理检测：结构合理，重心、支撑无问题。\n"
        "4. 物理原理检测：考虑物理特性。\n"
        "5. 外观检测：美观、协调。\n"
        "6. 结构检测：连接正确，功能部件位置恰当。\n"
        "- 当前环境是Blender 4.5, 只允许4.5 API。\n"
        "- 参考API文档: https://docs.blender.org/api/current/\n"
        "- 不要使用 if __name__ == '__main__' 结构，主函数用 bpy.app.timers.register(main)。\n"
        "- bpy.ops 操作需正确上下文。\n"
        "- 合并对象前正确选择。\n"
        "- 只返回Python代码，不要包含解释或注释，代码可直接运行。"
    )
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.3,
            top_p=1.0,
            max_tokens=2048,
            model=model
        )
        code = response.choices[0].message.content
        # 去除 markdown 格式
        if "```python" in code:
            code = code.split("```python")[1].split("```", 1)[0].strip()
        elif "```" in code:
            code = code.split("```", 1)[1].split("```", 1)[0].strip()
        return True, code
    except Exception as e:
        return False, f"OpenAI API 调用失败: {e}"

def evaluate_and_fix_code(code, error_message):
    if not token:
        return False, "未配置 GITHUB_TOKEN 环境变量，无法访问 OpenAI API。"
    system_prompt = (
        "你是一个Blender Python代码修复专家。请根据用户提供的错误信息和当前代码，给出如下格式的评估和修复建议：\n"
        "1. 总体评估: [通过/不通过]\n"
        "2. 问题列表: [如果有问题，列出每个问题]\n"
        "3. 修复建议: [针对每个问题提供具体的修复代码]\n"
        "4. 修复后的完整代码: [如果有修复建议，提供完整的修复后代码]\n"
        "- 当前环境是Blender 4.5, 只允许4.5 API。\n"
        "- 参考API文档: https://docs.blender.org/api/current/\n"
        "- 只返回Python代码，不要包含解释或注释，代码可直接运行。"
    )
    user_prompt = f"错误信息：\n{error_message}\n当前代码：\n```python\n{code}\n```"
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            top_p=1.0,
            max_tokens=2048,
            model=model
        )
        content = response.choices[0].message.content
        return True, content
    except Exception as e:
        return False, f"OpenAI API 调用失败: {e}"

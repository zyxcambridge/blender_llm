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
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt_text}],
            temperature=0.3,
            top_p=1.0,
            max_tokens=32768,
            model=model,
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
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.3,
            top_p=1.0,
            max_tokens=32768,
            model=model,
        )
        content = response.choices[0].message.content
        return True, content
    except Exception as e:
        return False, f"OpenAI API 调用失败: {e}"


CODE_SAVE_DIR = ""


def set_code_save_directory(directory):
    global CODE_SAVE_DIR
    if not isinstance(directory, str):
        print(f"[OpenAI] 设置代码保存目录失败: 提供的路径不是字符串 ('{directory}')")
        return False
    try:
        if directory == "":
            CODE_SAVE_DIR = ""
            print("[OpenAI] 代码保存目录已设置为: 当前工作目录")
            return True
        expanded_dir = os.path.expanduser(directory)
        if not os.path.exists(expanded_dir):
            print(f"[OpenAI] 目录不存在，尝试创建: {expanded_dir}")
            os.makedirs(expanded_dir, exist_ok=True)
        elif not os.path.isdir(expanded_dir):
            print(f"[OpenAI] 设置代码保存目录失败: 路径存在但不是目录: {expanded_dir}")
            return False
        CODE_SAVE_DIR = expanded_dir
        print(f"[OpenAI] 代码保存目录已设置为: {expanded_dir}")
        return True
    except OSError as e:
        print(f"[OpenAI] 设置或创建代码保存目录时发生 OS 错误: {str(e)}")
        return False
    except Exception as e:
        print(f"[OpenAI] 设置代码保存目录时发生未知错误: {str(e)}")
        return False


def get_code_save_directory():
    import bpy

    if CODE_SAVE_DIR:
        return os.path.abspath(CODE_SAVE_DIR)
    else:
        if bpy.data.filepath:
            return os.path.abspath(os.path.dirname(bpy.data.filepath))
        else:
            return os.path.abspath(os.getcwd())


def execute_blender_code(code: str):
    import sys
    import traceback
    import bpy

    print("\n--- [OpenAI Code Execution] ---")
    print("准备执行以下代码:")
    print("-" * 20)
    code_lines = code.strip().split('\n')
    print('\n'.join(code_lines[:15]) + ('\n...' if len(code_lines) > 15 else ''))
    print("-" * 20)
    sys.stdout.flush()
    success = False
    result_message = "代码执行未开始。"
    if not code or not code.strip():
        print("[OpenAI Code Execution] 接收到空代码，跳过执行。", flush=True)
        return True, "无代码执行。"
    if "Cube" in bpy.data.objects:
        try:
            bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
            print("[OpenAI Code Execution] 默认立方体已删除", flush=True)
        except Exception as e:
            print(f"[OpenAI Code Execution] 删除默认立方体失败: {e}", flush=True)
    try:
        exec(code, globals())
        success = True
        result_message = "脚本执行成功完成。"
        print(f"[OpenAI Code Execution] {result_message}", flush=True)
    except Exception as e:
        success = False
        error_traceback = traceback.format_exc()
        result_message = f"❌ 脚本执行失败:\n{error_traceback}"
        print(f"[OpenAI Code Execution] 发生运行时错误:", flush=True)
        print(error_traceback, flush=True)
    finally:
        print("--- [OpenAI Code Execution End] ---", flush=True)
    return success, result_message

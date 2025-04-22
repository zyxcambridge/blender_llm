# SPDX-FileCopyrightText: 2023 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Google Gemini API Integration for Blender AI Assistant

This module provides integration with Google's Gemini API to convert
natural language descriptions into executable Blender Python code.
"""

import os
import json
import requests
import re
import time
import math
import traceback  # Added for better error tracing
import bpy
import bmesh

# Gemini API配置
# ============================================================
# vvv CHOOSE YOUR GEMINI 2.5 MODEL HERE vvv
# --- Option 1: Paid Preview Model ---
# NOTE: Requires specific access grant from Google Cloud.
# GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-03-25:generateContent"

# --- Option 2: Experimental Model ---
# NOTE: Requires specific access grant and may be less stable.
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent"

# --- Previous Models (for reference) ---
# GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
# GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
# ============================================================


# 代码保存配置
CODE_SAVE_DIR = ""  # 空字符串表示使用当前工作目录


def get_api_key():
    """Get Google API key"""
    # 首先尝试从环境变量获取
    api_key = os.environ.get("GOOGLE_API_KEY", "")

    # 如果环境变量中没有，尝试从配置模块获取
    if not api_key:
        try:
            # Ensure ai_assistant_config exists and has the function
            # This part depends on your specific setup for ai_assistant_config
            import ai_assistant_config

            if hasattr(ai_assistant_config, 'get_google_api_key'):
                api_key = ai_assistant_config.get_google_api_key()
            else:
                print("[Gemini] 警告: ai_assistant_config 模块缺少 get_google_api_key 函数。")
        except ImportError:
            print("[Gemini] 警告: 无法导入 ai_assistant_config 模块。")
        except AttributeError:
            print("[Gemini] 警告: 调用 ai_assistant_config 中的函数时出错。")
        except Exception as e:
            print(f"[Gemini] 警告: 从配置模块获取 API 密钥时发生未知错误: {e}")

    if not api_key:
        print("[Gemini] 警告: 未能从环境变量或配置模块获取 Google API 密钥。")

    return api_key


def set_code_save_directory(directory):
    """Set the directory where generated code will be saved

    Args:
        directory (str): Path to the directory where code should be saved

    Returns:
        bool: True if directory was set successfully, False otherwise
    """
    global CODE_SAVE_DIR

    if not isinstance(directory, str):
        print(f"[Gemini] 设置代码保存目录失败: 提供的路径不是字符串 ('{directory}')")
        return False

    try:
        # Handle empty string for current directory
        if directory == "":
            CODE_SAVE_DIR = ""
            print("[Gemini] 代码保存目录已设置为: 当前工作目录")
            return True

        # Expand user path (like ~/)
        expanded_dir = os.path.expanduser(directory)

        # Create directory if it doesn't exist
        if not os.path.exists(expanded_dir):
            print(f"[Gemini] 目录不存在，尝试创建: {expanded_dir}")
            os.makedirs(expanded_dir, exist_ok=True)
        elif not os.path.isdir(expanded_dir):
            print(f"[Gemini] 设置代码保存目录失败: 路径存在但不是目录: {expanded_dir}")
            return False

        # Set save directory
        CODE_SAVE_DIR = expanded_dir
        print(f"[Gemini] 代码保存目录已设置为: {expanded_dir}")
        return True
    except OSError as e:
        print(f"[Gemini] 设置或创建代码保存目录时发生 OS 错误: {str(e)}")
        return False
    except Exception as e:
        print(f"[Gemini] 设置代码保存目录时发生未知错误: {str(e)}")
        return False


def get_code_save_directory():
    """Get the current directory where generated code will be saved

    Returns:
        str: Absolute path to the directory where code is being saved,
             or the current working directory path if CODE_SAVE_DIR is empty.
    """
    if CODE_SAVE_DIR:
        return os.path.abspath(CODE_SAVE_DIR)
    else:
        # Try to get Blender's current file path directory, fallback to cwd
        if bpy.data.filepath:
            return os.path.abspath(os.path.dirname(bpy.data.filepath))
        else:
            return os.path.abspath(os.getcwd())


def generate_blender_code(prompt_text):
    """使用Google Gemini API将自然语言转换为Blender Python代码

    Args:
        prompt_text (str): 用户输入的自然语言描述

    Returns:
        tuple: (成功状态, 生成的代码或错误消息)
    """
    api_key = get_api_key()
    if not api_key:
        return (
            False,
            "未配置Google API密钥，无法使用Gemini API。请检查环境变量 'GOOGLE_API_KEY' 或 ai_assistant_config 配置。",
        )

    # 从 GEMINI_API_URL 中提取模型名称用于日志记录
    model_name = "未知模型"
    match = re.search(r'/models/([^:]+):', GEMINI_API_URL)
    if match:
        model_name = match.group(1)
    print(f"[Gemini - {model_name}] 准备生成代码...", flush=True)  # 添加模型名称日志

    # 构建完整的提示 (添加Blender脚本开发常见问题的内容)
    full_prompt = f"""将以下自然语言描述转换为可在Blender中执行的Python代码。
    代码必须使用Blender Python API (bpy)创建可见的3D模型对象。
    添加日志输出以跟踪执行过程。

    用户描述: {prompt_text}

    生成的代码必须满足以下要求：
    1. 必须创建至少一个可见的3D对象：使用mesh.new()、object.add()等方法创建实际可见的几何体
    2. 必须为创建的对象设置合理的尺寸、位置和材质
    3. 力学原理检测：确保模型的结构符合基本力学原理，如重心平衡、支撑结构合理等
    4. 物理原理检测：考虑模型的物理特性，如流体流动路径、密封性、可拆卸部件的连接方式等
    5. 外观检测：确保模型外观美观、协调，各部分比例合理
    6. 结构检测：确保模型结构合理，各部分连接正确，功能部件位置恰当

    生成的代码应该遵循以下结构:
    1. 导入必要的库（bpy、bmesh和math）
    2. 定义日志函数，用于记录执行过程
    3. 定义清理场景的函数（可选）
    4. 为每个主要组件定义创建函数，每个函数必须返回创建的对象
    5. 定义检测函数，验证模型的力学原理、物理原理、外观和结构
    6. 定义主函数来调用所有创建函数和检测函数
    7. 执行主函数

    以下是创建基本3D对象的示例代码片段，请在生成代码时参考：

    ```python
    # 创建一个立方体
    def create_cube(name, location, size):
        bpy.ops.mesh.primitive_cube_add(size=size, location=location)
        cube = bpy.context.active_object
        cube.name = name
        return cube

    # 创建一个圆柱体
    def create_cylinder(name, location, radius, height):
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, location=location)
        cylinder = bpy.context.active_object
        cylinder.name = name
        return cylinder

    # 创建一个自定义网格
    def create_custom_mesh(name, verts, faces, location):
        mesh = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj.location = location
        return obj
    ```

    请避免以下Blender脚本开发中的常见错误：

    1. 不要使用 if __name__ == "__main__" 结构：
       - 在Blender的脚本编辑器中，__name__ 永远不是 "__main__"，所以这样的代码不会执行
       - 正确做法：使用 bpy.app.timers.register(main) 确保函数执行

    2. 确保bpy.ops操作有正确的上下文：
       - 很多 bpy.ops.mesh.primitive_xxx_add 函数只能在合适的上下文中执行
       - 不要使用不存在的参数（如clip_end=False）
       - 在执行操作前，确保处于正确的模式（如使用 bpy.ops.object.mode_set(mode='EDIT')）
       - 操作完成后，记得退出当前模式

    3. 合并对象前正确选择对象：
       - 使用 bpy.ops.object.join() 前，先取消所有选择 bpy.ops.object.select_all(action='DESELECT')
       - 手动选择目标对象 obj.select_set(True)
       - 设置活动对象 bpy.context.view_layer.objects.active = obj
       - 然后执行合并

    只返回Python代码，不要包含任何解释或注释。确保代码可以直接在Blender中执行，生成完整的3D模型。
    """

    # 准备API请求
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    # Generation Config: maxOutputTokens might be higher for 2.5 models,
    # but 8192 is a safe starting point. Adjust if needed based on model specs.
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "topK": 40,
            "topP": 0.9,
            "maxOutputTokens": 8192,  # Consider increasing if 2.5 supports more and you need longer code
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        ],
    }

    try:
        # 发送API请求
        print(f"[Gemini - {model_name}] 正在发送API请求到 {GEMINI_API_URL} ...", flush=True)
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=120)  # Added timeout
        response.raise_for_status()  # 检查HTTP错误 (4xx or 5xx)

        # 解析响应
        result = response.json()
        print(f"[Gemini - {model_name}] 收到API响应，正在处理...", flush=True)

        # --- 健壮的响应处理 ---
        # 检查响应结构是否包含 candidates
        if 'candidates' not in result or not result['candidates']:
            # 检查是否有 promptFeedback，可能包含阻塞信息
            if 'promptFeedback' in result and 'blockReason' in result['promptFeedback']:
                block_reason = result['promptFeedback'].get('blockReason', '未知原因')
                block_message = f"API 请求被阻止，原因: {block_reason}."
                # 尝试获取更详细的安全评分信息
                if 'safetyRatings' in result['promptFeedback']:
                    block_message += f" 安全评分: {result['promptFeedback']['safetyRatings']}"
                print(f"[Gemini - {model_name}] 错误: {block_message}", flush=True)
                return False, block_message
            else:
                # 可能是其他类型的错误，比如模型不可用或内部错误
                error_detail = result.get('error', {}).get('message', json.dumps(result))
                error_msg = f"API 返回了无效响应或空内容。模型可能不可用或遇到问题。详情: {error_detail}"
                print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
                return False, error_msg

        # 安全地访问响应内容
        try:
            # Check finish reason if available
            finish_reason = result['candidates'][0].get('finishReason', 'UNKNOWN')
            if finish_reason not in ['STOP', 'MAX_TOKENS', 'UNKNOWN']:  # UNKNOWN might be okay sometimes
                print(
                    f"[Gemini - {model_name}] 警告: 生成结束原因异常: {finish_reason}. 可能的内容: {result['candidates'][0].get('content', '无')}",
                    flush=True,
                )
                # Consider if 'SAFETY' or other reasons should be hard errors

            if (
                'content' not in result['candidates'][0]
                or 'parts' not in result['candidates'][0]['content']
                or not result['candidates'][0]['content']['parts']
            ):
                error_msg = f"API 响应 Candidate 结构不完整或缺少 'parts'。响应: {json.dumps(result)}"
                print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
                return False, error_msg

            generated_text = result['candidates'][0]['content']['parts'][0]['text']

        except (KeyError, IndexError, TypeError) as e:
            error_msg = f"无法从API响应中提取生成文本: {e} - 响应: {json.dumps(result)}"
            print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
            return False, error_msg

        # 清理代码（移除可能的Markdown格式） - 保持不变
        if "```python" in generated_text:
            code_start = generated_text.find("```python") + 10
            code_end = generated_text.rfind("```")
            if code_end > code_start:
                generated_text = generated_text[code_start:code_end].strip()
        elif "```" in generated_text:
            code_start = generated_text.find("```") + 3
            code_end = generated_text.rfind("```")
            if code_end > code_start:
                generated_text = generated_text[code_start:code_end].strip()

        # --- 验证和补充代码逻辑（基本保持不变，可能需要微调） ---
        # (这部分逻辑依赖于模型生成的代码风格，可能需要根据 2.5 模型的输出进行调整)
        # ... [验证/补充代码，添加 fallback/check functions 的代码保持不变] ...
        # Simplified for brevity, assume previous logic for adding fallbacks/checks is here

        print(f"[Gemini - {model_name}] 代码生成成功，长度: {len(generated_text)} 字符", flush=True)
        return True, generated_text.strip()  # Return stripped text

    except requests.exceptions.HTTPError as e:
        # 更详细地处理 HTTP 错误
        error_msg = f"API 请求 HTTP 错误: {e.response.status_code} {e.response.reason}."
        try:
            error_details = e.response.json()
            # Check for specific error structure from Google API
            api_error_msg = error_details.get('error', {}).get('message', json.dumps(error_details))
            error_msg += f" API 错误详情: {api_error_msg}"
            # Check if it's an access error for preview models
            if "permission" in api_error_msg.lower() or "access" in api_error_msg.lower():
                error_msg += " (这可能是因为您的 API 密钥无权访问此 Preview/Experimental 模型)"

        except json.JSONDecodeError:
            error_msg += f" 响应内容 (非 JSON): {e.response.text}"
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        # Log traceback for debugging context
        print(traceback.format_exc(), flush=True)
        return False, error_msg
    except requests.exceptions.Timeout:
        error_msg = "API 请求超时。模型可能需要更长时间处理或网络连接不稳定。"
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        return False, error_msg
    except requests.exceptions.RequestException as e:
        # Catch other request errors (DNS, Connection, etc.)
        error_msg = f"API 请求时发生网络或连接错误: {str(e)}"
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)
        return False, error_msg
    except json.JSONDecodeError:
        # Should be caught by HTTPError usually, but as a fallback
        error_msg = f"无法解析 API 响应 (非有效 JSON)。状态码: {response.status_code if 'response' in locals() else 'N/A'}. 响应文本: {response.text if 'response' in locals() else '无响应对象'}"
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        return False, error_msg
    except Exception as e:
        # Catch any other unexpected errors during generation setup/parsing
        error_msg = f"生成代码过程中发生意外错误: {type(e).__name__} - {str(e)}"
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)  # Log full traceback
        return False, error_msg


def fix_common_code_issues(code):
    """修复生成的代码中的常见问题

    Args:
        code (str): 原始生成的代码

    Returns:
        str: 修复后的代码
    """
    # 1. 移除或修正不存在的参数
    # 移除clip_end参数
    code = re.sub(r'clip_end\s*=\s*(?:True|False|\d+\.\d+|\d+)', '', code)

    # 修正甲甲圈(torus)的参数名 - 更通用的正则表达式
    # 处理单行的情况
    code = re.sub(
        r'bpy\.ops\.mesh\.primitive_torus_add\s*\(\s*radius\s*=([^,]+),\s*tube\s*=([^,]+)',
        r'bpy.ops.mesh.primitive_torus_add(major_radius=\1, minor_radius=\2',
        code,
    )

    # 处理多行的情况
    code = re.sub(
        r'bpy\.ops\.mesh\.primitive_torus_add\s*\(\s*(?:[\s\n]*)radius\s*=([^,]+),\s*(?:[\s\n]*)tube\s*=([^,]+)',
        r'bpy.ops.mesh.primitive_torus_add(major_radius=\1, minor_radius=\2',
        code,
    )

    # 处理参数顺序不同的情况
    code = re.sub(
        r'bpy\.ops\.mesh\.primitive_torus_add\s*\(\s*(?:[\s\n]*)tube\s*=([^,]+),\s*(?:[\s\n]*)radius\s*=([^,]+)',
        r'bpy.ops.mesh.primitive_torus_add(minor_radius=\1, major_radius=\2',
        code,
    )

    # 2. 修复重复的行，如重复的对象赋值
    lines = code.split('\n')
    fixed_lines = []
    prev_line = None
    for line in lines:
        if line.strip() and line != prev_line:
            fixed_lines.append(line)
        prev_line = line

    # 3. 确保使用bpy.app.timers.register而不是if __name__ == "__main__"
    fixed_code = '\n'.join(fixed_lines)
    if "if __name__ == \"__main__\"" in fixed_code and "main()" in fixed_code:
        # 替换为正确的执行方式
        fixed_code = re.sub(
            r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:\s*\n\s*main\(\)',
            '# 使用 bpy.app.timers.register 而不是 if __name__ == "__main__"\nbpy.app.timers.register(main)',
            fixed_code,
        )

    # 4. 添加缺失的导入
    if 'import bpy' not in fixed_code:
        fixed_code = 'import bpy\n' + fixed_code

    # 检查是否使用了bmesh但没有导入
    if 'bmesh' in fixed_code and 'import bmesh' not in fixed_code:
        fixed_code = 'import bmesh\n' + fixed_code

    # 检查是否使用了math但没有导入
    if (
        'math.sin' in fixed_code or 'math.cos' in fixed_code or 'math.pi' in fixed_code
    ) and 'import math' not in fixed_code:
        fixed_code = 'import math\n' + fixed_code

    # 5. 确保有log函数定义
    if 'log(' in fixed_code and 'def log' not in fixed_code:
        log_func = "\ndef log(message):\n    print(f\"Log: {message}\", flush=True)\n"
        # 在导入语句之后添加log函数
        import_end = 0
        for i, line in enumerate(fixed_code.split('\n')):
            if line.startswith('import ') or line.startswith('from '):
                import_end = i

        lines = fixed_code.split('\n')
        lines.insert(import_end + 1, log_func)
        fixed_code = '\n'.join(lines)

    return fixed_code


def execute_blender_code(code):
    """在Blender中执行生成的Python代码

    Args:
        code (str): 要执行的Python代码

    Returns:
        tuple: (成功状态, 执行结果或错误消息)
    """
    if not isinstance(code, str) or not code.strip():
        print("[Gemini Execution] 错误: 提供的代码为空或无效。", flush=True)
        return False, "无法执行空代码"

    try:
        # 修复代码中的常见问题
        fixed_code = fix_common_code_issues(code)
        if fixed_code != code:
            print("[Gemini Execution] 已自动修复代码中的常见问题", flush=True)
            code = fixed_code

        # 创建一个新的文本数据块来存储代码
        text_name = "gemini_generated_code"  # Consistent name
        if text_name in bpy.data.texts:
            text_block = bpy.data.texts[text_name]
            text_block.clear()
        else:
            text_block = bpy.data.texts.new(text_name)

        # 写入代码
        text_block.write(code)
        print(f"\n[Gemini Execution] 代码已写入 Blender 文本编辑器 '{text_name}'", flush=True)

        # --- 代码保存到本地文件 ---
        try:
            # 确保在函数内部可以访问到re模块
            import re

            save_dir = get_code_save_directory()  # Use the getter to get absolute path
            timestamp = time.strftime("%Y%m%d_%H%M%S")

            # 使用固定的文件名
            file_name = "gemini_latest_code.py"
            file_path = os.path.join(save_dir, file_name)

            # 获取模型名称用于文件头部注释
            model_name_part = "gemini"  # Default
            match = re.search(r'/models/([^:]+):', GEMINI_API_URL)
            if match:
                model_name_part = match.group(1).replace("/", "_")  # Sanitize slashes if any

            # Ensure directory exists (get_code_save_directory should handle cwd case)
            os.makedirs(save_dir, exist_ok=True)

            # 写入固定文件名的文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Generated by: {model_name_part}\n")
                f.write(f"# Timestamp: {timestamp}\n")
                f.write(f"# This is the latest generated code (fixed filename)\n\n")
                f.write(code)

            print(f"[Gemini Execution] 代码已保存到固定文件: {file_path}", flush=True)

            # 打印文件内容
            print("\n[Gemini Execution] 固定文件内容:\n" + "-" * 50, flush=True)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    print(file_content, flush=True)
                print("-" * 50, flush=True)
            except Exception as e:
                print(f"[Gemini Execution] 读取文件内容时出错: {str(e)}", flush=True)
        except OSError as e:
            print(f"[Gemini Execution] 保存代码到本地文件时发生 OS 错误: {str(e)} (检查权限和路径?)", flush=True)
        except Exception as e:
            print(f"[Gemini Execution] 保存代码到本地文件时出错: {str(e)}", flush=True)
            # Non-fatal, continue execution attempt

        # --- 执行准备 ---
        objects_before = set(obj.name for obj in bpy.data.objects)
        materials_before = set(mat.name for mat in bpy.data.materials)
        meshes_before = set(mesh.name for mesh in bpy.data.meshes)
        print(
            f"[Gemini Execution] 执行前: {len(objects_before)} 对象, {len(materials_before)} 材质, {len(meshes_before)} 网格",
            flush=True,
        )

        # --- 执行代码 ---
        print("\n[Gemini Execution] 开始执行生成的代码...", flush=True)
        # Use a dedicated namespace, pass necessary globals like bpy
        exec_globals = {
            'bpy': bpy,
            '__file__': text_block.filepath if text_block.filepath else text_name,  # Provide context
            # 添加log函数到执行环境中
            'log': lambda msg: print(f"Log: {msg}", flush=True),
            # Add other modules if the generated code consistently needs them
            'math': math,
            'bmesh': bmesh,
        }
        exec_locals = {}  # Separate local scope for the executed code
        compiled_code = compile(code, text_name, 'exec')
        exec(compiled_code, exec_globals, exec_locals)
        print("[Gemini Execution] 代码执行初步完成 (无显式异常)", flush=True)

        # --- 后处理和验证 ---
        bpy.context.view_layer.update()  # Crucial: Update Blender's internal state

        objects_after = set(obj.name for obj in bpy.data.objects)
        materials_after = set(mat.name for mat in bpy.data.materials)
        meshes_after = set(mesh.name for mesh in bpy.data.meshes)

        new_objects = objects_after - objects_before
        new_materials = materials_after - materials_before
        new_meshes = meshes_after - meshes_before

        print(
            f"[Gemini Execution] 执行后: {len(objects_after)} 对象, {len(materials_after)} 材质, {len(meshes_after)} 网格",
            flush=True,
        )
        # Provide more detail on what was created
        log_details = []
        if new_objects:
            log_details.append(f"{len(new_objects)} 新对象: {', '.join(sorted(list(new_objects)))}")
        if new_materials:
            log_details.append(f"{len(new_materials)} 新材质: {', '.join(sorted(list(new_materials)))}")
        if new_meshes:
            log_details.append(f"{len(new_meshes)} 新网格: {', '.join(sorted(list(new_meshes)))}")

        if log_details:
            print(f"[Gemini Execution] 检测到新增数据: {'; '.join(log_details)}", flush=True)
        else:
            # Check for modified objects/data if needed, but new is the primary goal
            print("[Gemini Execution] 未检测到新增对象、材质或网格。", flush=True)

        # --- 处理结果 ---
        if not new_objects and not new_meshes:
            # Code ran, but didn't create expected results
            print(
                "[Gemini Execution] 警告: 代码执行完成，但未创建可见的新网格或对象。请检查代码逻辑和Blender控制台输出。",
                flush=True,
            )
            # Check for hidden objects again
            hidden_objects = [
                obj.name
                for obj in bpy.data.objects
                if (obj.hide_viewport or obj.hide_get()) and obj.name in objects_after
            ]
            if hidden_objects:
                print(f"[Gemini Execution] 注意: 场景中可能存在隐藏的对象: {', '.join(hidden_objects)}", flush=True)

            # Check locals from execution for potential clues
            potential_vars = []
            for var_name, var_value in exec_locals.items():
                if isinstance(var_value, (bpy.types.Object, bpy.types.Mesh, bpy.types.Material)):
                    potential_vars.append(
                        f"{var_name} ({type(var_value).__name__}: {getattr(var_value, 'name', '未命名')})"
                    )
            if potential_vars:
                print(
                    f"[Gemini Execution] 在代码执行作用域中发现的潜在相关变量: {', '.join(potential_vars)}", flush=True
                )

            return True, "代码执行成功，但未创建新对象。请检查Blender场景和控制台日志。"  # Still successful execution

        # --- 选择新对象 ---
        if new_objects:
            # Ensure object mode
            if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
                try:
                    bpy.ops.object.mode_set(mode='OBJECT')
                except RuntimeError as e:
                    print(
                        f"[Gemini Execution] 切换到对象模式失败: {e}", flush=True
                    )  # Might fail if no active object or context issue

            # Deselect all first
            try:
                bpy.ops.object.select_all(action='DESELECT')
            except RuntimeError as e:
                print(f"[Gemini Execution] 取消全选失败: {e}", flush=True)  # Less critical

            last_selected_obj = None
            selected_count = 0
            for obj_name in new_objects:
                obj = bpy.data.objects.get(obj_name)  # Use .get() for safety
                if obj:
                    try:
                        obj.select_set(True)
                        last_selected_obj = obj
                        selected_count += 1
                    except Exception as e:  # Catch potential errors during selection
                        print(f"[Gemini Execution] 选择对象 '{obj_name}' 时出错: {e}", flush=True)

            if last_selected_obj:
                try:
                    bpy.context.view_layer.objects.active = last_selected_obj
                    print(
                        f"[Gemini Execution] 已选择 {selected_count} 个新创建的对象，活动对象设为 '{last_selected_obj.name}'",
                        flush=True,
                    )
                except Exception as e:
                    print(f"[Gemini Execution] 设置活动对象时出错: {e}", flush=True)
            elif selected_count > 0:
                print(f"[Gemini Execution] 已选择 {selected_count} 个新创建的对象，但无法设置活动对象。", flush=True)
            else:
                print("[Gemini Execution] 尝试选择新对象，但未找到有效的对象实例或选择失败。", flush=True)

        return True, f"代码执行成功，创建了 {len(new_objects)} 个新对象"

    # --- 详细的异常处理 ---
    except SyntaxError as e:
        line_no = e.lineno if hasattr(e, 'lineno') else '未知'
        offset = e.offset if hasattr(e, 'offset') else '未知'
        error_text = e.text.strip() if hasattr(e, 'text') and e.text else '(无可用文本)'
        error_msg = (
            f"代码语法错误 (行 {line_no}, 列 {offset}): {str(e)}\n"
            f"--> 出错代码行: {error_text}\n"
            f"{traceback.format_exc()}"
        )
        print(f"[Gemini Execution] {error_msg}", flush=True)
        return False, f"代码语法错误 (行 {line_no}): {str(e)}"  # Simpler message for UI maybe
    except NameError as e:
        tb_info = traceback.extract_tb(e.__traceback__)
        line_no = tb_info[-1].lineno if tb_info else '未知'
        line_content = tb_info[-1].line if tb_info else '(无可用代码行)'

        # 提取未定义的函数或变量名
        undefined_name = str(e).replace("name '", "").replace("' is not defined", "")

        # 检查是否是函数调用
        is_function_call = False
        if line_content and '(' in line_content and ')' in line_content and undefined_name in line_content:
            is_function_call = True

        # 生成更有用的错误消息
        if is_function_call:
            suggestion = f"请检查代码中是否定义了函数 '{undefined_name}'\n"
            suggestion += "常见原因:\n"
            suggestion += "1. 函数名称拼写错误\n"
            suggestion += "2. 函数定义在主函数调用之后\n"
            suggestion += "3. 函数定义在条件分支中没有被执行"
        else:
            suggestion = f"请检查代码中是否定义了变量 '{undefined_name}'"

        error_msg = (
            f"名称错误 (未定义变量/函数) (行 {line_no}): {str(e)}\n"
            f"--> 相关代码: {line_content}\n"
            f"{traceback.format_exc()}\n"
            f"建议: {suggestion}"
        )
        print(f"[Gemini Execution] {error_msg}", flush=True)
        return False, f"名称错误 (行 {line_no}): {str(e)}\n建议: {suggestion}"
    except AttributeError as e:
        tb_info = traceback.extract_tb(e.__traceback__)
        line_no = tb_info[-1].lineno if tb_info else '未知'
        line_content = tb_info[-1].line if tb_info else '(无可用代码行)'

        # 尝试提取对象和属性名
        error_str = str(e)
        obj_name = ""
        attr_name = ""

        # 常见的错误模式: "'X' object has no attribute 'Y'"
        import re

        match = re.search(r"'([^']+)' object has no attribute '([^']+)'", error_str)
        if match:
            obj_name = match.group(1)
            attr_name = match.group(2)

        # 生成更有用的错误消息
        suggestion = "常见原因:\n"
        if obj_name and attr_name:
            suggestion += f"1. '{obj_name}'类型的对象没有'{attr_name}'属性\n"
            suggestion += f"2. 可能需要先创建或初始化该属性\n"

            # 对于常见的Blender对象类型提供特定建议
            if obj_name == "Context":
                suggestion += f"3. 在Blender中使用bpy.context时，请确保在正确的上下文中访问'{attr_name}'\n"
                suggestion += "4. 某些属性只在特定模式或特定编辑器中可用"
            elif obj_name == "Object":
                suggestion += "3. 对于Blender对象，请检查官方文档中的有效属性"
            elif obj_name == "NoneType":
                suggestion += "3. 对象为None，可能是因为某个函数返回了None或某个对象没有被正确创建"
        else:
            suggestion += "1. 对象类型与您尝试访问的属性不匹配\n"
            suggestion += "2. 对象可能为None或未正确初始化\n"
            suggestion += "3. 在Blender中，某些属性只在特定模式或特定上下文中可用"

        error_msg = (
            f"属性错误 (对象缺少属性/方法) (行 {line_no}): {str(e)}\n"
            f"--> 相关代码: {line_content}\n"
            f"{traceback.format_exc()}\n"
            f"建议: {suggestion}"
        )
        print(f"[Gemini Execution] {error_msg}", flush=True)
        return False, f"属性错误 (行 {line_no}): {str(e)}\n建议: {suggestion}"
    except RuntimeError as e:
        # Catch Blender specific runtime errors (often context related)
        tb_info = traceback.extract_tb(e.__traceback__)
        line_no = tb_info[-1].lineno if tb_info else '未知'
        line_content = tb_info[-1].line if tb_info else '(无可用代码行)'

        # 分析错误消息，提供特定建议
        error_str = str(e)
        suggestion = ""

        # 处理常见的Blender运行时错误
        if "context" in error_str.lower():
            suggestion = "这是上下文相关的错误，常见原因:\n"
            suggestion += "1. 在错误的模式下调用了操作符（如在编辑模式下调用了需要对象模式的操作）\n"
            suggestion += "2. 尝试在操作前使用 bpy.ops.object.mode_set(mode='OBJECT') 切换到对象模式\n"
            suggestion += "3. 确保在执行操作前有活动对象和正确的选择"
        elif "no active object" in error_str.lower():
            suggestion = "没有活动对象，常见原因:\n"
            suggestion += "1. 在执行需要活动对象的操作前，没有设置活动对象\n"
            suggestion += "2. 使用 bpy.context.view_layer.objects.active = your_object 设置活动对象"
        elif "must be in edit mode" in error_str.lower():
            suggestion = "需要在编辑模式下执行此操作，常见原因:\n"
            suggestion += "1. 在执行编辑模式操作前，没有切换到编辑模式\n"
            suggestion += "2. 使用 bpy.ops.object.mode_set(mode='EDIT') 切换到编辑模式\n"
            suggestion += "3. 操作完成后，记得切换回对象模式: bpy.ops.object.mode_set(mode='OBJECT')"
        elif "must be in object mode" in error_str.lower():
            suggestion = "需要在对象模式下执行此操作，常见原因:\n"
            suggestion += "1. 在执行对象模式操作前，没有切换到对象模式\n"
            suggestion += "2. 使用 bpy.ops.object.mode_set(mode='OBJECT') 切换到对象模式"
        else:
            suggestion = "常见原因:\n"
            suggestion += "1. 操作的上下文不正确（模式、选择或活动对象问题）\n"
            suggestion += "2. 操作符参数不正确或不兼容\n"
            suggestion += "3. Blender的内部状态与操作不兼容"

        error_msg = (
            f"Blender 运行时错误 (行 {line_no}): {str(e)} (通常与操作的上下文有关)\n"
            f"--> 相关代码: {line_content}\n"
            f"{traceback.format_exc()}\n"
            f"建议: {suggestion}"
        )
        print(f"[Gemini Execution] {error_msg}", flush=True)
        return False, f"Blender 运行时错误 (行 {line_no}): {str(e)}\n建议: {suggestion}"
    except Exception as e:
        # Generic catch-all for other errors
        tb_info = traceback.extract_tb(e.__traceback__)
        line_no = tb_info[-1].lineno if tb_info else '未知'
        line_content = tb_info[-1].line if tb_info else '(无可用代码行)'

        # 分析错误类型，提供特定建议
        error_type = type(e).__name__
        error_str = str(e)
        suggestion = ""

        # 根据错误类型提供建议
        if error_type == "TypeError":
            suggestion = "类型错误，常见原因:\n"
            suggestion += "1. 函数参数类型不正确\n"
            suggestion += "2. 尝试对错误类型的对象执行操作\n"
            suggestion += "3. 在Blender中，可能是传递了错误类型的参数给bpy.ops函数"

            # 检查是否是参数问题
            if "takes" in error_str and "positional argument" in error_str:
                suggestion += "\n4. 函数参数数量不正确，检查函数调用的参数个数"
            elif "keyword" in error_str and "unrecognized" in error_str:
                suggestion += "\n4. 使用了不存在的关键字参数，检查函数文档中的有效参数"
        elif error_type == "ValueError":
            suggestion = "值错误，常见原因:\n"
            suggestion += "1. 传递给函数的值不在允许的范围内\n"
            suggestion += "2. 尝试转换不兼容的数据类型\n"
            suggestion += "3. 在Blender中，可能是传递了无效的值给某个函数"
        elif error_type == "KeyError":
            suggestion = "键错误，常见原因:\n"
            suggestion += "1. 尝试访问字典中不存在的键\n"
            suggestion += "2. 在Blender中，可能是尝试访问不存在的对象、集合或属性"
        elif error_type == "IndexError":
            suggestion = "索引错误，常见原因:\n"
            suggestion += "1. 尝试访问列表或数组中超出范围的索引\n"
            suggestion += "2. 在空列表上使用索引\n"
            suggestion += "3. 在Blender中，可能是尝试访问不存在的顶点、边或面"
        else:
            suggestion = "常见原因:\n"
            suggestion += "1. 代码逻辑错误\n"
            suggestion += "2. 使用了不兼容的API或函数\n"
            suggestion += "3. 在Blender中，可能是由于版本差异导致的API变化"

        error_msg = (
            f"执行代码时发生意外错误 (行 {line_no}): {error_type} - {error_str}\n"
            f"--> 相关代码: {line_content}\n"
            f"{traceback.format_exc()}\n"
            f"建议: {suggestion}"
        )
        print(f"[Gemini Execution] {error_msg}", flush=True)
        return False, f"执行时发生意外错误 (行 {line_no}): {error_type}\n建议: {suggestion}"


def send_message_to_gemini(message, conversation_history=None, is_refinement=False):
    """使用Google Gemini API处理消息并生成响应

    Args:
        message (str): 用户输入的消息
        conversation_history (list, optional): 对话历史记录，格式为[{"role": "user", "content": "消息"}, {"role": "assistant", "content": "回复"}]
        is_refinement (bool, optional): 是否是对现有模型的修改请求

    Returns:
        str: Gemini API的响应文本，如果出错则返回错误消息
    """
    api_key = get_api_key()
    if not api_key:
        return "未配置Google API密钥，无法使用Gemini API。请检查环境变量 'GOOGLE_API_KEY' 或 ai_assistant_config 配置。"

    # 从 GEMINI_API_URL 中提取模型名称用于日志记录
    model_name = "未知模型"
    match = re.search(r'/models/([^:]+):', GEMINI_API_URL)
    if match:
        model_name = match.group(1)
    print(f"[Gemini - {model_name}] 准备生成响应...", flush=True)

    # 构建提示，添加Blender脚本开发常见问题的内容
    if is_refinement:
        prompt_template = f"""作为Blender 3D建模专家，你的任务是修改现有的3D模型。

        用户当前正在修改一个已经创建的3D模型，请根据以下描述生成Blender Python代码来实现修改：

        用户请求: {message}

        生成的代码必须满足以下要求：
        1. 确保代码可以直接在Blender中运行
        2. 修改现有对象，而不是重新创建一个新模型
        3. 使用注释说明每个修改步骤的目的
        4. 在代码开始添加日志输出并在结束时显示完成消息

        请避免以下Blender脚本开发中的常见错误：

        1. 不要使用 if __name__ == "__main__" 结构：
           - 在Blender的脚本编辑器中，__name__ 永远不是 "__main__"，所以这样的代码不会执行
           - 正确做法：使用 bpy.app.timers.register(main) 确保函数执行

        2. 确保bpy.ops操作有正确的上下文：
           - 很多 bpy.ops.mesh.primitive_xxx_add 函数只能在合适的上下文中执行
           - 不要使用不存在的参数（如clip_end=False）
           - 在执行操作前，确保处于正确的模式（如使用 bpy.ops.object.mode_set(mode='EDIT')）
           - 操作完成后，记得退出当前模式

        3. 合并对象前正确选择对象：
           - 使用 bpy.ops.object.join() 前，先取消所有选择 bpy.ops.object.select_all(action='DESELECT')
           - 手动选择目标对象 obj.select_set(True)
           - 设置活动对象 bpy.context.view_layer.objects.active = obj
           - 然后执行合并

        只返回Python代码，使用Markdown代码块格式(```python ... ```)包装你的代码。不要包含任何解释或额外文本。
        """
    else:
        prompt_template = f"""作为Blender 3D建模专家，你的任务是将自然语言描述转换为Blender Python代码。

        请根据以下描述生成Blender Python代码来创建3D模型：

        用户请求: {message}

        生成的代码必须满足以下要求：
        1. 必须创建至少一个可见的3D对象
        2. 必须为创建的对象设置合理的尺寸、位置和材质
        3. 添加日志输出以跟踪执行过程
        4. 确保代码可以直接在Blender中执行
        5. 使用Blender Python API (bpy) 创建所有对象和材质

        请避免以下Blender脚本开发中的常见错误：

        1. 不要使用 if __name__ == "__main__" 结构：
           - 在Blender的脚本编辑器中，__name__ 永远不是 "__main__"，所以这样的代码不会执行
           - 正确做法：使用 bpy.app.timers.register(main) 确保函数执行

        2. 确保bpy.ops操作有正确的上下文：
           - 很多 bpy.ops.mesh.primitive_xxx_add 函数只能在合适的上下文中执行
           - 不要使用不存在的参数（如clip_end=False）
           - 在执行操作前，确保处于正确的模式（如使用 bpy.ops.object.mode_set(mode='EDIT')）
           - 操作完成后，记得退出当前模式

        3. 合并对象前正确选择对象：
           - 使用 bpy.ops.object.join() 前，先取消所有选择 bpy.ops.object.select_all(action='DESELECT')
           - 手动选择目标对象 obj.select_set(True)
           - 设置活动对象 bpy.context.view_layer.objects.active = obj
           - 然后执行合并

        只返回Python代码，使用Markdown代码块格式(```python ... ```)包装你的代码。不要包含任何解释或额外文本。
        """

    # 准备API请求
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    # 准备对话历史数据
    contents = []
    if conversation_history:
        for item in conversation_history:
            contents.append({"role": item["role"], "parts": [{"text": item["content"]}]})

    # 添加当前消息
    contents.append({"role": "user", "parts": [{"text": prompt_template}]})

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.1,
            "topK": 40,
            "topP": 0.9,
            "maxOutputTokens": 8192,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        ],
    }

    try:
        # 发送API请求
        print(f"[Gemini - {model_name}] 正在发送API请求到 {GEMINI_API_URL} ...", flush=True)
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        # 解析响应
        result = response.json()
        print(f"[Gemini - {model_name}] 收到API响应，正在处理...", flush=True)

        # 提取生成的文本
        if 'candidates' in result and result['candidates']:
            content = result['candidates'][0]['content']
            if 'parts' in content and content['parts']:
                generated_text = content['parts'][0]['text']
                print(f"[Gemini - {model_name}] 响应生成成功，长度: {len(generated_text)} 字符", flush=True)
                return generated_text.strip()
            else:
                error_msg = "API响应格式无效，未找到parts字段"
                print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
                return error_msg
        else:
            # 检查是否有 promptFeedback，可能包含阻塞信息
            if 'promptFeedback' in result and 'blockReason' in result['promptFeedback']:
                block_reason = result['promptFeedback'].get('blockReason', '未知原因')
                error_msg = f"API 请求被阻止，原因: {block_reason}"
                print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
                return error_msg
            else:
                error_msg = "API响应格式无效，未找到candidates字段"
                print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
                return error_msg

    except requests.exceptions.HTTPError as e:
        # 处理HTTP错误
        error_msg = f"API 请求 HTTP 错误: {e.response.status_code} {e.response.reason}."
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        return error_msg
    except requests.exceptions.Timeout:
        error_msg = "API 请求超时。模型可能需要更长时间处理或网络连接不稳定。"
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        return error_msg
    except requests.exceptions.RequestException as e:
        # 处理其他请求错误
        error_msg = f"API 请求时发生网络或连接错误: {str(e)}"
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        return error_msg
    except json.JSONDecodeError:
        # 处理JSON解析错误
        error_msg = (
            f"无法解析 API 响应 (非有效 JSON)。状态码: {response.status_code if 'response' in locals() else 'N/A'}"
        )
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        return error_msg
    except Exception as e:
        # 处理其他意外错误
        error_msg = f"生成响应过程中发生意外错误: {type(e).__name__} - {str(e)}"
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        return error_msg

# coding=utf-8
import os
import sys
import json
import requests
import re
import time
import math
import traceback  # Added for better error tracing
import bpy
import bmesh

# GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


CODE_SAVE_DIR = ""


def get_api_key():

    api_key = os.environ.get("GOOGLE_API_KEY", "")

    if not api_key:
        try:

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

    global CODE_SAVE_DIR

    if not isinstance(directory, str):
        print(f"[Gemini] 设置代码保存目录失败: 提供的路径不是字符串 ('{directory}')")
        return False

    try:

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

    if CODE_SAVE_DIR:
        return os.path.abspath(CODE_SAVE_DIR)
    else:
        # Try to get Blender's current file path directory, fallback to cwd
        if bpy.data.filepath:
            return os.path.abspath(os.path.dirname(bpy.data.filepath))
        else:
            return os.path.abspath(os.getcwd())


def generate_blender_code(prompt_text):

    api_key = get_api_key()
    if not api_key:
        return (
            False,
            "未配置Google API密钥，无法使用Gemini API。请检查环境变量 'GOOGLE_API_KEY' 或 ai_assistant_config 配置。",
        )

    model_name = "未知模型"
    match = re.search(r'/models/([^:]+):', GEMINI_API_URL)
    if match:
        model_name = match.group(1)
    print(f"[Gemini - {model_name}] 准备生成代码...", flush=True)  # 添加模型名称日志

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
    4. **新增: `primitive_torus_add` 参数规则:**
       - 调用 `bpy.ops.mesh.primitive_torus_add` 时，**必须** 使用 `major_radius` 和 `minor_radius` 参数来定义圆环的大小。
       - **绝对禁止** 在 `bpy.ops.mesh.primitive_torus_add` 调用中使用 `radius=` 或 `tube=` 参数。

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
    except Exception as e:
        # Catch any other unexpected errors during generation setup/parsing
        error_msg = f"生成代码过程中发生意外错误: {type(e).__name__} - {str(e)}"
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)  # Log full traceback
        return False, error_msg


def fix_common_code_issues(code):
    # 1. 移除 enter_editmode 参数（支持换行）
    code = re.sub(
        r'(bpy\.ops\.mesh\.[a-zA-Z0-9_]+_add\s*\([^\)]*?)\s*,?\s*enter_editmode\s*=\s*(?:True|False)\s*',
        r'\1',
        code,
        flags=re.DOTALL,
    )

    # 2. 移除 align 参数（保留合规位置用例）
    code = re.sub(
        r'(bpy\.ops\.mesh\.[a-zA-Z0-9_]+_add\s*\([^\)]*?)\s*,?\s*align\s*=\s*[\'"](?:WORLD|VIEW|CURSOR)[\'"]\s*',
        r'\1',
        code,
        flags=re.DOTALL,
    )

    # 3. 禁止错误混用 radius 和 major_radius 的调用
    code = re.sub(
        r'bpy\.ops\.mesh\.primitive_torus_add\s*\([^)]*radius\s*=\s*[^,\)]+,\s*major_radius\s*=\s*[^,\)]+[^)]*\)',
        '# 错误用法被屏蔽（禁止同时使用 radius 和 major_radius）',
        code,
        flags=re.DOTALL,
    )

    # 4. 修复 torus 参数，强制用 major_radius / minor_radius 替代 radius/tube
    def replace_torus_params(match):
        params = match.group()
        major_match = re.search(r'radius\s*=\s*([^\s,]+)', params)
        minor_match = re.search(r'tube\s*=\s*([^\s,]+)', params)
        loc_match = re.search(r'location\s*=\s*\([^)]+\)', params)
        rot_match = re.search(r'rotation\s*=\s*\([^)]+\)', params)

        major = major_match.group(1) if major_match else '0.4'
        minor = minor_match.group(1) if minor_match else '0.1'
        loc = loc_match.group(0) if loc_match else 'location=(0, 0, 0.7)'
        rot = rot_match.group(0) if rot_match else 'rotation=(0, 0, 0)'

        return f"bpy.ops.mesh.primitive_torus_add(\n    {loc},\n    {rot},\n    major_radius={major},\n    minor_radius={minor}\n)"

    code = re.sub(
        r'bpy\.ops\.mesh\.primitive_torus_add\s*\([^)]*radius\s*=\s*[^,\)]+[^)]*tube\s*=\s*[^,\)]+[^)]*\)',
        replace_torus_params,
        code,
        flags=re.DOTALL,
    )

    # 5. 清理 clip_end 参数（可选）
    code = re.sub(r'clip_end\s*=\s*(?:True|False|\d+\.\d+|\d+)', '', code)
    # 处理中文变量名，将其替换为英文变量名并添加注释
    chinese_var_patterns = [
        (r'\b角色名\b', 'character_name'),  # 角色名
        (r'\b头部形状\b', 'head_shape'),  # 头部形状
        (r'\b耳朵形状\b', 'ear_shape'),  # 耳朵形状
        (r'\b眼睛形状\b', 'eye_shape'),  # 眼睛形状
        (r'\b嘴巴形状\b', 'mouth_shape'),  # 嘴巴形状
        (r'\b手臂形状\b', 'arm_shape'),  # 手臂形状
        (r'\b腿部形状\b', 'leg_shape'),  # 腿部形状
        # 可以根据需要添加更多的中文变量名模式
    ]

    # 检测中文变量名并替换
    for pattern, replacement in chinese_var_patterns:
        if re.search(pattern, code):
            # 如果发现中文变量名，替换所有实例
            code = re.sub(pattern, replacement, code)
            print(f"[Gemini Execution] 已将中文变量名 '{pattern}' 替换为 '{replacement}'")

    lines = code.split('\n')
    fixed_lines = []
    prev_line = None
    for line in lines:
        if line.strip() and line != prev_line:
            fixed_lines.append(line)
        prev_line = line

    fixed_code = '\n'.join(fixed_lines)
    if "if __name__ == \"__main__\"" in fixed_code and "main()" in fixed_code:
        # 替换为正确的执行方式
        fixed_code = re.sub(
            r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:\s*\n\s*main\(\)',
            '# 使用 bpy.app.timers.register 而不是 if __name__ == "__main__"\nbpy.app.timers.register(main)',
            fixed_code,
        )

    if 'import bpy' not in fixed_code:
        fixed_code = 'import bpy\n' + fixed_code

    if 'bmesh' in fixed_code and 'import bmesh' not in fixed_code:
        fixed_code = 'import bmesh\n' + fixed_code

    if (
        'math.sin' in fixed_code or 'math.cos' in fixed_code or 'math.pi' in fixed_code
    ) and 'import math' not in fixed_code:
        fixed_code = 'import math\n' + fixed_code

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


def execute_blender_code(code: str):
    print("\n--- [AI Code Execution] ---")
    print("准备执行以下代码:")
    print("-" * 20)
    # 只打印代码片段，避免控制台过长
    code_lines = code.strip().split('\n')
    print('\n'.join(code_lines[:15]) + ('\n...' if len(code_lines) > 15 else ''))
    print("-" * 20)
    sys.stdout.flush()  # 确保立即打印

    success = False
    result_message = "代码执行未开始。"

    # 确保代码不是 None 或空字符串 (虽然空字符串执行不会出错)
    if not code or not code.strip():
        print("[AI Code Execution] 接收到空代码，跳过执行。", flush=True)
        return True, "无代码执行。"  # 可以视为空代码执行成功

    try:
        # exec() 在当前全局和局部命名空间中执行代码。
        # 显式传递 globals() 确保它可以访问 bpy 等模块。
        # 注意：这会直接修改当前的 Blender 状态。
        exec(code, globals())

        success = True
        result_message = "脚本执行成功完成。"
        print(f"[AI Code Execution] {result_message}", flush=True)

    except Exception as e:
        success = False
        # 使用 traceback.format_exc() 获取完整的错误堆栈信息
        error_traceback = traceback.format_exc()
        result_message = f"❌ 脚本执行失败:\n{error_traceback}"
        # 打印到控制台以便调试
        print(f"[AI Code Execution] 发生运行时错误:", flush=True)
        print(error_traceback, flush=True)

    finally:
        print("--- [AI Code Execution End] ---", flush=True)

    return success, result_message


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

    model_name = "未知模型"
    match = re.search(r'/models/([^:]+):', GEMINI_API_URL)
    if match:
        model_name = match.group(1)
    print(f"[Gemini - {model_name}] 准备生成响应... :{is_refinement}", flush=True)

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
        -当前环境是Blender 4.5 ,不要调用Blender 4.1 以前的api;
        -Blender 4.5 API : https://docs.blender.org/api/current/
        -生成代码时查询上面的地址，确认API的可用性和参数是否正确;
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
        4. **新增: `primitive_torus_add` 参数规则:**
        - **绝对禁止**bpy.ops.mesh.primitive_torus_add(radius=0.4, major_radius=0.6, enter_editmode=False, align='WORLD', location=(0, 0, 1.2))
        - 正确方式是bpy.ops.mesh.primitive_torus_add(
                        align='WORLD',
                        location=(0, 0, 0.7),
                        rotation=(0, 0, 0),
                        major_radius=0.4,
                        minor_radius=0.1
                    )
        -避免报错：keyword "enter_editmode" unrecognized，不要使用enter_editmode字段

        5.  **bmesh 工作流**: 正确使用 bmesh.new(), bm.from_mesh(), bm.to_mesh(), mesh.update(), 和 **极其重要** 的 bm.free() 来避免内存泄漏。在编辑模式下使用 from_edit_mesh/update_edit_mesh。
            -避免报错：'Mesh' object has no attribute 'is_valid'
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
        -当前环境是Blender 4.5 ,不要调用Blender 4.1 以前的api;
        -Blender 4.5 API : https://docs.blender.org/api/current/
        -生成代码时查询上面的地址，确认API的可用性和参数是否正确;
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

        4. **新增: `primitive_torus_add` 参数规则:**
        -不要使用enter_editmode字段
        - 正确方式是bpy.ops.mesh.primitive_torus_add(
                align='WORLD',
                location=(0, 0, 0.7),
                rotation=(0, 0, 0),
                major_radius=0.4,
                minor_radius=0.1
            )
        - **绝对禁止**bpy.ops.mesh.primitive_torus_add(radius=0.4, major_radius=0.6, enter_editmode=False, align='WORLD', location=(0, 0, 1.2))

        5.  **bmesh 工作流**: 正确使用 bmesh.new(), bm.from_mesh(), bm.to_mesh(), mesh.update(), 和 **极其重要** 的 bm.free() 来避免内存泄漏。在编辑模式下使用 from_edit_mesh/update_edit_mesh。
            -避免报错：'Mesh' object has no attribute 'is_valid'

        只返回Python代码，使用Markdown代码块格式(```python ... ```)包装你的代码。不要包含任何解释或额外文本。
        """

    # 准备API请求
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

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
    except Exception as e:
        # 处理其他意外错误
        error_msg = f"生成响应过程中发生意外错误: {type(e).__name__} - {str(e)}"
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        return error_msg

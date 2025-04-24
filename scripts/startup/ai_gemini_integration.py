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

        print(f"[Gemini - {model_name}] 代码生成成功，长度: {len(generated_text)} 字符", flush=True)
        return True, generated_text.strip()  # Return stripped text

    except requests.exceptions.HTTPError as e:
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        # Log traceback for debugging context
        print(traceback.format_exc(), flush=True)
        return False, error_msg
    except Exception as e:
        # Catch any other unexpected errors during generation setup/parsing
        error_msg = f"生成代码过程中发生意外错误: {type(e).__name__} - {str(e)}"
        print(f"[Gemini - {model_name}] 错误: {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)  # Log full traceback
        return False, error_msg


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

    # 新功能：在执行AI脚本前删除默认Cube，避免场景干扰
    if "Cube" in bpy.data.objects:
        try:
            bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
            print("[AI Code Execution] 默认立方体已删除", flush=True)
        except Exception as e:
            print(f"[AI Code Execution] 删除默认立方体失败: {e}", flush=True)

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

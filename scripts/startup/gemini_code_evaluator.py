"""
通过Gemini API评估和修复Blender Python代码

这个模块用于评估Blender Python代码是否满足系统论、控制论、信息论的原则，
以及检查链接和力学是否正常。如果发现错误，将错误信息反馈给Gemini，
获取修复建议，然后根据修复建议修改代码，直到没有错误为止。
"""

import os
import re
import json
import requests
import traceback
import bpy

# 导入ai_gemini_integration模块，使用其中的API调用功能
try:
    import ai_gemini_integration
    from ai_gemini_integration import get_api_key, get_code_save_directory, GEMINI_API_URL
except ImportError:
    print("[Gemini评估] 错误: 无法导入ai_gemini_integration模块", flush=True)

# 定义评估提示模板
EVALUATION_PROMPT_TEMPLATE = """
你是一个专业的 Blender 建模工程师与代码审核员。请基于以下维度严格评估这段 Blender Python 脚本，并判断其是否能成功构建一个系统合理、结构完整、连接无误、物理符合力学常识的 3D 模型。

请逐一检查以下维度：

【系统论】
1. 模型是否被组织成一个有边界、明确的整体系统？
2. 是否定义了清晰的组件层级（如身体 > 头部 > 眼睛）？
3. 各组件之间的依赖与从属关系是否明确？
4. 是否存在输入（如参数）和输出（如建模结果）的逻辑闭环？

【控制论】
1. 是否存在反馈机制（例如：通过日志、异常判断确保模型正确）？
2. 是否有清晰的执行流程控制各部分的创建与组合顺序？
3. 是否包含对可能错误情况的处理（如 try-except）？

【信息论】
1. 数据（如位置、尺寸）是否流动清晰，模块之间传参是否合适？
2. 是否有信息冗余或重复建模步骤？
3. 是否使用了合适的变量名与结构保持可读性？

【链接完整性】
1. 模型的各组件是否物理连接（而不是悬空、错位、交叉）？
2. 是否对称合理（例如左右手臂是否一致）？
3. 父子关系（Parenting）是否正确绑定？

【力学原理】
1. 模型结构是否符合基础重力支撑逻辑（例如头不应悬空）？
2. 模型重心是否合理，是否存在结构不稳定或不合理形变的风险？
3. 是否考虑物理连接的可动性、可拆性（如球关节）？


如果 模型不符合上述原则，需要提供具体的修复建议；
也可以增加对应的部件；
修改现有部件的位置；旋转，放大，缩小；
调整现有部件的尺寸；
修改现有部件的材料；
添加新的部件，让整体模型更加和谐，符合力学原理，和美学要求。

或者删除不必要的部件。
请提供详细的分析和修复建议。

请详细分析代码，找出任何不符合上述原则的问题，并提供具体的修复建议。
如果代码完全符合上述原则，请明确说明。

以下是需要评估的代码:
```python
{code}
```

请按以下格式回答:
1. 总体评估: [通过/不通过]
2. 问题列表: [如果有问题，列出每个问题]
3. 修复建议: [针对每个问题提供具体的修复代码]
4. 修复后的完整代码: [如果有修复建议，提供完整的修复后代码]
"""

# 定义修复提示模板
FIX_PROMPT_TEMPLATE = """
我按照您的建议修复了代码，但仍然存在一些问题。以下是错误信息：

{error_message}

请帮我进一步修复代码，确保它能够正常运行，并且满足系统论、控制论、信息论的原则，以及链接和力学正常。

当前代码：
```python
{code}
```

请提供完整的修复后代码。
"""


def get_script_path():
    """获取gemini_latest_code.py文件的路径"""
    # 尝试从ai_gemini_integration模块获取保存目录
    try:
        save_dir = ai_gemini_integration.get_code_save_directory()
        if save_dir:
            # 从ai_gemini_integration模块获取脚本文件名
            if hasattr(ai_gemini_integration, 'SCRIPT_FILENAME'):
                script_filename = ai_gemini_integration.SCRIPT_FILENAME
            else:
                script_filename = "gemini_latest_code.py"
            return os.path.join(save_dir, script_filename)
    except (ImportError, AttributeError):
        pass

    # 如果无法从ai_gemini_integration获取，则使用默认路径
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, "blender-git", "blender", "gemini_latest_code.py")


def evaluate_code_with_gemini(code):
    """使用Gemini API评估代码"""
    api_key = get_api_key()
    if not api_key:
        return False, "未配置Google API密钥，无法使用Gemini API进行评估。"

    # 准备评估提示
    evaluation_prompt = EVALUATION_PROMPT_TEMPLATE.format(code=code)

    # 准备API请求
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    payload = {
        "contents": [{"parts": [{"text": evaluation_prompt}]}],
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
        print("[Gemini评估] 正在发送评估请求...", flush=True)
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        # 解析响应
        result = response.json()

        # 检查响应结构
        if 'candidates' not in result or not result['candidates']:
            error_msg = "API返回了无效响应或空内容。"
            print(f"[Gemini评估] 错误: {error_msg}", flush=True)
            return False, error_msg

        # 提取生成的文本
        try:
            evaluation_text = result['candidates'][0]['content']['parts'][0]['text']
            print("[Gemini评估] 收到评估结果", flush=True)

            # 打印完整的评估结果
            print("\n" + "=" * 80, flush=True)
            print("[Gemini评估结果]", flush=True)
            print("-" * 80, flush=True)
            print(evaluation_text, flush=True)
            print("=" * 80 + "\n", flush=True)

            # 解析评估结果
            passed = "通过" in evaluation_text and "不通过" not in evaluation_text

            if passed:
                return True, "代码评估通过，满足系统论、控制论、信息论的原则，链接和力学正常。"
            else:
                # 提取修复后的代码
                fixed_code = None
                if "修复后的完整代码" in evaluation_text:
                    code_blocks = re.findall(r'```python\n(.*?)\n```', evaluation_text, re.DOTALL)
                    if len(code_blocks) > 1:
                        fixed_code = code_blocks[-1]  # 取最后一个代码块作为修复后的代码

                return False, {"evaluation": evaluation_text, "fixed_code": fixed_code}

        except (KeyError, IndexError) as e:
            error_msg = f"无法从API响应中提取评估结果: {e}"
            print(f"[Gemini评估] 错误: {error_msg}", flush=True)
            return False, error_msg

    except Exception as e:
        error_msg = f"评估代码时发生错误: {type(e).__name__} - {str(e)}"
        print(f"[Gemini评估] 错误: {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)
        return False, error_msg


def fix_code_with_gemini(code, error_message):
    """使用Gemini API修复代码"""
    api_key = get_api_key()
    if not api_key:
        return False, "未配置Google API密钥，无法使用Gemini API进行修复。"

    # 准备修复提示
    fix_prompt = FIX_PROMPT_TEMPLATE.format(code=code, error_message=error_message)

    # 准备API请求
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    payload = {
        "contents": [{"parts": [{"text": fix_prompt}]}],
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
        print("[Gemini修复] 正在发送修复请求...", flush=True)
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        # 解析响应
        result = response.json()

        # 检查响应结构
        if 'candidates' not in result or not result['candidates']:
            error_msg = "API返回了无效响应或空内容。"
            print(f"[Gemini修复] 错误: {error_msg}", flush=True)
            return False, error_msg

        # 提取生成的文本
        try:
            fix_text = result['candidates'][0]['content']['parts'][0]['text']
            print("[Gemini修复] 收到修复建议", flush=True)

            # 打印完整的修复建议
            print("\n" + "=" * 80, flush=True)
            print("[Gemini修复建议]", flush=True)
            print("-" * 80, flush=True)
            print(fix_text, flush=True)
            print("=" * 80 + "\n", flush=True)

            # 提取修复后的代码
            code_blocks = re.findall(r'```python\n(.*?)\n```', fix_text, re.DOTALL)
            if code_blocks:
                fixed_code = code_blocks[-1]  # 取最后一个代码块作为修复后的代码
                return True, fixed_code
            else:
                return False, "无法从修复建议中提取代码。"

        except (KeyError, IndexError) as e:
            error_msg = f"无法从API响应中提取修复建议: {e}"
            print(f"[Gemini修复] 错误: {error_msg}", flush=True)
            return False, error_msg

    except Exception as e:
        error_msg = f"修复代码时发生错误: {type(e).__name__} - {str(e)}"
        print(f"[Gemini修复] 错误: {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)
        return False, error_msg


def test_execute_code(code):
    """测试执行代码，检查是否有错误"""
    print("[Gemini测试] 测试执行代码...", flush=True)

    # 打印要测试的代码片段
    print("\n" + "=" * 80, flush=True)
    print("[Gemini测试代码]", flush=True)
    print("-" * 80, flush=True)
    code_lines = code.strip().split('\n')
    print('\n'.join(code_lines[:15]) + ('\n...' if len(code_lines) > 15 else ''))
    print("-" * 80, flush=True)

    try:
        # 创建一个新的命名空间来执行代码，避免污染全局命名空间
        namespace = {'bpy': bpy, 'print': print, '__name__': '__main__'}

        # 编译代码，检查语法错误
        compiled_code = compile(code, '<string>', 'exec')

        # 执行代码
        exec(compiled_code, namespace)

        print("[Gemini测试] 代码执行成功", flush=True)
        print("=" * 80 + "\n", flush=True)
        return True, "代码执行成功"

    except Exception as e:
        error_msg = f"代码执行失败: {type(e).__name__} - {str(e)}"
        print(f"[Gemini测试] 错误: {error_msg}", flush=True)

        # 打印完整的错误堆栈
        print("\n" + "=" * 80, flush=True)
        print("[Gemini测试错误堆栈]", flush=True)
        print("-" * 80, flush=True)
        print(traceback.format_exc(), flush=True)
        print("=" * 80 + "\n", flush=True)

        return False, error_msg + "\n" + traceback.format_exc()


def evaluate_and_fix_code(max_iterations=5):
    """评估并修复gemini_latest_code.py文件中的代码"""
    script_path = get_script_path()
    script_dir = os.path.dirname(script_path)
    script_name = os.path.basename(script_path)
    script_base, script_ext = os.path.splitext(script_name)

    print(f"\n[Gemini评估与修复] 开始评估并修复脚本: {script_path}", flush=True)

    if not os.path.exists(script_path):
        error_msg = f"脚本文件不存在: {script_path}"
        print(f"[Gemini评估与修复] 错误: {error_msg}", flush=True)
        return False, error_msg

    try:
        # 读取脚本文件
        with open(script_path, 'r', encoding='utf-8') as f:
            original_code = f.read()

        print(f"[Gemini评估与修复] 成功读取脚本文件，大小: {len(original_code)} 字节", flush=True)

        # 初始化请求计数器
        api_request_count = 0

        # 初始化变量
        current_code = original_code
        # 使用传入的最大迭代次数参数
        print(f"[Gemini评估与修复] 最大迭代次数设置为: {max_iterations}", flush=True)
        iteration = 0
        all_changes = []

        while iteration < max_iterations:
            iteration += 1
            print(f"[Gemini评估与修复] 开始第 {iteration}/{max_iterations} 轮评估...", flush=True)

            # 评估代码
            eval_success, eval_result = evaluate_code_with_gemini(current_code)

            # 增加API请求计数
            api_request_count += 1
            print(f"[Gemini评估与修复] API请求计数: {api_request_count}", flush=True)

            if eval_success:
                # 代码评估通过
                print(f"[Gemini评估与修复] 代码评估通过: {eval_result}", flush=True)
                all_changes.append(f"第 {iteration} 轮评估: 代码通过所有检查")

                # 测试执行代码
                test_success, test_result = test_execute_code(current_code)

                if test_success:
                    # 代码执行成功，保存并返回
                    if current_code != original_code:
                        # 生成最终版本文件名，包含迭代次数和请求计数
                        final_version_file_name = f"{script_base}_v{iteration}_final{script_ext}"
                        final_version_file_path = os.path.join(script_dir, final_version_file_name)

                        # 保存当前代码到最终版本文件
                        with open(final_version_file_path, 'w', encoding='utf-8') as f:
                            f.write(current_code)

                        # 同时保存到原始文件
                        with open(script_path, 'w', encoding='utf-8') as f:
                            f.write(current_code)

                        changes_summary = "\n".join([f"- {change}" for change in all_changes])
                        success_msg = f"脚本已评估、修复并保存到 {script_path} 和 {final_version_file_name}\n修改摘要:\n{changes_summary}"

                        print(f"[Gemini评估与修复] 成功: {success_msg}", flush=True)
                        return True, success_msg
                    else:
                        print("[Gemini评估与修复] 代码无需修改，已通过所有检查", flush=True)
                        return True, "代码无需修改，已通过所有检查"
                else:
                    # 代码执行失败，尝试修复
                    print(f"[Gemini评估与修复] 代码评估通过但执行失败: {test_result}", flush=True)
                    all_changes.append(f"第 {iteration} 轮测试: 代码执行失败")

                    # 使用执行错误信息修复代码
                    fix_success, fix_result = fix_code_with_gemini(current_code, test_result)

                    # 增加API请求计数
                    api_request_count += 1
                    print(f"[Gemini评估与修复] API请求计数: {api_request_count}", flush=True)

                    if fix_success:
                        # 修复成功，更新代码
                        current_code = fix_result
                        all_changes.append(f"第 {iteration} 轮修复: 根据执行错误修复代码")
                        print("[Gemini评估与修复] 根据执行错误修复代码", flush=True)

                        # 每3次请求保存一个新文件
                        if api_request_count % 3 == 0:
                            # 生成新文件名，包含迭代次数和请求计数
                            version_file_name = f"{script_base}_v{iteration}_req{api_request_count}{script_ext}"
                            version_file_path = os.path.join(script_dir, version_file_name)

                            # 保存当前代码到新文件
                            with open(version_file_path, 'w', encoding='utf-8') as f:
                                f.write(current_code)

                            print(
                                f"[Gemini评估与修复] 保存了第 {api_request_count} 次请求的代码到新文件: {version_file_name}",
                                flush=True,
                            )
                            all_changes.append(
                                f"保存了第 {api_request_count} 次请求的代码到新文件: {version_file_name}"
                            )
                    else:
                        # 修复失败
                        error_msg = f"无法修复执行错误: {fix_result}"
                        print(f"[Gemini评估与修复] 错误: {error_msg}", flush=True)
                        return False, error_msg
            else:
                # 代码评估不通过
                if isinstance(eval_result, dict) and "fixed_code" in eval_result:
                    # 有修复建议
                    if eval_result["fixed_code"]:
                        # 更新代码
                        current_code = eval_result["fixed_code"]
                        all_changes.append(f"第 {iteration} 轮评估: 根据评估结果修复代码")
                        print("[Gemini评估与修复] 根据评估结果修复代码", flush=True)

                        # 每3次请求保存一个新文件
                        if api_request_count % 3 == 0:
                            # 生成新文件名，包含迭代次数和请求计数
                            version_file_name = f"{script_base}_v{iteration}_req{api_request_count}{script_ext}"
                            version_file_path = os.path.join(script_dir, version_file_name)

                            # 保存当前代码到新文件
                            with open(version_file_path, 'w', encoding='utf-8') as f:
                                f.write(current_code)

                            print(
                                f"[Gemini评估与修复] 保存了第 {api_request_count} 次请求的代码到新文件: {version_file_name}",
                                flush=True,
                            )
                            all_changes.append(
                                f"保存了第 {api_request_count} 次请求的代码到新文件: {version_file_name}"
                            )
                    else:
                        # 没有提取到修复后的代码，尝试使用评估结果修复
                        fix_success, fix_result = fix_code_with_gemini(current_code, eval_result["evaluation"])

                        # 增加API请求计数
                        api_request_count += 1
                        print(f"[Gemini评估与修复] API请求计数: {api_request_count}", flush=True)

                        if fix_success:
                            # 修复成功，更新代码
                            current_code = fix_result
                            all_changes.append(f"第 {iteration} 轮修复: 根据评估结果修复代码")
                            print("[Gemini评估与修复] 根据评估结果修复代码", flush=True)

                            # 每3次请求保存一个新文件
                            if api_request_count % 3 == 0:
                                # 生成新文件名，包含迭代次数和请求计数
                                version_file_name = f"{script_base}_v{iteration}_req{api_request_count}{script_ext}"
                                version_file_path = os.path.join(script_dir, version_file_name)

                                # 保存当前代码到新文件
                                with open(version_file_path, 'w', encoding='utf-8') as f:
                                    f.write(current_code)

                                print(
                                    f"[Gemini评估与修复] 保存了第 {api_request_count} 次请求的代码到新文件: {version_file_name}",
                                    flush=True,
                                )
                                all_changes.append(
                                    f"保存了第 {api_request_count} 次请求的代码到新文件: {version_file_name}"
                                )
                        else:
                            # 修复失败
                            error_msg = f"无法根据评估结果修复代码: {fix_result}"
                            print(f"[Gemini评估与修复] 错误: {error_msg}", flush=True)
                            return False, error_msg
                else:
                    # 评估失败
                    error_msg = f"代码评估失败: {eval_result}"
                    print(f"[Gemini评估与修复] 错误: {error_msg}", flush=True)
                    return False, error_msg

        # 达到最大迭代次数
        if current_code != original_code:
            # 生成最终版本文件名，包含迭代次数和请求计数
            final_version_file_name = f"{script_base}_v{iteration}_max_iterations{script_ext}"
            final_version_file_path = os.path.join(script_dir, final_version_file_name)

            # 保存当前代码到最终版本文件
            with open(final_version_file_path, 'w', encoding='utf-8') as f:
                f.write(current_code)

            # 同时保存到原始文件
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(current_code)

            changes_summary = "\n".join([f"- {change}" for change in all_changes])
            warning_msg = f"达到最大迭代次数 ({max_iterations})，保存最后一次修改的代码到 {script_path} 和 {final_version_file_name}\n修改摘要:\n{changes_summary}"

            print(f"[Gemini评估与修复] 警告: {warning_msg}", flush=True)
            return True, warning_msg
        else:
            # 代码没有变化
            warning_msg = f"达到最大迭代次数 ({max_iterations})，但代码没有变化"
            print(f"[Gemini评估与修复] 警告: {warning_msg}", flush=True)
            return False, warning_msg

    except Exception as e:
        error_msg = f"评估并修复脚本时出错: {e}"
        print(f"[Gemini评估与修复] 错误: {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)
        return False, error_msg


# 定义Blender操作符类
class SCRIPT_OT_evaluate_fix_gemini_code(bpy.types.Operator):
    bl_idname = "script.evaluate_fix_gemini_code"
    bl_label = "Agent 评估反思"
    bl_description = "Agent 评估生成的代码是否满足系统论、控制论、信息论的原则，以及链接和力学是否正常，并修复问题"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # 检查脚本文件是否存在
        return os.path.exists(get_script_path())

    # 允许通过属性设置最大迭代次数
    max_iterations: bpy.props.IntProperty(
        name="反思次数",
        description="Gemini反思/评估最大次数",
        default=5,
        min=1,
        max=20
    )

    def execute(self, context):
        print("\n[Gemini评估与修复] 执行评估并修复脚本操作", flush=True)

        # 在消息历史中添加开始评估的消息
        if hasattr(context.scene, "ai_assistant"):
            ai_props = context.scene.ai_assistant
            start_msg = ai_props.messages.add()
            start_msg.text = f"⚙️ Agent 正在评估代码是否满足系统论、控制论、信息论的原则，以及链接和力学是否正常... (最多{self.max_iterations}轮评估)"
            start_msg.is_user = False
            ai_props.active_message_index = len(ai_props.messages) - 1

            # 强制刷新所有面板，显示开始评估的消息
            for area in context.screen.areas:
                area.tag_redraw()

        # 新功能：如果用户在输入框中提供新的要求，则先调整脚本
        if hasattr(context.scene, "ai_assistant"):
            ai_props = context.scene.ai_assistant
            user_req = ai_props.message.strip()
            print(f"[Gemini预处理] 读取到用户要求: {user_req}", flush=True)
            if user_req:
                ai_props.message = ""
                script_path = get_script_path()
                try:
                    with open(script_path, 'r', encoding='utf-8') as f:
                        current_code = f.read()
                    prompt = f"请根据以下要求修改现有脚本：\n{user_req}\n\n现有脚本内容：\n{current_code}"
                    gen_success, gen_result = ai_gemini_integration.generate_blender_code(prompt)
                    if gen_success:
                        with open(script_path, 'w', encoding='utf-8') as f:
                            f.write(gen_result)
                        upd_msg = ai_props.messages.add()
                        upd_msg.text = f"🔄 根据用户要求修改脚本：{user_req}"
                        upd_msg.is_user = False
                        ai_props.active_message_index = len(ai_props.messages) - 1
                    else:
                        error_text = gen_result if isinstance(gen_result, str) else str(gen_result)
                        err_msg = ai_props.messages.add()
                        err_msg.text = f"❌ 修改脚本失败：{error_text}"
                        err_msg.is_user = False
                        return {'CANCELLED'}
                except Exception as e:
                    err_msg = ai_props.messages.add()
                    err_msg.text = f"❌ 修改脚本时出错：{e}"
                    err_msg.is_user = False
                    return {'CANCELLED'}

        # 执行评估并修复脚本操作
        success, message = evaluate_and_fix_code(max_iterations=self.max_iterations)

        if success:
            self.report({'INFO'}, message.split('\n')[0])  # 只报告第一行，避免消息过长

            # 在消息历史中添加成功消息
            if hasattr(context.scene, "ai_assistant"):
                ai_props = context.scene.ai_assistant
                msg = ai_props.messages.add()
                if "无需修改" in message:
                    msg.text = f"ℹ️ {message}"
                else:
                    msg.text = f"✅ {message}"
                msg.is_user = False
                ai_props.active_message_index = len(ai_props.messages) - 1

                # 如果有多行消息，添加详细信息
                if "\n" in message and "修改摘要" in message:
                    # 提取修改摘要部分
                    summary_start = message.find("修改摘要")
                    if summary_start > 0:
                        summary = message[summary_start:]
                        detail_msg = ai_props.messages.add()
                        detail_msg.text = f"ℹ️ {summary}"
                        detail_msg.is_user = False
                        ai_props.active_message_index = len(ai_props.messages) - 1
        else:
            self.report({'ERROR'}, message)

            # 在消息历史中添加错误消息
            if hasattr(context.scene, "ai_assistant"):
                ai_props = context.scene.ai_assistant
                msg = ai_props.messages.add()
                msg.text = f"❌ {message}"
                msg.is_user = False
                ai_props.active_message_index = len(ai_props.messages) - 1

            return {'CANCELLED'}

        # 强制刷新所有面板
        for area in context.screen.areas:
            area.tag_redraw()

        print("[Gemini评估与修复] 评估并修复脚本操作完成\n", flush=True)
        return {'FINISHED'}


# 注册和注销函数
def register():
    bpy.utils.register_class(SCRIPT_OT_evaluate_fix_gemini_code)
    print("[Gemini评估与修复] 已注册评估并修复Gemini脚本操作符")


def unregister():
    bpy.utils.unregister_class(SCRIPT_OT_evaluate_fix_gemini_code)
    print("[Gemini评估与修复] 已注销评估并修复Gemini脚本操作符")


if __name__ == "__main__":
    register()

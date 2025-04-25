"""
修复OpenAI生成的Blender Python脚本中的常见错误，并集成OpenAI多轮评估反思。
"""

import os
import re
import bpy
import traceback

# 导入OpenAI评估与修复模块
try:
    import openai_code_evaluator

    has_openai_evaluator = True
except ImportError:
    has_openai_evaluator = False
    print("警告: 无法导入openai_code_evaluator模块，评估修复功能将不可用", flush=True)


def get_script_path():
    """获取openai_latest_code.py文件的路径"""
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, "blender-git", "blender", "openai_latest_code.py")


# 通用修复函数（可扩展，现只做简单占位）
def fix_common_errors(code):
    # 可以在此添加正则修复等本地修复
    return code


# 多轮OpenAI反思修复主流程
def fix_script(max_rounds=5, user_extra_prompt=None):
    """
    反复请求OpenAI评估代码，自动修复，直到无错误或达到最大轮数。
    user_extra_prompt: 用户输入的额外需求，将合并进每一轮prompt。
    """
    if not has_openai_evaluator:
        print("[OpenAI修复] 缺少 openai_code_evaluator，无法自动修复。", flush=True)
        return False, "缺少openai_code_evaluator依赖"
    script_path = get_script_path()
    if not os.path.exists(script_path):
        return False, f"未找到脚本: {script_path}"
    with open(script_path, 'r', encoding='utf-8') as f:
        code = f.read()
    error_message = ""
    history = []
    # 新增：每轮读取Blender面板的最新需求
    def get_latest_user_prompt():
        try:
            import bpy
            scene = bpy.context.scene
            if hasattr(scene, "ai_assistant"):
                msg = scene.ai_assistant.message.strip()
                if msg:
                    return msg
        except Exception:
            pass
        return None
    for round_idx in range(1, max_rounds + 1):
        # 每轮都合并最新输入需求
        latest_prompt = get_latest_user_prompt()
        prompt_to_use = latest_prompt if latest_prompt else user_extra_prompt
        if latest_prompt:
            print(f"[OpenAI反思] 本轮读取的用户输入框内容: {latest_prompt}", flush=True)
        else:
            print(f"[OpenAI反思] 本轮未检测到新的用户输入，使用默认/上次需求。", flush=True)

        print(f"[OpenAI反思] 第{round_idx}轮评估...", flush=True)
        # 评估与修复（将最新需求合并进 error_message）
        if prompt_to_use:
            merged_error_message = f"{error_message}\n用户新需求: {prompt_to_use}" if error_message else f"用户新需求: {prompt_to_use}"
        else:
            merged_error_message = error_message
        success, result = openai_code_evaluator.evaluate_and_fix_code(code, merged_error_message)
        if not success:
            print(f"[OpenAI反思] 评估失败: {result}", flush=True)
            return False, result
        history.append({"round": round_idx, "code": code, "error": error_message, "result": result})
        # 解析评估结果，判断是否通过
        if "总体评估: 通过" in result or "总体评估：[通过]" in result:
            print("[OpenAI反思] 代码已通过评估，无需进一步修复。", flush=True)
            break
        # 提取修复后代码（简单策略：找最后一个完整代码块）
        new_code = code
        if '修复后的完整代码' in result:
            # 提取修复后代码块
            after = result.split('修复后的完整代码', 1)[-1]
            if '```python' in after:
                new_code = after.split('```python', 1)[-1].split('```', 1)[0].strip()
            elif '```' in after:
                new_code = after.split('```', 1)[-1].split('```', 1)[0].strip()
            else:
                # 兜底：取最后一段
                new_code = after.strip().split('\n')[-1]
        elif '```python' in result:
            new_code = result.split('```python', 1)[-1].split('```', 1)[0].strip()
        elif '```' in result:
            new_code = result.split('```', 1)[-1].split('```', 1)[0].strip()
        if prompt_to_use:
            # 用户新需求合并到代码注释（或prompt）
            new_code = f"# 用户需求: {prompt_to_use}\n" + new_code
        # 本地修复
        new_code = fix_common_errors(new_code)
        if not new_code.strip():
            print("[OpenAI反思] 反思修复后代码为空，未覆盖原脚本。", flush=True)
            return False, "反思修复后未能生成有效代码，请检查输入或修复流程。"
        # 保存新代码
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        code = new_code
        # 假设OpenAI每轮都会返回最新错误信息（可扩展）
        error_message = ""  # 这里可根据实际情况更新
    return True, history


# Blender面板操作符（可选，仿照fix_gemini_script实现）
import bpy


class SCRIPT_OT_fix_openai_code(bpy.types.Operator):
    bl_idname = "script.fix_openai_code"
    bl_label = "Agent 评估反思 (OpenAI)"
    bl_description = "Agent 使用OpenAI多轮评估并修复代码，确保可执行"
    bl_options = {'REGISTER', 'UNDO'}

    max_rounds: bpy.props.IntProperty(name="反思轮数", description="最多自动评估修复次数", default=5, min=1, max=20)
    user_extra_prompt: bpy.props.StringProperty(name="用户新需求", description="可选，额外补充的建模需求")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        ok, history = fix_script(
            max_rounds=self.max_rounds,
            user_extra_prompt=self.user_extra_prompt.strip() if self.user_extra_prompt else None,
        )
        if ok:
            self.report({'INFO'}, f"OpenAI反思修复完成，共{len(history)}轮")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"修复失败: {history}")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(SCRIPT_OT_fix_openai_code)


def unregister():
    bpy.utils.unregister_class(SCRIPT_OT_fix_openai_code)


if __name__ == "__main__":
    register()

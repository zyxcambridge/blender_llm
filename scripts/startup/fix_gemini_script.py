"""
修复Gemini生成的Blender Python脚本中的常见错误

这个脚本用于修复Gemini生成的Blender Python脚本中的常见错误，
特别是scale参数错误问题。
"""

import os
import re
import bpy
import traceback


def get_script_path():
    """获取gemini_latest_code.py文件的路径"""
    # 尝试从ai_gemini_integration模块获取保存目录
    try:
        import ai_gemini_integration

        save_dir = ai_gemini_integration.get_code_save_directory()
        if save_dir:
            # 从ai_gemini_integration模块获取脚本文件名
            if hasattr(ai_gemini_integration, 'SCRIPT_FILENAME'):
                script_filename = ai_gemini_integration.SCRIPT_FILENAME
            else:
                script_filename = "gemini_latest_code.py"
            return os.path.join(save_dir, script_filename)
    except ImportError:
        pass

    # 如果无法从ai_gemini_integration获取，则使用默认路径
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, "blender-git", "blender", "gemini_latest_code.py")


def fix_scale_parameter(code):
    """修复代码中的scale参数错误"""
    fixed_code = code
    changes_made = []

    # 1. 修复create_mouth函数中的scale参数错误
    def fix_create_mouth_scale(match):
        # 提取原始函数内容
        func_content = match.group(0)

        # 替换错误的scale参数
        fixed_content = re.sub(
            r'bpy\.ops\.mesh\.primitive_\w+_add\s*\([^)]*?scale\s*=\s*[^,)]+[^)]*\)',
            lambda m: re.sub(r'scale\s*=\s*[^,)]+', '', m.group(0)),
            func_content,
        )

        # 如果有变化，添加注释
        if fixed_content != func_content:
            fixed_content = fixed_content.replace("def create_mouth(", "# 修复: 移除了scale参数\ndef create_mouth(")
            changes_made.append("修复了create_mouth函数中的scale参数错误")
            print("[脚本修复] 修复了create_mouth函数中的scale参数错误", flush=True)

        return fixed_content

    # 使用正则表达式查找并修复create_mouth函数
    create_mouth_fixed = re.sub(
        r'def\s+create_mouth\s*\([^)]*\)\s*:[^\n]*(?:\n[^\n]*)*?\breturn\b[^\n]*',
        fix_create_mouth_scale,
        fixed_code,
        flags=re.DOTALL,
    )

    if create_mouth_fixed != fixed_code:
        fixed_code = create_mouth_fixed

    # 2. 修复所有函数中的scale参数错误
    scale_params_count = 0

    def fix_primitive_add_scale(match):
        nonlocal scale_params_count
        # 提取原始函数调用
        func_call = match.group(0)

        # 移除scale参数
        fixed_call = re.sub(r'\s*,?\s*scale\s*=\s*[^,)]+', '', func_call)

        if fixed_call != func_call:
            scale_params_count += 1
            # 提取函数名称以便日志输出
            func_name_match = re.search(r'bpy\.ops\.mesh\.([\w_]+)', func_call)
            if func_name_match:
                func_name = func_name_match.group(1)
                print(f"[脚本修复] 修复了{func_name}函数调用中的scale参数错误", flush=True)

        return fixed_call

    # 修复所有primitive_*_add函数调用中的scale参数
    all_primitives_fixed = re.sub(
        r'bpy\.ops\.mesh\.primitive_\w+_add\s*\([^)]*?scale\s*=\s*[^,)]+[^)]*\)', fix_primitive_add_scale, fixed_code
    )

    if all_primitives_fixed != fixed_code:
        fixed_code = all_primitives_fixed
        changes_made.append(f"修复了{scale_params_count}处primitive_*_add函数调用中的scale参数错误")
        print(f"[脚本修复] 总共修复了{scale_params_count}处primitive_*_add函数调用中的scale参数错误", flush=True)

    return fixed_code, changes_made


def fix_enter_editmode_parameter(code):
    """修复代码中的enter_editmode参数错误"""
    # 移除enter_editmode参数（支持换行）
    pattern = r'(bpy\.ops\.mesh\.[a-zA-Z0-9_]+_add\s*\([^\)]*?)\s*,?\s*enter_editmode\s*=\s*(?:True|False)\s*'
    matches = re.findall(pattern, code, re.DOTALL)
    if matches:
        print(f"[脚本修复] 发现{len(matches)}处enter_editmode参数错误", flush=True)
        for match in matches:
            func_name_match = re.search(r'bpy\.ops\.mesh\.([\w_]+)', match)
            if func_name_match:
                func_name = func_name_match.group(1)
                print(f"[脚本修复] 将从{func_name}中移除enter_editmode参数", flush=True)

    fixed_code = re.sub(
        pattern,
        r'\1',
        code,
        flags=re.DOTALL,
    )
    return fixed_code


def fix_align_parameter(code):
    """修复代码中的align参数错误"""
    # 移除align参数（保留合规位置用例）
    fixed_code = re.sub(
        r'(bpy\.ops\.mesh\.[a-zA-Z0-9_]+_add\s*\([^\)]*?)\s*,?\s*align\s*=\s*[\'"](?:WORLD|VIEW|CURSOR)[\'"]\s*',
        r'\1',
        code,
        flags=re.DOTALL,
    )
    return fixed_code


def fix_torus_parameters(code):
    """修复代码中的torus参数错误"""
    # 修复语法错误: bpy.ops.mesh.primitive_torus_add(,
    fixed_code = re.sub(r'bpy\.ops\.mesh\.primitive_torus_add\s*\(\s*,', 'bpy.ops.mesh.primitive_torus_add(', code)

    # 禁止错误混用radius和major_radius的调用
    fixed_code = re.sub(
        r'bpy\.ops\.mesh\.primitive_torus_add\s*\([^)]*radius\s*=\s*[^,\)]+,\s*major_radius\s*=\s*[^,\)]+[^)]*\)',
        '# 错误用法被屏蔽（禁止同时使用radius和major_radius）',
        fixed_code,
        flags=re.DOTALL,
    )

    # 修复torus参数，强制用major_radius/minor_radius替代radius/tube
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

    fixed_code = re.sub(
        r'bpy\.ops\.mesh\.primitive_torus_add\s*\([^)]*radius\s*=\s*[^,\)]+[^)]*tube\s*=\s*[^,\)]+[^)]*\)',
        replace_torus_params,
        fixed_code,
        flags=re.DOTALL,
    )

    return fixed_code


def fix_clip_end_parameter(code):
    """修复代码中的clip_end参数错误"""
    # 清理clip_end参数
    fixed_code = re.sub(r'clip_end\s*=\s*(?:True|False|\d+\.\d+|\d+)', '', code)
    return fixed_code


def fix_chinese_variables(code):
    """修复代码中的中文变量名"""
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

    fixed_code = code
    # 检测中文变量名并替换
    for pattern, replacement in chinese_var_patterns:
        if re.search(pattern, fixed_code):
            # 如果发现中文变量名，替换所有实例
            fixed_code = re.sub(pattern, replacement, fixed_code)
            print(f"[脚本修复] 已将中文变量名 '{pattern}' 替换为 '{replacement}'")

    return fixed_code


def fix_main_execution(code):
    """修复代码中的main函数执行方式"""
    fixed_code = code

    # 如果存在if __name__ == "__main__"结构，替换为正确的执行方式
    if "if __name__ == \"__main__\"" in fixed_code and "main()" in fixed_code:
        fixed_code = re.sub(
            r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:\s*\n\s*main\(\)',
            '# 使用bpy.app.timers.register而不是if __name__ == "__main__"\nbpy.app.timers.register(main)',
            fixed_code,
        )

    return fixed_code


def ensure_imports(code):
    """确保代码中包含必要的导入语句"""
    fixed_code = code

    # 确保导入bpy
    if 'import bpy' not in fixed_code:
        fixed_code = 'import bpy\n' + fixed_code

    # 确保导入bmesh（如果代码中使用了bmesh）
    if 'bmesh' in fixed_code and 'import bmesh' not in fixed_code:
        fixed_code = 'import bmesh\n' + fixed_code

    # 确保导入math（如果代码中使用了math函数）
    if (
        'math.sin' in fixed_code or 'math.cos' in fixed_code or 'math.pi' in fixed_code
    ) and 'import math' not in fixed_code:
        fixed_code = 'import math\n' + fixed_code

    return fixed_code


def add_log_function(code):
    """添加log函数（如果代码中使用了log函数但没有定义）"""
    fixed_code = code

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


def remove_duplicate_lines(code):
    """移除代码中的重复行"""
    lines = code.split('\n')
    fixed_lines = []
    prev_line = None
    for line in lines:
        if line.strip() and line != prev_line:
            fixed_lines.append(line)
        prev_line = line

    return '\n'.join(fixed_lines)


def fix_syntax_errors(code):
    """修复代码中的语法错误"""
    fixed_code = code
    changes_made = []

    # 1. 修复逗号后缺少参数的错误
    comma_errors = re.findall(r'\([\s,]*\)', fixed_code)
    if comma_errors:
        print(f"[脚本修复] 发现{len(comma_errors)}处逗号语法错误", flush=True)
        changes_made.append(f"修复了{len(comma_errors)}处逗号语法错误")

    # 修复空括号或只有逗号的括号
    fixed_code = re.sub(r'\([\s,]*\)', '()', fixed_code)

    # 2. 修复参数名后面缺少值的错误
    param_errors = re.findall(r'(\w+)\s*=\s*,', fixed_code)
    if param_errors:
        print(f"[脚本修复] 发现{len(param_errors)}处参数名后缺少值的错误", flush=True)
        for param in param_errors:
            print(f"[脚本修复] 修复参数 {param} 后缺少值的错误", flush=True)
        changes_made.append(f"修复了{len(param_errors)}处参数名后缺少值的错误")

    # 修复参数名后面缺少值的错误
    fixed_code = re.sub(r'(\w+)\s*=\s*,', r'\1=0,', fixed_code)

    # 3. 修复逗号后面缺少参数的错误
    trailing_comma_errors = re.findall(r',\s*\)', fixed_code)
    if trailing_comma_errors:
        print(f"[脚本修复] 发现{len(trailing_comma_errors)}处逗号后缺少参数的错误", flush=True)
        changes_made.append(f"修复了{len(trailing_comma_errors)}处逗号后缺少参数的错误")

    # 修复逗号后面缺少参数的错误
    fixed_code = re.sub(r',\s*\)', ')', fixed_code)

    # 4. 修复缺少右括号的错误
    # 这种错误很难自动修复，只能尝试检测并记录
    unbalanced_parens = 0
    for char in fixed_code:
        if char == '(':
            unbalanced_parens += 1
        elif char == ')':
            unbalanced_parens -= 1

    if unbalanced_parens > 0:
        print(f"[脚本修复] 警告: 发现{unbalanced_parens}个未配对的左括号，请手动检查", flush=True)
        changes_made.append(f"警告: 发现{unbalanced_parens}个未配对的左括号，请手动检查")

    return fixed_code, changes_made


def fix_script():
    """修复gemini_latest_code.py脚本中的常见错误"""
    script_path = get_script_path()

    print(f"\n[脚本修复] 开始修复脚本: {script_path}", flush=True)

    if not os.path.exists(script_path):
        error_msg = f"脚本文件不存在: {script_path}"
        print(f"[脚本修复] 错误: {error_msg}", flush=True)
        return False, error_msg

    try:
        # 读取脚本文件
        with open(script_path, 'r', encoding='utf-8') as f:
            script_code = f.read()

        print(f"[脚本修复] 成功读取脚本文件，大小: {len(script_code)} 字节", flush=True)

        # 初始化变量记录所有修改
        all_changes = []
        fixed_code = script_code

        # 首先修复语法错误，这是最重要的
        print("[脚本修复] 开始修复语法错误...", flush=True)
        fixed_code, syntax_changes = fix_syntax_errors(fixed_code)
        all_changes.extend(syntax_changes)

        # 应用所有修复
        print("[脚本修复] 开始修复scale参数错误...", flush=True)
        fixed_code, scale_changes = fix_scale_parameter(fixed_code)
        all_changes.extend(scale_changes)

        print("[脚本修复] 开始修夌enter_editmode参数...", flush=True)
        before = fixed_code
        fixed_code = fix_enter_editmode_parameter(fixed_code)
        if fixed_code != before:
            all_changes.append("修复了enter_editmode参数")
            print("[脚本修复] 修复了enter_editmode参数", flush=True)

        print("[脚本修复] 开始修复align参数...", flush=True)
        before = fixed_code
        fixed_code = fix_align_parameter(fixed_code)
        if fixed_code != before:
            all_changes.append("修复了align参数")
            print("[脚本修复] 修复了align参数", flush=True)

        print("[脚本修复] 开始修复torus参数...", flush=True)
        before = fixed_code
        fixed_code = fix_torus_parameters(fixed_code)
        if fixed_code != before:
            all_changes.append("修复了torus参数")
            print("[脚本修复] 修复了torus参数", flush=True)

        print("[脚本修复] 开始修复clip_end参数...", flush=True)
        before = fixed_code
        fixed_code = fix_clip_end_parameter(fixed_code)
        if fixed_code != before:
            all_changes.append("修复了clip_end参数")
            print("[脚本修复] 修复了clip_end参数", flush=True)

        print("[脚本修复] 开始修复中文变量名...", flush=True)
        before = fixed_code
        fixed_code = fix_chinese_variables(fixed_code)
        if fixed_code != before:
            all_changes.append("修复了中文变量名")
            print("[脚本修复] 修复了中文变量名", flush=True)

        print("[脚本修复] 开始修复main函数执行方式...", flush=True)
        before = fixed_code
        fixed_code = fix_main_execution(fixed_code)
        if fixed_code != before:
            all_changes.append("修复了main函数执行方式")
            print("[脚本修复] 修复了main函数执行方式", flush=True)

        print("[脚本修复] 开始确保必要的导入语句...", flush=True)
        before = fixed_code
        fixed_code = ensure_imports(fixed_code)
        if fixed_code != before:
            all_changes.append("添加了缺失的导入语句")
            print("[脚本修复] 添加了缺失的导入语句", flush=True)

        print("[脚本修复] 开始添加log函数...", flush=True)
        before = fixed_code
        fixed_code = add_log_function(fixed_code)
        if fixed_code != before:
            all_changes.append("添加了log函数")
            print("[脚本修复] 添加了log函数", flush=True)

        print("[脚本修复] 开始移除重复行...", flush=True)
        before = fixed_code
        fixed_code = remove_duplicate_lines(fixed_code)
        if fixed_code != before:
            all_changes.append("移除了重复行")
            print("[脚本修复] 移除了重复行", flush=True)

        # 如果代码有变化，则保存
        if fixed_code != script_code:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code)

            # 生成详细的修改摘要
            changes_summary = "\n".join([f"- {change}" for change in all_changes])
            success_msg = f"脚本已修复并保存到 {script_path}\n修改摘要:\n{changes_summary}"

            print(f"[脚本修复] 成功: {success_msg}", flush=True)
            return True, success_msg
        else:
            print("[脚本修复] 信息: 脚本检查完成，未发现需要修复的错误。", flush=True)
            return True, "脚本检查完成，未发现需要修复的错误。"

    except Exception as e:
        error_msg = f"修复脚本时出错: {e}"
        print(f"[脚本修复] 错误: {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)
        return False, error_msg


# 定义Blender操作符类
class SCRIPT_OT_fix_gemini_code(bpy.types.Operator):
    bl_idname = "script.fix_gemini_code"
    bl_label = "Agent 评估反思"
    bl_description = "Agent 评估生成的代码并修复常见错误，确保代码可执行"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # 检查脚本文件是否存在
        return os.path.exists(get_script_path())

    def execute(self, context):
        print("\n[脚本修复] 执行修复脚本操作符", flush=True)

        # 在消息历史中添加开始修复的消息
        if hasattr(context.scene, "ai_assistant"):
            ai_props = context.scene.ai_assistant
            start_msg = ai_props.messages.add()
            start_msg.text = "⚙️ Agent 正在评估代码并进行反思..."
            start_msg.is_user = False
            ai_props.active_message_index = len(ai_props.messages) - 1

            # 强制刷新所有面板，显示开始修复的消息
            for area in context.screen.areas:
                area.tag_redraw()

        # 执行修复脚本操作
        success, message = fix_script()

        if success:
            self.report({'INFO'}, message.split('\n')[0])  # 只报告第一行，避免消息过长

            # 在消息历史中添加成功消息
            if hasattr(context.scene, "ai_assistant"):
                ai_props = context.scene.ai_assistant
                msg = ai_props.messages.add()
                if "未发现" in message:
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

        print("[脚本修复] 修复脚本操作完成\n", flush=True)
        return {'FINISHED'}


# 注册和注销函数
def register():
    bpy.utils.register_class(SCRIPT_OT_fix_gemini_code)
    print("[脚本修复] 已注册修复Gemini脚本操作符")


def unregister():
    bpy.utils.unregister_class(SCRIPT_OT_fix_gemini_code)
    print("[脚本修复] 已注销修复Gemini脚本操作符")


if __name__ == "__main__":
    register()

"""
Blender OpenAI Integration - 延迟初始化，安全用于 Blender 插件。
"""

import base64

CODE_SAVE_DIR = ""


def get_openai_client():
    import os
    from openai import OpenAI

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("未检测到 GITHUB_TOKEN 环境变量，请在系统环境变量中设置你的 OpenAI/GitHub Token，或在 Blender 启动前导出变量。例如：export GITHUB_TOKEN=your_token")

    endpoint = os.environ.get("OPENAI_API_BASE", "https://models.github.ai/inference")
    # model = os.environ.get("OPENAI_MODEL", "openai/gpt-4.1")
    # model = os.environ.get("OPENAI_MODEL", "openai/gpt-4.1-mini")
    model = os.environ.get("OPENAI_MODEL", "openai/gpt-4o")
    client = OpenAI(base_url=endpoint, api_key=token)
    return client, model, token


def get_image_data_url(image_file: str, image_format: str) -> str:
    """
    Helper function to converts an image file to a data URL string.

    Args:
        image_file (str): The path to the image file.
        image_format (str): The format of the image file.

    Returns:
        str: The data URL of the image.
    """
    try:
        with open(image_file, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Could not read '{image_file}'.")
        exit()
    return f"data:image/{image_format};base64,{image_data}"


def generate_blender_code(prompt_text, image_file="0g.jpg"):
    client, model, token = get_openai_client()
    if not token:
        return False, "未配置 GITHUB_TOKEN 环境变量，无法访问 OpenAI API。"
    system_prompt = (
        "将以下自然语言描述转换为可在Blender 4.5中执行的Python代码。"
        "代码必须严格使用Blender 4.5 API（详见 https://docs.blender.org/api/current/ ），不得调用4.1及以前版本API。"
        "生成代码时请查询上述API文档，确保所有API和参数均为4.5版本可用。"
        "请务必规避以下Blender脚本开发常见错误：\n"
        "1. 不要使用 if __name__ == '__main__' 结构，主函数用 bpy.app.timers.register(main)。\n"
        "2. bpy.ops 操作需正确上下文，勿用不存在参数，执行前后切换正确模式。\n"
        "3. 合并对象前需先取消所有选择，手动选择目标对象并设置活动对象，再执行 bpy.ops.object.join()。\n"
        "4. primitive_torus_add 只能用如下参数：bpy.ops.mesh.primitive_torus_add(align='WORLD', location=(0,0,0), rotation=(0,0,0), major_radius=0.4, minor_radius=0.1)。绝对禁止使用 enter_editmode 字段或 radius 字段。\n"
        "5. bmesh 工作流必须规范，使用 bmesh.new(), bm.from_mesh(), bm.to_mesh(), mesh.update(), 并且最后 bm.free()，在编辑模式下用 from_edit_mesh/update_edit_mesh。避免 'Mesh' object has no attribute 'is_valid' 报错。\n"
        "6. 只允许Blender 4.5支持的参数和API。\n"
        "7. 添加日志输出以跟踪执行过程。\n"
        "8. 生成代码必须满足如下要求：\n"
        "- 必须创建至少一个可见的3D对象。\n"
        "- 必须为创建的对象设置合理的尺寸、位置和材质。\n"
        "- 力学原理检测：结构合理，重心、支撑无问题。\n"
        "- 物理原理检测：考虑物理特性。\n"
        "- 外观检测：美观、协调。\n"
        "- 结构检测：连接正确，功能部件位置恰当。\n"
        "- 只返回Python代码，不要包含解释或注释，代码可直接运行。\n"
        "9. 每次通过 nodes.get('Principled BSDF') 获取节点后，必须判断是否为 None。如果为 None，需自动 nodes.new(type='ShaderNodeBsdfPrincipled') 并设置 location，确保后续 .inputs[...] 操作不出错。\n"
        "10. 任何材质节点操作都必须保证节点存在，绝不能假定 nodes.get(...) 一定返回非 None。"
        "11. 禁止使用 bpy.app.timers.register 或类似定时器/异步方式生成模型，建模函数必须直接同步执行，确保 exec(code) 后模型已生成。"
        "12. 必须为所有主要模型对象设置材质和颜色，禁止无材质/无颜色输出。"
        "13. 必须为场景添加至少一个主光源（如SUN），并设置合适能量和颜色，禁止无光照。"
        "14. 必须保证生成的模型完整且对称，不能只生成一半身体。"
    )

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "理解图片中的内容，生成的模型要和图片类似",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": get_image_data_url(image_file, "jpg"), "detail": "low"},
                        },
                    ],
                },
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_text},
            ],
            temperature=0.3,
            top_p=1.0,
            model=model,
        )
        code = response.choices[0].message.content
        # 去除 markdown 格式
        if "```python" in code:
            code = code.split("```python", 1)[1].split("```", 1)[0].strip()
        elif "```" in code:
            code = code.split("```", 1)[1].split("```", 1)[0].strip()
        return True, code
    except Exception as e:
        return False, f"OpenAI API 调用失败: {e}"


def evaluate_and_fix_code(code, error_message):
    client, model, token = get_openai_client()
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
    # 其余与多轮反思、fix_openai_script相关的遗留内容已清理，仅保留必要的代码修复功能。
    user_prompt = f"错误信息：\n{error_message}\n当前代码：\n```python\n{code}\n```"
    try:
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.3,
            top_p=1.0,
            model=model,
        )
        content = response.choices[0].message.content
        return True, content
    except Exception as e:
        return False, f"OpenAI API 调用失败: {e}"


def set_code_save_directory(directory):
    global CODE_SAVE_DIR
    import os

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
    import os

    try:
        import bpy

        if CODE_SAVE_DIR:
            return os.path.abspath(CODE_SAVE_DIR)
        else:
            if bpy.data.filepath:
                return os.path.abspath(os.path.dirname(bpy.data.filepath))
            else:
                return os.path.abspath(os.getcwd())
    except Exception:
        return os.getcwd()


def execute_blender_code(code: str):
    import sys
    import traceback

    try:
        import bpy
    except Exception:
        print("[OpenAI Code Execution] 无法导入 bpy，跳过执行。", flush=True)
        return False, "无法导入 bpy，无法执行代码。"
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
    # 设置渲染引擎为 CYCLES（优先）或 EEVEE
    scene = bpy.context.scene
    if hasattr(scene.render, 'engine'):
        try:
            scene.render.engine = 'CYCLES'
            print("[OpenAI Code Execution] 渲染引擎设置为 CYCLES", flush=True)
        except Exception:
            scene.render.engine = 'BLENDER_EEVEE'
            print("[OpenAI Code Execution] 渲染引擎设置为 EEVEE", flush=True)
    # 尝试启用 GPU 渲染
    prefs = bpy.context.preferences
    if hasattr(prefs, 'addons') and 'cycles' in prefs.addons:
        cycles_prefs = prefs.addons['cycles'].preferences
        if hasattr(cycles_prefs, 'compute_device_type'):
            cycles_prefs.compute_device_type = 'CUDA' if 'CUDA' in cycles_prefs.devices else 'NONE'
            scene.cycles.device = 'GPU' if cycles_prefs.compute_device_type != 'NONE' else 'CPU'
            print(f"[OpenAI Code Execution] Cycles 设备: {scene.cycles.device}", flush=True)

    # 设置世界背景色为明亮灰色，避免黑屏
    if scene.world is not None:
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes.get('Background')
        if bg:
            bg.inputs[0].default_value = (0.8, 0.8, 0.8, 1)
            bg.inputs[1].default_value = 1.0
        print("[OpenAI Code Execution] 世界背景色已设置为亮灰色", flush=True)

    # 清除默认Cube
    if "Cube" in bpy.data.objects:
        try:
            bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
            print("[OpenAI Code Execution] 默认立方体已删除", flush=True)
        except Exception as e:
            print(f"[OpenAI Code Execution] 删除默认立方体失败: {e}", flush=True)
    # 清除所有摄像机和灯光，避免干扰
    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(obj, do_unlink=True)
    print("[OpenAI Code Execution] 已清除所有摄像机和灯光", flush=True)

    # 自动添加主摄像机并正对模型整体中心
    import mathutils

    mesh_objs = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    if mesh_objs:
        # 计算所有 mesh 的包围盒中心和高度
        min_z = min(
            [obj.matrix_world @ mathutils.Vector([v[0], v[1], v[2]]) for obj in mesh_objs for v in obj.bound_box],
            key=lambda v: v.z,
        ).z
        max_z = max(
            [obj.matrix_world @ mathutils.Vector([v[0], v[1], v[2]]) for obj in mesh_objs for v in obj.bound_box],
            key=lambda v: v.z,
        ).z
        center = sum((obj.location for obj in mesh_objs), mathutils.Vector((0, 0, 0))) / len(mesh_objs)
        model_height = max_z - min_z
        cam_dist = max(4, model_height * 2)
        cam_z = max_z - model_height / 2 + 0.5
        cam = bpy.data.cameras.new("AIAgent_Camera")
        cam_obj = bpy.data.objects.new("AIAgent_Camera", cam)
        bpy.context.collection.objects.link(cam_obj)
        cam_obj.location = (center.x, center.y - cam_dist, cam_z)
        direction = mathutils.Vector((center.x, center.y, cam_z)) - cam_obj.location
        cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        bpy.context.scene.camera = cam_obj
        print(
            f"[OpenAI Code Execution] 已自动对齐主摄像机，center=({center.x:.2f},{center.y:.2f},{cam_z:.2f}), dist={cam_dist:.2f}",
            flush=True,
        )
    else:
        cam = bpy.data.cameras.new("AIAgent_Camera")
        cam_obj = bpy.data.objects.new("AIAgent_Camera", cam)
        bpy.context.collection.objects.link(cam_obj)
        cam_obj.location = (0, -8, 2.5)
        cam_obj.rotation_euler = (1.2, 0, 0)
        bpy.context.scene.camera = cam_obj
        print("[OpenAI Code Execution] 已添加主摄像机", flush=True)

    # 自动添加主光源（太阳灯），放到模型正上方，并提高能量
    sun_data = bpy.data.lights.new(name="AIAgent_Sun", type='SUN')
    sun_data.energy = 15.0
    sun_data.color = (1.0, 0.95, 0.85)
    sun_obj = bpy.data.objects.new(name="AIAgent_Sun", object_data=sun_data)
    bpy.context.collection.objects.link(sun_obj)
    # 放到模型正上方
    if mesh_objs:
        min_z = min(
            [obj.matrix_world @ mathutils.Vector([v[0], v[1], v[2]]) for obj in mesh_objs for v in obj.bound_box],
            key=lambda v: v.z,
        ).z
        max_z = max(
            [obj.matrix_world @ mathutils.Vector([v[0], v[1], v[2]]) for obj in mesh_objs for v in obj.bound_box],
            key=lambda v: v.z,
        ).z
        center = sum((obj.location for obj in mesh_objs), mathutils.Vector((0, 0, 0))) / len(mesh_objs)
        sun_obj.location = (center.x, center.y, max_z + 3)
    else:
        sun_obj.location = (0, 0, 8)
    print(f"[OpenAI Code Execution] 已添加主光源，位置: {sun_obj.location}, 能量: {sun_data.energy}", flush=True)
    # 增加一个辅助点光源，放在模型正前方稍偏上
    if mesh_objs:
        point_data = bpy.data.lights.new(name="AIAgent_Fill", type='POINT')
        point_data.energy = 8.0
        point_data.color = (1.0, 1.0, 1.0)
        point_obj = bpy.data.objects.new(name="AIAgent_Fill", object_data=point_data)
        bpy.context.collection.objects.link(point_obj)
        point_obj.location = (
            center.x,
            center.y - (model_height if 'model_height' in locals() else 4),
            max_z - model_height / 3 + 1.0,
        )
        print(
            f"[OpenAI Code Execution] 已添加辅助点光源，位置: {point_obj.location}, 能量: {point_data.energy}",
            flush=True,
        )

    # 设置渲染分辨率
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.resolution_percentage = 100
    print("[OpenAI Code Execution] 渲染分辨率设置为1920x1080", flush=True)

    try:
        exec(code, globals())
        # 检查场景中是否有 MESH 对象，无则循环等待（最多2秒）
        import time

        for _ in range(10):
            mesh_objs = [obj for obj in bpy.data.objects if obj.type == "MESH"]
            if mesh_objs:
                break
            time.sleep(0.2)
        else:
            print("[OpenAI Code Execution] 警告：未检测到任何模型对象，渲染可能为空白！", flush=True)
        # 检查主要 mesh 是否有材质和颜色
        mesh_objs = [obj for obj in bpy.data.objects if obj.type == "MESH"]
        no_mat = [
            obj.name
            for obj in mesh_objs
            if not obj.data.materials or not any(mat and mat.use_nodes for mat in obj.data.materials)
        ]
        if no_mat:
            print(f"[OpenAI Code Execution] 警告：以下模型未设置材质或颜色，渲染可能无色: {no_mat}", flush=True)
        # 粗略检测模型是否对称（按名称/数量）
        left = [obj for obj in mesh_objs if "L" in obj.name or "Left" in obj.name or "_L" in obj.name]
        right = [obj for obj in mesh_objs if "R" in obj.name or "Right" in obj.name or "_R" in obj.name]
        if abs(len(left) - len(right)) > 1:
            print(f"[OpenAI Code Execution] 警告：模型左右部件数量不对称，可能只生成了一半身体！", flush=True)
        success = True
        result_message = "脚本执行成功完成。"
        print(f"[OpenAI Code Execution] {result_message}", flush=True)
    except IndentationError as e:
        success = False
        error_traceback = traceback.format_exc()
        result_message = f"❌ 脚本缩进错误: {e}\n请检查 AI 生成的代码缩进，尤其是 if/else 被注释后是否有多余缩进。\n详细信息:\n{error_traceback}"
        print(result_message, flush=True)
    except Exception as e:
        success = False
        error_traceback = traceback.format_exc()
        result_message = f"❌ 脚本执行失败:\n{error_traceback}"
        print(f"[OpenAI Code Execution] 发生运行时错误:", flush=True)
        print(error_traceback, flush=True)
    finally:
        print("--- [OpenAI Code Execution End] ---", flush=True)
    return success, result_message

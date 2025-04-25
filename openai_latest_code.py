import bpy
import math

def log(msg):
    print(f"[LOG] {msg}")

def main():
    character_name = "卡通小熊"
    objs = []

    # 头部（球体）
    log("创建头部")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 2.3))
    head = bpy.context.active_object
    head.name = character_name + "_Head"
    objs.append(head)

    # 头部材质
    mat_head = bpy.data.materials.new(name="Head_Mat")
    mat_head.use_nodes = True
    bsdf = mat_head.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.85, 0.65, 0.35, 1)
    head.data.materials.append(mat_head)

    # 耳朵（小球体）
    log("创建左耳朵")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(-0.65, 0, 3.1))
    ear_L = bpy.context.active_object
    ear_L.name = character_name + "_Ear_L"
    objs.append(ear_L)
    ear_L.data.materials.append(mat_head)

    log("创建右耳朵")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(0.65, 0, 3.1))
    ear_R = bpy.context.active_object
    ear_R.name = character_name + "_Ear_R"
    objs.append(ear_R)
    ear_R.data.materials.append(mat_head)

    # 眼睛（球体）
    log("创建左眼睛")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(-0.32, 0.85, 2.5))
    eye_L = bpy.context.active_object
    eye_L.name = character_name + "_Eye_L"
    objs.append(eye_L)
    mat_eye = bpy.data.materials.new(name="Eye_Mat")
    mat_eye.use_nodes = True
    bsdf_eye = mat_eye.node_tree.nodes.get("Principled BSDF")
    bsdf_eye.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1)
    eye_L.data.materials.append(mat_eye)

    log("创建右眼睛")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0.32, 0.85, 2.5))
    eye_R = bpy.context.active_object
    eye_R.name = character_name + "_Eye_R"
    objs.append(eye_R)
    eye_R.data.materials.append(mat_eye)

    # 嘴巴（甜甜圈）
    log("创建嘴巴")
    bpy.ops.mesh.primitive_torus_add(location=(0, 0.6, 2.05), major_radius=0.18, minor_radius=0.05, rotation=(math.radians(90), 0, 0))
    mouth = bpy.context.active_object
    mouth.name = character_name + "_Mouth"
    objs.append(mouth)
    mat_mouth = bpy.data.materials.new(name="Mouth_Mat")
    mat_mouth.use_nodes = True
    bsdf_mouth = mat_mouth.node_tree.nodes.get("Principled BSDF")
    bsdf_mouth.inputs["Base Color"].default_value = (0.9, 0.3, 0.3, 1)
    mouth.data.materials.append(mat_mouth)

    # 身体（球体，略小于头部）
    log("创建身体")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0, 0, 1.1), scale=(1, 0.9, 1.1))
    body = bpy.context.active_object
    body.name = character_name + "_Body"
    objs.append(body)
    body.data.materials.append(mat_head)

    # 手臂（细长圆柱体）
    log("创建左手臂")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=1.1, location=(-0.95, 0, 1.35), rotation=(0, 0, math.radians(25)))
    arm_L = bpy.context.active_object
    arm_L.name = character_name + "_Arm_L"
    objs.append(arm_L)
    arm_L.data.materials.append(mat_head)

    log("创建右手臂")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=1.1, location=(0.95, 0, 1.35), rotation=(0, 0, math.radians(-25)))
    arm_R = bpy.context.active_object
    arm_R.name = character_name + "_Arm_R"
    objs.append(arm_R)
    arm_R.data.materials.append(mat_head)

    # 腿部（较粗圆柱体）
    log("创建左腿")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.7, location=(-0.33, 0, 0.35))
    leg_L = bpy.context.active_object
    leg_L.name = character_name + "_Leg_L"
    objs.append(leg_L)
    leg_L.data.materials.append(mat_head)

    log("创建右腿")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.7, location=(0.33, 0, 0.35))
    leg_R = bpy.context.active_object
    leg_R.name = character_name + "_Leg_R"
    objs.append(leg_R)
    leg_R.data.materials.append(mat_head)

    # 配件：帽子（上半球）
    log("创建帽子")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(0, 0, 3.45), scale=(1.15, 1.15, 0.55))
    hat = bpy.context.active_object
    hat.name = character_name + "_Hat"
    # 删除下半球
    bpy.context.view_layer.objects.active = hat
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_less()  # 选中下半部分
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    mat_hat = bpy.data.materials.new(name="Hat_Mat")
    mat_hat.use_nodes = True
    bsdf_hat = mat_hat.node_tree.nodes.get("Principled BSDF")
    bsdf_hat.inputs["Base Color"].default_value = (0.2, 0.4, 0.8, 1)
    hat.data.materials.append(mat_hat)
    objs.append(hat)

    # 配件：背包（缩放立方体）
    log("创建背包")
    bpy.ops.mesh.primitive_cube_add(size=0.45, location=(0, -0.7, 1.1), scale=(0.6, 1, 1.2))
    backpack = bpy.context.active_object
    backpack.name = character_name + "_Backpack"
    mat_bag = bpy.data.materials.new(name="Backpack_Mat")
    mat_bag.use_nodes = True
    bsdf_bag = mat_bag.node_tree.nodes.get("Principled BSDF")
    bsdf_bag.inputs["Base Color"].default_value = (0.4, 0.8, 0.4, 1)
    backpack.data.materials.append(mat_bag)
    objs.append(backpack)

    # 合并所有部件
    log("合并所有部件")
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = head
    bpy.ops.object.join()
    merged = bpy.context.active_object
    merged.name = character_name

    log(f"角色「{character_name}」建模完成")

bpy.app.timers.register(main)
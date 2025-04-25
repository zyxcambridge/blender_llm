import bpy
import math

def log(msg):
    print(f"[LOG] {msg}")

def main():
    character_name = "卡通小兔"
    objs = []

    # 头部（球体）
    log("创建头部")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 2.5))
    head = bpy.context.active_object
    head.name = character_name + "_Head"
    objs.append(head)

    # 头部材质（淡粉色）
    mat_head = bpy.data.materials.new(name="Head_Mat")
    mat_head.use_nodes = True
    bsdf = mat_head.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.95, 0.85, 0.95, 1)
    bsdf.inputs["Roughness"].default_value = 0.45
    head.data.materials.append(mat_head)

    # 耳朵（细长椭球体，内外双色）
    log("创建左耳朵")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.23, location=(-0.45, 0, 3.6), scale=(0.5, 0.5, 2.2))
    ear_L = bpy.context.active_object
    ear_L.name = character_name + "_Ear_L"
    objs.append(ear_L)
    # 外耳材质
    ear_L.data.materials.append(mat_head)

    # 内耳（粉色）
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(-0.45, 0.01, 3.7), scale=(0.28, 0.28, 1.2))
    inner_ear_L = bpy.context.active_object
    inner_ear_L.name = character_name + "_Inner_Ear_L"
    mat_inner_ear = bpy.data.materials.new(name="Inner_Ear_Mat")
    mat_inner_ear.use_nodes = True
    bsdf_inner_ear = mat_inner_ear.node_tree.nodes.get("Principled BSDF")
    bsdf_inner_ear.inputs["Base Color"].default_value = (1.0, 0.7, 0.8, 1)
    bsdf_inner_ear.inputs["Roughness"].default_value = 0.45
    inner_ear_L.data.materials.append(mat_inner_ear)
    objs.append(inner_ear_L)

    log("创建右耳朵")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.23, location=(0.45, 0, 3.6), scale=(0.5, 0.5, 2.2))
    ear_R = bpy.context.active_object
    ear_R.name = character_name + "_Ear_R"
    objs.append(ear_R)
    ear_R.data.materials.append(mat_head)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0.45, 0.01, 3.7), scale=(0.28, 0.28, 1.2))
    inner_ear_R = bpy.context.active_object
    inner_ear_R.name = character_name + "_Inner_Ear_R"
    inner_ear_R.data.materials.append(mat_inner_ear)
    objs.append(inner_ear_R)

    # 眼睛（球体，黑色，带高光）
    log("创建左眼睛")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(-0.32, 0.85, 2.8))
    eye_L = bpy.context.active_object
    eye_L.name = character_name + "_Eye_L"
    objs.append(eye_L)
    mat_eye = bpy.data.materials.new(name="Eye_Mat")
    mat_eye.use_nodes = True
    bsdf_eye = mat_eye.node_tree.nodes.get("Principled BSDF")
    bsdf_eye.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1)
    bsdf_eye.inputs["Roughness"].default_value = 0.2
    eye_L.data.materials.append(mat_eye)

    # 眼睛高光
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(-0.36, 0.93, 2.86))
    eye_L_highlight = bpy.context.active_object
    eye_L_highlight.name = character_name + "_Eye_L_Highlight"
    mat_eye_highlight = bpy.data.materials.new(name="Eye_Highlight_Mat")
    mat_eye_highlight.use_nodes = True
    bsdf_eye_highlight = mat_eye_highlight.node_tree.nodes.get("Principled BSDF")
    bsdf_eye_highlight.inputs["Base Color"].default_value = (1, 1, 1, 1)
    bsdf_eye_highlight.inputs["Roughness"].default_value = 0.05
    eye_L_highlight.data.materials.append(mat_eye_highlight)
    objs.append(eye_L_highlight)

    log("创建右眼睛")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0.32, 0.85, 2.8))
    eye_R = bpy.context.active_object
    eye_R.name = character_name + "_Eye_R"
    objs.append(eye_R)
    eye_R.data.materials.append(mat_eye)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(0.36, 0.93, 2.86))
    eye_R_highlight = bpy.context.active_object
    eye_R_highlight.name = character_name + "_Eye_R_Highlight"
    eye_R_highlight.data.materials.append(mat_eye_highlight)
    objs.append(eye_R_highlight)

    # 嘴巴（甜甜圈，粉红色）
    log("创建嘴巴")
    bpy.ops.mesh.primitive_torus_add(location=(0, 0.6, 2.35), major_radius=0.13, minor_radius=0.035, rotation=(math.radians(90), 0, 0))
    mouth = bpy.context.active_object
    mouth.name = character_name + "_Mouth"
    objs.append(mouth)
    mat_mouth = bpy.data.materials.new(name="Mouth_Mat")
    mat_mouth.use_nodes = True
    bsdf_mouth = mat_mouth.node_tree.nodes.get("Principled BSDF")
    bsdf_mouth.inputs["Base Color"].default_value = (0.9, 0.4, 0.5, 1)
    bsdf_mouth.inputs["Roughness"].default_value = 0.35
    mouth.data.materials.append(mat_mouth)

    # 身体（椭球体，略小于头部，淡紫色）
    log("创建身体")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0, 0, 1.1), scale=(1, 0.9, 1.2))
    body = bpy.context.active_object
    body.name = character_name + "_Body"
    objs.append(body)
    mat_body = bpy.data.materials.new(name="Body_Mat")
    mat_body.use_nodes = True
    bsdf_body = mat_body.node_tree.nodes.get("Principled BSDF")
    bsdf_body.inputs["Base Color"].default_value = (0.88, 0.8, 0.95, 1)
    bsdf_body.inputs["Roughness"].default_value = 0.45
    body.data.materials.append(mat_body)

    # 手臂（细长圆柱体，淡紫色）
    log("创建左手臂")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=1.05, location=(-0.85, 0, 1.4), rotation=(0, 0, math.radians(25)))
    arm_L = bpy.context.active_object
    arm_L.name = character_name + "_Arm_L"
    objs.append(arm_L)
    arm_L.data.materials.append(mat_body)

    log("创建右手臂")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=1.05, location=(0.85, 0, 1.4), rotation=(0, 0, math.radians(-25)))
    arm_R = bpy.context.active_object
    arm_R.name = character_name + "_Arm_R"
    objs.append(arm_R)
    arm_R.data.materials.append(mat_body)

    # 腿部（较粗圆柱体，淡紫色）
    log("创建左腿")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.7, location=(-0.28, 0, 0.38))
    leg_L = bpy.context.active_object
    leg_L.name = character_name + "_Leg_L"
    objs.append(leg_L)
    leg_L.data.materials.append(mat_body)

    log("创建右腿")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.7, location=(0.28, 0, 0.38))
    leg_R = bpy.context.active_object
    leg_R.name = character_name + "_Leg_R"
    objs.append(leg_R)
    leg_R.data.materials.append(mat_body)

    # 配件：帽子（上半球，紫色）
    log("创建帽子")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.65, location=(0, 0, 3.9), scale=(1.2, 1.2, 0.55))
    hat = bpy.context.active_object
    hat.name = character_name + "_Hat"
    bpy.context.view_layer.objects.active = hat
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_less()
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    mat_hat = bpy.data.materials.new(name="Hat_Mat")
    mat_hat.use_nodes = True
    bsdf_hat = mat_hat.node_tree.nodes.get("Principled BSDF")
    bsdf_hat.inputs["Base Color"].default_value = (0.7, 0.5, 0.9, 1)
    bsdf_hat.inputs["Roughness"].default_value = 0.35
    hat.data.materials.append(mat_hat)
    objs.append(hat)

    # 帽檐（圆环，深紫色）
    bpy.ops.mesh.primitive_torus_add(location=(0, 0, 3.7), major_radius=0.78, minor_radius=0.07, rotation=(math.radians(90), 0, 0))
    hat_brim = bpy.context.active_object
    hat_brim.name = character_name + "_Hat_Brim"
    mat_hat_brim = bpy.data.materials.new(name="Hat_Brim_Mat")
    mat_hat_brim.use_nodes = True
    bsdf_hat_brim = mat_hat_brim.node_tree.nodes.get("Principled BSDF")
    bsdf_hat_brim.inputs["Base Color"].default_value = (0.4, 0.2, 0.6, 1)
    bsdf_hat_brim.inputs["Roughness"].default_value = 0.4
    hat_brim.data.materials.append(mat_hat_brim)
    objs.append(hat_brim)

    # 配件：尾巴（小球体，白色）
    log("创建尾巴")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0, -0.7, 1.0), scale=(1, 0.8, 1))
    tail = bpy.context.active_object
    tail.name = character_name + "_Tail"
    mat_tail = bpy.data.materials.new(name="Tail_Mat")
    mat_tail.use_nodes = True
    bsdf_tail = mat_tail.node_tree.nodes.get("Principled BSDF")
    bsdf_tail.inputs["Base Color"].default_value = (0.98, 0.98, 0.98, 1)
    bsdf_tail.inputs["Roughness"].default_value = 0.55
    tail.data.materials.append(mat_tail)
    objs.append(tail)

    # 配件：背包（缩放立方体，绿色）
    log("创建背包")
    bpy.ops.mesh.primitive_cube_add(size=0.38, location=(0, -0.6, 1.15), scale=(0.5, 1.1, 1.1))
    backpack = bpy.context.active_object
    backpack.name = character_name + "_Backpack"
    mat_bag = bpy.data.materials.new(name="Backpack_Mat")
    mat_bag.use_nodes = True
    bsdf_bag = mat_bag.node_tree.nodes.get("Principled BSDF")
    bsdf_bag.inputs["Base Color"].default_value = (0.4, 0.8, 0.4, 1)
    bsdf_bag.inputs["Roughness"].default_value = 0.5
    backpack.data.materials.append(mat_bag)
    objs.append(backpack)

    # 背包带（深绿色）
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.7, location=(-0.13, -0.4, 1.45), rotation=(math.radians(90), 0, math.radians(20)))
    strap_L = bpy.context.active_object
    strap_L.name = character_name + "_Backpack_Strap_L"
    mat_strap = bpy.data.materials.new(name="Backpack_Strap_Mat")
    mat_strap.use_nodes = True
    bsdf_strap = mat_strap.node_tree.nodes.get("Principled BSDF")
    bsdf_strap.inputs["Base Color"].default_value = (0.2, 0.5, 0.2, 1)
    bsdf_strap.inputs["Roughness"].default_value = 0.55
    strap_L.data.materials.append(mat_strap)
    objs.append(strap_L)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.7, location=(0.13, -0.4, 1.45), rotation=(math.radians(90), 0, math.radians(-20)))
    strap_R = bpy.context.active_object
    strap_R.name = character_name + "_Backpack_Strap_R"
    strap_R.data.materials.append(mat_strap)
    objs.append(strap_R)

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
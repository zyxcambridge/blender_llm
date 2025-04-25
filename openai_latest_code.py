import bpy
import math

角色名 = "卡通小熊"

def log(msg):
    print(f"[LOG] {msg}")

def create_cartoon_bear():
    bpy.ops.object.select_all(action='DESELECT')
    log("开始创建卡通角色：卡通小熊")
    objs = []

    # 头部：球体
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 2.5), segments=48, ring_count=32)
    head = bpy.context.active_object
    head.name = "Bear_Head"
    mat_head = bpy.data.materials.new(name="Head_Mat")
    mat_head.use_nodes = True
    bsdf_head = mat_head.node_tree.nodes.get("Principled BSDF")
    bsdf_head.inputs["Base Color"].default_value = (0.85, 0.65, 0.4, 1)
    bsdf_head.inputs["Roughness"].default_value = 0.45
    head.data.materials.append(mat_head)
    objs.append(head)
    log("头部完成")

    # 耳朵：两个小球体
    ear_offset_x = 0.8
    ear_offset_z = 3.5
    ear_radius = 0.35
    for i, sign in enumerate([-1, 1]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=ear_radius, location=(sign * ear_offset_x, 0, ear_offset_z), segments=32, ring_count=16)
        ear = bpy.context.active_object
        ear.name = f"Bear_Ear_{i+1}"
        mat_ear = bpy.data.materials.new(name=f"Ear_Mat_{i+1}")
        mat_ear.use_nodes = True
        bsdf_ear = mat_ear.node_tree.nodes.get("Principled BSDF")
        bsdf_ear.inputs["Base Color"].default_value = (0.85, 0.65, 0.4, 1)
        bsdf_ear.inputs["Roughness"].default_value = 0.5
        ear.data.materials.append(mat_ear)
        objs.append(ear)
    log("耳朵完成")

    # 眼睛：两个球体
    eye_offset_x = 0.38
    eye_offset_z = 2.7
    eye_offset_y = 0.85
    eye_radius = 0.16
    for i, sign in enumerate([-1, 1]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=eye_radius, location=(sign * eye_offset_x, eye_offset_y, eye_offset_z), segments=24, ring_count=12)
        eye = bpy.context.active_object
        eye.name = f"Bear_Eye_{i+1}"
        mat_eye = bpy.data.materials.new(name=f"Eye_Mat_{i+1}")
        mat_eye.use_nodes = True
        bsdf_eye = mat_eye.node_tree.nodes.get("Principled BSDF")
        bsdf_eye.inputs["Base Color"].default_value = (0.08, 0.08, 0.08, 1)
        bsdf_eye.inputs["Roughness"].default_value = 0.15
        eye.data.materials.append(mat_eye)
        objs.append(eye)
    log("眼睛完成")

    # 嘴巴：甜甜圈
    bpy.ops.mesh.primitive_torus_add(location=(0, 1.0, 2.2), major_radius=0.18, minor_radius=0.07, major_segments=32, minor_segments=16)
    mouth = bpy.context.active_object
    mouth.name = "Bear_Mouth"
    mat_mouth = bpy.data.materials.new(name="Mouth_Mat")
    mat_mouth.use_nodes = True
    bsdf_mouth = mat_mouth.node_tree.nodes.get("Principled BSDF")
    bsdf_mouth.inputs["Base Color"].default_value = (0.7, 0.3, 0.2, 1)
    bsdf_mouth.inputs["Roughness"].default_value = 0.25
    mouth.data.materials.append(mat_mouth)
    objs.append(mouth)
    log("嘴巴完成")

    # 身体：椭球体（球体缩放）
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.85, location=(0, 0, 1.1), segments=48, ring_count=32)
    body = bpy.context.active_object
    body.name = "Bear_Body"
    body.scale[2] = 1.25
    body.scale[0] = 0.95
    mat_body = bpy.data.materials.new(name="Body_Mat")
    mat_body.use_nodes = True
    bsdf_body = mat_body.node_tree.nodes.get("Principled BSDF")
    bsdf_body.inputs["Base Color"].default_value = (0.85, 0.65, 0.4, 1)
    bsdf_body.inputs["Roughness"].default_value = 0.5
    body.data.materials.append(mat_body)
    objs.append(body)
    log("身体完成")

    # 手臂：两个细长圆柱体
    arm_length = 1.0
    arm_radius = 0.13
    arm_offset_x = 0.95
    arm_offset_z = 1.5
    arm_offset_y = 0.0
    for i, sign in enumerate([-1, 1]):
        bpy.ops.mesh.primitive_cylinder_add(radius=arm_radius, depth=arm_length, location=(sign * arm_offset_x, arm_offset_y, arm_offset_z))
        arm = bpy.context.active_object
        arm.name = f"Bear_Arm_{i+1}"
        # 旋转手臂自然下垂
        arm.rotation_euler[1] = math.radians(25)
        arm.rotation_euler[0] = math.radians(0)
        mat_arm = bpy.data.materials.new(name=f"Arm_Mat_{i+1}")
        mat_arm.use_nodes = True
        bsdf_arm = mat_arm.node_tree.nodes.get("Principled BSDF")
        bsdf_arm.inputs["Base Color"].default_value = (0.85, 0.65, 0.4, 1)
        bsdf_arm.inputs["Roughness"].default_value = 0.5
        arm.data.materials.append(mat_arm)
        objs.append(arm)
    log("手臂完成")

    # 腿部：两个较粗圆柱体
    leg_length = 0.7
    leg_radius = 0.18
    leg_offset_x = 0.38
    leg_offset_z = 0.2
    for i, sign in enumerate([-1, 1]):
        bpy.ops.mesh.primitive_cylinder_add(radius=leg_radius, depth=leg_length, location=(sign * leg_offset_x, 0, leg_offset_z))
        leg = bpy.context.active_object
        leg.name = f"Bear_Leg_{i+1}"
        # 旋转腿部自然
        leg.rotation_euler[0] = math.radians(90)
        mat_leg = bpy.data.materials.new(name=f"Leg_Mat_{i+1}")
        mat_leg.use_nodes = True
        bsdf_leg = mat_leg.node_tree.nodes.get("Principled BSDF")
        bsdf_leg.inputs["Base Color"].default_value = (0.85, 0.65, 0.4, 1)
        bsdf_leg.inputs["Roughness"].default_value = 0.5
        leg.data.materials.append(mat_leg)
        objs.append(leg)
    log("腿部完成")

    # 配件1：帽子（上半球）
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(0, 0, 3.2), segments=32, ring_count=16)
    hat = bpy.context.active_object
    hat.name = "Bear_Hat"
    # 仅保留上半球
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    hat.scale[2] = 0.45
    mat_hat = bpy.data.materials.new(name="Hat_Mat")
    mat_hat.use_nodes = True
    bsdf_hat = mat_hat.node_tree.nodes.get("Principled BSDF")
    bsdf_hat.inputs["Base Color"].default_value = (0.3, 0.5, 0.8, 1)
    bsdf_hat.inputs["Roughness"].default_value = 0.35
    hat.data.materials.append(mat_hat)
    objs.append(hat)
    log("帽子完成")

    # 配件2：背包（缩放立方体）
    bpy.ops.mesh.primitive_cube_add(size=0.45, location=(0, -0.78, 1.1))
    backpack = bpy.context.active_object
    backpack.name = "Bear_Backpack"
    backpack.scale[0] = 0.6
    backpack.scale[2] = 1.0
    mat_bag = bpy.data.materials.new(name="Bag_Mat")
    mat_bag.use_nodes = True
    bsdf_bag = mat_bag.node_tree.nodes.get("Principled BSDF")
    bsdf_bag.inputs["Base Color"].default_value = (0.2, 0.7, 0.3, 1)
    bsdf_bag.inputs["Roughness"].default_value = 0.45
    backpack.data.materials.append(mat_bag)
    objs.append(backpack)
    log("背包完成")

    # 合并所有部件
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = head
    bpy.ops.object.join()
    merged = bpy.context.active_object
    merged.name = 角色名
    log(f"卡通角色「{角色名}」创建完成并已展示")

def main():
    create_cartoon_bear()

bpy.app.timers.register(main)
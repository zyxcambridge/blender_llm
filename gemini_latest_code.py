import bpy
import bmesh
import math

def log(message):
    print(f"Log: {message}")

def create_head(shape="球体"):
    log("创建头部")
    if shape == "球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, enter_editmode=False, align='WORLD', location=(0, 0, 0))
        head = bpy.context.object
        head.name = "Head"
        head.scale = (1.5, 1.5, 1.5)
        return head
    else:
        log(f"不支持的头部形状: {shape}")
        return None

def create_ear(shape="小球体", location=(0, 0, 0), rotation=(0, 0, 0)):
    log("创建耳朵")
    if shape == "小球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, enter_editmode=False, align='WORLD', location=location)
        ear = bpy.context.object
        ear.name = "Ear"
        ear.rotation_euler = rotation
        return ear
    else:
        log(f"不支持的耳朵形状: {shape}")
        return None

def create_eye(shape="球体", location=(0, 0, 0)):
    log("创建眼睛")
    if shape == "球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, enter_editmode=False, align='WORLD', location=location)
        eye = bpy.context.object
        eye.name = "Eye"
        return eye
    else:
        log(f"不支持的眼睛形状: {shape}")
        return None

def create_mouth(shape="甜甜圈", location=(0, 0, 0)):
    log("创建嘴巴")
    if shape == "甜甜圈":
        bpy.ops.mesh.primitive_torus_add(align='WORLD', location=location, major_radius=0.5, minor_radius=0.2)
        mouth = bpy.context.object
        mouth.name = "Mouth"
        mouth.rotation_euler[0] = math.radians(90)
        return mouth
    else:
        log(f"不支持的嘴巴形状: {shape}")
        return None

def create_arm(shape="细长圆柱体", location=(0, 0, 0), rotation=(0, 0, 0)):
    log("创建手臂")
    if shape == "细长圆柱体":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.0, enter_editmode=False, align='WORLD', location=location)
        arm = bpy.context.object
        arm.name = "Arm"
        arm.rotation_euler = rotation
        return arm
    else:
        log(f"不支持的手臂形状: {shape}")
        return None

def create_leg(shape="较粗圆柱体", location=(0, 0, 0), rotation=(0, 0, 0)):
    log("创建腿部")
    if shape == "较粗圆柱体":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.2, enter_editmode=False, align='WORLD', location=location)
        leg = bpy.context.object
        leg = bpy.context.object
        leg.name = "Leg"
        leg.rotation_euler = rotation
        return leg
    else:
        log(f"不支持的腿部形状: {shape}")
        return None

def create_backpack():
    log("创建背包")
    bpy.ops.mesh.primitive_cube_add(size=0.6, enter_editmode=False, align='WORLD', location=(0.2, -1.0, 0.5))
    backpack = bpy.context.object
    backpack.name = "Backpack"
    backpack.scale = (1.0, 0.5, 1.0)
    return backpack

def create_hat():
    log("创建帽子")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, enter_editmode=False, align='WORLD', location=(0, 0, 2.0))
    hat = bpy.context.object
    hat.name = "Hat"
    hat.scale = (1.0, 1.0, 0.3)
    return hat

def check_mechanics(objects):
    log("检查力学原理")
    # 简单示例：检查重心是否大致位于底部
    if objects:
        total_z = sum(obj.location.z for obj in objects)
        average_z = total_z / len(objects)
        if average_z < 0.5:
            log("警告：重心可能过低，稳定性可能不足。")
        else:
            log("力学原理检查通过（初步）。")
    else:
        log("没有对象可供力学原理检查。")

def check_physics(objects):
    log("检查物理原理")
    # 简单示例：检查是否有封闭的几何体
    has_closed_geometry = False
    for obj in objects:
        if obj.type == 'MESH':
            mesh = obj.data
            if mesh.is_valid:
                bm = bmesh.new()
                bm.from_mesh(mesh)
                if bm.is_manifold:
                    has_closed_geometry = True
                    break
                bm.free()
    if has_closed_geometry:
        log("物理原理检查通过（初步）。存在封闭几何体。")
    else:
        log("警告：物理原理检查失败。可能没有封闭几何体。")

def check_appearance(objects):
    log("检查外观")
    # 简单示例：检查部件比例是否合理
    head = next((obj for obj in objects if obj.name == "Head"), None)
    if head:
        if head.scale[0] < 1.0 or head.scale[0] > 2.0:
            log("警告：头部比例可能不合理。")
        else:
            log("外观检查通过（初步）。")
    else:
        log("没有找到头部对象，无法进行外观检查。")

def check_structure(objects):
    log("检查结构")
    # 简单示例：检查耳朵是否连接到头部
    head = next((obj for obj in objects if obj.name == "Head"), None)
    ears = [obj for obj in objects if obj.name == "Ear"]
    if head and ears:
        for ear in ears:
            if abs(ear.location.z - head.location.z) < 2.0:
                log("结构检查通过（初步）。耳朵位置合理。")
                break
        else:
            log("警告：耳朵位置可能不合理。")
    else:
        log("没有找到头部或耳朵对象，无法进行结构检查。")

def main():
    log("开始创建卡通角色")

    # 创建头部
    head = create_head()

    # 创建耳朵
    ear_left = create_ear(location=(0.8, 0.5, 1.5), rotation=(0, 0, 0))
    ear_right = create_ear(location=(-0.8, 0.5, 1.5), rotation=(0, 0, 0))

    # 创建眼睛
    eye_left = create_eye(location=(0.5, -1.0, 1.0))
    eye_right = create_eye(location=(-0.5, -1.0, 1.0))

    # 创建嘴巴
    mouth = create_mouth(location=(0, -1.0, 0.5))

    # 创建手臂
    arm_left = create_arm(location=(1.5, 0, 0.5), rotation=(0, 0, 1.57))
    arm_right = create_arm(location=(-1.5, 0, 0.5), rotation=(0, 0, -1.57))

    # 创建腿部
    leg_left = create_leg(location=(0.5, 0, -1.0), rotation=(0, 0, 0))
    leg_right = create_leg(location=(-0.5, 0, -1.0), rotation=(0, 0, 0))

    # 创建背包
    backpack = create_backpack()

    # 创建帽子
    hat = create_hat()

    # 收集所有创建的对象
    objects_to_join = [obj for obj in bpy.data.objects if obj.name in ("Head", "Ear", "Eye", "Mouth", "Arm", "Leg", "Backpack", "Hat")]

    # 合并对象
    if objects_to_join:
        log("合并对象")
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects_to_join:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
        bpy.ops.object.join()
        bpy.context.object.name = "CartoonCharacter"
    else:
        log("没有对象可以合并。")

    # 执行检查
    all_objects = [obj for obj in bpy.data.objects if obj.name == "CartoonCharacter"]
    check_mechanics(all_objects)
    check_physics(all_objects)
    check_appearance(all_objects)
    check_structure(all_objects)

    log("卡通角色创建完成")

bpy.app.timers.register(main)
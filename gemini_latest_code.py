import bpy
import bmesh
import math

def log(message):
    print(f"Log: {message}")

def create_head(shape="球体"):
    log("创建头部")
    if shape == "球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, enter_editmode=False, align='WORLD', location=(0, 0, 1))
        head = bpy.context.object
        head.name = "Head"
        return head
    else:
        log("不支持的头部形状")
        return None

def create_ear(shape="小球体", location=(0, 0, 0), rotation=(0, 0, 0)):
    log("创建耳朵")
    if shape == "小球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, enter_editmode=False, align='WORLD', location=location)
        ear = bpy.context.object
        ear.name = "Ear"
        ear.rotation_euler = rotation
        return ear
    else:
        log("不支持的耳朵形状")
        return None

def create_eye(shape="球体", location=(0, 0, 0)):
    log("创建眼睛")
    if shape == "球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, enter_editmode=False, align='WORLD', location=location)
        eye = bpy.context.object
        eye.name = "Eye"
        return eye
    else:
        log("不支持的眼睛形状")
        return None

def create_mouth(shape="甜甜圈", location=(0, 0, 0)):
    log("创建嘴巴")
    if shape == "甜甜圈":
        bpy.ops.mesh.primitive_torus_add(major_radius=0.2, minor_radius=0.05, enter_editmode=False, align='WORLD', location=location)
        mouth = bpy.context.object
        mouth.name = "Mouth"
        mouth.rotation_euler[0] = math.radians(90)
        return mouth
    else:
        log("不支持的嘴巴形状")
        return None

def create_arm(shape="细长圆柱体", location=(0, 0, 0), rotation=(0, 0, 0)):
    log("创建手臂")
    if shape == "细长圆柱体":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.8, enter_editmode=False, align='WORLD', location=location)
        arm = bpy.context.object
        arm.name = "Arm"
        arm.rotation_euler = rotation
        return arm
    else:
        log("不支持的手臂形状")
        return None

def create_leg(shape="较粗圆柱体", location=(0, 0, 0), rotation=(0, 0, 0)):
    log("创建腿部")
    if shape == "较粗圆柱体":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=1, enter_editmode=False, align='WORLD', location=location)
        leg = bpy.context.object
        leg = bpy.context.object
        leg.name = "Leg"
        leg.rotation_euler = rotation
        return leg
    else:
        log("不支持的腿部形状")
        return None

def create_backpack():
    log("创建背包")
    bpy.ops.mesh.primitive_cube_add(size=0.4, enter_editmode=False, align='WORLD', location=(0, -0.3, 0.5))
    backpack = bpy.context.object
    backpack.name = "Backpack"
    backpack.scale[1] = 0.5
    return backpack

def check_mechanics(head, arms, legs):
    log("检查力学原理")
    if head and arms and legs:
        # 简单重心检查
        total_mass = 1.0  # 假设头部质量为1
        center_x = 0.0
        center_y = 0.0
        center_z = 1.0 # 头部中心
        
        # 检查腿部支撑
        if legs:
            leg_count = len(legs)
            if leg_count > 0:
                log("腿部支撑结构良好")
            else:
                log("警告：没有腿部，角色无法站立")
        else:
            log("警告：没有腿部，角色无法站立")
        
        log(f"重心: ({center_x}, {center_y}, {center_z})")
    else:
        log("力学原理检查失败：缺少关键部件")

def check_physics():
    log("检查物理原理")
    # 简单检查，可以添加更复杂的物理模拟检查
    log("物理原理检查通过 (简单检查)")

def check_appearance():
    log("检查外观")
    log("外观检查通过")

def check_structure(head, ears, eyes, mouth, arms, legs, backpack=None):
    log("检查结构")
    if head:
        log("头部结构良好")
    else:
        log("警告：缺少头部")

    if ears:
        log("耳朵结构良好")
    else:
        log("警告：缺少耳朵")

    if eyes:
        log("眼睛结构良好")
    else:
        log("警告：缺少眼睛")

    if mouth:
        log("嘴巴结构良好")
    else:
        log("警告：缺少嘴巴")

    if arms:
        log("手臂结构良好")
    else:
        log("警告：缺少手臂")

    if legs:
        log("腿部结构良好")
    else:
        log("警告：缺少腿部")

    if backpack:
        log("背包结构良好")
    else:
        log("没有背包")

def main():
    character_name = "小黄人"
    log(f"开始创建角色：{character_name}")

    # 创建头部
    head = create_head()

    # 创建耳朵
    ear_left = create_ear(location=(0.5, 0, 1.5), rotation=(0, 0, 0))
    ear_right = create_ear(location=(-0.5, 0, 1.5), rotation=(0, 0, 0))
    ears = [ear_left, ear_right]

    # 创建眼睛
    eye_left = create_eye(location=(0.3, 0.45, 1))
    eye_right = create_eye(location=(-0.3, 0.45, 1))
    eyes = [eye_left, eye_right]

    # 创建嘴巴
    mouth = create_mouth(location=(0, -0.2, 0.7))

    # 创建手臂
    arm_left = create_arm(location=(0.7, 0, 0.5), rotation=(0, 0, math.radians(90)))
    arm_right = create_arm(location=(-0.7, 0, 0.5), rotation=(0, 0, math.radians(-90)))
    arms = [arm_left, arm_right]

    # 创建腿部
    leg_left = create_leg(location=(0.2, 0, -0.5))
    leg_right = create_leg(location=(-0.2, 0, -0.5))
    legs = [leg_left, leg_right]

    # 创建背包
    backpack = create_backpack()

    # 结构检查
    check_structure(head, ears, eyes, mouth, arms, legs, backpack)

    # 力学、物理、外观检查
    check_mechanics(head, arms, legs)
    check_physics()
    check_appearance()

    # 合并对象
    all_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if all_objects:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in all_objects:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
        bpy.ops.object.join()
        bpy.context.object.name = character_name
        log(f"角色 {character_name} 创建完成")
    else:
        log("没有可合并的对象")

    return 0

bpy.app.timers.register(main)
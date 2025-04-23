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
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.8, enter_editmode=False, align='WORLD', location=location)
        leg = bpy.context.object
        leg.name = "Leg"
        leg.rotation_euler = rotation
        return leg
    else:
        log("不支持的腿部形状")
        return None

def create_backpack():
    log("创建背包")
    bpy.ops.mesh.primitive_cube_add(size=0.3, enter_editmode=False, align='WORLD', location=(0, -0.3, 0.5))
    backpack = bpy.context.object
    backpack.name = "Backpack"
    backpack.scale[1] = 0.5
    return backpack

def check_mechanics(head, arms, legs):
    log("检查力学原理")
    if head and arms and legs:
        # 简单检查：重心是否在支撑范围内
        head_location = head.location
        leg1_location = legs[0].location
        leg2_location = legs[1].location

        if leg1_location[0] <= head_location[0] <= leg2_location[0] or leg2_location[0] <= head_location[0] <= leg1_location[0]:
            log("力学原理检查通过：重心在支撑范围内")
        else:
            log("力学原理检查失败：重心不在支撑范围内")

        # 简单检查：手臂和腿部连接是否合理
        if arms[0].location[2] < head_location[2] and arms[1].location[2] < head_location[2]:
            log("力学原理检查通过：手臂位置合理")
        else:
            log("力学原理检查失败：手臂位置不合理")

        if legs[0].location[2] < head_location[2] and legs[1].location[2] < head_location[2]:
            log("力学原理检查通过：腿部位置合理")
        else:
            log("力学原理检查失败：腿部位置不合理")
    else:
        log("力学原理检查失败：缺少关键部件")

def check_physics(head, mouth):
    log("检查物理原理")
    if head and mouth:
        # 简单检查：嘴巴是否在头部内
        if head.location[2] > mouth.location[2]:
            log("物理原理检查通过：嘴巴位置合理")
        else:
            log("物理原理检查失败：嘴巴位置不合理")
    else:
        log("物理原理检查失败：缺少关键部件")

def check_appearance(head, ears, eyes, mouth, arms, legs, backpack=None):
    log("检查外观")
    if head and ears and eyes and mouth and arms and legs:
        log("外观检查通过：基本部件存在")
        # 简单检查：眼睛对称
        if abs(eyes[0].location[0] + eyes[1].location[0]) < 0.01:
            log("外观检查通过：眼睛对称")
        else:
            log("外观检查失败：眼睛不对称")
    else:
        log("外观检查失败：缺少关键部件")

def check_structure(head, ears, eyes, mouth, arms, legs, backpack=None):
    log("检查结构")
    if head and ears and eyes and mouth and arms and legs:
        log("结构检查通过：基本部件存在")
        # 简单检查：耳朵在头部上方
        if ears[0].location[2] > head.location[2] and ears[1].location[2] > head.location[2]:
            log("结构检查通过：耳朵位置合理")
        else:
            log("结构检查失败：耳朵位置不合理")
    else:
        log("结构检查失败：缺少关键部件")

def main():
    character_name = "MyCharacter"
    log(f"开始创建角色：{character_name}")

    # 创建头部
    head = create_head()

    # 创建耳朵
    ear1 = create_ear(location=(0.5, 0, 1.2))
    ear2 = create_ear(location=(-0.5, 0, 1.2))
    ears = [ear1, ear2]

    # 创建眼睛
    eye1 = create_eye(location=(0.2, 0.4, 1))
    eye2 = create_eye(location=(-0.2, 0.4, 1))
    eyes = [eye1, eye2]

    # 创建嘴巴
    mouth = create_mouth(location=(0, 0.4, 0.7))

    # 创建手臂
    arm1 = create_arm(location=(0.8, 0, 0.5), rotation=(0, 0, math.radians(90)))
    arm2 = create_arm(location=(-0.8, 0, 0.5), rotation=(0, 0, math.radians(-90)))
    arms = [arm1, arm2]

    # 创建腿部
    leg1 = create_leg(location=(0.3, 0, -0.5), rotation=(0, 0, 0))
    leg2 = create_leg(location=(-0.3, 0, -0.5), rotation=(0, 0, 0))
    legs = [leg1, leg2]

    # 创建背包
    backpack = create_backpack()

    # 调整位置和比例
    if head:
        head.scale = (1, 1, 1)
    if ear1:
        ear1.location[1] = 0.2
    if ear2:
        ear2.location[1] = 0.2
    if arm1:
        arm1.location[1] = 0.4
    if arm2:
        arm2.location[1] = 0.4
    if leg1:
        leg1.location[1] = 0.2
    if leg2:
        leg2.location[1] = 0.2

    # 合并对象
    all_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.name != "Camera" and obj.name != "Light"]
    if all_objects:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in all_objects:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
        bpy.ops.object.join()
        bpy.context.object.name = character_name
        log(f"角色 {character_name} 创建完成")

    # 运行检测
    check_mechanics(head, arms, legs)
    check_physics(head, mouth)
    check_appearance(head, ears, eyes, mouth, arms, legs, backpack)
    check_structure(head, ears, eyes, mouth, arms, legs, backpack)

    log("脚本执行完毕")

bpy.app.timers.register(main)
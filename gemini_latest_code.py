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
    else:
        log(f"不支持的头部形状: {shape}")
        return None
    return head

def create_ear(shape="小球体", location=(0,0,0), rotation=(0,0,0)):
    log("创建耳朵")
    if shape == "小球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, enter_editmode=False, align='WORLD', location=location)
        ear = bpy.context.object
        ear.name = "Ear"
        ear.rotation_euler = rotation
    else:
        log(f"不支持的耳朵形状: {shape}")
        return None
    return ear

def create_eye(shape="球体", location=(0,0,0)):
    log("创建眼睛")
    if shape == "球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, enter_editmode=False, align='WORLD', location=location)
        eye = bpy.context.object
        eye.name = "Eye"
    else:
        log(f"不支持的眼睛形状: {shape}")
        return None
    return eye

def create_mouth(shape="甜甜圈"):
    log("创建嘴巴")
    if shape == "甜甜圈":
        bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.2, enter_editmode=False, align='WORLD', location=(0, -0.5, -0.5))
        mouth = bpy.context.object
        mouth.name = "Mouth"
        mouth.rotation_euler = (math.radians(90), 0, 0)
    else:
        log(f"不支持的嘴巴形状: {shape}")
        return None
    return mouth

def create_arm(shape="细长圆柱体", location=(0,0,0), rotation=(0,0,0)):
    log("创建手臂")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.0, enter_editmode=False, align='WORLD', location=location)
    arm = bpy.context.object
    arm.name = "Arm"
    arm.rotation_euler = rotation
    return arm

def create_leg(shape="较粗圆柱体", location=(0,0,0)):
    log("创建腿部")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.2, enter_editmode=False, align='WORLD', location=location)
    leg = bpy.context.object
    leg.name = "Leg"
    return leg

def create_backpack():
    log("创建背包")
    bpy.ops.mesh.primitive_cube_add(size=0.6, enter_editmode=False, align='WORLD', location=(0, -0.5, 0.5))
    backpack = bpy.context.object
    backpack.name = "Backpack"
    backpack.scale = (1.2, 0.8, 0.4)
    return backpack

def check_model():
    log("开始模型检测")
    # 简单检测示例
    head = bpy.data.objects.get("Head")
    if head is None:
        log("检测失败：头部未创建")
        return False
    log("检测通过：头部存在")

    # 力学原理检测 (简化示例)
    if bpy.data.objects.get("Leg") is not None:
        log("检测通过：腿部存在，初步符合支撑结构")
    else:
        log("检测失败：腿部缺失，不符合支撑结构")
        return False

    # 外观检测 (简化示例)
    if bpy.data.objects.get("Mouth") is not None:
        log("检测通过：嘴巴存在，外观协调")
    else:
        log("检测失败：嘴巴缺失，外观不协调")
        return False

    log("模型检测完成，通过")
    return True

def main():
    log("开始创建卡通角色")
    head = create_head("球体")
    if head is None:
        log("创建头部失败，停止创建")
        return

    ear_left = create_ear("小球体", location=(1.2, 0.8, 1.8), rotation=(0, 0, math.radians(30)))
    ear_right = create_ear("小球体", location=(-1.2, 0.8, 1.8), rotation=(0, 0, math.radians(-30)))

    eye_left = create_eye("球体", location=(0.6, 1.2, 0.5))
    eye_right = create_eye("球体", location=(-0.6, 1.2, 0.5))

    mouth = create_mouth("甜甜圈")

    arm_left = create_arm("细长圆柱体", location=(1.8, 0, 0.5), rotation=(0, 0, math.radians(90)))
    arm_right = create_arm("细长圆柱体", location=(-1.8, 0, 0.5), rotation=(0, 0, math.radians(-90)))

    leg_left = create_leg("较粗圆柱体", location=(0.6, 0, -1.5))
    leg_right = create_leg("较粗圆柱体", location=(-0.6, 0, -1.5))

    backpack = create_backpack()

    # 合并对象
    objects_to_join = [obj for obj in bpy.data.objects if obj.name in ["Head", "Ear", "Eye", "Mouth", "Arm", "Leg", "Backpack"]]
    if objects_to_join:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects_to_join:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
        bpy.ops.object.join()
        bpy.context.active_object.name = "CartoonCharacter"
        log("角色创建完成并合并")
    else:
        log("没有可合并的对象")

    if check_model():
        log("模型创建成功")
    else:
        log("模型创建失败")

bpy.app.timers.register(main)
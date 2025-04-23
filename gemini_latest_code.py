import bpy
import bmesh
import math

def log(message):
    print(f"Log: {message}")

def create_head(head_shape="球体"):
    log("创建头部")
    if head_shape == "球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, enter_editmode=False, align='WORLD', location=(0, 0, 2))
        head = bpy.context.object
        head.name = "头部"
        return head
    else:
        log("不支持的头部形状")
        return None

def create_ear(ear_shape="小球体", location=(0,0,0), rotation=(0,0,0)):
    log("创建耳朵")
    if ear_shape == "小球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, enter_editmode=False, align='WORLD', location=location)
        ear = bpy.context.object
        ear.name = "耳朵"
        ear.rotation_euler = rotation
        return ear
    else:
        log("不支持的耳朵形状")
        return None

def create_eye(eye_shape="球体", location=(0,0,0)):
    log("创建眼睛")
    if eye_shape == "球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, enter_editmode=False, align='WORLD', location=location)
        eye = bpy.context.object
        eye.name = "眼睛"
        return eye
    else:
        log("不支持的眼睛形状")
        return None

def create_mouth(mouth_shape="甜甜圈"):
    log("创建嘴巴")
    if mouth_shape == "甜甜圈":
        bpy.ops.mesh.primitive_torus_add(radius=0.4, major_radius=0.6, enter_editmode=False, align='WORLD', location=(0, 0, 1.2))
        mouth = bpy.context.object
        mouth.name = "嘴巴"
        mouth.rotation_euler[0] = math.radians(90)
        return mouth
    else:
        log("不支持的嘴巴形状")
        return None

def create_arm(arm_shape="细长圆柱体", location=(0,0,0), rotation=(0,0,0)):
    log("创建手臂")
    if arm_shape == "细长圆柱体":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1.0, enter_editmode=False, align='WORLD', location=location)
        arm = bpy.context.object
        arm.name = "手臂"
        arm.rotation_euler = rotation
        return arm
    else:
        log("不支持的手臂形状")
        return None

def create_leg(leg_shape="较粗圆柱体", location=(0,0,0), rotation=(0,0,0)):
    log("创建腿部")
    if leg_shape == "较粗圆柱体":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.0, enter_editmode=False, align='WORLD', location=location)
        leg = bpy.context.object
        leg.name = "腿部"
        leg.rotation_euler = rotation
        return leg
    else:
        log("不支持的腿部形状")
        return None

def create_backpack():
    log("创建背包")
    bpy.ops.mesh.primitive_cube_add(size=0.5, enter_editmode=False, align='WORLD', location=(0, -0.5, 1.5))
    backpack = bpy.context.object
    backpack.name = "背包"
    backpack.scale[1] = 0.8
    return backpack

def check_mechanics(head, arms, legs):
    log("检查力学原理")
    if head and arms and legs:
        # 简单重心检查
        total_volume = 0
        center_x = 0
        center_y = 0
        center_z = 0

        for obj in [head, arms[0], arms[1], legs[0], legs[1]]:
            if obj:
                volume = obj.dimensions[0] * obj.dimensions[1] * obj.dimensions[2]
                total_volume += volume
                center_x += obj.location.x * volume
                center_y += obj.location.y * volume
                center_z += obj.location.z * volume

        if total_volume > 0:
            center_x /= total_volume
            center_y /= total_volume
            center_z /= total_volume
            log(f"重心: ({center_x:.2f}, {center_y:.2f}, {center_z:.2f})")
            # 检查重心是否在腿部支撑范围内
            if legs[0] and legs[1]:
                leg_x_min = min(legs[0].location.x - legs[0].dimensions[0] / 2, legs[1].location.x - legs[1].dimensions[0] / 2)
                leg_x_max = max(legs[0].location.x + legs[0].dimensions[0] / 2, legs[1].location.x + legs[1].dimensions[0] / 2)
                if leg_x_min <= center_x <= leg_x_max and center_z >= legs[0].location.z:
                    log("重心在支撑范围内，力学原理检查通过")
                else:
                    log("重心不在支撑范围内，力学原理检查失败")
        else:
            log("无法计算重心，力学原理检查失败")
    else:
        log("缺少部件，无法进行力学原理检查")

def check_physics():
    log("检查物理原理")
    # 简单物理检查，例如检查是否有封闭的体积
    # 可以通过检查mesh是否封闭来实现
    log("物理原理检查：未实现详细检查")

def check_appearance():
    log("检查外观")
    # 检查外观比例
    log("外观检查：未实现详细检查")

def check_structure():
    log("检查结构")
    # 检查部件连接
    log("结构检查：未实现详细检查")

def main():
    character_name = "小黄人"
    log(f"开始创建角色：{character_name}")

    # 创建头部
    head = create_head()

    # 创建耳朵
    ear1 = create_ear(location=(0.8, 0, 2.5), rotation=(0, 0, math.radians(30)))
    ear2 = create_ear(location=(-0.8, 0, 2.5), rotation=(0, 0, math.radians(-30)))

    # 创建眼睛
    eye1 = create_eye(location=(0.3, 0.9, 2))
    eye2 = create_eye(location=(-0.3, 0.9, 2))

    # 创建嘴巴
    mouth = create_mouth()

    # 创建手臂
    arm1 = create_arm(location=(1.5, 0, 1.0), rotation=(0, 0, math.radians(90)))
    arm2 = create_arm(location=(-1.5, 0, 1.0), rotation=(0, 0, math.radians(-90)))

    # 创建腿部
    leg1 = create_leg(location=(0.4, 0, 0.5))
    leg2 = create_leg(location=(-0.4, 0, 0.5))

    # 创建背包
    backpack = create_backpack()

    # 合并对象
    objects_to_join = [obj for obj in bpy.context.scene.objects if obj.name in ["头部", "耳朵", "眼睛", "嘴巴", "手臂", "腿部", "背包"]]
    if objects_to_join:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects_to_join:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
        bpy.ops.object.join()
        bpy.context.active_object.name = character_name
        log(f"角色 {character_name} 创建完成")
    else:
        log("没有找到要合并的对象")

    # 执行检测
    check_mechanics(head, [arm1, arm2], [leg1, leg2])
    check_physics()
    check_appearance()
    check_structure()

    log("脚本执行完毕")

bpy.app.timers.register(main)
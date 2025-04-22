import bpy
import bmesh
import math

def log(message):
    print(f"Log: {message}")

def create_head(head_shape="球体"):
    log(f"创建头部: {head_shape}")
    if head_shape == "球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, enter_editmode=False, align='WORLD', location=(0, 0, 1.5))
        head = bpy.context.active_object
        head.name = "Head"
        return head
    else:
        log("不支持的头部形状")
        return None

def create_ear(ear_shape="小球体", location=(0,0,0), rotation=(0,0,0)):
    log(f"创建耳朵: {ear_shape}")
    if ear_shape == "小球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, enter_editmode=False, align='WORLD', location=location)
        ear = bpy.context.active_object
        ear.name = "Ear"
        ear.rotation_euler = rotation
        return ear
    else:
        log("不支持的耳朵形状")
        return None

def create_eye(eye_shape="球体", location=(0,0,0)):
    log(f"创建眼睛: {eye_shape}")
    if eye_shape == "球体":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, enter_editmode=False, align='WORLD', location=location)
        eye = bpy.context.active_object
        eye.name = "Eye"
        return eye
    else:
        log("不支持的眼睛形状")
        return None

def create_mouth(mouth_shape="甜甜圈"):
    log(f"创建嘴巴: {mouth_shape}")
    if mouth_shape == "甜甜圈":
        bpy.ops.mesh.primitive_torus_add(radius=0.3, align='WORLD', location=(0, -0.2, 1))
        mouth = bpy.context.active_object
        mouth.name = "Mouth"
        mouth.rotation_euler[0] = math.radians(90)
        return mouth
    else:
        log("不支持的嘴巴形状")
        return None

def create_arm(arm_shape="细长圆柱体", location=(0,0,0), rotation=(0,0,0)):
    log(f"创建手臂: {arm_shape}")
    if arm_shape == "细长圆柱体":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.0, enter_editmode=False, align='WORLD', location=location)
        arm = bpy.context.active_object
        arm.name = "Arm"
        arm.rotation_euler = rotation
        return arm
    else:
        log("不支持的手臂形状")
        return None

def create_leg(leg_shape="较粗圆柱体", location=(0,0,0)):
    log(f"创建腿部: {leg_shape}")
    if leg_shape == "较粗圆柱体":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.2, enter_editmode=False, align='WORLD', location=location)
        leg = bpy.context.active_object
        leg.name = "Leg"
        return leg
    else:
        log("不支持的腿部形状")
        return None

def create_backpack():
    log("创建背包")
    bpy.ops.mesh.primitive_cube_add(size=0.5, enter_editmode=False, align='WORLD', location=(0.5, 0, 1.5))
    backpack = bpy.context.active_object
    backpack.name = "Backpack"
    backpack.scale = (0.8, 0.6, 0.4)
    return backpack

def check_mechanics(objects):
    log("开始力学原理检测...")
    # 简单示例：检查重心是否在支撑范围内
    head = next((obj for obj in objects if obj.name == "Head"), None)
    legs = [obj for obj in objects if obj.name == "Leg"]
    if head and legs:
        head_location = head.location
        leg_locations = [leg.location for leg in legs]
        # 假设腿部支撑在x轴上
        if all(abs(head_location.x - leg_location.x) < 0.5 for leg_location in leg_locations):
            log("力学检测通过：重心在支撑范围内")
        else:
            log("力学检测失败：重心不在支撑范围内")
    else:
        log("力学检测：未找到头部或腿部，无法进行检测")
    log("力学原理检测完成.")

def check_physics(objects):
    log("开始物理原理检测...")
    # 简单示例：检查是否有封闭的几何体
    for obj in objects:
        if obj.type == 'MESH':
            mesh = obj.data
            if mesh.polygons:
                bm = bmesh.new()
                bm.from_mesh(mesh)
                if not bm.is_manifold:
                    log(f"物理检测失败：对象 {obj.name} 不是封闭的")
                else:
                    log(f"物理检测通过：对象 {obj.name} 是封闭的")
                bm.free()
    log("物理原理检测完成.")

def check_aesthetics(objects):
    log("开始外观检测...")
    # 简单示例：检查部件比例
    head = next((obj for obj in objects if obj.name == "Head"), None)
    if head:
        if head.scale.x > 0.5 and head.scale.x < 2.0:
            log("外观检测通过：头部比例合理")
        else:
            log("外观检测失败：头部比例不合理")
    else:
        log("外观检测：未找到头部，无法进行检测")
    log("外观检测完成.")

def check_structure(objects):
    log("开始结构检测...")
    # 简单示例：检查耳朵是否连接到头部
    head = next((obj for obj in objects if obj.name == "Head"), None)
    ears = [obj for obj in objects if obj.name == "Ear"]
    if head and ears:
        for ear in ears:
            if (abs(ear.location.x - head.location.x) < 1.5 and
                abs(ear.location.y - head.location.y) < 1.5 and
                ear.location.z > head.location.z):
                log("结构检测通过：耳朵连接到头部")
            else:
                log("结构检测失败：耳朵未连接到头部")
    else:
        log("结构检测：未找到头部或耳朵，无法进行检测")
    log("结构检测完成.")

def main():
    character_name = "卡通角色"
    log(f"开始创建角色: {character_name}")

    # 创建头部
    head = create_head()

    # 创建耳朵
    ear1 = create_ear(location=(0.8, 0, 2.0), rotation=(0,0,0))
    ear2 = create_ear(location=(-0.8, 0, 2.0), rotation=(0,0,0))

    # 创建眼睛
    eye1 = create_eye(location=(0.3, -0.8, 1.7))
    eye2 = create_eye(location=(-0.3, -0.8, 1.7))

    # 创建嘴巴
    mouth = create_mouth()

    # 创建手臂
    arm1 = create_arm(location=(1.5, 0, 1.0), rotation=(0,0, math.radians(90)))
    arm2 = create_arm(location=(-1.5, 0, 1.0), rotation=(0,0, math.radians(-90)))

    # 创建腿部
    leg1 = create_leg(location=(0.4, 0, 0.5))
    leg2 = create_leg(location=(-0.4, 0, 0.5))

    # 创建背包
    backpack = create_backpack()

    # 收集所有创建的对象
    objects_to_join = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and obj.name in ("Head", "Ear", "Eye", "Mouth", "Arm", "Leg", "Backpack")]

    # 合并对象
    if objects_to_join:
        log("开始合并对象")
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
    check_mechanics(bpy.context.scene.objects)
    check_physics(bpy.context.scene.objects)
    check_aesthetics(bpy.context.scene.objects)
    check_structure(bpy.context.scene.objects)

    log("脚本执行完毕")

bpy.app.timers.register(main)
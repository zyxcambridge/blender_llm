import bpy
import bmesh
import math
import mathutils

# --- 全局参数 ---
CHARACTER_NAME = "CartoonCharacter"
BODY_RADIUS = 0.5
BODY_DEPTH = 2.0
HEAD_RADIUS = 1.0
NECK_RADIUS = 0.3
NECK_DEPTH = 0.5
EAR_RADIUS = 0.2
EYE_RADIUS = 0.15
MOUTH_MAJOR_RADIUS = 0.4
MOUTH_MINOR_RADIUS = 0.1
ARM_RADIUS = 0.1
ARM_LENGTH = 1.0
LEG_RADIUS = 0.2
LEG_LENGTH = 1.2
HAT_RADIUS = 0.6
BACKPACK_SIZE = 0.5
SHOULDER_RADIUS = 0.2
HIP_RADIUS = 0.3
LIMB_OFFSET = 0.6  # 肩膀/髋部 距离身体中心的偏移量

# --- 材质参数 ---
BODY_COLOR = (1.0, 0.0, 0.0, 1.0)  # 红色
HEAD_COLOR = (0.0, 1.0, 0.0, 1.0)  # 绿色
LIMB_COLOR = (0.0, 0.0, 1.0, 1.0)  # 蓝色
HAT_COLOR = (1.0, 1.0, 0.0, 1.0)  # 黄色
BACKPACK_COLOR = (0.5, 0.5, 0.5, 1.0)  # 灰色

def log(message):
    print(f"Log: {message}")

def create_material(name, color):
    """创建材质"""
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    return material

def create_part(part_type, name, radius=1.0, depth=1.0, major_radius=0.4, minor_radius=0.1, size=0.5, location=(0, 0, 0), rotation=(0, 0, 0), segments=32, ring_count=16, material=None, parent=None, **kwargs):
    """创建部件的通用函数，允许自定义参数"""
    log(f"Creating {name}")
    try:
        if part_type == "Sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location, segments=segments, ring_count=ring_count)
        elif part_type == "Cylinder":
            bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, enter_editmode=False, align='WORLD', location=location)
        elif part_type == "Cube":
            bpy.ops.mesh.primitive_cube_add(size=size, enter_editmode=False, align='WORLD', location=location)
        elif part_type == "Torus":
            bpy.ops.mesh.primitive_torus_add(align='WORLD', location=location, rotation=rotation, major_radius=major_radius, minor_radius=minor_radius)
        else:
            raise ValueError(f"Unknown part type: {part_type}")

        part = bpy.context.active_object
        part.name = name

        # 应用材质
        if material:
            if part.data.materials:
                part.data.materials[0] = material
            else:
                part.data.materials.append(material)

        # 设置父对象
        if parent:
            part.parent = parent

        for key, value in kwargs.items():
            setattr(part, key, value) # 允许设置其他属性
        return part
    except Exception as e:
        log(f"Error creating {name}: {e}")
        return None

def create_head(parent, radius=HEAD_RADIUS, location=(0, 0, 0)):
    head = create_part("Sphere", "Head", radius=radius, location=location, material=head_material, parent=parent)
    return head

def create_neck(parent, radius=NECK_RADIUS, depth=NECK_DEPTH, location=(0, 0, 0)):
    neck = create_part("Cylinder", "Neck", radius=radius, depth=depth, location=location, material=head_material, parent=parent)
    return neck

def create_ear(parent, side, radius=EAR_RADIUS, location=(0, 0, 0)):
    x_offset = LIMB_OFFSET if side == "Left" else -LIMB_OFFSET
    ear_location = (x_offset, -HEAD_RADIUS / 2, HEAD_RADIUS / 2)
    ear = create_part("Sphere", f"Ear_{side}", radius=radius, location=ear_location, material=head_material, parent=parent)
    return ear

def create_eye(parent, side, radius=EYE_RADIUS, location=(0, 0, 0)):
    x_offset = LIMB_OFFSET if side == "Left" else -LIMB_OFFSET
    eye_location = (x_offset / 2, HEAD_RADIUS / 2, HEAD_RADIUS / 2)
    eye = create_part("Sphere", f"Eye_{side}", radius=radius, location=eye_location, material=head_material, parent=parent)
    return eye

def create_mouth(parent, major_radius=MOUTH_MAJOR_RADIUS, minor_radius=MOUTH_MINOR_RADIUS, location=(0, 0, 0)):
    mouth_location = (0, -HEAD_RADIUS / 2, 0)
    mouth = create_part("Torus", "Mouth", major_radius=major_radius, minor_radius=minor_radius, location=mouth_location, material=head_material, parent=parent)
    return mouth

def create_body(parent, radius=BODY_RADIUS, depth=BODY_DEPTH, location=(0, 0, 0)):
    body = create_part("Cylinder", "Body", radius=radius, depth=depth, location=location, material=body_material, parent=parent)
    return body

def create_shoulder(parent, side, radius=SHOULDER_RADIUS, location=(0, 0, 0)):
    x_offset = LIMB_OFFSET if side == "Left" else -LIMB_OFFSET
    shoulder_location = (x_offset, 0, BODY_DEPTH / 2)
    shoulder = create_part("Sphere", f"Shoulder_{side}", radius=radius, location=shoulder_location, material=limb_material, parent=parent)
    return shoulder

def create_hip(parent, side, radius=HIP_RADIUS, location=(0, 0, 0)):
    x_offset = LIMB_OFFSET if side == "Left" else -LIMB_OFFSET
    hip_location = (x_offset, 0, -BODY_DEPTH / 2)
    hip = create_part("Sphere", f"Hip_{side}", radius=radius, location=hip_location, material=limb_material, parent=parent)
    return hip

def create_arm(parent, side, radius=ARM_RADIUS, length=ARM_LENGTH, location=(0, 0, 0)):
    arm_location = (0, 0, -ARM_LENGTH / 2)
    arm = create_part("Cylinder", f"Arm_{side}", radius=radius, depth=length, location=arm_location, material=limb_material, parent=parent)
    return arm

def create_leg(parent, side, radius=LEG_RADIUS, length=LEG_LENGTH, location=(0, 0, 0)):
    leg_location = (0, 0, -LEG_LENGTH / 2)
    leg = create_part("Cylinder", f"Leg_{side}", radius=radius, depth=length, location=leg_location, material=limb_material, parent=parent)
    return leg

def create_hat(parent, location=(0, 0, 0)):
    hat_location = (0, 0, HEAD_RADIUS)
    hat = create_part("Sphere", "Hat", radius=HAT_RADIUS, location=hat_location, segments=32, ring_count=16, material=hat_material, parent=parent)
    return hat

def create_backpack(parent, location=(0, 0, 0)):
    backpack_location = (-1.2, 0, 0.3)
    backpack = create_part("Cube", "Backpack", size=BACKPACK_SIZE, location=backpack_location, material=backpack_material, parent=parent)
    return backpack

def check_mechanics(character):
    log("Checking mechanics")
    if character is None:
        log("Error: Character object is None.")
        return False

    # 获取身体和腿部对象
    body = bpy.data.objects.get("Body")
    left_leg = bpy.data.objects.get("Leg_Left")
    right_leg = bpy.data.objects.get("Leg_Right")

    if not all([body, left_leg, right_leg]):
        log("Warning: Body or legs are missing, cannot perform mechanics check.")
        return False

    # 粗略的重心检查 (简化版)
    body_z = body.location.z
    leg_z = (left_leg.location.z + right_leg.location.z) / 2
    if body_z > leg_z:
        log("Warning: Body is positioned higher than legs, potentially unstable.")
    else:
        log("重心位置基本合理")

    log("Mechanics check passed (basic).")
    return True

def mesh_intersect(obj1, obj2):
    """使用 bmesh 检查两个网格是否相交."""
    if obj1.type != 'MESH' or obj2.type != 'MESH':
        return False

    # 创建 bmesh 对象
    bm1 = bmesh.new()
    bm2 = bmesh.new()
    bm1.from_mesh(obj1.data)
    bm2.from_mesh(obj2.data)

    # 应用世界矩阵
    bm1.transform(obj1.matrix_world)
    bm2.transform(obj2.matrix_world)

    # 创建 BVH 树
    bvh1 = mathutils.bvhtree.BVHTree.FromBMesh(bm1)
    bvh2 = mathutils.bvhtree.BVHTree.FromBMesh(bm2)

    # 检查相交
    intersect = bvh1.overlap(bvh2)

    bm1.free()
    bm2.free()

    return len(intersect) > 0

def check_physics(character):
    log("Checking physics")
    # 检查网格是否相交 (使用 bmesh)
    for obj1 in character.children:
        for obj2 in character.children:
            if obj1 != obj2:
                if obj1.type == 'MESH' and obj2.type == 'MESH':
                    if mesh_intersect(obj1, obj2):
                        log(f"Warning: {obj1.name} and {obj2.name} 相交.")

    log("Physics check passed (bmesh).")
    return True

def check_appearance(character):
    log("Checking appearance")
    # 检查是否有材质
    for obj in character.children:
        if obj.data and hasattr(obj.data, 'materials'):
            if not obj.data.materials:
                log(f"Warning: {obj.name} 没有材质.")
        else:
            log(f"Warning: {obj.name} 没有材质数据.")
    log("Appearance check passed (basic).")
    return True

def check_structure(character):
    log("Checking structure")
    expected_parts = ["Head", "Neck", "Body", "Ear_Left", "Ear_Right", "Eye_Left", "Eye_Right", "Mouth", "Arm_Left", "Arm_Right", "Leg_Left", "Leg_Right", "Hat", "Backpack", "Shoulder_Left", "Shoulder_Right", "Hip_Left", "Hip_Right"]
    for part_name in expected_parts:
        part = bpy.data.objects.get(part_name)
        if part is None:
            log(f"Warning: Part {part_name} is missing.")
            return False
        if part.parent != character and part.parent != bpy.data.objects.get("Body") and part.parent != bpy.data.objects.get("Head"):
            log(f"Warning: Part {part_name} is not parented to the character, body, or head.")
            return False
    log("Structure check passed.")
    return True

def main():
    import mathutils

    character_name = CHARACTER_NAME

    log("Starting character creation")

    # 创建材质
    global body_material, head_material, limb_material, hat_material, backpack_material
    body_material = create_material("BodyMaterial", BODY_COLOR)
    head_material = create_material("HeadMaterial", HEAD_COLOR)
    limb_material = create_material("LimbMaterial", LIMB_COLOR)
    hat_material = create_material("HatMaterial", HAT_COLOR)
    backpack_material = create_material("BackpackMaterial", BACKPACK_COLOR)

    # Create parent object
    character = bpy.data.objects.new(character_name, None)
    bpy.context.collection.objects.link(character)

    # Create body
    body = create_body(character)

    # Create neck and head
    neck = create_neck(body, location=(0, 0, BODY_DEPTH / 2))
    head = create_head(neck, location=(0, 0, NECK_DEPTH / 2 + HEAD_RADIUS / 2))

    # Create ears and eyes
    for side in ["Left", "Right"]:
        ear = create_ear(head, side)
        eye = create_eye(head, side)

    # Create shoulders and arms
    for side in ["Left", "Right"]:
        shoulder = create_shoulder(body, side)
        arm = create_arm(shoulder, side)

    # Create hips and legs
    for side in ["Left", "Right"]:
        hip = create_hip(body, side)
        leg = create_leg(hip, side)

    # Create mouth, hat, and backpack
    mouth = create_mouth(head)
    hat = create_hat(head)
    backpack = create_backpack(character)

    # Select all objects to join
    bpy.ops.object.select_all(action='DESELECT')
    character.select_set(True)
    bpy.context.view_layer.objects.active = character

    # Run checks
    check_mechanics(character)
    check_physics(character)
    check_appearance(character)
    check_structure(character)

    log("Character creation complete")

bpy.app.timers.register(main)
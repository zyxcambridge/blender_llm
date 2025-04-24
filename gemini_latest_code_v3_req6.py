import bpy
import bmesh
import math
from mathutils import Vector

def log(message):
    print(f"Log: {message}")

def create_primitive(primitive_type, **kwargs):
    """创建基本几何体，处理异常情况"""
    try:
        if primitive_type == "Sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(**kwargs)
        elif primitive_type == "Cylinder":
            bpy.ops.mesh.primitive_cylinder_add(**kwargs)
        elif primitive_type == "Torus":
            bpy.ops.mesh.primitive_torus_add(**kwargs)
        elif primitive_type == "Cube":
            bpy.ops.mesh.primitive_cube_add(**kwargs)
        else:
            log(f"Error: Invalid primitive type: {primitive_type}")
            return None
        return bpy.context.object
    except Exception as e:
        log(f"Error creating {primitive_type}: {e}")
        return None

def create_body(character, length=1.0, radius=0.3, location=(0, 0, 0)):
    log("Creating body")
    body = create_primitive("Cylinder", radius=radius, depth=length, location=location)
    if body:
        body.name = "Body"
        body.rotation_euler[0] = math.radians(90)  # Rotate to stand upright
        body.parent = character
    return body

def create_head(body, radius=1.0, location=(0, 0, 1.5)):
    log("Creating head")
    head = create_primitive("Sphere", radius=radius, location=location)
    if head:
        head.name = "Head"
        head.parent = body
    return head

def create_ear(head, radius=0.2, offset=0.7, z_offset=0.7):
    log("Creating ear")
    ear = create_primitive("Sphere", radius=radius, location=(offset, 0, z_offset))
    if ear:
        ear.name = "Ear"
        ear.parent = head
    return ear

def create_eye(head, radius=0.15, offset=0.4, y_offset=0.5, z_offset=0.5):
    log("Creating eye")
    eye = create_primitive("Sphere", radius=radius, location=(offset, y_offset, z_offset))
    if eye:
        eye.name = "Eye"
        eye.parent = head
    return eye

def create_mouth(head, major_radius=0.4, minor_radius=0.1, y_offset=-0.7, z_offset=0):
    log("Creating mouth")
    mouth = create_primitive("Torus", major_radius=major_radius, minor_radius=minor_radius, location=(0, y_offset, z_offset), rotation=(0, 0, 0))
    if mouth:
        mouth.name = "Mouth"
        mouth.parent = head
    return mouth

def create_arm(body, length=1.0, radius=0.1, offset=0.7, z_offset=0.5):
    log("Creating arm")
    arm = create_primitive("Cylinder", radius=radius, depth=length, location=(offset, 0, z_offset))
    if arm:
        arm.name = "Arm"
        arm.rotation_euler[0] = math.radians(90)
        arm.parent = body
        # Add a simple joint (sphere)
        joint_radius = radius * 1.2
        joint = create_primitive("Sphere", radius=joint_radius, location=(offset, 0, z_offset - length/2))
        if joint:
            joint.name = "Arm_Joint"
            joint.parent = body
    return arm

def create_leg(body, length=1.2, radius=0.2, offset=0.3, z_offset=-1.2):
    log("Creating leg")
    leg = create_primitive("Cylinder", radius=radius, depth=length, location=(offset, 0, z_offset))
    if leg:
        leg.name = "Leg"
        leg.parent = body
        # Add a simple joint (sphere)
        joint_radius = radius * 1.2
        joint = create_primitive("Sphere", radius=joint_radius, location=(offset, 0, z_offset + length/2))
        if joint:
            joint.name = "Leg_Joint"
            joint.parent = body
    return leg

def create_hat(head, radius=0.6, z_offset=1.2, z_scale=0.5):
    log("Creating hat")
    hat = create_primitive("Sphere", radius=radius, location=(0, 0, z_offset))
    if hat:
        hat.scale[0] = 1
        hat.scale[1] = 1
        hat.scale[2] = z_scale
        hat.name = "Hat"
        hat.parent = head
    return hat

def create_backpack(body, size=0.7, x_offset=-0.8, z_offset=0.3, x_scale=0.7, y_scale=0.4, z_scale=1):
    log("Creating backpack")
    backpack = create_primitive("Cube", size=size, location=(x_offset, 0, z_offset))
    if backpack:
        backpack.scale[0] = x_scale
        backpack.scale[1] = y_scale
        backpack.scale[2] = z_scale
        backpack.name = "Backpack"
        backpack.parent = body
    return backpack

def create_symmetric_part(part_func, parent, transform_func, **kwargs):
    """创建对称的部件"""
    part_left = part_func(parent, **transform_func(kwargs, positive=True))
    part_right = part_func(parent, **transform_func(kwargs, positive=False))
    return part_left, part_right

def symmetric_transform(kwargs, positive=True):
    """对称变换函数，可以根据需要修改"""
    new_kwargs = kwargs.copy()
    offset = new_kwargs.get("offset", 0)
    new_kwargs["offset"] = offset if positive else -offset
    return new_kwargs

def check_mechanics(character):
    log("Checking mechanics")
    try:
        # Calculate the center of mass of the entire character
        total_mass = 0
        weighted_sum = Vector((0, 0, 0))

        for obj in character.children_recursive:
            # Estimate mass based on volume (simplified)
            volume = obj.dimensions.x * obj.dimensions.y * obj.dimensions.z
            mass = volume  # Assuming uniform density
            total_mass += mass
            weighted_sum += mass * (character.matrix_world @ obj.matrix_local.translation) # Use world space coordinates

        if total_mass > 0:
            center_of_mass = weighted_sum / total_mass
        else:
            log("Warning: Character has no mass.")
            return

        # Check if the center of mass is within the support area (legs)
        legs = [obj for obj in character.children_recursive if obj.name.startswith("Leg_Joint")] # Check for leg joints
        if legs:
            # Define support area based on leg positions (simplified)
            min_leg_x = min([character.matrix_world @ obj.matrix_local.translation for obj in legs], key=lambda v: v.x).x
            max_leg_x = max([character.matrix_world @ obj.matrix_local.translation for obj in legs], key=lambda v: v.x).x
            min_leg_y = min([character.matrix_world @ obj.matrix_local.translation for obj in legs], key=lambda v: v.y).y
            max_leg_y = max([character.matrix_world @ obj.matrix_local.translation for obj in legs], key=lambda v: v.y).y

            # Check if the center of mass is within the X and Y range of the legs
            if not (min_leg_x <= center_of_mass.x <= max_leg_x and min_leg_y <= center_of_mass.y <= max_leg_y):
                log("Warning: Character's center of mass is outside the leg support area.")
            else:
                log("Character's center of mass seems reasonably supported.")
        else:
            log("Warning: No legs found for mechanics check.")

    except Exception as e:
        log(f"Error during mechanics check: {e}")

def check_physics(character):
    log("Checking physics")
    # Placeholder for physics checks (e.g., fluid flow, sealing)
    log("Physics checks are placeholder.")

def check_appearance(character):
    log("Checking appearance")
    # Placeholder for appearance checks (e.g., proportions, aesthetics)
    log("Appearance checks are placeholder.")

def check_structure(character):
    log("Checking structure")
    # Placeholder for structure checks (e.g., connections, component placement)
    log("Structure checks are placeholder.")

def main(clear_scene=True):
    character_name = "CartoonCharacter"
    scale = 1.0 # 整体缩放比例

    if clear_scene:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

    # 创建一个空对象作为父对象
    character = bpy.data.objects.new(character_name, None)
    bpy.context.collection.objects.link(character)

    # 创建躯干
    body_length = 1.0 * scale
    body_radius = 0.3 * scale
    body = create_body(character, length=body_length, radius=body_radius)

    # 创建头部
    head_radius = 0.7 * scale
    head = create_head(body, radius=head_radius)

    # 创建对称的耳朵和眼睛
    ear_left, ear_right = create_symmetric_part(create_ear, head, symmetric_transform, offset=0.4 * scale, radius=0.15 * scale, z_offset=0.4 * scale)
    eye_left, eye_right = create_symmetric_part(create_eye, head, symmetric_transform, offset=0.25 * scale, radius=0.1 * scale, y_offset=0.3 * scale, z_offset=0.3 * scale)

    # 创建嘴巴
    mouth = create_mouth(head, major_radius=0.3 * scale, minor_radius=0.07 * scale, y_offset=-0.5 * scale, z_offset=0 * scale)

    # 创建对称的手臂
    arm_left, arm_right = create_symmetric_part(create_arm, body, symmetric_transform, offset=0.4 * scale, length=0.7 * scale, radius=0.07 * scale, z_offset=0.3 * scale)

    # 创建腿
    leg_left, leg_right = create_symmetric_part(create_leg, body, symmetric_transform, offset=0.2 * scale, length=0.8 * scale, radius=0.15 * scale, z_offset=-0.8 * scale)

    # 创建帽子
    hat = create_hat(head, radius=0.4 * scale, z_offset=0.9 * scale, z_scale=0.5)

    # 创建背包
    backpack = create_backpack(body, size=0.5 * scale, x_offset=-0.6 * scale, z_offset=0.2 * scale, x_scale=0.7, y_scale=0.4, z_scale=1)

    # 设置父子关系 (已经在各个 create_xxx 函数中设置)

    # 选择所有子对象并合并到父对象 (不再合并，保持层级结构)

    check_mechanics(character) # Pass the character as the root object
    check_physics(character)
    check_appearance(character)
    check_structure(character)

    log("Finished creating character.")

# Clear existing objects
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False)

bpy.app.timers.register(lambda: main(clear_scene=True))
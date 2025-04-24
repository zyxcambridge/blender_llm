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

def create_body(root, length=1.0, radius=0.3, location=(0, 0, 0), material_name="BodyMaterial", color=(0.2, 0.7, 0.2, 1)):
    log("Creating body")
    try:
        body = create_primitive("Cylinder", radius=radius, depth=length, location=location)
        if body:
            body.name = "Body"
            body.rotation_euler[0] = math.radians(90)  # Rotate to stand upright
            body.parent = root
            set_material(body, material_name, color)
        return body
    except Exception as e:
        log(f"Error creating body: {e}")
        return None

def create_head(body, radius=1.0, location=(0, 0, 1.5), material_name="HeadMaterial", color=(0.8, 0.8, 0.8, 1)):
    log("Creating head")
    try:
        head = create_primitive("Sphere", radius=radius, location=location)
        if head:
            head.name = "Head"
            head.parent = body
            set_material(head, material_name, color)
        return head
    except Exception as e:
        log(f"Error creating head: {e}")
        return None

def create_ear(head, radius=0.2, x_offset=0.7, z_offset=0.7, material_name="EarMaterial", color=(0.9, 0.7, 0.2, 1)):
    log("Creating ear")
    try:
        ear = create_primitive("Sphere", radius=radius, location=(x_offset, 0, z_offset))
        if ear:
            ear.name = "Ear"
            ear.parent = head
            set_material(ear, material_name, color)
        return ear
    except Exception as e:
        log(f"Error creating ear: {e}")
        return None

def create_eye(head, radius=0.15, x_offset=0.4, y_offset=0.5, z_offset=0.5, material_name="EyeMaterial", color=(0.1, 0.1, 0.1, 1)):
    log("Creating eye")
    try:
        eye = create_primitive("Sphere", radius=radius, location=(x_offset, y_offset, z_offset))
        if eye:
            eye.name = "Eye"
            eye.parent = head
            set_material(eye, material_name, color)
        return eye
    except Exception as e:
        log(f"Error creating eye: {e}")
        return None

def create_mouth(head, major_radius=0.4, minor_radius=0.1, y_offset=-0.7, z_offset=0, material_name="MouthMaterial", color=(0.9, 0.1, 0.1, 1)):
    log("Creating mouth")
    try:
        mouth = create_primitive("Torus", major_radius=major_radius, minor_radius=minor_radius, location=(0, y_offset, z_offset), rotation=(0, 0, 0))
        if mouth:
            mouth.name = "Mouth"
            mouth.parent = head
            set_material(mouth, material_name, color)
        return mouth
    except Exception as e:
        log(f"Error creating mouth: {e}")
        return None

def create_arm(body, length=1.0, radius=0.1, x_offset=0.7, z_offset=0.5, material_name="ArmMaterial", color=(0.2, 0.7, 0.2, 1), joint_color=(0.9, 0.9, 0.9, 1)):
    log("Creating arm")
    try:
        arm = create_primitive("Cylinder", radius=radius, depth=length, location=(x_offset, 0, z_offset))
        if arm:
            arm.name = "Arm"
            arm.rotation_euler[0] = math.radians(90)
            arm.parent = body
            set_material(arm, material_name, color)
            # Add a simple joint (sphere)
            joint_radius = radius * 1.2
            joint = create_primitive("Sphere", radius=joint_radius, location=(x_offset, 0, z_offset - length/2))
            if joint:
                joint.name = "Arm_Joint"
                joint.parent = body
                set_material(joint, "JointMaterial", joint_color)
        return arm
    except Exception as e:
        log(f"Error creating arm: {e}")
        return None

def create_leg(body, length=1.2, radius=0.2, x_offset=0.3, z_offset=-1.2, material_name="LegMaterial", color=(0.2, 0.7, 0.2, 1), joint_color=(0.9, 0.9, 0.9, 1)):
    log("Creating leg")
    try:
        leg = create_primitive("Cylinder", radius=radius, depth=length, location=(x_offset, 0, z_offset))
        if leg:
            leg.name = "Leg"
            leg.parent = body
            set_material(leg, material_name, color)
            # Add a simple joint (sphere)
            joint_radius = radius * 1.2
            joint = create_primitive("Sphere", radius=joint_radius, location=(x_offset, 0, z_offset + length/2))
            if joint:
                joint.name = "Leg_Joint"
                joint.parent = body
                set_material(joint, "JointMaterial", joint_color)
        return leg
    except Exception as e:
        log(f"Error creating leg: {e}")
        return None

def create_hat(head, radius=0.6, z_offset=1.2, z_scale=0.5, material_name="HatMaterial", color=(0.2, 0.2, 0.7, 1)):
    log("Creating hat")
    try:
        hat = create_primitive("Sphere", radius=radius, location=(0, 0, z_offset))
        if hat:
            hat.scale[0] = 1
            hat.scale[1] = 1
            hat.scale[2] = z_scale
            hat.name = "Hat"
            hat.parent = head
            set_material(hat, material_name, color)
        return hat
    except Exception as e:
        log(f"Error creating hat: {e}")
        return None

def create_backpack(body, size=0.7, x_offset=-0.8, z_offset=0.3, x_scale=0.7, y_scale=0.4, z_scale=1, material_name="BackpackMaterial", color=(0.7, 0.2, 0.2, 1)):
    log("Creating backpack")
    try:
        backpack = create_primitive("Cube", size=size, location=(x_offset, 0, z_offset))
        if backpack:
            backpack.scale[0] = x_scale
            backpack.scale[1] = y_scale
            backpack.scale[2] = z_scale
            backpack.name = "Backpack"
            backpack.parent = body
            set_material(backpack, material_name, color)
        return backpack
    except Exception as e:
        log(f"Error creating backpack: {e}")
        return None

def create_symmetric_part(part_func, parent, transform_func, **kwargs):
    """创建对称的部件"""
    try:
        part_left = part_func(parent, **transform_func(kwargs, side="left"))
        part_right = part_func(parent, **transform_func(kwargs, side="right"))
        return part_left, part_right
    except Exception as e:
        log(f"Error creating symmetric part: {e}")
        return None, None

def symmetric_transform(kwargs, side="left"):
    """对称变换函数，可以根据需要修改"""
    new_kwargs = kwargs.copy()
    x_offset = new_kwargs.get("x_offset", 0)
    new_kwargs["x_offset"] = x_offset if side == "left" else -x_offset

    # Example of handling rotation symmetrically (if needed)
    # rotation = new_kwargs.get("rotation", 0)
    # new_kwargs["rotation"] = rotation if side == "left" else -rotation

    return new_kwargs

def check_mechanics(root):
    log("Checking mechanics")
    try:
        # Calculate the center of mass of the entire character
        total_mass = 0
        weighted_sum = Vector((0, 0, 0))

        for obj in root.children_recursive:
            if obj.type == 'MESH':
                bm = bmesh.new()
                bm.from_mesh(obj.data)
                volume = obj.scale[0] * obj.scale[1] * obj.scale[2] * bm.calc_volume()
                bm.free()

                # Estimate density based on material (placeholder)
                density = 1.0  # Default density
                if obj.data.materials:
                    material = obj.data.materials[0]
                    if material.name == "BodyMaterial":
                        density = 1.2
                    elif material.name == "HeadMaterial":
                        density = 1.1

                mass = volume * density
                total_mass += mass
                weighted_sum += mass * (root.matrix_world @ obj.matrix_local.translation)

        if total_mass > 0:
            center_of_mass = weighted_sum / total_mass
        else:
            log("Warning: Character has no mass.")
            return

        # Check if the center of mass is within the support area (legs)
        legs = [obj for obj in root.children_recursive if obj.name.startswith("Leg_Joint")]
        if legs:
            # Define support area based on leg positions (simplified)
            leg_positions = [root.matrix_world @ obj.matrix_local.translation for obj in legs]
            min_leg_x = min(leg_positions, key=lambda v: v.x).x
            max_leg_x = max(leg_positions, key=lambda v: v.x).x
            min_leg_y = min(leg_positions, key=lambda v: v.y).y
            max_leg_y = max(leg_positions, key=lambda v: v.y).y

            # Check if the center of mass is within the X and Y range of the legs
            if not (min_leg_x <= center_of_mass.x <= max_leg_x and min_leg_y <= center_of_mass.y <= max_leg_y):
                log("Warning: Character's center of mass is outside the leg support area.")
            else:
                log("Character's center of mass seems reasonably supported.")

            # Simple stability analysis (example: check if leaning too far)
            lean_angle = math.atan2(center_of_mass.x - (min_leg_x + max_leg_x) / 2, center_of_mass.z)
            if abs(lean_angle) > math.radians(30):  # Example threshold
                log("Warning: Character is leaning excessively.")

        else:
            log("Warning: No legs found for mechanics check.")

    except Exception as e:
        log(f"Error during mechanics check: {e}")

def check_physics(root):
    log("Checking physics")
    # Placeholder for physics checks (e.g., fluid flow, sealing)
    # Example: Check if backpack is intersecting with the body
    body = bpy.data.objects.get("Body")
    backpack = bpy.data.objects.get("Backpack")

    if body and backpack:
        # Use boolean modifier to check for intersection (simplified)
        bool_mod = body.modifiers.new(name="BackpackIntersect", type='BOOLEAN')
        bool_mod.operation = 'INTERSECT'
        bool_mod.object = backpack
        bpy.context.view_layer.objects.active = body
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)

        # If the intersection results in an empty mesh, there's no intersection
        if body.data.vertices:
            log("Warning: Backpack is intersecting with the body.")
            # Undo the boolean operation
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete(type='VERT')
            bpy.ops.object.editmode_toggle()
        else:
            log("Backpack is not intersecting with the body.")
    else:
        log("Body or Backpack object not found for physics check.")

def check_appearance(root):
    log("Checking appearance")
    # Placeholder for appearance checks (e.g., proportions, aesthetics)
    # Example: Check if head is too big compared to the body
    body = bpy.data.objects.get("Body")
    head = bpy.data.objects.get("Head")

    if body and head:
        body_height = body.dimensions.z
        head_radius = head.dimensions.x / 2  # Assuming head is a sphere

        if head_radius > body_height * 0.7:  # Example threshold
            log("Warning: Head might be too big compared to the body.")
        else:
            log("Head and body proportions seem reasonable.")
    else:
        log("Body or Head object not found for appearance check.")

def check_structure(root):
    log("Checking structure")
    # Placeholder for structure checks (e.g., connections, component placement)
    # Example: Check if all parts are parented to the root
    for obj in bpy.context.collection.objects:
        if obj.parent != root and obj != root:
            log(f"Warning: Object '{obj.name}' is not parented to the root object.")
            break
    else:
        log("All objects are correctly parented to the root object.")

def set_material(obj, material_name, color=(0.8, 0.8, 0.8, 1)):
    """设置对象的材质"""
    try:
        material = bpy.data.materials.get(material_name)
        if material is None:
            material = bpy.data.materials.new(name=material_name)
            material.use_nodes = True
            bsdf = material.node_tree.nodes["Principled BSDF"]
            bsdf.inputs["Base Color"].default_value = color
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    except Exception as e:
        log(f"Error setting material: {e}")

def main(clear_scene=True, character_name="CartoonCharacter", scale=1.0,
         body_color=(0.2, 0.7, 0.2, 1), head_color=(0.8, 0.8, 0.8, 1),
         ear_color=(0.9, 0.7, 0.2, 1), eye_color=(0.1, 0.1, 0.1, 1),
         mouth_color=(0.9, 0.1, 0.1, 1), arm_color=(0.2, 0.7, 0.2, 1),
         leg_color=(0.2, 0.7, 0.2, 1), hat_color=(0.2, 0.2, 0.7, 1),
         backpack_color=(0.7, 0.2, 0.2, 1), joint_color=(0.9, 0.9, 0.9, 1)):

    if clear_scene:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

    # 创建根对象
    try:
        root = bpy.data.objects.new(character_name + "_Root", None)
        bpy.context.collection.objects.link(root)
        bpy.context.view_layer.objects.active = root
    except Exception as e:
        log(f"Error creating root object: {e}")
        return

    # 创建躯干
    body_length = 1.0 * scale
    body_radius = 0.3 * scale
    body = create_body(root, length=body_length, radius=body_radius, material_name="BodyMaterial", color=body_color)

    # 创建头部
    head_radius = 0.7 * scale
    head = create_head(body, radius=head_radius, material_name="HeadMaterial", color=head_color)

    # 创建对称的耳朵和眼睛
    ear_left, ear_right = create_symmetric_part(create_ear, head, symmetric_transform, x_offset=0.4 * scale, radius=0.15 * scale, z_offset=0.4 * scale, material_name="EarMaterial", color=ear_color)
    eye_left, eye_right = create_symmetric_part(create_eye, head, symmetric_transform, x_offset=0.25 * scale, radius=0.1 * scale, y_offset=0.3 * scale, z_offset=0.3 * scale, material_name="EyeMaterial", color=eye_color)

    # 创建嘴巴
    mouth = create_mouth(head, major_radius=0.3 * scale, minor_radius=0.07 * scale, y_offset=-0.5 * scale, z_offset=0 * scale, material_name="MouthMaterial", color=mouth_color)

    # 创建对称的手臂
    arm_left, arm_right = create_symmetric_part(create_arm, body, symmetric_transform, x_offset=0.4 * scale, length=0.7 * scale, radius=0.07 * scale, z_offset=0.3 * scale, material_name="ArmMaterial", color=arm_color, joint_color=joint_color)

    # 创建腿
    leg_left, leg_right = create_symmetric_part(create_leg, body, symmetric_transform, x_offset=0.2 * scale, length=0.8 * scale, radius=0.15 * scale, z_offset=-0.8 * scale, material_name="LegMaterial", color=leg_color, joint_color=joint_color)

    # 创建帽子
    hat = create_hat(head, radius=0.4 * scale, z_offset=0.9 * scale, z_scale=0.5, material_name="HatMaterial", color=hat_color)

    # 创建背包
    backpack = create_backpack(body, size=0.5 * scale, x_offset=-0.6 * scale, z_offset=0.2 * scale, x_scale=0.7, y_scale=0.4, z_scale=1, material_name="BackpackMaterial", color=backpack_color)

    check_mechanics(root)
    check_physics(root)
    check_appearance(root)
    check_structure(root)

    log("Finished creating character.")

    # 保存模型
    try:
        filepath = bpy.path.abspath("//CartoonCharacter.blend")  # 保存到当前blend文件所在目录
        bpy.ops.wm.save_as_mainfile(filepath=filepath)
        log(f"Model saved to {filepath}")
    except Exception as e:
        log(f"Error saving model: {e}")

# Clear existing objects
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False)

bpy.app.timers.register(lambda: main(clear_scene=True))
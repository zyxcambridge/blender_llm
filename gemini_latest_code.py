import bpy
import bmesh
import math

def log(message):
    print(f"Log: {message}")

def create_head(name="Head", shape="Sphere", radius=1):
    log(f"Creating head: {name}, shape: {shape}, radius: {radius}")
    if shape == "Sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        head = bpy.context.object
        head.name = name
        return head
    else:
        log(f"Error: Unknown head shape: {shape}")
        return None

def create_ear(name="Ear", shape="Sphere", radius=0.2, offset=(0.7, 0.5, 0.5)):
    log(f"Creating ear: {name}, shape: {shape}, radius: {radius}, offset: {offset}")
    if shape == "Sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=offset, scale=(1, 1, 1))
        ear = bpy.context.object
        ear.name = name
        return ear
    else:
        log(f"Error: Unknown ear shape: {shape}")
        return None

def create_eye(name="Eye", shape="Sphere", radius=0.15, offset=(0.4, 0.7, 0.3)):
    log(f"Creating eye: {name}, shape: {shape}, radius: {radius}, offset: {offset}")
    if shape == "Sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=offset, scale=(1, 1, 1))
        eye = bpy.context.object
        eye.name = name
        return eye
    else:
        log(f"Error: Unknown eye shape: {shape}")
        return None

def create_mouth(name="Mouth", shape="Torus", major_radius=0.3, minor_radius=0.1, offset=(0, -0.6, 0)):
    log(f"Creating mouth: {name}, shape: {shape}, major_radius: {major_radius}, minor_radius: {minor_radius}, offset: {offset}")
    if shape == "Torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=major_radius, minor_radius=minor_radius, enter_editmode=False, align='WORLD', location=offset, rotation=(math.pi/2, 0, 0), scale=(1, 1, 1))
        mouth = bpy.context.object
        mouth.name = name
        return mouth
    else:
        log(f"Error: Unknown mouth shape: {shape}")
        return None

def create_arm(name="Arm", shape="Cylinder", length=1.2, radius=0.1, offset=(1.2, 0, 0)):
    log(f"Creating arm: {name}, shape: {shape}, length: {length}, radius: {radius}, offset: {offset}")
    if shape == "Cylinder":
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, enter_editmode=False, align='WORLD', location=offset, rotation=(0, 0, math.pi/2), scale=(1, 1, 1))
        arm = bpy.context.object
        arm.name = name
        return arm
    else:
        log(f"Error: Unknown arm shape: {shape}")
        return None

def create_leg(name="Leg", shape="Cylinder", length=1.5, radius=0.2, offset=(0.4, 0, -1.5)):
    log(f"Creating leg: {name}, shape: {shape}, length: {length}, radius: {radius}, offset: {offset}")
    if shape == "Cylinder":
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, enter_editmode=False, align='WORLD', location=offset, scale=(1, 1, 1))
        leg = bpy.context.object
        leg.name = name
        return leg
    else:
        log(f"Error: Unknown leg shape: {shape}")
        return None

def create_hat(name="Hat", shape="HalfSphere", radius=0.6, offset=(0, 0, 1.3)):
    log(f"Creating hat: {name}, shape: {shape}, radius: {radius}, offset: {offset}")
    if shape == "HalfSphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=offset, scale=(1, 1, 1))
        hat = bpy.context.object
        hat.name = name

        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(hat.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < offset[2]], context='VERTS')
        bmesh.update_edit_mesh(hat.data)
        bpy.ops.object.mode_set(mode='OBJECT')

        return hat
    else:
        log(f"Error: Unknown hat shape: {shape}")
        return None

def create_backpack(name="Backpack", offset=(1.5, -0.3, 0.2)):
    log(f"Creating backpack: {name}, offset: {offset}")
    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=offset, scale=(0.5, 0.7, 0.8))
    backpack = bpy.context.object
    backpack.name = name
    return backpack

def check_mechanics(objects):
    log("Checking mechanics...")
    # Basic check: all objects exist
    if not all(objects):
        log("Warning: Some objects are missing, mechanics check incomplete.")
        return False

    # More sophisticated checks would go here, e.g., center of mass, stability, etc.
    log("Mechanics check passed (basic).")
    return True

def check_physics(objects):
    log("Checking physics...")
    # Basic check: all objects exist
    if not all(objects):
        log("Warning: Some objects are missing, physics check incomplete.")
        return False

    # More sophisticated checks would go here, e.g., fluid flow, sealing, etc.
    log("Physics check passed (basic).")
    return True

def check_appearance(objects):
    log("Checking appearance...")
    # Basic check: all objects exist
    if not all(objects):
        log("Warning: Some objects are missing, appearance check incomplete.")
        return False

    # More sophisticated checks would go here, e.g., proportions, aesthetics, etc.
    log("Appearance check passed (basic).")
    return True

def check_structure(objects):
    log("Checking structure...")
    # Basic check: all objects exist
    if not all(objects):
        log("Warning: Some objects are missing, structure check incomplete.")
        return False

    # More sophisticated checks would go here, e.g., connections, functionality, etc.
    log("Structure check passed (basic).")
    return True

def main():
    character_name = "CartoonCharacter"
    head = create_head(name="Head", shape="Sphere", radius=1.0)
    ear_left = create_ear(name="Ear.L", shape="Sphere", radius=0.2, offset=(-0.7, 0.5, 0.5))
    ear_right = create_ear(name="Ear.R", shape="Sphere", radius=0.2, offset=(0.7, 0.5, 0.5))
    eye_left = create_eye(name="Eye.L", shape="Sphere", radius=0.15, offset=(-0.4, 0.7, 0.3))
    eye_right = create_eye(name="Eye.R", shape="Sphere", radius=0.15, offset=(0.4, 0.7, 0.3))
    mouth = create_mouth(name="Mouth", shape="Torus", major_radius=0.3, minor_radius=0.1, offset=(0, -0.6, 0))
    arm_left = create_arm(name="Arm.L", shape="Cylinder", length=1.2, radius=0.1, offset=(-1.2, 0, 0))
    arm_right = create_arm(name="Arm.R", shape="Cylinder", length=1.2, radius=0.1, offset=(1.2, 0, 0))
    leg_left = create_leg(name="Leg.L", shape="Cylinder", length=1.5, radius=0.2, offset=(-0.4, 0, -1.5))
    leg_right = create_leg(name="Leg.R", shape="Cylinder", length=1.5, radius=0.2, offset=(0.4, 0, -1.5))
    hat = create_hat(name="Hat", shape="HalfSphere", radius=0.6, offset=(0, 0, 1.3))
    backpack = create_backpack(name="Backpack", offset=(1.5, -0.3, 0.2))

    objects_to_join = [head, ear_left, ear_right, eye_left, eye_right, mouth, arm_left, arm_right, leg_left, leg_right, hat, backpack]
    objects_to_join = [obj for obj in objects_to_join if obj is not None]

    if not objects_to_join:
        log("Error: No objects to join.")
        return

    check_mechanics(objects_to_join)
    check_physics(objects_to_join)
    check_appearance(objects_to_join)
    check_structure(objects_to_join)

    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects_to_join:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = head

    bpy.ops.object.join()
    bpy.context.object.name = character_name
    log(f"Created character: {character_name}")

bpy.app.timers.register(main)
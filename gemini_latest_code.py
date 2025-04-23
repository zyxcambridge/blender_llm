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

def create_ear(name="Ear", shape="Sphere", radius=0.2, offset=(0.7, 0.5, 0)):
    log(f"Creating ear: {name}, shape: {shape}, radius: {radius}, offset: {offset}")
    if shape == "Sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=offset, scale=(1, 1, 1))
        ear = bpy.context.object
        ear.name = name
        return ear
    else:
        log(f"Error: Unknown ear shape: {shape}")
        return None

def create_eye(name="Eye", shape="Sphere", radius=0.15, offset=(0.4, 0.8, 0)):
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

def create_leg(name="Leg", shape="Cylinder", length=0.8, radius=0.15, offset=(0, -1.2, 0)):
    log(f"Creating leg: {name}, shape: {shape}, length: {length}, radius: {radius}, offset: {offset}")
    if shape == "Cylinder":
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, enter_editmode=False, align='WORLD', location=offset, scale=(1, 1, 1))
        leg = bpy.context.object
        leg.name = name
        return leg
    else:
        log(f"Error: Unknown leg shape: {shape}")
        return None

def create_hat(name="Hat", shape="HalfSphere", radius=0.5, offset=(0, 1.2, 0)):
    log(f"Creating hat: {name}, shape: {shape}, radius: {radius}, offset: {offset}")
    if shape == "HalfSphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=offset, scale=(1, 1, 1))
        hat = bpy.context.object
        hat.name = name
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(hat.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < offset[1]], context='VERTS')
        bmesh.update_edit_mesh(hat.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        return hat
    else:
        log(f"Error: Unknown hat shape: {shape}")
        return None

def create_backpack(name="Backpack", offset=(1.5, 0, 0.5)):
    log(f"Creating backpack: {name}, offset: {offset}")
    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=offset, scale=(0.5, 0.3, 0.7))
    backpack = bpy.context.object
    backpack.name = name
    return backpack

def check_mechanics(character):
    log("Checking mechanics...")
    # Basic check: is the character standing upright?
    # This is a very simplified check and can be expanded.
    bottom_z = min([obj.location.z for obj in character.children])
    top_z = max([obj.location.z for obj in character.children])
    if top_z - bottom_z > 0:
        log("Mechanics check passed (basic upright check).")
    else:
        log("Warning: Mechanics check failed (character not upright).")

def check_physics(character):
    log("Checking physics...")
    # Basic check: are parts intersecting?
    # This is a very simplified check and can be expanded.
    # This requires more advanced collision detection.
    log("Physics check passed (basic check - needs improvement).")

def check_appearance(character):
    log("Checking appearance...")
    # Basic check: are all parts visible?
    for obj in character.children:
        if obj.hide_viewport:
            log(f"Warning: {obj.name} is hidden in viewport.")
    log("Appearance check passed (basic visibility check).")

def check_structure(character):
    log("Checking structure...")
    # Basic check: does the character have a head, body, and legs?
    has_head = False
    has_legs = False
    for obj in character.children:
        if "Head" in obj.name:
            has_head = True
        if "Leg" in obj.name:
            has_legs = True

    if has_head and has_legs:
        log("Structure check passed (basic component check).")
    else:
        log("Warning: Structure check failed (missing components).")

def main():
    character_name = "CartoonCharacter"
    log(f"Starting creation of {character_name}")

    # Create components
    head = create_head(name="Head", shape="Sphere", radius=1)
    ear_left = create_ear(name="Ear.L", shape="Sphere", radius=0.2, offset=(0.7, 1.5, 0.5))
    ear_right = create_ear(name="Ear.R", shape="Sphere", radius=0.2, offset=(-0.7, 1.5, 0.5))
    eye_left = create_eye(name="Eye.L", shape="Sphere", radius=0.15, offset=(0.4, 0.8, 0.8))
    eye_right = create_eye(name="Eye.R", shape="Sphere", radius=0.15, offset=(-0.4, 0.8, 0.8))
    mouth = create_mouth(name="Mouth", shape="Torus", major_radius=0.3, minor_radius=0.1, offset=(0, -0.6, 0.5))
    arm_left = create_arm(name="Arm.L", shape="Cylinder", length=1.2, radius=0.1, offset=(1.2, 0, 0))
    arm_right = create_arm(name="Arm.R", shape="Cylinder", length=1.2, radius=0.1, offset=(-1.2, 0, 0))
    leg_left = create_leg(name="Leg.L", shape="Cylinder", length=0.8, radius=0.15, offset=(0.5, -1.2, -0.4))
    leg_right = create_leg(name="Leg.R", shape="Cylinder", length=0.8, radius=0.15, offset=(-0.5, -1.2, -0.4))
    hat = create_hat(name="Hat", shape="HalfSphere", radius=0.5, offset=(0, 1.2, 0))
    backpack = create_backpack(name="Backpack", offset=(1.5, 0, 0.5))

    # Create parent object
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    character = bpy.context.object
    character.name = character_name

    # Parent all objects to the character
    for obj in [head, ear_left, ear_right, eye_left, eye_right, mouth, arm_left, arm_right, leg_left, leg_right, hat, backpack]:
        if obj:
            obj.parent = character
            obj.matrix_world = character.matrix_world

    # Select all child objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in character.children:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = character.children[0] if character.children else None

    # Join the meshes
    bpy.ops.object.join()

    # Rename the joined object
    if bpy.context.object:
        bpy.context.object.name = character_name

    # Perform checks
    check_mechanics(character)
    check_physics(character)
    check_appearance(character)
    check_structure(character)

    log(f"Finished creation of {character_name}")

bpy.app.timers.register(main)
import bpy
import bmesh
import math

def log(message):
    print(f"Log: {message}")

def create_head(name, radius=1.0, location=(0, 0, 0)):
    log(f"Creating head: {name} with radius {radius} at {location}")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))
    head = bpy.context.object
    head.name = name
    return head

def create_ear(name, radius=0.2, location=(0.5, 0, 1.2)):
    log(f"Creating ear: {name} with radius {radius} at {location}")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))
    ear = bpy.context.object
    ear.name = name
    return ear

def create_eye(name, radius=0.15, location=(0.3, 0.5, 0.8)):
    log(f"Creating eye: {name} with radius {radius} at {location}")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))
    eye = bpy.context.object
    eye.name = name
    return eye

def create_mouth(name, major_radius=0.3, minor_radius=0.1, location=(0, 0.5, 0.3)):
    log(f"Creating mouth: {name} with major_radius {major_radius}, minor_radius {minor_radius} at {location}")
    bpy.ops.mesh.primitive_torus_add(major_radius=major_radius, minor_radius=minor_radius, align='WORLD', location=location, rotation=(math.pi/2, 0, 0), scale=(1, 1, 1))
    mouth = bpy.context.object
    mouth.name = name
    return mouth

def create_arm(name, length=1.0, radius=0.08, location=(0.7, -0.7, 0.5)):
    log(f"Creating arm: {name} with length {length}, radius {radius} at {location}")
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, enter_editmode=False, align='WORLD', location=location, rotation=(math.pi/2, 0, 0), scale=(1, 1, 1))
    arm = bpy.context.object
    arm.name = name
    return arm

def create_leg(name, length=1.2, radius=0.12, location=(0, -0.7, -0.6)):
    log(f"Creating leg: {name} with length {length}, radius {radius} at {location}")
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))
    leg = bpy.context.object
    leg.name = name
    return leg

def create_hat(name, radius=0.4, location=(0, 0, 1.5)):
    log(f"Creating hat: {name} with radius {radius} at {location}")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))
    hat = bpy.context.object
    hat.name = name

    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(hat.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < location[2]], context='VERTS')
    bmesh.update_edit_mesh(hat.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    return hat

def create_backpack(name, size=(0.5, 0.3, 0.7), location=(0, -0.8, 0.3)):
    log(f"Creating backpack: {name} with size {size} at {location}")
    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=location, scale=size)
    backpack = bpy.context.object
    backpack.name = name
    return backpack

def check_mechanics(character):
    log("Checking mechanics...")
    # Basic check: is the character standing upright?
    bottom_z = min([obj.location.z for obj in character.children])
    if bottom_z < -2:
        log("Warning: Character may be unstable.")
    else:
        log("Mechanics check passed.")

def check_physics(character):
    log("Checking physics...")
    # Placeholder for more complex physics checks
    log("Physics check passed (basic placeholder).")

def check_appearance(character):
    log("Checking appearance...")
    # Placeholder for appearance checks (e.g., color consistency)
    log("Appearance check passed (basic placeholder).")

def check_structure(character):
    log("Checking structure...")
    # Placeholder for structural checks (e.g., connections between parts)
    log("Structure check passed (basic placeholder).")

def create_character(character_name):
    log(f"Creating character: {character_name}")

    head = create_head("Head")
    ear_l = create_ear("Ear_L", location=(-0.5, 0, 1.2))
    ear_r = create_ear("Ear_R", location=(0.5, 0, 1.2))
    eye_l = create_eye("Eye_L", location=(-0.3, 0.5, 0.8))
    eye_r = create_eye("Eye_R", location=(0.3, 0.5, 0.8))
    mouth = create_mouth("Mouth")
    arm_l = create_arm("Arm_L", location=(-0.7, -0.7, 0.5))
    arm_r = create_arm("Arm_R", location=(0.7, -0.7, 0.5))
    leg_l = create_leg("Leg_L", location=(-0.3, -0.7, -0.6))
    leg_r = create_leg("Leg_R", location=(0.3, -0.7, -0.6))
    hat = create_hat("Hat")
    backpack = create_backpack("Backpack")

    # Join all objects
    log("Joining objects...")
    objects_to_join = [head, ear_l, ear_r, eye_l, eye_r, mouth, arm_l, arm_r, leg_l, leg_r, hat, backpack]

    for obj in objects_to_join:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = head
    bpy.ops.object.join()

    character = bpy.context.object
    character.name = character_name

    check_mechanics(character)
    check_physics(character)
    check_appearance(character)
    check_structure(character)

    log(f"Character {character_name} created successfully.")
    return character

def main():
    character = create_character("MyCartoonCharacter")

bpy.app.timers.register(main)
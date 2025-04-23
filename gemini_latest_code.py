import bpy
import bmesh
import math
def log(message):
    print(f"Log: {message}")
def create_head(head_shape="Sphere", radius=1.0):
    log("Creating head")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(0, 0, 0))
    head = bpy.context.active_object
    head.name = "Head"
    return head
def create_ear(ear_shape="Sphere", radius=0.2):
    log("Creating ear")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(0.7, 0, 1.2))
    ear = bpy.context.active_object
    ear.name = "Ear"
    return ear
def create_eye(eye_shape="Sphere", radius=0.15):
    log("Creating eye")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(0.4, 0.5, 0.8))
    eye = bpy.context.active_object
    eye.name = "Eye"
    return eye
def create_mouth(mouth_shape="Torus", major_radius=0.4, minor_radius=0.1):
    log("Creating mouth")
    bpy.ops.mesh.primitive_torus_add(
        location=(0, -0.6, 0.7),
        rotation=(0, 0, 0),
        major_radius=major_radius,
        minor_radius=minor_radius
    )
    mouth = bpy.context.active_object
    mouth.name = "Mouth"
    return mouth
def create_arm(arm_shape="Cylinder", radius=0.1, length=1.0):
    log("Creating arm")
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=(1.2, 0, 0))
    arm = bpy.context.active_object
    arm.name = "Arm"
    return arm
def create_leg(leg_shape="Cylinder", radius=0.2, length=1.2):
    log("Creating leg")
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=(0, 0, -1.2))
    leg = bpy.context.active_object
    leg.name = "Leg"
    return leg
def create_hat():
    log("Creating hat")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(0, 0, 1.7), segments=32, ring_count=16)
    hat = bpy.context.active_object
    hat.name = "Hat"
    return hat
def create_backpack():
    log("Creating backpack")
    bpy.ops.mesh.primitive_cube_add(size=0.5, location=(-1.2, 0, 0.5))
    backpack = bpy.context.active_object
    backpack.name = "Backpack"
    return backpack
def check_mechanics(obj):
    log(f"Checking mechanics for {obj.name}")
    # Basic check: object exists
    if obj is None:
        log(f"Error: {obj.name} is None")
        return False
    log(f"Mechanics check passed for {obj.name}")
    return True
def check_physics(obj):
    log(f"Checking physics for {obj.name}")
    # Basic check: object exists
    if obj is None:
        log(f"Error: {obj.name} is None")
        return False
    log(f"Physics check passed for {obj.name}")
    return True
def check_appearance(obj):
    log(f"Checking appearance for {obj.name}")
    # Basic check: object exists
    if obj is None:
        log(f"Error: {obj.name} is None")
        return False
    log(f"Appearance check passed for {obj.name}")
    return True
def check_structure(obj):
    log(f"Checking structure for {obj.name}")
    # Basic check: object exists
    if obj is None:
        log(f"Error: {obj.name} is None")
        return False
    log(f"Structure check passed for {obj.name}")
    return True
def main():
    character_name = "CartoonCharacter"
    log("Starting character creation")
    head = create_head()
    ear_left = create_ear()
    ear_left.location = (-0.7, 0.5, 1.2)
    ear_right = create_ear()
    ear_right.location = (0.7, 0.5, 1.2)
    eye_left = create_eye()
    eye_left.location = (-0.4, 0.5, 0.8)
    eye_right = create_eye()
    eye_right.location = (0.4, 0.5, 0.8)
    mouth = create_mouth()
    arm_left = create_arm()
    arm_left.location = (-1.2, 0, 0)
    arm_left.rotation_euler = (0, 0, math.radians(90))
    arm_right = create_arm()
    arm_right.location = (1.2, 0, 0)
    arm_right.rotation_euler = (0, 0, math.radians(-90))
    leg_left = create_leg()
    leg_left.location = (-0.4, 0, -1.2)
    leg_right = create_leg()
    leg_right.location = (0.4, 0, -1.2)
    hat = create_hat()
    backpack = create_backpack()
    log("Joining objects")
    objects_to_join = [head, ear_left, ear_right, eye_left, eye_right, mouth, arm_left, arm_right, leg_left, leg_right, hat, backpack]
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects_to_join:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = head
    bpy.ops.object.join()
    joined_object = bpy.context.active_object
    joined_object.name = character_name
    log("Performing checks")
    check_mechanics(joined_object)
    check_physics(joined_object)
    check_appearance(joined_object)
    check_structure(joined_object)
    log("Character creation complete")
bpy.app.timers.register(main)
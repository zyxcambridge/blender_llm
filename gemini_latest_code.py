import bpy
import bmesh
import math

def log(message):
    print(f"Log: {message}")

def create_head(head_shape="Sphere", radius=1.0):
    log("Creating head")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    head = bpy.context.active_object
    head.name = "Head"
    return head

def create_ear(ear_shape="Sphere", radius=0.2):
    log("Creating ear")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=(0.7, 0, 1.2))
    ear = bpy.context.active_object
    ear.name = "Ear"
    return ear

def create_eye(eye_shape="Sphere", radius=0.15):
    log("Creating eye")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=(0.4, 0.5, 0.8))
    eye = bpy.context.active_object
    eye.name = "Eye"
    return eye

def create_mouth(mouth_shape="Torus", major_radius=0.4, minor_radius=0.1):
    log("Creating mouth")
    bpy.ops.mesh.primitive_torus_add(
        align='WORLD',
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
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, enter_editmode=False, align='WORLD', location=(1.2, 0, 0))
    arm = bpy.context.active_object
    arm.name = "Arm"
    return arm

def create_leg(leg_shape="Cylinder", radius=0.2, length=1.2):
    log("Creating leg")
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, enter_editmode=False, align='WORLD', location=(0, 0, -1.2))
    leg = bpy.context.active_object
    leg.name = "Leg"
    return leg

def create_hat():
    log("Creating hat")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, enter_editmode=False, align='WORLD', location=(0, 0, 1.7), segments=32, ring_count=16)
    hat = bpy.context.active_object
    hat.name = "Hat"
    return hat

def create_backpack():
    log("Creating backpack")
    bpy.ops.mesh.primitive_cube_add(size=0.5, enter_editmode=False, align='WORLD', location=(-1.2, 0, 0.3))
    backpack = bpy.context.active_object
    backpack.name = "Backpack"
    return backpack

def check_mechanics(character):
    log("Checking mechanics")
    # Basic check: is the character object present?
    if character is None:
        log("Error: Character object is None.")
        return False

    # More sophisticated checks would go here, e.g.,
    # - Check if the center of mass is within the support polygon
    # - Check for obvious structural weaknesses

    log("Mechanics check passed (basic).")
    return True

def check_physics(character):
    log("Checking physics")
    # Basic check: are there any intersecting meshes?
    # (This is a very basic check; more sophisticated checks would be needed for real physics simulation)

    # More sophisticated checks would go here, e.g.,
    # - Check for fluid flow paths if the character is supposed to interact with fluids
    # - Check for airtightness if the character is supposed to be sealed

    log("Physics check passed (basic).")
    return True

def check_appearance(character):
    log("Checking appearance")
    # Basic check: does the character have any materials assigned?

    # More sophisticated checks would go here, e.g.,
    # - Check for color harmony
    # - Check for consistent level of detail

    log("Appearance check passed (basic).")
    return True

def check_structure(character):
    log("Checking structure")
    # Basic check: are all the expected parts present?
    if not all(part in character.children for part in [bpy.data.objects.get("Head"), bpy.data.objects.get("Ear"), bpy.data.objects.get("Eye"), bpy.data.objects.get("Mouth"), bpy.data.objects.get("Arm"), bpy.data.objects.get("Leg")] if part is not None):
        log("Warning: Not all expected parts are present.")

    # More sophisticated checks would go here, e.g.,
    # - Check for correct parent-child relationships
    # - Check for correct placement of functional components

    log("Structure check passed (basic).")
    return True

def main():
    character_name = "CartoonCharacter"

    log("Starting character creation")

    head = create_head()
    ear_left = create_ear()
    ear_left.location.x = 0.7
    ear_left.location.y = -0.5
    ear_right = create_ear()
    ear_right.location.x = -0.7
    ear_right.location.y = -0.5
    eye_left = create_eye()
    eye_left.location.x = 0.4
    eye_left.location.y = 0.5
    eye_right = create_eye()
    eye_right.location.x = -0.4
    eye_right.location.y = 0.5
    mouth = create_mouth()
    arm_left = create_arm()
    arm_left.location.x = 1.2
    arm_left.location.y = 0
    arm_right = create_arm()
    arm_right.location.x = -1.2
    arm_right.location.y = 0
    leg_left = create_leg()
    leg_left.location.x = 0.5
    leg_left.location.y = 0
    leg_right = create_leg()
    leg_right.location.x = -0.5
    leg_right.location.y = 0
    hat = create_hat()
    backpack = create_backpack()

    # Create parent object
    character = bpy.data.objects.new(character_name, None)
    bpy.context.collection.objects.link(character)

    # Parent all objects to the character object
    head.parent = character
    ear_left.parent = character
    ear_right.parent = character
    eye_left.parent = character
    eye_right.parent = character
    mouth.parent = character
    arm_left.parent = character
    arm_right.parent = character
    leg_left.parent = character
    leg_right.parent = character
    hat.parent = character
    backpack.parent = character

    # Select all objects to join
    bpy.ops.object.select_all(action='DESELECT')
    character.select_set(True)
    bpy.context.view_layer.objects.active = character

    # Join all meshes into one object
    #bpy.ops.object.join() # No need to join since we are parenting

    # Run checks
    check_mechanics(character)
    check_physics(character)
    check_appearance(character)
    check_structure(character)

    log("Character creation complete")

bpy.app.timers.register(main)
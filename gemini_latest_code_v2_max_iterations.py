import bpy
import math

def log(message):
    print(message)

def create_head(radius=1.0):
    log("Creating head")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    head = bpy.context.active_object
    head.name = "Head"
    return head

def create_eye(radius=0.1):
    log("Creating eye")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    eye = bpy.context.active_object
    eye.name = "Eye"
    return eye

def create_body(radius=0.3, length=1.5):
    log("Creating body")
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, enter_editmode=False, align='WORLD', location=(0, 0, -0.5))
    body = bpy.context.active_object
    body.name = "Body"
    return body

def create_arm(length=0.7):
    log("Creating arm")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=length, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    arm = bpy.context.active_object
    arm.name = "Arm"
    return arm

def create_leg(length=1.0):
    log("Creating leg")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=length, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    leg = bpy.context.active_object
    leg.name = "Leg"
    return leg

def create_hat(radius=0.6):
    log("Creating hat")
    bpy.ops.mesh.primitive_circle_add(radius=radius, enter_editmode=False, align='WORLD', location=(0, 0.5, 1.8))
    hat = bpy.context.active_object
    hat.name = "Hat"
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 0.3)})
    bpy.ops.object.mode_set(mode='OBJECT')
    return hat

def create_backpack(width=0.4, height=0.5, depth=0.2):
    log("Creating backpack")
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    backpack = bpy.context.active_object
    backpack.name = "Backpack"
    backpack.scale = (width, depth, height)
    return backpack

def add_material(obj, color=(1.0, 0.0, 0.0, 1.0)):  # RGBA
    material = bpy.data.materials.new(name="Material")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    obj.data.materials.append(material)

def create_symmetric_component(create_func, offset_x, parent_obj):
    left = create_func()
    left.location.x = offset_x
    left.parent = parent_obj
    right = create_func()
    right.location.x = -offset_x
    right.parent = parent_obj
    return left, right

def check_mechanics(character):
    log("Checking mechanics")
    # Basic check: ensure the character is not floating too high
    if character.location.z > 2:
        log("Warning: Character is floating too high.")

    # Check if head is parented
    if character.children:
        log("Character has children")
    else:
        log("Warning: Character has no children")

    # Add more sophisticated checks here, e.g., center of mass, stability, etc.
    # This is a placeholder for more advanced mechanics checks.
    log("Mechanics check complete.")

def create_character(character_name="CartoonCharacter"):
    # Create root object
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
    character = bpy.context.active_object
    character.name = character_name

    try:
        # Create components
        head = create_head()
        head.parent = character

        body = create_body()
        body.parent = character
        body.location.z = -0.5 # Adjust body position

        head.location.z = 1.0 # Adjust head position

        head_radius = 1.0
        eye_offset_x = head_radius * 0.4
        eye_offset_z = head_radius * 0.8

        eye_left, eye_right = create_symmetric_component(create_eye, eye_offset_x, head)
        eye_left.location.y = head_radius + 0.1
        eye_left.location.z = eye_offset_z
        eye_right.location.y = head_radius + 0.1
        eye_right.location.z = eye_offset_z

        arm_left, arm_right = create_symmetric_component(create_arm, 0.5, body)
        arm_left.location.z = 0.5
        arm_right.location.z = 0.5

        leg_left, leg_right = create_symmetric_component(create_leg, 0.3, body)
        leg_left.location.z = -1.5
        leg_right.location.z = -1.5

        hat = create_hat()
        hat.parent = head
        hat.location.z = 0.8 # Adjust hat position

        backpack = create_backpack()
        backpack.parent = body
        backpack.location.x = -head_radius - 0.2
        backpack.location.y = -0.3
        backpack.location.z = 0.2

        # Add materials
        add_material(head, (1.0, 0.8, 0.6, 1.0)) # Skin color
        add_material(body, (0.2, 0.4, 0.8, 1.0)) # Blue shirt
        add_material(arm_left, (1.0, 0.8, 0.6, 1.0))
        add_material(arm_right, (1.0, 0.8, 0.6, 1.0))
        add_material(leg_left, (0.2, 0.2, 0.2, 1.0)) # Dark pants
        add_material(leg_right, (0.2, 0.2, 0.2, 1.0))
        add_material(hat, (0.8, 0.2, 0.2, 1.0)) # Red hat
        add_material(backpack, (0.4, 0.2, 0.1, 1.0)) # Brown backpack

        check_mechanics(character)

    except Exception as e:
        log(f"Error creating character: {e}")

    return character

# Example usage:
create_character()
import bpy
import bmesh
import math

# --- Configuration ---
CHARACTER_NAME = "CartoonCharacter"
BODY_HEIGHT = 2.0
BODY_RADIUS = 0.5
HEAD_RADIUS = 1.0
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
JOINT_RADIUS = 0.07  # 球关节半径
NECK_HEIGHT = 0.3
NECK_RADIUS = 0.3

# --- Utility Functions ---
def log(message):
    print(f"Log: {message}")

def clear_scene():
    """Clears the scene of all objects."""
    log("Clearing scene")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_material(name, color=(0.8, 0.8, 0.8, 1.0)):  # Default: light gray
    """Creates a new material with the given name and color."""
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    return material

def assign_material(obj, material):
    """Assigns the given material to the object."""
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)

# --- Component Creation Functions ---
def create_body(parent, height=BODY_HEIGHT, radius=BODY_RADIUS):
    """Creates the body of the character."""
    log("Creating body")
    try:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, enter_editmode=False, align='WORLD', location=(0, 0, height/2))
        body = bpy.context.active_object
        body.name = "Body"
        body.parent = parent
        assign_material(body, create_material("BodyMaterial", (0.8, 0.2, 0.2, 1.0))) # Red
        return body
    except Exception as e:
        log(f"Error creating body: {e}")
        return None

def create_neck(parent, height=NECK_HEIGHT, radius=NECK_RADIUS, location=(0, 0, BODY_HEIGHT)):
    """Creates the neck of the character."""
    log("Creating neck")
    try:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, enter_editmode=False, align='WORLD', location=location)
        neck = bpy.context.active_object
        neck.name = "Neck"
        neck.parent = parent
        assign_material(neck, create_material("NeckMaterial", (0.9, 0.7, 0.3, 1.0))) # Skin color
        return neck
    except Exception as e:
        log(f"Error creating neck: {e}")
        return None

def create_head(parent, radius=HEAD_RADIUS, location=(0, 0, NECK_HEIGHT)):
    """Creates the head of the character."""
    log("Creating head")
    try:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location)
        head = bpy.context.active_object
        head.name = "Head"
        head.parent = parent
        assign_material(head, create_material("HeadMaterial", (0.9, 0.7, 0.3, 1.0))) # Skin color
        return head
    except Exception as e:
        log(f"Error creating head: {e}")
        return None

def create_symmetric_component(create_func, parent, location, **kwargs):
    """Creates a component and its symmetric counterpart by mirroring."""
    try:
        obj = create_func(parent, location=location, **kwargs)
        if obj:
            # Duplicate the object
            obj_right = obj.copy()
            obj_right.data = obj.data.copy()  # Duplicate mesh data as well
            obj_right.name = obj.name + "_Right"
            bpy.context.collection.objects.link(obj_right)  # Add to the scene

            # Mirror the object along the X axis
            obj_right.scale.x = -1
            obj_right.location.x = -location[0]

            return obj
        else:
            return None
    except Exception as e:
        log(f"Error creating symmetric component: {e}")
        return None

def create_ear(parent, radius=EAR_RADIUS, location=(HEAD_RADIUS * 0.7, HEAD_RADIUS * 0.5, HEAD_RADIUS * 0.6)):
    """Creates an ear for the character."""
    log("Creating ear")
    try:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location)
        ear = bpy.context.active_object
        ear.name = "Ear"
        ear.parent = parent
        assign_material(ear, create_material("EarMaterial", (0.9, 0.7, 0.3, 1.0))) # Skin color
        return ear
    except Exception as e:
        log(f"Error creating ear: {e}")
        return None

def create_eye(parent, radius=EYE_RADIUS, location=(HEAD_RADIUS * 0.4, HEAD_RADIUS * 0.5, HEAD_RADIUS * 0.3)):
    """Creates an eye for the character."""
    log("Creating eye")
    try:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location)
        eye = bpy.context.active_object
        eye.name = "Eye"
        eye.parent = parent
        assign_material(eye, create_material("EyeMaterial", (0.1, 0.1, 0.1, 1.0))) # Black
        return eye
    except Exception as e:
        log(f"Error creating eye: {e}")
        return None

def create_mouth(parent, major_radius=MOUTH_MAJOR_RADIUS, minor_radius=MOUTH_MINOR_RADIUS, location=(0, -HEAD_RADIUS * 0.6, -HEAD_RADIUS * 0.3)):
    """Creates a mouth for the character."""
    log("Creating mouth")
    try:
        bpy.ops.mesh.primitive_torus_add(
            align='WORLD',
            location=location,
            rotation=(math.radians(90), 0, 0), # Rotate to be horizontal
            major_radius=major_radius,
            minor_radius=minor_radius
        )
        mouth = bpy.context.active_object
        mouth.name = "Mouth"
        mouth.parent = parent
        assign_material(mouth, create_material("MouthMaterial", (0.8, 0.1, 0.1, 1.0))) # Dark red
        return mouth
    except Exception as e:
        log(f"Error creating mouth: {e}")
        return None

def create_arm(parent, location, radius=ARM_RADIUS, length=ARM_LENGTH):
    """Creates an arm for the character."""
    log("Creating arm")
    try:
        # Create arm
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, enter_editmode=False, align='WORLD', location=location)
        arm = bpy.context.active_object
        arm.name = "Arm"
        arm.parent = parent
        arm.rotation_euler = (math.radians(90), 0, 0) # Rotate to stick out
        assign_material(arm, create_material("ArmMaterial", (0.9, 0.7, 0.3, 1.0))) # Skin color
        return arm
    except Exception as e:
        log(f"Error creating arm: {e}")
        return None

def create_leg(parent, location, radius=LEG_RADIUS, length=LEG_LENGTH):
    """Creates a leg for the character."""
    log("Creating leg")
    try:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, enter_editmode=False, align='WORLD', location=location)
        leg = bpy.context.active_object
        leg.name = "Leg"
        leg.parent = parent
        assign_material(leg, create_material("LegMaterial", (0.2, 0.2, 0.8, 1.0))) # Blue
        return leg
    except Exception as e:
        log(f"Error creating leg: {e}")
        return None

def create_hat(parent, location=(0, 0, HEAD_RADIUS * 1.1)):
    """Creates a hat for the character."""
    log("Creating hat")
    try:
        bpy.ops.mesh.primitive_cone_add(radius1=HAT_RADIUS, depth=HAT_RADIUS * 1.2, enter_editmode=False, align='WORLD', location=location)
        hat = bpy.context.active_object
        hat.name = "Hat"
        hat.parent = parent
        assign_material(hat, create_material("HatMaterial", (0.2, 0.8, 0.2, 1.0))) # Green
        return hat
    except Exception as e:
        log(f"Error creating hat: {e}")
        return None

def create_backpack(parent, location=(-BODY_RADIUS - BACKPACK_SIZE/2, 0, BODY_HEIGHT * 0.5)):
    """Creates a backpack for the character."""
    log("Creating backpack")
    try:
        bpy.ops.mesh.primitive_cube_add(size=BACKPACK_SIZE, enter_editmode=False, align='WORLD', location=location)
        backpack = bpy.context.active_object
        backpack.name = "Backpack"
        backpack.parent = parent
        assign_material(backpack, create_material("BackpackMaterial", (0.5, 0.3, 0.1, 1.0))) # Brown
        return backpack
    except Exception as e:
        log(f"Error creating backpack: {e}")
        return None

# --- Validation Functions ---
def check_mechanics(character):
    log("Checking mechanics")
    if character is None:
        log("Error: Character object is None.")
        return False

    # Example: Check if the head is above the body
    head = bpy.data.objects.get("Head")
    body = bpy.data.objects.get("Body")
    if head and body:
        if head.location.z <= body.location.z + BODY_HEIGHT:
            log("Warning: Head is not positioned correctly above the body.")

    log("Mechanics check passed (basic).")
    return True

def check_physics(character):
    log("Checking physics")
    if character is None:
        log("Error: Character object is None.")
        return False

    # Example: Check for intersecting geometry (very basic)
    # This is a placeholder; proper collision detection is complex
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj != character:
            # Check distance between object origins
            distance = (character.location - obj.location).length
            if distance < 0.1:  # Arbitrary threshold
                log(f"Warning: Object {obj.name} is very close to the character.")

    log("Physics check passed (basic).")
    return True

def check_appearance(character):
    log("Checking appearance")
    if character is None:
        log("Error: Character object is None.")
        return False

    # Example: Check for consistent material properties (very basic)
    # This is a placeholder; proper appearance checks are subjective
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if obj.data.materials:
                material = obj.data.materials[0]
                if material:
                    if "Base Color" in material.node_tree.nodes["Principled BSDF"].inputs:
                        color = material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value
                        if sum(color[:3]) / 3 < 0.2: # Check if the color is too dark
                            log(f"Warning: Object {obj.name} has a very dark material.")

    log("Appearance check passed (basic).")
    return True

def check_structure(character):
    log("Checking structure")
    if character is None:
        log("Error: Character object is None.")
        return False

    # Example: Check for correct object hierarchy
    # This is a placeholder; proper hierarchy checks depend on the intended structure
    body = bpy.data.objects.get("Body")
    if body:
        for obj in bpy.data.objects:
            if obj.parent == character and obj != body:
                log(f"Warning: Object {obj.name} is directly parented to the character, not the Body.")

    log("Structure check passed (basic).")
    return True

# --- Main Function ---
def main():
    log("Starting character creation...")

    # Clear existing scene
    clear_scene()

    # Create the character object (Empty)
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
    character = bpy.context.active_object
    character.name = CHARACTER_NAME

    # Create body and parent it to the character
    body = create_body(character)
    if not body:
        log("Failed to create body. Aborting.")
        return

    # Create neck and parent it to the body
    neck = create_neck(body)
    if not neck:
        log("Failed to create neck. Aborting.")
        return

    # Create components and parent them to the neck
    head = create_head(neck)
    if not head:
        log("Failed to create head. Aborting.")
        return

    # Create ears
    ear_location_left = (HEAD_RADIUS * 0.7, HEAD_RADIUS * 0.5, HEAD_RADIUS * 0.6)
    ear_left = create_symmetric_component(create_ear, head, ear_location_left)
    if ear_left:
        ear_left.name = "Ear_Left"

    # Create eyes
    eye_location_left = (HEAD_RADIUS * 0.4, HEAD_RADIUS * 0.5, HEAD_RADIUS * 0.3)
    eye_left = create_symmetric_component(create_eye, head, eye_location_left)
    if eye_left:
        eye_left.name = "Eye_Left"

    # Mirror ears and eyes
    for obj_name in ["Ear", "Eye"]:
        obj_left = bpy.data.objects.get(f"{obj_name}_Left")
        if obj_left:
            obj_right = obj_left.copy()
            obj_right.data = obj_left.data.copy()
            obj_right.name = f"{obj_name}_Right"
            bpy.context.collection.objects.link(obj_right)
            obj_right.scale.x = -1
            obj_right.location.x = -obj_left.location.x

    mouth = create_mouth(head)

    # Arm joint location relative to the body
    arm_y_offset = BODY_RADIUS + ARM_RADIUS  # Move arms slightly forward
    arm_z_offset = BODY_HEIGHT * 0.7
    arm_location_left = (BODY_RADIUS + ARM_RADIUS, arm_y_offset, arm_z_offset)
    arm_left = create_symmetric_component(create_arm, body, arm_location_left)
    if arm_left:
        arm_left.name = "Arm_Left"

    # Leg joint location relative to the body
    leg_y_offset = BODY_RADIUS/2  # Move legs slightly forward
    leg_z_offset = 0
    leg_location_left = (BODY_RADIUS/2, leg_y_offset, leg_z_offset)
    leg_left = create_symmetric_component(create_leg, body, leg_location_left)
    if leg_left:
        leg_left.name = "Leg_Left"

    # Mirror arms and legs
    for obj_name in ["Arm", "Leg"]:
        obj_left = bpy.data.objects.get(f"{obj_name}_Left")
        if obj_left:
            obj_right = obj_left.copy()
            obj_right.data = obj_left.data.copy()
            obj_right.name = f"{obj_name}_Right"
            bpy.context.collection.objects.link(obj_right)
            obj_right.scale.x = -1
            obj_right.location.x = -obj_left.location.x

    hat = create_hat(head)
    backpack = create_backpack(body)

    # Select the character
    bpy.context.view_layer.objects.active = character
    character.select_set(True)

    # Perform checks
    check_mechanics(character)
    check_physics(character)
    check_appearance(character)
    check_structure(character)

    log("Character creation complete.")

# --- Run the script ---
bpy.app.timers.register(main)
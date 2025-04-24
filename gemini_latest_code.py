import bpy
import bmesh
import math

def log(message):
    print(f"Log: {message}")

def clear_scene():
    log("Clearing scene")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_head(head_shape="Sphere", radius=1.0, location=(0, 0, 1.0)):
    log("Creating head")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location)
    head = bpy.context.active_object
    head.name = "Head"

    # Add a simple material
    material = bpy.data.materials.new(name="HeadMaterial")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.8, 0.2, 0.2, 1)  # Reddish color
    head.data.materials.append(material)

    return head

def create_ear(ear_shape="Sphere", radius=0.2, location=(0.7, 0, 1.2)):
    log("Creating ear")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location)
    ear = bpy.context.active_object
    ear.name = "Ear"

    # Add a simple material
    material = bpy.data.materials.new(name="EarMaterial")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.8, 0.5, 0.2, 1)  # Orange color
    ear.data.materials.append(material)

    return ear

def create_eye(eye_shape="Sphere", radius=0.15, location=(0.4, 0.5, 0.8)):
    log("Creating eye")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location)
    eye = bpy.context.active_object
    eye.name = "Eye"

    # Add a simple material
    material = bpy.data.materials.new(name="EyeMaterial")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1)  # Black color
    eye.data.materials.append(material)

    return eye

def create_mouth(mouth_shape="Torus", major_radius=0.4, minor_radius=0.1, location=(0, -0.6, 0.7)):
    log("Creating mouth")
    bpy.ops.mesh.primitive_torus_add(
        align='WORLD',
        location=location,
        rotation=(0, 0, 0),
        major_radius=major_radius,
        minor_radius=minor_radius
    )
    mouth = bpy.context.active_object
    mouth.name = "Mouth"

    # Add a simple material
    material = bpy.data.materials.new(name="MouthMaterial")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.9, 0.1, 0.1, 1)  # Dark Red color
    mouth.data.materials.append(material)

    return mouth

def create_arm(arm_shape="Cylinder", radius=0.1, length=1.0, location=(1.2, 0, 0)):
    log("Creating arm")
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, enter_editmode=False, align='WORLD', location=location)
    arm = bpy.context.active_object
    arm.name = "Arm"

    # Add a simple material
    material = bpy.data.materials.new(name="ArmMaterial")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.7, 0.7, 0.7, 1)  # Gray color
    arm.data.materials.append(material)

    return arm

def create_leg(leg_shape="Cylinder", radius=0.2, length=1.2, location=(0, 0, -1.2)):
    log("Creating leg")
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, enter_editmode=False, align='WORLD', location=location)
    leg = bpy.context.active_object
    leg.name = "Leg"

    # Add a simple material
    material = bpy.data.materials.new(name="LegMaterial")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.7, 0.7, 0.7, 1)  # Gray color
    leg.data.materials.append(material)

    return leg

def create_hat(location=(0, 0, 1.7)):
    log("Creating hat")
    bpy.ops.mesh.primitive_cone_add(radius1=0.6, depth=0.8, enter_editmode=False, align='WORLD', location=location)
    hat = bpy.context.active_object
    hat.name = "Hat"

    # Add a simple material
    material = bpy.data.materials.new(name="HatMaterial")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.8, 1)  # Blue color
    hat.data.materials.append(material)

    return hat

def create_backpack(location=(-1.2, 0, 0)):
    log("Creating backpack")
    bpy.ops.mesh.primitive_cube_add(size=0.5, enter_editmode=False, align='WORLD', location=location)
    backpack = bpy.context.active_object
    backpack.name = "Backpack"

    # Add a simple material
    material = bpy.data.materials.new(name="BackpackMaterial")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.3, 0.8, 0.3, 1)  # Green color
    backpack.data.materials.append(material)

    return backpack

def check_mechanics(character):
    log("Checking mechanics")
    # Basic check: ensure the character has a leg and a head
    has_leg = False
    has_head = False
    for obj in character.children:
        if "Leg" in obj.name:
            has_leg = True
        if "Head" in obj.name:
            has_head = True

    if not has_leg:
        log("Warning: Character has no legs!")
    if not has_head:
        log("Warning: Character has no head!")

    # Check for balance (very basic)
    total_weight = 0
    center_of_mass = [0, 0, 0]
    for obj in character.children:
        # Assume each object has a weight proportional to its volume
        volume = obj.scale[0] * obj.scale[1] * obj.scale[2]  # Very rough approximation
        weight = volume
        total_weight += weight
        center_of_mass[0] += obj.location[0] * weight
        center_of_mass[1] += obj.location[1] * weight
        center_of_mass[2] += obj.location[2] * weight

    if total_weight > 0:
        center_of_mass[0] /= total_weight
        center_of_mass[1] /= total_weight
        center_of_mass[2] /= total_weight

        log(f"Approximate Center of Mass: {center_of_mass}")

        # Check if the center of mass is above the support (legs)
        if center_of_mass[2] < -0.5:  # Assuming legs are around -1.2
            log("Warning: Center of mass is too low. Character may be unstable.")

def check_physics(character):
    log("Checking physics")
    # Placeholder for physics checks.  More sophisticated checks would require
    # simulation or analysis.
    pass

def check_appearance(character):
    log("Checking appearance")
    # Placeholder for appearance checks.  This would ideally involve
    # evaluating proportions and aesthetics.
    pass

def check_structure(character):
    log("Checking structure")
    # Placeholder for structure checks.  This would involve verifying
    # that parts are connected correctly.
    pass

def main():
    character_name = "CartoonCharacter"

    clear_scene()

    # Create components
    head = create_head()
    ear_left = create_ear()
    ear_right = create_ear(location=(-ear_left.location.x, ear_left.location.y, ear_left.location.z))
    eye_left = create_eye()
    eye_right = create_eye(location=(-eye_left.location.x, eye_left.location.y, eye_left.location.z))
    mouth = create_mouth()
    arm_left = create_arm()
    arm_right = create_arm(location=(-arm_left.location.x, arm_left.location.y, arm_left.location.z))
    leg_left = create_leg()
    leg_right = create_leg(location=(-leg_left.location.x, leg_left.location.y, leg_left.location.z))
    hat = create_hat()
    backpack = create_backpack()

    # Create an empty object to act as the parent for the entire character
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
    character = bpy.context.active_object
    character.name = character_name

    # Parent components to the character (head not linked)
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
    head.parent = character

    # Perform checks
    check_mechanics(character)
    check_physics(character)
    check_appearance(character)
    check_structure(character)

    log("Character creation complete.")

bpy.app.timers.register(main)
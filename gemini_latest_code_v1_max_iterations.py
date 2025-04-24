import bpy
import bmesh
import math

def log(message):
    print(f"Log: {message}")

def create_head(head_shape="Sphere", radius=1.0, material_name="HeadMaterial"):
    log("Creating head")
    try:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=(0, 0, 0))
        head = bpy.context.object
        head.name = "Head"
        add_material(head, material_name)
        return head
    except Exception as e:
        log(f"Error creating head: {e}")
        return None

def create_body(body_height=2.0, body_radius=0.5, material_name="BodyMaterial"):
    log("Creating body")
    try:
        bpy.ops.mesh.primitive_cylinder_add(radius=body_radius, depth=body_height, align='WORLD', location=(0, 0, -body_height/2))
        body = bpy.context.object
        body.name = "Body"
        add_material(body, material_name)
        return body
    except Exception as e:
        log(f"Error creating body: {e}")
        return None

def create_ear(head, ear_shape="Sphere", radius=0.2, offset=(0.6, 0, 0.8), material_name="EarMaterial"):
    log("Creating ear")
    try:
        ear_location = (head.location.x + offset[0], head.location.y + offset[1], head.location.z + offset[2])
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=ear_location)
        ear = bpy.context.object
        ear.name = "Ear"
        ear.parent = head
        add_material(ear, material_name)
        return ear
    except Exception as e:
        log(f"Error creating ear: {e}")
        return None

def create_eye(head, eye_shape="Sphere", radius=0.15, offset=(0.4, 0.5, 0.3), material_name="EyeMaterial"):
    log("Creating eye")
    try:
        eye_location = (head.location.x + offset[0], head.location.y + offset[1], head.location.z + offset[2])
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=eye_location)
        eye = bpy.context.object
        eye.name = "Eye"
        eye.parent = head
        add_material(eye, material_name)
        return eye
    except Exception as e:
        log(f"Error creating eye: {e}")
        return None

def create_mouth(head, mouth_shape="Torus", major_radius=0.4, minor_radius=0.1, offset=(0, -0.6, -0.2), material_name="MouthMaterial"):
    log("Creating mouth")
    try:
        mouth_location = (head.location.x + offset[0], head.location.y + offset[1], head.location.z + offset[2])
        bpy.ops.mesh.primitive_torus_add(
            align='WORLD',
            location=mouth_location,
            rotation=(0, 0, 0),
            major_radius=major_radius,
            minor_radius=minor_radius
        )
        mouth = bpy.context.object
        mouth.name = "Mouth"
        mouth.parent = head
        add_material(mouth, material_name)
        return mouth
    except Exception as e:
        log(f"Error creating mouth: {e}")
        return None

def create_arm(body, arm_shape="Cylinder", length=1.0, radius=0.1, offset=(0.7, 0, 0.7), material_name="ArmMaterial"):
    log("Creating arm")
    try:
        arm_location = (body.location.x + offset[0], body.location.y + offset[1], body.location.z + body.dimensions.z/2 + offset[2])
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, align='WORLD', location=arm_location)
        arm = bpy.context.object
        arm.name = "Arm"
        arm.parent = body
        add_material(arm, material_name)
        return arm
    except Exception as e:
        log(f"Error creating arm: {e}")
        return None

def create_leg(body, leg_shape="Cylinder", length=1.2, radius=0.2, offset=(0.2, -1.0, 0), material_name="LegMaterial"):
    log("Creating leg")
    try:
        leg_location = (body.location.x + offset[0], body.location.y + offset[1], body.location.z + offset[2])
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, align='WORLD', location=leg_location)
        leg = bpy.context.object
        leg.name = "Leg"
        leg.parent = body
        add_material(leg, material_name)
        return leg
    except Exception as e:
        log(f"Error creating leg: {e}")
        return None

def create_hat(head, radius=0.6, offset=(0, 0, 0.7), material_name="HatMaterial"):
    log("Creating hat")
    try:
        hat_location = (head.location.x + offset[0], head.location.y + offset[1], head.location.z + head.dimensions.z/2 + offset[2])
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=hat_location)
        hat = bpy.context.object
        hat.name = "Hat"
        add_material(hat, material_name)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.view_layer.objects.active = hat
        hat_mesh = bmesh.new()
        hat_mesh.from_mesh(hat.data)

        verts_to_remove = [v for v in hat_mesh.verts if v.co.z < hat_location[2]]
        bmesh.ops.delete(hat_mesh, geom=verts_to_remove, context='VERTS')

        hat_mesh.to_mesh(hat.data)
        hat.data.update()
        hat_mesh.free()
        bpy.ops.object.mode_set(mode='OBJECT')

        return hat
    except Exception as e:
        log(f"Error creating hat: {e}")
        return None

def create_backpack(body, size=(0.5, 0.3, 0.7), offset=(0, 0.1, 0.5), material_name="BackpackMaterial"):
    log("Creating backpack")
    try:
        backpack_location = (body.location.x + offset[0], body.location.y + offset[1], body.location.z + body.dimensions.z/2 + offset[2])
        bpy.ops.mesh.primitive_cube_add(size=1, align='WORLD', location=backpack_location)
        backpack = bpy.context.object
        backpack.name = "Backpack"
        backpack.scale = size
        backpack.parent = body
        add_material(backpack, material_name)
        return backpack
    except Exception as e:
        log(f"Error creating backpack: {e}")
        return None

def add_material(obj, material_name, color=(0.8, 0.8, 0.8, 1)):
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
        log(f"Error adding material {material_name}: {e}")

def check_mechanics(character):
    log("Checking mechanics")
    if character.location.z > 0:
        log("Warning: Character is floating in the air.")
    else:
        log("Character is grounded.")

def check_physics(character):
    log("Checking physics")
    log("Physics checks are placeholder.")

def check_appearance(character):
    log("Checking appearance")
    log("Appearance checks are placeholder.")

def check_structure(character):
    log("Checking structure")
    log("Structure checks are placeholder.")

def scale_character(character, scale_factor=1.0):
    log(f"Scaling character by: {scale_factor}")
    character.scale = (scale_factor, scale_factor, scale_factor)

def main():
    try:
        character_name = "CartoonCharacter"
        log(f"Creating character: {character_name}")

        bpy.ops.object.select_all(action='DESELECT')

        body = create_body()
        if not body:
            return

        head = create_head()
        if not head:
            return

        head.location.z = body.location.z + body.dimensions.z/2 + head.dimensions.z/2
        head.parent = body

        ear_left = create_ear(head, offset=(-0.6, 0, 0.8))
        ear_right = create_ear(head, offset=(0.6, 0, 0.8))
        eye_left = create_eye(head, offset=(-0.4, 0.5, 0.3))
        eye_right = create_eye(head, offset=(0.4, 0.5, 0.3))
        mouth = create_mouth(head, offset=(0, -0.6, -0.2))
        arm_left = create_arm(body, offset=(-0.7, 0, 0.7))
        arm_right = create_arm(body, offset=(0.7, 0, 0.7))
        leg_left = create_leg(body, offset=(-0.2, -1.0, 0))
        leg_right = create_leg(body, offset=(0.2, -1.0, 0))
        hat = create_hat(head)
        backpack = create_backpack(body)

        bpy.context.view_layer.objects.active = body
        body.name = character_name

        check_mechanics(body)
        check_physics(body)
        check_appearance(body)
        check_structure(body)

        scale_character(body, 1.2)

        log("Character creation complete.")

    except Exception as e:
        log(f"Error during character creation: {e}")

bpy.app.timers.register(main)
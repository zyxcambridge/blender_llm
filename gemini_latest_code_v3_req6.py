import bpy
import bmesh
import math

def log(message):
    print(f"Log: {message}")

def create_head(head_shape="Sphere", radius=1.0, location=(0, 0, 2.0)):
    log("Creating head")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=location)
    head = bpy.context.active_object
    head.name = "Head"
    return head

def create_face(head):
    face = bpy.data.objects.new("Face", None)
    bpy.context.collection.objects.link(face)
    face.parent = head
    face.matrix_parent_inverse = head.matrix_world.inverted()
    return face

def create_symmetric_part(part_type, radius, length, location, rotation, name_prefix):
    log(f"Creating symmetric part: {name_prefix}")
    if part_type == "arm":
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, align='WORLD', location=location, rotation=rotation)
    elif part_type == "leg":
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, align='WORLD', location=location, rotation=rotation)
    elif part_type == "ear":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=location)
    elif part_type == "eye":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=location)
    else:
        log(f"Error: Unknown part type: {part_type}")
        return None

    part = bpy.context.active_object
    part.name = name_prefix
    return part

def create_arm(radius=0.1, length=0.7, location=(0.6, 0, -0.0), rotation=(math.radians(90), 0, 0)):
    log("Creating arm")
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, align='WORLD', location=location, rotation=rotation)
    arm = bpy.context.active_object
    arm.name = "Arm"
    return arm

def create_leg(radius=0.2, length=0.8, location=(0.3, 0, -1.3), rotation=(math.radians(90), 0, 0)):
    log("Creating leg")
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, align='WORLD', location=location, rotation=rotation)
    leg = bpy.context.active_object
    leg.name = "Leg"
    return leg

def create_body(size=1.0, location=(0, 0, 0.0)):
    log("Creating body")
    bpy.ops.mesh.primitive_cube_add(size=size, align='WORLD', location=location)
    body = bpy.context.active_object
    body.name = "Body"
    return body

def create_shoulder(radius=0.15, location=(0.6, 0, 0.0)):
    log("Creating shoulder")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=location)
    shoulder = bpy.context.active_object
    shoulder.name = "Shoulder"
    return shoulder

def create_hand(radius=0.1, location=(0.8, 0, 0.0)):
    log("Creating hand")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=location)
    hand = bpy.context.active_object
    hand.name = "Hand"
    return hand

def create_foot(radius=0.2, location=(0.3, 0, -2.1)):
    log("Creating foot")
    bpy.ops.mesh.primitive_cube_add(size=0.4, align='WORLD', location=location)
    foot = bpy.context.active_object
    foot.name = "Foot"
    return foot

def create_hat(location=(0, 0, 2.7)):
    log("Creating hat")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, align='WORLD', location=location, segments=32, ring_count=16)
    hat = bpy.context.active_object
    hat.name = "Hat"
    return hat

def create_backpack(location=(-0.6, -0.3, 0.2)):
    log("Creating backpack")
    bpy.ops.mesh.primitive_cube_add(size=0.5, align='WORLD', location=location)
    backpack = bpy.context.active_object
    backpack.name = "Backpack"
    return backpack

def create_mouth(major_radius=0.4, minor_radius=0.1, location=(0, -0.4, 1.2)):
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
    return mouth

def calculate_center_of_mass(objects):
    total_mass = 0
    weighted_sum = [0, 0, 0]
    for obj in objects:
        volume = obj.data.volume if obj.type == 'MESH' and obj.data else 1
        total_mass += volume
        weighted_sum[0] += obj.location.x * volume
        weighted_sum[1] += obj.location.y * volume
        weighted_sum[2] += obj.location.z * volume

    if total_mass > 0:
        center_of_mass = [coord / total_mass for coord in weighted_sum]
        return center_of_mass
    else:
        return [0, 0, 0]

def check_mechanics(obj):
    log(f"Checking mechanics for {obj.name}")
    if obj.type == 'MESH' and obj.data:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        isolated_verts = [v for v in bm.verts if len(v.link_edges) == 0]
        if isolated_verts:
            log(f"Warning: {obj.name} has {len(isolated_verts)} isolated vertices.")
        bm.free()
    else:
        log(f"Warning: {obj.name} has no valid mesh data.")

def check_physics(obj):
    log(f"Checking physics for {obj.name}")
    if obj.type == 'MESH' and obj.data:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        for face in bm.faces:
            for other_face in bm.faces:
                if face != other_face:
                    if face.calc_center().distance(other_face.calc_center()) < 0.01:
                        log(f"Warning: {obj.name} has faces that are very close to each other (potential self-intersection).")
                        break
        bm.free()
    else:
        log(f"Warning: {obj.name} has no valid mesh data.")

def check_appearance(obj):
    log(f"Checking appearance for {obj.name}")
    if obj.type == 'MESH' and obj.data.materials:
        pass
    else:
        log(f"Warning: {obj.name} has no material assigned.")

def check_structure(obj):
    log(f"Checking structure for {obj.name}")
    if obj.type == 'MESH' and obj.data:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        non_manifold_edges = [e for e in bm.edges if e.is_manifold == False]
        if non_manifold_edges:
            log(f"Warning: {obj.name} has {len(non_manifold_edges)} non-manifold edges.")
        bm.free()
    else:
        log(f"Warning: {obj.name} has no valid mesh data.")

def main(body_size=1.0, head_radius=0.5, arm_length=0.7, leg_length=0.8):
    character_name = "CartoonCharacter"

    body = create_body(size=body_size)
    head = create_head(radius=head_radius, location=(0, 0, body_size + head_radius))

    face = create_face(head)

    ear_left = create_symmetric_part("ear", 0.2, 0, (0.7, 0, 0.7), (0, 0, 0), "Ear_Left")
    ear_right = create_symmetric_part("ear", 0.2, 0, (-0.7, 0, 0.7), (0, 0, 0), "Ear_Right")
    eye_left = create_symmetric_part("eye", 0.15, 0, (0.4, 0.6, 0.3), (0, 0, 0), "Eye_Left")
    eye_right = create_symmetric_part("eye", 0.15, 0, (-0.4, 0.6, 0.3), (0, 0, 0), "Eye_Right")
    mouth = create_mouth(location=(0, -0.4, 0.1))

    if ear_left:
        ear_left.parent = face
        ear_left.matrix_parent_inverse = face.matrix_world.inverted()
    if ear_right:
        ear_right.parent = face
        ear_right.matrix_parent_inverse = face.matrix_world.inverted()
    if eye_left:
        eye_left.parent = face
        eye_left.matrix_parent_inverse = face.matrix_world.inverted()
    if eye_right:
        eye_right.parent = face
        eye_right.matrix_parent_inverse = face.matrix_world.inverted()
    mouth.parent = face
    mouth.matrix_parent_inverse = face.matrix_world.inverted()

    shoulder_left = create_shoulder(location=(body_size/2 + 0.05, 0, body_size/2))
    shoulder_right = create_shoulder(location=(-body_size/2 - 0.05, 0, body_size/2))

    arm_left = create_arm(length=arm_length, location=(body_size/2 + 0.15 + arm_length/2, 0, body_size/2), rotation=(math.radians(90), 0, 0))
    arm_right = create_arm(length=arm_length, location=(-body_size/2 - 0.15 - arm_length/2, 0, body_size/2), rotation=(math.radians(90), 0, 0))

    hand_left = create_hand(location=(body_size/2 + 0.15 + arm_length + 0.1, 0, body_size/2))
    hand_right = create_hand(location=(-body_size/2 - 0.15 - arm_length - 0.1, 0, body_size/2))

    leg_left = create_leg(length=leg_length, location=(body_size/4, 0, -leg_length/2), rotation=(math.radians(90), 0, 0))
    leg_right = create_leg(length=leg_length, location=(-body_size/4, 0, -leg_length/2), rotation=(math.radians(90), 0, 0))

    foot_left = create_foot(location=(body_size/4, 0, -leg_length - 0.2))
    foot_right = create_foot(location=(-body_size/4, 0, -leg_length - 0.2))

    hat = create_hat(location=(0, 0, body_size + head_radius + 0.2))
    backpack = create_backpack(location=(-body_size/2 - 0.1, -body_size/4, body_size/4))

    hat.parent = head
    hat.matrix_parent_inverse = head.matrix_world.inverted()

    backpack.parent = body
    backpack.matrix_parent_inverse = body.matrix_world.inverted()

    head.parent = body
    head.matrix_parent_inverse = body.matrix_world.inverted()

    shoulder_left.parent = body
    shoulder_left.matrix_parent_inverse = body.matrix_world.inverted()
    shoulder_right.parent = body
    shoulder_right.matrix_parent_inverse = body.matrix_world.inverted()

    arm_left.parent = shoulder_left
    arm_left.matrix_parent_inverse = shoulder_left.matrix_world.inverted()
    arm_right.parent = shoulder_right
    arm_right.matrix_parent_inverse = shoulder_right.matrix_world.inverted()

    hand_left.parent = arm_left
    hand_left.matrix_parent_inverse = arm_left.matrix_world.inverted()
    hand_right.parent = arm_right
    hand_right.matrix_parent_inverse = arm_right.matrix_world.inverted()

    leg_left.parent = body
    leg_left.matrix_parent_inverse = body.matrix_world.inverted()
    leg_right.parent = body
    leg_right.matrix_parent_inverse = body.matrix_world.inverted()

    foot_left.parent = leg_left
    foot_left.matrix_parent_inverse = leg_left.matrix_world.inverted()
    foot_right.parent = leg_right
    foot_right.matrix_parent_inverse = leg_right.matrix_world.inverted()

    objects_for_com = [body, head, ear_left, ear_right, eye_left, eye_right, mouth, arm_left, arm_right, leg_left, leg_right, hat, backpack, shoulder_left, shoulder_right, hand_left, hand_right, foot_left, foot_right]
    center_of_mass = calculate_center_of_mass(objects_for_com)
    log(f"Center of mass: {center_of_mass}")

    bpy.ops.object.select_all(action='DESELECT')
    objects_to_join = [obj for obj in objects_for_com if obj is not None]

    for obj in objects_to_join:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    body.name = character_name

    check_mechanics(body)
    check_physics(body)
    check_appearance(body)
    check_structure(body)

    log("Finished creating character")

bpy.app.timers.register(lambda: main(body_size=1.2, head_radius=0.6, arm_length=0.8, leg_length=0.9))
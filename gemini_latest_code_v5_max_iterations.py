import bpy
import bmesh
import math

def log(message):
    print(f"Log: {message}")

def create_head(head_shape="Sphere", radius=1.0, location=(0, 0, 2.0)):
    log("Creating head")
    try:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=location)
        head = bpy.context.active_object
        head.name = "Head"
        return head
    except Exception as e:
        log(f"Error creating head: {e}")
        return None

def create_neck(radius=0.3, length=0.5, location=(0, 0, 0.5)):
    log("Creating neck")
    try:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, align='WORLD', location=location)
        neck = bpy.context.active_object
        neck.name = "Neck"
        return neck
    except Exception as e:
        log(f"Error creating neck: {e}")
        return None

def create_symmetric_part(part_type, radius, length, location, rotation, name_prefix):
    log(f"Creating symmetric part: {name_prefix}")
    try:
        if part_type == "arm":
            bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, align='WORLD', location=location, rotation=rotation)
        elif part_type == "leg":
            bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, align='WORLD', location=location, rotation=rotation)
        elif part_type == "ear":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=location)
        elif part_type == "eye":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=location)
        elif part_type == "elbow_joint" or part_type == "knee_joint":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=location)
        else:
            log(f"Error: Unknown part type: {part_type}")
            return None

        part = bpy.context.active_object
        part.name = name_prefix
        return part
    except Exception as e:
        log(f"Error creating symmetric part {name_prefix}: {e}")
        return None

def create_arm(radius=0.1, length=0.7, location=(0.6, 0, -0.0), rotation=(math.radians(90), 0, 0)):
    log("Creating arm")
    try:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, align='WORLD', location=location, rotation=rotation)
        arm = bpy.context.active_object
        arm.name = "Arm"
        return arm
    except Exception as e:
        log(f"Error creating arm: {e}")
        return None

def create_leg(radius=0.2, length=0.8, location=(0.3, 0, -1.3), rotation=(math.radians(90), 0, 0)):
    log("Creating leg")
    try:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, align='WORLD', location=location, rotation=rotation)
        leg = bpy.context.active_object
        leg.name = "Leg"
        return leg
    except Exception as e:
        log(f"Error creating leg: {e}")
        return None

def create_body(size=1.0, location=(0, 0, 0.0)):
    log("Creating body")
    try:
        bpy.ops.mesh.primitive_cube_add(size=size, align='WORLD', location=location)
        body = bpy.context.active_object
        body.name = "Body"
        return body
    except Exception as e:
        log(f"Error creating body: {e}")
        return None

def create_shoulder(radius=0.15, location=(0.6, 0, 0.0)):
    log("Creating shoulder")
    try:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=location)
        shoulder = bpy.context.active_object
        shoulder.name = "Shoulder"
        return shoulder
    except Exception as e:
        log(f"Error creating shoulder: {e}")
        return None

def create_hand(radius=0.1, location=(0.8, 0, 0.0)):
    log("Creating hand")
    try:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=location)
        hand = bpy.context.active_object
        hand.name = "Hand"
        return hand
    except Exception as e:
        log(f"Error creating hand: {e}")
        return None

def create_foot(radius=0.2, location=(0.3, 0, -2.1)):
    log("Creating foot")
    try:
        bpy.ops.mesh.primitive_cube_add(size=0.4, align='WORLD', location=location)
        foot = bpy.context.active_object
        foot.name = "Foot"
        return foot
    except Exception as e:
        log(f"Error creating foot: {e}")
        return None

def create_hat(location=(0, 0, 2.7)):
    log("Creating hat")
    try:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, align='WORLD', location=location, segments=32, ring_count=16)
        hat = bpy.context.active_object
        hat.name = "Hat"
        return hat
    except Exception as e:
        log(f"Error creating hat: {e}")
        return None

def create_backpack(location=(-0.6, -0.3, 0.2)):
    log("Creating backpack")
    try:
        bpy.ops.mesh.primitive_cube_add(size=0.5, align='WORLD', location=location)
        backpack = bpy.context.active_object
        backpack.name = "Backpack"
        return backpack
    except Exception as e:
        log(f"Error creating backpack: {e}")
        return None

def create_mouth(location=(0, 0, 1.2), major_radius=0.4, minor_radius=0.1):
    log("Creating mouth")
    try:
        bpy.ops.mesh.primitive_torus_add(align='WORLD', location=location, rotation=(0, 0, 0), major_radius=major_radius, minor_radius=minor_radius)
        mouth = bpy.context.active_object
        mouth.name = "Mouth"
        return mouth
    except Exception as e:
        log(f"Error creating mouth: {e}")
        return None

def calculate_center_of_mass(objects):
    total_mass = 0
    weighted_sum = [0, 0, 0]
    for obj in objects:
        if obj and obj.type == 'MESH' and obj.data:
            try:
                bm = bmesh.new()
                bm.from_mesh(obj.data)
                volume = obj.data.volume
                total_mass += volume
                weighted_sum[0] += obj.location.x * volume
                weighted_sum[1] += obj.location.y * volume
                weighted_sum[2] += obj.location.z * volume
                bm.free()
            except Exception as e:
                log(f"Error calculating volume for {obj.name}: {e}")
                continue

    if total_mass > 0:
        center_of_mass = [coord / total_mass for coord in weighted_sum]
        return center_of_mass
    else:
        return [0, 0, 0]

def check_mechanics(obj):
    log(f"Checking mechanics for {obj.name}")
    if obj and obj.type == 'MESH' and obj.data:
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
    if obj and obj.type == 'MESH' and obj.data:
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
    if obj and obj.type == 'MESH' and obj.data and obj.data.materials:
        pass
    else:
        log(f"Warning: {obj.name} has no material assigned.")

def check_structure(obj):
    log(f"Checking structure for {obj.name}")
    if obj and obj.type == 'MESH' and obj.data:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        non_manifold_edges = [e for e in bm.edges if e.is_manifold == False]
        if non_manifold_edges:
            log(f"Warning: {obj.name} has {len(non_manifold_edges)} non-manifold edges.")
        bm.free()
    else:
        log(f"Warning: {obj.name} has no valid mesh data.")

def set_parent(child, parent):
    try:
        child.parent = parent
        child.matrix_parent_inverse = parent.matrix_world.inverted()
    except Exception as e:
        log(f"Error setting parent for {child.name}: {e}")

def create_character(body_size=1.0, head_radius=0.5, arm_length=0.7, leg_length=0.8):
    character_name = "CartoonCharacter"

    if body_size <= 0 or head_radius <= 0 or arm_length <= 0 or leg_length <= 0:
        log("Error: Invalid input parameters. Sizes and lengths must be positive.")
        return

    body = create_body(size=body_size)
    neck = create_neck(location=(0, 0, body_size))
    head = create_head(radius=head_radius, location=(0, 0, body_size + 0.5 + head_radius))

    ear_left = create_symmetric_part("ear", 0.2, 0, (head_radius, 0, head_radius), (0, 0, 0), "Ear_Left")
    ear_right = create_symmetric_part("ear", 0.2, 0, (-head_radius, 0, head_radius), (0, 0, 0), "Ear_Right")
    eye_left = create_symmetric_part("eye", 0.15, 0, (head_radius/2, head_radius/2, head_radius/2), (0, 0, 0), "Eye_Left")
    eye_right = create_symmetric_part("eye", 0.15, 0, (-head_radius/2, head_radius/2, head_radius/2), (0, 0, 0), "Eye_Right")
    mouth = create_mouth(location=(0, -head_radius/2, -head_radius/4))

    if ear_left:
        set_parent(ear_left, head)
    if ear_right:
        set_parent(ear_right, head)
    if eye_left:
        set_parent(eye_left, head)
    if eye_right:
        set_parent(eye_right, head)
    if mouth:
        set_parent(mouth, head)

    shoulder_left = create_shoulder(location=(body_size/2 + 0.05, 0, body_size/2))
    shoulder_right = create_shoulder(location=(-body_size/2 - 0.05, 0, body_size/2))

    arm_left = create_arm(length=arm_length, location=(body_size/2 + 0.15 + arm_length/2, 0, body_size/2), rotation=(math.radians(90), 0, 0))
    arm_right = create_arm(length=arm_length, location=(-body_size/2 - 0.15 - arm_length/2, 0, body_size/2), rotation=(math.radians(90), 0, 0))

    elbow_joint_left = create_symmetric_part("elbow_joint", 0.1, 0, (body_size/2 + 0.15 + arm_length/2, 0, body_size/2 - arm_length/2), (0, 0, 0), "Elbow_Left")
    elbow_joint_right = create_symmetric_part("elbow_joint", 0.1, 0, (-body_size/2 - 0.15 - arm_length/2, 0, body_size/2 - arm_length/2), (0, 0, 0), "Elbow_Right")

    hand_left = create_hand(location=(body_size/2 + 0.15 + arm_length + 0.1, 0, body_size/2))
    hand_right = create_hand(location=(-body_size/2 - 0.15 - arm_length - 0.1, 0, body_size/2))

    leg_left = create_leg(length=leg_length, location=(body_size/4, 0, -leg_length/2), rotation=(math.radians(90), 0, 0))
    leg_right = create_leg(length=leg_length, location=(-body_size/4, 0, -leg_length/2), rotation=(math.radians(90), 0, 0))

    knee_joint_left = create_symmetric_part("knee_joint", 0.2, 0, (body_size/4, 0, -leg_length), (0, 0, 0), "Knee_Left")
    knee_joint_right = create_symmetric_part("knee_joint", 0.2, 0, (-body_size/4, 0, -leg_length), (0, 0, 0), "Knee_Right")

    foot_left = create_foot(location=(body_size/4, 0, -leg_length - 0.2))
    foot_right = create_foot(location=(-body_size/4, 0, -leg_length - 0.2))

    hat = create_hat(location=(0, 0, body_size + 0.5 + head_radius + 0.2))
    backpack = create_backpack(location=(-body_size/2 - 0.1, -body_size/4, body_size/4))

    if hat:
        set_parent(hat, head)

    if backpack:
        set_parent(backpack, body)

    set_parent(neck, body)
    set_parent(head, neck)

    set_parent(shoulder_left, body)
    set_parent(shoulder_right, body)

    set_parent(arm_left, shoulder_left)
    set_parent(arm_right, shoulder_right)

    if elbow_joint_left:
        set_parent(elbow_joint_left, arm_left)
    if elbow_joint_right:
        set_parent(elbow_joint_right, arm_right)

    set_parent(hand_left, arm_left)
    set_parent(hand_right, arm_right)

    set_parent(leg_left, body)
    set_parent(leg_right, body)

    if knee_joint_left:
        set_parent(knee_joint_left, leg_left)
    if knee_joint_right:
        set_parent(knee_joint_right, leg_right)

    set_parent(foot_left, leg_left)
    set_parent(foot_right, leg_right)

    objects_for_com = [body, head, neck, ear_left, ear_right, eye_left, eye_right, mouth, arm_left, arm_right, leg_left, leg_right, hat, backpack, shoulder_left, shoulder_right, hand_left, hand_right, foot_left, foot_right, elbow_joint_left, elbow_joint_right, knee_joint_left, knee_joint_right]
    objects_for_com = [obj for obj in objects_for_com if obj is not None]
    center_of_mass = calculate_center_of_mass(objects_for_com)
    log(f"Center of mass: {center_of_mass}")

    bpy.ops.object.select_all(action='DESELECT')

    for obj in objects_for_com:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = body
    try:
        bpy.ops.object.join()
        body.name = character_name
    except Exception as e:
        log(f"Error joining objects: {e}")

    check_mechanics(body)
    check_physics(body)
    check_appearance(body)
    check_structure(body)

    log("Finished creating character")

def main():
    create_character(body_size=1.2, head_radius=0.6, arm_length=0.8, leg_length=0.9)

bpy.app.timers.register(main)
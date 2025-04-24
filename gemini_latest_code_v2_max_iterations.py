import bpy
import bmesh
import math

def log(message):
    print(f"Log: {message}")

def delete_all_objects():
    log("Deleting all objects in scene")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

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

def create_sphere(radius=1.0, location=(0, 0, 0), name="Sphere", material_name="Material", color=(0.8, 0.8, 0.8, 1)):
    try:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, align='WORLD', location=location)
        obj = bpy.context.object
        obj.name = name
        add_material(obj, material_name, color=color)
        return obj
    except Exception as e:
        log(f"Error creating {name}: {e}")
        return None

def create_cylinder(radius=0.5, depth=2.0, location=(0, 0, 0), name="Cylinder", material_name="Material", color=(0.8, 0.8, 0.8, 1)):
    try:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, align='WORLD', location=location)
        obj = bpy.context.object
        obj.name = name
        add_material(obj, material_name, color=color)
        return obj
    except Exception as e:
        log(f"Error creating {name}: {e}")
        return None

def create_cube(size=1.0, location=(0, 0, 0), name="Cube", material_name="Material", color=(0.8, 0.8, 0.8, 1)):
    try:
        bpy.ops.mesh.primitive_cube_add(size=size, align='WORLD', location=location)
        obj = bpy.context.object
        obj.name = name
        add_material(obj, material_name, color=color)
        return obj
    except Exception as e:
        log(f"Error creating {name}: {e}")
        return None

def create_head(radius=1.0, material_name="HeadMaterial", location=(0, 0, 0), color=(0.8, 0.8, 0.8, 1)):
    log("Creating head")
    return create_sphere(radius=radius, location=location, name="Head", material_name=material_name, color=color)

def create_body(body_height=2.0, body_radius=0.5, material_name="BodyMaterial", location=(0, 0, -1), color=(0.8, 0.8, 0.8, 1)):
    log("Creating body")
    return create_cylinder(radius=body_radius, depth=body_height, location=location, name="Body", material_name=material_name, color=color)

def create_ear(head, radius=0.2, ear_offset=(0.6, 0, 0.8), material_name="EarMaterial", color=(0.8, 0.8, 0.8, 1)):
    log("Creating ear")
    try:
        ear_location = (head.location.x + ear_offset[0], head.location.y + ear_offset[1], head.location.z + ear_offset[2])
        ear = create_sphere(radius=radius, location=ear_location, name="Ear", material_name=material_name, color=color)
        ear.parent = head
        return ear
    except Exception as e:
        log(f"Error creating ear: {e}")
        return None

def create_eye(head, radius=0.15, eye_offset=(0.4, 0.5, 0.3), material_name="EyeMaterial", color=(0.8, 0.8, 0.8, 1)):
    log("Creating eye")
    try:
        eye_location = (head.location.x + eye_offset[0], head.location.y + eye_offset[1], head.location.z + eye_offset[2])
        eye = create_sphere(radius=radius, location=eye_location, name="Eye", material_name=material_name, color=color)
        eye.parent = head
        return eye
    except Exception as e:
        log(f"Error creating eye: {e}")
        return None

def create_mouth(head, major_radius=0.4, minor_radius=0.1, mouth_offset=(0, -0.6, -0.2), material_name="MouthMaterial", color=(0.8, 0.8, 0.8, 1)):
    log("Creating mouth")
    try:
        mouth_location = (head.location.x + mouth_offset[0], head.location.y + mouth_offset[1], head.location.z + mouth_offset[2])
        bpy.ops.mesh.primitive_torus_add(
            align='WORLD',
            location=mouth_location,
            rotation=(0, 0, 0),
            major_radius=major_radius,
            minor_radius=minor_radius
        )
        mouth = bpy.context.object
        mouth.name = "Mouth"
        add_material(mouth, material_name, color=color)
        mouth.parent = head
        return mouth
    except Exception as e:
        log(f"Error creating mouth: {e}")
        return None

def create_arm(body, radius=0.1, length=1.0, arm_offset=(0.7, 0, 0.7), material_name="ArmMaterial", rotation=(0, 0, 0), color=(0.8, 0.8, 0.8, 1)):
    log("Creating arm")
    try:
        arm_location = (body.location.x + arm_offset[0], body.location.y + arm_offset[1], body.location.z + body.dimensions.z/2 + arm_offset[2])
        arm = create_cylinder(radius=radius, depth=length, location=arm_location, name="Arm", material_name=material_name, color=color)
        if arm:
            arm.parent = body
            arm.rotation_euler = rotation
        return arm
    except Exception as e:
        log(f"Error creating arm: {e}")
        return None

def create_leg(body, length=1.2, radius=0.2, leg_offset=(0, 0, 0), material_name="LegMaterial", rotation=(0, 0, 0), color=(0.8, 0.8, 0.8, 1)):
    log("Creating leg")
    try:
        body_height = body.dimensions.z
        leg_y_offset = - body_height/2 - length/2
        leg_location = (body.location.x + leg_offset[0], body.location.y + leg_offset[1], body.location.z + leg_y_offset)

        leg = create_cylinder(radius=radius, depth=length, location=leg_location, name="Leg", material_name=material_name, color=color)
        if leg:
            leg.parent = body
            leg.rotation_euler = rotation
        return leg
    except Exception as e:
        log(f"Error creating leg: {e}")
        return None

def create_foot(leg, leg_length, length=0.3, width=0.4, height=0.1, foot_offset=(0, 0, 0), material_name="FootMaterial", foot_shape="CUBE", color=(0.8, 0.8, 0.8, 1)):
    log("Creating foot")
    try:
        foot_location = (leg.location.x + foot_offset[0], leg.location.y + foot_offset[1], leg.location.z - leg_length/2 - height/2)

        if foot_shape == "CUBE":
            foot = create_cube(size=1.0, location=foot_location, name="Foot", material_name=material_name, color=color)
            if foot:
                foot.scale = (width, length, height)
        elif foot_shape == "SPHERE":
            foot = create_sphere(radius=width, location=foot_location, name="Foot", material_name=material_name, color=color)
            if foot:
                foot.scale = (1, length/width, height/width)
        else:
            log(f"Error: Unknown foot shape: {foot_shape}")
            return None

        if foot:
            foot.parent = leg
        return foot
    except Exception as e:
        log(f"Error creating foot: {e}")
        return None

def create_hat(head, radius=0.6, height=0.8, hat_offset=(0, 0, 0.7), material_name="HatMaterial", color=(0.8, 0.8, 0.8, 1), hat_shape="CONE"):
    log("Creating hat")
    try:
        hat_location = (head.location.x + hat_offset[0], head.location.y + hat_offset[1], head.location.z + head.dimensions.z/2 + hat_offset[2])
        if hat_shape == "CONE":
            bpy.ops.mesh.primitive_cone_add(radius1=radius, depth=height, align='WORLD', location=hat_location)
        elif hat_shape == "CYLINDER":
            bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, align='WORLD', location=hat_location)
        elif hat_shape == "CUBE":
            bpy.ops.mesh.primitive_cube_add(size=radius*2, align='WORLD', location=hat_location)
        else:
            log(f"Error: Unknown hat shape: {hat_shape}")
            return None
        hat = bpy.context.object
        hat.name = "Hat"
        add_material(hat, material_name, color=color)
        hat.parent = head
        return hat
    except Exception as e:
        log(f"Error creating hat: {e}")
        return None

def create_backpack(body, size=(0.5, 0.3, 0.7), backpack_offset=(0, 0.1, 0.5), material_name="BackpackMaterial", color=(0.8, 0.8, 0.8, 1), backpack_shape="CUBE"):
    log("Creating backpack")
    try:
        body_height = body.dimensions.z
        backpack_location = (body.location.x + backpack_offset[0], body.location.y + backpack_offset[1], body.location.z + body_height/2 + backpack_offset[2])
        if backpack_shape == "CUBE":
            backpack = create_cube(size=1, location=backpack_location, name="Backpack", material_name=material_name, color=color)
            if backpack:
                backpack.scale = size
        elif backpack_shape == "SPHERE":
            backpack = create_sphere(radius=size[0], location=backpack_location, name="Backpack", material_name=material_name, color=color)
            if backpack:
                backpack.scale = (1, size[1]/size[0], size[2]/size[0])
        else:
            log(f"Error: Unknown backpack shape: {backpack_shape}")
            return None
        if backpack:
            backpack.parent = body
        return backpack
    except Exception as e:
        log(f"Error creating backpack: {e}")
        return None

def create_ground(size=10, material_name="GroundMaterial", color=(0.5, 0.5, 0.5, 1)):
    log("Creating ground")
    try:
        bpy.ops.mesh.primitive_plane_add(size=size, align='WORLD', location=(0, 0, -2))
        ground = bpy.context.object
        ground.name = "Ground"
        add_material(ground, material_name, color=color)
        return ground
    except Exception as e:
        log(f"Error creating ground: {e}")
        return None

def create_base(radius=1.0, height=0.2, material_name="BaseMaterial", color=(0.6, 0.6, 0.6, 1)):
    log("Creating base")
    try:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, align='WORLD', location=(0, 0, -2.2))
        base = bpy.context.object
        base.name = "Base"
        add_material(base, material_name, color=color)
        return base
    except Exception as e:
        log(f"Error creating base: {e}")
        return None

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

class CartoonCharacter:
    def __init__(self, name="CartoonCharacter", body_height=2.0, body_radius=0.5, head_radius=1.0, arm_length=1.0, leg_length=1.2, scale=1.0, location=(0, 0, 0),
                 ear_color=(0.8, 0.8, 0.8, 1), eye_color=(0,1,0,1), mouth_color=(0,0,1,1), hat_color=(0.8, 0.8, 0.8, 1), backpack_color=(0.8, 0.8, 0.8, 1),
                 foot_shape="CUBE", hat_shape="CONE", backpack_shape="CUBE", ground_size=10, base_radius=1.5, base_height=0.3,
                 body_color=(0.2, 0.8, 0.2, 1), head_color=(0.8, 0.2, 0.2, 1)):
        self.name = name
        self.body_height = body_height
        self.body_radius = body_radius
        self.head_radius = head_radius
        self.arm_length = arm_length
        self.leg_length = leg_length
        self.scale = scale
        self.location = location
        self.body = None
        self.head = None
        self.ears = []
        self.eyes = []
        self.mouth = None
        self.arms = []
        self.legs = []
        self.hat = None
        self.backpack = None
        self.ground = None
        self.feet = []
        self.base = None
        self.ear_offset = (0.6, 0, 0.8)
        self.eye_offset = (0.4, 0.5, 0.3)
        self.arm_offset = (self.body_radius + 0.2, 0, self.body_height / 2)
        self.leg_offset = (self.body_radius / 2, 0, 0)
        self.hat_offset = (0, 0, 0.7)
        self.backpack_offset = (0, 0.1, 0.5)
        self.ear_color = ear_color
        self.eye_color = eye_color
        self.mouth_color = mouth_color
        self.hat_color = hat_color
        self.backpack_color = backpack_color
        self.foot_shape = foot_shape
        self.hat_shape = hat_shape
        self.backpack_shape = backpack_shape
        self.ground_size = ground_size
        self.base_radius = base_radius
        self.base_height = base_height
        self.body_color = body_color
        self.head_color = head_color

        if self.body_height <= 0:
            raise ValueError("body_height must be greater than 0")
        if self.head_radius <= 0:
            raise ValueError("head_radius must be greater than 0")

    def build(self):
        try:
            log(f"Creating character: {self.name}")

            bpy.ops.object.select_all(action='DESELECT')

            # Create root object
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=self.location)
            root = bpy.context.object
            root.name = self.name + "_Root"

            # Create collection for the character
            character_collection = bpy.data.collections.new(self.name + "_Collection")
            bpy.context.scene.collection.children.link(character_collection)

            def add_to_collection(obj):
                character_collection.objects.link(obj)

            self.base = create_base(radius=self.base_radius * self.scale, height=self.base_height * self.scale)
            if not self.base:
                log("Base creation failed. Aborting.")
                return
            self.base.parent = root
            add_to_collection(self.base)

            body_location = (0, 0, self.base_height * self.scale)
            self.body = create_body(body_height=self.body_height * self.scale, body_radius=self.body_radius * self.scale, location=body_location, color=self.body_color)
            if not self.body:
                log("Body creation failed. Aborting.")
                bpy.data.objects.remove(root, do_unlink=True)
                bpy.data.collections.remove(character_collection)
                return
            self.body.parent = root
            add_to_collection(self.body)

            head_location = (0, 0, self.body_height * self.scale / 2 + self.head_radius * self.scale + self.base_height * self.scale)
            self.head = create_head(radius=self.head_radius * self.scale, location=head_location, color=self.head_color)
            if not self.head:
                log("Head creation failed. Aborting.")
                bpy.data.objects.remove(root, do_unlink=True)
                bpy.data.collections.remove(character_collection)
                return
            self.head.parent = self.body
            add_to_collection(self.head)

            ear_offsets = [(-self.ear_offset[0] * self.scale, self.ear_offset[1] * self.scale, self.ear_offset[2] * self.scale),
                           (self.ear_offset[0] * self.scale, self.ear_offset[1] * self.scale, self.ear_offset[2] * self.scale)]
            self.ears = []
            for offset in ear_offsets:
                ear = create_ear(self.head, radius=0.2 * self.scale, ear_offset=offset, color=self.ear_color)
                if ear:
                    self.ears.append(ear)
                    add_to_collection(ear)

            eye_offsets = [(-self.eye_offset[0] * self.scale, self.eye_offset[1] * self.scale, self.eye_offset[2] * self.scale),
                           (self.eye_offset[0] * self.scale, self.eye_offset[1] * self.scale, self.eye_offset[2] * self.scale)]
            self.eyes = []
            for offset in eye_offsets:
                eye = create_eye(self.head, radius=0.15 * self.scale, eye_offset=offset, color=self.eye_color)
                if eye:
                    self.eyes.append(eye)
                    add_to_collection(eye)

            self.mouth = create_mouth(self.head, major_radius=0.4 * self.scale, minor_radius=0.1 * self.scale, mouth_offset=(0, -0.6 * self.scale, -0.2 * self.scale), color=self.mouth_color)
            if self.mouth:
                add_to_collection(self.mouth)

            arm_offsets = [(-self.arm_offset[0] * self.scale, self.arm_offset[1] * self.scale, self.arm_offset[2] * self.scale),
                           (self.arm_offset[0] * self.scale, self.arm_offset[1] * self.scale, self.arm_offset[2] * self.scale)]
            arm_rotations = [(0, 0, math.radians(10)), (0, 0, math.radians(-10))]
            self.arms = []
            for i, offset in enumerate(arm_offsets):
                arm = create_arm(self.body, length=self.arm_length * self.scale, radius=0.1 * self.scale, arm_offset=offset, rotation=arm_rotations[i], color=self.hat_color)
                if arm:
                    self.arms.append(arm)
                    add_to_collection(arm)

            leg_offsets = [(-self.leg_offset[0] * self.scale, self.leg_offset[1] * self.scale, 0),
                           (self.leg_offset[0] * self.scale, self.leg_offset[1] * self.scale, 0)]
            self.legs = []
            self.feet = []
            for offset in leg_offsets:
                leg = create_leg(self.body, length=self.leg_length * self.scale, radius=0.2 * self.scale, leg_offset=offset, color=self.body_color)
                if leg:
                    self.legs.append(leg)
                    add_to_collection(leg)
                    foot = create_foot(leg, self.leg_length * self.scale, length=0.3 * self.scale, width=0.4 * self.scale, height=0.1 * self.scale, foot_offset=(0, 0, 0), foot_shape=self.foot_shape, color=self.head_color)
                    if foot:
                        self.feet.append(foot)
                        add_to_collection(foot)
                else:
                    log("Leg creation failed. Continuing.")

            self.hat = create_hat(self.head, radius=0.6 * self.scale, height=0.8 * self.scale, hat_offset=self.hat_offset, color=self.hat_color, hat_shape=self.hat_shape)
            if self.hat:
                add_to_collection(self.hat)

            self.backpack = create_backpack(self.body, size=(0.5 * self.scale, 0.3 * self.scale, 0.7 * self.scale), backpack_offset=self.backpack_offset, color=self.backpack_color, backpack_shape=self.backpack_shape)
            if self.backpack:
                add_to_collection(self.backpack)

            self.ground = create_ground(size=self.ground_size)
            if self.ground:
                ground_z = -self.leg_length * self.scale - self.base_height * self.scale
                self.ground.location = (self.location[0], self.location[1], ground_z)
                self.ground.parent = root
                add_to_collection(self.ground)

            check_mechanics(self.body)
            check_physics(self.body)
            check_appearance(self.body)
            check_structure(self.body)

            root.location = self.location
            add_to_collection(root)

            log("Character creation complete.")

        except Exception as e:
            log(f"Error during character creation: {e}")
            # 清理已创建的对象
            for obj in character_collection.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(character_collection)

def main():
    try:
        delete_all_objects()
        character = CartoonCharacter(scale=1.0, location=(0,0,0), ear_color=(0.2, 0.2, 0.8, 1), eye_color=(0,1,0,1), mouth_color=(0,0,1,1), hat_color=(0.8, 0.8, 0.2, 1), backpack_color=(0.8, 0.2, 0.8, 1),
                                     foot_shape="CUBE", hat_shape="CONE", backpack_shape="CUBE", ground_size=20, base_radius=1.5, base_height=0.3,
                                     body_color=(0.2, 0.8, 0.2, 1), head_color=(0.8, 0.2, 0.2, 1))
        character.build()

    except Exception as e:
        log(f"Error during main: {e}")

bpy.app.timers.register(main)
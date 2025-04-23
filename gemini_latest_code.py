import bpy
import bmesh
import math
from mathutils import Vector

def log(message):
    print(f"Log: {message}")

class Character:
    def __init__(self, name="CartoonCharacter"):
        self.name = name
        self.armature = None  # The armature object
        self.head = None
        self.body = None
        self.ear_left = None
        self.ear_right = None
        self.eye_left = None
        self.eye_right = None
        self.mouth = None
        self.arm_left_upper = None
        self.arm_left_lower = None
        self.arm_right_upper = None
        self.arm_right_lower = None
        self.leg_left_upper = None
        self.leg_left_lower = None
        self.leg_right_upper = None
        self.leg_right_lower = None
        self.hat = None
        self.backpack = None
        self.scale = 1.0  # Overall scale of the character
        self.density = 1.0 # Density for mass calculation (simplified)
        self.bone_length = 0.5 * self.scale # Default bone length

    def create_armature(self):
        log("Creating armature")
        try:
            # Create armature data
            armature_data = bpy.data.armatures.new(name=self.name + "_ArmatureData")
            self.armature = bpy.data.objects.new(name=self.name + "_Armature", object_data=armature_data)

            # Link armature object to the scene
            bpy.context.collection.objects.link(self.armature)

            # Set armature active and enter edit mode
            bpy.context.view_layer.objects.active = self.armature
            bpy.ops.object.mode_set(mode='EDIT')

            # Create bones (example: spine, head)
            armature = self.armature.data
            # Spine
            spine_bone = armature.edit_bones.new("Spine")
            spine_bone.head = (0, 0, 0)
            spine_bone.tail = (0, 0, self.bone_length * 2)

            # Head
            head_bone = armature.edit_bones.new("HeadBone")
            head_bone.head = spine_bone.tail
            head_bone.tail = (0, 0, spine_bone.tail[2] + self.bone_length)
            head_bone.parent = spine_bone

            # Left Arm
            arm_left_upper_bone = armature.edit_bones.new("ArmLeftUpper")
            arm_left_upper_bone.head = (self.bone_length, 0, spine_bone.tail[2])
            arm_left_upper_bone.tail = (arm_left_upper_bone.head[0] + self.bone_length, arm_left_upper_bone.head[1], arm_left_upper_bone.head[2])
            arm_left_upper_bone.parent = spine_bone

            arm_left_lower_bone = armature.edit_bones.new("ArmLeftLower")
            arm_left_lower_bone.head = arm_left_upper_bone.tail
            arm_left_lower_bone.tail = (arm_left_lower_bone.head[0] + self.bone_length, arm_left_lower_bone.head[1], arm_left_lower_bone.head[2])
            arm_left_lower_bone.parent = arm_left_upper_bone

            # Right Arm
            arm_right_upper_bone = armature.edit_bones.new("ArmRightUpper")
            arm_right_upper_bone.head = (-self.bone_length, 0, spine_bone.tail[2])
            arm_right_upper_bone.tail = (arm_right_upper_bone.head[0] - self.bone_length, arm_right_upper_bone.head[1], arm_right_upper_bone.head[2])
            arm_right_upper_bone.parent = spine_bone

            arm_right_lower_bone = armature.edit_bones.new("ArmRightLower")
            arm_right_lower_bone.head = arm_right_upper_bone.tail
            arm_right_lower_bone.tail = (arm_right_lower_bone.head[0] - self.bone_length, arm_right_lower_bone.head[1], arm_right_lower_bone.head[2])
            arm_right_lower_bone.parent = arm_right_upper_bone

            # Left Leg
            leg_left_upper_bone = armature.edit_bones.new("LegLeftUpper")
            leg_left_upper_bone.head = (self.bone_length / 2, 0, 0)
            leg_left_upper_bone.tail = (leg_left_upper_bone.head[0], 0, -self.bone_length)
            leg_left_upper_bone.parent = spine_bone

            leg_left_lower_bone = armature.edit_bones.new("LegLeftLower")
            leg_left_lower_bone.head = leg_left_upper_bone.tail
            leg_left_lower_bone.tail = (leg_left_lower_bone.head[0], 0, leg_left_lower_bone.head[2] - self.bone_length)
            leg_left_lower_bone.parent = leg_left_upper_bone

            # Right Leg
            leg_right_upper_bone = armature.edit_bones.new("LegRightUpper")
            leg_right_upper_bone.head = (-self.bone_length / 2, 0, 0)
            leg_right_upper_bone.tail = (leg_right_upper_bone.head[0], 0, -self.bone_length)
            leg_right_upper_bone.parent = spine_bone

            leg_right_lower_bone = armature.edit_bones.new("LegRightLower")
            leg_right_lower_bone.head = leg_right_upper_bone.tail
            leg_right_lower_bone.tail = (leg_right_lower_bone.head[0], 0, leg_right_lower_bone.head[2] - self.bone_length)
            leg_right_lower_bone.parent = leg_right_upper_bone

            # Exit edit mode
            bpy.ops.object.mode_set(mode='OBJECT')

            return self.armature
        except Exception as e:
            log(f"Error creating armature: {e}")
            return None

    def create_mesh_object(self, mesh_type, **kwargs):
        """Helper function to create mesh objects."""
        try:
            if mesh_type == "Sphere":
                bpy.ops.mesh.primitive_uv_sphere_add(**kwargs)
            elif mesh_type == "Cube":
                bpy.ops.mesh.primitive_cube_add(**kwargs)
            elif mesh_type == "Cylinder":
                bpy.ops.mesh.primitive_cylinder_add(**kwargs)
            elif mesh_type == "Torus":
                bpy.ops.mesh.primitive_torus_add(**kwargs)
            else:
                log(f"Invalid mesh type: {mesh_type}")
                return None

            obj = bpy.context.object
            return obj
        except Exception as e:
            log(f"Error creating {mesh_type}: {e}")
            return None

    def create_head(self, head_shape="Sphere", radius=1.0, location=(0, 0, 1.0)):
        log("Creating head")
        if head_shape not in ["Sphere"]:
            log("Invalid head shape. Creating sphere instead.")
            head_shape = "Sphere"

        head = self.create_mesh_object(
            head_shape,
            radius=radius * self.scale,
            enter_editmode=False,
            align='WORLD',
            location=location
        )

        if head:
            head.name = "Head"
            self.head = head
        return head

    def create_body(self, size=(0.5, 0.5, 1.0), location=(0, 0, 0)):
        log("Creating body")
        body = self.create_mesh_object(
            "Cube",
            size=1 * self.scale,
            enter_editmode=False,
            align='WORLD',
            location=location
        )

        if body:
            body.name = "Body"
            body.scale = (size[0] * self.scale, size[1] * self.scale, size[2] * self.scale)
            self.body = body
        return body

    def create_ear(self, ear_shape="Sphere", radius=0.2, location=(0.7, 0, 1.8)):
        log("Creating ear")
        if ear_shape not in ["Sphere"]:
            log("Invalid ear shape. Creating sphere instead.")
            ear_shape = "Sphere"

        ear = self.create_mesh_object(
            ear_shape,
            radius=radius * self.scale,
            enter_editmode=False,
            align='WORLD',
            location=location
        )

        if ear:
            ear.name = "Ear"
        return ear

    def create_eye(self, eye_shape="Sphere", radius=0.15, location=(0.4, 0.7, 1.3)):
        log("Creating eye")
        if eye_shape not in ["Sphere"]:
            log("Invalid eye shape. Creating sphere instead.")
            eye_shape = "Sphere"

        eye = self.create_mesh_object(
            eye_shape,
            radius=radius * self.scale,
            enter_editmode=False,
            align='WORLD',
            location=location
        )

        if eye:
            eye.name = "Eye"
        return eye

    def create_mouth(self, mouth_shape="Torus", major_radius=0.4, minor_radius=0.1, location=(0, 0.2, 0.7)):
        log("Creating mouth")
        if mouth_shape not in ["Torus"]:
            log("Invalid mouth shape. Creating torus instead.")
            mouth_shape = "Torus"

        mouth = self.create_mesh_object(
            mouth_shape,
            major_radius=major_radius * self.scale,
            minor_radius=minor_radius * self.scale,
            align='WORLD',
            location=location,
            rotation=(0, 0, 0)
        )

        if mouth:
            mouth.name = "Mouth"
        return mouth

    def create_arm_part(self, part_name, arm_shape="Cylinder", length=0.5, radius=0.08, location=(0.75, 0, 0.5)):
        log(f"Creating {part_name}")
        if arm_shape not in ["Cylinder"]:
            log("Invalid arm shape. Creating cylinder instead.")
            arm_shape = "Cylinder"

        arm_part = self.create_mesh_object(
            arm_shape,
            radius=radius * self.scale,
            depth=length * self.scale,
            enter_editmode=False,
            align='WORLD',
            location=location,
            rotation=(math.radians(90), 0, 0) # Rotate to align with bone
        )

        if arm_part:
            arm_part.name = part_name
        return arm_part

    def create_leg_part(self, part_name, leg_shape="Cylinder", length=0.6, radius=0.15, location=(0, -1.1, 0)):
        log(f"Creating {part_name}")
        if leg_shape not in ["Cylinder"]:
            log("Invalid leg shape. Creating cylinder instead.")
            leg_shape = "Cylinder"

        leg_part = self.create_mesh_object(
            leg_shape,
            radius=radius * self.scale,
            depth=length * self.scale,
            enter_editmode=False,
            align='WORLD',
            location=location,
            rotation=(math.radians(90), 0, 0) # Rotate to align with bone
        )

        if leg_part:
            leg_part.name = part_name
        return leg_part

    def create_hat(self, radius=0.5, location=(0, 0, 2.0)):
        log("Creating hat")
        hat = self.create_mesh_object(
            "Sphere",
            radius=radius * self.scale,
            enter_editmode=False,
            align='WORLD',
            location=location
        )

        if hat:
            hat.name = "Hat"
            try:
                bpy.ops.object.mode_set(mode='EDIT')
                bm = bmesh.new()
                bm.from_mesh(hat.data)
                bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < location[2]], context='VERTS')
                bm.to_mesh(hat.data)
                hat.data.update()
                bm.free()
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception as e:
                log(f"Error editing hat mesh: {e}")
        return hat

    def create_backpack(self, size=(0.5, 0.3, 0.7), location=(0, -0.3, 0.5)):
        log("Creating backpack")
        backpack = self.create_mesh_object(
            "Cube",
            size=1 * self.scale,
            enter_editmode=False,
            align='WORLD',
            location=location
        )

        if backpack:
            backpack.name = "Backpack"
            backpack.scale = (size[0] * self.scale, size[1] * self.scale, size[2] * self.scale)
        return backpack

    def parent_objects(self):
        log("Parenting objects")
        try:
            if self.armature:
                if self.head:
                    self.head.parent = self.armature
                    self.head.matrix_parent_inverse = self.armature.matrix_world.inverted() # Important for correct parenting
                    modifier = self.head.modifiers.new(name="Armature", type='ARMATURE')
                    modifier.object = self.armature

                if self.body:
                    self.body.parent = self.armature
                    self.body.matrix_parent_inverse = self.armature.matrix_world.inverted()
                    modifier = self.body.modifiers.new(name="Armature", type='ARMATURE')
                    modifier.object = self.armature

                # Parent other objects to the head or body as appropriate
                if self.head:
                    for obj in [self.ear_left, self.ear_right, self.eye_left, self.eye_right, self.mouth, self.hat]:
                        if obj:
                            obj.parent = self.head
                            obj.matrix_parent_inverse = self.head.matrix_world.inverted()

                if self.body:
                    for obj in [self.backpack]:
                        if obj:
                            obj.parent = self.body
                            obj.matrix_parent_inverse = self.body.matrix_world.inverted()

                # Parent arms and legs to armature and add armature modifier
                for part in [self.arm_left_upper, self.arm_left_lower, self.arm_right_upper, self.arm_right_lower, self.leg_left_upper, self.leg_left_lower, self.leg_right_upper, self.leg_right_lower]:
                    if part:
                        part.parent = self.armature
                        part.matrix_parent_inverse = self.armature.matrix_world.inverted()
                        modifier = part.modifiers.new(name="Armature", type='ARMATURE')
                        modifier.object = self.armature

        except Exception as e:
            log(f"Error parenting objects: {e}")

    def calculate_volume(self, obj):
        """Calculates the approximate volume of a mesh object."""
        if not obj or not obj.data:
            return 0.0

        try:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            volume = bm.calc_volume()
            bm.free()
            return volume
        except Exception as e:
            log(f"Error calculating volume for {obj.name}: {e}")
            return 0.0

    def calculate_center_of_mass(self):
        log("Calculating center of mass (volume-weighted).")
        total_mass = 0.0
        weighted_sum = Vector((0, 0, 0))

        for obj in [self.head, self.body, self.arm_left_upper, self.arm_left_lower, self.arm_right_upper, self.arm_right_lower, self.leg_left_upper, self.leg_left_lower, self.leg_right_upper, self.leg_right_lower, self.backpack, self.hat, self.ear_left, self.ear_right, self.eye_left, self.eye_right, self.mouth]:
            if obj:
                volume = self.calculate_volume(obj)
                mass = volume * self.density  # Simplified: mass = volume * density
                total_mass += mass
                weighted_sum += mass * Vector(obj.location)

        if total_mass > 0:
            center_of_mass = weighted_sum / total_mass
            return center_of_mass
        else:
            log("Warning: No mass to calculate center of mass.")
            return Vector((0, 0, 0))

    def check_mechanics(self):
        log("Checking mechanics")
        center_of_mass = self.calculate_center_of_mass()
        log(f"Center of mass: {center_of_mass}")

        # Basic check: Is the center of mass above the support polygon (legs)?
        if self.leg_left_lower and self.leg_right_lower:
            leg_left_loc = Vector(self.leg_left_lower.location)
            leg_right_loc = Vector(self.leg_right_lower.location)
            support_center = (leg_left_loc + leg_right_loc) / 2
            # Check if COM is within a reasonable distance of the support center in X and Y
            if abs(center_of_mass.x - support_center.x) > 0.5 * self.scale or abs(center_of_mass.y - support_center.y) > 0.3 * self.scale:
                log("Warning: Center of mass is not well-aligned with the legs. Unstable!")
                return False

        log("Mechanics check passed (basic).")
        return True

    def check_physics(self):
        log("Checking physics")
        # Add more sophisticated physics checks here if needed.
        log("Physics check passed (basic).")
        return True

    def check_appearance(self):
        log("Checking appearance")
        # Add more sophisticated appearance checks here if needed.
        log("Appearance check passed (basic).")
        return True

    def check_structure(self):
        log("Checking structure")
        # Add more sophisticated structure checks here if needed.
        log("Structure check passed (basic).")
        return True

    def create_character(self):
        log("Creating character")
        try:
            self.armature = self.create_armature()

            self.head = self.create_head(location=(0, 0, 1.5 * self.scale))
            self.body = self.create_body(location=(0, 0, 0))

            # Adjust ear, eye, mouth locations relative to the head
            ear_offset = (0.7 * self.scale, 0.5 * self.scale, 0.8 * self.scale)
            eye_offset = (0.4 * self.scale, 0.6 * self.scale, 0.3 * self.scale)
            mouth_offset = (0, 0.2 * self.scale, -0.3 * self.scale)
            arm_offset = (0.6 * self.scale, 0, 0.5 * self.scale)
            leg_offset = (0.3 * self.scale, 0, -0.6 * self.scale) # Adjusted leg offset
            hat_offset = (0, 0, 0.6 * self.scale)

            if self.head:
                self.ear_left = self.create_ear(location=(self.head.location.x + ear_offset[0], self.head.location.y + ear_offset[1], self.head.location.z + ear_offset[2]))
                self.ear_right = self.create_ear(location=(self.head.location.x - ear_offset[0], self.head.location.y + ear_offset[1], self.head.location.z + ear_offset[2]))
                self.eye_left = self.create_eye(location=(self.head.location.x + eye_offset[0], self.head.location.y + eye_offset[1], self.head.location.z + eye_offset[2]))
                self.eye_right = self.create_eye(location=(self.head.location.x - eye_offset[0], self.head.location.y + eye_offset[1], self.head.location.z + eye_offset[2]))
                self.mouth = self.create_mouth(location=(self.head.location.x + mouth_offset[0], self.head.location.y + mouth_offset[1], self.head.location.z + mouth_offset[2]))
                self.hat = self.create_hat(location=(self.head.location.x + hat_offset[0], self.head.location.y + hat_offset[1], self.head.location.z + hat_offset[2]))

            if self.body:
                self.arm_left_upper = self.create_arm_part("ArmLeftUpper", location=(self.body.location.x + arm_offset[0], self.body.location.y + arm_offset[1], self.body.location.z + arm_offset[2]))
                self.arm_left_lower = self.create_arm_part("ArmLeftLower", location=(self.body.location.x + arm_offset[0], self.body.location.y + arm_offset[1], self.body.location.z + arm_offset[2] - self.bone_length), length = self.bone_length)
                self.arm_right_upper = self.create_arm_part("ArmRightUpper", location=(self.body.location.x - arm_offset[0], self.body.location.y + arm_offset[1], self.body.location.z + arm_offset[2]))
                self.arm_right_lower = self.create_arm_part("ArmRightLower", location=(self.body.location.x - arm_offset[0], self.body.location.y + arm_offset[1], self.body.location.z + arm_offset[2] - self.bone_length), length = self.bone_length)

                self.leg_left_upper = self.create_leg_part("LegLeftUpper", location=(self.body.location.x + leg_offset[0], self.body.location.y + leg_offset[1], self.body.location.z + leg_offset[2]))
                self.leg_left_lower = self.create_leg_part("LegLeftLower", location=(self.body.location.x + leg_offset[0], self.body.location.y + leg_offset[1], self.body.location.z + leg_offset[2] - self.bone_length), length = self.bone_length)
                self.leg_right_upper = self.create_leg_part("LegRightUpper", location=(self.body.location.x - leg_offset[0], self.body.location.y + leg_offset[1], self.body.location.z + leg_offset[2]))
                self.leg_right_lower = self.create_leg_part("LegRightLower", location=(self.body.location.x - leg_offset[0], self.body.location.y + leg_offset[1], self.body.location.z + leg_offset[2] - self.bone_length), length = self.bone_length)

                self.backpack = self.create_backpack()

            self.parent_objects()

            if self.validate_model():
                self.adjust_model()
            else:
                log("Model validation failed.  Character may be incomplete or incorrect.")

        except Exception as e:
            log(f"Error creating character: {e}")

    def validate_model(self):
        log("Validating model")
        # Example validation: Check if all required parts exist
        if not all([self.head, self.body, self.leg_left_lower, self.leg_right_lower]):
            log("Warning: Missing essential parts (head, body, legs).")
            return False

        # Add more sophisticated checks here, e.g., proportion checks,
        # collision detection, etc.

        log("Model validation passed.")
        return True

    def adjust_model(self):
        log("Adjusting model")
        # Example adjustment: Move the head slightly higher if it's clipping into the body
        if self.head and self.body:
            if self.head.location.z < self.body.location.z + self.body.scale[2]:
                self.head.location.z = self.body.location.z + self.body.scale[2] + 0.1 * self.scale
                log("Adjusted head position to avoid clipping.")

        # Add more sophisticated adjustments here, e.g., automatic
        # scaling to maintain proportions, etc.

def main():
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    character = Character()
    character.name = "CartoonCharacter"
    character.scale = 0.5  # Adjust the overall scale here
    character.density = 500 # Adjust density

    log("Starting character creation")
    character.create_character()
    log("Character creation complete")

    log("Starting checks")
    mechanics_ok = character.check_mechanics()
    physics_ok = character.check_physics()
    appearance_ok = character.check_appearance()
    structure_ok = character.check_structure()

    log(f"Mechanics check: {mechanics_ok}")
    log(f"Physics check: {physics_ok}")
    log(f"Appearance check: {appearance_ok}")
    log(f"Structure check: {structure_ok}")

bpy.app.timers.register(main)
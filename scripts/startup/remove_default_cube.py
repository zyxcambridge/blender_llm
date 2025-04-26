bl_info = {
    "name": "Remove Default Cube on Startup",
    "blender": (2, 80, 0),
    "category": "Object",
    "version": (1, 0, 0),
    "author": "AI Assistant",
    "description": "Removes the default cube when a new Blender file is loaded.",
}

import bpy
from bpy.app.handlers import persistent


@persistent
def remove_default_cube(scene):
    # 删除所有对象（Cube、Camera、Light等）
    to_remove = [obj for obj in bpy.data.objects]
    for obj in to_remove:
        obj_name = obj.name  # 先保存名字
        bpy.data.objects.remove(obj, do_unlink=True)
        print(f"[RemoveDefaultCube] Removed: {obj_name}")
    if not to_remove:
        print("[RemoveDefaultCube] No objects found to remove.")


def register():
    bpy.app.handlers.load_post.append(remove_default_cube)
    print("[RemoveDefaultCube] Handler registered.")


def unregister():
    if remove_default_cube in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(remove_default_cube)
    print("[RemoveDefaultCube] Handler unregistered.")

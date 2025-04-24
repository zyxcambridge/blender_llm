bl_info = {
    "name": "Remove Default Cube on Startup",
    "blender": (2, 80, 0),
    "category": "Object",
    "version": (1, 0, 0),
    "author": "AI Assistant",
    "description": "Removes the default cube when a new Blender file is loaded."
}

import bpy
from bpy.app.handlers import persistent

@persistent
def remove_default_cube(scene):
    cube = bpy.data.objects.get("Cube")
    if cube is not None:
        bpy.data.objects.remove(cube, do_unlink=True)
        print("[RemoveDefaultCube] Default cube removed.")
    else:
        print("[RemoveDefaultCube] No default cube found.")

def register():
    bpy.app.handlers.load_post.append(remove_default_cube)
    print("[RemoveDefaultCube] Handler registered.")

def unregister():
    if remove_default_cube in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(remove_default_cube)
    print("[RemoveDefaultCube] Handler unregistered.")

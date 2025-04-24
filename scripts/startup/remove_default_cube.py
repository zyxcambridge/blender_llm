import bpy

def remove_default_cube():
    # Look for the object named 'Cube' in the scene
    cube = bpy.data.objects.get("Cube")
    if cube is not None:
        bpy.data.objects.remove(cube, do_unlink=True)
        print("[Startup] Default cube removed.")
    else:
        print("[Startup] No default cube found.")

# Run on script load
remove_default_cube()

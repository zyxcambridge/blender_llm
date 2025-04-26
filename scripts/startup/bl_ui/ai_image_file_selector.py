import bpy
from bpy.types import Operator

class AI_OT_select_image_file(Operator):
    bl_idname = "ai.select_image_file"
    bl_label = "选择图片文件"
    bl_description = "选择用于AI建模的图片"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        ai_props = context.scene.ai_assistant
        ai_props.image_file = self.filepath
        self.report({'INFO'}, f"已选择图片: {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

import bpy
from bpy.types import Menu, Operator
from bpy.props import StringProperty


# AUGMENT菜单 - 只包含UI相关功能
class TOPBAR_MT_ai_assistant_menu(Menu):
    bl_label = "AUGMENT"
    bl_idname = "TOPBAR_MT_ai_assistant_menu"

    def draw(self, context):
        layout = self.layout

        # 一、顶部标题栏
        row = layout.row()
        row.scale_y = 1.5
        row.label(text="AUGMENT", icon='COMMUNITY')

        layout.separator()

        # 二、模式切换区
        box = layout.box()
        row = box.row()
        row.label(text="右边增加侧边栏，对话框...", icon='RIGHTARROW')

        row = box.row(align=True)
        row.label(text="Agent模式", icon='TOOL_SETTINGS')
        row.label(text="Chat模式", icon='SPEECH_BUBBLE')

        layout.separator()

        # 三、核心信息展示区
        box = layout.box()
        row = box.row()
        row.label(text="· AI助手更新", icon='KEYFRAME_HLT')

        row = box.row()
        row.label(text="■ 使用方法", icon='HELP')

        layout.separator()

        # 四、底部状态栏
        box = layout.box()
        row = box.row()
        row.label(text="Augment Memories · blender")
        row = box.row()
        row.label(text="Beta · space_topbar.py")

        # 指令输入区
        row = layout.row()
        row.label(text="Ask or instruct Augment Agent", icon='PLAY')


# 简化的打开助手操作符
class AI_OT_open_assistant(Operator):
    bl_idname = "ai.open_assistant"
    bl_label = "Open AI Assistant"
    bl_description = "Open the AI Assistant panel"

    def execute(self, context):
        self.report({'INFO'}, "UI框架展示")
        return {'FINISHED'}


# 要注册的类列表
classes = (
    TOPBAR_MT_ai_assistant_menu,
    AI_OT_open_assistant,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

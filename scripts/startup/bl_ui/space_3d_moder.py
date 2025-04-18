import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty


# 3D Moder Copilot属性组
class MoCoProperties(PropertyGroup):
    message: StringProperty(name="Message", description="Input message or command", default="")

    mode: EnumProperty(
        name="Mode",
        items=[
            ('AGENT', "Agent Mode", "General AI assistant mode"),
            ('MODER', "3D Moder Mode", "3D modeling specific mode"),
        ],
        default='MODER',
    )

    uploaded_file: StringProperty(name="Uploaded File", description="Path to uploaded 3D model", default="")

    file_details: StringProperty(name="File Details", description="Details about the uploaded file", default="")


# 3D Moder Copilot主面板
class VIEW3D_PT_3d_moder_copilot(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_label = "3D MODER Copilot"
    bl_options = {'DEFAULT_CLOSED'}
    bl_ui_units_x = 80
    bl_ui_units_y = 60

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 确保属性组已注册
        if not hasattr(scene, "moco_props"):
            row = layout.row()
            row.label(text="3D Moder Copilot not initialized.")
            row.operator("moco.initialize", text="Initialize", icon='FILE_REFRESH')
            return

        moco_props = scene.moco_props

        # 顶部栏
        topbar = layout.box()
        topbar_row = topbar.row()

        # 左侧标题
        title_col = topbar_row.column()
        title_col.scale_y = 1.5
        title_col.label(text="🧠 3D MODER Copilot", icon='OUTLINER_OB_MESH')

        # 右侧图标
        icons_col = topbar_row.column()
        icons_row = icons_col.row(align=True)
        icons_row.alignment = 'RIGHT'
        icons_row.label(text="📦")
        icons_row.label(text="✉️")
        icons_row.label(text="🔔")
        icons_row.label(text="👤")
        icons_row.label(text="❌")

        layout.separator()

        # 模式切换
        mode_row = layout.row()

        # Agent Mode按钮
        agent_col = mode_row.column()
        agent_btn = agent_col.operator("moco.set_mode", text="Agent Mode", depress=(moco_props.mode == 'AGENT'))
        agent_btn.mode = 'AGENT'

        # 3D Moder Mode按钮
        moder_col = mode_row.column()
        moder_btn = moder_col.operator("moco.set_mode", text="✅ 3D Moder Mode", depress=(moco_props.mode == 'MODER'))
        moder_btn.mode = 'MODER'

        layout.separator()

        # 上传区域
        upload_box = layout.box()
        upload_box.label(text="📤 Upload 3D Model", icon='IMPORT')
        upload_row = upload_box.row()
        upload_row.label(text="Supported formats: .obj, .fbx, .glb")
        upload_row.operator("moco.upload_file", text="Upload File", icon='FILE_NEW')

        # 如果已上传文件，显示文件详情
        if moco_props.uploaded_file:
            upload_box.label(text=f"✅ Uploaded: {moco_props.file_details}", icon='CHECKMARK')

        layout.separator()

        # 主内容区 - 双栏布局
        main_row = layout.row()

        # 左侧栏
        left_col = main_row.column()
        left_box = left_col.box()

        left_box.label(text="Edit 3D Models with Moder Copilot", icon='MODIFIER')
        left_box.label(text="3D Moder Mode • Auto Mesh Optimization & Rigging")

        features_box = left_box.box()
        features_box.label(text="Features:")
        features_box.label(text="✅ Auto-fix 3D mesh topology errors")
        features_box.label(text="✅ Generate UV maps & apply materials")
        features_box.label(text="✅ Animate rigs based on motion capture data")

        cmd_box = left_box.box()
        cmd_box.label(text="Command Shortcuts:", icon='CONSOLE')
        cmd_box.label(text="# Attach 3D reference images or material assets")
        cmd_box.label(text="@ Invoke 3D plugins (cmd)")

        warning_box = left_box.box()
        warning_row = warning_box.row()
        warning_row.alert = True
        warning_row.label(text="3D models may contain topology or animation logic errors.", icon='ERROR')
        warning_row = warning_box.row()
        warning_row.alert = True
        warning_row.label(text="Validate keyframes and physics simulations.")

        # 右侧栏
        right_col = main_row.column()
        right_box = right_col.box()

        right_box.label(text="Live 3D Preview", icon='SHADING_WIRE')

        preview_box = right_box.box()
        preview_row = preview_box.row()
        preview_row.alignment = 'CENTER'
        preview_row.scale_y = 8.0

        if moco_props.uploaded_file:
            preview_row.label(text=f"Preview: {moco_props.uploaded_file}", icon='OUTLINER_OB_MESH')
        else:
            preview_row.label(text="3D Wireframe Model", icon='OUTLINER_OB_MESH')

        tools_row = right_box.row(align=True)
        tools_row.alignment = 'CENTER'
        tools_row.label(text="", icon='ORIENTATION_VIEW')
        tools_row.label(text="", icon='SHADING_SOLID')
        tools_row.label(text="", icon='CAMERA_DATA')

        # 底部状态栏
        layout.separator()
        footer_box = layout.box()
        footer_row = footer_box.row()

        # 左侧资源统计
        left_footer = footer_row.column()
        left_footer.label(text="3D Assets: 12", icon='OUTLINER_OB_MESH')

        # 中间文件信息
        middle_footer = footer_row.column()
        middle_footer.alignment = 'CENTER'
        if moco_props.uploaded_file:
            middle_footer.label(text=f"{moco_props.uploaded_file}:Mesh[Body] -- Material[Auto]")
        else:
            middle_footer.label(text="character_model.fbx:Mesh[Body] -- Material[Skin]")

        # 右侧引擎标识
        right_footer = footer_row.column()
        right_footer.alignment = 'RIGHT'
        right_footer.label(text="🧠 NVIDIA Omniverse (beta)", icon='GPU')

        # 输入区域 - 强调高度而非宽度
        input_box = layout.box()

        # 输入框行
        input_row = input_box.row()

        # 输入框 - 适当的高度和宽度
        input_col = input_row.column()
        input_col.scale_y = 6.0  # 适当的高度
        input_col.scale_x = 0.8  # 适当的宽度
        input_col.prop(moco_props, "message", text="", placeholder="Type a command (e.g. /subdivide, @plugin)")

        # 发送按钮
        send_col = input_row.column()
        send_col.scale_x = 0.8  # 增加宽度确保按钮完全显示
        send_col.scale_y = 6.0  # 与输入框高度一致
        send_col.operator("moco.send_command", text="发送", icon='PLAY')

        # 再添加一个输入框行以增加总体高度
        input_row2 = input_box.row()
        input_col2 = input_row2.column()
        input_col2.scale_y = 6.0
        input_col2.enabled = False  # 禁用该行，只用于占位增加高度
        input_col2.prop(moco_props, "message", text="", placeholder="")

        # 再添加一个输入框行以增加总体高度
        input_row3 = input_box.row()
        input_col3 = input_row3.column()
        input_col3.scale_y = 6.0
        input_col3.enabled = False  # 禁用该行，只用于占位增加高度
        input_col3.prop(moco_props, "message", text="", placeholder="")


# 初始化3D Moder Copilot
class MOCO_OT_initialize(Operator):
    bl_idname = "moco.initialize"
    bl_label = "Initialize 3D Moder Copilot"
    bl_description = "Initialize the 3D Moder Copilot"

    def execute(self, context):
        scene = context.scene
        scene.moco_props.mode = 'MODER'
        scene.moco_props.message = ""
        scene.moco_props.uploaded_file = ""
        scene.moco_props.file_details = ""

        self.report({'INFO'}, "3D Moder Copilot initialized")
        return {'FINISHED'}


# 设置模式
class MOCO_OT_set_mode(Operator):
    bl_idname = "moco.set_mode"
    bl_label = "Set Mode"
    bl_description = "Set the 3D Moder Copilot mode"

    mode: StringProperty(name="Mode", default="MODER")

    def execute(self, context):
        context.scene.moco_props.mode = self.mode
        mode_name = "Agent Mode" if self.mode == 'AGENT' else "3D Moder Mode"
        self.report({'INFO'}, f"Mode set to {mode_name}")
        return {'FINISHED'}


# 上传文件
class MOCO_OT_upload_file(Operator):
    bl_idname = "moco.upload_file"
    bl_label = "Upload File"
    bl_description = "Upload a 3D model file"

    filepath: StringProperty(name="File Path", description="Path to the file", default="", subtype='FILE_PATH')

    filter_glob: StringProperty(default="*.obj;*.fbx;*.glb", options={'HIDDEN'})

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        import os

        filename = os.path.basename(self.filepath)
        filesize = os.path.getsize(self.filepath) / 1024  # KB
        filetype = os.path.splitext(self.filepath)[1]

        context.scene.moco_props.uploaded_file = filename
        context.scene.moco_props.file_details = f"{filename} ({filetype}, {filesize:.2f} KB)"

        self.report({'INFO'}, f"Uploaded: {filename}")
        return {'FINISHED'}


# 发送命令
class MOCO_OT_send_command(Operator):
    bl_idname = "moco.send_command"
    bl_label = "Send Command"
    bl_description = "Send a command to 3D Moder Copilot"

    def execute(self, context):
        message = context.scene.moco_props.message
        if not message:
            self.report({'WARNING'}, "Please enter a command")
            return {'CANCELLED'}

        # 处理命令
        if message.startswith('/'):
            self.report({'INFO'}, f"Executing command: {message}")
        elif message.startswith('@'):
            self.report({'INFO'}, f"Invoking plugin: {message}")
        elif message.startswith('#'):
            self.report({'INFO'}, f"Attaching reference: {message}")
        else:
            self.report({'INFO'}, f"Processing: {message}")

        # 清空输入框
        context.scene.moco_props.message = ""

        return {'FINISHED'}


# 在顶部栏添加3D Moder Copilot按钮
def draw_3d_moder_button(self, context):
    layout = self.layout

    # 3D MODER COPILOT按钮 - 放在最右侧
    row = layout.row(align=True)
    row.alignment = 'RIGHT'
    row.scale_x = 1.5
    row.scale_y = 1.5
    row.alert = True  # 使按钮更加醒目

    # 使用亮蓝色文字和3D立方体图标
    row.popover(panel="VIEW3D_PT_3d_moder_copilot", text="3D MODER COPILOT", icon='CUBE')


# 要注册的类列表
classes = (
    MoCoProperties,
    VIEW3D_PT_3d_moder_copilot,
    MOCO_OT_initialize,
    MOCO_OT_set_mode,
    MOCO_OT_upload_file,
    MOCO_OT_send_command,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # 注册属性组
    bpy.types.Scene.moco_props = PointerProperty(type=MoCoProperties)

    # 在顶部栏添加按钮
    bpy.types.TOPBAR_HT_upper_bar.append(draw_3d_moder_button)


def unregister():
    # 从顶部栏移除按钮
    bpy.types.TOPBAR_HT_upper_bar.remove(draw_3d_moder_button)

    # 移除属性组
    del bpy.types.Scene.moco_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

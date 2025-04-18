# SPDX-FileCopyrightText: 2023 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

import sys
import bpy
from bpy.types import (
    Panel,
    PropertyGroup,
    UIList,
)
from bpy.props import (
    EnumProperty,
    StringProperty,
    CollectionProperty,
    IntProperty,
    BoolProperty,
)


# Message item for chat history
class AIMessageItem(PropertyGroup):
    text: StringProperty(
        name="Message Text",
        description="Content of the message",
        default="",
    )
    is_user: BoolProperty(
        name="Is User",
        description="Whether this message is from the user or the AI",
        default=True,
    )


# Property group to store AI assistant settings
class AIAssistantProperties(PropertyGroup):
    mode: EnumProperty(
        name="Mode",
        description="Select the AI assistant mode",
        items=[
            ('AGENT', "Agent", "Use AI as an agent that can perform tasks"),
            ('CHAT', "Chat", "Use AI as a chat assistant for conversations"),
        ],
        default='AGENT',
    )

    message: StringProperty(
        name="Message",
        description="Message to send to the AI assistant",
        default="",
    )

    messages: CollectionProperty(
        type=AIMessageItem,
        name="Messages",
        description="Chat history",
    )

    active_message_index: IntProperty(
        name="Active Message Index",
        default=0,
    )

    keep_open: BoolProperty(
        name="Keep Panel Open",
        description="Keep the AI Assistant panel open",
        default=False,
    )


# Custom UI list for chat messages
class AI_UL_messages(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            if item.is_user:
                row.label(text=f"You: {item.text}", icon='USER')
            else:
                row.label(text=f"AI: {item.text}", icon='CONSOLE')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='TEXT')


# Main panel for the AI Assistant sidebar
class VIEW3D_PT_ai_assistant(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_label = "AI Assistant"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # Title with icon
        row = layout.row()
        row.label(text="AI Assistant", icon='COMMUNITY')

        # Check if the property group is registered
        if not hasattr(context.scene, "ai_assistant"):
            layout.label(text="AI Assistant not initialized yet.")
            layout.label(text="Please restart Blender.")

            # Try to register the property group
            row = layout.row()
            row.operator("ai.initialize", text="Initialize AI Assistant", icon='FILE_REFRESH')
            return

        ai_props = context.scene.ai_assistant

        # Mode selection
        box = layout.box()
        row = box.row()
        row.label(text="Mode:", icon='PRESET')

        # Create a row with two radio buttons for mode selection
        row = box.row()
        row.scale_y = 1.2
        row.prop(ai_props, "mode", expand=True)

        # Debug button (only visible in development mode)
        if bpy.app.debug:
            row = layout.row()
            row.operator("ai.debug", text="Debug", icon='CONSOLE')


# Import sys for forcing output flush


# Debug function that can be called from the Python console
def debug_ai_assistant():
    print("\n==== AI Assistant Debug Information ====", flush=True)
    if hasattr(bpy.context.scene, "ai_assistant"):
        ai_props = bpy.context.scene.ai_assistant
        print(f"Mode: {ai_props.mode}", flush=True)
        print(f"Message: {ai_props.message}", flush=True)
        print(f"Messages count: {len(ai_props.messages)}", flush=True)
        print(f"Keep open: {ai_props.keep_open}", flush=True)
        print(f"Active message index: {ai_props.active_message_index}", flush=True)
    else:
        print("AI Assistant not initialized yet.", flush=True)
    sys.stdout.flush()
    return "Debug information printed to console"


# 设置模式操作符
class AI_OT_set_mode(bpy.types.Operator):
    bl_idname = "ai.set_mode"
    bl_label = "Set Mode"
    bl_description = "Set the AI assistant mode"

    mode: StringProperty(name="Mode", default="AGENT")

    def execute(self, context):
        context.scene.ai_assistant.mode = self.mode
        mode_name = "Agent Mode" if self.mode == 'AGENT' else "3D Moder Mode"
        self.report({'INFO'}, f"Mode set to {mode_name}")
        return {'FINISHED'}


# Operator to send a message to the AI assistant
class AI_OT_send_message(bpy.types.Operator):
    bl_idname = "ai.send_message"
    bl_label = "Send Message"
    bl_description = "Send a message to the AI assistant"

    def execute(self, context):
        # Check if the property group is registered
        if not hasattr(context.scene, "ai_assistant"):
            self.report({'ERROR'}, "3D Moder Copilot not initialized yet. Please restart Blender.")
            return {'CANCELLED'}

        ai_props = context.scene.ai_assistant
        mode = ai_props.mode
        message = ai_props.message

        if not message.strip():
            self.report({'ERROR'}, "请输入消息或命令")
            return {'CANCELLED'}

        # Add user message to chat history
        user_msg = ai_props.messages.add()
        user_msg.text = message
        user_msg.is_user = True

        # 处理Agent模式下的命令
        if mode == 'AGENT':
            # 处理特定命令
            if message.startswith('/'):
                command = message.split()[0][1:]  # 提取命令名称

                # 根据命令类型生成响应
                if command == 'subdivide':
                    ai_response = f"Subdivided mesh: Body – {message.split()[1] if len(message.split()) > 1 else '1'} levels complete"
                elif command == 'auto_uv':
                    ai_response = "UV Unwrapping applied on 3 mesh islands."
                else:
                    ai_response = f"Executed command: {command}"
            else:
                ai_response = f"Processing: {message}"
        else:
            # 3D Moder模式下的响应
            ai_response = f"3D Moder: {message}"

        # 添加AI响应到历史记录
        ai_msg = ai_props.messages.add()
        ai_msg.text = ai_response
        ai_msg.is_user = False

        # 清空输入框
        ai_props.message = ""

        self.report({'INFO'}, f"Command processed: {message}")
        return {'FINISHED'}

        # Update the active index to show the latest message
        ai_props.active_message_index = len(ai_props.messages) - 1
        print(f"Active message index set to: {ai_props.active_message_index}")

        # Clear the message field after sending
        ai_props.message = ""

        # Set keep_open to True to keep the panel open
        ai_props.keep_open = True

        self.report({'INFO'}, f"消息已发送 ({mode} 模式)")
        return {'FINISHED'}


# Operator to clear chat history
class AI_OT_clear_history(bpy.types.Operator):
    bl_idname = "ai.clear_history"
    bl_label = "Clear History"
    bl_description = "Clear the chat history"

    def execute(self, context):
        # Check if the property group is registered
        if not hasattr(context.scene, "ai_assistant"):
            self.report({'ERROR'}, "AI Assistant not initialized yet. Please restart Blender.")
            return {'CANCELLED'}

        ai_props = context.scene.ai_assistant
        ai_props.messages.clear()
        ai_props.active_message_index = 0

        # Set keep_open to True to keep the panel open
        ai_props.keep_open = True

        self.report({'INFO'}, "对话历史已清除")
        return {'FINISHED'}


# Panel for fixed input box for AI Assistant
class VIEW3D_PT_ai_assistant_input(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_label = "3D Moder Copilot"
    bl_parent_id = "VIEW3D_PT_ai_assistant"
    bl_options = {'INSTANCED'}
    bl_ui_units_x = 80  # 增加宽度
    bl_ui_units_y = 60  # 增加高度

    def draw(self, context):
        layout = self.layout

        # Check if the property group is registered
        if not hasattr(context.scene, "ai_assistant"):
            layout.label(text="3D Moder Copilot not initialized yet.")
            layout.label(text="Please restart Blender.")

            # Try to register the property group
            row = layout.row()
            row.operator("ai.initialize", text="Initialize 3D Moder", icon='FILE_REFRESH')
            return

        ai_props = context.scene.ai_assistant

        # 顶部标题栏 - 带有边框的盒子
        title_box = layout.box()
        title_row = title_box.row()
        title_row.scale_y = 1.5
        title_row.label(text="🧊 3D MODER COPILOT – 建模智能助手", icon='OUTLINER_OB_MESH')

        if ai_props.mode == 'AGENT':
            title_row.label(text="（Agent模式）")
        else:
            title_row.label(text="（3D Moder模式）")

        # 模式切换区
        mode_box = layout.box()
        mode_row = mode_box.row(align=True)
        mode_row.scale_y = 1.5

        # Agent模式按钮
        if ai_props.mode == 'AGENT':
            agent_btn = mode_row.operator("ai.set_mode", text="✅ Agent Mode", icon='TOOL_SETTINGS')
            agent_btn.mode = 'AGENT'
        else:
            agent_btn = mode_row.operator("ai.set_mode", text="Agent Mode", icon='TOOL_SETTINGS')
            agent_btn.mode = 'AGENT'

        mode_row.separator(factor=1.0)

        # 3D Moder模式按钮
        if ai_props.mode == 'CHAT':
            moder_btn = mode_row.operator("ai.set_mode", text="✅ 3D Moder Mode", icon='OUTLINER_OB_MESH')
            moder_btn.mode = 'CHAT'
        else:
            moder_btn = mode_row.operator("ai.set_mode", text="3D Moder Mode", icon='OUTLINER_OB_MESH')
            moder_btn.mode = 'CHAT'

        # Agent模式界面
        if ai_props.mode == 'AGENT':
            # 模型预览区
            preview_box = layout.box()
            preview_title = preview_box.row()
            preview_title.scale_y = 1.2
            preview_title.label(text="🔹 模型预览", icon='SHADING_WIRE')

            # 模型预览图像
            preview_img = preview_box.row()
            preview_img.scale_y = 6.0
            preview_img.alignment = 'CENTER'
            preview_img.label(text="默认模型加载（静态展示或旋转预览）", icon='OUTLINER_OB_MESH')

            # 操作记录/信息输出区
            log_box = layout.box()
            log_title = log_box.row()
            log_title.scale_y = 1.2
            log_title.label(text="🔸 操作记录 / 信息输出区", icon='TEXT')

            # 操作记录内容
            log_content = log_box.box()
            log_content.scale_y = 1.0

            # 系统消息
            system_row = log_content.row()
            system_row.label(text="[System] Loaded default character model.fbx")

            # 用户命令
            user_row1 = log_content.row()
            user_row1.label(text="[User] /subdivide 2")

            # AI响应
            ai_row1 = log_content.row()
            ai_row1.label(text="[AI] Subdivided mesh: Body – 2 levels complete")

            # 用户命令2
            user_row2 = log_content.row()
            user_row2.label(text="[User] /auto_uv")

            # AI响应2
            ai_row2 = log_content.row()
            ai_row2.label(text="[AI] UV Unwrapping applied on 3 mesh islands.")

            # 持续追加提示
            more_row = log_content.row()
            more_row.label(text="......（持续追加）")

            # 输入栏 + 发送按钮
            input_box = layout.box()
            input_title = input_box.row()
            input_title.scale_y = 1.2
            input_title.label(text="💬 输入栏 + 发送按钮", icon='CONSOLE')

            # 输入框行
            input_row = input_box.row()

            # 输入框
            input_col = input_row.column()
            input_col.scale_y = 2.0
            input_col.scale_x = 5.0
            input_col.prop(ai_props, "message", text="", placeholder="/subdivide 2")

            # 发送按钮
            send_col = input_row.column()
            send_col.scale_x = 0.5
            send_col.scale_y = 2.0
            send_col.operator("ai.send_message", text="发送 ➤", icon='PLAY')

        # 3D Moder模式界面
        else:
            # 双栏布局：左侧功能区，右侧预览区
            split = layout.split(factor=0.6)

            # 左侧功能面板（深灰底色）
            left_col = split.column()
            content_box = left_col.box()

            # 主操作引导
            title_row = content_box.row()
            title_row.scale_y = 1.5
            title_row.label(text="Edit 3D Model with AI", icon='MODIFIER')

            # 副标题
            subtitle_row = content_box.row()
            subtitle_row.scale_y = 1.2
            subtitle_row.label(text="Current Mode: Auto Topology Fix")

            # 符号指令栏
            cmd_box = content_box.box()
            cmd_title = cmd_box.row()
            cmd_title.scale_y = 1.2
            cmd_title.label(text="Input Commands:", icon='CONSOLE')

            # 指令示例
            commands = ["# 输入指令...", "@ 调用插件库", "/subdivide 2"]

            for cmd in commands:
                cmd_row = cmd_box.row()
                cmd_row.scale_y = 1.2
                cmd_row.label(text=cmd)

            # AI建议面板
            ai_box = content_box.box()
            ai_title = ai_box.row()
            ai_title.alert = True
            ai_title.scale_y = 1.2
            ai_title.label(text="[AI建议] 检测到3处非流形边 → 修复", icon='ERROR')

            # 材质/动画库
            material_box = content_box.box()
            material_title = material_box.row()
            material_title.scale_y = 1.2
            material_title.label(text="材质库", icon='MATERIAL')

            # 材质球列表
            material_row = material_box.row()
            material_row.scale_y = 1.5
            material_row.label(text="金属", icon='MATERIAL')
            material_row.label(text="塑料", icon='MATERIAL')
            material_row.label(text="玻璃", icon='MATERIAL')

            # 右侧预览窗口（黑色背景）
            right_col = split.column()
            preview_box = right_col.box()

            # 实时渲染区
            preview_title = preview_box.row()
            preview_title.scale_y = 1.2
            preview_title.label(text="3D Preview", icon='SHADING_WIRE')

            # 工具栏悬浮层 - 顶部
            tools_top = preview_box.row(align=True)
            tools_top.alignment = 'CENTER'
            tools_top.scale_y = 1.0
            tools_top.label(text="", icon='ORIENTATION_VIEW')
            tools_top.label(text="", icon='SHADING_SOLID')
            tools_top.label(text="", icon='CAMERA_DATA')

            # 模型预览图像
            preview_img = preview_box.row()
            preview_img.scale_y = 8.0
            preview_img.alignment = 'CENTER'
            preview_img.label(text="[可旋转模型]", icon='OUTLINER_OB_MESH')

            # 工具栏悬浮层 - 底部
            tools_bottom = preview_box.row(align=True)
            tools_bottom.alignment = 'CENTER'
            tools_bottom.scale_y = 1.0
            tools_bottom.label(text="", icon='VERTEXSEL')
            tools_bottom.label(text="", icon='EDGESEL')
            tools_bottom.label(text="", icon='FACESEL')

            # 悬浮工具提示
            tools_row = preview_box.row()
            tools_row.alignment = 'CENTER'
            tools_row.label(text="右键唤出工具环", icon='TOOL_SETTINGS')

            # 视图控制提示
            view_row = preview_box.row()
            view_row.alignment = 'CENTER'
            view_row.label(text="旋转: 方向键 | 缩放: 滚轮")

            # 底部状态栏（半透明黑色底栏）
            footer_box = layout.box()
            footer_row = footer_box.row()

            # 左侧功能区
            left_footer = footer_row.row()
            left_footer.alignment = 'LEFT'
            left_footer.label(text="3D Assets: 12 | Textures: 24", icon='OUTLINER_OB_MESH')

            # Add Context按钮
            add_context_btn = left_footer.operator("wm.context_toggle", text="Add Context...", icon='ADD')

            # 中间文件信息（高亮显示）
            middle_footer = footer_row.row()
            middle_footer.alignment = 'CENTER'
            middle_footer.alert = True  # 高亮显示
            middle_footer.label(text="character.fbx > Mesh[Body]")

            # 右侧引擎标识
            right_footer = footer_row.row()
            right_footer.alignment = 'RIGHT'
            right_footer.label(text="NVIDIA Omniverse AI Engine v2.1", icon='GPU')

            # 消息输入区 - 完整铺满整个程序
            input_box = layout.box()

            # 输入框行
            input_row = input_box.row()

            # 输入框 - 大尺寸
            input_col = input_row.column()
            input_col.scale_y = 3.0  # 增加高度
            input_col.scale_x = 5.0  # 增加宽度
            input_col.prop(ai_props, "message", text="", placeholder="Type a message or /subdivide, @")

            # 发送按钮
            send_col = input_row.column()
            send_col.scale_x = 0.2
            send_col.scale_y = 3.0  # 增加高度与输入框一致
            send_col.operator("ai.send_message", text="", icon='PLAY')


# Operator to toggle the AI Assistant panel
class AI_OT_quick_input(bpy.types.Operator):
    bl_idname = "ai.quick_input"
    bl_label = "AI Assistant"
    bl_description = "Open AI Assistant panel"

    def execute(self, context):
        # Add debug print statements with forced flush
        print("\n==== AI Assistant Quick Input ====", flush=True)
        print(f"Context: {context}", flush=True)

        # Check if the property group is registered
        if not hasattr(context.scene, "ai_assistant"):
            # Try to initialize the AI Assistant
            try:
                bpy.ops.ai.initialize()
            except Exception as e:
                self.report({'ERROR'}, f"Failed to initialize AI Assistant: {e}")
                print(f"Error initializing AI Assistant: {e}", flush=True)
                return {'CANCELLED'}

        # Open the properties panel and navigate to the AI Assistant section
        for area in context.screen.areas:
            if area.type == 'PROPERTIES':
                # Make sure the scene context is active
                for space in area.spaces:
                    if space.type == 'PROPERTIES':
                        space.context = 'SCENE'
                return {'FINISHED'}

        # If no properties area is found, try to create one
        # This is a more complex operation and might not always work as expected
        # For simplicity, we'll just report that the user should open the properties panel
        self.report({'INFO'}, "Please open the Properties panel to access AI Assistant")

        # Call the debug function
        debug_ai_assistant()

        return {'FINISHED'}


# Initialize AI Assistant operator
class AI_OT_initialize(bpy.types.Operator):
    bl_idname = "ai.initialize"
    bl_label = "Initialize AI Assistant"
    bl_description = "Initialize the AI Assistant property group"

    def execute(self, context):
        print("\n==== Initializing AI Assistant ====", flush=True)

        # Make sure the property class is registered
        try:
            if AIAssistantProperties not in bpy.utils.bl_rna_get_subclasses(bpy.types.PropertyGroup):
                bpy.utils.register_class(AIAssistantProperties)
                print("Registered AIAssistantProperties class", flush=True)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to register property class: {e}")
            print(f"Error registering AIAssistantProperties: {e}", flush=True)
            return {'CANCELLED'}

        # Register the property group
        try:
            if not hasattr(bpy.types.Scene, "ai_assistant"):
                bpy.types.Scene.ai_assistant = bpy.props.PointerProperty(type=AIAssistantProperties)
                print("Registered ai_assistant property", flush=True)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to register property group: {e}")
            print(f"Error registering ai_assistant property: {e}", flush=True)
            return {'CANCELLED'}

        # Initialize the property values
        try:
            context.scene.ai_assistant.keep_open = True
            context.scene.ai_assistant.message = ""
            print("Initialized ai_assistant properties", flush=True)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to initialize properties: {e}")
            print(f"Error initializing properties: {e}", flush=True)
            return {'CANCELLED'}

        self.report({'INFO'}, "AI Assistant initialized successfully")
        return {'FINISHED'}


# Debug operator with breakpoint
class AI_OT_debug(bpy.types.Operator):
    bl_idname = "ai.debug"
    bl_label = "Debug AI"
    bl_description = "Debug the AI Assistant (sets breakpoint)"

    def execute(self, context):
        print("\n==== AI Assistant Debug Breakpoint ====", flush=True)
        print("Setting breakpoint...", flush=True)
        sys.stdout.flush()

        # This will definitely trigger a breakpoint
        import pdb

        pdb.set_trace()

        # Create debug variables
        import builtins

        builtins.ai_debug_context = context
        builtins.ai_debug_self = self

        # Call the debug function
        debug_ai_assistant()

        return {'FINISHED'}


# Panel for chat history
class VIEW3D_PT_ai_assistant_history(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_label = "Chat History"
    bl_parent_id = "VIEW3D_PT_ai_assistant"

    def draw(self, context):
        layout = self.layout

        # Check if the property group is registered
        if not hasattr(context.scene, "ai_assistant"):
            layout.label(text="AI Assistant not initialized yet.")
            layout.label(text="Please restart Blender.")
            return

        ai_props = context.scene.ai_assistant

        # Display chat history using UIList
        layout.template_list("AI_UL_messages", "", ai_props, "messages", ai_props, "active_message_index", rows=10)

        # Clear chat history button
        row = layout.row()
        row.operator("ai.clear_history", text="Clear History", icon='TRASH')


# List of classes to register
classes = (
    AIMessageItem,
    # AIAssistantProperties is registered separately to ensure correct order
    # AIAssistantProperties,
    AI_UL_messages,
    VIEW3D_PT_ai_assistant,
    VIEW3D_PT_ai_assistant_history,
    VIEW3D_PT_ai_assistant_input,
    AI_OT_set_mode,
    AI_OT_send_message,
    AI_OT_clear_history,
    AI_OT_quick_input,
    AI_OT_initialize,
    AI_OT_debug,
)


# Handler to ensure the AI Assistant is properly initialized
@bpy.app.handlers.persistent
def ensure_ai_assistant_initialized(dummy):
    # Make sure we have a valid context
    if not hasattr(bpy, "context") or bpy.context is None:
        print("No valid context in handler", flush=True)
        return 0.1

    # Make sure we have a valid scene
    if not hasattr(bpy.context, "scene") or bpy.context.scene is None:
        print("No valid scene in handler", flush=True)
        return 0.1

    # Check if the property group is registered
    if not hasattr(bpy.context.scene, "ai_assistant"):
        # Register the property group if it's not already registered
        try:
            print("Attempting to register ai_assistant in handler...", flush=True)
            # Make sure the class is registered first
            if AIAssistantProperties not in bpy.utils.bl_rna_get_subclasses(bpy.types.PropertyGroup):
                bpy.utils.register_class(AIAssistantProperties)
            # Then register the property
            bpy.types.Scene.ai_assistant = bpy.props.PointerProperty(type=AIAssistantProperties)
            print("Successfully registered ai_assistant in handler", flush=True)
        except Exception as e:
            print(f"Error registering ai_assistant in handler: {e}", flush=True)
            # If we can't register it now, we'll try again later
            return 0.1

    return 1.0  # Check again in 1 second


def register():
    print("Registering AI Assistant...", flush=True)

    # First register the property class
    bpy.utils.register_class(AIAssistantProperties)

    # Then register the property group
    if not hasattr(bpy.types.Scene, "ai_assistant"):
        print("Creating ai_assistant property...", flush=True)
        bpy.types.Scene.ai_assistant = bpy.props.PointerProperty(type=AIAssistantProperties)

    # Register all other classes
    for cls in classes:
        if cls != AIAssistantProperties:  # Skip AIAssistantProperties as it's already registered
            bpy.utils.register_class(cls)

    # Register the handler to ensure the AI Assistant is properly initialized
    if ensure_ai_assistant_initialized not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(ensure_ai_assistant_initialized)

    # Force initialization of the property group
    # This is important to ensure it's available immediately
    if hasattr(bpy.context, "scene") and bpy.context.scene is not None:
        if hasattr(bpy.context.scene, "ai_assistant"):
            print("Initializing ai_assistant properties...", flush=True)
            bpy.context.scene.ai_assistant.keep_open = False
            bpy.context.scene.ai_assistant.message = ""
            print("AI Assistant initialized successfully!", flush=True)
        else:
            print("WARNING: ai_assistant property not available on scene", flush=True)
    else:
        print("WARNING: No valid scene context available for initialization", flush=True)


def unregister():
    print("Unregistering AI Assistant...", flush=True)

    # Unregister the handler
    if ensure_ai_assistant_initialized in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(ensure_ai_assistant_initialized)

    # Unregister all classes first
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Error unregistering {cls.__name__}: {e}", flush=True)

    # Unregister the property class last
    try:
        bpy.utils.unregister_class(AIAssistantProperties)
    except Exception as e:
        print(f"Error unregistering AIAssistantProperties: {e}", flush=True)

    # Remove the property group
    try:
        del bpy.types.Scene.ai_assistant
        print("AI Assistant property removed successfully", flush=True)
    except Exception as e:
        print(f"Error removing ai_assistant property: {e}", flush=True)


if __name__ == "__main__":
    register()

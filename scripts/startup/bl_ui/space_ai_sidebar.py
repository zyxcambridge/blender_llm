# SPDX-FileCopyrightText: 2023 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

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
    bl_space_type = 'TOPBAR'
    bl_region_type = 'HEADER'
    bl_label = "AI Assistant"
    bl_ui_units_x = 30

    def draw(self, context):
        layout = self.layout

        # Title with icon
        row = layout.row()
        row.label(text="AI Assistant", icon='COMMUNITY')

        # Check if the property group is registered
        if not hasattr(context.scene, "ai_assistant"):
            layout.label(text="AI Assistant not initialized yet.")
            layout.label(text="Please restart Blender.")
            return

        ai_props = context.scene.ai_assistant

        # Keep panel open option
        row = layout.row()
        row.prop(ai_props, "keep_open", text="Keep Panel Open")

        layout.separator()

        # Mode selection
        box = layout.box()
        row = box.row()
        row.label(text="Mode:", icon='PRESET')

        # Create a row with two radio buttons for mode selection
        row = box.row()
        row.scale_y = 1.2
        row.prop(ai_props, "mode", expand=True)

        # Chat history
        box = layout.box()
        row = box.row()
        row.label(text="Chat History:", icon='COMMUNITY')

        # Display chat history using UIList
        box.template_list("AI_UL_messages", "", ai_props, "messages", ai_props, "active_message_index", rows=6)

        # Message input area
        box = layout.box()
        row = box.row()
        row.label(text="Message:", icon='TEXT')

        # Larger input field
        col = box.column()
        col.scale_y = 2.0
        col.prop(ai_props, "message", text="")

        # Send button
        row = layout.row()
        row.scale_y = 1.5
        row.operator("ai.send_message", text="Send", icon='PLAY')

        # Clear chat history button
        row = layout.row()
        row.operator("ai.clear_history", text="Clear History", icon='TRASH')


# Import sys for forcing output flush
import sys


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


# Operator to send a message to the AI assistant
class AI_OT_send_message(bpy.types.Operator):
    bl_idname = "ai.send_message"
    bl_label = "Send Message"
    bl_description = "Send a message to the AI assistant"

    def execute(self, context):
        # Add debug print statements with forced flush
        print("\n==== AI Assistant Send Message ====", flush=True)
        print(f"Context: {context}", flush=True)

        # Create a global variable for debugging
        import builtins

        builtins.ai_debug_context = context
        builtins.ai_debug_self = self
        print("Debug variables set: ai_debug_context, ai_debug_self", flush=True)

        # Force flush all output
        sys.stdout.flush()

        # Check if the property group is registered
        if not hasattr(context.scene, "ai_assistant"):
            self.report({'ERROR'}, "AI Assistant not initialized yet. Please restart Blender.")
            return {'CANCELLED'}

        ai_props = context.scene.ai_assistant
        mode = ai_props.mode
        message = ai_props.message

        if not message.strip():
            self.report({'ERROR'}, "请输入消息")
            return {'CANCELLED'}

        # Add user message to chat history
        print(f"Adding user message: {message}")
        user_msg = ai_props.messages.add()
        user_msg.text = message
        user_msg.is_user = True
        print(f"User message added, total messages: {len(ai_props.messages)}")

        # Here you would implement the actual functionality to send the message
        # to either the agent or chat system and get a response

        # For now, just add a dummy AI response
        print(f"Adding AI response in mode: {mode}")
        ai_msg = ai_props.messages.add()
        if mode == 'AGENT':
            ai_msg.text = f"Agent收到: {message}"
        else:
            ai_msg.text = f"Chat回复: {message}"
        ai_msg.is_user = False
        print(f"AI response added, total messages: {len(ai_props.messages)}")

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
    bl_space_type = 'TOPBAR'
    bl_region_type = 'HEADER'
    bl_label = "AI Assistant Input"
    bl_ui_units_x = 30

    def draw(self, context):
        # Add debug print statements
        print("\n==== AI Assistant Panel Draw ====")
        print(f"Context: {context}")

        # Uncomment the line below to use pdb for interactive debugging
        # import pdb; pdb.set_trace()

        layout = self.layout

        # Check if the property group is registered
        if not hasattr(context.scene, "ai_assistant"):
            layout.label(text="AI Assistant not initialized yet.")
            layout.label(text="Please restart Blender.")
            return

        ai_props = context.scene.ai_assistant

        # Title with icon
        row = layout.row()
        row.label(text="AI Assistant", icon='COMMUNITY')

        # Message input area
        box = layout.box()

        # Larger input field
        col = box.column()
        col.scale_y = 2.0
        col.prop(ai_props, "message", text="")

        # Send button
        row = layout.row()
        row.scale_y = 1.5
        row.operator("ai.send_message", text="Send", icon='PLAY')


# Operator to toggle the AI Assistant input panel
class AI_OT_quick_input(bpy.types.Operator):
    bl_idname = "ai.quick_input"
    bl_label = "AI Assistant"
    bl_description = "Toggle AI Assistant input panel"

    def execute(self, context):
        # Check if the property group is registered
        if not hasattr(context.scene, "ai_assistant"):
            self.report({'ERROR'}, "AI Assistant not initialized yet. Please restart Blender.")
            return {'CANCELLED'}

        # Toggle the keep_open property to show/hide the panel
        ai_props = context.scene.ai_assistant
        ai_props.keep_open = not ai_props.keep_open

        return {'FINISHED'}


# List of classes to register
classes = (
    AIMessageItem,
    AIAssistantProperties,
    AI_UL_messages,
    VIEW3D_PT_ai_assistant,
    VIEW3D_PT_ai_assistant_input,
    AI_OT_send_message,
    AI_OT_clear_history,
    AI_OT_quick_input,
)


# Handler to keep the AI Assistant panel open
@bpy.app.handlers.persistent
def keep_ai_panel_open(dummy):
    # Check if the property group is registered
    if not hasattr(bpy.context.scene, "ai_assistant"):
        # Register the property group if it's not already registered
        try:
            bpy.types.Scene.ai_assistant = bpy.props.PointerProperty(type=AIAssistantProperties)
        except:
            # If we can't register it now, we'll try again later
            return 0.1

    # Check if the panel should be kept open
    if bpy.context.scene.ai_assistant.keep_open:
        # Force the panel to stay open by accessing it
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'TOPBAR':
                    # This will force the panel to stay open
                    pass
    return 0.1  # Check again in 0.1 seconds


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register the property group
    if not hasattr(bpy.types.Scene, "ai_assistant"):
        bpy.types.Scene.ai_assistant = bpy.props.PointerProperty(type=AIAssistantProperties)

    # Register the handler to keep the panel open
    if keep_ai_panel_open not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(keep_ai_panel_open)

    # Initialize a default message
    if hasattr(bpy.context.scene, "ai_assistant"):
        bpy.context.scene.ai_assistant.keep_open = False


def unregister():
    # Unregister the handler
    if keep_ai_panel_open in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(keep_ai_panel_open)

    # Unregister the property group
    del bpy.types.Scene.ai_assistant

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

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
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_label = "Input"
    bl_parent_id = "VIEW3D_PT_ai_assistant"

    def draw(self, context):
        # Add debug print statements with forced flush
        print("\n==== AI Assistant Panel Draw ====", flush=True)
        print(f"Context: {context}", flush=True)

        layout = self.layout

        # Check if the property group is registered
        if not hasattr(context.scene, "ai_assistant"):
            layout.label(text="AI Assistant not initialized yet.")
            layout.label(text="Please restart Blender.")

            # Try to register the property group
            row = layout.row()
            row.operator("ai.initialize", text="Initialize AI Assistant", icon='FILE_REFRESH')
            return

        ai_props = context.scene.ai_assistant

        # Create a column that pushes content to the bottom
        col = layout.column()
        col.alignment = 'EXPAND'

        # Add spacer to push content to bottom
        col.separator(factor=4.0)

        # Message input area with larger input field
        input_col = col.column()
        input_col.scale_y = 2.0
        input_col.prop(ai_props, "message", text="")

        # Send button
        row = col.row()
        row.scale_y = 1.5
        row.operator("ai.send_message", text="Send", icon='PLAY')


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

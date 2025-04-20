import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup, UIList, Panel, Operator

# Print debug information
print("\n==== AI Assistant Initialization Script ====", flush=True)


# Define the message item class
class AIMessageItem(PropertyGroup):
    text: StringProperty(name="Message", description="Message text", default="")
    is_user: BoolProperty(name="Is User", description="Whether this message is from the user", default=False)


# Define the AI Assistant properties
class AIAssistantProperties(PropertyGroup):
    mode: EnumProperty(
        name="Mode",
        description="AI Assistant mode",
        items=[('AGENT', "Agent", "Agent mode"), ('CHAT', "Chat", "Chat mode")],
        default='AGENT',
    )
    message: StringProperty(name="Message", description="Message to send to the AI assistant", default="")
    messages: CollectionProperty(type=AIMessageItem, name="Messages", description="Chat history")
    active_message_index: IntProperty(name="Active Message Index", description="Index of the active message", default=0)
    keep_open: BoolProperty(name="Keep Open", description="Keep the AI Assistant panel open", default=False)


# Register the classes
def register():
    print("Registering AI Assistant properties from init script...", flush=True)
    try:
        # Register the classes
        bpy.utils.register_class(AIMessageItem)
        bpy.utils.register_class(AIAssistantProperties)

        # Register the property group
        if not hasattr(bpy.types.Scene, "ai_assistant"):
            bpy.types.Scene.ai_assistant = PointerProperty(type=AIAssistantProperties)
            print("AI Assistant property group registered successfully!", flush=True)
        else:
            print("AI Assistant property group already registered.", flush=True)

        # Initialize the property values if possible
        if hasattr(bpy.context, "scene") and bpy.context.scene is not None:
            if hasattr(bpy.context.scene, "ai_assistant"):
                bpy.context.scene.ai_assistant.keep_open = False
                bpy.context.scene.ai_assistant.message = ""
                print("AI Assistant properties initialized successfully!", flush=True)
            else:
                print("WARNING: ai_assistant property not available on scene", flush=True)
        else:
            print("WARNING: No valid scene context available for initialization", flush=True)

    except Exception as e:
        print(f"ERROR registering AI Assistant properties: {e}", flush=True)


# Unregister the classes
def unregister():
    print("Unregistering AI Assistant properties from init script...", flush=True)
    try:
        # Remove the property group
        if hasattr(bpy.types.Scene, "ai_assistant"):
            del bpy.types.Scene.ai_assistant
            print("AI Assistant property group unregistered successfully!", flush=True)

        # Unregister the classes
        bpy.utils.unregister_class(AIAssistantProperties)
        bpy.utils.unregister_class(AIMessageItem)
    except Exception as e:
        print(f"ERROR unregistering AI Assistant properties: {e}", flush=True)


# Register the classes when the script is run
if __name__ == "__main__":
    register()

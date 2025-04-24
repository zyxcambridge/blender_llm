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
    reflection_count: IntProperty(name="反思次数", description="Gemini反思/评估最大次数", default=5, min=1, max=20)


# 自动展开 Outliner 树
import bpy

def expand_outliner():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'OUTLINER':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {
                            'window': window,
                            'screen': window.screen,
                            'area': area,
                            'region': region,
                            'scene': bpy.context.scene,
                        }
                        try:
                            bpy.ops.outliner.show_hierarchy(override)
                        except Exception as e:
                            print(f"[Outliner Auto Expand] Error: {e}", flush=True)
                        return  # 只展开第一个找到的 Outliner
    # 如果没找到，延迟重试
    return 1.0

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

    # 注册定时器，Blender 启动后自动展开 Outliner
    bpy.app.timers.register(expand_outliner, first_interval=1)


# Unregister the classes
def unregister():
    # 取消定时器（如果有需要，可以用更复杂的方式追踪定时器，但Blender会在关闭时自动清理）
    pass

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

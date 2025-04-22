# SPDX-FileCopyrightText: 2023 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

import sys
import os
import json
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


# 加载配置文件
def load_config():
    """从JSON配置文件加载设置"""
    config_path = os.path.join(os.path.dirname(__file__), "ai_assistant_config.json")
    default_config = {
        "default_prompts": {
            "cartoon_character": "为一个名为「小兔子」的卡通角色创建完整3D模型...",
            "placeholder_short": "为一个名为「小兔子」的卡通角色创建完整3D模型，包含头部、耳朵、眼睛、嘴巴、手臂、腿部和尾巴等结构...",
            "chat_mode": "Type a message or /subdivide, @",
        }
    }

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"配置文件不存在: {config_path}，使用默认配置", flush=True)
            return default_config
    except Exception as e:
        print(f"加载配置文件出错: {e}，使用默认配置", flush=True)
        return default_config


# 全局配置变量
CONFIG = load_config()


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
    # 移除模式切换功能，只保留Agent模式
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

    # 添加一个隐藏的模式属性，始终为'AGENT'，用于兼容现有代码
    mode: StringProperty(
        name="Mode",
        description="AI Assistant mode (always AGENT)",
        default="AGENT",
    )


# 移除消息列表UI类


# Main panel for the AI Assistant sidebar
class VIEW3D_PT_ai_assistant(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_label = "AI Assistant"
    bl_options = {'DEFAULT_CLOSED'}
    bl_ui_units_x = 120  # 增加宽度
    bl_ui_units_y = 80  # 增加高度

    def draw(self, context):
        layout = self.layout

        # Check if the property group is registered
        if not hasattr(context.scene, "ai_assistant"):
            layout.label(text="AI Assistant not initialized yet.")
            layout.label(text="Please restart Blender.")

            # Try to register the property group
            row = layout.row()
            row.operator("ai.initialize", text="Initialize AI Assistant", icon='FILE_REFRESH')
            return

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
        print(f"Message: {ai_props.message}", flush=True)
        print(f"Messages count: {len(ai_props.messages)}", flush=True)
        print(f"Keep open: {ai_props.keep_open}", flush=True)
        print(f"Active message index: {ai_props.active_message_index}", flush=True)
    else:
        print("AI Assistant not initialized yet.", flush=True)
    sys.stdout.flush()
    return "Debug information printed to console"


# 移除不需要的模式切换操作符


# Operator to send a message to the AI assistant
class AI_OT_send_message(bpy.types.Operator):
    bl_idname = "ai.send_message"
    bl_label = "Send Message"
    bl_description = "Send a message to the AI assistant"

    def execute(self, context):
        # 获取AI助手属性
        ai_props = context.scene.ai_assistant

        # 获取用户输入的消息
        message = ai_props.message

        # 检查消息是否为空，如果为空则使用默认内容
        if not message.strip():
            # 从配置文件读取默认提示文本
            message = CONFIG.get("default_prompts", {}).get(
                "cartoon_character", "为一个名为「小兔子」的卡通角色创建完整3D模型..."
            )

            # 更新输入框显示默认消息
            ai_props.message = message

        # 添加用户消息到历史记录
        user_msg = ai_props.messages.add()
        user_msg.text = message
        user_msg.is_user = True

        # 处理用户消息
        # 导入Gemini API集成模块
        try:
            import ai_gemini_integration

            print("\n==== 使用Google Gemini API生成Blender代码 ====\n", flush=True)
            print(f"用户输入: {message}", flush=True)

            # 使用Gemini API生成Blender代码
            success, result = ai_gemini_integration.generate_blender_code(message)

            if success:
                print("\n[Gemini] 代码生成成功，准备执行...", flush=True)

                # 构建AI响应
                ai_response = f"已使用Google Gemini生成并执行以下代码:\n"
                ai_response += f"```python\n{result[:200]}...\n```\n\n"

                # 执行生成的代码
                exec_success, exec_result = ai_gemini_integration.execute_blender_code(result)

                if exec_success:
                    ai_response += "✅ 代码执行成功，3D模型已生成。\n"
                    ai_response += "\n您可以继续输入更多细节来完善模型。例如:\n"
                    ai_response += "- 调整尺寸和比例\n"
                    ai_response += "- 添加更多细节和功能部件\n"
                    ai_response += "- 修改材质和颜色\n"
                else:
                    ai_response += f"❌ 代码执行失败: {exec_result}\n"
                    print(f"[Gemini] 执行错误: {exec_result}", flush=True)
            else:
                # 如果Gemini API调用失败，提供错误反馈
                print(f"[Gemini] API调用失败: {result}", flush=True)
                ai_response = f"❌ Gemini API调用失败: {result}\n\n"
                ai_response += "请检查以下可能的问题:\n"
                ai_response += "- API密钥是否正确配置\n"
                ai_response += "- 网络连接是否正常\n"
                ai_response += "- 请求是否符合API要求\n\n"
                ai_response += "您可以尝试重新发送请求或修改您的描述后再试。"
        except ImportError:
            print("\n[错误] 无法导入ai_gemini_integration模块", flush=True)

            # 提供错误反馈
            ai_response = "❌ 系统错误: 无法加载Gemini API集成模块\n\n"
            ai_response += "请检查以下可能的问题:\n"
            ai_response += "- Blender安装是否完整\n"
            ai_response += "- ai_gemini_integration.py文件是否存在于正确位置\n"
            ai_response += "- 是否有权限访问该文件\n\n"
            ai_response += "请联系系统管理员解决此问题。"

        # 添加AI响应到历史记录
        ai_msg = ai_props.messages.add()
        ai_msg.text = ai_response
        ai_msg.is_user = False

        # 清空输入框
        ai_props.message = ""

        # 更新活动索引以显示最新消息
        ai_props.active_message_index = len(ai_props.messages) - 1

        # 设置keep_open为True以保持面板打开
        ai_props.keep_open = True

        # 立即刷新UI以显示最新消息
        for area in context.screen.areas:
            area.tag_redraw()

        self.report({'INFO'}, "指令已处理")
        return {'FINISHED'}

    # 移除不需要的方法


# 移除清除历史记录的操作符


# Panel for fixed input box for AI Assistant
class VIEW3D_PT_ai_assistant_input(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_label = "AI Assistant"
    bl_parent_id = "VIEW3D_PT_ai_assistant"
    bl_options = {'INSTANCED'}
    bl_ui_units_x = 80  # 增加宽度
    bl_ui_units_y = 60  # 增加高度

    def draw(self, context):
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

        # 移除标题栏和模式切换区

        # 显示主界面

        # 操作记录/信息输出区
        log_box = layout.box()
        log_title = log_box.row()
        log_title.scale_y = 1.2
        log_title.label(text="🔸 操作记录 / 信息输出区", icon='TEXT')

        # 移除所有按钮

        # 操作记录内容
        log_content = log_box.box()
        log_content.scale_y = 1.0

        # 显示历史对话记录
        if hasattr(ai_props, "messages") and len(ai_props.messages) > 0:
            # 最多显示最近的8条消息
            start_idx = max(0, len(ai_props.messages) - 8)

            for i in range(start_idx, len(ai_props.messages)):
                msg = ai_props.messages[i]
                msg_row = log_content.row()

                if msg.is_user:
                    msg_row.label(text=f"[User] {msg.text[:60]}{'...' if len(msg.text) > 60 else ''}")
                else:
                    msg_row.label(text=f"[AI] {msg.text[:60]}{'...' if len(msg.text) > 60 else ''}")
        else:
            # 如果没有历史消息，不显示任何默认内容
            pass

        # 3. 用户需求输入文本区
        input_box = layout.box()
        input_title = input_box.row()
        input_title.scale_y = 1.2
        input_title.label(text="💬 输入栏 + 发送按钮", icon='CONSOLE')

        # 输入框行
        input_row = input_box.row()

        # 输入框
        input_col = input_row.column()
        input_col.scale_y = 2.0
        input_col.scale_x = 8.0  # 增加输入框宽度
        # 从配置文件读取占位符文本
        placeholder_text = CONFIG.get("default_prompts", {}).get(
            "placeholder_short",
            "为一个名为「小兔子」的卡通角色创建完整3D模型，包含头部、耳朵、眼睛、嘴巴、手臂、腿部和尾巴等结构...",
        )

        input_col.prop(
            ai_props,
            "message",
            text="",
            placeholder=placeholder_text,
        )

        # 发送按钮
        send_col = input_row.column()
        send_col.scale_x = 1.0
        send_col.scale_y = 2.0
        send_col.operator("ai.send_message", text="发送", icon='PLAY')

        # 4. 执行Blender Python脚本按钮
        script_box = layout.box()
        script_row = script_box.row()
        script_row.scale_y = 1.5
        script_row.operator("ai.execute_script", text="执行 Blender Python 脚本", icon='SCRIPT')


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


# 需要在classes列表之前添加AI_OT_refresh_history类定义


# 移除刷新历史记录的操作符


# 移除重新加载配置文件的操作符


# 移除重复的VIEW3D_PT_ai_assistant_input类


# 移除快速输入操作符


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


# 移除聊天历史面板


# 移除设置代码保存目录的操作符


# 移除显示当前代码保存目录的操作符


# 添加切换AI Assistant面板显示的操作符
class AI_OT_toggle_panel(bpy.types.Operator):
    bl_idname = "ai.toggle_panel"
    bl_label = "切换AI Assistant面板"
    bl_description = "切换AI Assistant面板的显示状态"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # 切换keep_open属性
        if hasattr(context.scene, "ai_assistant"):
            context.scene.ai_assistant.keep_open = not context.scene.ai_assistant.keep_open

            # 强制刷新UI
            for area in context.screen.areas:
                area.tag_redraw()

            status = "打开" if context.scene.ai_assistant.keep_open else "关闭"
            self.report({'INFO'}, f"AI Assistant面板已{status}")
        else:
            self.report({'ERROR'}, "AI Assistant尚未初始化")
            return {'CANCELLED'}
        return {'FINISHED'}


# 添加执行Blender Python脚本的操作符
class AI_OT_execute_script(bpy.types.Operator):
    bl_idname = "ai.execute_script"
    bl_label = "执行脚本"
    bl_description = "执行生成的Blender Python脚本"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            import ai_gemini_integration

            # 获取脚本文件路径
            script_path = os.path.join(ai_gemini_integration.get_code_save_directory(), "gemini_latest_code.py")

            if not os.path.exists(script_path):
                self.report({'ERROR'}, f"脚本文件不存在: {script_path}")
                return {'CANCELLED'}

            # 执行脚本
            print(f"\n[Blender Script] 正在执行脚本: {script_path}", flush=True)
            with open(script_path, 'r', encoding='utf-8') as f:
                script_code = f.read()

            # 使用exec执行脚本
            exec_globals = {
                'bpy': bpy,
                '__file__': script_path,
                'math': __import__('math'),
                'bmesh': __import__('bmesh'),
                'log': lambda msg: print(f"Log: {msg}", flush=True),
            }
            exec(script_code, exec_globals)

            self.report({'INFO'}, "脚本执行完成")
        except ImportError as e:
            self.report({'ERROR'}, f"无法导入模块: {str(e)}")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"执行脚本时出错: {str(e)}")
            print(traceback.format_exc(), flush=True)
            return {'CANCELLED'}
        return {'FINISHED'}


# 在register函数之前的类列表中添加新的操作符
classes = (
    AIMessageItem,
    # AIAssistantProperties, # 这个类通常单独注册
    VIEW3D_PT_ai_assistant,
    VIEW3D_PT_ai_assistant_input,
    AI_OT_send_message,
    AI_OT_initialize,
    AI_OT_toggle_panel,  # 添加切换AI Assistant面板显示的操作符
    AI_OT_execute_script,  # 添加执行Blender Python脚本的操作符
)


# Handler to ensure the AI Assistant is properly initialized
@bpy.app.handlers.persistent
def ensure_ai_assistant_initialized(dummy):
    # Make sure we have a valid context
    if not hasattr(bpy, "context") or bpy.context is None:
        print(
            "No valid 屏幕上你看到的左边的这个应用是电视剧都不敢这么演，昨天送完背背后。context in handler", flush=True
        )
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

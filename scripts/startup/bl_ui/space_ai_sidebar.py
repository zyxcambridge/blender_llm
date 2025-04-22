# SPDX-FileCopyrightText: 2023 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

import sys
import os
import json
import traceback
import bpy
from bpy.types import (
    Panel,
    PropertyGroup,
    # UIList, # Not currently used directly in panel drawing
)
from bpy.props import (
    # EnumProperty, # Not used
    StringProperty,
    CollectionProperty,
    IntProperty,
    BoolProperty,
)


# --- Configuration Loading ---


def load_config():
    """从JSON配置文件加载设置"""
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "ai_assistant_config.json")
    default_config = {
        "default_prompts": {
            "cartoon_character": "为一个名为「小兔子」的卡通角色创建完整3D模型...",
            "placeholder_short": "描述你想创建的模型...",
            "chat_mode": "Type a message or /subdivide, @",
        },
        "script_filename": "gemini_latest_code.py",
    }
    config = default_config
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                config.update(loaded_config)
                print(f"配置已加载: {config_path}", flush=True)
        else:
            print(f"配置文件不存在: {config_path}，使用默认配置。", flush=True)
    except json.JSONDecodeError as e:
        print(f"加载配置文件JSON解析错误: {e}，使用默认配置。", flush=True)
        config = default_config
    except Exception as e:
        print(f"加载配置文件时发生未知错误: {e}，使用默认配置。", flush=True)
        config = default_config
    return config


CONFIG = load_config()
SCRIPT_FILENAME = CONFIG.get("script_filename", "gemini_latest_code.py")


# --- Properties ---


class AIMessageItem(PropertyGroup):
    text: StringProperty(default="")
    is_user: BoolProperty(default=True)


class AIAssistantProperties(PropertyGroup):
    message: StringProperty(default="")
    messages: CollectionProperty(type=AIMessageItem)
    active_message_index: IntProperty(default=-1)
    keep_open: BoolProperty(default=True)
    use_pin: BoolProperty(default=True)
    mode: StringProperty(default="AGENT")  # Keep internal mode


# --- Main Panel (in 3D View Sidebar with Chinese Labels) ---


class VIEW3D_PT_ai_assistant(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender AI助手"  # <<< Changed: Sidebar Tab Name (Chinese)
    bl_label = "Blender AI助手"  # <<< Changed: Panel Title (Chinese)

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "ai_assistant")

    def draw_header(self, context):
        if hasattr(context.scene, "ai_assistant"):
            ai_props = context.scene.ai_assistant
            layout = self.layout
            layout.prop(ai_props, "use_pin", text="", icon='PINNED' if ai_props.use_pin else 'UNPINNED', emboss=False)
            # Label set by bl_label

    def draw(self, context):
        layout = self.layout
        if not hasattr(context.scene, "ai_assistant"):
            layout.label(text="Blender AI助手尚未初始化。")  # <<< Changed
            row = layout.row()
            # Keep operator ID english, but label chinese
            row.operator("ai.initialize", text="初始化 Blender AI助手", icon='FILE_REFRESH')  # <<< Changed
            return

        # Debug button
        if bpy.app.debug:
            row = layout.row(align=True)
            row.operator("ai.initialize", text="重新初始化", icon='FILE_REFRESH')  # <<< Changed
            # row.operator("ai.debug", text="调试", icon='CONSOLE') # Optional debug button


# --- Child Panel for Input/History ---
# This contains the main UI elements drawn within the parent panel
class VIEW3D_PT_ai_assistant_input(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender AI助手"  # <<< Changed: Match Parent Category
    bl_parent_id = VIEW3D_PT_ai_assistant.__name__
    bl_options = {'HIDE_HEADER'}  # Hide this sub-panel's header
    bl_label = "输入与历史"  # Internal label if header wasn't hidden

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "ai_assistant")

    def draw(self, context):
        layout = self.layout
        ai_props = context.scene.ai_assistant

        # --- History Section ---
        history_box = layout.box()
        history_header = history_box.row(align=True)
        history_header.label(text="历史记录", icon='INFO')  # <<< Changed
        history_header.operator("ai.clear_history", text="", icon='TRASH', emboss=False)

        if len(ai_props.messages) > 0:
            history_content_box = history_box.box()
            max_history_display = 10
            start_idx = max(0, len(ai_props.messages) - max_history_display)
            for i in range(start_idx, len(ai_props.messages)):
                msg = ai_props.messages[i]
                row = history_content_box.row()
                prefix = "[用户] " if msg.is_user else "[AI] "  # <<< Changed
                icon = 'USER' if msg.is_user else ('ERROR' if '❌' in msg.text else 'LIGHT')
                display_text = msg.text.splitlines()[0]
                if len(display_text) > 80:
                    display_text = display_text[:77] + "..."
                row.label(text=prefix + display_text, icon=icon)
        else:
            history_box.label(text="暂无消息。")  # <<< Changed

        # --- Input Section ---
        input_box = layout.box()
        input_box.label(text="输入提示:", icon='CONSOLE')  # <<< Changed
        row_input = input_box.row()
        placeholder = CONFIG.get("default_prompts", {}).get("placeholder_short", "描述模型...")
        row_input.prop(ai_props, "message", text="", placeholder=placeholder)

        # --- Action Buttons ---
        button_row = layout.row(align=True)
        button_row.scale_y = 1.3
        # Send Button
        button_row.operator("ai.send_message", text="发送给AI", icon='PLAY')  # <<< Changed
        # Execute Button
        button_row.operator("ai.execute_script", text="执行上次脚本", icon='SCRIPTPLUGINS')  # <<< Changed


# --- Operators (Update Labels/Descriptions) ---


class AI_OT_initialize(bpy.types.Operator):
    bl_idname = "ai.initialize"
    bl_label = "初始化 Blender AI助手"  # <<< Changed
    bl_description = "初始化 Blender AI助手属性组"  # <<< Changed

    def execute(self, context):
        print("\n==== Initializing AI Assistant ====", flush=True)
        try:
            # Ensure PropertyGroup class is registered
            if AIAssistantProperties.__name__ not in bpy.context.window_manager.bl_rna.properties:
                if not hasattr(bpy.types, AIAssistantProperties.__name__):
                    bpy.utils.register_class(AIAssistantProperties)

            # Ensure PointerProperty exists on Scene
            if not hasattr(bpy.types.Scene, "ai_assistant"):
                bpy.types.Scene.ai_assistant = bpy.props.PointerProperty(type=AIAssistantProperties)

            # Initialize values
            ai_props = context.scene.ai_assistant
            ai_props.keep_open = True
            ai_props.use_pin = True
            ai_props.message = ""
            ai_props.messages.clear()
            ai_props.active_message_index = -1
            ai_props.mode = "AGENT"
            print("Initialized ai_assistant properties (keep_open=True, use_pin=True)", flush=True)
        except Exception as e:
            self.report({'ERROR'}, f"初始化失败: {e}")  # <<< Changed
            print(f"Error initializing AI Assistant: {traceback.format_exc()}", flush=True)
            return {'CANCELLED'}

        self.report({'INFO'}, "Blender AI助手已初始化")  # <<< Changed
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()
        return {'FINISHED'}


class AI_OT_send_message(bpy.types.Operator):
    bl_idname = "ai.send_message"
    bl_label = "发送消息"  # <<< Changed
    bl_description = "发送消息给 Blender AI助手并执行生成的代码"  # <<< Changed

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "ai_assistant")

    def execute(self, context):
        ai_props = context.scene.ai_assistant
        user_input = ai_props.message.strip()

        if not user_input:
            user_input = CONFIG.get("default_prompts", {}).get(
                "cartoon_character", "Create a simple cartoon character."
            )
            ai_props.message = user_input

        # Add user message
        user_msg = ai_props.messages.add()
        user_msg.text = user_input
        user_msg.is_user = True
        ai_props.active_message_index = len(ai_props.messages) - 1
        ai_props.message = ""  # Clear input

        # Force redraw
        for area in context.screen.areas:
            area.tag_redraw()

        # --- Gemini Integration ---
        ai_response_text = "处理中..."  # <<< Changed
        try:
            import ai_gemini_integration

            print(f"\n==== Calling Gemini: {user_input} ====", flush=True)
            success, result = ai_gemini_integration.generate_blender_code(user_input)

            if success:
                print("[Gemini] 代码生成成功。", flush=True)  # <<< Changed
                generated_code = result
                code_snippet = generated_code.strip().split('\n')
                display_code = "\n".join(code_snippet[:8]) + ("\n..." if len(code_snippet) > 8 else "")
                ai_response_text = f"✅ 代码已生成:\n```python\n{display_code}\n```\n"  # <<< Changed

                # Save code
                save_dir = ai_gemini_integration.get_code_save_directory()
                script_path = os.path.join(save_dir, SCRIPT_FILENAME)
                try:
                    os.makedirs(save_dir, exist_ok=True)
                    with open(script_path, 'w', encoding='utf-8') as f:
                        f.write(generated_code)
                    print(f"代码已保存至 {script_path}", flush=True)  # <<< Changed
                except Exception as save_e:
                    print(f"保存代码时出错: {save_e}", flush=True)  # <<< Changed
                    ai_response_text += f"\n⚠️ 保存代码时出错: {save_e}"  # <<< Changed

                # Execute code
                exec_success, exec_result = ai_gemini_integration.execute_blender_code(generated_code)
                if exec_success:
                    ai_response_text += f"\n✅ 代码执行结果: {exec_result}"  # <<< Changed
                else:
                    ai_response_text += f"\n❌ 代码执行失败: {exec_result}"  # <<< Changed
                    print(f"[Gemini] 执行错误: {exec_result}", flush=True)  # <<< Changed
            else:
                ai_response_text = f"❌ Gemini API 错误: {result}"  # <<< Changed
                print(f"[Gemini] API 错误: {result}", flush=True)  # <<< Changed

        except ImportError:
            ai_response_text = "❌ 系统错误: 无法导入 'ai_gemini_integration'."  # <<< Changed
            print(f"[Error] {ai_response_text}", flush=True)
        except Exception as e:
            ai_response_text = f"❌ 未知错误: {e}"  # <<< Changed
            print(f"[Error] {ai_response_text}\n{traceback.format_exc()}", flush=True)

        # Add AI response
        ai_msg = ai_props.messages.add()
        ai_msg.text = ai_response_text.strip()
        ai_msg.is_user = False
        ai_props.active_message_index = len(ai_props.messages) - 1

        # Ensure panel stays open
        ai_props.keep_open = True
        ai_props.use_pin = True

        # Final redraw
        for area in context.screen.areas:
            area.tag_redraw()

        self.report({'INFO'}, "AI 回应已处理。")  # <<< Changed
        return {'FINISHED'}


class AI_OT_execute_script(bpy.types.Operator):
    bl_idname = "ai.execute_script"
    bl_label = "执行上次脚本"  # <<< Changed
    bl_description = f"执行上次生成的脚本 '{SCRIPT_FILENAME}'"  # <<< Changed
    bl_options = {'REGISTER', 'UNDO'}

    _script_path = None

    @classmethod
    def poll(cls, context):
        if cls._script_path is None or not os.path.exists(cls._script_path):
            try:
                import ai_gemini_integration

                save_dir = ai_gemini_integration.get_code_save_directory()
                if not save_dir:
                    cls._script_path = ""
                    return False
                cls._script_path = os.path.join(save_dir, SCRIPT_FILENAME)
            except ImportError:
                cls._script_path = ""
                return False
            except Exception:
                cls._script_path = ""
                return False
        return os.path.exists(cls._script_path)

    def execute(self, context):
        script_path = ""
        try:
            import ai_gemini_integration

            save_dir = ai_gemini_integration.get_code_save_directory()
            if not save_dir:
                raise FileNotFoundError("代码保存目录未配置。")  # <<< Changed
            script_path = os.path.join(save_dir, SCRIPT_FILENAME)
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"脚本文件未找到: {script_path}")  # <<< Changed

            print(f"\n[Execute Script] 执行脚本: {script_path}", flush=True)  # <<< Changed
            with open(script_path, 'r', encoding='utf-8') as f:
                script_code = f.read()

            exec_success, exec_result = ai_gemini_integration.execute_blender_code(script_code)

            if exec_success:
                report_msg = f"脚本执行完毕: {exec_result}"  # <<< Changed
                self.report({'INFO'}, report_msg)
                result_msg = f"ℹ️ 已执行 '{SCRIPT_FILENAME}'. 结果: {exec_result}"  # <<< Changed
            else:
                report_msg = f"脚本执行失败: {exec_result}"  # <<< Changed
                self.report({'ERROR'}, report_msg)
                result_msg = f"❌ 执行 '{SCRIPT_FILENAME}' 失败: {exec_result}"  # <<< Changed

            # Add result to history
            if hasattr(context.scene, "ai_assistant"):
                ai_props = context.scene.ai_assistant
                msg = ai_props.messages.add()
                msg.text = result_msg
                msg.is_user = False
                ai_props.active_message_index = len(ai_props.messages) - 1

        except (ImportError, FileNotFoundError, Exception) as e:
            error_msg = f"执行错误: {e}"  # <<< Changed
            self.report({'ERROR'}, error_msg)
            print(f"[Execute Script] Error: {traceback.format_exc()}", flush=True)
            if hasattr(context.scene, "ai_assistant"):
                ai_props = context.scene.ai_assistant
                msg = ai_props.messages.add()
                msg.text = f"❌ 执行错误: {e}"  # <<< Changed
                msg.is_user = False
                ai_props.active_message_index = len(ai_props.messages) - 1
            return {'CANCELLED'}

        # Ensure panel stays open
        if hasattr(context.scene, "ai_assistant"):
            context.scene.ai_assistant.keep_open = True
            context.scene.ai_assistant.use_pin = True

        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}


class AI_OT_clear_history(bpy.types.Operator):
    bl_idname = "ai.clear_history"
    bl_label = "清除历史记录"  # <<< Changed
    bl_description = "清除 AI 消息历史记录"  # <<< Changed
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "ai_assistant") and len(context.scene.ai_assistant.messages) > 0

    def execute(self, context):
        ai_props = context.scene.ai_assistant
        count = len(ai_props.messages)
        ai_props.messages.clear()
        ai_props.active_message_index = -1
        self.report({'INFO'}, f"已清除 {count} 条消息。")  # <<< Changed
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}


class AI_OT_debug(bpy.types.Operator):
    bl_idname = "ai.debug"
    bl_label = "调试 AI助手"  # <<< Changed
    bl_description = "调试 Blender AI助手 (设置断点)"  # <<< Changed

    def execute(self, context):
        print("\n==== AI Assistant Debug Breakpoint ====", flush=True)
        # debug_ai_assistant() # Optional call to print info before break
        print("设置断点...", flush=True)  # <<< Changed
        sys.stdout.flush()
        import pdb

        pdb.set_trace()
        return {'FINISHED'}


# --- Classes List for Registration ---
classes = (
    AIMessageItem,
    AIAssistantProperties,
    AI_OT_initialize,
    AI_OT_send_message,
    AI_OT_execute_script,
    AI_OT_clear_history,
    VIEW3D_PT_ai_assistant,
    VIEW3D_PT_ai_assistant_input,  # Keep child panel for structure
    AI_OT_debug,  # Keep debug if needed
)


# --- Handler ---
@bpy.app.handlers.persistent
def force_panel_open_handler(dummy):
    if not bpy.context or not hasattr(bpy.context, 'scene') or not bpy.context.scene:
        return 1.0
    if hasattr(bpy.context.scene, "ai_assistant"):
        ai_props = bpy.context.scene.ai_assistant
        if not ai_props.keep_open:
            ai_props.keep_open = True
        if not ai_props.use_pin:
            ai_props.use_pin = True
    return None


# --- Registration ---
def register():
    print("注册 Blender AI助手...", flush=True)  # <<< Changed
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass
        except Exception as e:
            print(f"  注册 {cls.__name__} 时出错: {e}", flush=True)  # <<< Changed

    try:
        if not hasattr(bpy.types.Scene, "ai_assistant"):
            bpy.types.Scene.ai_assistant = bpy.props.PointerProperty(type=AIAssistantProperties)
            print("  已添加 'ai_assistant' 属性到场景。", flush=True)  # <<< Changed
    except Exception as e:
        print(f"  添加属性时出错: {e}", flush=True)  # <<< Changed

    if force_panel_open_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(force_panel_open_handler)
        print("  已注册 load_post 处理程序。", flush=True)  # <<< Changed

    print("Blender AI助手注册完成。", flush=True)  # <<< Changed


def unregister():
    print("注销 Blender AI助手...", flush=True)  # <<< Changed
    if force_panel_open_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(force_panel_open_handler)
        print("  已注销 load_post 处理程序。", flush=True)  # <<< Changed

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
        except Exception as e:
            print(f"  注销 {cls.__name__} 时出错: {e}", flush=True)  # <<< Changed

    try:
        if hasattr(bpy.types.Scene, "ai_assistant"):
            del bpy.types.Scene.ai_assistant
    except Exception as e:
        print(f"  移除属性时出错: {e}", flush=True)  # <<< Changed

    print("Blender AI助手注销完成。", flush=True)  # <<< Changed


# --- Main Guard ---
# if __name__ == "__main__":
#     print("请通过Blender插件系统运行注册。") # <<< Changed

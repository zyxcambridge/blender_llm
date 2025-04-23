import sys
import os
import json
import traceback
import bpy
import ai_gemini_integration

# 导入修复脚本模块
try:
    import fix_gemini_script

    has_fix_script = True
except ImportError:
    has_fix_script = False
    print("警告: 无法导入fix_gemini_script模块，修复脚本功能将不可用", flush=True)

from bpy.types import (
    Panel,
    PropertyGroup,
)
from bpy.props import (
    StringProperty,
    CollectionProperty,
    IntProperty,
    BoolProperty,
    PointerProperty,
)


def load_config():
    """从JSON配置文件加载设置"""
    config_path = ""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "ai_assistant_config.json")
    except NameError:
        print("无法确定脚本目录以查找 ai_assistant_config.json", flush=True)

    default_config = {
        "default_prompts": {
            "cartoon_character": "为一个名为「小兔子」的卡通角色创建完整3D模型...",
            "placeholder_short": "描述你想创建的模型...",
            "chat_mode": "Type a message or /subdivide, @",
        },
        "script_filename": "gemini_latest_code.py",
    }
    config = default_config.copy()

    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                for key, default_value in default_config.items():
                    if key in loaded_config:
                        if isinstance(default_value, dict) and isinstance(loaded_config[key], dict):
                            config[key].update(loaded_config[key])
                        else:
                            config[key] = loaded_config[key]
            print(f"配置已加载: {config_path}", flush=True)
        except json.JSONDecodeError as e:
            print(f"加载配置文件JSON解析错误: {e}，路径: {config_path}，使用默认配置。", flush=True)
        except Exception as e:
            print(f"加载配置文件时发生未知错误: {e}，路径: {config_path}，使用默认配置。", flush=True)
    else:
        if config_path:
            print(f"配置文件不存在: {config_path}，使用默认配置。", flush=True)
        else:
            print("未找到配置文件路径，使用默认配置。", flush=True)

    return config


CONFIG = load_config()
SCRIPT_FILENAME = CONFIG.get("script_filename", "gemini_latest_code.py")


class AIMessageItem(PropertyGroup):
    text: StringProperty(default="")
    is_user: BoolProperty(default=True)


class AIAssistantProperties(PropertyGroup):
    message: StringProperty(default="")
    messages: CollectionProperty(type=AIMessageItem)
    active_message_index: IntProperty(default=-1)
    keep_open: BoolProperty(default=True)
    use_pin: BoolProperty(default=True)
    mode: StringProperty(default="AGENT")


class VIEW3D_PT_ai_assistant(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender AI Agent"
    bl_label = "Blender AI Agent"
    bl_options = {'HIDE_HEADER', 'DEFAULT_CLOSED'}
    bl_order = 0  # 确保面板显示在最上面

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "ai_assistant")

    def draw_header(self, context):
        if hasattr(context.scene, "ai_assistant"):
            ai_props = context.scene.ai_assistant
            layout = self.layout
            # Make sure the property exists before trying to access it
            if hasattr(ai_props, "use_pin"):
                layout.prop(
                    ai_props, "use_pin", text="", icon='PINNED' if ai_props.use_pin else 'UNPINNED', emboss=False
                )
            else:
                print("Warning: 'use_pin' property not found in AIAssistantProperties", flush=True)

    def draw(self, context):
        layout = self.layout
        if not hasattr(context.scene, "ai_assistant"):
            layout.label(text="Blender AI助手尚未初始化。")
            row = layout.row()
            row.operator("ai.initialize", text="初始化 Blender AI助手", icon='FILE_REFRESH')
            return

        ai_props = context.scene.ai_assistant

        # 1. 标题区
        title_box = layout.box()
        title_row = title_box.row()
        title_row.label(text="Blender AI Agent", icon='OUTLINER_OB_ARMATURE')

        # 如果在调试模式下，显示重新初始化按钮
        if bpy.app.debug:
            debug_row = layout.row(align=True)
            debug_row.operator("ai.initialize", text="重新初始化", icon='FILE_REFRESH')

        # 2. 用户需求记录区
        history_box = layout.box()
        history_header = history_box.row(align=True)
        history_header.label(text="操作记录/信息输出区", icon='INFO')
        history_header.operator("ai.clear_history", text="", icon='TRASH', emboss=False)

        if len(ai_props.messages) > 0:
            history_content_box = history_box.box()
            max_history_display = 10
            start_idx = max(0, len(ai_props.messages) - max_history_display)
            for i in range(start_idx, len(ai_props.messages)):
                msg = ai_props.messages[i]
                row = history_content_box.row()
                prefix = "[用户] " if msg.is_user else "[AI] "
                icon = 'USER' if msg.is_user else ('ERROR' if '❌' in msg.text else 'LIGHT')
                display_text = msg.text.splitlines()[0]
                if len(display_text) > 80:
                    display_text = display_text[:77] + "..."
                row.label(text=prefix + display_text, icon=icon)
        else:
            history_box.label(text="暂无消息。")

        # 3. 用户需求输入文本区
        input_box = layout.box()
        input_box.label(text="输入提示:", icon='CONSOLE')
        row_input = input_box.row()
        placeholder = CONFIG.get("default_prompts", {}).get("placeholder_short", "描述你想创建的模型...")
        row_input.prop(ai_props, "message", text="", placeholder=placeholder)

        # 4. 按钮区 - Agent 工作流程
        button_row = layout.row(align=True)
        button_row.scale_y = 1.5  # 增大按钮高度
        button_row.operator("ai.send_message", text="Agent 建模规划", icon='OUTLINER_OB_LIGHT')

        # 修复脚本错误按钮
        if has_fix_script:
            fix_row = layout.row(align=True)
            fix_row.scale_y = 1.5  # 增大按钮高度
            fix_row.operator("script.fix_gemini_code", text="Agent 评估反思", icon='OUTLINER_OB_FORCE_FIELD')

        # 执行 Blender Python 脚本按钮
        execute_row = layout.row(align=True)
        execute_row.scale_y = 1.5  # 增大按钮高度
        execute_row.operator("ai.execute_script", text="Agent 执行", icon='OUTLINER_OB_ARMATURE')


class AI_OT_initialize(bpy.types.Operator):
    bl_idname = "ai.initialize"
    bl_label = "初始化 Blender AI助手"
    bl_description = "初始化 Blender AI助手属性组"

    def execute(self, context):
        print("\n==== Initializing AI Assistant ====", flush=True)
        try:
            if AIAssistantProperties.__name__ not in bpy.context.window_manager.bl_rna.properties:
                if not hasattr(bpy.types, AIAssistantProperties.__name__):
                    bpy.utils.register_class(AIAssistantProperties)

            if not hasattr(bpy.types.Scene, "ai_assistant"):
                bpy.types.Scene.ai_assistant = PointerProperty(type=AIAssistantProperties)

            ai_props = context.scene.ai_assistant
            ai_props.keep_open = True
            ai_props.use_pin = True
            ai_props.message = ""
            ai_props.messages.clear()
            ai_props.active_message_index = -1
            ai_props.mode = "AGENT"
            print("Initialized ai_assistant properties (keep_open=True, use_pin=True)", flush=True)
        except Exception as e:
            self.report({'ERROR'}, f"初始化失败: {e}")
            print(f"Error initializing AI Assistant: {traceback.format_exc()}", flush=True)
            return {'CANCELLED'}

        self.report({'INFO'}, "Blender AI助手已初始化")
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()
        return {'FINISHED'}


class AI_OT_send_message(bpy.types.Operator):
    bl_idname = "ai.send_message"
    bl_label = "Agent 建模规划"
    bl_description = "发送消息给 AI Agent 生成建模规划和代码（不自动执行）"

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

        user_msg = ai_props.messages.add()
        user_msg.text = user_input
        user_msg.is_user = True
        ai_props.active_message_index = len(ai_props.messages) - 1
        ai_props.message = ""

        for area in context.screen.areas:
            area.tag_redraw()

        ai_response_text = "处理中..."
        try:
            import ai_gemini_integration

            print(f"\n==== Calling Gemini: {user_input} ====", flush=True)
            success, result = ai_gemini_integration.generate_blender_code(user_input)

            if success:
                print("[Gemini] 代码生成成功。", flush=True)
                generated_code = result
                code_snippet = generated_code.strip().split('\n')
                display_code = "\n".join(code_snippet[:8]) + ("\n..." if len(code_snippet) > 8 else "")
                ai_response_text = f"✅ 代码已生成:\n```python\n{display_code}\n```\n"

                save_dir = ai_gemini_integration.get_code_save_directory()
                script_path = os.path.join(save_dir, SCRIPT_FILENAME)
                try:
                    os.makedirs(save_dir, exist_ok=True)
                    with open(script_path, 'w', encoding='utf-8') as f:
                        f.write(generated_code)
                    print(f"代码已保存至 {script_path}", flush=True)
                except Exception as save_e:
                    print(f"保存代码时出错: {save_e}", flush=True)
                    ai_response_text += f"\n⚠️ 保存代码时出错: {save_e}"

                # 不自动执行代码，只生成和保存
                ai_response_text += f"\n✅ 代码已生成并保存到 {script_path}"
                ai_response_text += "\nℹ️ 请点击'执行脚本 (类似Alt+P)'按钮执行代码"
            else:
                ai_response_text = f"❌ Gemini API 错误: {result}"
                print(f"[Gemini] API 错误: {result}", flush=True)
        except Exception as e:
            ai_response_text = f"❌ 未知错误: {e}"
            print(f"[Error] {ai_response_text}\n{traceback.format_exc()}", flush=True)

        ai_msg = ai_props.messages.add()
        ai_msg.text = ai_response_text.strip()
        ai_msg.is_user = False
        ai_props.active_message_index = len(ai_props.messages) - 1

        # 确保面板保持打开
        ai_props.keep_open = True
        ai_props.use_pin = True

        # 强制刷新所有面板
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'UI':
                            region.tag_redraw()

        for area in context.screen.areas:
            area.tag_redraw()

        self.report({'INFO'}, "AI 回应已处理。")
        return {'FINISHED'}


class AI_OT_execute_script(bpy.types.Operator):
    bl_idname = "ai.execute_script"
    bl_label = "Agent 执行"
    bl_description = f"Agent 执行生成的 Blender Python 脚本，实现建模规划"
    bl_options = {'REGISTER', 'UNDO'}

    _script_path = None

    @classmethod
    def poll(cls, context):
        # 检查是否有文本编辑器打开的脚本
        for area in context.screen.areas:
            if area.type == 'TEXT_EDITOR' and area.spaces.active.text:
                return True

        # 如果没有打开的脚本，检查是否有保存的 gemini_latest_code.py 文件
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
        script_code = ""
        script_name = ""

        try:
            import ai_gemini_integration

            # 首先检查是否有文本编辑器打开的脚本
            active_text = None
            for area in context.screen.areas:
                if area.type == 'TEXT_EDITOR' and area.spaces.active.text:
                    active_text = area.spaces.active.text
                    break

            if active_text:
                # 使用当前打开的脚本
                script_code = active_text.as_string()
                script_name = active_text.name
                print(f"\n[Execute Script] 执行文本编辑器中的脚本: {script_name}", flush=True)
            else:
                # 如果没有打开的脚本，使用保存的 gemini_latest_code.py 文件
                save_dir = ai_gemini_integration.get_code_save_directory()
                if not save_dir:
                    raise FileNotFoundError("代码保存目录未配置。")
                script_path = os.path.join(save_dir, SCRIPT_FILENAME)
                if not os.path.exists(script_path):
                    raise FileNotFoundError(f"脚本文件未找到: {script_path}")

                print(f"\n[Execute Script] 执行脚本文件: {script_path}", flush=True)
                with open(script_path, 'r', encoding='utf-8') as f:
                    script_code = f.read()
                script_name = SCRIPT_FILENAME

            # 执行脚本代码
            exec_success, exec_result = ai_gemini_integration.execute_blender_code(script_code)

            if exec_success:
                report_msg = f"脚本执行完毕: {exec_result}"
                self.report({'INFO'}, report_msg)
                result_msg = f"ℹ️ 已执行 '{script_name}'. 结果: {exec_result}"
            else:
                report_msg = f"脚本执行失败: {exec_result}"
                self.report({'ERROR'}, report_msg)
                result_msg = f"❌ 执行 '{script_name}' 失败: {exec_result}"

            if hasattr(context.scene, "ai_assistant"):
                ai_props = context.scene.ai_assistant
                msg = ai_props.messages.add()
                msg.text = result_msg
                msg.is_user = False
                ai_props.active_message_index = len(ai_props.messages) - 1

        except (ImportError, FileNotFoundError, Exception) as e:
            error_msg = f"执行错误: {e}"
            self.report({'ERROR'}, error_msg)
            print(f"[Execute Script] Error: {traceback.format_exc()}", flush=True)
            if hasattr(context.scene, "ai_assistant"):
                ai_props = context.scene.ai_assistant
                msg = ai_props.messages.add()
                msg.text = f"❌ 执行错误: {e}"
                msg.is_user = False
                ai_props.active_message_index = len(ai_props.messages) - 1
            return {'CANCELLED'}

        if hasattr(context.scene, "ai_assistant"):
            context.scene.ai_assistant.keep_open = True
            context.scene.ai_assistant.use_pin = True

            # 强制刷新所有面板
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'VIEW_3D':
                        for region in area.regions:
                            if region.type == 'UI':
                                region.tag_redraw()

        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}


class AI_OT_clear_history(bpy.types.Operator):
    bl_idname = "ai.clear_history"
    bl_label = "清除历史记录"
    bl_description = "清除 AI 消息历史记录"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "ai_assistant") and len(context.scene.ai_assistant.messages) > 0

    def execute(self, context):
        ai_props = context.scene.ai_assistant
        count = len(ai_props.messages)
        ai_props.messages.clear()
        ai_props.active_message_index = -1
        self.report({'INFO'}, f"已清除 {count} 条消息。")
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}


class AI_OT_debug(bpy.types.Operator):
    bl_idname = "ai.debug"
    bl_label = "调试 AI助手"
    bl_description = "调试 Blender AI助手 (设置断点)"

    def execute(self, context):
        print("\n==== AI Assistant Debug Breakpoint ====", flush=True)
        print("设置断点...", flush=True)
        sys.stdout.flush()
        import pdb

        pdb.set_trace()
        return {'FINISHED'}


class AI_OT_toggle_panel(bpy.types.Operator):
    bl_idname = "ai.toggle_panel"
    bl_label = "切换 AI助手面板"
    bl_description = "显示或隐藏 Blender AI助手面板"

    def execute(self, context):
        if hasattr(context.scene, "ai_assistant"):
            ai_props = context.scene.ai_assistant
            # 切换面板状态
            ai_props.keep_open = not ai_props.keep_open

            # 如果是打开面板，确保它被固定
            if ai_props.keep_open:
                ai_props.use_pin = True

                # 强制刷新所有面板
                for window in context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.type == 'VIEW_3D':
                            for region in area.regions:
                                if region.type == 'UI':
                                    region.tag_redraw()

        return {'FINISHED'}


classes = (
    AIMessageItem,
    AIAssistantProperties,
    AI_OT_initialize,
    AI_OT_send_message,
    AI_OT_execute_script,
    AI_OT_clear_history,
    VIEW3D_PT_ai_assistant,
    AI_OT_debug,
    AI_OT_toggle_panel,
)


@bpy.app.handlers.persistent
def force_panel_open_handler(dummy):
    if not bpy.context or not hasattr(bpy.context, 'scene') or not bpy.context.scene:
        return 0.1  # 更频繁地检查

    if hasattr(bpy.context.scene, "ai_assistant"):
        ai_props = bpy.context.scene.ai_assistant
        # 始终强制面板保持打开状态
        ai_props.keep_open = True
        ai_props.use_pin = True

        # 确保面板在侧边栏中可见
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    # 尝试将面板所在的区域设置为可见
                    for region in area.regions:
                        if region.type == 'UI':
                            # 确保区域可见
                            if region.alignment == 'RIGHT':
                                region.width = max(region.width, 300)  # 确保面板有足够的宽度
                            region.tag_redraw()

                    # 强制刷新区域
                    area.tag_redraw()

    # 非常频繁地运行此处理程序，确保面板始终保持打开
    return 0.05  # 更频繁地运行，每0.05秒检查一次


def register():
    print("注册 Blender AI助手...", flush=True)

    # 注册修复脚本模块
    if has_fix_script:
        try:
            fix_gemini_script.register()
            print("  已注册修复脚本模块", flush=True)
        except Exception as e:
            print(f"  注册修复脚本模块时出错: {e}", flush=True)

    # 注册其他类
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass
        except Exception as e:
            print(f"  注册 {cls.__name__} 时出错: {e}", flush=True)

    try:
        if not hasattr(bpy.types.Scene, "ai_assistant"):
            bpy.types.Scene.ai_assistant = PointerProperty(type=AIAssistantProperties)
            print("  已添加 'ai_assistant' 属性到场景。", flush=True)
    except Exception as e:
        print(f"  添加属性时出错: {e}", flush=True)

    # 添加到多个处理程序中，确保面板始终保持打开
    handlers = [
        bpy.app.handlers.load_post,
        bpy.app.handlers.depsgraph_update_post,
        bpy.app.handlers.frame_change_post,
        # 添加更多处理程序以确保面板始终可见
        bpy.app.handlers.scene_update_post if hasattr(bpy.app.handlers, 'scene_update_post') else None,
        bpy.app.handlers.undo_post,
        bpy.app.handlers.redo_post,
    ]

    for handler_list in handlers:
        if handler_list is not None and force_panel_open_handler not in handler_list:
            handler_list.append(force_panel_open_handler)
            print(f"  已注册处理程序到 {handler_list.__name__}", flush=True)

    # 添加到定时器中，确保面板始终保持打开
    if force_panel_open_handler not in bpy.app.timers.get_list():
        bpy.app.timers.register(force_panel_open_handler, first_interval=0.1, persistent=True)
        print("  已注册处理程序到定时器", flush=True)

    # 立即初始化 AI 助手
    def init_ai_assistant():
        try:
            if hasattr(bpy.context, 'scene') and bpy.context.scene:
                # 调用初始化操作符
                bpy.ops.ai.initialize()
                return None
        except Exception as e:
            print(f"  自动初始化 AI 助手时出错: {e}", flush=True)
        return 0.5  # 如果失败，稍后重试

    # 添加到定时器中，确保在启动时初始化
    bpy.app.timers.register(init_ai_assistant, first_interval=0.5)

    print("Blender AI助手注册完成。", flush=True)


def unregister():
    print("注销 Blender AI助手...", flush=True)

    # 注销修复脚本模块
    if has_fix_script:
        try:
            fix_gemini_script.unregister()
            print("  已注销修复脚本模块", flush=True)
        except Exception as e:
            print(f"  注销修复脚本模块时出错: {e}", flush=True)

    # 从所有处理程序中移除
    handlers = [
        bpy.app.handlers.load_post,
        bpy.app.handlers.depsgraph_update_post,
        bpy.app.handlers.frame_change_post,
        bpy.app.handlers.scene_update_post if hasattr(bpy.app.handlers, 'scene_update_post') else None,
        bpy.app.handlers.undo_post,
        bpy.app.handlers.redo_post,
    ]

    for handler_list in handlers:
        if handler_list is not None and force_panel_open_handler in handler_list:
            handler_list.remove(force_panel_open_handler)
            print(f"  已从 {handler_list.__name__} 移除处理程序", flush=True)

    # 从定时器中移除
    if hasattr(bpy.app.timers, "unregister"):
        try:
            bpy.app.timers.unregister(force_panel_open_handler)
            print("  已从定时器移除处理程序", flush=True)
        except ValueError:
            pass  # 如果定时器不存在，忽略错误

    # 移除定时器
    if hasattr(bpy.app.timers, "unregister"):
        for timer in bpy.app.timers.get_list():
            if timer.__name__ == "init_ai_assistant":
                bpy.app.timers.unregister(timer)
                print("  已移除 AI 助手初始化定时器", flush=True)

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
        except Exception as e:
            print(f"  注销 {cls.__name__} 时出错: {e}", flush=True)

    try:
        if hasattr(bpy.types.Scene, "ai_assistant"):
            del bpy.types.Scene.ai_assistant
    except Exception as e:
        print(f"  移除属性时出错: {e}", flush=True)

    print("Blender AI助手注销完成。", flush=True)


if __name__ == "__main__":
    print("请通过Blender插件系统运行注册。")
    register()

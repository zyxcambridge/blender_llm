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
    bl_ui_units_x = 120  # 增加宽度
    bl_ui_units_y = 80  # 增加高度

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

        # 标题和描述
        box = layout.box()
        row = box.row()
        row.label(text="AI Assistant", icon='COMMUNITY')
        row = box.row()
        row.label(text="使用AI助手生成和执行Blender Python代码")

        # Debug button (only visible in development mode)
        if bpy.app.debug:
            row = layout.row()
            row.operator("ai.debug", text="Debug", icon='CONSOLE')
            row.operator("ai.run_tests", text="运行测试", icon='SCRIPT')


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


# 修改AI_OT_set_mode操作符 - 始终设置为Agent模式
class AI_OT_set_mode(bpy.types.Operator):
    bl_idname = "ai.set_mode"
    bl_label = "Set Mode"
    bl_description = "Set the AI assistant mode"

    mode: StringProperty(name="Mode", default="AGENT")

    def execute(self, context):
        # 始终设置为Agent模式
        context.scene.ai_assistant.mode = 'AGENT'
        # 确保面板保持打开
        context.scene.ai_assistant.keep_open = True
        self.report({'INFO'}, "AI Assistant is in Agent Mode")
        return {'FINISHED'}


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

    def execute_operation(self, api_call):
        """安全执行API调用

        这个函数执行由Agent 1生成的Blender API调用
        """
        print(f"\n[执行API] 开始执行API调用: {api_call}", flush=True)

        # 使用exec而不是eval以支持多行操作
        namespace = {'bpy': bpy}
        try:
            # 执行API调用
            exec(api_call, namespace)
            print(f"[执行API] API调用执行成功", flush=True)
            return True
        except Exception as e:
            print(f"[执行API] 执行错误 ({api_call}): {str(e)}", flush=True)
            raise e

    def get_conversation_history(self):
        """获取对话历史记录，用于上下文理解

        返回一个包含所有历史消息的列表，格式为：["用户: 消息1", "AI: 回复1", ...]
        """
        context = []

        # 获取场景中的AI助手属性
        if hasattr(bpy.context.scene, "ai_assistant"):
            ai_props = bpy.context.scene.ai_assistant

            # 遍历所有历史消息
            for msg in ai_props.messages:
                prefix = "用户: " if msg.is_user else "AI: "
                context.append(prefix + msg.text)

        return context

    def is_refinement_request(self, message, context):
        """检查当前消息是否是对之前模型的细化请求

        参数:
            message: 当前用户消息
            context: 对话历史记录列表

        返回:
            is_refinement: 是否是细化请求
            previous_model: 之前创建的模型信息 (如果有)
        """
        # 如果没有历史记录，则不是细化请求
        if not context:
            return False, None

        # 检查关键词
        refinement_keywords = ["细化", "修改", "调整", "改进", "优化", "更精细", "更详细", "完善"]
        has_refinement_intent = any(keyword in message for keyword in refinement_keywords)

        # 查找之前创建的模型信息
        previous_model = None
        for msg in reversed(context):
            if "AI: " in msg and "创建" in msg:
                # 提取之前创建的模型信息
                previous_model = msg
                break

        # 如果有细化意图且有之前的模型，则认为是细化请求
        return has_refinement_intent and previous_model is not None, previous_model

    # natural_language_to_operations方法已被移除，所有用户输入现在通过Gemini API处理

    def api_to_mouse_action(self, api_call, description):
        """Agent 2: 将API调用转换为具体的鼠标点击操作

        这个函数模拟了第二个Agent的功能，将Blender API调用转换为用户界面上的鼠标操作步骤
        """
        # 这里可以集成Google的Agent或其他LLM服务来生成更精确的鼠标操作指南
        # 目前使用简化的映射作为示例
        import re

        # 基于API调用的简单映射
        if "primitive_cube_add" in api_call:
            # 解析参数
            size_match = re.search(r'size=([^,)]+)', api_call)
            location_match = re.search(r'location=\(([^)]+)\)', api_call)

            size = size_match.group(1) if size_match else "2"
            location = location_match.group(1) if location_match else "0, 0, 0"

            mouse_action = f"单击添加 > 网格 > 立方体"
            if location_match:
                mouse_action += f"，然后在位置面板中设置位置为({location})"
            if size_match and size != "2":
                mouse_action += f"，设置尺寸为{size}"

            return mouse_action

        elif "primitive_uv_sphere_add" in api_call:
            # 解析参数
            radius_match = re.search(r'radius=([^,)]+)', api_call)
            location_match = re.search(r'location=\(([^)]+)\)', api_call)

            radius = radius_match.group(1) if radius_match else "1"
            location = location_match.group(1) if location_match else "0, 0, 0"

            mouse_action = f"单击添加 > 网格 > 球体"
            if location_match:
                mouse_action += f"，然后在位置面板中设置位置为({location})"
            if radius_match and radius != "1":
                mouse_action += f"，设置半径为{radius}"

            return mouse_action

        elif "primitive_cylinder_add" in api_call:
            # 解析参数
            radius_match = re.search(r'radius=([^,)]+)', api_call)
            depth_match = re.search(r'depth=([^,)]+)', api_call)
            location_match = re.search(r'location=\(([^)]+)\)', api_call)
            vertices_match = re.search(r'vertices=([^,)]+)', api_call)
            rotation_match = re.search(r'rotation=\(([^)]+)\)', api_call)

            radius = radius_match.group(1) if radius_match else "1"
            depth = depth_match.group(1) if depth_match else "2"
            location = location_match.group(1) if location_match else "0, 0, 0"
            vertices = vertices_match.group(1) if vertices_match else "32"
            rotation = rotation_match.group(1) if rotation_match else "0, 0, 0"

            mouse_action = f"单击添加 > 网格 > 圆柱体"
            if location_match:
                mouse_action += f"，然后在位置面板中设置位置为({location})"
            if radius_match and radius != "1":
                mouse_action += f"，设置半径为{radius}"
            if depth_match and depth != "2":
                mouse_action += f"，设置深度为{depth}"
            if vertices_match and vertices != "32":
                mouse_action += f"，设置顶点数为{vertices}"
            if rotation_match and rotation != "0, 0, 0":
                mouse_action += f"，设置旋转为({rotation})"

            return mouse_action

        elif "object.light_add" in api_call:
            # 解析参数
            type_match = re.search(r'type=\'([^\']+)\'', api_call)
            radius_match = re.search(r'radius=([^,)]+)', api_call)
            location_match = re.search(r'location=\(([^)]+)\)', api_call)

            light_type = type_match.group(1) if type_match else "POINT"
            radius = radius_match.group(1) if radius_match else "1"
            location = location_match.group(1) if location_match else "0, 0, 0"

            light_type_map = {"POINT": "点光源", "SUN": "太阳光", "SPOT": "聚光灯", "AREA": "区域光"}

            light_type_zh = light_type_map.get(light_type, light_type)

            mouse_action = f"单击添加 > 光源 > {light_type_zh}"
            if location_match:
                mouse_action += f"，然后在位置面板中设置位置为({location})"
            if radius_match and radius != "1":
                mouse_action += f"，设置半径为{radius}"

            return mouse_action

        elif "object.delete" in api_call:
            return "选择物体 > 按Delete键 > 确认删除"

        elif "transform.rotate" in api_call:
            # 解析旋转轴和角度
            value_match = re.search(r'value=([^,]+)', api_call)
            axis_match = re.search(r'orient_axis=\'([^\']+)\'', api_call)

            value = value_match.group(1) if value_match else "1.5708"
            axis = axis_match.group(1) if axis_match else "Z"

            # 将弧度转换为角度（大致）
            try:
                angle = round(float(value) * 180 / 3.14159)
            except:
                angle = 90

            return f"选择物体 > 按R键 > {axis}键 > 输入{angle} > 回车"

        elif "transform.resize" in api_call:
            # 解析缩放值
            value_match = re.search(r'value=\(([^)]+)\)', api_call)

            if value_match:
                values = value_match.group(1).split(',')
                if len(values) > 0:
                    scale = values[0].strip()
                    return f"选择物体 > 按S键 > 输入{scale} > 回车"

            return "选择物体 > 按S键 > 输入2 > 回车"

        elif "object.mode_set" in api_call and "EDIT" in api_call:
            return "选择物体 > Tab键"

        elif "object.select_pattern" in api_call:
            # 解析选择模式
            pattern_match = re.search(r'pattern=\'([^\']+)\'', api_call)
            pattern = pattern_match.group(1) if pattern_match else "物体"

            return f"在大纲视图中找到并选择{pattern}"

        elif "object.modifier_add" in api_call:
            # 解析修改器类型
            type_match = re.search(r'type=\'([^\']+)\'', api_call)
            mod_type = type_match.group(1) if type_match else "SUBSURF"

            modifier_type_map = {
                "SUBSURF": "细分曲面",
                "BEVEL": "倒角",
                "MIRROR": "镜像",
                "SOLIDIFY": "实体化",
                "ARRAY": "阵列",
            }

            mod_type_zh = modifier_type_map.get(mod_type, mod_type)

            return f"选择物体 > 右键 > 添加修改器 > {mod_type_zh}"

        elif "object.select_all" in api_call and "SELECT" in api_call:
            return "按A键全选所有物体"

        elif "object.material_slot_add" in api_call:
            # 检查是否有材质颜色设置
            color_match = re.search(r'diffuse_color\s*=\s*\(([^)]+)\)', api_call)

            mouse_action = "材质属性面板 > 点击新建按钮"
            if color_match:
                color = color_match.group(1)
                mouse_action += f" > 设置漫反射颜色为({color})"

            return mouse_action

        # 默认情况
        return f"执行操作: {description}"


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
            # 在VIEW3D_PT_ai_assistant_input类的draw方法中，修改操作记录/信息输出区部分

            # 操作记录/信息输出区
            log_box = layout.box()
            log_title = log_box.row()
            log_title.scale_y = 1.2
            log_title.label(text="🔸 操作记录 / 信息输出区", icon='TEXT')

            # 添加刷新按钮
            refresh_btn = log_title.operator("ai.refresh_history", text="", icon='FILE_REFRESH')

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
            send_col.scale_x = 1.0  # 增加宽度确保按钮完全显示
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
            # 从配置文件读取聊天模式占位符文本
            chat_placeholder = CONFIG.get("default_prompts", {}).get("chat_mode", "Type a message or /subdivide, @")
            input_col.prop(ai_props, "message", text="", placeholder=chat_placeholder)

            # 发送按钮
            send_col = input_row.column()
            send_col.scale_x = 0.8  # 增加宽度确保按钮完全显示
            send_col.scale_y = 3.0  # 增加高度与输入框一致
            send_col.operator("ai.send_message", text="发送", icon='PLAY')


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


# 添加刷新历史记录的操作符
class AI_OT_refresh_history(bpy.types.Operator):
    bl_idname = "ai.refresh_history"
    bl_label = "刷新历史"
    bl_description = "刷新AI助手对话历史记录"

    def execute(self, context):
        if not hasattr(context.scene, "ai_assistant"):
            self.report({'ERROR'}, "AI助手尚未初始化。请重启Blender。")
            return {'CANCELLED'}

        # 强制刷新UI
        for area in context.screen.areas:
            area.tag_redraw()

        self.report({'INFO'}, "已刷新对话历史")
        return {'FINISHED'}


# 添加重新加载配置文件的操作符
class AI_OT_reload_config(bpy.types.Operator):
    bl_idname = "ai.reload_config"
    bl_label = "重新加载配置"
    bl_description = "重新加载配置文件"

    def execute(self, context):
        global CONFIG
        # 重新加载配置文件
        CONFIG = load_config()

        # 强制刷新UI
        for area in context.screen.areas:
            area.tag_redraw()

        self.report({'INFO'}, "已重新加载配置文件")
        return {'FINISHED'}


# 保持其他代码不变
class VIEW3D_PT_ai_assistant_input(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_label = "AI Assistant"
    bl_parent_id = "VIEW3D_PT_ai_assistant"
    bl_options = {'INSTANCED'}
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

        ai_props = context.scene.ai_assistant

        # 移除顶部标题栏

        # 移除设置区

        # 始终显示Agent模式界面
        # 在VIEW3D_PT_ai_assistant_input类的draw方法中，修改操作记录/信息输出区部分

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

        # 已移除 3D Moder 模式界面


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
    bl_ui_units_x = 120  # 增加宽度
    bl_ui_units_y = 80  # 增加高度

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


# 添加设置代码保存目录的操作符
class AI_OT_set_code_save_dir(bpy.types.Operator):
    bl_idname = "ai.set_code_save_dir"
    bl_label = "设置代码保存目录"
    bl_description = "设置生成的Python代码保存目录"
    bl_options = {'REGISTER'}

    directory: bpy.props.StringProperty(
        name="目录", description="选择保存生成代码的目录", subtype='DIR_PATH', default=""
    )

    def execute(self, context):
        try:
            import ai_gemini_integration

            success = ai_gemini_integration.set_code_save_directory(self.directory)
            if success:
                self.report({'INFO'}, f"代码保存目录已设置为: {self.directory if self.directory else '当前工作目录'}")
            else:
                self.report({'ERROR'}, "设置代码保存目录失败")
        except ImportError:
            self.report({'ERROR'}, "无法导入ai_gemini_integration模块")
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# 添加显示当前代码保存目录的操作符
class AI_OT_show_code_save_dir(bpy.types.Operator):
    bl_idname = "ai.show_code_save_dir"
    bl_label = "显示代码保存目录"
    bl_description = "显示当前生成的Python代码保存目录"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            import ai_gemini_integration

            directory = ai_gemini_integration.get_code_save_directory()
            if directory:
                self.report({'INFO'}, f"当前代码保存目录: {directory}")
            else:
                self.report({'INFO'}, "当前代码保存目录: 当前工作目录")
        except ImportError:
            self.report({'ERROR'}, "无法导入ai_gemini_integration模块")
            return {'CANCELLED'}
        return {'FINISHED'}


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
    AI_UL_messages,
    VIEW3D_PT_ai_assistant,
    VIEW3D_PT_ai_assistant_input,
    AI_OT_set_mode,
    AI_OT_send_message,
    AI_OT_clear_history,
    AI_OT_initialize,
    AI_OT_debug,
    AI_OT_toggle_panel,  # 添加切换AI Assistant面板显示的操作符
    AI_OT_execute_script,  # 添加执行Blender Python脚本的操作符
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

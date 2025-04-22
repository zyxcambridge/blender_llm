import unittest
import bpy
import sys
import os

# 添加当前目录到Python路径，以便导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入需要测试的模块
import space_ai_sidebar

class TestAIAssistant(unittest.TestCase):
    """测试AI Assistant功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 确保AI Assistant已初始化
        if not hasattr(bpy.context.scene, "ai_assistant"):
            # 注册属性组
            bpy.utils.register_class(space_ai_sidebar.AIAssistantProperties)
            bpy.types.Scene.ai_assistant = bpy.props.PointerProperty(type=space_ai_sidebar.AIAssistantProperties)
        
        # 初始状态：面板关闭
        bpy.context.scene.ai_assistant.keep_open = False
    
    def tearDown(self):
        """测试后的清理工作"""
        # 恢复初始状态
        if hasattr(bpy.context.scene, "ai_assistant"):
            bpy.context.scene.ai_assistant.keep_open = False
    
    def test_toggle_panel(self):
        """测试切换面板显示状态"""
        # 初始状态：面板关闭
        self.assertFalse(bpy.context.scene.ai_assistant.keep_open)
        
        # 模拟点击AI Assistant按钮
        bpy.ops.ai.toggle_panel()
        
        # 验证面板已打开
        self.assertTrue(bpy.context.scene.ai_assistant.keep_open)
        
        # 再次模拟点击AI Assistant按钮
        bpy.ops.ai.toggle_panel()
        
        # 验证面板已关闭
        self.assertFalse(bpy.context.scene.ai_assistant.keep_open)
    
    def test_send_message_keeps_panel_open(self):
        """测试发送消息后面板保持打开"""
        # 初始状态：面板关闭
        self.assertFalse(bpy.context.scene.ai_assistant.keep_open)
        
        # 模拟点击AI Assistant按钮
        bpy.ops.ai.toggle_panel()
        
        # 验证面板已打开
        self.assertTrue(bpy.context.scene.ai_assistant.keep_open)
        
        # 设置消息
        bpy.context.scene.ai_assistant.message = "测试消息"
        
        # 模拟发送消息
        bpy.ops.ai.send_message()
        
        # 验证面板仍然保持打开
        self.assertTrue(bpy.context.scene.ai_assistant.keep_open)
        
        # 验证可以连续发送多条消息
        bpy.context.scene.ai_assistant.message = "第二条测试消息"
        bpy.ops.ai.send_message()
        
        # 验证面板仍然保持打开
        self.assertTrue(bpy.context.scene.ai_assistant.keep_open)
        
        # 验证只有再次点击AI Assistant按钮才会关闭面板
        bpy.ops.ai.toggle_panel()
        
        # 验证面板已关闭
        self.assertFalse(bpy.context.scene.ai_assistant.keep_open)

def run_tests():
    """运行单元测试"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAIAssistant)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    run_tests()

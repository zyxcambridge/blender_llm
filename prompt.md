点击Blender AI助手3D Moder Copilot主面板后，发送按钮 左边的默认的输入内容，为： 设计一个鼻炎吸鼻器：

三部分组成，一个盒子是洗鼻器的主体，包含电机等，

可拆卸的部分1，能加入0.9%的生理盐水胶囊，想转子弹一样装上；

可拆卸的部分2 ，带走废液，倒掉；像卸载子弹一样卸载；
：




点击 发送后 将自然语言指令转化为Blender可执行的鼠标点击操作，并且鼠标点击操作变成API函数调用。
把点击操作和 ，API 调用的函数，输出到log中，print出来


log 打印出来了，但是没有 实现类似人的鼠标点击，在blender的主界面用户视角没有显示出来，我需要的3d模型：


点击Blender AI助手3D Moder Copilot主面板后  变成连续对话模式，先查看一下 操作记录/信息输出区 是在哪里实现的； 上一次的输入的命令 显示在操作记录/信息输出区，并且能保留下来，并且能进行刷新；



点击Blender AI助手3D Moder Copilot主面板后 ，让它一直显示在哪里


阶段 1：规则映射（1 个月）：
实现简单的指令到脚本映射，例如：• 指令“创建一个立方体” → bpy.ops.mesh.primitive_cube_add()。
• 使用 Python 字典或简单脚本存储映射关系。

• 阶段 2：引入 AI（2 个月）：
• 使用现有 LLM（如 GPT-4 或开源模型 Llama）通过 API 生成 Blender 脚本，参考 Blender Tutorial with ChatGPT.
• 如果资源允许，fine-tune 小型模型（如基于 BlendNet 数据集 (Hugging Face BlendNet)).

• 阶段 3：反馈机制（1-2 个月）：
• 软件错误反馈：检测脚本语法或运行时错误，优化生成（如 BlenderLLM 的错误率仅 3.4%）。
• 结构力学反馈：集成 Blender 的有限元分析插件（如 BlenderFEA）或外部工具（如 PyNite）验证模型物理正确性。

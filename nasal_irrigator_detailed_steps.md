# 鼻炎吸鼻器3D模型设计详细操作步骤

## 一、Blender界面操作与API调用对照表

以下是设计鼻炎吸鼻器时，Blender界面操作与对应的Python API调用的详细步骤：

### 第一部分：主体盒子设计

| 步骤 | 界面操作 | API调用 | 说明 |
|------|---------|---------|------|
| 1 | 点击「添加」菜单 → 「网格」→ 「立方体」 | `bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))` | 创建主体盒子的基础形状 |
| 2 | 在「物体属性」面板中修改名称为「主体盒子」 | `bpy.context.object.name = "主体盒子"` | 命名对象 |
| 3 | 在「物体属性」面板中修改缩放值为X:2, Y:1, Z:0.8 | `bpy.context.object.scale = (2, 1, 0.8)` | 调整主体盒子的尺寸 |
| 4 | 按Tab键进入编辑模式 | `bpy.ops.object.editmode_toggle()` | 进入编辑模式进行细节调整 |
| 5 | 按A键取消全选 | `bpy.ops.mesh.select_all(action='DESELECT')` | 取消选择所有顶点/边/面 |
| 6 | 点击「选择」菜单 → 「选择模式」→ 「面」 | `bpy.ops.mesh.select_mode(type='FACE')` | 切换到面选择模式 |
| 7 | 选择顶部面 | `bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')` | 选择四边形面（顶部面） |
| 8 | 按G键，然后按Z键，移动0.2单位 | `bpy.ops.transform.translate(value=(0, 0, 0.2))` | 向上移动顶部面 |
| 9 | 按E键挤出，然后按Z键，移动0.3单位 | `bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate=(0, 0, 0.3))` | 挤出顶部面创建电机舱空间 |
| 10 | 按A键取消全选 | `bpy.ops.mesh.select_all(action='DESELECT')` | 取消选择 |
| 11 | 选择右侧面 | `bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')` | 选择四边形面（右侧面） |
| 12 | 按I键内插，设置厚度为0.1 | `bpy.ops.mesh.inset(thickness=0.1, depth=0)` | 在侧面创建内插区域 |
| 13 | 按E键挤出，然后按X键，移动0.2单位 | `bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate=(0.2, 0, 0))` | 挤出右侧面创建插槽 |
| 14 | 按A键取消全选 | `bpy.ops.mesh.select_all(action='DESELECT')` | 取消选择 |
| 15 | 选择左侧面 | `bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')` | 选择四边形面（左侧面） |
| 16 | 按I键内插，设置厚度为0.1 | `bpy.ops.mesh.inset(thickness=0.1, depth=0)` | 在侧面创建内插区域 |
| 17 | 按E键挤出，然后按X键，移动-0.2单位 | `bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate=(-0.2, 0, 0))` | 挤出左侧面创建插槽 |
| 18 | 按Tab键退出编辑模式 | `bpy.ops.object.editmode_toggle()` | 退出编辑模式 |
| 19 | 点击「修改器属性」面板 → 「添加修改器」→ 「倒角」 | `bpy.ops.object.modifier_add(type='BEVEL')` | 添加倒角修改器 |
| 20 | 设置倒角宽度为0.02，段数为3 | `bpy.context.object.modifiers["Bevel"].width = 0.02`<br>`bpy.context.object.modifiers["Bevel"].segments = 3` | 调整倒角参数 |
| 21 | 点击「应用」按钮 | `bpy.ops.object.modifier_apply(modifier="Bevel")` | 应用倒角修改器 |

### 第二部分：生理盐水胶囊仓设计

| 步骤 | 界面操作 | API调用 | 说明 |
|------|---------|---------|------|
| 22 | 点击「添加」菜单 → 「网格」→ 「圆柱体」 | `bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.2, enter_editmode=False, align='WORLD', location=(2.5, 0, 0))` | 创建胶囊形状的盐水仓 |
| 23 | 在「物体属性」面板中修改名称为「盐水胶囊仓」 | `bpy.context.object.name = "盐水胶囊仓"` | 命名对象 |
| 24 | 点击「添加」菜单 → 「网格」→ 「UV球体」 | `bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, enter_editmode=False, align='WORLD', location=(2.5, 0, 0.6))` | 添加半球形端部 |
| 25 | 在「物体属性」面板中修改名称为「胶囊顶部」 | `bpy.context.object.name = "胶囊顶部"` | 命名对象 |
| 26 | 按A键取消全选，然后选择「盐水胶囊仓」 | `bpy.ops.object.select_all(action='DESELECT')`<br>`bpy.data.objects["盐水胶囊仓"].select_set(True)`<br>`bpy.context.view_layer.objects.active = bpy.data.objects["盐水胶囊仓"]` | 选择盐水胶囊仓对象 |
| 27 | 点击「修改器属性」面板 → 「添加修改器」→ 「布尔」 | `bpy.ops.object.modifier_add(type='BOOLEAN')` | 添加布尔修改器 |
| 28 | 设置操作为「联集」，对象为「胶囊顶部」 | `bpy.context.object.modifiers["Boolean"].operation = 'UNION'`<br>`bpy.context.object.modifiers["Boolean"].object = bpy.data.objects["胶囊顶部"]` | 设置布尔修改器参数 |
| 29 | 点击「应用」按钮 | `bpy.ops.object.modifier_apply(modifier="Boolean")` | 应用布尔修改器 |
| 30 | 删除「胶囊顶部」对象 | `bpy.data.objects.remove(bpy.data.objects["胶囊顶部"], do_unlink=True)` | 删除不需要的半球对象 |
| 31 | 点击「添加」菜单 → 「网格」→ 「圆柱体」 | `bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.1, enter_editmode=False, align='WORLD', location=(2.5, 0, -0.65))` | 创建连接机制 |
| 32 | 在「物体属性」面板中修改名称为「连接部件」 | `bpy.context.object.name = "连接部件"` | 命名对象 |
| 33 | 按A键取消全选，然后选择「盐水胶囊仓」 | `bpy.ops.object.select_all(action='DESELECT')`<br>`bpy.data.objects["盐水胶囊仓"].select_set(True)`<br>`bpy.context.view_layer.objects.active = bpy.data.objects["盐水胶囊仓"]` | 选择盐水胶囊仓对象 |
| 34 | 点击「修改器属性」面板 → 「添加修改器」→ 「布尔」 | `bpy.ops.object.modifier_add(type='BOOLEAN')` | 添加布尔修改器 |
| 35 | 设置操作为「联集」，对象为「连接部件」 | `bpy.context.object.modifiers["Boolean"].operation = 'UNION'`<br>`bpy.context.object.modifiers["Boolean"].object = bpy.data.objects["连接部件"]` | 设置布尔修改器参数 |
| 36 | 点击「应用」按钮 | `bpy.ops.object.modifier_apply(modifier="Boolean")` | 应用布尔修改器 |
| 37 | 删除「连接部件」对象 | `bpy.data.objects.remove(bpy.data.objects["连接部件"], do_unlink=True)` | 删除不需要的连接部件对象 |

### 第三部分：废液收集仓设计

| 步骤 | 界面操作 | API调用 | 说明 |
|------|---------|---------|------|
| 38 | 点击「添加」菜单 → 「网格」→ 「圆柱体」 | `bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.8, enter_editmode=False, align='WORLD', location=(-2.5, 0, 0))` | 创建废液收集仓主体 |
| 39 | 在「物体属性」面板中修改名称为「废液收集仓」 | `bpy.context.object.name = "废液收集仓"` | 命名对象 |
| 40 | 按Tab键进入编辑模式 | `bpy.ops.object.editmode_toggle()` | 进入编辑模式 |
| 41 | 按A键取消全选 | `bpy.ops.mesh.select_all(action='DESELECT')` | 取消选择所有顶点/边/面 |
| 42 | 点击「选择」菜单 → 「选择模式」→ 「面」 | `bpy.ops.mesh.select_mode(type='FACE')` | 切换到面选择模式 |
| 43 | 选择顶面 | `bpy.ops.mesh.select_face_by_sides(number=32, type='EQUAL')` | 选择顶面（32边形） |
| 44 | 按I键内插，设置厚度为0.05 | `bpy.ops.mesh.inset(thickness=0.05, depth=0)` | 在顶面创建内插区域 |
| 45 | 按E键挤出，然后按Z键，移动-0.7单位 | `bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate=(0, 0, -0.7))` | 向内挤出顶面 |
| 46 | 按X键删除选中的面 | `bpy.ops.mesh.delete(type='FACE')` | 删除内部面，形成空心 |
| 47 | 按Tab键退出编辑模式 | `bpy.ops.object.editmode_toggle()` | 退出编辑模式 |
| 48 | 点击「添加」菜单 → 「网格」→ 「圆柱体」 | `bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.1, enter_editmode=False, align='WORLD', location=(-2.5, 0, 0.45))` | 创建连接机制 |
| 49 | 在「物体属性」面板中修改名称为「废液仓连接部件」 | `bpy.context.object.name = "废液仓连接部件"` | 命名对象 |
| 50 | 按A键取消全选，然后选择「废液收集仓」 | `bpy.ops.object.select_all(action='DESELECT')`<br>`bpy.data.objects["废液收集仓"].select_set(True)`<br>`bpy.context.view_layer.objects.active = bpy.data.objects["废液收集仓"]` | 选择废液收集仓对象 |
| 51 | 点击「修改器属性」面板 → 「添加修改器」→ 「布尔」 | `bpy.ops.object.modifier_add(type='BOOLEAN')` | 添加布尔修改器 |
| 52 | 设置操作为「联集」，对象为「废液仓连接部件」 | `bpy.context.object.modifiers["Boolean"].operation = 'UNION'`<br>`bpy.context.object.modifiers["Boolean"].object = bpy.data.objects["废液仓连接部件"]` | 设置布尔修改器参数 |
| 53 | 点击「应用」按钮 | `bpy.ops.object.modifier_apply(modifier="Boolean")` | 应用布尔修改器 |
| 54 | 删除「废液仓连接部件」对象 | `bpy.data.objects.remove(bpy.data.objects["废液仓连接部件"], do_unlink=True)` | 删除不需要的连接部件对象 |

### 第四部分：组装模型

| 步骤 | 界面操作 | API调用 | 说明 |
|------|---------|---------|------|
| 55 | 选择「盐水胶囊仓」对象 | `bpy.data.objects["盐水胶囊仓"].select_set(True)`<br>`bpy.context.view_layer.objects.active = bpy.data.objects["盐水胶囊仓"]` | 选择盐水胶囊仓对象 |
| 56 | 在「物体属性」面板中修改位置为X:1.2, Y:0, Z:0 | `bpy.context.object.location = (1.2, 0, 0)` | 调整盐水胶囊仓位置 |
| 57 | 在「物体属性」面板中修改旋转为X:0, Y:1.5708, Z:0 | `bpy.context.object.rotation_euler = (0, 1.5708, 0)` | 旋转盐水胶囊仓（90度） |
| 58 | 按A键取消全选，然后选择「废液收集仓」 | `bpy.ops.object.select_all(action='DESELECT')`<br>`bpy.data.objects["废液收集仓"].select_set(True)`<br>`bpy.context.view_layer.objects.active = bpy.data.objects["废液收集仓"]` | 选择废液收集仓对象 |
| 59 | 在「物体属性」面板中修改位置为X:-1.2, Y:0, Z:0 | `bpy.context.object.location = (-1.2, 0, 0)` | 调整废液收集仓位置 |
| 60 | 在「物体属性」面板中修改旋转为X:0, Y:1.5708, Z:0 | `bpy.context.object.rotation_euler = (0, 1.5708, 0)` | 旋转废液收集仓（90度） |

### 第五部分：添加材质和细节

| 步骤 | 界面操作 | API调用 | 说明 |
|------|---------|---------|------|
| 61 | 按A键取消全选，然后选择「主体盒子」 | `bpy.ops.object.select_all(action='DESELECT')`<br>`bpy.data.objects["主体盒子"].select_set(True)`<br>`bpy.context.view_layer.objects.active = bpy.data.objects["主体盒子"]` | 选择主体盒子对象 |
| 62 | 点击「材质属性」面板 → 「新建」按钮 | `bpy.ops.material.new()` | 创建新材质 |
| 63 | 修改材质名称为「主体材质」 | `bpy.context.object.active_material.name = "主体材质"` | 命名材质 |
| 64 | 设置漫反射颜色为蓝色 | `bpy.context.object.active_material.diffuse_color = (0.2, 0.5, 0.8, 1.0)` | 设置材质颜色 |
| 65 | 按A键取消全选，然后选择「盐水胶囊仓」 | `bpy.ops.object.select_all(action='DESELECT')`<br>`bpy.data.objects["盐水胶囊仓"].select_set(True)`<br>`bpy.context.view_layer.objects.active = bpy.data.objects["盐水胶囊仓"]` | 选择盐水胶囊仓对象 |
| 66 | 点击「材质属性」面板 → 「新建」按钮 | `bpy.ops.material.new()` | 创建新材质 |
| 67 | 修改材质名称为「胶囊材质」 | `bpy.context.object.active_material.name = "胶囊材质"` | 命名材质 |
| 68 | 设置漫反射颜色为半透明白色 | `bpy.context.object.active_material.diffuse_color = (0.9, 0.9, 0.9, 0.8)` | 设置材质颜色和透明度 |
| 69 | 按A键取消全选，然后选择「废液收集仓」 | `bpy.ops.object.select_all(action='DESELECT')`<br>`bpy.data.objects["废液收集仓"].select_set(True)`<br>`bpy.context.view_layer.objects.active = bpy.data.objects["废液收集仓"]` | 选择废液收集仓对象 |
| 70 | 点击「材质属性」面板 → 「新建」按钮 | `bpy.ops.material.new()` | 创建新材质 |
| 71 | 修改材质名称为「废液仓材质」 | `bpy.context.object.active_material.name = "废液仓材质"` | 命名材质 |
| 72 | 设置漫反射颜色为半透明红色 | `bpy.context.object.active_material.diffuse_color = (0.8, 0.3, 0.3, 0.7)` | 设置材质颜色和透明度 |

## 二、使用AI Agent思想完成产品设计和建模

使用AI Agent思想（记忆、规划、行动、调用工具）来完成鼻炎吸鼻器的设计和建模，可以按照以下方法进行：

### 1. 记忆（Memory）模块实现

记忆模块负责存储和管理设计过程中的各种信息：

```python
# 记忆模块实现代码
class DesignMemory:
    def __init__(self):
        # 存储产品需求
        self.requirements = {
            "main_body": "包含电机的主体盒子",
            "part1": "可拆卸的生理盐水胶囊仓，像子弹一样装卸",
            "part2": "可拆卸的废液收集仓，像卸载子弹一样卸载"
        }
        
        # 存储参考设计
        self.references = []
        
        # 存储设计历史和决策
        self.design_history = []
        
        # 存储当前设计状态
        self.current_state = {
            "main_body": None,
            "part1": None,
            "part2": None,
            "assembly": False
        }
    
    def add_reference(self, reference_path, description):
        """添加参考设计"""
        self.references.append({
            "path": reference_path,
            "description": description
        })
    
    def log_decision(self, step, decision, reason):
        """记录设计决策"""
        self.design_history.append({
            "step": step,
            "decision": decision,
            "reason": reason,
            "timestamp": time.time()
        })
    
    def update_state(self, component, object_reference):
        """更新当前设计状态"""
        self.current_state[component] = object_reference
    
    def get_design_history(self):
        """获取设计历史"""
        return self.design_history
    
    def get_current_state(self):
        """获取当前设计状态"""
        return self.current_state
```

### 2. 规划（Planning）模块实现

规划模块负责将设计任务分解为可执行的步骤：

```python
# 规划模块实现代码
class DesignPlanner:
    def __init__(self, memory):
        self.memory = memory
        self.plan = []
        self.dependencies = {}
    
    def create_plan(self):
        """创建设计计划"""
        # 主体盒子设计步骤
        main_body_steps = [
            {"id": "mb1", "step": "创建主体盒子", "api": "bpy.ops.mesh.primitive_cube_add", "params": {"size": 1, "location": (0, 0, 0)}},
            {"id": "mb2", "step": "调整主体盒子尺寸", "api": "bpy.context.object.scale", "params": {"scale": (2, 1, 0.8)}},
            {"id": "mb3", "step": "进入编辑模式", "api": "bpy.ops.object.editmode_toggle", "params": {}},
            {"id": "mb4", "step": "创建电机舱空间", "api": "多步骤操作", "params": {}},
            {"id": "mb5", "step": "创建插槽", "api": "多步骤操作", "params": {}},
            {"id": "mb6", "step": "添加倒角", "api": "bpy.ops.object.modifier_add", "params": {"type": "BEVEL"}}
        ]
        
        # 盐水胶囊仓设计步骤
        capsule_steps = [
            {"id": "cp1", "step": "创建胶囊主体", "api": "bpy.ops.mesh.primitive_cylinder_add", "params": {"radius": 0.3, "depth": 1.2}},
            {"id": "cp2", "step": "添加半球顶部", "api": "bpy.ops.mesh.primitive_uv_sphere_add", "params": {"radius": 0.3}},
            {"id": "cp3", "step": "合并主体和顶部", "api": "布尔运算", "params": {"operation": "UNION"}},
            {"id": "cp4", "step": "添加连接机制", "api": "多步骤操作", "params": {}}
        ]
        
        # 废液收集仓设计步骤
        waste_steps = [
            {"id": "ws1", "step": "创建收集仓主体", "api": "bpy.ops.mesh.primitive_cylinder_add", "params": {"radius": 0.35, "depth": 0.8}},
            {"id": "ws2", "step": "挖空内部", "api": "编辑模式操作", "params": {}},
            {"id": "ws3", "step": "添加连接机制", "api": "多步骤操作", "params": {}}
        ]
        
        # 组装和材质步骤
        assembly_steps = [
            {"id": "as1", "step": "定位盐水胶囊仓", "api": "位置和旋转调整", "params": {}},
            {"id": "as2", "step": "定位废液收集仓", "api": "位置和旋转调整", "params": {}},
            {"id": "as3", "step": "添加材质", "api": "bpy.ops.material.new", "params": {}}
        ]
        
        # 合并所有步骤
        self.plan = main_body_steps + capsule_steps + waste_steps + assembly_steps
        
        # 设置依赖关系
        self.dependencies = {
            "mb2": ["mb1"],  # 调整尺寸依赖于创建主体
            "mb3": ["mb2"],  # 编辑模式依赖于调整尺寸
            "mb4": ["mb3"],  # 创建空间依赖于编辑模式
            "mb5": ["mb4"],  # 创建插槽依赖于创建空间
            "mb6": ["mb5"],  # 添加倒角依赖于创建插槽
            "cp3": ["cp1", "cp2"],  # 合并依赖于创建主体和顶部
            "cp4": ["cp3"],  # 连接机制依赖于合并
            "ws2": ["ws1"],  # 挖空依赖于创建主体
            "ws3": ["ws2"],  # 连接机制依赖于挖空
            "as1": ["cp4", "mb6"],  # 定位依赖于完成各部分
            "as2": ["ws3", "mb6"],  # 定位依赖于完成各部分
            "as3": ["as1", "as2"]   # 材质依赖于定位
        }
        
        return self.plan
    
    def get_next_executable_steps(self, completed_steps):
        """获取下一个可执行的步骤"""
        executable_steps = []
        
        for step in self.plan:
            # 如果步骤已完成，跳过
            if step["id"] in completed_steps:
                continue
                
            # 检查依赖是否
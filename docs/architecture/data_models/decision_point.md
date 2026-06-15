# 决策点数据模型设计

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-18（知识编译与决策索引系统）

---

## 1. 设计目标

定义决策点（Decision Point）的标准数据结构，支持：
- 决策点不可变特性
- 全局决策索引结构
- context_injection_summary 格式
- 不可变原则执行机制

---

## 2. 决策点（Decision Point）结构

### 2.1 完整字段定义

```yaml
decision_point:
  # ========== 基础标识 ==========
  dp_id: "DP-S1-03"                        # 全局唯一：DP-{scene_abbr}-{3位序号}
  task_id: "task_course_plan_2026_06_12_001"
  scene_type: "course_planning"            # 场景类型
  stage: "stage1_objectives"               # 所属阶段
  
  # ========== 决策内容 ==========
  category: "teaching_method"              # 决策类别
  content: "教学方法采用讲授法 + 探究法 + 项目引领"
  
  # ========== 来源追溯 ==========
  source_reference: "kn_stage1.yaml: teaching_methods[1].name"
  source_line: 156
  source_field: "teaching_methods[1].name"
  
  # ========== 确认信息 ==========
  confirmed_by: "teacher_001"             # 确认人
  confirmed_at: "2026-06-12T10:15:00Z"    # 确认时间
  
  # ========== 不可变特性 ==========
  is_immutable: true                      # 一经确认不可修改
  
  # ========== 版本管理 ==========
  revision: 1                              # 迭代版本（从1开始）
  superseded_by: null                       # 被哪个 DP 替代（仅当 is_immutable=true 且有新版本时）
  supersedes: []                           # 废弃了哪些旧 DP
  
  # ========== 元数据 ==========
  created_at: "2026-06-12T10:15:00Z"
  created_by: "system"                     # system / agent / teacher
  version: "v1.0"
```

### 2.2 决策点 ID 命名规则

| 组成部分 | 说明 | 示例 |
|---------|------|------|
| `DP` | 前缀 | 固定为 DP |
| `{scene_abbr}` | 场景缩写（2-4字符） | S1=Stage1, CP=CoursePlanning, LN=LessonNote |
| `{3位序号}` | 3位数字，从 001 开始 | 001, 002, 003 |

#### 场景缩写对照表

| 场景 | 缩写 | 说明 |
|-----|------|------|
| course_planning | CP | 课程规划 |
| lesson_preparation | LP | 备课辅助 |
| exercise_generation | EG | 练习题生成 |
| assessment_design | AD | 评估设计 |
| knowledge_network | KN | 知识网络 |

### 2.3 决策类别

| category | 说明 | 示例 |
|----------|------|------|
| `objective` | 教学目标类 | "总课时 = 12", "面向初三学生" |
| `method` | 教学方法类 | "教学方法 = 讲授法 + 探究法" |
| `structure` | 课程结构类 | "课程结构 = 4个单元" |
| `node` | 知识节点类 | "新增节点：配方法概念" |
| `edge` | 知识边类 | "建立边：消元法→建模策略" |
| `evaluation` | 评估方式类 | "评估指标 = 课堂表现 + 作业" |
| `constraint` | 约束条件类 | "课时上限 = 16", "必须覆盖中考考点" |
| `parameter` | 参数配置类 | "Agent temperature = 0.7" |

---

## 3. 全局决策索引结构

### 3.1 决策索引完整结构

```yaml
decision_index:
  # ========== 基础信息 ==========
  index_id: "idx_course_plan_2026_06_12_001"
  task_id: "task_course_plan_2026_06_12_001"
  name: "初中数学：一元二次方程 - 课程规划决策索引"
  
  # ========== 时间信息 ==========
  created_at: "2026-06-12T09:00:00Z"
  last_updated: "2026-06-12T10:45:00Z"
  version: "v3"
  
  # ========== 任务状态 ==========
  current_stage: "stage3_network_completed"    # 当前完成的阶段
  completed_stages:
    - stage1_objectives
    - stage2_structure
    - stage3_network
  pending_stages:
    - stage4_lesson_plan
    - stage5_exercises
  
  # ========== 决策统计 ==========
  dp_count: 12
  dp_by_category:
    objective: 3
    method: 2
    structure: 2
    node: 4
    edge: 1
  
  # ========== 决策列表 ==========
  decisions:
    - dp_id: "DP-CP-001"
      category: "objective"
      content: "总课时 = 12"
      stage: "stage1_objectives"
      confirmed_at: "2026-06-12T09:30:00Z"
      
    - dp_id: "DP-CP-002"
      category: "objective"
      content: "目标学生层次：初三"
      stage: "stage1_objectives"
      confirmed_at: "2026-06-12T09:30:00Z"
      
    - dp_id: "DP-CP-003"
      category: "method"
      content: "教学方法 = 讲授法 + 探究法 + 项目引领"
      stage: "stage1_objectives"
      confirmed_at: "2026-06-12T09:35:00Z"
      
    # ... 更多决策点
  
  # ========== 上下文注入摘要（自动生成）============
  context_injection_summary:
    format: "bulleted_list"
    max_tokens: 300
    generated_at: "2026-06-12T10:45:00Z"
    summary: |
      已确认决策（截至 stage3_network_completed）：
      · 总课时12，面向初三学生
      · 教学方法：讲授法+探究法+项目引领
      · 课程结构：4个单元（引入/解法探究/建模/综合）
      · 知识网络含概念/技能/工具三层，共6个节点
      · 评估指标含课堂表现+书面作业+项目作品
```

---

## 4. context_injection_summary 格式

### 4.1 设计目标

context_injection_summary 是自动生成的极简上下文摘要，用于注入到 Agent 的 prompt 中，控制 Token 消耗。

### 4.2 生成规则

| 规则 | 说明 |
|-----|------|
| **格式** | bullet list，每行一个决策 |
| **长度上限** | 300 Token |
| **内容来源** | 从所有已确认的 DP 中提取 |
| **优先级** | 按 category 排序：objective > method > structure > node > edge > evaluation > constraint |
| **摘要粒度** | 每类最多显示 3 个关键决策，超出部分用"...等"标注 |

### 4.3 生成示例

```yaml
context_injection_summary:
  format: "bulleted_list"
  max_tokens: 300
  generated_at: "2026-06-12T10:45:00Z"
  
  # 完整内容（实际注入时会被压缩）
  full_content: |
    已确认决策（截至 stage3）：
    · 目标：总课时12节，面向初三学生
    · 方法：讲授法+探究法+项目引领
    · 结构：4个单元（引入/解法探究/建模/综合）
    · 节点：6个节点（一元二次方程的概念/技能/工具各2个）
    · 边：5条边（前置2条+跨层理解2条+跨层操作1条）
    · 评估：课堂表现20%+书面作业30%+项目作品50%
  
  # Token 统计
  token_count: 186
  compression_ratio: 0.62
```

### 4.4 不同阶段的摘要示例

```yaml
# Stage 1 完成后的摘要
summary_stage1: |
  已确认决策：
  · 总课时12节
  · 面向初三学生
  · 教学方法：讲授法+探究法+项目引领

# Stage 2 完成后的摘要
summary_stage2: |
  已确认决策（截至 stage2）：
  · 总课时12节，面向初三学生
  · 教学方法：讲授法+探究法+项目引领
  · 课程结构：4个单元（引入/解法探究/建模/综合）

# Stage 3 完成后的摘要
summary_stage3: |
  已确认决策（截至 stage3）：
  · 总课时12节，面向初三学生
  · 教学方法：讲授法+探究法+项目引领
  · 课程结构：4个单元（引入/解法探究/建模/综合）
  · 知识网络含概念/技能/工具三层，共6个节点
```

---

## 5. 不可变原则执行机制

### 5.1 不可变特性定义

决策点一经确认（`confirmed_by` 字段被填充），`is_immutable` 自动设为 `true`，此后：
- 不得直接修改 `content` 字段
- 不得删除 DP 记录
- 不得修改 `confirmed_by` 和 `confirmed_at`

### 5.2 修改决策的正确方式

当教师需要修改已确认的决策时，应通过以下流程：

```
教师提出修改需求
       │
       ▼
[创建新决策点]
       │
       ├─ 新 DP 继承原 DP 的引用关系
       ├─ 新 DP 的 revision = 原 DP.revision + 1
       └─ 新 DP 的 supersedes = [原 DP.dp_id]
       │
       ▼
[标记原决策点为已废弃]
       │
       ├─ 原 DP.is_immutable = true（保持）
       ├─ 原 DP.superseded_by = 新 DP.dp_id
       │
       ▼
[新决策点等待确认]
       │
       ▼
教师确认新决策点
       │
       ▼
[新决策点生效]
```

### 5.3 版本更迭示例

```yaml
# 原决策点 v1
decision_point:
  dp_id: "DP-CP-003"
  revision: 1
  content: "教学方法 = 讲授法 + 探究法"
  confirmed_by: "teacher_001"
  confirmed_at: "2026-06-12T09:35:00Z"
  is_immutable: true
  superseded_by: "DP-CP-003-v2"
  supersedes: []
  
# 新决策点 v2（替代 v1）
decision_point:
  dp_id: "DP-CP-003-v2"
  revision: 2
  content: "教学方法 = 讲授法 + 探究法 + 项目引领"
  confirmed_by: "teacher_001"
  confirmed_at: "2026-06-13T14:20:00Z"
  is_immutable: true
  superseded_by: null
  supersedes:
    - "DP-CP-003"              # 指向被废弃的原 DP
```

### 5.4 代码层面强制执行

```python
class DecisionPoint:
    """决策点数据模型"""
    
    def update(self, updates: dict, actor: str) -> None:
        """
        更新决策点。
        
        不可变原则：如果 is_immutable=True，只能修改特定字段。
        """
        if self.is_immutable and actor != "system":
            # 只允许修改 superseded_by 和 supersedes
            allowed_fields = {"superseded_by", "supersedes", "updated_at"}
            illegal_fields = set(updates.keys()) - allowed_fields
            if illegal_fields:
                raise ImmutableDecisionPointError(
                    f"Cannot modify immutable DP {self.dp_id}. "
                    f"Illegal fields: {illegal_fields}"
                )
        
        # 执行更新
        for key, value in updates.items():
            setattr(self, key, value)
    
    def mark_superseded(self, new_dp_id: str) -> None:
        """标记为被新 DP 替代"""
        if not self.is_immutable:
            raise ValueError("Can only supersede an immutable DP")
        self.superseded_by = new_dp_id
```

---

## 6. DP 记录生命周期

### 6.1 状态流转

```
                                    ┌──────────────┐
                                    │   draft      │ ← 初始状态
                                    └──────┬───────┘
                                           │ teacher/action=confirm
                                           ▼
                              ┌────────────────────────┐
                              │   confirmed            │ ← is_immutable=true
                              │   (不可变)             │
                              └───────────┬────────────┘
                                          │ new DP created to replace
                                          ▼
                              ┌────────────────────────┐
                              │   superseded          │ ← 保持不可变
                              │   (被替代)            │   但 superseded_by 填充
                              └────────────────────────┘
```

### 6.2 状态字段说明

| 状态 | 说明 | 转换条件 |
|-----|------|---------|
| `draft` | 草稿状态 | 初始状态，可编辑 |
| `confirmed` | 已确认 | `confirmed_by` 被填充，`is_immutable=true` |
| `superseded` | 已被替代 | `superseded_by` 被填充 |

---

## 7. 数据校验规则

### 7.1 DP 校验规则

| 规则 | 约束条件 |
|-----|---------|
| dp_id 唯一性 | 全局范围内不能重复 |
| dp_id 格式 | 必须符合 `DP-{scene_abbr}-{NNN}` 或 `DP-{scene_abbr}-{NNN}-v{N}` |
| scene_type 存在 | 必须是已注册的场景类型 |
| category 枚举 | 必须是 8 种类别之一 |
| content 非空 | content 字段长度 > 0 |
| confirmed_by 非空 | 当 is_immutable=true 时，confirmed_by 必填 |
| revision >= 1 | 版本号从 1 开始 |
| superseded_by 引用 | 必须指向存在的 dp_id 或 null |

### 7.2 决策索引校验规则

| 规则 | 约束条件 |
|-----|---------|
| index_id 唯一性 | 全局范围内不能重复 |
| dp_count 一致性 | 必须等于 decisions 数组长度 |
| stage 顺序性 | completed_stages 中的阶段必须按顺序排列 |
| context_injection_summary.token_count | 必须 <= 300 |

---

## 8. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| DP ID 命名 | `DP-{scene_abbr}-{NNN}` | 全局唯一，支持版本化 |
| 不可变原则 | 一经确认即不可修改 | 保证决策一致性和可审计性 |
| 版本更迭 | 新增 DP 而非修改 | 保持历史追溯能力 |
| context_injection | ≤ 300 Token | 控制上下文膨胀 |
| 摘要格式 | bullet list | 简洁、结构化、LLM 易解析 |
| 状态流转 | draft → confirmed → superseded | 清晰的状态管理 |

---

## 9. 文件目录结构

```
eduagents/
├── knowledge_compilation/
│   ├── compiler/
│   │   ├── dp_extractor.py          # 决策点提取器
│   │   ├── index_updater.py         # 决策索引更新器
│   │   └── validator.py            # DP 校验器
│   ├── wiki/                        # Knowledge Wiki
│   │   └── ...                      # 见 decision_index.md
│   ├── decision_index.json          # 全局决策索引
│   └── dp_registry.yaml             # DP 注册表（可选）
└── docs/architecture/data_models/
    └── decision_point.md            # 本文档
```

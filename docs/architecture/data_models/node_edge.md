# 节点与边数据模型设计

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-05（立体分层知识网络）

---

## 1. 设计目标

定义知识网络中节点（Node）和边（Edge）的标准数据结构，支持：
- 三层立体结构（概念层、技能层、工具层）
- 多类型边关系（前置、支持、理解、操作）
- 布鲁姆分类法映射
- 节点元数据管理

---

## 2. 节点数据结构

### 2.1 节点 ID 命名规则

节点 ID 采用 `{domain}_{topic}_{layer}_{seq}` 格式，确保全局唯一性：

| 组成部分 | 说明 | 示例 |
|---------|------|------|
| `domain` | 学科领域 | math, physics, chemistry, english |
| `topic` | 知识点主题（下划线分隔） | quadratic_equation, linear_function |
| `layer` | 层次 | concept, skill, tool |
| `seq` | 同主题同层序号（3位数字） | 001, 002, 003 |

#### 命名示例

```yaml
# 数学领域，一元二次方程主题，概念层，第1个节点
node_id: "node_math_quadratic_equation_concept_001"

# 数学领域，一元二次方程主题，技能层，第1个节点
node_id: "node_math_quadratic_equation_skill_001"

# 数学领域，一元二次方程主题，工具层，第1个节点
node_id: "node_math_quadratic_equation_tool_001"
```

### 2.2 节点完整结构

```yaml
node:
  # ========== 基础标识 ==========
  node_id: "node_math_quadratic_equation_concept_001"
  name: "一元二次方程的本质"
  description: "理解一元二次方程的数学本质，掌握其几何意义"
  
  # ========== 层级分类 ==========
  layer: "concept"                              # concept / skill / tool
  domain: "mathematics"
  topic: "quadratic_equation"
  sub_topic: "equation_basic"                  # 可选：子主题
  
  # ========== 教学属性 ==========
  
  # 布鲁姆分类级别
  bloom_level: "analysis"                     # remember / understand / apply / analyze / evaluate / create
  
  # 难度等级（1-5）
  difficulty: 3
  
  # 预估学习时长（分钟）
  estimated_periods: 45
  
  # 是否支持自学
  can_self_learn: true
  
  # ========== 关联映射 ==========
  
  # 关联的教学单元
  mapped_unit: "unit_002"
  
  # 同主题其他层的关联节点
  related_nodes:
    same_topic_skill: "node_math_quadratic_equation_skill_001"
    same_topic_tool: "node_math_quadratic_equation_tool_001"
  
  # ========== 评估标准 ==========
  mastery_criteria:
    - type: "quiz"
      threshold: 0.8                          # 正确率 ≥ 80%
      question_count: 10
    - type: "explanation"
      threshold: "satisfactory"               # 解释质量达标
      rubric: "能清晰阐述方程的几何意义"
    - type: "practice"
      threshold: 5                            # 正确完成5道练习
  
  # ========== 学习资源 ==========
  resources:
    - type: "video"
      url: "/resources/video/quadratic_intro.mp4"
      duration_minutes: 15
    - type: "document"
      url: "/resources/docs/quadratic_theory.pdf"
    - type: "interactive"
      url: "/resources/interactive/quadratic explorer.html"
  
  # ========== 元数据 ==========
  created_at: "2026-06-01T10:00:00Z"
  updated_at: "2026-06-12T15:30:00Z"
  created_by: "teacher_001"
  version: "v1.0"
  
  # ========== 状态字段（运行时）============
  status: "active"                            # active / deprecated / under_review
  tags: ["基础", "重要", "中考必考"]
```

### 2.3 各层节点特征

| 层次 | 关注点 | 典型描述模板 | 评估方式 |
|-----|-------|------------|---------|
| **概念层（Concept）** | 为什么（本质、原理、推导） | "理解...的本质" "掌握...的原理" | 解释、论证、设计 |
| **技能层（Skill）** | 何时用（情境判断、迁移、策略选择） | "能够在...情境下应用" "能判断...的适用条件" | 情境判断、问题解决 |
| **工具层（Tool）** | 怎么操作（步骤、流程、模板） | "能够正确操作..." "能够使用...步骤完成..." | 操作正确性、熟练度 |

### 2.4 布鲁姆分类映射

```yaml
bloom_taxonomy_mapping:
  remember:
    description: "识别、回忆事实"
    example: "能说出求根公式"
    assessment: "默写、识别"
    
  understand:
    description: "解释含义，构建意义"
    example: "能用语言描述配方法的几何意义"
    assessment: "解释、举例"
    
  apply:
    description: "在情境中应用"
    example: "能用配方法解一元二次方程"
    assessment: "解题、操作"
    
  analyze:
    description: "拆解分析关系"
    example: "能分析判别式与根的关系"
    assessment: "分析、对比、分类"
    
  evaluate:
    description: "基于标准判断"
    example: "能判断何时使用配方法还是公式法"
    assessment: "评价、决策"
    
  create:
    description: "综合创新产生"
    example: "能设计一元二次方程的实际应用问题"
    assessment: "设计、创作、发明"
```

---

## 3. 边数据结构

### 3.1 边关系类型

| 边类型 | 含义 | 方向规则 | 典型示例 |
|-------|------|---------|---------|
| **is_prerequisite** | 前置依赖 | A → B（A 是 B 的前置） | 一元一次方程 → 二元一次方程 |
| **supports_understanding** | 支持理解（跨层） | tool → skill → concept | 消元法操作 → 建模策略 → 方程概念 |
| **enables_operation** | 支持操作（跨层） | concept → skill → tool | 方程概念 → 解方程技能 → 消元法操作 |
| **same_topic_cross_layer** | 同主题跨层 | 双向关联 | 一元二次方程(概念) ↔ 一元二次方程(技能) |
| **related_topic** | 相关主题 | 双向 | 一元二次方程 ↔ 二次函数 |

### 3.2 边完整结构

```yaml
edge:
  # ========== 基础标识 ==========
  edge_id: "edge_math_quadratic_001"
  name: "配方法操作支持解方程技能理解"
  
  # ========== 连接关系 ==========
  source_node_id: "node_math_quadratic_equation_tool_001"   # 消元法工具
  target_node_id: "node_math_quadratic_equation_skill_001"   # 解方程技能
  relation_type: "supports_understanding"                    # 边关系类型
  
  # ========== 关系属性 ==========
  
  # 权重（影响推荐优先级，0.0-1.0）
  weight: 1.0
  
  # 是否必须掌握（用于约束推荐）
  is_required: true
  
  # 学习方向：A→B 表示先学 A 再学 B
  learning_direction: "forward"                              # forward / backward / bidirectional
  
  # ========== 描述信息 ==========
  description: "掌握配方法的具体操作步骤有助于理解解方程的策略选择"
  
  # ========== 元数据 ==========
  created_at: "2026-06-01T10:00:00Z"
  updated_at: "2026-06-12T15:30:00Z"
  created_by: "teacher_001"
  version: "v1.0"
```

### 3.3 边关系详细说明

#### 3.3.1 is_prerequisite（前置依赖）

```yaml
# 示例：一元一次方程是二元一次方程的前置
edge:
  edge_id: "edge_prereq_linear_to_systems"
  source_node_id: "node_math_linear_equation_tool_001"
  target_node_id: "node_math_linear_systems_skill_001"
  relation_type: "is_prerequisite"
  weight: 1.0
  is_required: true
  description: "掌握一元一次方程的解法是学习二元一次方程组的前提"
```

#### 3.3.2 supports_understanding（支持理解）

```yaml
# 示例：消元法操作帮助理解建模策略
edge:
  edge_id: "edge_support_elimination_skill"
  source_node_id: "node_math_elimination_tool_001"
  target_node_id: "node_math_modeling_skill_001"
  relation_type: "supports_understanding"
  weight: 0.8
  is_required: false
  description: "消元法操作经验有助于理解何时选择建模策略"
```

#### 3.3.3 enables_operation（支持操作）

```yaml
# 示例：方程概念支持解方程技能
edge:
  edge_id: "edge_enable_equation_concept_skill"
  source_node_id: "node_math_quadratic_equation_concept_001"
  target_node_id: "node_math_quadratic_equation_skill_001"
  relation_type: "enables_operation"
  weight: 1.0
  is_required: true
  description: "理解方程本质有助于掌握解方程的技能"
```

#### 3.3.4 same_topic_cross_layer（同主题跨层）

```yaml
# 示例：一元二次方程概念层与技能层关联
edge:
  edge_id: "edge_same_topic_concept_skill"
  source_node_id: "node_math_quadratic_equation_concept_001"
  target_node_id: "node_math_quadratic_equation_skill_001"
  relation_type: "same_topic_cross_layer"
  weight: 1.0
  is_required: false
  learning_direction: "bidirectional"
  description: "一元二次方程的概念理解与技能应用相互促进"
```

#### 3.3.5 related_topic（相关主题）

```yaml
# 示例：一元二次方程与二次函数相关
edge:
  edge_id: "edge_related_quadratic_function"
  source_node_id: "node_math_quadratic_equation_concept_001"
  target_node_id: "node_math_quadratic_function_concept_001"
  relation_type: "related_topic"
  weight: 0.6
  is_required: false
  learning_direction: "bidirectional"
  description: "一元二次方程与二次函数在图像和代数上密切相关"
```

---

## 4. 节点元数据

### 4.1 元数据字段说明

| 字段 | 类型 | 说明 | 必填 |
|-----|------|------|------|
| `bloom_level` | enum | 布鲁姆分类级别 | 是 |
| `difficulty` | integer (1-5) | 难度等级 | 是 |
| `can_self_learn` | boolean | 是否支持自学 | 是 |
| `estimated_periods` | integer | 预估学习时长（分钟） | 是 |
| `mastery_criteria` | array | 掌握判定标准 | 是 |
| `mapped_unit` | string | 关联教学单元 | 否 |
| `resources` | array | 学习资源列表 | 否 |
| `tags` | array | 标签（搜索/筛选用） | 否 |

### 4.2 元数据示例

```yaml
# 概念层节点元数据
node_metadata:
  layer: concept
  bloom_level: analyze
  difficulty: 4
  can_self_learn: false
  estimated_periods: 90
  mastery_criteria:
    - type: explanation
      threshold: satisfactory
    - type: quiz
      threshold: 0.85

---
  
# 技能层节点元数据
node_metadata:
  layer: skill
  bloom_level: apply
  difficulty: 3
  can_self_learn: true
  estimated_periods: 60
  mastery_criteria:
    - type: scenario_judgment
      threshold: 0.85
    - type: problem_solving
      threshold: 3

---
  
# 工具层节点元数据
node_metadata:
  layer: tool
  bloom_level: understand
  difficulty: 2
  can_self_learn: true
  estimated_periods: 30
  mastery_criteria:
    - type: operation_correctness
      threshold: 2                    # 连续2次正确
    - type: fluency
      threshold: 5                    # 5分钟内完成
```

---

## 5. 知识网络整体结构

### 5.1 网络结构

```yaml
knowledge_network:
  # ========== 基础信息 ==========
  network_id: "network_math_grade9_2026"
  name: "九年级数学知识网络"
  description: "九年级数学课程的立体分层知识网络"
  domain: "mathematics"
  grade_level: "9"
  version: "v1.0"
  
  # ========== 节点管理 ==========
  nodes:
    - node_id: "node_math_quadratic_equation_concept_001"
      name: "一元二次方程的本质"
      layer: "concept"
      # ... 完整节点对象
    - node_id: "node_math_quadratic_equation_skill_001"
      name: "解一元二次方程的技能"
      layer: "skill"
      # ... 完整节点对象
    - node_id: "node_math_quadratic_equation_tool_001"
      name: "配方法操作"
      layer: "tool"
      # ... 完整节点对象
  
  # ========== 边管理 ==========
  edges:
    - edge_id: "edge_enable_equation_concept_skill"
      source_node_id: "node_math_quadratic_equation_concept_001"
      target_node_id: "node_math_quadratic_equation_skill_001"
      relation_type: "enables_operation"
      weight: 1.0
      is_required: true
    - edge_id: "edge_support_operation_skill"
      source_node_id: "node_math_quadratic_equation_tool_001"
      target_node_id: "node_math_quadratic_equation_skill_001"
      relation_type: "supports_understanding"
      weight: 0.8
      is_required: false
    # ... 更多边
  
  # ========== 统计信息 ==========
  statistics:
    total_nodes: 156
    concept_nodes: 52
    skill_nodes: 54
    tool_nodes: 50
    total_edges: 312
    
  # ========== 元数据 ==========
  created_at: "2026-06-01T10:00:00Z"
  updated_at: "2026-06-12T15:30:00Z"
  created_by: "teacher_001"
```

---

## 6. 数据校验规则

### 6.1 节点校验

| 规则 | 约束条件 |
|-----|---------|
| node_id 唯一性 | 全局范围内不能重复 |
| node_id 格式 | 必须符合 `{domain}_{topic}_{layer}_{seq}` |
| layer 枚举 | 必须是 concept/skill/tool 之一 |
| bloom_level 枚举 | 必须是 remember/understand/apply/analyze/evaluate/create 之一 |
| difficulty 范围 | 必须是 1-5 的整数 |
| estimated_periods 范围 | 必须 > 0 |
| related_nodes 引用 | 必须指向存在的 node_id |

### 6.2 边校验

| 规则 | 约束条件 |
|-----|---------|
| edge_id 唯一性 | 全局范围内不能重复 |
| source_node_id 存在 | 必须指向已存在的节点 |
| target_node_id 存在 | 必须指向已存在的节点 |
| source ≠ target | 边不能连接自身 |
| relation_type 枚举 | 必须是 5 种边类型之一 |
| weight 范围 | 必须是 0.0-1.0 的浮点数 |

---

## 7. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| 节点 ID 命名 | `{domain}_{topic}_{layer}_{seq}` | 保证唯一性，便于识别和管理，支持按主题/层筛选 |
| 边关系类型 | 5 种基础类型 | 覆盖主要教学关系，支持语义化查询 |
| 布鲁姆映射 | 6 级分类 | 与主流教学理论对齐，便于评估设计 |
| 掌握判定 | 分层差异化标准 | 不同层次的掌握要求不同，符合教学规律 |
| 元数据完整性 | bloom_level/difficulty/can_self_learn/estimated_periods 必填 | 保证知识网络的可推荐性 |

---

## 8. 文件目录结构

```
eduagents/
├── data/
│   └── knowledge_networks/
│       ├── network_math_grade9_2026/
│       │   ├── network.yaml              # 完整网络定义
│       │   ├── nodes/
│       │   │   ├── concept_nodes.yaml
│       │   │   ├── skill_nodes.yaml
│       │   │   └── tool_nodes.yaml
│       │   └── edges/
│       │       └── edges.yaml
│       └── index.json                    # 网络索引
├── models/
│   └── node_edge.py                      # 节点边数据模型
└── docs/architecture/data_models/
    └── node_edge.md                      # 本文档
```

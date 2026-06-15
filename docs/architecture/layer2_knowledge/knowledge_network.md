# 立体分层知识网络设计

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-05（立体分层知识网络）

---

## 1. 设计目标

知识网络是 EduAgents 的核心数据结构，支持：
- 概念/技能/工具三层立体结构
- 同层边与跨层边关系
- 动态学习路径推荐
- 节点掌握状态追踪

| 设计原则 | 说明 |
|---------|------|
| **分层设计** | 同一知识点在概念/技能/工具三层投影为独立节点 |
| **多路径支持** | 允许多个入口节点和多条达成路径 |
| **可扩展性** | 支持节点类型扩展和边关系类型扩展 |
| **可序列化** | 支持 YAML/JSON 格式持久化 |

---

## 2. 数据模型

### 2.1 节点类型

| 节点层次 | 关注点 | 布鲁姆分类 | 评估方式 |
|---------|--------|-----------|---------|
| **概念层（Concept）** | 为什么（本质、原理、推导） | 分析/评价/创造 | 解释、论证、设计 |
| **技能层（Skill）** | 何时用（情境判断、迁移、策略选择） | 应用/分析 | 情境判断、问题解决 |
| **工具层（Tool）** | 怎么操作（步骤、流程、模板） | 记忆/理解/应用 | 操作正确性、熟练度 |

### 2.2 节点数据结构

```yaml
node:
  node_id: "node_math_quadratic_concept_001"  # {domain}_{topic}_{layer}_{seq}
  name: "一元二次方程的本质"
  description: "理解一元二次方程的数学本质，掌握其几何意义"
  layer: "concept"                            # concept / skill / tool
  domain: "mathematics"
  topic: "quadratic_equation"
  
  # 布鲁姆分类级别
  bloom_level: "analysis"                     # remember/understand/apply/analyze/evaluate/create
  
  # 难度等级（1-5）
  difficulty: 3
  
  # 预估学习时长（分钟）
  estimated_periods: 45
  
  # 是否支持自学
  can_self_learn: true
  
  # 关联的教学单元
  mapped_unit: "unit_002"
  
  # 评估标准
  mastery_criteria:
    - type: "quiz"
      threshold: 0.8                          # 正确率 ≥ 80%
    - type: "explanation"
      threshold: "satisfactory"               # 解释质量达标
  
  # 学习资源引用
  resources:
    - type: "video"
      url: "/resources/video/quadratic_intro.mp4"
    - type: "document"
      url: "/resources/docs/quadratic_theory.pdf"
  
  # 创建/更新信息
  created_at: "2026-06-01T10:00:00Z"
  updated_at: "2026-06-12T15:30:00Z"
  created_by: "teacher_001"
```

### 2.3 边关系类型

| 边类型 | 含义 | 方向 | 示例 |
|-------|------|------|------|
| **is_prerequisite** | 前置依赖 | A → B（A是B的前置） | 一元一次方程 → 二元一次方程 |
| **supports_understanding** | 支持理解（跨层） | tool → skill → concept | 消元法操作 → 建模策略选择 |
| **enables_operation** | 支持操作（跨层） | concept → skill → tool | 方程概念 → 解方程技能 → 消元法操作 |
| **same_topic_cross_layer** | 同主题跨层 | 同一知识点不同层 | 一元二次方程(概念) ↔ 一元二次方程(技能) |
| **related_topic** | 相关主题 | 双向 | 一元二次方程 ↔ 二次函数 |

### 2.4 边数据结构

```yaml
edge:
  edge_id: "edge_math_quadratic_001"
  source_node_id: "node_math_linear_tool_001"
  target_node_id: "node_math_quadratic_tool_001"
  relation_type: "is_prerequisite"            # 边关系类型
  
  # 权重（影响推荐优先级）
  weight: 1.0
  
  # 是否必须掌握（用于约束推荐）
  is_required: true
  
  # 描述
  description: "掌握一元一次方程解法是学习二元一次方程的前提"
  
  created_at: "2026-06-01T10:00:00Z"
  created_by: "teacher_001"
```

### 2.5 知识网络整体结构

```yaml
knowledge_network:
  network_id: "network_math_grade9_2026"
  name: "九年级数学知识网络"
  description: "九年级数学课程的立体分层知识网络"
  domain: "mathematics"
  grade_level: "9"
  
  # 节点列表
  nodes:
    - {node_id: "node_math_quadratic_concept_001", ...}
    - {node_id: "node_math_quadratic_skill_001", ...}
    - {node_id: "node_math_quadratic_tool_001", ...}
    - ...
  
  # 边列表
  edges:
    - {edge_id: "edge_math_quadratic_001", ...}
    - {edge_id: "edge_math_quadratic_002", ...}
    - ...
  
  # 元数据
  created_at: "2026-06-01T10:00:00Z"
  updated_at: "2026-06-12T15:30:00Z"
  version: "v1.0"
```

---

## 3. 知识网络构建流程

### 3.1 三阶段构建流程

```
阶段1：教学目标设计
       │
       ▼
输入：课程名称、课程描述、目标学生层次
       │
       ▼
输出：knowledge_goals / ability_goals / quality_goals
      teaching_methods / assessment_methods
       │
       ▼
阶段2：课程结构设计
       │
       ▼
输入：阶段1输出
       │
       ▼
输出：units 结构数组
      每个unit含：teaching_method + estimated_periods + core_knowledge_keywords
       │
       ▼
阶段3：立体分层知识网络设计
       │
       ▼
输入：阶段2输出
       │
       ▼
输出：nodes（concept/skill/tool三层） + edges（层内+跨层）
```

### 3.2 教师+Agent共创流程

```
Agent 生成初稿
       │
       ▼
教师审核
       │
       ├─ 通过 → 标记为已确认，进入下一阶段
       │
       └─ 修改 → Agent 根据反馈迭代
                 │
                 ▼
            重复直至确认
```

---

## 4. 节点掌握状态模型

### 4.1 学生节点掌握记录

```yaml
student_node_progress:
  progress_id: "progress_stu001_node001"
  student_id: "student_001"
  node_id: "node_math_quadratic_concept_001"
  
  # 掌握状态
  mastery_status: "in_progress"               # not_started / in_progress / mastered / needs_attention
  
  # 评估记录
  assessments:
    - assessment_id: "assess_001"
      type: "quiz"
      score: 0.75
      timestamp: "2026-06-12T10:00:00Z"
    - assessment_id: "assess_002"
      type: "explanation"
      score: "satisfactory"
      timestamp: "2026-06-12T11:30:00Z"
  
  # 学习时长（分钟）
  total_time_spent: 90
  
  # 错题记录
  error_count: 3
  
  # 最后学习时间
  last_learned_at: "2026-06-12T11:30:00Z"
```

### 4.2 掌握判定规则

| 节点层次 | 掌握条件 | 重试上限 |
|---------|---------|---------|
| 概念层 | 解释质量达标 AND 测验正确率 ≥ 80% | 3次 |
| 技能层 | 情境判断正确率 ≥ 85% | 3次 |
| 工具层 | 连续2次操作正确 | 5次 |

---

## 5. 数据访问接口

### 5.1 核心接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `create_network(network_data)` | 创建知识网络 | network_data: dict | network_id: str |
| `get_network(network_id)` | 获取知识网络 | network_id: str | Network 对象 |
| `update_network(network_id, updates)` | 更新知识网络 | network_id: str, updates: dict | 更新后的 Network |
| `delete_network(network_id)` | 删除知识网络 | network_id: str | 操作结果 |
| `add_node(network_id, node_data)` | 添加节点 | network_id: str, node_data: dict | node_id: str |
| `update_node(node_id, updates)` | 更新节点 | node_id: str, updates: dict | 更新后的 Node |
| `delete_node(node_id)` | 删除节点 | node_id: str | 操作结果 |
| `add_edge(network_id, edge_data)` | 添加边 | network_id: str, edge_data: dict | edge_id: str |
| `update_edge(edge_id, updates)` | 更新边 | edge_id: str, updates: dict | 更新后的 Edge |
| `delete_edge(edge_id)` | 删除边 | edge_id: str | 操作结果 |
| `get_node_by_topic(topic, layer)` | 按主题查询节点 | topic: str, layer: str | Node 列表 |
| `get_prerequisites(node_id)` | 获取前置节点 | node_id: str | Node 列表 |
| `get_successors(node_id)` | 获取后继节点 | node_id: str | Node 列表 |

---

## 6. 序列化与持久化

### 6.1 存储格式

| 格式 | 用途 | 优点 |
|-----|------|------|
| YAML | 配置文件、人工编辑 | 人类可读、结构化 |
| JSON | API 传输、程序处理 | 轻量、解析快 |
| SQLite/PostgreSQL | 生产环境持久化 | 事务支持、查询高效 |

### 6.2 文件目录结构

```
knowledge_networks/
├── network_math_grade9_2026/
│   ├── network.yaml           # 完整网络定义
│   ├── nodes/                 # 节点定义（可选拆分）
│   │   ├── concept_nodes.yaml
│   │   ├── skill_nodes.yaml
│   │   └── tool_nodes.yaml
│   └── edges/                 # 边定义（可选拆分）
│       └── edges.yaml
└── index.json                 # 网络索引
```

---

## 7. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| 节点ID命名 | `{domain}_{topic}_{layer}_{seq}` | 保证唯一性，便于识别和管理 |
| 边关系类型 | 5种基础类型 + 可扩展 | 覆盖主要教学关系，支持未来扩展 |
| 掌握判定 | 分层差异化标准 | 不同层次的掌握要求不同 |
| 持久化格式 | YAML + 数据库 | 兼顾人类可读性与程序处理效率 |
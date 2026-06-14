# DP-CONT-02：课程规划完整产物结构

**确认日期**：2026-06-12 · **确认人**：项目核心团队 · **决策类别**：内容

---

## 决策摘要

SCENE-001（课程规划）的完整产物以 `course_planning` YAML 结构组织，覆盖：**stage1 教学目标体系（知识/能力/素质目标 + 教学方法选择 + 检验方式）** → **stage2 课程结构（units 数组，含 teaching_method / estimated_periods / core_knowledge_keywords）** → **stage3 立体分层知识网络（nodes + edges + network_notes）**。贯穿产物 evaluation_metrics 与节点绑定。

## 核心设计原则

1. **三阶段产物以一个 YAML 结构统一表示，
2. **stage2 units 与 stage3 nodes 保持映射关系（mapped_unit 字段），
3. **evaluation_metrics 与 stage3 具体节点绑定（target_node 字段），
4. **每个节点独立含 bloom_level / difficulty / can_self_learn / estimated_periods，
5. **边关系区分同层 is_prerequisite / 跨层 supports_understanding / enables_operation / same_topic_cross_layer。

## 关键细节

### course_planning 顶层结构

```yaml
course_planning:
  metadata:
    course_name: "课程名称"
    target_level: "目标学生层次"
    total_periods: N
    version: "x.y"
    created_at: "{datetime}"
    teacher_id: "t_{NNN}"

  # ============== stage1 产物：教学目标体系 ==============
  stage1_teaching_objectives:
    knowledge_goals:          # 知识目标列表，每项为 string
      - "..."
    ability_goals:            # 能力目标列表
      - "..."
    quality_goals:            # 素质目标列表
      - "..."
    expected_learning_outcomes:  # 可观测的学习产出
      - "..."
    teaching_methods:         # 见 DP-CONT-01
      - method_id: "lecture"
        name: "讲授法"
        applicable_structure: "chapter"
    assessment_methods:       # 学习效果检验方式
      - "课堂小检测"
      - "书面作业"

  # ============== stage2 产物：课程结构 ==============
  stage2_course_structure:
    structure_type: "mixed"   # chapter / scene / inquiry / mixed

    units:
      - unit_id: "unit_01"
        title: "..."
        teaching_method: "讲授法 + 讨论法"
        estimated_periods: N
        core_knowledge_keywords: ["...", "..."]

      - unit_id: "unit_02"
        title: "..."
        # 同上 ...

  # ============== stage3 产物：立体分层知识网络 ==============
  stage3_knowledge_network:
    nodes:
      # 概念层节点（为什么 / 原理 / 本质）
      - id: "concept_{xxx}"
        layer: "concept"
        title: "..."
        bloom_level: "analyze"               # remember/understand/apply/analyze/evaluate/create
        difficulty: N                        # 1-5
        can_self_learn: false
        estimated_periods: N
        mapped_unit: "unit_{NN}"              # 与 stage2 unit 映射
        teaching_objectives:
          knowledge: ["..."]
          ability: ["..."]
          quality: ["..."]

      # 技能层节点（何时用 / 判断情境 / 迁移应用）
      - id: "skill_{xxx}"
        layer: "skill"
        title: "..."
        bloom_level: "apply"
        difficulty: N
        can_self_learn: false
        estimated_periods: N
        mapped_unit: "unit_{NN}"
        teaching_objectives:
          knowledge: ["..."]
          ability: ["..."]

      # 工具层节点（怎么操作 / 固定步骤 / 模板化使用）
      - id: "tool_{xxx}"
        layer: "tool"
        title: "..."
        bloom_level: "apply"
        difficulty: N
        can_self_learn: true
        estimated_periods: N
        mapped_unit: "unit_{NN}"

    edges:
      # 层内边（同层次前后依赖）
      - from: "concept_{A}"
        to: "concept_{B}"
        relation_type: "is_prerequisite"

      - from: "tool_{A}"
        to: "tool_{B}"
        relation_type: "is_prerequisite"

      # 跨层边（概念支撑技能，技能支撑工具）
      - from: "concept_{A}"
        to: "skill_{X}"
        relation_type: "supports_understanding"

      - from: "skill_{X}"
        to: "tool_{Y}"
        relation_type: "enables_operation"

      # 同主题跨层边（同一知识点三层间对应关系）
      - from: "concept_{A}"
        to: "skill_{X}"
        relation_type: "same_topic_cross_layer"

    network_notes:            # 多路径入口说明
      - "学生可从 {节点A}（基础较好）或 {节点B}（基础一般）进入网络"
      - "到达 {节点X} 可通过多条路径"
      - "{节点X} 是课程学习效果达成的汇聚节点"

  # ============== 贯穿产物：评估指标体系 ==============
  evaluation_metrics:
    - metric_id: "m_{NNN}"
      target_node: "concept_{xxx}"           # 绑定具体节点
      metric_type: "observational_scale"      # observational_scale / written_test / project_rubric
      content: "评估内容描述"
      observation_target: "课堂表现 + 课堂小检测"
      scoring_rubric: "评分规则描述"
      bloom_level: "understand"
      node_layer: "concept"                   # 与 target_node.layer 一致

agent_session_id: "sess_{scene}_{NNN}"
iteration_counts:
  stage1: N
  stage2: N
  stage3: N
created_at: "{datetime}"
```

### stage2 与 stage3 的映射约束

| 字段 | 位置 | 含义 |
|-----|------|------|
| units[*].unit_id | stage2 | 单元唯一标识 |
| nodes[*].mapped_unit | stage3 | 该节点归属的单元 ID，必须匹配 stage2 中某个 unit_id |
| units[*].core_knowledge_keywords | stage2 | 与 nodes[*].title / teaching_objectives 中的关键词呼应 |

### 边关系类型约束

| relation_type | 允许的 from.layer → to.layer | 说明 |
|---------------|-------------------------------|------|
| is_prerequisite | 相同 layer | 同层次节点先后依赖 |
| supports_understanding | concept → skill | 概念理解支撑技能应用 |
| enables_operation | skill → tool | 技能判断支撑工具操作 |
| same_topic_cross_layer | concept → skill / skill → tool | 同一知识点三层间对应 |

## 影响范围

- 关联 FR：FR-05（立体分层知识网络）、FR-10（教学评估）、FR-18（知识编译）；
- 关联场景：SCENE-001（课程规划）、SCENE-002（备课辅助）、SCENE-008（教学评估）；
- 关联决策：DP-CONT-01（教学方法 8 种）、DP-ARCH-11（教学评估指标设计）、DP-ARCH-13（知识网络动态维护）。

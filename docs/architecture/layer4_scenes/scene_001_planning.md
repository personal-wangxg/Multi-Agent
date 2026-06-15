# SCENE-001：课程规划场景

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**场景编号**：SCENE-001  
**关联功能需求**：FR-01（场景识别）、FR-02（Agent配置生成）、FR-03（Agent编排调度）、FR-05（知识网络构建）、FR-13（人机协同接口）、FR-18（知识编译）

---

## 1. 场景概述

**一句话描述**：教师提出课程规划需求后，系统通过三阶段流程（stage1目标设计→stage2结构设计→stage3网络构建）自动生成完整的课程规划产物，经教师确认后编译为决策索引供后续场景使用。

**参与角色**：
- 教师（用户发起者，决策确认者）
- 教学目标设计Agent（Stage 1）
- 课程结构设计Agent（Stage 2）
- 知识网络构建Agent（Stage 3）
- 评估指标设计Agent（贯穿三阶段）
- 编排调度Agent（FR-03）
- 知识编译Agent（FR-18）

---

## 2. 核心流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCENE-001 课程规划核心流程                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  教师输入 │───▶│ FR-01   │───▶│ FR-02   │───▶│ FR-03   │              │
│  │  课程请求 │    │ 场景识别 │    │ Agent   │    │ 编排调度 │              │
│  └──────────┘    └──────────┘    │ 配置生成 │    └────┬─────┘              │
│                                   └──────────┘         │                    │
│                                                          ▼                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    三阶段设计管道（Pipeline）                          │   │
│  │                                                                     │   │
│  │  ┌─────────────┐    teacher confirm    ┌─────────────┐              │   │
│  │  │  Stage 1    │────────────────────▶│  Stage 2    │              │   │
│  │  │  目标设计   │◀────────────────────│  结构设计   │              │   │
│  │  └─────────────┘    teacher confirm   └──────┬──────┘              │   │
│  │         │                                        │                   │   │
│  │         │  teaching_methods                       │ stage2 output    │   │
│  │         ▼                                        ▼                   │   │
│  │  ┌─────────────┐    teacher confirm   ┌─────────────────┐            │   │
│  │  │  评估指标   │◀────────────────────▶│    Stage 3      │            │   │
│  │  │  设计Agent  │                      │   知识网络构建   │            │   │
│  │  └──────┬──────┘                      └────────┬────────┘            │   │
│  │         │                                     │                      │   │
│  │         │ eval_metrics                         │ kn_output            │   │
│  │         │                                     │                      │   │
│  └─────────┼─────────────────────────────────────┼──────────────────────┘   │
│            │                                     │                          │
│            ▼                                     ▼                          │
│  ┌──────────────────┐                  ┌──────────────────┐                 │
│  │  FR-18 知识编译  │                  │  FR-12 持久化     │                 │
│  │  decision_index │                  │  产物存储        │                 │
│  └──────────────────┘                  └──────────────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Stage 1：教学目标设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Stage 1：教学目标设计                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  输入：course_name, course_desc, target_student_level        │
│         teacher_preferences（可选）                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 教学目标设计Agent（基于布鲁姆分类法）                    │  │
│  │ 产出：                                                  │  │
│  │   - knowledge_objectives（知识目标）                    │  │
│  │   - ability_objectives（能力目标）                      │  │
│  │   - quality_objectives（素质目标）                      │  │
│  │   - teaching_methods（8种方法选择）                     │  │
│  │   - expected_bloom_distribution                        │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Harness Schema校验（三阶段管道 Stage 1）                │  │
│  │ - 目标数量是否合理（3~8个为宜）                        │  │
│  │ - 三维目标是否均衡（知识/能力/素质）                    │  │
│  │ - 教学方法是否符合DP-CONT-01                           │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ FR-13 人机协同：教师确认卡片                           │  │
│  │ 教师操作：approve / revise / reject                    │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          │                                     │
│              ┌──────────┴──────────┐                          │
│              ▼                     ▼                          │
│        [confirmed]           [rejected]                       │
│             │                     │                            │
│             │                     ▼                            │
│             │              返回Agent重试                       │
│             │              （≤3次）                           │
│             ▼                                               │
│       进入Stage 2                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Stage 2：课程结构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Stage 2：课程结构设计                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  输入：stage1_confirmed_objectives, total_periods           │
│         reference_knowledge_network（可选）                  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 课程结构设计Agent                                      │  │
│  │ 产出：                                                  │  │
│  │   - unit_list：结构单元列表                            │  │
│  │   - unit_periods：每个单元课时数                       │  │
│  │   - unit_prerequisites：单元间依赖关系                   │  │
│  │   - core_knowledge_keywords：每个单元的核心知识点         │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 评估指标设计Agent（与结构绑定）                          │  │
│  │ 为每个结构单元关联评估指标                               │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Harness Schema校验 + 完整性检查                         │  │
│  │ - sum(unit_periods) ≈ total_periods（±10%）            │  │
│  │ - 每个单元有关键词支撑                                  │  │
│  │ - 依赖关系无循环                                       │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ FR-13 人机协同：教师确认卡片                           │  │
│  │ 教师操作：approve / revise / reject                    │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          │                                     │
│              ┌──────────┴──────────┐                          │
│              ▼                     ▼                          │
│        [confirmed]           [rejected]                       │
│             │                     │                            │
│             ▼                     ▼                            │
│       进入Stage 3            返回Agent重试                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Stage 3：知识网络构建

```
┌─────────────────────────────────────────────────────────────┐
│                    Stage 3：知识网络构建                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  输入：stage2_confirmed_structure, stage1_teaching_methods   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 知识网络构建Agent（FR-05 核心流程）                       │  │
│  │ 产出：                                                  │  │
│  │   - nodes[]：每个单元拆分为concept/skill/tool三层      │  │
│  │   - edges[]：层内边+跨层边+同主题边                     │  │
│  │   - layer_distribution：每层节点数统计                  │  │
│  │   - network_notes：网络结构说明                         │  │
│  │   - evaluation_metrics：与节点绑定的评估指标             │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Harness Schema校验                                     │  │
│  │ - 三层完整性：每层≥1个节点                             │  │
│  │ - 边方向一致性：prerequisite同层/supports概念→技能/     │  │
│  │                 enables技能→工具                       │  │
│  │ - 无孤立节点                                          │  │
│  │ - mapped_unit引用有效性                                │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ FR-13 人机协同：教师确认卡片（最终产物）                │  │
│  │ 教师操作：approve / revise / reject                   │  │
│  │ 备注：此阶段允许教师对节点/边进行直接编辑               │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          │                                     │
│              ┌──────────┴──────────┐                          │
│              ▼                     ▼                          │
│        [confirmed]           [rejected]                       │
│             │                     │                            │
│             ▼                     ▼                            │
│  ┌──────────────────┐     返回Agent重试                        │
│  │ teacher_confirmed│                                          │
│  │ = true           │                                          │
│  └────────┬─────────┘                                          │
│           ▼                                                    │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ FR-18 知识编译：生成decision_index                     │      │
│  │ - DP-S1-01~0N：各阶段关键决策                         │      │
│  │ - global_context_injection_summary（≤800 Token）      │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Agent角色定义

| Agent ID | 角色名称 | 框架 | 职责说明 | 特殊要求 |
|----------|---------|------|---------|---------|
| `agent_scene001_objectives_001` | 教学目标设计Agent | DeepAgents | 基于布鲁姆分类法设计分层学习目标，输出知识/能力/素质三维目标 | 绑定`tpl_scene001_objectives_v1.0` |
| `agent_scene001_methods_002` | 教学方法设计Agent | DeepAgents | 根据DP-CONT-01选择8种教学方法并分配权重 | 绑定`tpl_scene001_methods_v1.0` |
| `agent_scene001_structure_003` | 课程结构设计Agent | DeepAgents | 将目标映射为结构单元，设计课时分配与依赖关系 | 绑定`tpl_scene001_structure_v1.0` |
| `agent_scene001_evaluation_004` | 评估指标设计Agent | DeepAgents | 为每个节点设计评估指标，与节点绑定 | 绑定`tpl_scene001_evaluation_v1.0` |
| `agent_scene001_network_005` | 知识网络构建Agent | DeepAgents | 执行FR-05的三层节点拆分与边关系构建 | 绑定`tpl_scene001_network_v1.0` |

**协作模式**：Pipeline（顺序依赖，stage间需教师确认）

---

## 4. 输入/输出规格

### 4.1 场景输入规格

```yaml
scene001_planning_input:
  request_type: "course_planning"
  course_name: "初中数学：一元二次方程"
  course_desc: "面向初三学生，讲解一元二次方程的求解方法与实际应用"
  target_student_level: "初中三年级"
  target_student_count: 30
  total_periods: 12
  teacher_id: "teacher_001"
  
  optional_overrides:
    preferred_methods: ["讲授法", "探究法"]  # 教学方法偏好
    emphasis_nodes: ["建模能力培养"]          # 重点强调节点
    ideological_elements: true               # 是否需要思政融合
  
  context_hints:
    reference_kn_ids: []                    # 可选：借鉴已有知识网络
    previous_course_id: null                # 前置课程引用
```

### 4.2 Stage 1 输出规格

```yaml
stage1_output:
  stage: "stage1_objectives"
  agent_id: "agent_scene001_objectives_001"
  teacher_confirmed: false
  
  teaching_objectives:
    knowledge_objectives:
      - id: "ko_001"
        content: "理解一元二次方程的定义与一般形式ax²+bx+c=0（a≠0）"
        bloom_level: "understand"
      - id: "ko_002"
        content: "掌握直接开方法、配方法、公式法、因式分解法四种解法"
        bloom_level: "apply"
      - id: "ko_003"
        content: "理解判别式Δ=b²-4ac的几何意义"
        bloom_level: "understand"
    
    ability_objectives:
      - id: "ao_001"
        content: "能根据方程特征灵活选择最简解法"
        bloom_level: "analyze"
      - id: "ao_002"
        content: "能在实际情境中建立一元二次方程模型并求解"
        bloom_level: "create"
    
    quality_objectives:
      - id: "qo_001"
        content: "培养抽象概括能力和逻辑推理能力"
        bloom_level: "remember"
      - id: "qo_002"
        content: "通过数学史融入培养文化自信"
        bloom_level: "understand"
  
  teaching_methods:
    primary: ["讲授法", "探究法"]
    secondary: ["项目引领", "情境教学"]
    allocation:
      讲授法: 0.30
      探究法: 0.25
      项目引领: 0.20
      情境教学: 0.15
      其他: 0.10
  
  expected_bloom_distribution:
    remember: 0.10
    understand: 0.25
    apply: 0.30
    analyze: 0.20
    evaluate: 0.05
    create: 0.10
```

### 4.3 Stage 2 输出规格

```yaml
stage2_output:
  stage: "stage2_structure"
  agent_id: "agent_scene001_structure_003"
  teacher_confirmed: false
  
  course_structure:
    total_periods: 12
    units:
      - unit_id: "unit_01"
        title: "一元二次方程的概念与引入"
        periods: 2
        keywords: ["方程定义", "一般形式", "实际情境引入"]
        mapped_objectives: ["ko_001", "qo_002"]
        prerequisite_unit_ids: []
      
      - unit_id: "unit_02"
        title: "直接开方法与配方法"
        periods: 3
        keywords: ["开方法", "配方法", "完全平方"]
        mapped_objectives: ["ko_002", "ao_001"]
        prerequisite_unit_ids: ["unit_01"]
      
      - unit_id: "unit_03"
        title: "公式法与判别式"
        periods: 3
        keywords: ["求根公式", "判别式", "Δ的几何意义"]
        mapped_objectives: ["ko_002", "ko_003", "ao_001"]
        prerequisite_unit_ids: ["unit_02"]
      
      - unit_id: "unit_04"
        title: "因式分解法"
        periods: 2
        keywords: ["十字相乘", "因式分解"]
        mapped_objectives: ["ko_002"]
        prerequisite_unit_ids: ["unit_02"]
      
      - unit_id: "unit_05"
        title: "实际问题与建模"
        periods: 2
        keywords: ["方程建模", "实际应用", "检验"]
        mapped_objectives: ["ao_002", "qo_001"]
        prerequisite_unit_ids: ["unit_03", "unit_04"]
  
  unit_prerequisites:
    - from: "unit_01"
      to: "unit_02"
      type: "sequential"
    - from: "unit_02"
      to: "unit_03"
      type: "sequential"
    - from: "unit_02"
      to: "unit_04"
      type: "sequential"
    - from: "unit_03"
      to: "unit_05"
      type: "sequential"
    - from: "unit_04"
      to: "unit_05"
      type: "sequential"
```

### 4.4 Stage 3 输出规格（知识网络）

```yaml
stage3_output:
  stage: "stage3_network"
  agent_id: "agent_scene001_network_005"
  teacher_confirmed: false
  
  knowledge_network:
    kn_id: "kn_001"
    course_name: "初中数学：一元二次方程"
    version: "1.0"
    total_nodes: 15
    total_edges: 22
    
    nodes:
      - id: "concept_equation_essence_01"
        layer: "concept"
        title: "理解一元二次方程的本质"
        bloom_level: "analyze"
        difficulty: 4
        can_self_learn: false
        estimated_periods: 1
        mapped_unit: "unit_01"
        teaching_objectives:
          knowledge: ["理解一元二次方程的定义与一般形式"]
          ability: ["能判断一个方程是否为一元二次方程"]
          quality: ["培养抽象概括能力"]
        prerequisites: []
        related_tool_nodes: ["tool_formula_method_07"]
        related_skill_nodes: ["skill_method_selection_04"]
      
      # ... 其他节点（concept/skill/tool各层）
    
    edges:
      # 层内边
      - from: "concept_equation_essence_01"
        to: "concept_discriminant_meaning_02"
        relation_type: "is_prerequisite"
      
      # 跨层边
      - from: "concept_equation_essence_01"
        to: "skill_method_selection_04"
        relation_type: "supports_understanding"
      
      - from: "skill_method_selection_04"
        to: "tool_formula_method_07"
        relation_type: "enables_operation"
      
      # 同主题边
      - from: "concept_equation_essence_01"
        to: "skill_method_selection_04"
        relation_type: "same_topic_cross_layer"
    
    layer_distribution:
      concept_nodes_count: 5
      skill_nodes_count: 5
      tool_nodes_count: 5
    
    network_notes:
      entry_nodes: ["concept_equation_essence_01", "tool_formula_method_07"]
      convergence_nodes: ["skill_model_building_12"]
      multi_path_description: "学生可从概念层进入（理论导向），或从工具层进入（操作导向）"
    
    evaluation_metrics:
      - metric_id: "m_001"
        target_node: "concept_equation_essence_01"
        metric_type: "observational_scale"
        content: "学生能否正确判断一元二次方程并解释其一般形式的意义"
        scoring_rubric: "1-5分，5分=能独立完成并解释理由"
        expected_target_score: 4.0
```

### 4.5 最终产物输出规格

```yaml
scene001_final_output:
  scene_type: "SCENE-001"
  session_id: "sess_course_plan_2026_06_15_001"
  overall_status: "completed"
  
  stages_completed:
    - stage: "stage1_objectives"
      status: "confirmed"
      confirmed_at: "2026-06-15T10:15:00Z"
      teacher_id: "teacher_001"
    
    - stage: "stage2_structure"
      status: "confirmed"
      confirmed_at: "2026-06-15T10:30:00Z"
      teacher_id: "teacher_001"
    
    - stage: "stage3_network"
      status: "confirmed"
      confirmed_at: "2026-06-15T11:00:00Z"
      teacher_id: "teacher_001"
  
  artifacts:
    - type: "course_planning_yaml"
      path: "/sessions/sess_course_plan_2026_06_15_001/working/course_planning.yaml"
      version: "1.0"
    
    - type: "decision_index_json"
      path: "/sessions/sess_course_plan_2026_06_15_001/working/decision_index.json"
      dp_count: 15
    
    - type: "knowledge_network_yaml"
      path: "/knowledge_networks/kn_001.yaml"
      version: "1.0"
    
    - type: "evaluation_metrics_yaml"
      path: "/evaluation/kn_001_metrics.yaml"
      version: "1.0"
  
  total_tokens_used: 145000
  total_tokens_budget: 300000
  
  generated_at: "2026-06-15T11:05:00Z"
  generated_by: "fr03_orchestration_engine"
```

---

## 5. 与其他场景的数据流关系

| 方向 | 场景 | 数据内容 | 说明 |
|------|------|---------|------|
| **输出→** | SCENE-002 备课辅助 | `kn_001`, `decision_index` | 知识网络作为备课输入 |
| **输出→** | SCENE-003 虚拟教室 | `kn_001`, `decision_index` | 虚拟教室读取节点进行教学 |
| **输出→** | SCENE-005 节点推荐 | `kn_001` | 推荐引擎基于网络拓扑计算 |
| **输出→** | SCENE-009 网络维护 | `kn_001` | 维护优化的基础数据 |
| **输出→** | FR-12 持久化 | 全部产物 | 配置持久化存储 |
| **输出→** | FR-18 知识编译 | stage1~3产出 | 编译为decision_index |

---

## 6. 关键约束

| 约束类型 | 约束内容 | 来源 |
|---------|---------|------|
| **流程约束** | 三阶段必须顺序执行，每阶段需教师确认后方可进入下一阶段 | DP-ARCH-03 |
| **Token约束** | 决策索引≤300 Token/条，全局摘要≤800 Token | DP-ARCH-10 |
| **Harness约束** | 每个Agent必须绑定Harness模板，未绑定不得执行 | DP-ARCH-07 |
| **网络约束** | 三层节点每层≥1个，无孤立节点，边方向遵循规则 | FR-05 |
| **评估约束** | 评估指标必须在规划阶段设计，与节点绑定 | DP-ARCH-11 |
| **思政约束** | 思政融合在备课阶段设计，不在规划阶段强制要求 | DP-ARCH-08 |
| **迭代约束** | Agent重试≤3次，超过触发人工干预 | FR-03 |

---

## 7. 验收标准

| 验收项 | 验收条件 | 验证方式 |
|-------|---------|---------|
| **VA-001** | 对标准课程输入，可完成三阶段完整流程并产出知识网络 | 端到端集成测试 |
| **VA-002** | 知识网络包含≥3 concept + ≥3 skill + ≥3 tool节点 | Schema校验 |
| **VA-003** | 每阶段教师确认后进入下一阶段，未确认则阻塞 | 人机协同测试 |
| **VA-004** | 产出decision_index包含≥10条DP，总Token≤3000 | Token计数 |
| **VA-005** | Agent配置100%绑定Harness模板 | 配置校验 |
| **VA-006** | 边关系方向100%符合规范 | Schema自定义规则校验 |
| **VA-007** | 评估指标与节点100%绑定 | 引用完整性校验 |
| **VA-008** | 教师确认后产物持久化至FR-12，Git提交成功 | 存储校验 |
| **VA-009** | 无孤立节点（除入口/汇聚节点外） | 网络拓扑校验 |
| **VA-010** | 课程总课时与sum(unit_periods)偏差≤10% | 一致性校验 |

---

## 8. 文档变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|-----|------|---------|-------|
| v1.0 | 2026-06-15 | 初始版本 | EduAgents架构组 |

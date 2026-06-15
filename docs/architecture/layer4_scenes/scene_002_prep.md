# SCENE-002：备课辅助场景

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**场景编号**：SCENE-002  
**关联功能需求**：FR-05（知识网络）、FR-13（人机协同接口）、FR-15（Harness约束）、FR-16（思政融合设计）

---

## 1. 场景概述

**一句话描述**：基于SCENE-001产出的知识网络，系统为每个知识节点自动生成教案、学案、配套资源，并提供思政融合建议，经教师审核确认后写入教学包。

**参与角色**：
- 教师（教案/学案审阅者，思政融合审核者）
- 教案生成Agent（针对每个节点）
- 学案生成Agent（针对每个节点）
- 资源推荐Agent
- 思政融合Agent（FR-16）
- 人机协同接口Agent（FR-13）

---

## 2. 核心流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCENE-002 备课辅助核心流程                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  输入来源                                                               │
│  ┌──────────────┐                                                        │
│  │ SCENE-001    │  knowledge_network (kn_001)                            │
│  │ 课程规划产出 │  decision_index                                          │
│  └──────┬───────┘  evaluation_metrics                                      │
│         │                                                                  │
│         ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    备课辅助主流程                                      │   │
│  │                                                                     │   │
│  │  ┌───────────────────────────────────────────────────────────────┐ │   │
│  │  │ for each node in knowledge_network.nodes:                     │ │   │
│  │  │                                                               │ │   │
│  │  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │ │   │
│  │  │   │  教案生成   │  │  学案生成   │  │  资源推荐   │         │ │   │
│  │  │   │   Agent     │  │   Agent     │  │   Agent     │         │ │   │
│  │  │   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │ │   │
│  │  │          │                │                │                  │ │   │
│  │  │          └────────────────┼────────────────┘                  │ │   │
│  │  │                           ▼                                    │ │   │
│  │  │               ┌─────────────────────────┐                     │ │   │
│  │  │               │  FR-15 Harness 校验     │                     │ │   │
│  │  │               │  schema + 内容边界检查   │                     │ │   │
│  │  │               └───────────┬─────────────┘                     │ │   │
│  │  │                           │                                    │ │   │
│  │  │          ┌────────────────┴────────────────┐                  │ │   │
│  │  │          ▼                                 ▼                  │ │   │
│  │  │   [校验通过]                         [校验失败]                │ │   │
│  │  │        │                                 │                     │ │   │
│  │  │        │                          重试（≤3次）                 │ │   │
│  │  │        │                                 │                     │ │   │
│  │  │        └─────────────────────────────────┘                     │ │   │
│  │  │                                                               │ │   │
│  │  │   ┌───────────────────────────────────────────────────────────┐ │   │
│  │  │   │ 思政融合建议生成（FR-16）                                  │ │   │
│  │  │   │ - ideological_element                                    │ │   │
│  │  │   │ - integration_method                                      │ │   │
│  │  │   │ - classroom_activity                                     │ │   │
│  │  │   │ - time_allocation                                        │ │   │
│  │  │   └───────────────────────────┬───────────────────────────────┘ │   │
│  │  │                               │                               │   │
│  │  │   ┌───────────────────────────┴───────────────────────────────┐ │   │
│  │  │   │  FR-13 人机协同：教师审阅每个节点的教学包                   │ │   │
│  │  │   │  教师操作：approve / approve_with_comments / revise / reject│ │   │
│  │  │   └───────────────────────────┬───────────────────────────────┘ │   │
│  │  │                               │                               │   │
│  │  └───────────────────────────────┼───────────────────────────────┘ │   │
│  │                                  │                                  │   │
│  └──────────────────────────────────┼──────────────────────────────────┘   │
│                                     │                                         │
│                                     ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 思政融合二次确认（FR-16 Double Confirmation）                         │   │
│  │ 1. 教师审核通过后，系统询问："是否将此思政建议写入教案？"              │   │
│  │ 2. 教师点击"确认写入"后，内容方才写入teaching_package                │   │
│  │ 3. 写入操作记录至审计日志                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  输出                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ teaching_package:                                                   │   │
│  │   - node_id/teaching_plan.yaml  (教案)                              │   │
│  │   - node_id/student_activity.yaml  (学案)                           │   │
│  │   - node_id/resources.yaml  (资源清单)                              │   │
│  │   - node_id/ideological_integration.yaml  (思政建议，待写入)        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Agent角色定义

| Agent ID | 角色名称 | 框架 | 职责说明 | 特殊要求 |
|----------|---------|------|---------|---------|
| `agent_scene002_teaching_plan_001` | 教案生成Agent | DeepAgents | 为每个节点生成标准教案 | 绑定`tpl_scene002_plan_v1.0` |
| `agent_scene002_student_activity_002` | 学案生成Agent | DeepAgents | 为每个节点生成学生自主学习材料 | 绑定`tpl_scene002_activity_v1.0` |
| `agent_scene002_resources_003` | 资源推荐Agent | DeepAgents | 推荐与节点配套的教学资源 | 绑定`tpl_scene002_resources_v1.0` |
| `agent_scene002_ideological_004` | 思政融合Agent | DeepAgents | 生成思政融合建议（FR-16） | 绑定`tpl_scene002_ideological_v1.0` |

**协作模式**：Node-level Parallel（同一节点的教案/学案/资源并行生成，节点间顺序处理）

---

## 4. 输入/输出规格

### 4.1 场景输入规格

```yaml
scene002_prep_input:
  request_type: "lesson_prep"
  knowledge_network_ref: "kn_001"
  decision_index_ref: "/sessions/sess_001/working/decision_index.json"
  target_nodes: ["all"]  # 或指定节点ID列表
  
  teacher_preferences:
    plan_format: "standard"  # standard / detailed / brief
    include_ideological: true
    resource_types: ["video", "worksheet", "game"]
  
  context_hints:
    class_duration_minutes: 45
    student_level: "初中三年级"
    class_size: 30
```

### 4.2 教案输出规格（per node）

```yaml
teaching_plan:
  node_id: "concept_equation_essence_01"
  version: "1.0"
  
  header:
    unit: "unit_01"
    topic: "一元二次方程的概念与引入"
    periods: 1
    class_duration: 45
  
  teaching_objectives:
    knowledge: "理解一元二次方程的定义与一般形式ax²+bx+c=0（a≠0）"
    ability: "能判断一个方程是否为一元二次方程"
    quality: "培养抽象概括能力"
  
  teaching_methods:
    primary: "讲授法"
    secondary: ["问答法", "演示法"]
  
  teaching_process:
    - phase: "导入"
      duration_minutes: 5
      activities:
        - type: "情境引入"
          description: "展示实际问题：'一块正方形花园面积为16m²，边长是多少？'"
          teacher_action: "提问引导"
          student_action: "思考回答"
    
    - phase: "新授"
      duration_minutes: 25
      activities:
        - type: "概念讲解"
          description: "从实际问题抽象出一元二次方程的一般形式"
          teacher_action: "讲授+板书"
          student_action: "记笔记"
        - type: "师生问答"
          description: "判断下列方程是否为一元二次方程：x²-3x+2=0, x³+1=0, (x-1)²=4"
          teacher_action: "追问"
          student_action: "抢答"
    
    - phase: "练习"
      duration_minutes: 10
      activities:
        - type: "随堂练习"
          description: "完成学案中练习1-5"
          teacher_action: "巡视"
          student_action: "独立完成"
    
    - phase: "小结"
      duration_minutes: 5
      activities:
        - type: "总结"
          description: "梳理本节要点"
          teacher_action: "引导"
          student_action: "发言"
  
  resources:
    - type: "worksheet"
      id: "res_ws_001"
      name: "一元二次方程概念练习题"
    - type: "video"
      id: "res_vd_001"
      name: "数学史：方程的演变"
  
  assessment:
    method: "课堂问答+随堂练习"
    criteria: "正确判断5道题中至少4道"
  
  teacher_notes: ""
  
  ideological_integration_ref:  # 待写入确认
    suggestion_id: "ideol_sugg_n001_001"
    status: "pending_write_confirmation"
```

### 4.3 学案输出规格（per node）

```yaml
student_activity:
  node_id: "concept_equation_essence_01"
  version: "1.0"
  
  header:
    unit: "unit_01"
    topic: "一元二次方程的概念与引入"
    periods: 1
    self_learning_duration: 20
  
  self_learning_objectives:
    - "能说出什么是一元二次方程"
    - "能判断一个方程是否为一元二次方程"
    - "能举出生活中一元二次方程的实际例子"
  
  activities:
    - section: "预习任务"
      duration_minutes: 10
      items:
        - type: "reading"
          content: "阅读教材第48-50页，划出关键定义"
        - type: "question"
          content: "预习后思考：一元二次方程与一元一次方程的区别是什么？"
    
    - section: "课堂学习任务"
      items:
        - type: "guided_note"
          template: |
            一元二次方程的定义：
            ________________________________________________
            
            一般形式：________________（其中a_____，b_____，c_____）
            
            练习：判断下列方程是否为一元二次方程：
            1. x² + 2x + 1 = 0    （    ）
            2. x³ - 4x = 0       （    ）
            3. 2x² - 5 = 0       （    ）
        
        - type: "practice"
          problems:
            - "判断：x² + 1 = 0 是否为一元二次方程？说明理由"
            - "编写一道一元二次方程的实际问题情境"
    
    - section: "课后巩固"
      items:
        - type: "homework"
          problems: 5
          difficulty_distribution: [2, 3, 3, 4, 4]
  
  self_assessment:
    questions:
      - "本节内容我已经理解：□ 是  □ 否"
      - "我能够判断一元二次方程：□ 熟练  □ 基本可以  □ 还需要练习"
      - "我在本节的最大收获是：________________"
```

### 4.4 思政融合建议规格（FR-16）

```yaml
ideological_integration_suggestion:
  suggestion_id: "ideol_sugg_concept_essence_01_001"
  node_id: "concept_equation_essence_01"
  teacher_id: "teacher_001"
  generated_at: "2026-06-15T14:00:00Z"
  
  ideological_element:
    category: "数学文化与数学史"
    keywords: ["一元二次方程的历史", "中国古代数学成就", "文化自信"]
    description: |
      通过介绍中国古代数学典籍中对一元二次方程（如《九章算术》
      中的'少广'章）的早期研究，让学生了解中国数学历史成就，
      培养文化自信
  
  integration_method: "课堂讨论 + 案例分享"
  
  integration_points:
    - location: "概念引入环节"
      timing_minutes: 3
      description: "在引入一般形式前，用3分钟介绍中国古代数学家的相关成就"
  
  classroom_activity:
    activity_type: "short_sharing"
    duration_minutes: 5
    content: "让2-3名学生课前预习资料，课堂上简要分享中国古代数学家的一项相关成就"
    materials: ["简要资料：《九章算术》少广章摘录（1页）"]
  
  time_allocation:
    total_in_class_minutes: 8
    percentage_of_node_time: 0.10  # 10%
  
  evaluation:
    type: "participation_observation"
    description: "通过课堂分享的参与度评估，不额外设置考试分值"
  
  review_status: "pending"  # pending / approved / rejected / revised
  teacher_comments: null
  teacher_confirmed_for_write: false  # 二次确认标志
  
  harness_content_verification: "passed"
```

### 4.5 最终产物输出规格

```yaml
scene002_final_output:
  scene_type: "SCENE-002"
  session_id: "sess_prep_2026_06_15_001"
  knowledge_network_ref: "kn_001"
  
  nodes_processed: 15
  nodes_confirmed: 15
  
  teaching_packages:
    - node_id: "concept_equation_essence_01"
      teaching_plan: "/sessions/sess_prep_2026_06_15_001/teaching_packages/concept_equation_essence_01/teaching_plan.yaml"
      student_activity: "/sessions/sess_prep_2026_06_15_001/teaching_packages/concept_equation_essence_01/student_activity.yaml"
      resources: "/sessions/sess_prep_2026_06_15_001/teaching_packages/concept_equation_essence_01/resources.yaml"
      ideological_integration:
        included: true
        confirmed_for_write: true
        write_timestamp: "2026-06-15T14:30:00Z"
    
    # ... 其他节点
  
  ideological_summary:
    total_suggestions_generated: 12
    total_approved: 10
    total_rejected: 2
    total_pending_write: 0  # 所有已批准均已确认写入
  
  artifacts_persisted:
    - type: "teaching_package_directory"
      path: "/teaching_packages/kn_001/v1.0/"
      version: "1.0"
  
  generated_at: "2026-06-15T15:00:00Z"
  generated_by: "fr03_orchestration_engine"
```

---

## 5. 与其他场景的数据流关系

| 方向 | 场景/FR | 数据内容 | 说明 |
|------|---------|---------|------|
| **输入←** | SCENE-001 | `kn_001`, `decision_index`, `evaluation_metrics` | 课程规划的产出作为备课输入 |
| **输入←** | FR-16 | 思政融合设计流程 | 生成思政融合建议 |
| **输出→** | SCENE-003 | `teaching_package` | 虚拟教室使用教案/学案 |
| **输出→** | FR-12 | 教学包持久化 | 配置持久化存储 |
| **触发→** | FR-13 | 教师审阅流程 | 人机协同确认 |
| **思政输出→** | FR-14 | 写入确认记录 | 审计日志记录 |

---

## 6. 关键约束

| 约束类型 | 约束内容 | 来源 |
|---------|---------|------|
| **思政约束** | 思政建议必须通过教师explicit写入确认后方可进入教学包 | DP-ARCH-08 + FR-16 |
| **思政时间约束** | 思政内容不超过节点总课时15% | FR-16 |
| **内容约束** | 教案/学案内容必须与知识网络节点的教学目标一致 | FR-05 |
| **Harness约束** | 所有输出必须通过三阶段校验管道 | DP-ARCH-07 |
| **资源约束** | 推荐资源必须可访问且与节点相关 | FR-16 |
| **审核约束** | 每个节点的教学包需教师逐个确认 | FR-13 |
| **版本约束** | 备课产出版本与知识网络版本绑定 | FR-12 |

---

## 7. 验收标准

| 验收项 | 验收条件 | 验证方式 |
|-------|---------|---------|
| **VA-001** | 对15个节点的知识网络，可生成15份完整教学包 | 端到端测试 |
| **VA-002** | 思政建议未经教师写入确认，不出现在教案中 | 二次确认流程测试 |
| **VA-003** | 教案 teaching_process 包含导入/新授/练习/小结 四个环节 | Schema校验 |
| **VA-004** | 学案 self_learning_objectives 与节点 teaching_objectives 一致 | 内容一致性校验 |
| **VA-005** | 思政时间占比≤15% | 计算校验 |
| **VA-006** | 所有教案/学案通过Harness schema校验 | 校验管道测试 |
| **VA-007** | 资源推荐包含可访问路径或外部链接 | 可访问性校验 |
| **VA-008** | 每个节点教师审阅率100% | 人机协同日志校验 |
| **VA-009** | 教学包正确持久化至FR-12指定路径 | 存储校验 |
| **VA-010** | 思政建议通过Harness内容边界过滤 | 内容过滤测试 |

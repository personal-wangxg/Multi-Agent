# SCENE-008：教学评估场景

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**场景编号**：SCENE-008  
**关联功能需求**：FR-10（教学评估）、FR-11（网络维护触发）

---

## 1. 场景概述

**一句话描述**：课程/单元结束后，使用规划阶段设计的评估指标体系，结合多源过程数据，对教学效果进行系统性评估，产出反思报告与可操作的改进建议。

**参与角色**：
- 指标解析Agent
- 数据收集Agent
- 教学评估Agent
- 反思引导Agent
- 改进建议Agent
- 教师确认Agent

---

## 2. 核心流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCENE-008 教学评估核心流程                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  触发条件                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. 单元结束（end_of_unit）：完成unit_03后自动触发                     │   │
│  │ 2. 课程结束（course_end）：完成全部单元后触发                         │   │
│  │ 3. 期中评估（midterm_review）：学期中手动触发                        │   │
│  │ 4. 教师手动触发：教师可随时发起评估                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                             │                                                 │
│                             ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      评估主流程                                      │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 1. 指标解析Agent                                              │  │   │
│  │  │    - 从 evaluation_metrics_ref 读取规划阶段设计的指标         │  │   │
│  │  │    - 提取每个 metric 的 target_node、type、rubric              │  │   │
│  │  │    - 验证指标完整性                                            │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 2. 数据收集Agent                                              │  │   │
│  │  │    - observational_scale → 读取SCENE-003课堂表现              │  │   │
│  │  │    - written_test → 读取SCENE-006作业批改                    │  │   │
│  │  │    - project_rubric → 读取SCENE-002项目作品                   │  │   │
│  │  │    - 聚合全班数据形成统计量                                    │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 3. 教学评估Agent                                              │  │   │
│  │  │    - 按 rubric 为每个 metric 打出 achieved_score              │  │   │
│  │  │    - 对比 expected_target_score                               │  │   │
│  │  │    - 附结构化 supporting_evidence                             │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 4. 反思引导Agent                                              │  │   │
│  │  │    - 汇总整体评估 → overall_rating                            │  │   │
│  │  │    - 分析 strengths 和 areas_for_improvement                  │  │   │
│  │  │    - 提出引导性反思问题（供教师填写）                          │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 5. 改进建议Agent                                              │  │   │
│  │  │    - 对 below_target 指标生成建议                             │  │   │
│  │  │    - 每条含 target_node / suggestion / expected_impact        │  │   │
│  │  │    - 建议可反馈至 SCENE-002 / FR-11                          │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  └───────────────────────────────┼─────────────────────────────────────┘   │
│                                  │                                          │
│                                  ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      教师确认（FR-13）                                │   │
│  │                                                                      │   │
│  │  教师可：                                                           │   │
│  │  - 调整分数                                                         │   │
│  │  - 补充反思                                                         │   │
│  │  - 修改建议                                                         │   │
│  │  - 确认报告正式归档                                                  │   │
│  │                                                                      │   │
│  │  teacher_confirmed = true 后，报告正式生效                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Agent角色定义

| Agent ID | 角色名称 | 框架 | 职责说明 | 特殊要求 |
|----------|---------|------|---------|---------|
| `agent_scene008_metrics_parser_001` | 指标解析Agent | DeepAgents | 解析规划阶段设计的评估指标 | 绑定`tpl_scene008_metrics_v1.0` |
| `agent_scene008_data_collector_002` | 数据收集Agent | DeepAgents | 从多源收集评估证据 | 绑定`tpl_scene008_collector_v1.0` |
| `agent_scene008_evaluator_003` | 教学评估Agent | DeepAgents | 评定指标得分，生成证据 | 绑定`tpl_scene008_evaluator_v1.0` |
| `agent_scene008_reflection_004` | 反思引导Agent | DeepAgents | 生成整体评估与反思问题 | 绑定`tpl_scene008_reflection_v1.0` |
| `agent_scene008_suggestion_005` | 改进建议Agent | DeepAgents | 生成可操作的改进建议 | 绑定`tpl_scene008_suggestion_v1.0` |

**协作模式**：Sequential（解析→收集→评估→反思→建议）

---

## 4. 输入/输出规格

### 4.1 场景输入规格

```yaml
scene008_evaluation_input:
  request_type: "teaching_evaluation"
  
  evaluation_scope: "unit_end"  # course_end / unit_end / midterm_review
  unit_or_course_ref: "unit_03"
  course_ref: "kn_001"
  
  knowledge_network_ref: "kn_001"
  
  evaluation_metrics_ref: "/data/eval/kn_001_evaluation_metrics.yaml"
  
  data_sources:
    - type: "virtual_classroom_summary"
      ref: "/data/vc/summary_kn001_unit03.yaml"
    
    - type: "homework_grading_class_summaries"
      ref: "/data/hw/class_summary_unit03.yaml"
    
    - type: "learning_analytics_reports"
      ref: "/data/analytics/analytics_20260615_001.yaml"
    
    - type: "teacher_feedback_from_harness"
      ref: "/data/feedback/teacher_feedback_unit03.yaml"
  
  teacher_id: "teacher_001"
  
  teacher_self_reflection: |
    "学生在建模题上表现较弱，可能我在课堂上的建模案例不够多。
    下次备课时应增加更多实际情境的建模练习。"
  
  context_hints:
    previous_evaluation_id: null  # 如有前序评估
```

### 4.2 教学评估报告输出

```yaml
teaching_evaluation_report:
  report_id: "teach_eval_20260615_001"
  scope: "unit_end"
  unit_ref: "unit_03"
  course_ref: "kn_001"
  
  teacher_id: "teacher_001"
  generated_at: "2026-06-15T18:30:00Z"
  
  evaluation_summary:
    metrics_total: 5
    metrics_evaluated: 5
    metrics_meets_target: 3
    metrics_below_target: 1
    metrics_exceeds_target: 1
  
  # ========== 指标评估详情 ==========
  metric_evaluations:
    - metric_id: "m_001"
      target_node: "concept_equation_essence_01"
      metric_type: "observational_scale"
      
      content: "学生能否正确判断一元二次方程并解释其一般形式的意义"
      
      scoring_rubric: "1-5分，5分=能独立完成并解释理由"
      max_score: 5
      achieved_score: 4.2
      target_score: 4.0
      
      status: "meets_target"  # meets_target / below_target / exceeds_target
      
      supporting_evidence:
        - "全班75%学生能独立解释一般形式"
        - "SCENE-003课堂问答中，68%学生能主动指出方程定义条件"
        - "相关作业正确率78%"
        - "教师观察：大部分学生在概念引入环节表现积极"
      
      improvement_notes: |
        加强对'为什么需要一般形式ax²+bx+c=0（a≠0）'的讨论，
        可结合数学史融入
  
    - metric_id: "m_002"
      target_node: "skill_model_building_12"
      metric_type: "project_rubric"
      
      content: "学生能否在实际情境中正确建立一元二次方程模型并求解"
      
      scoring_rubric: |
        按建模过程正确性（40%）/求解过程（30%）/合理性检验（20%）/反思总结（10%）评分
      max_score: 5
      achieved_score: 3.2
      target_score: 4.0
      
      status: "below_target"
      
      supporting_evidence:
        - "全班平均建模得分3.2/5"
        - "主要失分点：情境→方程的转化错误（43%学生在此丢分）"
        - "错题闭环在该节点的平均触发次数2.1次/学生"
        - "SCENE-007学情分析显示该节点hotness_level为hot"
      
      improvement_notes: |
        需增加课堂建模案例；采用'教师示范→学生小练→互评'的渐进式训练方式
  
    - metric_id: "m_003"
      target_node: "tool_formula_method_07"
      metric_type: "written_test"
      
      content: "学生能否熟练使用公式法求解标准形式的一元二次方程"
      
      scoring_rubric: "结果正确4分；有小错误3分；结果错但公式正确1分"
      max_score: 5
      achieved_score: 4.3
      target_score: 4.0
      
      status: "exceeds_target"
      
      supporting_evidence:
        - "相关作业正确率92%"
        - "该节点首次尝试即掌握率85%"
        - "平均耗时低于估计课时15%"
        - "学生反馈：公式法是最容易掌握的解法"
      
      improvement_notes: |
        考虑给优秀学生增加含参数的变式题，保持挑战性
  
  # ========== 整体总结 ==========
  overall_summary:
    overall_rating: 3.9  # 综合评分（0-5）
    
    strengths:
      - "工具层训练效果良好（平均掌握率83%）"
      - "概念层入门清晰，多数学生能理解基本定义（75%学生能独立解释）"
      - "错题闭环有效帮助学生纠正计算错误"
      - "公式法教学效果超出预期"
    
    areas_for_improvement:
      - "技能应用（尤其是情境建模）是班级主要薄弱环节"
      - "从工具层到技能层的跃迁衔接不畅，30%学生在此节点停留超过2倍预期课时"
      - "概念层与技能层的课堂整合不足，学生感知为两个独立主题"
  
  # ========== 改进建议 ==========
  concrete_improvement_suggestions:
    - id: "imp_001"
      target_node: "skill_model_building_12"
      suggestion: |
        增加2-3个完整课堂建模案例；采用'教师示范→小组合作建模→全班展示→同伴评价'的流程；
        配套训练题难度逐步提升
      expected_impact: "该节点掌握率从42%提升至75%+"
      priority: "high"
      
      feedback_to_scenes:
        - system: "SCENE-002 备课辅助"
          content: "下一单元的备课请考虑在技能层增加建模案例与渐进式训练"
        - system: "FR-11 网络维护"
          content: "建议拆分skill_model_building_12节点为2个难度递进的子节点"
        - system: "SCENE-009 网络维护"
          content: "在概念层与技能层间增加过渡节点"
    
    - id: "imp_002"
      target_node: "概念_技能跨层衔接"
      suggestion: |
        在concept_equation_essence_01和skill_method_selection_04之间新增1个过渡实践节点，
        让学生在掌握概念后立即进行中等难度的方法选择训练
      expected_impact: "减少学生进入技能层的挫败感，提升衔接顺畅度"
      priority: "medium"
      
      feedback_to_scenes:
        - system: "SCENE-009 网络维护"
          content: "新增transition_node建议：tool_to_skill_practice_07.5"
  
  # ========== 教师反思（教师填写） ==========
  teacher_self_reflection: |
    "学生在建模题上表现较弱，可能我在课堂上的建模案例不够多。
    下次备课时应增加更多实际情境的建模练习。
    我计划在下一单元增加2课时的建模专题训练。"
  
  teacher_review:
    reviewed: false
    score_adjustments: []
    additional_comments: null
  
  # ========== 反哺闭环 ==========
  automatic_feedback_to_systems:
    - system: "SCENE-002 备课辅助"
      content: "下一单元的备课请考虑在技能层增加建模案例与渐进式训练"
      triggered_at: "2026-06-15T18:35:00Z"
    
    - system: "FR-11 知识网络动态维护"
      content: "建议拆分skill_model_building_12节点为2个难度递进的子节点"
      triggered_at: "2026-06-15T18:35:00Z"
    
    - system: "SCENE-009 网络维护"
      content: "在概念层与技能层间增加过渡节点"
      triggered_at: "2026-06-15T18:35:00Z"
```

### 4.3 最终产物输出规格

```yaml
scene008_final_output:
  scene_type: "SCENE-008"
  report_id: "teach_eval_20260615_001"
  
  scope: "unit_end"
  unit_ref: "unit_03"
  course_ref: "kn_001"
  
  evaluation_completed_at: "2026-06-15T18:30:00Z"
  
  status: "awaiting_teacher_confirmation"  # awaiting_confirmation / confirmed
  
  metrics_summary:
    total: 5
    meets_target: 3
    below_target: 1
    exceeds_target: 1
  
  overall_rating: 3.9
  
  suggestions_count: 2
  suggestions_priorities:
    high: 1
    medium: 1
    low: 0
  
  feedback_triggered:
    scene002_prep: true
    scene009_maintenance: true
    fr11_network: true
  
  artifacts_persisted:
    - type: "teaching_evaluation_report"
      path: "/teaching_eval/kn_001/teach_eval_20260615_001.yaml"
      version: "1.0"
  
  generated_at: "2026-06-15T18:35:00Z"
  generated_by: "fr10_teaching_evaluation_engine"
```

---

## 5. 与其他场景的数据流关系

| 方向 | 场景/FR | 数据内容 | 说明 |
|------|---------|---------|------|
| **输入←** | SCENE-001 | 评估指标定义 | 规划阶段设计的指标 |
| **输入←** | SCENE-003 | 课堂表现数据 | observational_scale证据 |
| **输入←** | SCENE-006 | 作业批改数据 | written_test证据 |
| **输入←** | SCENE-007 | 学情分析数据 | 综合分析证据 |
| **输出→** | SCENE-002 | 备课调整建议 | 改进反馈 |
| **输出→** | SCENE-009 | 网络优化建议 | 触发维护 |
| **输出→** | FR-12 | 评估报告持久化 | 存档 |

---

## 6. 关键约束

| 约束类型 | 约束内容 | 来源 |
|---------|---------|------|
| **指标约束** | 必须使用规划阶段设计的指标，不允许新增 | FR-10 |
| **证据约束** | 所有得分必须附可追溯的evidence | FR-10 |
| **建议约束** | below_target指标必须≥1条建议 | FR-10 |
| **时间约束** | 报告生成≤5分钟 | FR-10 |
| **确认约束** | teacher_confirmed=true后正式归档 | FR-10 |

---

## 7. 验收标准

| 验收项 | 验收条件 | 验证方式 |
|-------|---------|---------|
| **VA-001** | 对≥5个指标的标准输入可完整输出报告 | 端到端测试 |
| **VA-002** | below_target指标≥1条改进建议 | 内容校验 |
| **VA-003** | 建议自动反馈至SCENE-002和FR-11 | 数据流测试 |
| **VA-004** | 所有achieved_score附supporting_evidence | 证据校验 |
| **VA-005** | 教师可修改分数/补充反思 | 人机协同测试 |
| **VA-006** | teacher_confirmed后报告正式归档 | 流程测试 |

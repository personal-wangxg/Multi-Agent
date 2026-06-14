# DP-ARCH-11：教学评估指标在课程规划阶段设计

**确认日期**：2026-06-12 · **确认人**：项目核心团队 · **决策类别**：架构

---

## 决策摘要

教学评估指标**不是事后补做，而是在课程规划阶段（SCENE-001）与知识网络（FR-05）关联设计**。每个评估项与知识网络的具体节点绑定（可精确到概念层 / 技能层 / 工具层）。SCENE-008 教学评估场景使用 SCENE-001 中产出的同一套指标进行评估，确保评估与教学目标一致。

## 核心设计原则

1. **评估指标与知识网络节点绑定，可追溯到节点层级（概念/技能/工具，
2. **指标在课程规划阶段生产，贯穿 stage1/2/3 同步产出，
3. **SCENE-008 使用 SCENE-001 产出的同一套指标进行评估，不重新设计，
4. **评估指标结构化保存，可被教学评估 Agent 自动读取，
5. **教学评估结果反哺备课优化，形成闭环。

## 关键细节

### 评估指标在 SCENE-001 中的产出位置

| 阶段 | 评估指标的产出内容 | 与节点关系 |
|-----|-------------------|-----------|
| stage1：教学目标设计 | 与 knowledge_goals / ability_goals / quality_goals 对应 | 节点层面评估指标的雏形 |
| stage2：课程结构 | 与每个 unit 的 teaching_method 匹配的观测点 | 单元层面观测点 |
| stage3：知识网络 | 与每个 node 绑定的评估项 | 节点层面具体指标 |

### evaluation_metrics 数据结构（SCENE-001 输出）

```yaml
evaluation_metrics:
  - metric_id: "m_001"
    target_node: "concept_equation_essence"         # 绑定到具体节点
    metric_type: "observational_scale"               # observational_scale / written_test / project_rubric / interview
    content: "学生能否正确判断一元二次方程并解释其一般形式的意义"
    observation_target: "课堂表现 + 课堂小检测"
    scoring_rubric: "1-5分，5分=能独立完成并解释理由"
    bloom_level: "understand"
    node_layer: "concept"                             # concept / skill / tool

  - metric_id: "m_002"
    target_node: "skill_model_building"
    metric_type: "project_rubric"
    content: "学生能否在实际情境中正确建立一元二次方程模型并求解"
    observation_target: "项目作品 + 书面作业"
    scoring_rubric: "按建模过程/求解过程/合理性检验/反思总结四维度评分"
    bloom_level: "create"
    node_layer: "skill"

  - metric_id: "m_003"
    target_node: "tool_formula_method"
    metric_type: "written_test"
    content: "学生能否正确使用公式法求解一元二次方程"
    observation_target: "课堂小检测 + 作业"
    scoring_rubric: "正确率 ≥ 80% 为掌握"
    bloom_level: "apply"
    node_layer: "tool"
```

### SCENE-008 与 SCENE-001 的指标复用

```
SCENE-001（课程规划）
   │
   └→ 产出 evaluation_metrics 数组（与节点绑定）
         │
         ▼
   写入 VFS / decision_index.json 中的 DP
         │
         ▼
SCENE-008（教学评估）
   │
   ├─ 步骤 1：从 SCENE-001 产物中提取 evaluation_metrics
   │
   ├─ 步骤 2：从 SCENE-003/004/006/007 收集评估数据
   │
   ├─ 步骤 3：对照指标逐项评定，生成教学评估报告
   │
   └→ 产出：teaching_evaluation_report（含 achieved_score / max_score / target_score / status）
```

### SCENE-008 输出示例（摘要）

```yaml
teaching_evaluation_report:
  report_id: "teach_eval_001"
  metric_evaluations:
    - metric_id: "m_001"
      achieved_score: 4.2
      max_score: 5
      target_score: 4.0
      status: "meets_target"
      supporting_evidence:
        - "全班 75% 学生能独立解释一般形式"
        - "课堂讨论表现良好"
    - metric_id: "m_002"
      achieved_score: 3.2
      max_score: 5
      target_score: 4.0
      status: "below_target"
      supporting_evidence:
        - "建模题平均正确率 58%"
  overall_summary:
    overall_rating: 3.8
    strengths: ["工具层教学高效", "思政融合执行到位"]
    areas_for_improvement: ["技能层节点教学方法需改进", "跨层推进节奏过快"]
  concrete_improvement_suggestions:
    - id: "imp_001"
      target_node: "skill_model_building"
      suggestion: "增加 2-3 个完整课堂建模案例，让学生自己出题并互相评价"
      expected_impact: "技能层节点掌握率提升至 80%+"
  teacher_confirmed: false
```

## 影响范围

- 关联 FR：FR-05（立体分层知识网络）、FR-10（教学评估）、FR-18（知识编译）；
- 关联场景：SCENE-001（课程规划）、SCENE-008（教学评估）；
- 关联产物：course_planning.evaluation_metrics、teaching_evaluation_report。

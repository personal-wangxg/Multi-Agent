# SCENE-008：教学评估

**父文档**：[system_requirements.md](../../system_requirements.md) · [场景索引](../03_user_roles_scenes_index.md)
**相关决策**：[dp_arch_11](../../decisions/dp_arch_11.md)

---

### 3.2.8 SCENE-008：教学评估（课程/单元末）

**场景目标**：使用课程规划阶段（SCENE-001）设计的评估指标，对教师的教学过程进行系统评估，生成反思报告与改进建议，服务教师专业成长。

**核心设计原则**：
1. **指标来源于课程规划**
2. **关注过程而非只看结果**
3. **数据来源于多个场景**（虚拟教室、作业批改、学情分析等）
4. **强调反思与成长**（不是给教师打分排名）

#### Agent 角色定义

| Agent 角色 | 框架 | 数量 | 职责边界 |
|-----------|------|------|---------|
| 指标解析 Agent | DeepAgents | 1 | 从 SCENE-001 输出提取评估指标与评分标准 |
| 数据收集 Agent | DeepAgents | 1 | 从各场景汇总教学相关数据 |
| 教学评估 Agent | DeepAgents | 1 | 对照评估指标逐项评定，生成评估报告 |
| 反思引导 Agent | DeepAgents | 1 | 生成教师反思问题与改进建议 |

#### 输出规格（摘要版）

```yaml
teaching_evaluation_report:
  report_id: "teach_eval_001"
  metric_evaluations:
    - metric_id: "m_001"
      achieved_score: 3.5
      max_score: 5
      target_score: 4.0
      status: "below_target"
      supporting_evidence:
        - "全班60%学生掌握技能层节点（目标80%）"
        - "建模题平均正确率58%"
  overall_summary:
    overall_rating: 3.8
    strengths: ["工具层节点教学高效", "思政元素融合执行到位", "虚拟教室提升参与度"]
    areas_for_improvement: ["技能层节点教学方法需改进", "跨层推进节奏过快"]
  concrete_improvement_suggestions:
    - id: "imp_001"
      priority: "high"
      target_node: "skill_model_solve_system"
      suggestion: "增加2-3个完整课堂建模案例；让学生自己出题并互相评价；在虚拟教室中增加'多策略讨论'环节"
      expected_impact: "技能层节点掌握率提升至80%+"
  teacher_confirmed: false
```

#### 边界与异常

| 异常场景 | 系统行为 |
|---------|---------|
| 未找到 SCENE-001 定义的评估指标 | 提示 ERR-METRIC-001，提供空模板让教师手动填写 |
| 数据来源中某类数据缺失 | 标记"数据不足"，降低该指标权重，在最终评估中注明 |
| Token 超预算 | 生成精简版报告（仅核心指标评分 + Top3 改进建议） |

---


# SCENE-007：学情分析

**父文档**：[system_requirements.md](../../system_requirements.md) · [场景索引](../03_user_roles_scenes_index.md)
**相关决策**：[dp_arch_09](../../decisions/dp_arch_09.md), [dp_arch_04](../../decisions/dp_arch_04.md)

---

### 3.2.7 SCENE-007：学情分析

**场景目标**：基于学生在各节点的学习数据，生成单个学生的**学习画像**和班级的**学习热力图**与**薄弱环节分析**。

**核心设计原则**：
1. **数据驱动**：所有分析基于真实学习数据
2. **与知识网络关联**：分析结果定位到具体节点
3. **自动化**：学生每次完成学习活动后自动更新

#### Agent 角色定义

| Agent 角色 | 框架 | 数量 | 职责边界 |
|-----------|------|------|---------|
| 数据聚合 Agent | DeepAgents | 1 | 从 SCENE-003/004/006 汇总所有学生数据 |
| 学生画像 Agent | DeepAgents | 1 | 为每个学生生成学习画像 |
| 班级分析 Agent | DeepAgents | 1 | 生成班级热力图、薄弱环节识别、班级对比 |
| 教学调整建议 Agent | DeepAgents | 1 | 生成教师应如何调整教学的建议 |

#### 输出规格（班级分析摘要）

```yaml
class_analysis_report:
  report_id: "report_2026_06_12_class_001"
  total_students: 30
  knowledge_network_heatmap:
    - node_id: "tool_elimination_method"
      average_mastery_rate: 0.85
      common_issues: ["符号处理"]
    - node_id: "skill_model_solve_system"
      average_mastery_rate: 0.62
      common_issues: ["情境理解不足"]
  student_tiers:
    - tier: "advanced"
      count: 5
      avg_accuracy: 0.92
      notes: "可挑战概念层"
    - tier: "needs_support"
      count: 7
      avg_accuracy: 0.58
      notes: "可能存在前置知识缺口"
  teaching_adjustment_recommendations:
    - id: "adj_001"
      priority: "high"
      target_node: "skill_model_solve_system"
      suggestion: "安排1课时课堂建模专题练习"
      expected_outcome: "掌握率提升至80%"
```

#### 边界与异常

| 异常场景 | 系统行为 |
|---------|---------|
| 学生学习数据不足（<2 个节点） | 标记为"数据不足无法完整分析" |
| 分析引擎崩溃或超时 | 返回最近一次成功报告缓存，触发告警 |
| 数据异常矛盾 | 标记为"数据矛盾"，提示教师人工核查 |

---


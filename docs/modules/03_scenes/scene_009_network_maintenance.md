# SCENE-009：知识网络动态维护

**父文档**：[system_requirements.md](../../system_requirements.md) · [场景索引](../03_user_roles_scenes_index.md)
**相关决策**：[dp_arch_13](../../decisions/dp_arch_13.md)

---

### 3.2.9 SCENE-009：知识网络动态维护（后台 meta-scenario）

**场景目标**：基于累积的学生学习数据，系统定期分析知识网络的"实际表现"，检测网络结构中的潜在问题（节点过于困难、节点过于容易、节点间衔接断层等），生成网络优化建议报告，供教师/教研人员参考。

**核心设计原则**：
1. **数据驱动优化**：基于真实学生表现
2. **定期 + 手动双触发**：默认每月/每学期自动运行一次，也可教师手动触发
3. **只给建议，不自动修改**：最终决策权在教师
4. **建议要可操作**：问题描述 + 数据证据 + 修改建议 + 预期效果

#### Agent 角色定义

| Agent 角色 | 框架 | 数量 | 职责边界 |
|-----------|------|------|---------|
| 节点性能分析 Agent | DeepAgents | 1 | 分析每个节点的学生表现（掌握率/耗时/错误率） |
| 边关系分析 Agent | DeepAgents | 1 | 分析节点间迁移难度、是否存在衔接断层 |
| 结构优化 Agent | DeepAgents | 1 | 生成网络结构优化建议（拆分/合并/新增/删除节点） |
| 报告生成 Agent | DeepAgents | 1 | 生成人类可读的优化建议报告 |

#### 交互流程

```
触发（定时/手动） → 节点性能分析 → 边关系分析
                       │
                       ▼
                 结构优化 Agent
                       │
                       ▼
              报告生成 → 教师审阅采纳
                       │
                       ▼
           采纳的建议 → 触发 SCENE-001 重新设计
```

#### 输出规格（摘要版）

```yaml
knowledge_network_optimization_report:
  report_id: "net_opt_001"
  network_ref: "kn_001"
  total_students_included: 30
  trigger_type: "scheduled_monthly"
  node_performance_analysis:
    - node_id: "tool_elimination_method"
      design_difficulty: 2
      actual_performance_difficulty: 2
      mastery_rate: 0.85
      status: "as_expected"
    - node_id: "skill_model_solve_system"
      design_difficulty: 3
      actual_performance_difficulty: 4.2
      mastery_rate: 0.60
      status: "significantly_more_difficult_than_expected"
  optimization_suggestions:
    - id: "opt_001"
      priority: "high"
      type: "split_node"
      target_node: "skill_model_solve_system"
      problem_description: "设计难度3，但实际表现难度4.2，掌握率仅60%"
      evidence_data: ["30%学生触发3次或更多错题闭环", "平均完成耗时45分钟（预期30分钟）"]
      suggested_action: "拆分为两个子节点：①'情境中的方程识别与提取'；②'完整建模求解'。第一个节点专注于'从文字到方程'的转化"
      expected_effect: "拆分后每个节点掌握率80%+；降低学生的断层感"
  expected_impact_if_all_adopted:
    expected_avg_mastery_rate_improvement: "+12% (from 78% to 90%)"
  teacher_review_status: "pending_review"
```

#### 边界与异常

| 异常场景 | 系统行为 |
|---------|---------|
| 学习数据不足（<30% 的节点有 ≥5 个学生数据） | 降级为"基于有限数据的初步分析"，醒目警告 |
| Token 超预算 | 仅输出节点+边的性能数据表 + Top3 优化建议 |
| 维护服务崩溃 | 通知运维，保留上次成功报告 |
| 节点性能与设计预期极度矛盾（数据量充足） | 标记为"高优先级优化目标"，主动提醒教师 |

---


# SCENE-005：节点推荐引擎

**父文档**：[system_requirements.md](../../system_requirements.md) · [场景索引](../03_user_roles_scenes_index.md)
**相关决策**：[dp_arch_05](../../decisions/dp_arch_05.md), [dp_arch_09](../../decisions/dp_arch_09.md)

---

**场景目标**：当学生在某节点被标记为"已掌握"后，系统基于知识网络的边关系、学生历史表现、学生目标层次，自动计算并推荐 2~4 个候选下一节点，供学生选择。

**核心设计原则**：
1. **网络驱动**：推荐的核心依据是知识网络中存在的边关系
2. **表现加权**：学生在相关节点的历史表现数据会影响推荐权重
3. **层次匹配**：推荐会考虑学生的目标层级（tool/skill/concept）
4. **学生选择**：系统推荐多个候选，最终由学生决定走哪条路径
5. **不做全局路径规划**：每次只推荐"下一步"，路径是动态涌现的

#### Agent 角色定义

| Agent 角色 | 框架 | 数量 | 职责边界 |
|-----------|------|------|---------|
| 路径分析 Agent | DeepAgents | 1 | 分析知识网络中的可选路径，计算每条路径的"推荐分数" |
| 候选筛选 Agent | DeepAgents | 1 | 基于推荐分数、层次匹配、学生表现筛选 2~4 个最佳候选 |
| 推荐解释 Agent | DeepAgents | 1 | 为每个候选生成"为什么推荐"的解释文字 |

#### 交互流程

```
触发：学生在某节点标记为"已掌握"
  │
  ▼
  路径分析 Agent → 候选筛选 Agent → 推荐解释 Agent
                 │
                 ▼
           学生选择某节点
                 │
                 ▼
          启动 SCENE-003 虚拟教室
```

#### 输入规格

```yaml
recommendation_trigger:
  current_node_id: "tool_elimination_method"
  student_id: "s_001"
  mastery_level_at_current_node: "tool"
  knowledge_network_ref: "kn_001"
  student_target_level: "skill"
  candidate_count: 3
  teacher_approval_required: false
```

#### 输出规格（摘要版）

```yaml
recommendation_result:
  candidates:
    - rank: 1
      recommended_node_id: "skill_model_solve_system"
      recommendation_score: 0.92
      reason: "你在工具层节点表现优秀，下一步自然是学习如何将这种方法应用于真实情境"
    - rank: 2
      recommended_node_id: "tool_more_complex_systems"
      recommendation_score: 0.81
      reason: "如果你想先在工具层巩固，这是一个好选择，强化计算基础"
    - rank: 3
      recommended_node_id: "concept_linear_equations"
      recommendation_score: 0.65
      reason: "如果你对'为什么可以这样解'这个问题本身感兴趣，可以直接挑战概念层"
  student_final_choice: null
  auto_advanced: false
```

#### 边界与异常

| 异常场景 | 系统行为 |
|---------|---------|
| 从当前节点出发无可达后继节点 | 提示"你已完成该主题的所有学习！推荐进入下一主题" |
| 所有候选都被学生拒绝 | 列出知识网络中所有其他可选节点，让学生自由选择 |
| 推荐分数全部 < 0.5 | 扩大搜索范围重新计算；若仍无则提示教师手动建议 |
| 学生历史数据不足（<3 个节点） | 默认按网络结构推荐，表现权重降为 0，标注"待积累数据后自动调整" |

---


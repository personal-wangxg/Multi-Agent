# DP-ARCH-13：知识网络动态维护

**确认日期**：2026-06-12 · **确认人**：项目核心团队 · **决策类别**：架构

---

## 决策摘要

知识网络动态维护（SCENE-009）是一个**后台 meta-scenario**，定期自动运行 + 教师手动触发。基于累积的学生学习数据分析每个节点的实际表现与设计偏差、节点间衔接断层，生成可操作的优化建议（split_node / merge_node / add_transition_node / increase_difficulty / decrease_difficulty）。系统只生成建议，**所有网络结构变更需教师确认**。版本化管理，可追溯、可回滚。

## 核心设计原则

1. **数据驱动优化：基于真实学生表现数据，
2. **定期 + 手动双触发：默认每月/每学期自动运行一次，也可教师手动触发，
3. **只给建议，不自动修改：最终决策权在教师，
4. **建议要可操作：问题描述 + 数据证据 + 修改建议 + 预期效果，
5. **版本化管理：所有网络结构变更历史可追溯、可回滚。

## 关键细节

### 触发方式

| 触发方式 | 触发频率 | 适用场景 |
|---------|---------|---------|
| 定时自动 | 每月 / 每学期 | 常规优化检查 |
| 教师手动 | 按需 | 发现特定问题 / 教学周期结束后复盘 |

### 节点性能分析数据字段

```yaml
node_performance_analysis:
  - node_id: "tool_elimination_method"
    design_difficulty: 2          # 设计时设定的难度(1-5)
    actual_performance_difficulty: 2  # 实际表现难度(1-5)
    mastery_rate: 0.85            # 节点掌握率（班级平均）
    avg_time_minutes: 15          # 平均学习耗时
    avg_error_loop_count: 1.2     # 平均触发错题闭环次数
    status: "as_expected"         # as_expected /
                                  # significantly_more_difficult_than_expected /
                                  # significantly_easier_than_expected /
                                  # transition_gap_with_next
```

### 边关系分析与衔接断层检测

```yaml
edge_performance_analysis:
  - from_node: "tool_elimination_method"
    to_node: "skill_model_solving_systems"
    relation_type: "supports_understanding"
    transition_success_rate: 0.42  # 从前节点到后节点顺利推进比例
    avg_gap_time_minutes: 12       # 学生在前节点与后节点之间的"断层时间"
    diagnostic: "transition_gap"   # transition_smooth / transition_gap / needs_bridge_node
```

### 优化建议类型与格式

```yaml
optimization_suggestions:
  - id: "opt_001"
    priority: "high"                        # high / medium / low
    type: "split_node"                      # split_node / merge_node /
                                            # add_transition_node /
                                            # increase_difficulty / decrease_difficulty
    target_node: "skill_model_building"
    problem_description: "设计难度3，但实际表现难度4.2，掌握率仅60%"
    evidence_data:
      - "30% 学生触发 3 次或更多错题闭环"
      - "平均完成耗时 45 分钟（预期 30 分钟）"
      - "前置节点掌握率 85%，说明前置无断层"
    suggested_action: "拆分为两个子节点：①'情境中的方程识别与提取'；②'完整建模求解'。第一个节点专注于'从文字到方程'的转化"
    expected_effect: "拆分后每个节点掌握率 80%+；降低学生的断层感"
    teacher_review_status: "pending_review"  # pending_review / accepted / rejected / modified
```

### 建议类型说明

| type | 含义 | 典型触发条件 |
|-----|------|-------------|
| split_node | 拆分节点 | 实际难度远高于设计，掌握率低 |
| merge_node | 合并节点 | 两个节点过于简单，或主题高度重叠 |
| add_transition_node | 新增过渡节点 | 两节点间出现明显衔接断层 |
| increase_difficulty | 提升难度 | 实际难度远低于设计，学生太容易 |
| decrease_difficulty | 降低难度 | 实际难度过高，学生难以掌握 |

### 完整流程

```
触发（定时 / 手动）
   │
   ▼
节点性能分析 Agent
   │
   ▼
边关系分析 Agent
   │
   ▼
结构优化 Agent（生成 split/merge/add/... 建议）
   │
   ▼
报告生成 Agent → knowledge_network_optimization_report
   │
   ▼
教师审阅 / 采纳 / 拒绝 / 修改
   │
   └─ 采纳的建议 → 触发 SCENE-001 重新设计知识网络
   │
   └─ Git 提交网络结构变更（可追溯、可回滚）
```

### 报告输出结构

```yaml
knowledge_network_optimization_report:
  report_id: "net_opt_001"
  network_ref: "kn_001"
  total_students_included: 30
  trigger_type: "scheduled_monthly"          # scheduled_monthly / scheduled_semester / manual
  node_performance_analysis: [...]            # 见上
  edge_performance_analysis: [...]
  optimization_suggestions: [...]             # 见上
  expected_impact_if_all_adopted:
    expected_avg_mastery_rate_improvement: "+12% (从 78% 到 90%)"
  teacher_review_status: "pending_review"
  version_history:
    - version: "v1.2"
      changes: ["拆分 skill_model_building 为两个节点"]
      confirmed_by: "teacher_001"
      timestamp: "2026-06-12T11:00:00Z"
```

## 影响范围

- 关联 FR：FR-11（知识网络动态维护）、FR-12（配置持久化与管理）；
- 关联场景：SCENE-001（课程规划，采纳建议后重设计）、SCENE-009（后台维护）；
- 关联产物：knowledge_network_optimization_report、知识网络 Git 版本历史。

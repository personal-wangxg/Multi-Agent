# SCENE-009：网络维护场景

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**场景编号**：SCENE-009  
**关联功能需求**：FR-11（知识网络动态维护）、FR-05（知识网络）

---

## 1. 场景概述

**一句话描述**：基于学情分析和教学评估数据，系统定期对知识网络进行结构性优化建议——包括节点拆分/合并/新增/难度调整——经教师审核后执行，变更通过Git版本管理。

**参与角色**：
- 节点性能分析Agent
- 边关系分析Agent
- 优化建议生成Agent
- 教师审核Agent
- 网络重构Agent
- Git版本管理Agent

---

## 2. 核心流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCENE-009 网络维护核心流程                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  触发条件                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. 定期触发（monthly）：每月自动评估                                 │   │
│  │ 2. 单元结束触发（end_of_unit）：SCENE-008教学评估后                 │   │
│  │ 3. 教师手动触发（teacher_manual）：教师随时可发起                    │   │
│  │ 4. 自动触发阈值：薄弱节点数>3 或 整体掌握率<60%                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                             │                                                 │
│                             ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      分析流程                                        │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 1. 节点性能分析Agent                                          │  │   │
│  │  │    - 计算 designed_difficulty vs actual_difficulty            │  │   │
│  │  │    - 计算 class_mastery_rate                                  │  │   │
│  │  │    - 计算 average_time_vs_estimated                          │  │   │
│  │  │    - 标记需优化节点                                            │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 2. 边关系与衔接分析Agent                                      │  │   │
│  │  │    - 计算 transition_success_rate                             │  │   │
│  │  │    - 标记衔接断层                                             │  │   │
│  │  │    - 检查孤立节点                                            │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 3. 优化建议生成Agent                                          │  │   │
│  │  │    - 生成结构化建议列表                                        │  │   │
│  │  │    - 每条含 type/problem/suggestion/expected_impact/confidence │  │   │
│  │  │    - 自动置信度 > 0.85 的建议进入待采纳队列                   │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  └───────────────────────────────┼─────────────────────────────────────┘   │
│                                  │                                          │
│                                  ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      教师审核（FR-13）                                │   │
│  │                                                                      │   │
│  │  每条建议以卡片形式展示，教师可选择：                                 │   │
│  │                                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │ approve │  │ reject  │  │ revise   │  │ delay   │            │   │
│  │  │ 采纳    │  │ 拒绝    │  │ 修改后采纳 │  │ 延迟    │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                             │                                                 │
│              ┌──────────────┴──────────────┐                               │
│              ▼                             ▼                               │
│     [有采纳的建议]                  [全部拒绝/延迟]                        │
│              │                             │                               │
│              ▼                             ▼                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      采纳执行                                        │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 4. 网络重构Agent                                              │  │   │
│  │  │    - 调用SCENE-001重新设计受影响的子网络                      │  │   │
│  │  │    - 新网络通过Schema校验                                    │  │   │
│  │  │    - 生成新版本号                                             │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 5. Git版本管理Agent                                          │  │   │
│  │  │    - Git commit变更                                          │  │   │
│  │  │    - 更新decision_index                                      │  │   │
│  │  │    - 可一键回滚                                               │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Agent角色定义

| Agent ID | 角色名称 | 框架 | 职责说明 | 特殊要求 |
|----------|---------|------|---------|---------|
| `agent_scene009_node_analyzer_001` | 节点性能分析Agent | DeepAgents | 分析节点性能数据，识别优化目标 | 绑定`tpl_scene009_node_v1.0` |
| `agent_scene009_edge_analyzer_002` | 边关系分析Agent | DeepAgents | 分析边关系，识别衔接问题 | 绑定`tpl_scene009_edge_v1.0` |
| `agent_scene009_optimizer_003` | 优化建议生成Agent | DeepAgents | 生成结构化优化建议 | 绑定`tpl_scene009_optimizer_v1.0` |
| `agent_scene009_reconstructor_004` | 网络重构Agent | DeepAgents | 执行网络变更 | 绑定`tpl_scene009_reconstructor_v1.0` |
| `agent_scene009_git_manager_005` | Git版本管理Agent | DeepAgents | Git提交与回滚 | 绑定`tpl_scene009_git_v1.0` |

**协作模式**：Sequential（分析→建议→审核→重构→Git提交）

---

## 4. 输入/输出规格

### 4.1 场景输入规格

```yaml
scene009_maintenance_input:
  request_type: "network_maintenance"
  
  trigger: "end_of_unit"  # monthly / end_of_unit / teacher_manual
  
  knowledge_network_ref: "kn_001"
  current_version: "1.2"
  
  data_sources:
    - type: "learning_analytics_report"
      ref: "/data/analytics/analytics_20260615_001.yaml"
    
    - type: "teaching_evaluation_report"
      ref: "/teaching_eval/kn_001/teach_eval_20260615_001.yaml"
    
    - type: "node_mastery_performance"
      ref: "/data/mastery/kn_001_all_students.json"
  
  teacher_id: "teacher_001"
  
  maintenance_config:
    auto_apply_threshold: 0.85  # 置信度>0.85的建议自动进入待采纳
    require_teacher_approval: true  # 是否强制教师审批
    maintenance_frequency_min_weeks: 2  # 维护间隔不短于2周
  
  context_hints:
    previous_maintenance_id: "maint_20260601_001"  # 上次维护记录
```

### 4.2 维护建议报告输出

```yaml
network_maintenance_report:
  maintenance_id: "maint_20260615_001"
  kn_ref: "kn_001"
  
  previous_version: "1.2"
  new_version: null  # 确认采纳后填充
  
  triggered_by: "end_of_unit"  # monthly / end_of_unit / teacher_manual
  triggered_by_report_refs:
    - "/data/analytics/analytics_20260615_001.yaml"
    - "/teaching_eval/kn_001/teach_eval_20260615_001.yaml"
  
  analyzed_at: "2026-06-15T19:00:00Z"
  
  data_coverage:
    students_analyzed: 30
    nodes_with_data: 12
    nodes_with_insufficient_data: 0
    data_quality_note: "数据覆盖充分"
  
  # ========== 节点性能分析 ==========
  node_performance_analysis:
    - node_id: "skill_model_building_12"
      node_title: "实际问题与建模"
      layer: "skill"
      
      designed_difficulty: 4
      actual_difficulty: 4.8  # 由正确率/耗时/闭环次数综合计算
      deviation: 0.8
      deviation_flag: "positive"  # positive=偏难，negative=偏易
      
      class_mastery_rate: 0.42
      mastery_rate_flag: "low"  # low / medium / high
      
      average_time_minutes: 90
      estimated_periods: 2
      time_ratio: 2.25  # actual/estimated
      time_ratio_flag: "high"
      
      error_loops_per_student: 2.1
      
      flags:
        - "难度与设计偏差显著（|deviation|=0.8>1的阈值，实际上更偏难）"
        - "高难度节点（mastery_rate<50%）"
        - "可能需拆分（time_ratio>2.0）"
      
      optimization_types_recommended:
        - "split_node"
        - "decrease_difficulty"
    
    - node_id: "tool_factorization_method_08"
      node_title: "因式分解法求解"
      layer: "tool"
      
      designed_difficulty: 3
      actual_difficulty: 3.8
      deviation: 0.8
      deviation_flag: "positive"
      
      class_mastery_rate: 0.57
      mastery_rate_flag: "medium"
      
      average_time_minutes: 55
      estimated_periods: 2
      time_ratio: 1.38
      
      error_loops_per_student: 1.2
      
      flags:
        - "建议降低难度或增加前置铺垫"
      
      optimization_types_recommended:
        - "decrease_difficulty"
    
    # ... 其他节点分析（省略）
  
  # ========== 边关系与衔接分析 ==========
  edge_and_transition_analysis:
    - edge_id: "edge_001"
      from_node: "tool_formula_method_07"
      from_node_title: "公式法"
      to_node: "skill_method_selection_04"
      to_node_title: "方法选择"
      
      relation_type: "enables_operation"  # is_prerequisite / supports_understanding / enables_operation
      
      transition_success_rate: 0.38  # 从from到to的流畅度
      transition_rate_flag: "low"  # low(<0.4) / medium / high
      
      evidence:
        - "30%学生在from节点掌握后进入to节点时，停留超过2倍预期课时"
        - "该边衔接流畅度低于0.4阈值"
      
      flags:
        - "衔接断层，建议增加过渡节点"
      
      optimization_types_recommended:
        - "add_transition_node"
  
  # ========== 优化建议列表 ==========
  optimization_suggestions:
    - id: "opt_001"
      type: "split_node"
      target: "skill_model_building_12"
      
      problem_description: |
        该节点设计难度4，但学生实际感知难度4.8，掌握率仅42%，
        平均耗时达估计课时2.25倍。表明节点内容过大、难度跨度太大，
        需要拆分为更小颗粒度的子节点。
      
      suggestion: |
        拆分为2个子节点：
        - skill_model_building_basic_12a：从文字情境建立方程（含1-2步简单情境）
        - skill_model_building_advanced_12b：含多条件多变量的复杂情境建模
      
      expected_impact: |
        split后基本节点预计掌握率提升至70%+；
        高级节点作为可选拓展，供advanced学生挑战
      
      confidence: 0.88  # 数据证据强度
      confidence_threshold_exceeded: true  # >0.85
      
      teacher_decision: null  # 待审核
      teacher_comments: null
      teacher_decided_at: null
    
    - id: "opt_002"
      type: "add_transition_node"
      target: "tool_formula_method_07 → skill_method_selection_04"
      
      problem_description: |
        从工具层到技能层的衔接流畅度仅38%，30%学生在此节点停留超过2倍预期课时，
        表明从公式法到方法选择的跃迁缺乏过渡。
      
      suggestion: |
        新增过渡节点 transition_node：
        - node_id: "tool_to_skill_practice_07.5"
        - title: "公式法到方法选择过渡练习"
        - layer: tool（作为工具层顶节点）
        - difficulty: 3
        - content: 包含5-8道带脚手架的情境建模入门题
        - 边：tool_formula_method_07 → tool_to_skill_practice_07.5（is_prerequisite）
        - 边：tool_to_skill_practice_07.5 → skill_method_selection_04（is_prerequisite）
      
      expected_impact: |
        衔接流畅度预计从38%提升至65%+
      
      confidence: 0.75
      confidence_threshold_exceeded: false  # 0.75 < 0.85，不自动采纳
      
      teacher_decision: null
      teacher_comments: null
      teacher_decided_at: null
    
    - id: "opt_003"
      type: "decrease_difficulty"
      target: "tool_factorization_method_08"
      
      problem_description: |
        该节点设计难度3但实际难度3.8，且班级掌握率仅57%，
        因式分解对初学者的难度预期偏低。
      
      suggestion: |
        两个选项：
        A. 降低该节点设计难度标注从3至4（反映真实难度）
        B. 拆分为2个子节点：十字相乘基础 + 十字相乘进阶
      
      expected_impact: |
        降低预期可避免教师过度挤压课时；
        拆分可进一步细化学习颗粒度
      
      confidence: 0.65
      confidence_threshold_exceeded: false
      
      teacher_decision: null
      teacher_comments: null
      teacher_decided_at: null
  
  # ========== 审核状态汇总 ==========
  review_summary:
    total_suggestions: 3
    auto_approved: 0  # 无置信度>0.85的建议（因为优化类建议置信度通常较低）
    pending_review: 3
    approved: 0
    rejected: 0
    revised: 0
    delayed: 0
  
  data_sufficiency:
    has_sufficient_data: true
    nodes_with_insufficient_data: 0
    warning_note: null
```

### 4.3 采纳执行后输出

```yaml
maintenance_execution_result:
  maintenance_id: "maint_20260615_001"
  
  execution_status: "completed"  # pending / in_progress / completed / failed / rolled_back
  
  previous_version: "1.2"
  new_version: "1.3"
  
  changes_summary:
    nodes_added: 3  # 2个拆分节点 + 1个过渡节点
    nodes_removed: 1  # skill_model_building_12被拆分替代
    nodes_modified: 0
    edges_added: 5
    edges_removed: 2
  
  executed_suggestions:
    - suggestion_id: "opt_001"
      type: "split_node"
      status: "executed"
      details:
        original_node: "skill_model_building_12"
        new_nodes:
          - "skill_model_building_basic_12a"
          - "skill_model_building_advanced_12b"
        edges_created: 4
        student_learning_path_impact: "需重新学习basic后进入advanced"
    
    - suggestion_id: "opt_002"
      type: "add_transition_node"
      status: "executed"
      details:
        new_node: "tool_to_skill_practice_07.5"
        edges_created: 2
  
  git_commit:
    commit_hash: "a1b2c3d4e5f6"
    commit_message: "maintain(kn_001 v1.2→v1.3): split skill_model_building_12 into basic/advanced; add transition_node"
    committed_at: "2026-06-15T19:30:00Z"
    committer: "system_agent"
  
  decision_index_updated:
    new_dp_ids:
      - "DP-MAINT-001"
      - "DP-MAINT-002"
      - "DP-MAINT-003"
    compile_status: "success"
    compile_duration_ms: 1200
  
  rollback_available: true
  rollback_to_version: "1.2"
  
  artifacts_persisted:
    - type: "network_maintenance_report"
      path: "/maintenance/kn_001/maint_20260615_001.yaml"
    
    - type: "knowledge_network_yaml"
      path: "/knowledge_networks/kn_001.yaml"
      version: "1.3"
    
    - type: "decision_index_json"
      path: "/sessions/sess_maintenance_20260615_001/working/decision_index.json"
  
  next_scheduled_maintenance:
    scheduled_at: "2026-07-15T19:00:00Z"
    trigger: "monthly"
```

---

## 5. 与其他场景的数据流关系

| 方向 | 场景/FR | 数据内容 | 说明 |
|------|---------|---------|------|
| **输入←** | SCENE-007 | 学情分析数据 | 节点性能依据 |
| **输入←** | SCENE-008 | 教学评估报告 | 薄弱环节数据 |
| **触发→** | SCENE-001 | 重新设计子网络 | 网络重构 |
| **输出→** | FR-05 | 新知识网络版本 | Schema校验后生效 |
| **输出→** | FR-12 | 维护记录持久化 | 版本存档 |
| **输出→** | FR-18 | 决策索引更新 | 新DP记录 |

---

## 6. 关键约束

| 约束类型 | 约束内容 | 来源 |
|---------|---------|------|
| **数据约束** | 需基于30%节点≥5名学生数据 | FR-11 |
| **频率约束** | 维护间隔不短于2周 | FR-11 |
| **删除约束** | 节点/边删除必须教师明确批准 | FR-11 |
| **校验约束** | 新网络必须通过FR-05完整Schema校验 | FR-11 |
| **版本约束** | Git版本管理，任意版本可回滚 | FR-11 |
| **建议约束** | 每条含type/problem/suggestion/expected_impact/confidence | FR-11 |

---

## 7. 验收标准

| 验收项 | 验收条件 | 验证方式 |
|-------|---------|---------|
| **VA-001** | 基于标准学情+评估数据可生成≥2条优化建议 | 端到端测试 |
| **VA-002** | 每条建议含完整字段 | 格式校验 |
| **VA-003** | 采纳后版本号正确递增 | 版本管理测试 |
| **VA-004** | Git commit记录清晰可读 | 提交记录校验 |
| **VA-005** | 回滚功能可用 | 回滚测试 |
| **VA-006** | 新网络通过Schema校验 | 校验测试 |
| **VA-007** | decision_index正确更新 | DP校验 |

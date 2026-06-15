# SCENE-007：学情分析场景

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**场景编号**：SCENE-007  
**关联功能需求**：FR-09（学情分析）、FR-06（节点推荐数据支持）

---

## 1. 场景概述

**一句话描述**：系统持续采集学生在各节点的学习数据，生成个性化学习画像和班级知识网络热力图，识别薄弱环节并生成教学调整建议。

**参与角色**：
- 数据聚合Agent
- 学生画像Agent
- 班级热力图Agent
- 薄弱环节识别Agent
- 教学建议生成Agent

---

## 2. 核心流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCENE-007 学情分析核心流程                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  数据来源                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ FR-09 多源数据聚合：                                                 │   │
│  │                                                                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │   │
│  │  │ SCENE-003  │  │ SCENE-004  │  │ SCENE-006  │  │ SCENE-005  │  │   │
│  │  │ 虚拟教室   │  │ 错题闭环   │  │ 作业批改   │  │ 节点推荐   │  │   │
│  │  │ 会话记录   │  │ 记录      │  │ 结果       │  │ 选择记录   │  │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │   │
│  │                                                                      │   │
│  │  累计数据：                                                          │   │
│  │  - 各节点掌握状态（mastered/in_progress/not_started）               │   │
│  │  - 累计正确率                                                        │   │
│  │  - 错题闭环次数                                                      │   │
│  │  - 平均学习耗时                                                      │   │
│  │  - 错误类型分布                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                             │                                                 │
│                             ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      学情分析主流程                                  │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 1. 数据聚合Agent                                              │  │   │
│  │  │    - 抽取每个学生在每个节点的特征数据                          │  │   │
│  │  │    - 跨源数据整合与清洗                                        │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 2. 学生画像Agent（为每个学生生成）                             │  │   │
│  │  │    - 学习速度标签（快/中/慢）                                 │  │   │
│  │  │    - 优势类型（概念型/操作型/应用型）                          │  │   │
│  │  │    - 薄弱节点列表                                             │  │   │
│  │  │    - 偏好路径                                                 │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 3. 班级热力图Agent                                            │  │   │
│  │  │    - 节点热力值 = 1 - 班级平均掌握率                          │  │   │
│  │  │    - 错误热点标注                                             │  │   │
│  │  │    - 层次分布对比                                             │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 4. 薄弱环节识别Agent                                          │  │   │
│  │  │    - 掌握率<60%的节点识别                                     │  │   │
│  │  │    - 错误类型分布分析                                         │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ 5. 教学建议生成Agent                                          │  │   │
│  │  │    - 针对薄弱节点的具体建议                                   │  │   │
│  │  │    - 分层教学建议                                             │  │   │
│  │  │    - 预期改进效果                                             │  │   │
│  │  └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  └───────────────────────────────┼─────────────────────────────────────┘   │
│                                  │                                          │
│                                  ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 输出：完整学情分析报告                                               │   │
│  │   - per_student_profiles[]                                        │   │
│  │   - class_heatmap                                                 │   │
│  │   - weak_points_analysis[]                                        │   │
│  │   - teaching_adjustment_suggestions[]                             │   │
│  │   - student_tiers[]                                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  自动触发：每24小时自动更新 / 教师手动触发                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Agent角色定义

| Agent ID | 角色名称 | 框架 | 职责说明 | 特殊要求 |
|----------|---------|------|---------|---------|
| `agent_scene007_aggregator_001` | 数据聚合Agent | DeepAgents | 多源数据抽取与整合 | 绑定`tpl_scene007_aggregator_v1.0` |
| `agent_scene007_profiler_002` | 学生画像Agent | DeepAgents | 生成个性化学生画像 | 绑定`tpl_scene007_profiler_v1.0` |
| `agent_scene007_heatmap_003` | 班级热力图Agent | DeepAgents | 生成班级层面热力图 | 绑定`tpl_scene007_heatmap_v1.0` |
| `agent_scene007_weakness_004` | 薄弱环节识别Agent | DeepAgents | 识别班级薄弱节点 | 绑定`tpl_scene007_weakness_v1.0` |
| `agent_scene007_suggestion_005` | 教学建议Agent | DeepAgents | 生成可操作改进建议 | 绑定`tpl_scene007_suggestion_v1.0` |

**协作模式**：Sequential（聚合→画像→热力图→薄弱识别→建议）

---

## 4. 输入/输出规格

### 4.1 场景输入规格

```yaml
scene007_analytics_input:
  request_type: "learning_analytics"
  
  analysis_scope: "per_course"  # per_course / per_unit / per_node
  course_ref: "kn_001"
  
  target_students:
    scope_type: "class"  # class / individual / all
    class_id: "class_003"
    student_ids: ["student_001", "student_002", "...", "student_030"]
  
  knowledge_network_ref: "kn_001"
  
  data_sources:
    - type: "virtual_classroom_sessions"
      ref: "/data/vc/sess_*/node_*.json"
      date_range:
        from: "2026-05-01"
        to: "2026-06-15"
    
    - type: "error_loop_records"
      ref: "/data/err/err_loop_*.json"
      date_range:
        from: "2026-05-01"
        to: "2026-06-15"
    
    - type: "homework_grading_results"
      ref: "/data/hw/hw_*.json"
      date_range:
        from: "2026-05-01"
        to: "2026-06-15"
    
    - type: "node_mastery_log"
      ref: "/data/mastery/student_*_node_*.json"
  
  analysis_timestamp: "2026-06-15T18:00:00Z"
  
  auto_regeneration_config:
    enabled: true
    frequency_hours: 24
    trigger_on_threshold: true  # 是否在异常时触发
  
  teacher_id: "teacher_001"
```

### 4.2 学情分析报告输出

```yaml
learning_analytics_report:
  report_id: "analytics_20260615_001"
  course_ref: "kn_001"
  class_ref: "class_003"
  
  total_students: 30
  students_with_sufficient_data: 28
  students_with_insufficient_data: 2
  insufficient_data_student_ids: ["student_015", "student_022"]
  
  data_cutoff_time: "2026-06-15T18:00:00Z"
  data_coverage:
    virtual_classroom_sessions: 145
    error_loop_records: 62
    homework_grading_results: 28
    node_mastery_updates: 312
  
  report_generated_at: "2026-06-15T18:05:00Z"
  
  # ========== 学生个人画像 ==========
  per_student_profiles:
    - student_id: "student_023"
      overall_status: "on_track"  # advanced / on_track / needs_support
      
      nodes_mastered_count: 7
      nodes_in_progress_count: 2
      nodes_not_started_count: 3
      total_nodes_in_network: 12
      
      mastery_rate: 0.58
      
      average_accuracy: 0.82
      average_time_vs_estimated: 0.95  # 0.95 = 比预估快5%
      
      strength_type: "操作型"  # 概念型 / 操作型 / 应用型
      
      strength_evidence:
        - "tool_formula_method_07：正确率92%，耗时低于预估15%"
        - "tool_factorization_method_08：首次进入即掌握"
        - "tool_elimination_method_06：正确率88%"
      
      weak_nodes:
        - node_id: "skill_model_building_12"
          status: "in_progress"
          accuracy: 0.55
          error_loops_count: 3
          avg_time_vs_estimated: 1.8
          note: "在真实情境建模题上持续困难，可能需要额外辅导"
        
        - node_id: "skill_method_selection_04"
          status: "in_progress"
          accuracy: 0.60
          error_loops_count: 1
          avg_time_vs_estimated: 1.2
          note: "方法选择策略尚未形成体系"
      
      learning_path_preference: |
        工具层 → 技能层（在工具层节点上表现优秀，
        但进入技能层后学习速度放缓，
        建议加强概念层与技能层的衔接）
      
      active_in_last_7_days: true
      
      error_type_distribution:
        concept: 0.15
        computational: 0.45
        reading: 0.25
        prerequisite: 0.15
      
      recommended_actions:
        - "建议返回 skill_model_building_12 进行建模专项练习"
        - "可参考 advanced 学生 Chen 的学习路径作为参考"
        - "关注 computational 类错误的纠正"
    
    # ... 其他学生画像（省略）
  
  # ========== 班级知识网络热力图 ==========
  class_heatmap:
    overall_class_mastery_rate: 0.71
    overall_class_accuracy: 0.76
    
    per_node_statistics:
      - node_id: "concept_equation_essence_01"
        node_title: "理解一元二次方程的本质"
        layer: "concept"
        
        class_mastery_rate: 0.80
        students_mastered: 24
        students_in_progress: 4
        students_not_started: 2
        
        average_accuracy: 0.78
        average_time_minutes: 35
        estimated_periods: 1
        time_ratio: 0.78  # actual/estimated
        
        error_loops_per_student: 0.4
        hotness_level: "cool"  # cool / warm / hot
      
      - node_id: "skill_model_building_12"
        node_title: "实际问题与建模"
        layer: "skill"
        
        class_mastery_rate: 0.42
        students_mastered: 12
        students_in_progress: 10
        students_not_started: 8
        
        average_accuracy: 0.48
        average_time_minutes: 90
        estimated_periods: 2
        time_ratio: 2.25
        
        error_loops_per_student: 2.1
        hotness_level: "hot"  # 红色标记，需重点关注
      
      # ... 其他节点统计（省略）
    
    layer_performance_comparison:
      concept_layer:
        average_mastery_rate: 0.76
        average_accuracy: 0.80
        note: "概念理解整体尚可，80%学生能正确判断方程类型"
      
      skill_layer:
        average_mastery_rate: 0.58
        average_accuracy: 0.62
        note: "技能应用是班级主要薄弱环节，尤其是建模能力"
      
      tool_layer:
        average_mastery_rate: 0.83
        average_accuracy: 0.85
        note: "操作训练效果良好，学生在工具层表现稳定"
    
    error_hotspots:
      - node_id: "skill_model_building_12"
        error_type: "concept"
        description: "情境→方程的转化困难"
        affected_students_count: 14
        percentage_of_class: 0.47
      
      - node_id: "tool_completion_method_09"
        error_type: "computational"
        description: "配方法步骤不规范"
        affected_students_count: 11
        percentage_of_class: 0.37
  
  # ========== 薄弱环节分析 ==========
  weak_points_analysis:
    - node_id: "skill_model_building_12"
      class_mastery_rate: 0.42
      dominant_error_type: "concept"
      dominant_error_description: "情境建模中难以正确建立方程"
      
      evidence:
        - "本节点平均准确率仅48%，低于60%阈值"
        - "47%学生在此节点触发过概念类错误"
        - "平均耗时为预估的2.25倍"
        - "错题闭环平均触发2.1次/学生"
      
      recommendation: "加强情境建模教学，建议在课堂增加完整建模案例演练"
      priority: "high"
    
    - node_id: "skill_method_selection_04"
      class_mastery_rate: 0.55
      dominant_error_type: "concept"
      dominant_error_description: "学生难以根据方程特征选择最优解法"
      
      evidence:
        - "仅55%学生掌握方法选择策略"
        - "错误集中在'何时用配方法vs公式法'的判断"
      
      recommendation: "增加方法对比专题练习"
      priority: "medium"
  
  # ========== 教学调整建议 ==========
  teaching_adjustment_suggestions:
    - id: "adj_001"
      target: "全班教学策略"
      suggestion: |
        增加1课时课堂建模专题练习，采用'学生出题 + 互评选做'的互动方式，
        让学生在真实情境中体会方程建模过程
      expected_impact: |
        skill_model_building_12 掌握率从42%提升至70%+
      priority: "high"
      estimated_implementation_time: "1课时"
      feedback_to_scenes:
        - "SCENE-002 备课辅助：生成建模专题教案"
        - "SCENE-008 教学评估：在下次评估中重点关注该节点"
    
    - id: "adj_002"
      target: "students_tier: needs_support"
      suggestion: |
        为 7 名 needs_support 学生推荐从概念层重新进入相关节点，
        补齐概念理解根基后再进入技能层
      expected_impact: |
        预计提升 needs_support 学生后续节点表现15-20%
      priority: "medium"
      target_student_ids: ["student_003", "student_008", "student_015", ...]
    
    - id: "adj_003"
      target: "students_tier: advanced"
      suggestion: |
        为 5 名 advanced 学生推荐进入概念层扩展节点
        （如二次函数与二次方程的联系）
      expected_impact: |
        保持 advanced 学生学习动力，避免分层教学天花板效应
      priority: "low"
      target_student_ids: ["student_005", "student_012", ...]
  
  # ========== 学生分层（供教师分组教学使用） ==========
  student_tiers:
    - tier: "advanced"
      count: 5
      avg_accuracy: 0.92
      avg_mastery_rate: 0.85
      recommendation: "可提前进入概念层拓展节点或跨主题学习"
      student_ids: ["student_005", "student_012", "student_018", "student_025", "student_028"]
    
    - tier: "on_track"
      count: 18
      avg_accuracy: 0.76
      avg_mastery_rate: 0.68
      recommendation: "按标准路径推进，当前进度正常"
      student_ids: ["student_001", "student_002", ...]
    
    - tier: "needs_support"
      count: 7
      avg_accuracy: 0.58
      avg_mastery_rate: 0.45
      recommendation: "可能存在前置知识缺口，建议从概念层重新夯实"
      student_ids: ["student_003", "student_008", "student_015", ...]
  
  data_completeness:
    has_sufficient_data: true
    data_quality_notes: |
      30名学生中有28名有完整章节1-3学习数据；
      student_015 和 student_022 因病缺勤较多，数据不充分
    nodes_with_insufficient_data: 0  # 所有节点均有足够学生数据
  
  next_scheduled_update:
    scheduled_at: "2026-06-16T18:00:00Z"
    frequency_hours: 24
```

---

## 5. 与其他场景的数据流关系

| 方向 | 场景/FR | 数据内容 | 说明 |
|------|---------|---------|------|
| **输入←** | SCENE-003 | 虚拟教室会话记录 | 学习过程数据 |
| **输入←** | SCENE-004 | 错题闭环记录 | 错误诊断数据 |
| **输入←** | SCENE-006 | 作业批改结果 | 评估数据 |
| **输出→** | SCENE-005 | 学生画像数据 | 推荐引擎使用 |
| **输出→** | SCENE-008 | 分析数据 | 教学评估依据 |
| **输出→** | FR-12 | 报告持久化 | 存档 |
| **反馈→** | SCENE-002 | 教学建议 | 备课调整 |

---

## 6. 关键约束

| 约束类型 | 约束内容 | 来源 |
|---------|---------|------|
| **时间约束** | 单次分析≤2分钟 | FR-09 |
| **数据不足处理** | 某节点<3名学生数据不纳入判定 | FR-09 |
| **隐私约束** | 个人画像仅学生本人与教师可见 | FR-09 |
| **自动更新** | 默认每24小时自动更新 | FR-09 |
| **矛盾检测** | 同一学生同节点数据矛盾时标注 | FR-09 |

---

## 7. 验收标准

| 验收项 | 验收条件 | 验证方式 |
|-------|---------|---------|
| **VA-001** | 30名学生班级可在≤2分钟内生成完整报告 | 性能测试 |
| **VA-002** | 正确识别≥2个薄弱节点（掌握率<60%） | 准确性测试 |
| **VA-003** | strength_type与数据一致 | 内容校验 |
| **VA-004** | 每条建议含target/suggestion/expected_impact | 格式校验 |
| **VA-005** | 报告可自动影响SCENE-005推荐表现分 | 集成测试 |
| **VA-006** | 薄弱节点建议可反馈至SCENE-002 | 数据流测试 |
| **VA-007** | 学生分层数据正确 | 分层逻辑测试 |

# SCENE-005：节点推荐场景

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**场景编号**：SCENE-005  
**关联功能需求**：FR-06（节点推荐引擎）、FR-13（人机协同）

---

## 1. 场景概述

**一句话描述**：当学生在某节点达到掌握标准后，系统基于知识网络拓扑结构、学生历史表现和学习目标，计算并推荐2~4个候选下一节点，学生拥有最终选择权。

**参与角色**：
- 推荐引擎Agent（FR-06核心）
- 候选解释生成Agent
- 学生选择记录Agent
- 教师审核Agent（可选）

---

## 2. 核心流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCENE-005 节点推荐核心流程                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  触发条件                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. SCENE-003 虚拟教室中学生完成节点学习并确认掌握                    │   │
│  │ 2. SCENE-004 练习闭环完成后                                          │   │
│  │ 3. SCENE-006 作业批改后教师/学生请求推荐                             │   │
│  │ 4. 学生自主浏览网络后请求推荐                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  推荐计算流程                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │   ┌──────────────────────────────────────────────────────────────┐  │   │
│  │   │ 1. 可达后继节点收集                                            │  │   │
│  │   │    - is_prerequisite出边的直接后继                            │  │   │
│  │   │    - 跨层 supports/enables 边后继                             │  │   │
│  │   │    - 同主题 same_topic_cross_layer 纵向跃迁                  │  │   │
│  │   └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │   ┌──────────────────────────────────────────────────────────────┐  │   │
│  │   │ 2. 基础分计算（网络结构，60%权重）                            │  │   │
│  │   │    - is_prerequisite直接后继: 0.9                           │  │   │
│  │   │    - 跨层边后继: 0.75                                       │  │   │
│  │   │    - 路径长度衰减: 0.8^path_length                          │  │   │
│  │   └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │   ┌──────────────────────────────────────────────────────────────┐  │   │
│  │   │ 3. 表现分计算（历史数据，30%权重）                            │  │   │
│  │   │    - 同类节点历史正确率                                       │  │   │
│  │   │    - 错题闭环触发次数                                        │  │   │
│  │   │    - 掌握速度（耗时/预估）                                    │  │   │
│  │   │    - 数据不足时降为中性0.5                                   │  │   │
│  │   └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │   ┌──────────────────────────────────────────────────────────────┐  │   │
│  │   │ 4. 层次匹配分（目标层次，10%权重）                            │  │   │
│  │   │    - tool层节点 +0.2 (if target=tool)                        │  │   │
│  │   │    - skill层节点 +0.2 (if target=skill)                      │  │   │
│  │   │    - concept层节点 +0.2 (if target=concept)                   │  │   │
│  │   └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │   ┌──────────────────────────────────────────────────────────────┐  │   │
│  │   │ 5. 候选筛选与多样性保证                                       │  │   │
│  │   │    - 取前 candidate_count×2 个节点                           │  │   │
│  │   │    - 保证≥2个layer的多样性                                   │  │   │
│  │   │    - difficulty跳跃限制：|Δ| ≤ 1                             │  │   │
│  │   └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  │                               ▼                                     │   │
│  │   ┌──────────────────────────────────────────────────────────────┐  │   │
│  │   │ 6. 推荐解释生成                                                │  │   │
│  │   │    - 三要素：网络依赖 + 表现匹配 + 层次匹配                   │  │   │
│  │   │    - 结构化 score_breakdown                                  │  │   │
│  │   └──────────────────────────┬───────────────────────────────────┘  │   │
│  │                               │                                     │   │
│  └───────────────────────────────┼─────────────────────────────────────┘   │
│                                  │                                        │
│                                  ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ 学生选择环节                                                       │  │
│  │                                                                      │  │
│  │  系统展示推荐卡片：                                                 │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                              │  │
│  │  │ 候选1   │  │ 候选2   │  │ 候选3   │                              │  │
│  │  │ score   │  │ score   │  │ score   │                              │  │
│  │  │ 理由    │  │ 理由    │  │ 理由    │                              │  │
│  │  │ [选择]  │  │ [选择]  │  │ [选择]  │                              │  │
│  │  └─────────┘  └─────────┘  └─────────┘                              │  │
│  │                                                                      │  │
│  │  学生可：                                                           │  │
│  │  - 选择其中一个候选                                                │  │
│  │  - 全部拒绝后自由浏览网络                                          │  │
│  │  - (可选) 教师审核模式下由教师决定                                 │  │
│  │                                                                      │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Agent角色定义

| Agent ID | 角色名称 | 框架 | 职责说明 | 特殊要求 |
|----------|---------|------|---------|---------|
| `agent_scene005_recommender_001` | 推荐引擎Agent | DeepAgents | 执行推荐算法计算候选节点和分数 | 绑定`tpl_scene005_recommender_v1.0` |
| `agent_scene005_explainer_002` | 推荐解释生成Agent | DeepAgents | 生成自然语言推荐理由 | 绑定`tpl_scene005_explainer_v1.0` |
| `agent_scene005_selector_003` | 学生选择记录Agent | DeepAgents | 记录学生选择，更新偏好 | 绑定`tpl_scene005_selector_v1.0` |

**协作模式**：Pipeline（推荐计算→解释生成→选择记录）

---

## 4. 输入/输出规格

### 4.1 场景输入规格

```yaml
scene005_recommend_input:
  request_type: "node_recommendation"
  
  student_id: "student_023"
  current_node_id: "tool_formula_method_07"
  mastery_confirmed: true
  
  student_target_level: "skill"  # tool / skill / concept
  
  knowledge_network_ref: "kn_001"
  
  historical_performance_ref: "/data/students/student_023_performance.json"
  
  recommendation_config:
    candidate_count: 3
    teacher_approval_required: false  # 是否需要教师审核
    allow_reject_all: true
  
  optional_overrides:
    force_include_nodes: []  # 强制包含的节点ID
    exclude_nodes: []       # 排除的节点ID
```

### 4.2 推荐结果输出

```yaml
recommendation_result:
  request_id: "rec_20260615_007"
  student_id: "student_023"
  current_node_id: "tool_formula_method_07"
  algorithm_version: "v1.0"
  
  student_target_level: "skill"
  
  candidates:
    - rank: 1
      node_id: "skill_method_selection_04"
      node_title: "根据方程特征灵活选择解法"
      layer: "skill"
      recommendation_score: 0.91
      
      score_breakdown:
        network_structure_score: 0.54   # 60%权重
        network_contribution: "is_prerequisite直接后继"
        performance_score: 0.27        # 30%权重
        performance_contribution: "工具层表现优秀（正确率92%）"
        level_match_score: 0.10        # 10%权重
        level_match_contribution: "符合技能层学习目标"
      
      reason: |
        你在工具层'公式法'节点表现优秀（正确率92%，耗时低于预期15%），
        推荐进入技能层学习如何根据方程特征灵活选择解法。
        这符合你以技能应用为目标的学习方向。
      
      estimated_periods: 2
      difficulty: 4
      difficulty_delta: +1  # 相对于当前节点
      can_self_learn: false
      
      entry_requirements:
        - "掌握至少一种一元二次方程解法"
        - "能进行基本的代数运算"
      
      recommended_learning_path:
        - "先复习直接开方法与配方法"
        - "再学习判别式与解法选择策略"
        - "最后进行综合练习"
    
    - rank: 2
      node_id: "tool_factorization_method_08"
      node_title: "因式分解法求解"
      layer: "tool"
      recommendation_score: 0.82
      # ...
    
    - rank: 3
      node_id: "concept_discriminant_meaning_02"
      node_title: "理解判别式的几何意义"
      layer: "concept"
      recommendation_score: 0.68
      # ...
  
  diversity_guarantee:
    layers_covered: ["skill", "tool", "concept"]
    difficulty_range: [2, 4]
    meets_diversity_requirement: true
  
  alternatives_for_rejection:
    description: "如全部拒绝，可自由浏览完整知识网络"
    knowledge_network_browse_url: "/browse/kn_001"
  
  student_final_choice: null  # 学生选择后填充
  student_rejected_all: false
  choice_timestamp: null
  
  generated_at: "2026-06-15T15:00:00Z"
  auto_expire_at: "2026-06-15T23:59:59Z"  # 推荐24小时后过期
```

### 4.3 学生选择记录输出

```yaml
student_choice_record:
  request_id: "rec_20260615_007"
  student_id: "student_023"
  
  choice:
    selected_node_id: "skill_method_selection_04"
    selection_timestamp: "2026-06-15T15:10:00Z"
    selection_source: "recommended"  # recommended / rejected_all_browsed / teacher_assigned
  
  alternative_actions:
    - action: "rejected_all"
      count: 0  # 本次无拒绝
  
  preference_update:
    # 更新学生偏好模型，用于后续推荐微调
    student_preferences_ref: "/data/students/student_023_preferences.json"
    updated_fields:
      - field: "preferred_layer"
        old_value: "tool"
        new_value: "skill"
      - field: "risk_tolerance"
        old_value: "low"
        new_value: "medium"
  
  next_action:
    type: "launch_virtual_classroom"
    target_node: "skill_method_selection_04"
    session_id: "vc_20260615_002"
```

### 4.4 最终产物输出规格

```yaml
scene005_final_output:
  scene_type: "SCENE-005"
  session_id: "rec_session_20260615_001"
  
  recommendation_request:
    student_id: "student_023"
    current_node: "tool_formula_method_07"
    target_level: "skill"
  
  result_summary:
    candidates_generated: 3
    candidates_displayed: 3
    student_selected: true
    selected_node: "skill_method_selection_04"
    rejected_all: false
  
  algorithm_metrics:
    computation_time_ms: 850
    candidates_considered: 7
    diversity_check_passed: true
  
  follow_up_triggered:
    - type: "SCENE-003"
      target_node: "skill_method_selection_04"
      session_id: "vc_20260615_002"
  
  generated_at: "2026-06-15T15:10:00Z"
  generated_by: "fr06_recommendation_engine"
```

---

## 5. 与其他场景的数据流关系

| 方向 | 场景/FR | 数据内容 | 说明 |
|------|---------|---------|------|
| **输入←** | SCENE-003 | 节点掌握状态确认 | 推荐触发条件 |
| **输入←** | SCENE-004 | 闭环完成通知 | 更新表现分 |
| **输入←** | SCENE-006 | 作业批改结果 | 表现分数据源 |
| **输入←** | SCENE-007 | 学生画像数据 | 个性化推荐依据 |
| **输出→** | SCENE-003 | 启动虚拟教室 | 触发学生学习 |
| **输出→** | FR-12 | 推荐记录持久化 | 选择历史存储 |
| **输出→** | FR-09 | 推荐反馈数据 | 学情分析数据 |

---

## 6. 关键约束

| 约束类型 | 约束内容 | 来源 |
|---------|---------|------|
| **候选约束** | 推荐2~4个候选节点 | FR-06 |
| **多样性约束** | 候选必须覆盖≥2个layer | FR-06 |
| **解释约束** | 每个候选必须附结构化推荐理由 | FR-06 |
| **难度约束** | difficulty跳跃\|Δ\| ≤ 1 | FR-06 |
| **时间约束** | 推荐响应时间≤10秒 | FR-06 |
| **选择权约束** | 学生拥有最终选择权 | FR-06 |
| **数据不足处理** | 历史数据<3个节点时，表现分降为0.5 | FR-06 |

---

## 7. 验收标准

| 验收项 | 验收条件 | 验证方式 |
|-------|---------|---------|
| **VA-001** | 节点掌握后10秒内返回2~4个候选 | 响应时间测试 |
| **VA-002** | 推荐理由自然语言与score_breakdown一致 | 内容一致性校验 |
| **VA-003** | 候选节点保证≥2个layer多样性 | 多样性校验 |
| **VA-004** | 学生选择后SCENE-003可在正确节点启动 | 端到端测试 |
| **VA-005** | 100条历史数据模拟中平均掌握率≥75% | 模拟测试 |
| **VA-006** | 全部拒绝后学生可自由浏览网络 | 流程测试 |
| **VA-007** | 推荐记录正确持久化 | 存储校验 |
| **VA-008** | 候选分数<0.5时扩大搜索范围 | 边界测试 |

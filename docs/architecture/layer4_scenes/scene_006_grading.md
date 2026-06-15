# SCENE-006：作业批改场景

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**场景编号**：SCENE-006  
**关联功能需求**：FR-08（作业批改与评分）、FR-07（错题闭环触发）、FR-13（人机协同）

---

## 1. 场景概述

**一句话描述**：学生提交作业后，系统自动对照参考答案与评分rubric进行结构化批改——给出得分、逐题点评、错误类型归类，并触发错题闭环和节点掌握状态更新。

**参与角色**：
- 批改Agent
- 评分Agent
- 逐题点评Agent
- 错题闭环触发Agent（FR-07）
- 教师复核Agent（FR-13）

---

## 2. 核心流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCENE-006 作业批改核心流程                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  作业提交                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. 学生提交作业                                                      │   │
│  │    - 作业ID、题型、关联节点                                         │   │
│  │    - 题目内容+学生答案                                               │   │
│  │                                                                      │   │
│  │ 2. 教师/系统提供参考答案+评分rubric                                  │   │
│  │                                                                      │   │
│  │ 3. 加载学生历史表现数据（用于节点掌握判定）                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                             │                                                 │
│                             ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      自动批改主流程                                  │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ for each question in homework.questions:                        │  │   │
│  │  │                                                               │  │   │
│  │  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │  │   │
│  │  │   │  答案解析   │  │  逐题评分   │  │  错误归类   │           │  │   │
│  │  │   │   Agent     │──▶│   Agent     │──▶│   Agent     │           │  │   │
│  │  │   └─────────────┘  └─────────────┘  └──────┬──────┘           │  │   │
│  │  │                                             │                  │  │   │
│  │  │                           ┌─────────────────┴──────────────┐   │  │   │
│  │  │                           ▼                                ▼   │  │   │
│  │  │                    [答错]                              [答对]   │  │   │
│  │  │                           │                                │   │  │   │
│  │  │                           ▼                                │   │  │   │
│  │  │                   触发FR-07                           更新   │  │   │
│  │  │                   错题闭环                            掌握状态 │  │   │   │
│  │  │                                                               │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                             │                                                 │
│                             ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      班级汇总与异常检测                              │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ - 聚合全班学生批改数据                                         │  │   │
│  │  │ - 计算平均分、每题错误率                                       │  │   │
│  │  │ - 异常检测：平均分<40% 或 >95% 触发告警                       │  │   │
│  │  │ - 标记需要教师关注的节点                                       │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                             │                                                 │
│                             ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      教师复核接口（FR-13）                           │   │
│  │                                                                      │   │
│  │  教师可：                                                           │   │
│  │  - 查看自动批改结果                                                 │   │
│  │  - 调整分数/添加批注                                                 │   │
│  │  - 标记"待人工批改"题目                                             │   │
│  │                                                                      │   │
│  │  复核后正式归档                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Agent角色定义

| Agent ID | 角色名称 | 框架 | 职责说明 | 特殊要求 |
|----------|---------|------|---------|---------|
| `agent_scene006_grading_001` | 批改Agent | DeepAgents | 整体作业批改流程协调 | 绑定`tpl_scene006_grading_v1.0` |
| `agent_scene006_scorer_002` | 评分Agent | DeepAgents | 对照rubric给出得分 | 绑定`tpl_scene006_scorer_v1.0` |
| `agent_scene006_commentator_003` | 逐题点评Agent | DeepAgents | 生成结构化点评文本 | 绑定`tpl_scene006_commentator_v1.0` |
| `agent_scene006_class_summary_004` | 班级汇总Agent | DeepAgents | 聚合全班数据，计算统计量 | 绑定`tpl_scene006_summary_v1.0` |

**协作模式**：Question-level Parallel（题目间并行批改）

---

## 4. 输入/输出规格

### 4.1 场景输入规格

```yaml
scene006_grading_input:
  request_type: "homework_grading"
  
  homework:
    homework_id: "hw_20260615_001"
    assignment_type: "in_class_test"  # in_class_test / homework / final_exam
    course_ref: "kn_001"
    knowledge_node_ids: ["tool_formula_method_07", "tool_factorization_method_08"]
    submitted_at: "2026-06-15T11:00:00Z"
    duration_minutes: 45
  
  student_id: "student_023"
  
  questions_and_answers:
    - q_id: "q_001"
      content: "用公式法解方程：x² - 5x + 6 = 0"
      student_answer: "x = 2, x = 3"
      max_score: 5
    
    - q_id: "q_002"
      content: "用因式分解法解方程：x² - 3x - 10 = 0"
      student_answer: "x = 5, x = -2"
      max_score: 5
    
    - q_id: "q_003"
      content: "用配方法解方程：x² + 4x + 1 = 0"
      student_answer: "x = -2 + √3, x = -2 - √3"
      max_score: 5
  
  reference_answers_and_rubric:
    - q_id: "q_001"
      correct_answer: "x = 2, x = 3"
      scoring_rubric: |
        写出判别式得1分；正确计算得2分；写出两根各1分。
        步骤完整且正确5分；有小错误4分；结果对但无步骤2分；结果错但公式正确1分。
    
    - q_id: "q_002"
      correct_answer: "x = 5, x = -2"
      scoring_rubric: |
        成功因式分解得3分；正确写出两根各1分。
        步骤完整且正确5分。
    
    - q_id: "q_003"
      correct_answer: "x = -2 + √3, x = -2 - √3"
      scoring_rubric: |
        配方法步骤正确得3分；正确求根各1分。
        完全正确5分。
  
  historical_performance_ref: "/data/students/student_023_performance.json"
  
  grading_config:
    allow_partial_credit: true
    auto_trigger_error_loop: true
    teacher_review_required: false
```

### 4.2 个人批改结果输出

```yaml
homework_grading_result:
  homework_id: "hw_20260615_001"
  student_id: "student_023"
  
  total_score: 9
  max_total_score: 15
  score_percentage: 0.60
  
  graded_at: "2026-06-15T11:05:00Z"
  grading_mode: "auto"  # auto / teacher_reviewed / mixed
  
  per_question_results:
    - q_id: "q_001"
      content: "用公式法解方程：x² - 5x + 6 = 0"
      student_answer: "x = 2, x = 3"
      correct_answer: "x = 2, x = 3"
      scored: 5
      max_score: 5
      is_correct: true
      
      scoring_details: |
        判别式 Δ = 25 - 24 = 1 ... 1分
        x = (5±1)/2 计算正确 ... 2分
        两根 x=2, x=3 ... 2分
        合计：5分
      
      scoring_reason: "步骤完整，答案正确。判别式 Δ = 25 - 24 = 1，正确计算了 x = (5 ± 1) / 2"
      
      error_type: null
      triggered_error_loop_id: null
    
    - q_id: "q_002"
      content: "用因式分解法解方程：x² - 3x - 10 = 0"
      student_answer: "x = 5, x = -2"
      correct_answer: "x = 5, x = -2"
      scored: 4
      max_score: 5
      is_correct: true
      
      scoring_details: |
        因式分解 (x-5)(x+2) 正确 ... 3分
        两根正确各0.5分 ... 1分
        缺少中间展开验证步骤 ... -1分
      
      scoring_reason: "因式分解正确 (x - 5)(x + 2)，但步骤中缺少中间展开验证，扣1分"
      
      error_type: null
      triggered_error_loop_id: null
    
    - q_id: "q_003"
      content: "用配方法解方程：x² + 4x + 1 = 0"
      student_answer: "x = -2 + √3, x = -2 - √3"
      correct_answer: "x = -2 + √3, x = -2 - √3"
      scored: 0
      max_score: 5
      is_correct: false
      
      scoring_details: |
        学生答案：x = -2 + √3, x = -2 - √3
        正确答案：x = -2 + √3, x = -2 - √3
        形式一致，但学生使用了近似值符号而非精确表示
      
      scoring_reason: |
        学生将 √3 写成 √3（约等于1.732），而正确答案要求保留根号形式。
        这是审题错误（未注意题目对结果形式的要求）。
      
      error_type: "reading"  # concept / computational / reading / prerequisite
      
      triggered_error_loop_id: "err_loop_20260615_002"
  
  node_mastery_after_homework:
    - node_id: "tool_formula_method_07"
      mastery_confirmed: true
      cumulative_accuracy: 0.92
      evidence:
        - "本作业 q_001 正确"
        - "上一次虚拟教室正确率 90%"
      mastery_trend: "improving"
    
    - node_id: "tool_factorization_method_08"
      mastery_confirmed: false
      cumulative_accuracy: 0.65
      evidence:
        - "本作业 q_002 基本正确但步骤不完整"
        - "相关错题闭环进行中"
      mastery_trend: "stable"
  
  teacher_review:
    reviewed: false
    review_comments: []
    score_adjustments: {}
  
  recommended_follow_up:
    type: "error_loop_in_progress"  # advance_to_next_node / stay_and_retry / error_loop_in_progress
    error_loop_ids: ["err_loop_20260615_002"]
    target_next_node: null
```

### 4.3 班级汇总输出

```yaml
class_summary:
  homework_id: "hw_20260615_001"
  
  class_id: "class_003"
  total_students: 30
  submitted_count: 28
  not_submitted_count: 2
  not_submitted_student_ids: ["student_007", "student_019"]
  
  overall_statistics:
    average_score: 7.2
    max_score: 15
    median_score: 7.0
    std_deviation: 2.1
    
    score_distribution:
      "13-15分": 5
      "10-12分": 10
      "7-9分": 8
      "4-6分": 4
      "0-3分": 1
  
  per_question_statistics:
    - q_id: "q_001"
      average_score: 4.6
      max_score: 5
      error_rate: 0.14
      correct_count: 24
      incorrect_count: 4
      
      common_errors: []
    
    - q_id: "q_002"
      average_score: 4.2
      max_score: 5
      error_rate: 0.21
      correct_count: 22
      incorrect_count: 6
      
      common_errors:
        - type: "concept"
          count: 3
          description: "因式分解常数项符号错误"
        - type: "computational"
          count: 3
          description: "计算错误"
    
    - q_id: "q_003"
      average_score: 2.8
      max_score: 5
      error_rate: 0.57
      correct_count: 12
      incorrect_count: 16
      
      common_errors:
        - type: "reading"
          count: 8
          description: "未注意结果形式要求"
        - type: "computational"
          count: 5
          description: "配方法步骤不完整"
        - type: "concept"
          count: 3
          description: "配方后求根公式应用错误"
  
  flagged_nodes_for_attention:
    - node_id: "tool_factorization_method_08"
      class_mastery_rate: 0.57
      error_rate: 0.21
      attention_level: "medium"
      teacher_recommendation: "增加配方法的专项练习"
    
    - node_id: "tool_completion_method_09"
      class_mastery_rate: 0.43
      error_rate: 0.57
      attention_level: "high"
      teacher_recommendation: "全班普遍对配方法掌握不足，建议增加1课时专项训练"
  
  anomaly_alerts:
    - type: "low_average"
      threshold: 0.40
      actual: 0.48
      q_id: "q_003"
      message: "第3题平均分低于40%阈值，请确认参考答案正确性"
      action_required: true
  
  generated_at: "2026-06-15T11:10:00Z"
  generated_by: "fr08_grading_engine"
```

### 4.4 最终产物输出规格

```yaml
scene006_final_output:
  scene_type: "SCENE-006"
  homework_id: "hw_20260615_001"
  
  processing_summary:
    total_questions: 3
    auto_graded: 3
    pending_manual_review: 0
    error_loops_triggered: 1
  
  per_student_results:
    - student_id: "student_023"
      total_score: 9
      status: "completed"
      per_question_results: [...]

  class_summary_ref: "/data/hw/hw_20260615_001/class_summary.yaml"
  
  artifacts_persisted:
    - type: "homework_grading_result"
      path: "/homework/hw_20260615_001/student_023/grading_result.yaml"
    - type: "class_summary"
      path: "/homework/hw_20260615_001/class_summary.yaml"
    - type: "error_loop_trigger"
      path: "/data/err/trigger_err_loop_20260615_002.yaml"
  
  generated_at: "2026-06-15T11:10:00Z"
  generated_by: "fr08_grading_engine"
```

---

## 5. 与其他场景的数据流关系

| 方向 | 场景/FR | 数据内容 | 说明 |
|------|---------|---------|------|
| **触发→** | SCENE-004 | FR-07错题闭环 | 答错题触发 |
| **触发→** | SCENE-007 | 学情分析数据 | 班级汇总数据 |
| **输出→** | SCENE-005 | 节点掌握状态 | 推荐引擎使用 |
| **输出→** | FR-12 | 批改记录持久化 | 不可变记录 |
| **输出→** | FR-14 | 审计日志 | 操作追踪 |
| **教师复核→** | FR-13 | 复核记录 | 人机协同 |

---

## 6. 关键约束

| 约束类型 | 约束内容 | 来源 |
|---------|---------|------|
| **一致性约束** | 同类题评分一致性偏差≤5% | FR-08 |
| **异常检测** | 平均分<40%或>95%触发告警 | FR-08 |
| **不可变约束** | 批改记录写入后不可修改 | FR-12 |
| **闭环约束** | 答错题必须触发FR-07 | DP-ARCH-12 |
| **教师复核** | 教师可覆盖评分，记录原值 | FR-08 |

---

## 7. 验收标准

| 验收项 | 验收条件 | 验证方式 |
|-------|---------|---------|
| **VA-001** | 对标准作业可完成自动评分与逐题点评 | 端到端测试 |
| **VA-002** | 同类题评分一致性最大分差≤0.5分 | 一致性测试 |
| **VA-003** | 错题100%触发FR-07闭环 | 触发率测试 |
| **VA-004** | 平均分异常正确触发告警 | 边界测试 |
| **VA-005** | 批改数据正确驱动节点掌握状态更新 | 状态一致性校验 |
| **VA-006** | 班级汇总统计正确 | 数据校验 |
| **VA-007** | 批改记录正确持久化，不可修改 | 持久化测试 |
| **VA-008** | 教师复核覆盖评分保留原值记录 | 复核流程测试 |

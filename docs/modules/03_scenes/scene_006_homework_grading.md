# SCENE-006：作业批改

**父文档**：[system_requirements.md](../../system_requirements.md) · [场景索引](../03_user_roles_scenes_index.md)
**相关决策**：[dp_arch_04](../../decisions/dp_arch_04.md), [dp_arch_12](../../decisions/dp_arch_12.md)

---

### 3.2.6 SCENE-006：作业批改

**场景目标**：学生完成随堂测试/课后作业/结课考核后，系统自动评分、生成逐题点评、给出单个学生的学习评估与后续建议，同时生成全班学情分析。

**核心设计原则**：
1. **不同场景不同评阅策略**（随堂/课后/结课考核）
2. **错题触发 SCENE-004 节点内错题闭环**
3. **数据自动写入 SCENE-007 学情分析**

#### Agent 角色定义

| Agent 角色 | 框架 | 数量 | 职责边界 |
|-----------|------|------|---------|
| 答题解析 Agent | DeepAgents | 1 | 读取并结构化学生答案（支持文本/图片/手写） |
| 逐题批改 Agent | DeepAgents | N | 对照标准答案与评分标准逐题评定 |
| 学习建议 Agent | DeepAgents | 1 | 基于错题分布生成个性化建议 |
| 班级汇总 Agent | DeepAgents | 1 | 汇总全班数据，生成学情分析摘要 |

#### 交互流程

```
学生提交作业 → 答题解析 → 逐题批改
                           │
                    错题触发 SCENE-004
                           │
                           ▼
               学习建议 Agent → 班级汇总 Agent
                           │
                           ▼
                  持久化所有批改记录
```

#### 输入规格

```yaml
homework_submission:
  homework_id: "hw_001"
  homework_type: "in_class_test"
  student_id: "s_001"
  questions:
    - q_id: "q_001"
      content: "用消元法解：2x+3y=13, 3x+2y=12"
      student_answer: "x=2, y=3"
      max_score: 5
  reference_answers:
    - q_id: "q_001"
      correct_answer: "x=2, y=3"
      scoring_rubric: "步骤完整且正确5分；步骤有小错误4分..."
```

#### 输出规格（摘要版）

```yaml
homework_result:
  homework_id: "hw_001"
  student_id: "s_001"
  total_score: 28
  max_total_score: 30
  score_percentage: 0.93
  question_results:
    - q_id: "q_001"
      scored: 5
      is_correct: true
      scoring_reason: "步骤完整，答案正确"
    - q_id: "q_002"
      scored: 3
      is_correct: false
      error_type: "computational"
      triggered_error_loop: true
      error_loop_id: "err_loop_002"
  node_mastery_after_homework:
    node_id: "tool_elimination_method"
    mastery_confirmed: true
    accuracy: 0.93
  recommended_follow_up:
    type: "advance_to_next_node"
    target_next_node: "skill_model_solve_system"
  class_summary:
    average_score: 22
    common_errors: ["符号处理", "消元步骤遗漏系数"]
```

#### 边界与异常

| 异常场景 | 系统行为 |
|---------|---------|
| 学生答案格式无法解析 | 标记为"待人工批改"，记录 ERR-HW-001 |
| 未提供参考答案 | 降级为"仅记录学生答案，不自动评分"，等待教师提供后重批 |
| 全班平均分异常（<40% 或 >95%） | 触发 Harness 告警，提示教师确认参考答案是否正确 |
| 批改 Agent 3 次重试后仍无法评分 | 标记为"待人工批改"，不影响其他作业 |

---


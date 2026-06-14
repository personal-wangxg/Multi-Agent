# DP-ARCH-12：节点内错题闭环

**确认日期**：2026-06-12 · **确认人**：项目核心团队 · **决策类别**：架构

---

## 决策摘要

当学生在虚拟教室（SCENE-003）或作业批改（SCENE-006）中答错某题时，系统自动启动**诊断 → 补充讲解 → 同类新题 → 再评估**的微观学习闭环。连续 2 次答对同类题 或 累计正确率 ≥ 80% 时标记为"节点内已掌握"。诊断为"前置知识缺失"时自动推荐返回前序节点复习。默认重试上限 3 次，超过则标记为"需要教师关注"。

## 核心设计原则

1. **诊断优先：先分析错误本质，不是简单"再出一题，
2. **针对性补充：根据诊断结果给不同的补充讲解/资源推荐，
3. **递进练习：新题与原题同类型但不同难度/角度/情境，避免记答案，
4. **渐进退出：掌握后标记，未掌握但达重试上限时标记"需要教师关注，
5. **跨节点联动：诊断为"前置知识缺失"时推荐返回前序节点复习。

## 关键细节

### 错误类型分类

| 错误类型 | 英文标签 | 诊断依据 | 推荐策略 |
|---------|---------|---------|---------|
| 概念误解 | concept | 错误反映根本原理理解偏差 | 返回概念层节点重新讲解 |
| 计算错误 | computational | 符号运算/数值计算错误 | 给出计算步骤详解 + 提醒 |
| 审题偏差 | reading | 未正确理解题目要求 | 训练审题方法 |
| 前置知识缺失 | prerequisite | 需要未掌握的前序节点知识 | 推荐返回前序节点复习 |

### 闭环完整流程

```
触发条件：学生在 SCENE-003 / SCENE-006 中答错某题
   │
   ▼
┌────────────────────────────────────┐
│ 错题诊断 Agent                    │
│ 输出：error_type / specific_cause  │
│       / severity / prerequisite    │
└──────────────┬────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│ 补充讲解 Agent                    │
│ 基于 error_type 生成针对性讲解    │
│ 或推荐资源片段                    │
└──────────────┬────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│ 同类题生成 Agent                  │
│ 生成同考点但不同难度/角度的新题  │
│ 不直接复用原题（避免记答案）      │
└──────────────┬────────────────────┘
               │
               ▼
           学生完成新题
               │
               ▼
┌────────────────────────────────────┐
│ 评估 Agent                        │
│ 判断是否达成"节点内已掌握"        │
│                                   │
│ 掌握条件（任一成立）：            │
│   · 连续 2 次答对同类题           │
│   · 同类题累计正确率 ≥ 80%        │
└──────────────┬────────────────────┘
               │
               ├── 掌握 → 返回原节点流程
               │
               └── 未掌握，重试次数 < MAX_ATTEMPTS → 再次进入闭环
               │
               └── 未掌握，重试次数 ≥ MAX_ATTEMPTS →
                         标记"需要教师关注"
                         + 记录为"难点节点"
                         + 在学情分析中特别标记
```

### error_loop_record 输出结构

```yaml
error_loop_record:
  loop_id: "err_loop_001"
  node_id: "tool_elimination_method"
  original_error:
    question_id: "ex_b_003"
    diagnostic:
      error_type: "computational"
      specific_cause: "第二个方程在变形为 x=... 时符号处理错误"
      severity: "medium"
      prerequisite_knowledge_gap: null
    supplementary_explanation:
      approach: "step_by_step_review"
      content: "让我们重新检查第二个方程的变形过程..."
      resources_recommended: ["教材第一章例2", "可汗学院视频片段"]
  attempts:
    - attempt_number: 1
      new_question_id: "ex_b_003_v2"
      new_question_content: "同类型新题描述"
      student_answer: "x=3, y=2"
      is_correct: true
      mastery_after_this_attempt: false
  final_status: "mastered"    # mastered / needs_teacher_attention / not_mastered
  total_attempts: 1
  recommendation: "学生已掌握该题型，可返回原节点继续"
  triggered_at: "2026-06-12T10:45:00Z"
  completed_at: "2026-06-12T10:50:00Z"
```

### 重试上限与状态转移

| 条件 | final_status | 后续行动 |
|-----|-------------|---------|
| 连续 2 次答对同类题 | mastered | 返回原节点流程 |
| 累计正确率 ≥ 80% | mastered | 返回原节点流程 |
| 重试 ≥ MAX_ATTEMPTS 且未掌握 | needs_teacher_attention | 标记为"难点节点"，学情分析高亮 |
| 诊断为前置知识缺失 | not_mastered | 推荐返回前序节点复习 |
| 同类题 Agent 3 次生成失败 | needs_teacher_attention | 降级为从题库随机抽取 |

## 影响范围

- 关联 FR：FR-07（节点内错题闭环）、FR-09（学情分析）；
- 关联场景：SCENE-003（虚拟教室）、SCENE-004（节点内错题闭环）、SCENE-006（作业批改）、SCENE-007（学情分析）。

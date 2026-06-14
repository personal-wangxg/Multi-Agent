# SCENE-003：虚拟教室

**父文档**：[system_requirements.md](../../system_requirements.md) · [场景索引](../03_user_roles_scenes_index.md)
**相关决策**：[dp_arch_05](../../decisions/dp_arch_05.md), [dp_arch_09](../../decisions/dp_arch_09.md)

---

**场景目标**：真实学生在系统中自主学习时，由 AI 教师 + N 个 AI 同学 + 真实学生组成虚拟课堂。AI 教师负责按知识网络节点的教学要求推进学习过程、调用已有教学资源、发起课堂互动、合理引导学生理解。AI 学生模拟真实同学行为：回答问题、提出疑问、与其他同学（包括真实学生）讨论、互相评价。

**核心设计原则**：
1. 虚拟教室是**一个节点的完整学习体验**（不是整节课的缩影），学生学完该节点后由节点推荐引擎推荐下一节点
2. AI 教师按已确认的教案+学案推进，**不自由发挥**
3. 教学资源直接引用 SCENE-002 备课辅助输出的资源（按节点切片）
4. 支持不同模式：讲解模式 / 问答模式 / 讨论模式 / 练习模式
5. **真实学生在虚拟教室中的表现会影响节点掌握标记**

#### Agent 角色定义

| Agent 角色 | 框架 | 数量 | 职责边界 |
|-----------|------|------|---------|
| AI 教师 Agent | AgentScope | 1 | 按教案+学案推进学习，讲解要点，提问引导，控制节奏，调用资源，给予点评 |
| AI 学生 Agent | AgentScope | N（可配，默认 3） | 模拟不同水平的学生行为：回答问题、发起质疑、与真实学生讨论、互相评价 |
| 课堂记录 Agent | DeepAgents | 1 | 记录学习过程、节点进度、互动数据、生成节点总结 |

#### 交互流程

```
学生进入虚拟教室
  │
  ▼
系统识别学生当前所在节点（由学习路径决定）
  │
  ▼
加载 SCENE-002 输出的教案+学案+教学资源
  │
  ▼
  ┌──────────────────────────────────────┐
  │ AI 教师 Agent                       │
  │ 按教案步骤推进：                    │
  │   · 导入：用情境引入                │
  │   · 新授：讲解要点，穿插提问        │
  │   · 练习：学生完成练习题            │
  │   · 讨论：AI 学生+真实学生讨论      │
  │   · 总结：AI 教师总结 + 学生记录    │
  │ 过程中调用节点资源（PPT/题库/视频   │
  └──────────────┬───────────────────────┘
                 │
         ┌───────┴──────────────────┐
         ▼                           ▼
  ┌────────────────────┐   ┌────────────────────┐
  │ AI 学生 Agent      │   │ 真实学生           │
  │ 模拟真实同学行为  │   │ 学习+答题+互动     │
  │ 回答问题+讨论+评价│   │ （与 AI 学生互动）│
  └──────────┬─────────┘   └──────────┬─────────┘
             │                        │
             └────────────┬──────────┘
                          ▼
  ┌──────────────────────────────────────┐
  │ 课堂记录 Agent                      │
  │ 记录：                              │
  │   · 节点学习进度                    │
  │   · 学生答题情况                    │
  │   · 互动数据（AI 与真实）           │
  │   · 易错点/困难点                  │
  │   · 节点总结                       │
  └──────────────┬───────────────────────┘
                 │
                 ▼
  节点内错题闭环触发（当学生答错时，见 SCENE-004）
                 │
                 ▼
           标记节点掌握状态：
             · 掌握：节点推荐引擎（SCENE-005）
             · 未掌握：进入错题闭环 → 再评估
                 │
                 ▼
         持久化节点学习记录
```

#### 输入规格

```yaml
session_type: "virtual_classroom"
student_id: "s_001"                              # 必填，真实学生ID
knowledge_network_ref: "kn_001"                  # 必填，引用课程规划知识网络
current_node_id: "tool_elimination_method"       # 必填，学生当前所处节点
ai_student_count: 3                              # 选填，默认3
ai_student_profiles:                             # 选填，AI学生的角色设定
  - id: "ai_s_01"
    name: "好奇的小明"
    profile: "积极提问，喜欢追问'为什么'"
  - id: "ai_s_02"
    name: "细心的小红"
    profile: "回答认真，善于发现他人错误"
  - id: "ai_s_03"
    name: "严谨的小华"
    profile: "思维严谨，偏爱方法性讨论"
teaching_resource_ref: "res_tool_elimination_method"  # 必填，引用SCENE-002输出的资源
session_mode: "mixed"                               # lecture/qa/discussion/exercise/mixed
max_duration_minutes: 30                           # 选填，一次虚拟教室最长时长
```

#### 输出规格

```yaml
session_summary:
  session_id: "vc_20260612_001"
  target_node_id: "tool_elimination_method"
  student_id: "s_001"
  node_completed: true                              # true/false
  mastery_level_marked: "tool"                      # 该节点在哪个层级掌握（与节点layer匹配）
  learning_durations_minutes: 25
  student_responses:
    - id: "resp_001"
      turn_number: 3
      type: "answer"
      content: "我觉得应该消去 y，因为两式中 y 的系数可以通过乘以相同的数使其一致"
      correct: true
      ai_teacher_feedback: "很好的观察！你发现了消元法的关键——系数对齐"
  ai_student_discussions:
    - id: "disc_001"
      topic: "消去 x 还是消去 y 更好"
      participants: ["ai_s_01", "ai_s_02", "s_001"]
      summary: "学生们讨论了两种消元策略，发现根据系数特点选择可以简化计算"
  incorrect_answers:
    - question_id: "ex_b_003"
      wrong_answer_attempted: "x=5, y=-1"
      error_type: "计算错误（符号）"
      correction_hint: "再检查第二个方程中 x 的系数变形"
  resources_used:
    - type: "exercise"
      ref: "ex_b_001"
    - type: "ppt_outline"
      ref: "slide_2"
  error_node_triggered: true                    # 是否触发节点内错题闭环
  notes_for_next_node: ["该学生掌握较快，下一节点建议跳过基础讲解，直接进入练习"]
  mastery_confirmed: true                       # 综合表现确认是否掌握该节点
  next_step_reason: "已完成消元法所有练习，正确率90%，符合掌握标准"
```

#### 边界与异常

| 异常场景 | 系统行为 |
|---------|---------|
| 指定节点不存在对应的教学资源 | 提示 ERR-RES-001："节点未完成备课，请先完成 SCENE-002" |
| 虚拟教室运行超过 max_duration | AI 教师发起"时间到了，我们先总结本次学到的要点"，自动推进到结束流程 |
| AI 学生连续 3 轮无响应 | 课堂记录 Agent 标记为"静默学生"，AI 教师不再对其提问 |
| AI 学生发言涉及不当内容 | Harness 内容过滤拦截，消息被静默丢弃，触发告警并记录 |
| 真实学生连续 10 分钟无交互 | AI 教师主动发起引导性问题："你对这一步有什么想法吗？" |
| 真实学生打断并改变话题 | AI 教师按节点目标约束："这是一个很好的问题，但我们当前的目标是掌握消元法。等完成后我们再讨论你提出的问题" |
| 学生答题后触发节点内错题闭环 | 自动启动 SCENE-004 流程 |
| 节点完成后但掌握标记未通过 | 不推进到下一节点，进入错题闭环 → 重新评估 |
| 系统崩溃 | 恢复最后保存的会话状态，从断点继续 |

---


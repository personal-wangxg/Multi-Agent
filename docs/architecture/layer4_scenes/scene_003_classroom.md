# SCENE-003：虚拟教室场景

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**场景编号**：SCENE-003  
**关联功能需求**：FR-03（Agent编排调度）、FR-04（框架协议转换）、FR-06（节点推荐）、FR-07（错题闭环）、FR-13（人机协同）

---

## 1. 场景概述

**一句话描述**：学生在知识网络的某个节点上完成学习体验，通过AI教师Agent与AI学生Agent的交互（使用AgentScope框架）进行自适应学习，系统记录学习过程并更新节点掌握状态。

**参与角色**：
- 学生（主要学习者）
- AI教师Agent（使用AgentScope框架）
- AI学生Agent（使用AgentScope框架，模拟学生）
- 学习路径导航Agent（DeepAgents）
- 节点掌握判定Agent
- 编排调度Agent（FR-03）

---

## 2. 核心流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCENE-003 虚拟教室核心流程                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  进入虚拟教室的条件                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. 学生完成上一个节点并确认掌握（FR-06推荐 or 自主选择）               │   │
│  │ 2. 或 学生直接选择进入某个节点学习                                   │   │
│  │ 3. 或 教师指定学生进入特定节点                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  启动流程                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                 │
│  │ FR-06推荐    │    │ 学生自主选择  │    │ 教师指定    │                 │
│  │ 结果触发     │    │              │    │             │                 │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                 │
│         │                   │                   │                          │
│         └───────────────────┼───────────────────┘                          │
│                             ▼                                               │
│              ┌──────────────────────────────┐                               │
│              │ 加载 teaching_package         │                               │
│              │ 加载 节点掌握状态             │                               │
│              │ 初始化 AgentScope 会话        │                               │
│              └──────────────┬───────────────┘                               │
│                             ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      AgentScope 虚拟教室环境                          │   │
│  │                                                                     │   │
│  │  ┌──────────────┐                          ┌──────────────┐        │   │
│  │  │  AI教师Agent │←─────Message Hub─────→│  AI学生Agent  │        │   │
│  │  │             │                          │  (学生模拟)   │        │   │
│  │  └──────────────┘                          └──────┬───────┘        │   │
│  │         │                                           │                │   │
│  │         │    ┌──────────────────────────────────────┘                │   │
│  │         │    │                                                       │   │
│  │         ▼    ▼                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                    学习过程循环                               │   │   │
│  │  │                                                              │   │   │
│  │  │   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐    │   │   │
│  │  │   │  概念   │──▶│  示例   │──▶│  练习   │──▶│  反馈   │    │   │   │
│  │  │   │  讲解   │   │  演示   │   │  尝试   │   │  评价   │    │   │   │
│  │  │   └─────────┘   └─────────┘   └────┬────┘   └────┬────┘    │   │   │
│  │  │                                      │            │         │   │   │
│  │  │                              ┌────────┴────────────┴─────┐   │   │   │
│  │  │                              ▼                          ▼   │   │   │
│  │  │                       [答对]                      [答错]    │   │   │
│  │  │                          │                          │     │   │   │
│  │  │                          ▼                          ▼     │   │   │
│  │  │                  更新掌握状态                  触发FR-07    │   │   │
│  │  │                  进入下一知识点                  错题闭环   │   │   │
│  │  │                                                              │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  离开虚拟教室的条件                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. 学生完成节点内所有知识点学习                                      │   │
│  │ 2. 节点掌握状态达到mastered标准（FR-07闭环后）                       │   │
│  │ 3. 或 学生主动退出（记录为incomplete）                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 AI教师Agent与AI学生Agent交互流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AgentScope AI教师 ↔ AI学生 交互序列                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  AI教师Agent                           AI学生Agent                          │
│  ┌──────────────────┐                  ┌──────────────────┐              │
│  │ Persona:          │                  │ Persona:          │              │
│  │ - 专业知识扎实    │                  │ - 模拟真实学生    │              │
│  │ - 引导式教学      │                  │ - 会犯错、会提问  │              │
│  │ - 及时反馈        │                  │ - 有个性差异      │              │
│  └────────┬─────────┘                  └────────┬─────────┘              │
│           │                                        │                       │
│           │ 1. 发送学习任务                         │                       │
│           │─────────────────────────────────────────▶                       │
│           │                                        │                       │
│           │                        2. 学生尝试回答 / 提出疑问             │
│           │◀─────────────────────────────────────────                       │
│           │                                        │                       │
│           │ 3. 针对性讲解 / 解答疑惑               │                       │
│           │─────────────────────────────────────────▶                       │
│           │                                        │                       │
│           │                        4. 继续练习 / 巩固                       │
│           │◀─────────────────────────────────────────                       │
│           │                                        │                       │
│           │ ... (循环直到掌握或退出) ...           │                       │
│           │                                        │                       │
│           │ 5. 节点完成评估                        │                       │
│           │─────────────────────────────────────────▶                       │
│           │                                        │                       │
│           │                        6. 生成学习记录                         │
│           │◀─────────────────────────────────────────                       │
│           │                                        │                       │
└───────────┴────────────────────────────────────────┴───────────────────────┘
                                                                             
                                     │
                                     ▼
                         ┌─────────────────────────┐
                         │ FR-07 错题闭环触发      │
                         │ (如AI学生答错)          │
                         └─────────────────────────┘
```

---

## 3. Agent角色定义

| Agent ID | 角色名称 | 框架 | 职责说明 | 特殊要求 |
|----------|---------|------|---------|---------|
| `agent_scope_teacher_001` | AI教师Agent | AgentScope | 主导教学过程，提供讲解、提问、反馈 | 绑定AgentScope教师模板 |
| `agent_scope_student_001` | AI学生Agent | AgentScope | 模拟学生学习，犯错触发闭环 | 绑定AgentScope学生模板 |
| `agent_scene003_path_nav_002` | 学习路径导航Agent | DeepAgents | 管理节点内学习顺序，监控进度 | 绑定`tpl_scene003_nav_v1.0` |
| `agent_scene003_mastery判定_003` | 节点掌握判定Agent | DeepAgents | 基于闭环结果判定节点掌握状态 | 绑定`tpl_scene003_mastery_v1.0` |

**协作模式**：
- AgentScope内部：AI教师 ↔ AI学生通过Message Hub通信
- DeepAgents ↔ AgentScope：通过FR-04协议转换层通信

---

## 4. 输入/输出规格

### 4.1 场景输入规格

```yaml
scene003_classroom_input:
  request_type: "virtual_classroom"
  
  student_id: "student_023"
  current_node_id: "tool_formula_method_07"
  
  knowledge_network_ref: "kn_001"
  teaching_package_ref: "/teaching_packages/kn_001/v1.0/tool_formula_method_07/"
  
  entry_point:
    source: "recommendation"  # recommendation / student_choice / teacher_assignment
    recommendation_id: "rec_20260615_001"  # 如来自推荐
    student_choice_reason: null
  
  session_config:
    max_duration_minutes: 45
    allow_early_exit: true
    auto_save_interval_seconds: 30
  
  historical_performance:
    # 用于AI教师个性化调整
    student_error_patterns: ["符号处理错误", "判别式计算"]
    student_preferred_difficulty: "medium"
```

### 4.2 虚拟教室会话状态

```yaml
virtual_classroom_session:
  session_id: "vc_20260615_001"
  student_id: "student_023"
  node_id: "tool_formula_method_07"
  
  status: "in_progress"  # not_started / in_progress / completed / interrupted
  
  learning_progress:
    current_phase: "practice"  # concept / example / practice / feedback
    concepts_covered: ["求根公式推导", "判别式计算"]
    concepts_remaining: ["实际应用"]
    progress_percentage: 0.70
  
  interaction_log:
    - turn_id: 1
      speaker: "teacher"
      action: "explain"
      content: "今天我们学习公式法求解一元二次方程..."
      duration_seconds: 180
    
    - turn_id: 2
      speaker: "student"
      action: "ask_question"
      content: "老师，判别式Δ为什么要大于等于0才有实数解？"
    
    - turn_id: 3
      speaker: "teacher"
      action: "explain"
      content: "这是因为..."
    
    - turn_id: 4
      speaker: "student"
      action: "attempt"
      question_id: "ex_prac_001"
      student_answer: "x = 2, x = -1"
      is_correct: false
    
    - turn_id: 5
      speaker: "teacher"
      action: "error_feedback"
      error_type: "computational"
      explanation: "注意这里符号处理..."
  
  current_mastery_status:
    estimated_mastery_level: 0.65  # 实时估计
    consecutive_correct: 1
    attempts_this_session: 3
    accuracy_so_far: 0.67
  
  start_time: "2026-06-15T14:00:00Z"
  last_update_time: "2026-06-15T14:25:00Z"
```

### 4.3 节点掌握状态更新输出

```yaml
node_mastery_update:
  node_id: "tool_formula_method_07"
  student_id: "student_023"
  
  session_id: "vc_20260615_001"
  
  mastery_status: "in_progress"  # not_started / in_progress / mastered / needs_teacher_attention
  
  evidence:
    - session_id: "vc_20260615_001"
      source: "virtual_classroom"
      accuracy: 0.67
      attempts: 3
      consecutive_correct: 1
      timestamp: "2026-06-15T14:30:00Z"
  
  next_recommended_action: "continue_practice"  # continue_practice / trigger_error_loop / mark_mastered
  
  updated_ltm: true  # 是否更新长期记忆
  
  next_node_recommendation_ref: null  # 待FR-06生成
```

### 4.4 最终产物输出规格

```yaml
scene003_final_output:
  scene_type: "SCENE-003"
  session_id: "vc_20260615_001"
  student_id: "student_023"
  node_id: "tool_formula_method_07"
  
  completion_status: "completed"  # completed / interrupted / needs_attention
  
  session_summary:
    total_duration_minutes: 35
    phases_completed: ["concept", "example", "practice"]
    questions_attempted: 5
    questions_correct: 3
    overall_accuracy: 0.60
  
  mastery_result:
    final_mastery_status: "in_progress"
    consecutive_correct_required: 2
    current_consecutive_correct: 1
    note: "需要再完成1次连续正确方可标记为mastered"
  
  error_loops_triggered:
    - loop_id: "err_loop_20260615_001"
      error_type: "computational"
      triggered_at: "2026-06-15T14:20:00Z"
      status: "in_progress"
  
  interaction_data_for_analytics:
    learning_time_per_phase:
      concept: 10
      example: 8
      practice: 17
    student_questions_asked: 2
    teacher_explanations_given: 4
  
  artifacts:
    - type: "session_transcript"
      path: "/data/vc/vc_20260615_001/transcript.yaml"
    - type: "mastery_update"
      path: "/data/mastery/student_023_tool_formula_method_07.json"
  
  generated_at: "2026-06-15T14:35:00Z"
  generated_by: "agentscope_session_manager"
```

---

## 5. 与其他场景的数据流关系

| 方向 | 场景/FR | 数据内容 | 说明 |
|------|---------|---------|------|
| **输入←** | SCENE-001 | `kn_001`, `teaching_package` | 知识网络和备课产出作为学习内容 |
| **输入←** | SCENE-005 | 推荐结果触发进入 | 学生完成推荐后进入虚拟教室 |
| **输入←** | FR-04 | 跨框架协议转换 | DeepAgents ↔ AgentScope通信 |
| **触发→** | SCENE-004 | FR-07错题闭环 | 答错题时触发 |
| **触发→** | SCENE-005 | 节点掌握状态 | 完成后触发推荐下一节点 |
| **输出→** | SCENE-007 | 学习记录数据 | 学情分析使用 |
| **输出→** | FR-12 | 会话记录持久化 | 配置持久化 |

---

## 6. 关键约束

| 约束类型 | 约束内容 | 来源 |
|---------|---------|------|
| **框架约束** | AI教师/AI学生Agent必须使用AgentScope框架 | DP-ARCH-04 |
| **协议约束** | 与DeepAgents通信必须通过FR-04协议转换层 | FR-04 |
| **Token约束** | 上下文窗口控制：单次会话输入≤模型窗口50% | DP-ARCH-10 |
| **闭环约束** | 答错题必须触发FR-07错题闭环 | DP-ARCH-12 |
| **状态约束** | 节点掌握状态必须与FR-07闭环结果一致 | FR-07 |
| **记录约束** | 所有交互必须记录用于学情分析 | FR-09 |
| **安全约束** | 学生数据不得在跨框架传输中泄露 | FR-04 |

---

## 7. 验收标准

| 验收项 | 验收条件 | 验证方式 |
|-------|---------|---------|
| **VA-001** | AgentScope AI教师/学生可正常对话交互≥10轮 | 集成测试 |
| **VA-002** | 答错题100%触发FR-07错题闭环 | 错误注入测试 |
| **VA-003** | 节点掌握状态在闭环完成后正确更新 | 状态一致性校验 |
| **VA-004** | AgentScope ↔ DeepAgents跨框架通信成功 | 协议转换测试 |
| **VA-005** | 会话记录正确持久化至FR-12 | 存储校验 |
| **VA-006** | 学生可主动退出（标记为incomplete） | 流程测试 |
| **VA-007** | AI教师可根据学生历史表现调整难度 | 个性化测试 |
| **VA-008** | 单会话Token不超过限制 | Token监控测试 |
| **VA-009** | 虚拟教室可从FR-06推荐结果直接启动 | 端到端测试 |
| **VA-010** | 学习过程数据可被SCENE-007正确读取 | 数据流校验 |

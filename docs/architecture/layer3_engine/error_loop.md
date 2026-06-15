# 节点内错题闭环详细设计

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-07（节点内错题闭环）

---

## 1. 设计目标

节点内错题闭环是 EduAgents 实现个性化补救教学的核心机制。当学生在学习过程中答错题目时，系统自动触发"诊断→补充讲解→同类题→再评估"的四步闭环流程，确保学生真正理解和掌握知识点。

| 设计原则 | 说明 |
|---------|------|
| **精准诊断** | 准确识别错误类型，避免"头痛医头"式补救 |
| **即时反馈** | 在学习情境中即时触发，形成闭环 |
| **差异化管理** | 根据错误类型采用不同补救策略 |
| **可追溯性** | 完整记录闭环过程，支持分析和优化 |

---

## 2. 触发条件

### 2.1 触发场景

错题闭环可在以下场景触发：

| 场景 | 触发时机 | 说明 |
|-----|---------|------|
| **虚拟教室（SCENE-003）** | 学生在练习环节答错 | 实时学习过程中 |
| **作业批改（SCENE-006）** | 教师批改或系统自动批改发现错误 | 作业提交后 |
| **自适应评测** | 模块测验中答错 | 阶段性评估中 |

### 2.2 触发数据结构

```yaml
error_loop_trigger:
  trigger_id: "trigger_001"
  scenario: "SCENE-003"                   # SCENE-003 / SCENE-006 / 自适应评测
  
  # 学生信息
  student_id: "student_001"
  
  # 答题记录
  answer_record:
    record_id: "answer_001"
    node_id: "node_math_quadratic_skill_001"
    node_name: "二次方程的建模应用"
    layer: "skill"
    
    question_id: "q_skill_001"
    question_type: "application"          # concept / computational / reading / application
    difficulty: 3
    
    student_answer: "x = -3, x = 1"
    correct_answer: "x = 2, x = -1"
    is_correct: false
    
    timestamp: "2026-06-15T10:15:00Z"
  
  # 当前节点掌握状态
  current_mastery:
    status: "in_progress"
    attempts: 2                           # 该节点尝试次数
    error_count: 1                        # 该节点错误次数
```

### 2.3 触发判定规则

```
答题结果判定
    │
    ▼
is_correct == true ?
    │
    ├── 是 → 正常流程（更新掌握状态）
    │
    └── 否 → 检查重试上限
              │
              ▼
          attempts >= max_retries (3) ?
              │
              ├── 是 → 标记 needs_attention，触发人工干预
              │
              └── 否 → 触发错题闭环
```

---

## 3. 四步闭环流程

### 3.1 闭环流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                     错题闭环四步流程                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐                                                 │
│   │ 第1步    │                                                 │
│   │ 诊断Agent│                                                 │
│   └────┬─────┘                                                 │
│        │                                                       │
│        ▼                                                       │
│   ┌──────────────────────────────────────────┐                 │
│   │ 诊断结果：                                │                 │
│   │ · 错误类型分类                            │                 │
│   │ · 错误根因分析                            │                 │
│   │ · 补救方向建议                            │                 │
│   └────────────────────┬───────────────────┘                 │
│                        │                                        │
│                        ▼                                        │
│   ┌──────────┐                                                 │
│   │ 第2步    │                                                 │
│   │ 补充讲解 │                                                 │
│   │   Agent  │                                                 │
│   └────┬─────┘                                                 │
│        │                                                       │
│        ▼                                                       │
│   ┌──────────────────────────────────────────┐                 │
│   │ 讲解内容：                                │                 │
│   │ · 针对错误类型的知识点讲解                │                 │
│   │ · 易错点提示                              │                 │
│   │ · 正确解法示范                            │                 │
│   └────────────────────┬───────────────────┘                 │
│                        │                                        │
│                        ▼                                        │
│   ┌──────────┐                                                 │
│   │ 第3步    │                                                 │
│   │ 同类题   │                                                 │
│   │ 生成Agent│                                                 │
│   └────┬─────┘                                                 │
│        │                                                       │
│        ▼                                                       │
│   ┌──────────────────────────────────────────┐                 │
│   │ 生成题目：                                │                 │
│   │ · 同一知识点不同变式                      │                 │
│   │ · 相似情境应用                            │                 │
│   │ · 难度递进                                │                 │
│   └────────────────────┬───────────────────┘                 │
│                        │                                        │
│                        ▼                                        │
│   ┌──────────┐                                                 │
│   │ 第4步    │                                                 │
│   │ 评估Agent│                                                 │
│   └────┬─────┘                                                 │
│        │                                                       │
│        ▼                                                       │
│   ┌──────────────────────────────────────────┐                 │
│   │ 评估结果：                                │                 │
│   │ · 掌握判定                               │                 │
│   │ · 后续建议                               │                 │
│   │ · 状态更新                               │                 │
│   └──────────────────────────────────────────┘                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 各步骤详解

#### 第1步：诊断Agent

```yaml
diagnosis_agent:
  role: "错误诊断专家"
  goal: "准确识别错误类型和根因"
  
  output:
    error_type: "concept / computational / reading / prerequisite"
    root_cause: "详细错误原因分析"
    remediation_direction: "补救方向建议"
  
  错误类型定义:
    - concept: "概念理解错误（如混淆公式、条件遗漏）"
    - computational: "计算错误（如符号错误、运算失误）"
    - reading: "审题错误（如忽略条件、误解题意）"
    - prerequisite: "前置知识缺失（如基础技能不熟）"
```

#### 第2步：补充讲解Agent

```yaml
explanation_agent:
  role: "个性化辅导专家"
  goal: "针对错误类型提供精准补充讲解"
  
  input:
    - diagnosis_result         # 第1步输出
    - original_question        # 原题
    - student_answer           # 学生答案
  
  output:
    explanation_content: "针对错误的知识点讲解"
    key_points: ["易错点列表"]
    correct_solution: "正确解法示范"
  
  讲解策略:
    concept: "强调概念内涵，举反例对比"
    computational: "演示完整计算过程，标注易错步骤"
    reading: "引导审题技巧，分析关键词"
    prerequisite: "补充前置知识，建立知识联系"
```

#### 第3步：同类题生成Agent

```yaml
similar_question_agent:
  role: "题目设计专家"
  goal: "生成符合要求的同类练习题"
  
  input:
    - original_question        # 原题
    - diagnosis_result         # 诊断结果
    - node_info                # 节点信息
  
  output:
    similar_questions:
      - question_id: "q_similar_001"
        question: "同类题题目内容"
        answer: "参考答案"
        difficulty: 3
        variation_type: "change_numbers" / "change_context" / "reverse_process"
      
      - question_id: "q_similar_002"
        question: "第二道同类题"
        # ...
  
  生成要求:
    - 数量: 2-3道
    - 变式类型: 换数字/换情境/逆过程
    - 难度: 与原题相当或略高
    - 确保真正同类（同一知识点）
```

#### 第4步：评估Agent

```yaml
evaluation_agent:
  role: "学习效果评估专家"
  goal: "判断学生是否达到掌握标准"
  
  input:
    - error_loop_record        # 前3步记录
    - similar_question_results  # 同类题答题结果
  
  output:
    mastery_status: "mastered / needs_more_practice / needs_attention"
    final_attempts: 3          # 总尝试次数
    consecutive_correct: 2      # 连续正确次数
  
  掌握判定规则:
    mastered:
      - "连续2次答对" OR
      - "累计正确率≥80%"
    
    needs_more_practice:
      - "未达掌握标准但重试次数<3"
    
    needs_attention:
      - "重试次数已达3次上限"
```

---

## 4. 错误类型分类与处理策略

### 4.1 错误类型定义

| 错误类型 | 代码 | 定义 | 示例 |
|---------|------|------|------|
| **概念错误** | concept | 知识点理解偏差或概念混淆 | 混淆一元二次方程与二次函数定义域 |
| **计算错误** | computational | 计算过程中的失误 | 符号遗漏、去括号错误 |
| **审题错误** | reading | 未正确理解题意或遗漏条件 | 忽略"大于零"条件 |
| **前置缺失** | prerequisite | 所需前置知识技能不熟练 | 因分解因式不熟导致无法解题 |

### 4.2 处理策略矩阵

| 错误类型 | 补救方向 | 讲解重点 | 同类题特征 |
|---------|---------|---------|-----------|
| concept | 强化概念理解 | 辨析易混淆概念，举反例 | 考察同一概念的不同表述 |
| computational | 规范计算过程 | 演示完整步骤，标注易错点 | 同类型计算，换数字 |
| reading | 提升审题能力 | 关键词识别，条件拆解 | 换情境但考察点相同 |
| prerequisite | 补充前置知识 | 关联前置知识点，建立知识网络 | 回归前置知识的专项练习 |

### 4.3 错误诊断决策树

```
答题错误
    │
    ▼
审题检查：题目条件是否都使用了？
    │
    ├── 否 → reading（审题错误）
    │
    └── 是 → 概念检查：核心概念是否正确？
              │
              ├── 否 → concept（概念错误）
              │
              └── 是 → 计算检查：计算过程是否正确？
                        │
                        ├── 否 → computational（计算错误）
                        │
                        └── 是 → 前置检查：相关前置知识是否掌握？
                                  │
                                  ├── 否 → prerequisite（前置缺失）
                                  │
                                  └── 是 → 归类为 concept（概念理解不深）
```

---

## 5. 掌握判定规则

### 5.1 分层掌握标准

| 节点层次 | 掌握条件 | 重试上限 |
|---------|---------|---------|
| **工具层（tool）** | 连续2次操作正确 | 5次 |
| **技能层（skill）** | 情境判断正确率≥85% | 3次 |
| **概念层（concept）** | 解释质量达标 AND 测验正确率≥80% | 3次 |

### 5.2 错题闭环掌握判定

```yaml
mastery_criteria_for_error_loop:
  # 条件1：连续正确
  consecutive_correct:
    required: 2
    description: "连续答对2道同类题"
  
  # 条件2：累计正确率
  cumulative_accuracy:
    threshold: 0.8
    description: "累计正确率≥80%"
  
  # 判定逻辑
  # 满足任一条件即可判定为掌握
  logic: "consecutive_correct >= 2 OR cumulative_accuracy >= 0.8"
  
  # 重试上限
  max_attempts: 3
  # 超出上限标记为 needs_attention，触发人工干预
```

### 5.3 掌握状态流转

```
学生答题
    │
    ▼
答对？
    │
    ├── 是 → 更新正确计数
    │         │
    │         ▼
    │    连续正确≥2 或 累计正确率≥80%？
    │         │
    │         ├── 是 → mastery_status = "mastered"
    │         │
    │         └── 否 → 继续练习
    │
    └── 否 → 错误计数+1
              │
              ▼
          触发错题闭环
              │
              ▼
          错误次数 >= max_retries？
              │
              ├── 是 → mastery_status = "needs_attention"
              │         触发人工干预（教师介入）
              │
              └── 否 → 继续闭环流程
```

---

## 6. 输出规格

### 6.1 错题闭环记录数据结构

```yaml
error_loop_record:
  record_id: "el_001"
  trigger_id: "trigger_001"
  student_id: "student_001"
  
  # 原题信息
  original_question:
    question_id: "q_skill_001"
    node_id: "node_math_quadratic_skill_001"
    difficulty: 3
  
  # 四步闭环记录
  loop_steps:
    # 第1步：诊断
    step1_diagnosis:
      agent_id: "agent_diagnosis_001"
      timestamp: "2026-06-15T10:15:05Z"
      result:
        error_type: "computational"
        root_cause: "去括号时符号处理错误"
        remediation_direction: "强化去括号法则练习"
    
    # 第2步：补充讲解
    step2_explanation:
      agent_id: "agent_explanation_001"
      timestamp: "2026-06-15T10:15:30Z"
      result:
        explanation: "针对去括号法则的详细讲解..."
        key_points: ["括号前负号去括号变号", "分配律正确应用"]
    
    # 第3步：同类题
    step3_similar_questions:
      agent_id: "agent_sq_001"
      timestamp: "2026-06-15T10:16:00Z"
      result:
        questions:
          - question_id: "q_similar_001"
            content: "求解：3(x-2)=12"
            answer: "x=6"
          - question_id: "q_similar_002"
            content: "化简：-2(3x+1)"
            answer: "-6x-2"
    
    # 第4步：评估
    step4_evaluation:
      agent_id: "agent_evaluation_001"
      timestamp: "2026-06-15T10:17:00Z"
      result:
        attempts: 3
        consecutive_correct: 2
        cumulative_accuracy: 0.67
        mastery_status: "needs_more_practice"
        # 虽未完全掌握，但还有重试机会
  
  # 答题记录
  attempts:
    - attempt_id: 1
      question_id: "q_skill_001"
      is_correct: false
      timestamp: "2026-06-15T10:15:00Z"
    
    - attempt_id: 2
      question_id: "q_similar_001"
      is_correct: true
      timestamp: "2026-06-15T10:16:30Z"
    
    - attempt_id: 3
      question_id: "q_similar_002"
      is_correct: false
      timestamp: "2026-06-15T10:17:00Z"
  
  # 最终状态
  final_status:
    status: "needs_more_practice"          # mastered / needs_more_practice / needs_attention
    total_attempts: 3
    timestamp: "2026-06-15T10:17:00Z"
  
  # 触发来源
  triggered_from: "SCENE-003"
```

### 6.2 输出字段说明

| 字段 | 类型 | 说明 |
|-----|------|------|
| record_id | string | 闭环记录唯一标识 |
| loop_steps | object | 四步详细记录 |
| step1_diagnosis | object | 诊断步骤结果 |
| step2_explanation | object | 讲解步骤结果 |
| step3_similar_questions | object | 同类题步骤结果 |
| step4_evaluation | object | 评估步骤结果 |
| attempts | array | 所有答题尝试记录 |
| final_status | object | 最终掌握状态 |

---

## 7. 跨场景联动

### 7.1 联动场景

错题闭环完成后，需要与其他场景模块联动：

| 目标场景 | 触发条件 | 传递信息 |
|---------|---------|---------|
| **SCENE-003（虚拟教室）** | 闭环完成 | 更新节点掌握状态，呈现下一题 |
| **SCENE-006（作业批改）** | 闭环完成 | 记录错题到错题本，更新作业状态 |
| **流化学情分析** | 闭环完成/失败 | 上报学习行为数据 |

### 7.2 联动流程图

```
错题闭环完成
    │
    ├──▶ [SCENE-003 虚拟教室]
    │         │
    │         ▼
    │    更新学生节点掌握状态
    │    展示下一学习内容
    │
    ├──▶ [SCENE-006 作业批改]
    │         │
    │         ▼
    │    记录错题到错题本
    │    更新作业完成状态
    │
    └──▶ [学情分析模块]
              │
              ▼
         上报学习行为数据
              │
              ├──▶ 更新学生画像
              ├──▶ 更新班级热力图
              └──▶ 生成薄弱点报告
```

### 7.3 联动数据传递

```yaml
loop_completion_notify:
  source: "error_loop"
  record_id: "el_001"
  
  # 传递给虚拟教室
  classroom_update:
    student_id: "student_001"
    node_id: "node_math_quadratic_skill_001"
    mastery_status: "needs_more_practice"
    next_action: "continue_loop"            # continue_loop / next_node / mastered
  
  # 传递给作业批改
  grading_update:
    homework_id: "hw_001"
    question_id: "q_skill_001"
    error_record: "el_001"
    student_error_log_id: "error_log_001"
  
  # 传递给学情分析
  analytics_event:
    event_type: "error_loop_completed"
    student_id: "student_001"
    node_id: "node_math_quadratic_skill_001"
    error_type: "computational"
    final_status: "needs_more_practice"
    time_spent: 120                        # 秒
```

---

## 8. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| 闭环粒度 | 节点内闭环 | 针对当前节点的特定薄弱点，避免范围过大 |
| 同类题数量 | 2-3道 | 足够验证掌握，又不过度练习 |
| 掌握判定 | 连续2次或累计80% | 平衡严格性与灵活性 |
| 重试上限 | 默认3次 | 避免无限循环，及时人工介入 |
| 人工干预 | needs_attention时触发 | 确保学生不会卡在无法自愈的状态 |
| 错误分类 | 4类（concept/computational/reading/prerequisite） | 覆盖主要错误场景，指导精准补救 |

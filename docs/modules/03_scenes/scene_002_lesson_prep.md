# SCENE-002：备课辅助

**父文档**：[system_requirements.md](../../system_requirements.md) · [场景索引](../03_user_roles_scenes_index.md)
**相关决策**：[dp_arch_08](../../decisions/dp_arch_08.md), [dp_arch_04](../../decisions/dp_arch_04.md)

---

### 3.2.2 SCENE-002：备课辅助

**场景目标**：课程规划完成后，教师按知识点节点发起备课，系统为知识网络中的每个节点生成：
1. 教案（教师课堂授课部分，仅对非自学节点）
2. 学案（覆盖课堂与自学所有环节的学习脚手架）
3. 切片化教学资源（教材节选/PPT/视频/练习题库）
4. 思政融合设计（在哪个节点、融什么、如何融）
5. 课堂/自学标记（区分哪些内容在课堂讲、哪些需自学）

**核心设计原则**：
- 为知识网络的**每个节点**独立生成教学包
- 区分"课堂内容"与"自学内容"
- 教学资源按节点切片，而非按章节打包
- 思政融合由 Agent 提案 + 教师确认/修改，不自动输出内容

#### Agent 角色定义

| Agent 角色 | 框架 | 职责边界 | 提示词关键词 |
|-----------|------|---------|------------|
| 教材解析 Agent | DeepAgents | 解析教师提供的教材/讲义，映射到知识网络节点 | "你是教材分析专家，擅长从原始教材中提取与知识点对应的内容片段" |
| 教案设计 Agent | DeepAgents | 针对非自学节点生成课堂教案（导入/新授/练习/总结） | "你是教案设计专家，关注课堂节奏把控与重难点突破" |
| 学案设计 Agent | DeepAgents | 针对所有节点生成学生自学/课堂学案（引导问题/脚手架/活动建议） | "你是学习体验设计专家，擅长设计引导式学习脚手架" |
| 教学资源 Agent | DeepAgents | 按节点生成或匹配资源片段（题库/PPT建议/视频要点） | "你是教育资源库建设专家，擅长为特定知识点生成针对性练习" |
| 思政融合 Agent | DeepAgents | 为每个节点提出思政元素融合建议（位置/元素/方式） | "你是课程思政设计专家，擅长从学科内容中发掘价值引导切入点" |

#### 交互流程

```
SCENE-001 输出（已确认的知识网络）
  │
  ▼
教师选择需备课的节点范围（默认：一次处理一个节点或一组相关节点
  │
  ▼
教师提供教材/讲义/已有PPT（可选）
  │
  ▼
  ┌──────────────────────────────────────┐
  │ 教材解析 Agent                     │
  │ 将教材内容映射到节点               │
  │ 标注：课堂内容 vs 自学内容          │
  └──────────────┬───────────────────────┘
                 │
                 ▼
  ┌──────────────────────────────────────┐
  │ 教案设计 Agent                       │
  │ 针对课堂节点生成完整教案            │
  │ 教学过程（导入/新授/练习/总结）     │
  └──────────────┬───────────────────────┘
                 │
                 ▼
  ┌──────────────────────────────────────┐
  │ 学案设计 Agent                      │
  │ 覆盖课堂+自学全环节                 │
  │ 引导问题+脚手架+活动建议           │
  └──────────────┬───────────────────────┘
                 │
                 ▼
  ┌──────────────────────────────────────┐
  │ 教学资源 Agent                      │
  │ 生成题库/PPT要点/资源引用          │
  │ 按节点切片化存储                    │
  └──────────────┬───────────────────────┘
                 │
                 ▼
  ┌──────────────────────────────────────┐
  │ 思政融合 Agent                       │
  │ 仅给出结构化建议（不直接输出内容    │
  │ 建议内容：                           │
  │   · 目标节点 id                     │
  │   · 思政元素                        │
  │   · 融入方式                        │
  │   · 预计时长                        │
  │   · 活动建议（讨论/案例/角色扮演）  │
  └──────────────┬───────────────────────┘
                 │
                 ▼
           教师审阅 + 修改 + 确认
                 │
                 ▼
         Harness Schema 校验：
                 │
          ┌──────┴──────┐
          │ 通过        │ 不通过
          ▼             ▼
         持久化      自动重试（≤3次）
                 │
                 ▼
             人工干预提示

输出：每个节点一个完整教学包（教案+学案+资源+思政建议）
```

#### 输入规格

```yaml
knowledge_network_ref: "kn_001"                  # 必填，引用课程规划阶段生成的知识网络
node_range: ["tool_elimination_method", "skill_model_solve_system"]   # 必填，本次备课覆盖哪些节点
teacher_materials:                                # 选填，教师提供的原始教学材料
  - type: "textbook"
    content: "教材第一章：方程..."
  - type: "ppt"
    content: "已有的授课PPT要点..."
include_ideological_integration: true           # 必填，是否生成思政融合建议
instruction_for_student: false                  # 选填，是否区分自学内容
teaching_language: "中文"                       # 必填
```

#### 输出规格（按节点输出，每个节点独立一份）

```yaml
teaching_package:
  target_node_id: "tool_elimination_method"
  target_node_title: "消元法求解二元一次方程组"
  target_node_layer: "tool"
  is_classroom_content: true
  is_self_study_enabled: true

  lesson_plan:
    teaching_objectives:
      knowledge: ["掌握消元法三步操作：变形、消元、求解"]
      ability: ["能在给定练习题中熟练运用消元法"]
      quality: ["培养严谨的推理习惯"]
    teaching_process:
      - phase: "导入"
        duration_minutes: 5
        content: "以购物问题引入：已知2个苹果+3个梨=20元，3个苹果+2个梨=22元，求单价"
        method: "情境引入+问答法"
      - phase: "新授"
        duration_minutes: 20
        content: "消元法步骤演示：①变形使某系数相同 ②两式相减消去一个变量 ③求解剩余变量"
        method: "讲授+探究法"
      - phase: "练习"
        duration_minutes: 10
        content: "学生独立完成3道练习题，教师巡视答疑"
        method: "练习法"
      - phase: "总结"
        duration_minutes: 5
        content: "总结消元法要点：关键步骤是'消元'，注意符号变化"
        method: "问答总结"

  student_guide:
    pre_class: ["阅读教材第1-3页，尝试完成课前预习思考题1-2"]
    in_class_activities: ["跟随教师演示，记录消元法的关键步骤"]
    post_class: ["完成课后练习1-5题，记录不会的题目编号"]
    self_study_scaffold:
      guiding_questions:
        - "消元法的核心思想是什么？"
        - "如何选择消去哪个变量可以使计算更简单？"
      hints: ["提示1：先观察两式中系数最简单的变量", "提示2：如果两式某变量系数相同或相反，直接加减"]
      extension_activities: ["尝试用消元法解决你自己创设的一个实际问题"]

  resources:
    exercises:
      basic:
        - id: "ex_b_001"
          difficulty: 2
          content: "解方程组：2x+3y=13, 3x+2y=12"
          answer: "x=2, y=3"
        - id: "ex_b_002"
          ...
      moderate:
        - id: "ex_m_001"
          ...
    ppt_outline:
      - slide: 1
        title: "导入：生活中的方程组问题"
        key_points: ["购物问题"]
      - slide: 2
        title: "消元法三步曲"
        key_points: ["变形", "消元", "求解"]
    references: ["教材第一章p5-8", "可汗学院视频：消元法"]

  ideological_integration_suggestion:
    target_node_id: "tool_elimination_method"
    element: "用数学建模解决实际问题的价值观"
    approach: "在导入环节，用真实的校园购物问题引入，引导学生体会数学建模在生活决策中的应用"
    activity: "小组讨论：给出一个校园食堂预算问题，学生用方程组建模求解"
    duration_minutes: 5
    teacher_confirmation: "pending"     # pending/confirmed/modified_by_teacher

  assessment_criteria:
    classroom:
      tool_level: "能独立完成标准形式方程组的消元法求解"
      skill_level: "能根据系数特点灵活选择消去的变量"
      concept_level: "理解消元法本质是'降维'——把二元问题转化为一元"
    self_study:
      checkpoints: ["完成课前预习", "能总结消元法步骤", "完成练习正确率≥80%"]

created_at: "2026-06-12T10:30:00Z"
teacher_approved: false
```

#### 边界与异常

| 异常场景 | 系统行为 |
|---------|---------|
| 知识网络引用不存在 | 返回 ERR-REF-001，提示"未找到对应知识网络，请先完成课程规划" |
| 指定节点范围为空或不存在 | 提示 ERR-NODE-001，要求重新指定节点 |
| 思政融合 Agent 输出包含不适当内容 | Harness 内容过滤拦截，提示教师审查 |
| 教师确认后修改思政建议 | 记录修改历史，下次备课优先采用教师确认过的设计模式 |
| 练习题库数量 > 30 | 自动拆分节点，创建子节点或分组 |
| 任一 Agent 3 次重试失败 | 降级输出已完成部分，缺失部分标注"待人工补充" |
| 教师未提供原始教材 | 改为通用教学包，输出内容由教师手动补充 |
| Token 超预算 | 拆分备课流程：一次只处理一个节点，其余节点按队列执行 |

---


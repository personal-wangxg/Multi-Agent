# DP-ARCH-06：功能需求（FR）

**确认日期**：2026-06-12 · **确认人**：项目核心团队 · **决策类别**：架构

---

## 决策摘要

本决策点汇总并确认系统全部 **18 项功能需求（FR-01 ~ FR-18）** 的完整功能定义、输入输出、核心流程、关键约束与验收标准。这些 FR 按架构分层组织为：**平台基座（FR-01~04）**、**核心教学能力（FR-05~11）**、**运营支撑能力（FR-12~14）**、**约束与合规（FR-15~16）**、**扩展能力（FR-17）** 与 **知识编译核心（FR-18）**。所有需求一经确认即成为后续架构与内容决策点的基线。

## 核心设计原则

1. **分层优先级管理**：P0（必须实现，非实现不可上线）、P1（必须实现，与 P0 同版本交付）、P2（可选，后续版本迭代）
2. **分层架构**：平台基座层 → 核心教学能力层 → 约束与支撑能力层；上层依赖下层，下层不感知上层
3. **场景驱动**：9 类场景作为功能需求的组织依据，每一项 FR 至少服务一个场景；FR 之间的数据流通过场景协作体现
4. **迭代共创**：教师与 Agent 共同产出不可变更产物，每次迭代记录决策轨迹
5. **决策前置编译**：完整产物经编译为 DP 索引后消费，后续阶段不重新检索上下文

---

## FR 详细定义

### 3.1 FR-01：场景识别与分析（9 类场景）

**优先级**：P0 · **核心定位**：平台基座 · 输入路由能力 · **关联场景**：SCENE-001~009

**功能描述**：
当用户（教师/教研人员/运维管理员）在系统入口提交任务请求时，系统根据输入内容的关键词、目标描述与上下文信息，自动识别应路由至 9 类业务场景中的哪一类，并产出该场景的初始配置摘要供用户确认或调整。这是所有后续 Agent 协作的起点——错误的场景识别将直接导致下游所有 Agent 角色与流程错乱。

**输入规格**：
```yaml
user_request:
  request_type: "course_planning" | "lesson_prep" | "virtual_classroom" |
                 "error_loop" | "node_recommendation" | "homework_grading" |
                 "learning_analytics" | "teaching_evaluation" | "network_maintenance"
  course_name: "初中数学：一元二次方程"        # 可选：课程名称
  course_desc: "面向初三学生，讲解求解与应用"   # 可选：课程描述
  target_user_role: "teacher" | "student" | "researcher" | "admin"  # 可选
  free_text_description: "我想为下周的课程做规划"   # 可选：用户自由描述
  context_hints:                                # 可选：附加上下文提示
    - "已有知识网络：kn_001"
    - "目标学生层次：初中三年级"
```

**核心流程**：
1. **关键字匹配**：对 free_text_description 中的关键词（如"规划""备课""作业""评估""网络优化"等）进行模式匹配，产出候选场景列表及匹配分数
2. **意图分类**：当关键字匹配存在歧义（如同时命中"备课"与"作业"关键词）时，调用 LLM 基于完整输入进行意图二分类，产出主场景 + 辅助场景
3. **上下文消歧**：如提交中包含 course_name/course_desc/已有知识网络引用，则据此进一步验证场景合理性（如已有知识网络的请求不应路由至 SCENE-001 课程规划，而应路由至 SCENE-009 网络维护）
4. **用户确认**：以结构化卡片形式向用户展示识别结果（场景名称 + 推荐理由 + 可切换的场景列表），用户可确认或切换
5. **路由至 FR-02**：确认后将 scene_type 传递给 FR-02 Agent配置动态生成

**输出规格**：
```yaml
scene_recognition_result:
  primary_scene: "SCENE-001"                    # 主场景
  confidence_score: 0.87                        # 0.0 ~ 1.0
  alternative_scenes:                           # 可选候选，供用户切换
    - scene: "SCENE-002"
      reason: "文本中同时包含'备课'关键词"
      confidence_score: 0.62
  initial_config_hints:                         # 路由至 FR-02 的初始配置摘要
    required_agent_roles: ["教学目标设计Agent", "课程结构设计Agent", "知识网络构建Agent", "评估指标设计Agent"]
    suggested_framework: "DeepAgents"
    expected_stages: 3
  user_confirmed: true                          # 最终需由用户确认
```

**关键约束**：
- 识别准确率目标 ≥ 85%（对预置 9 类场景的标准输入）
- 响应时间 ≤ 5 秒
- 当识别置信度 < 0.5 时，不得自动路由，必须进入交互式澄清环节向用户提问
- 识别结果必须可审计：记录原始输入、匹配规则、LLM 判定原因、用户最终选择

**验收标准**：
- [ ] 对 9 类场景的标准输入各 ≥ 10 条测试用例，准确率 ≥ 85%
- [ ] 置信度 < 0.5 时正确触发交互式澄清
- [ ] 识别结果被审计日志记录，可回放
- [ ] 用户可在确认前切换至其他 8 个场景

---

### 3.2 FR-02：Agent 配置动态生成

**优先级**：P0 · **核心定位**：平台基座 · 运行时配置 · **关联场景**：SCENE-001~009

**功能描述**：
当 FR-01 输出确认的 scene_type 后，本 FR 根据场景类型自动生成该场景所需的 Agent 组合配置——包括每个 Agent 的角色定义、使用的框架（DeepAgents / AgentScope）、协作模式、工具白名单、Harness 策略绑定关系。配置以标准化 YAML/JSON 格式输出，可被 FR-03 直接加载执行，也可由教师在 FR-13 人机协同接口中审阅修改。

**输入规格**：
```yaml
scene_config_request:
  scene_type: "SCENE-001"
  course_name: "初中数学：一元二次方程"
  target_student_level: "初中三年级"
  teacher_id: "teacher_001"
  template_version: "v1.0"                          # 引用Harness模板版本
  custom_agent_overrides:                          # 可选：教师自定义覆盖
    - role: "评估指标设计Agent"
      tone: "更严格的量化指标"
```

**核心流程**：
1. **加载场景模板**：从配置库读取该 scene_type 对应的标准 Agent 组合模板（含角色定义、框架选择、协作模式）
2. **Harness 模板绑定**：为每个 Agent 自动绑定对应版本的提示词模板（FR-15 Harness约束层）、输出 Schema、工具白名单
3. **上下文变量注入**：将 course_name、target_student_level、teacher_id 等变量注入 Agent 的 dynamic_injection 区块（参考 dp_arch_07 六区块模板）
4. **教师覆盖合并**：如 teacher 提供 custom_agent_overrides，则在保持模板锁定区块不变的前提下，合并 dynamic_injection、tone 等可调整字段
5. **配置校验**：检查每个 Agent 是否已绑定 Harness 模板与 Schema，未绑定的 Agent 配置不得通过
6. **输出配置**：产出标准化的 Agent 配置 YAML

**输出规格**：
```yaml
agent_configuration:
  scene_type: "SCENE-001"
  total_agents: 4
  collaboration_mode: "pipeline"                    # pipeline / peer / master_slave

  agents:
    - agent_id: "agent_scene001_objectives_001"
      role: "教学目标设计Agent"
      framework: "DeepAgents"
      specialty: "按布鲁姆分类法设计分层学习目标"
      tone: "专业、严谨、结构清晰"
      harness_template_ref: "tpl_scene001_objectives_v1.0"
      output_schema_ref: "schema_objectives_v1.0"
      tool_whitelist_ref: "twl_scene001_basic_v1.0"
      max_retries: 3
      timeout_seconds: 120

    - agent_id: "agent_scene001_structure_002"
      role: "课程结构设计Agent"
      framework: "DeepAgents"
      # ... 同上格式 ...

    - agent_id: "agent_scene001_network_003"
      role: "知识网络构建Agent"
      framework: "DeepAgents"
      # ...

    - agent_id: "agent_scene001_evaluation_004"
      role: "评估指标设计Agent"
      framework: "DeepAgents"
      # ...

  message_routing_rules:
    - from: "agent_scene001_objectives_001"
      to: "agent_scene001_structure_002"
      trigger: "stage1_confirmed"
    - from: "agent_scene001_structure_002"
      to: "agent_scene001_network_003"
      trigger: "stage2_confirmed"

  context_injection:
    - key: "course_name"
      value: "初中数学：一元二次方程"
    - key: "target_student_level"
      value: "初中三年级"

  version: "v1.0"
  generated_at: "2026-06-12T10:00:00Z"
  generated_by: "fr02_config_generator"
```

**关键约束**：
- 每个 Agent 配置必须绑定至少 1 个 Harness 模板与 1 个输出 Schema；未绑定约束的 Agent 配置不得通过校验
- 配置生成响应时间 ≤ 10 秒
- 配置可保存至持久化存储（FR-12），可加载、可导出为模板
- Agent 角色定义必须与对应场景文档中描述的 Agent 角色一致（如 SCENE-003 的 AI 教师必须绑定 AgentScope 框架）

**验收标准**：
- [ ] 9 类场景均能生成合法的 Agent 配置 YAML
- [ ] 生成的配置 100% 通过 Harness 绑定校验
- [ ] 教师覆盖可正确合并至配置且不破坏锁定区块
- [ ] 配置可被 FR-03 Agent 编排与调度正确加载执行

---

### 3.3 FR-03：Agent 编排与调度

**优先级**：P0 · **核心定位**：平台基座 · 运行时执行 · **关联场景**：SCENE-001~009

**功能描述**：
依据 FR-02 生成的 Agent 配置，实际启动并运行各个 Agent 实例，协调其间的消息传递与状态同步；在每个 Agent 调用 LLM 前执行上下文 Token 检查与压缩；按 FR-04 的协议转换规则在 DeepAgents 与 AgentScope 框架间传递消息；处理单个 Agent 的失败重试与整体任务的异常降级。

**输入规格**：
```yaml
orchestration_request:
  agent_configuration_ref: "/sessions/sess_001/config.yaml"
  max_total_tokens: 300000                         # 本次会话总Token预算
  teacher_approval_mode: "key_decisions_only"      # auto / key_decisions_only / all
  failure_tolerance: "degrade"                     # fail_fast / degrade / retry_and_continue
```

**核心流程**：
1. **加载配置**：从 FR-12 持久化存储读取 FR-02 生成的 agent_configuration
2. **Agent 实例化**：依据 framework 字段在 DeepAgents 或 AgentScope 运行时中创建 Agent 实例；Harness 约束在实例创建时即加载并锁定
3. **消息路由启动**：根据 message_routing_rules 建立消息通道（DeepAgents 的 VFS 写入/读取；AgentScope 的 Message Hub 主题订阅）
4. **状态同步**：维护全局任务状态机（current_stage / completed_dps / token_used / error_count），在 Agent 间保持一致
5. **LLM 调用前检查**：每次调用 LLM 前计算当前输入 Token 量，若 > 模型窗口 × 50%，触发 FR-10 上下文压缩策略（见 dp_arch_10）
6. **教师审批触发**：在配置标记的关键决策节点（如 stage1_confirmed、stage2_confirmed）暂停，通过 FR-13 人机协同接口请求教师确认
7. **失败重试与降级**：单个 Agent Harness 校验失败 ≤ 3 次自动重试；超过阈值或出现不可恢复错误时，根据 failure_tolerance 策略决定是否降级为人工介入或终止
8. **Agent 销毁与会话收尾**：所有 Agent 完成后，产出完整执行记录，写入 FR-14 可观测性与审计日志

**输出规格**：
```yaml
orchestration_result:
  session_id: "sess_course_plan_2026_06_12_001"
  overall_status: "completed" | "completed_with_warnings" | "failed" | "awaiting_teacher"
  stages_completed: ["stage1", "stage2", "stage3"]
  total_tokens_used: 127500
  total_tokens_budget: 300000
  agent_execution_log:
    - agent_id: "agent_scene001_objectives_001"
      status: "completed"
      retries: 0
      tokens_used: 18500
      duration_seconds: 45
    # ... 其他Agent ...

  teacher_interventions:                       # 教师介入记录
    - stage: "stage1"
      action: "approved_with_comments"
      timestamp: "2026-06-12T10:15:00Z"
  output_artifacts:
    - type: "course_planning_yaml"
      path: "/sessions/sess_001/working/course_planning.yaml"
    - type: "decision_index_json"
      path: "/sessions/sess_001/working/decision_index.json"
    - type: "knowledge_wiki_pages"
      path: "/wiki/sess_001/"
  warnings_and_errors: []
  audit_log_ref: "/logs/audit/sess_001.json"
```

**关键约束**：
- Agent 启动时间 ≤ 30 秒（从配置加载完成到首个 Agent 开始执行）
- 单会话并发 Agent 数 ≥ 10
- Harness 校验失败的输出不得进入下游；必须在本 FR 内完成重试或标记失败
- 上下文 Token 检查在每个 Agent 每次 LLM 调用前强制执行；超限不得发起调用
- 运行稳定性目标：正常运行时间内任务成功率 ≥ 99%

**验收标准**：
- [ ] 可一键启动 SCENE-001~009 任一场景的多 Agent 协作并完成
- [ ] LLM 调用前 Token 检查 100% 执行；超限触发压缩流程
- [ ] 教师审批节点可正确暂停并等待 FR-13 反馈
- [ ] 失败重试 ≤ 3 次；超过阈值正确转入人工干预流程
- [ ] 完整执行记录被 FR-14 审计日志记录

---

### 3.4 FR-04：框架协议转换

**优先级**：P0 · **核心定位**：平台基座 · 框架兼容 · **关联框架**：DeepAgents ↔ AgentScope

**功能描述**：
系统中不同场景使用不同框架（如 SCENE-001/002/004/005/006/007/008/009 使用 DeepAgents；SCENE-003 虚拟教室使用 AgentScope 的 AI 教师 + AI 学生），而跨场景的数据流需要在不同框架之间共享决策索引、节点状态、学生表现数据。本 FR 定义一套统一消息协议与双向转换映射，屏蔽框架差异，使上层 FR 可统一操作。

**统一消息协议（Unified Message）**：
```yaml
unified_message:
  msg_id: "msg_20260612_00042"
  from_framework: "DeepAgents" | "AgentScope"
  to_framework: "AgentScope" | "DeepAgents"
  from_agent_id: "agent_scene005_recommender_001"
  to_agent_id: "ai_teacher_agent_001"
  intent: "node_recommendation_result"            # 业务意图枚举
  payload:
    # 结构化业务数据，Schema由intent决定
    recommended_node_id: "skill_model_building_01"
    student_id: "student_023"
    recommendation_score: 0.91
    reason: "该学生在工具层表现优秀，建议进入技能层学习建模"
  context_trace:
    session_id: "sess_001"
    decision_index_ref: "/sessions/sess_001/working/decision_index.json"
    dp_ids_referenced: ["DP-S1-03", "DP-S5-01"]
  timestamp: "2026-06-12T10:45:00Z"
  ttl_seconds: 300                                 # 消息超时回收
```

**框架映射规则**：
| 方向 | 统一协议字段 | DeepAgents 侧映射 | AgentScope 侧映射 |
|------|------------|-------------------|-------------------|
| DeepAgents → AgentScope | payload | DeepAgents write_todos 中 `result` 字段 | AgentScope Message Hub 主题消息体 |
| | context_trace.dp_ids | DeepAgents VFS decision_index.json 中的 dp_ids | AgentScope AgentState.context_metadata |
| | intent | DeepAgents agent_id + task_type 组合 | AgentScope 消息路由键（routing_key） |
| AgentScope → DeepAgents | payload | AgentScope Message Hub message.body | DeepAgents 动态注入 retrieved_memories |
| | context_trace.dp_ids | AgentScope 对话摘要中提取的决策点 | DeepAgents decision_index.json增量更新 |

**核心流程**：
1. **消息发出方**：任一 Agent 要与跨框架 Agent 通信时，先将业务数据封装为 unified_message
2. **协议转换层**：根据 from_framework 和 to_framework 查找映射规则，将 unified_message 转换为目标框架原生格式
3. **投递**：通过目标框架的原生通信机制投递（DeepAgents VFS 写入或 AgentScope Message Hub publish）
4. **接收与解析**：目标框架 Agent 接收原生消息后，通过协议层解析回 unified_message，提取 payload 与 context_trace
5. **决策索引同步**：跨框架通信附带的 dp_ids 必须在接收方 WM 的 decision_index 中增量更新，确保两框架的决策视图一致
6. **超时与重试**：消息 TTL 过期未被消费时自动触发告警；可配置重试次数

**关键约束**：
- 协议转换层必须在 ≤ 100ms 内完成一次消息转换
- 支持插拔式扩展：未来新增第三方框架时，仅需实现一个双向转换插件
- 跨框架的决策索引同步必须保证最终一致性（短时间不一致可容忍，但最终必须合并）
- 敏感字段（如教师反馈的内部批注）在跨框架传输时需脱敏处理

**验收标准**：
- [ ] DeepAgents → AgentScope 的 SCENE-005 推荐结果可被 SCENE-003 的 AI 教师正确读取
- [ ] AgentScope → DeepAgents 的 SCENE-003 学生节点掌握状态可触发 SCENE-007 学情分析
- [ ] 100 条并发跨框架消息的转换成功率 ≥ 99%
- [ ] 决策索引在两框架中最终一致（最终一致性窗口 ≤ 30 秒）

---

### 3.5 FR-05：立体分层知识网络

**优先级**：P0 · **核心定位**：核心教学能力 · 内容的结构化表示 · **关联场景**：SCENE-001 / SCENE-002 / SCENE-003 / SCENE-005 / SCENE-009

**功能描述**：
在 SCENE-001 课程规划的 Stage 3 阶段，基于 Stage 2 产出的课程结构单元，为每个抽象知识点生成"工具层/技能层/概念层"三个独立节点，并建立层内前置依赖边、跨层支撑边与同主题关联边，最终形成一张立体分层知识网络。该网络是后续所有场景（备课、虚拟教室、推荐、学情、维护）的核心数据骨架。

**输入规格**：
```yaml
knowledge_network_input:
  stage2_course_structure_ref: "/sessions/sess_001/working/stage2_structure.yaml"
  stage1_teaching_methods_ref: "/sessions/sess_001/working/stage1_methods.yaml"
  teacher_preferences:
    prefer_rich_tool_layer: true     # 工具层节点更细分
    emphasize_concept_first: false    # 是否优先从概念层进入
  reference_knowledge_network_ids: [] # 可选：借鉴已有网络
```

**核心流程（Stage 3 三阶段产出）**：
1. **节点拆分**：对 stage2 中每个结构单元的 core_knowledge_keywords，Agent 按"工具层（操作步骤）→ 技能层（情境迁移）→ 概念层（本质原理）"三层拆分，为每层生成独立节点，填写完整字段
2. **边关系推断**：
   - 层内边 is_prerequisite：按知识点自身的先后逻辑（如"先学直接开方 → 再学配方法"）建立同 layer 内的前置边
   - 跨层边 supports_understanding：从 concept 节点指向相关 skill 节点，表示概念理解支撑技能应用
   - 跨层边 enables_operation：从 skill 节点指向相关 tool 节点，表示技能判断支撑工具操作
   - 同主题边 same_topic_cross_layer：标记同一抽象知识点在三层间的对应关系，用于纵向学习路径的跃迁
3. **节点元数据填充**：为每个节点填写 bloom_level、difficulty、can_self_learn、estimated_periods、mapped_unit、teaching_objectives。其中 difficulty 默认 3，可由教师在迭代中调整
4. **网络结构说明生成**：生成 network_notes 描述多起点多路径、入口节点与汇聚节点
5. **Harness Schema 校验**：校验是否三层均有节点（layer_distribution 约束）、是否有孤立节点、边关系是否符合跨层方向规则
6. **教师迭代确认**：Agent 生成草案 → 教师审阅/修改（如"这两个节点可以合并""缺少一个过渡节点"）→ Agent 迭代生成 v2 → ... 直至教师确认
7. **持久化**：写入 FR-12，同时触发 FR-18 知识编译为决策索引

**输出规格**：
```yaml
knowledge_network:
  kn_id: "kn_001"
  course_name: "初中数学：一元二次方程"
  version: "1.0"
  total_nodes: 12
  total_edges: 18

  nodes:
    - id: "concept_equation_essence_01"
      layer: "concept"
      title: "理解一元二次方程的本质"
      bloom_level: "analyze"
      difficulty: 4
      can_self_learn: false
      estimated_periods: 1
      mapped_unit: "unit_01"
      teaching_objectives:
        knowledge: ["理解一元二次方程的定义与一般形式"]
        ability: ["能判断一个方程是否为一元二次方程"]
        quality: ["培养抽象概括能力"]
      prerequisites: []                          # 层内前置节点
      related_tool_nodes: ["tool_formula_method_07"]
      related_skill_nodes: ["skill_method_selection_04"]

    - id: "skill_method_selection_04"
      layer: "skill"
      title: "根据方程特征灵活选择解法"
      bloom_level: "apply"
      difficulty: 4
      can_self_learn: false
      estimated_periods: 2
      mapped_unit: "unit_02"
      # ...

    - id: "tool_formula_method_07"
      layer: "tool"
      title: "公式法求解一元二次方程"
      bloom_level: "apply"
      difficulty: 2
      can_self_learn: true
      estimated_periods: 2
      mapped_unit: "unit_02"
      # ...

  edges:
    # 层内边：同层次先后依赖
    - from: "concept_equation_essence_01"
      to: "concept_discriminant_meaning_02"
      relation_type: "is_prerequisite"
    - from: "tool_formula_method_07"
      to: "tool_factorization_method_08"
      relation_type: "is_prerequisite"

    # 跨层边：概念 → 技能 → 工具 的支撑关系
    - from: "concept_equation_essence_01"
      to: "skill_method_selection_04"
      relation_type: "supports_understanding"
    - from: "skill_method_selection_04"
      to: "tool_formula_method_07"
      relation_type: "enables_operation"

    # 同主题边：同一知识点三层间对应关系
    - from: "concept_equation_essence_01"
      to: "skill_method_selection_04"
      relation_type: "same_topic_cross_layer"

  layer_distribution:
    concept_nodes_count: 4
    skill_nodes_count: 4
    tool_nodes_count: 4

  network_notes:
    entry_nodes: ["concept_equation_essence_01", "tool_formula_method_07"]
    convergence_nodes: ["skill_model_building_12"]
    multi_path_description: "学生可从概念层进入（理论导向），或从工具层进入（操作导向），最终汇聚于技能层的建模节点"

  evaluation_metrics_ref: "eval_metrics_kn_001.yaml"   # 与节点绑定的评估指标
  teacher_confirmed: true
  created_at: "2026-06-12T10:30:00Z"
```

**关键约束**：
- 三层节点数量平衡：每层至少 ≥ 1 个节点；对于 ≥ 3 个结构单元的课程，每层建议 ≥ 3 个节点
- 边关系方向一致性：is_prerequisite 必须在同 layer 内；supports_understanding 必须 concept→skill；enables_operation 必须 skill→tool
- 无孤立节点：每个节点至少有一条入边或一条出边（入口节点可只有出边）
- mapped_unit 必须引用 stage2 中存在的结构单元 id
- 节点/边迭代次数：默认支持最多 5 轮迭代，超限标记为阶段性搁置

**验收标准**：
- [ ] 对标准课程输入，可生成包含 ≥ 3 概念节点 + ≥ 3 技能节点 + ≥ 3 工具节点的完整知识网络
- [ ] 边关系方向检查 100% 通过
- [ ] 教师可在 ≤ 3 轮迭代内完成确认
- [ ] 知识网络可被 SCENE-002 备课辅助、SCENE-003 虚拟教室、SCENE-005 节点推荐正确读取与使用

---

### 3.6 FR-06：节点推荐引擎—动态学习路径

**优先级**：P0 · **核心定位**：核心教学能力 · 动态路径涌现 · **关联场景**：SCENE-005 / SCENE-003 / SCENE-007

**功能描述**：
当学生在 SCENE-003 虚拟教室或 SCENE-006 作业批改中被标记为"已掌握当前节点"后，本 FR 基于知识网络的边关系、学生历史表现数据、学生目标层次，计算并推荐 2~4 个候选下一节点，同时为每个候选生成可解释的推荐理由。学生拥有最终选择权；选择结果被记录并反向影响后续推荐权重。

**输入规格**：
```yaml
recommendation_input:
  student_id: "student_023"
  current_node_id: "tool_formula_method_07"
  mastery_confirmed: true
  student_target_level: "skill"                # tool / skill / concept
  knowledge_network_ref: "kn_001"
  historical_performance_ref: "/data/students/student_023_performance.json"
  candidate_count: 3                            # 期望推荐数量（默认3）
  teacher_approval_required: false
```

**核心流程（权重计算 → 候选筛选 → 解释生成 → 学生选择）**：
1. **可达后继节点收集**：沿当前节点的 is_prerequisite 出边、supports_understanding/enables_operation 跨层边，收集所有可达的后继节点；同时收集同主题节点（same_topic_cross_layer）以支持纵向跃迁
2. **基础分（网络结构，60% 权重）**：
   - is_prerequisite 边的直接后继：基础分 0.9
   - 跨层 supports_understanding / enables_operation 边：基础分 0.75（但根据学生目标层次调整）
   - 路径长度 > 1（需经过其他节点）：基础分按 0.8^path_length 衰减
3. **表现分（历史数据，30% 权重）**：
   - 与当前节点同类节点（相同 layer、相似 difficulty）的历史正确率加权平均
   - 错题闭环触发次数：次数越多，后续巩固型推荐加分
   - 掌握速度（完成耗时 vs 节点 estimated_periods 之比）：速度快者推荐更高难度节点加分
   - 数据不足（< 3 个已掌握节点）：表现分降为中性 0.5，并在推荐中标注"待积累数据后自动调整"
4. **层次匹配分（目标层次，10% 权重）**：
   - student_target_level = tool：tool 层节点 +0.2
   - student_target_level = skill：skill 层节点 +0.2
   - student_target_level = concept：concept 层节点 +0.2
5. **候选筛选与多样性保证**：
   - 按总分排序，取前 candidate_count × 2 个节点
   - 保证候选节点分布在 ≥ 2 个 layer；不足时补充其他 layer 的最高得分节点
   - 难度跳跃限制：候选节点 difficulty 与当前节点之差绝对值 ≤ 1；不满足时用最接近的替代
6. **推荐解释生成**：
   每个候选节点附自然语言解释，包含三要素：(a)知识网络依赖——"这是你当前节点的自然后继"；(b)表现匹配——"你在工具层表现优秀，可以挑战技能层"；(c)层次匹配——"符合你以概念理解为目标的学习方向"
7. **学生选择**：系统以候选卡片形式展示（节点标题、recommendation_score、推荐理由、预计课时、难度），学生点击选择；也可全部拒绝后自由从完整知识网络选择
8. **记录与反馈**：学生选择被记录入 student_preferences，用于后续推荐的个性化微调；触发 SCENE-003 虚拟教室在选定节点启动

**输出规格**：
```yaml
recommendation_result:
  request_id: "rec_20260612_007"
  student_id: "student_023"
  current_node_id: "tool_formula_method_07"
  algorithm_version: "v1.0"

  candidates:
    - rank: 1
      node_id: "skill_method_selection_04"
      recommendation_score: 0.91
      score_breakdown:
        network_structure_score: 0.54   # 60% 权重
        performance_score: 0.27         # 30% 权重
        level_match_score: 0.10         # 10% 权重
      reason: "你在工具层'公式法'节点表现优秀（正确率92%，耗时低于预期），推荐进入技能层学习如何根据方程特征灵活选择解法。这符合你以技能应用为目标的学习方向。"
      estimated_periods: 2
      difficulty: 4
      can_self_learn: false

    - rank: 2
      node_id: "tool_factorization_method_08"
      recommendation_score: 0.82
      # ...

    - rank: 3
      node_id: "concept_discriminant_meaning_02"
      recommendation_score: 0.68
      # ...

  diversity_guarantee:
    layers_covered: ["skill", "tool", "concept"]
    difficulty_range: [2, 4]

  student_final_choice: null                   # 学生选择后填充
  student_rejected_all: false                  # 是否全部拒绝
  auto_advanced: false                         # 是否系统自动推进（教师审核模式下可启用）

  generated_at: "2026-06-12T10:45:00Z"
```

**关键约束**：
- 推荐引擎响应时间 ≤ 10 秒
- 每个候选必须附结构化推荐理由（非仅数字分数）
- 推荐后候选项可被教师审核覆盖（teacher_approval_required=true 时）
- 所有候选分数 < 0.5 时，扩大搜索范围（放宽 layer 限制或放宽 difficulty 跳跃限制至 2）重新计算；仍无则提示教师手动建议
- 从当前节点出发无可达后继节点时，提示"已完成该主题的所有学习！推荐进入下一主题"

**验收标准**：
- [ ] 学生掌握节点后，10 秒内返回 2~4 个候选
- [ ] 推荐理由自然语言解释与结构化 score_breakdown 一致
- [ ] 候选节点保证 ≥ 2 个 layer 的多样性
- [ ] 学生选择后，SCENE-003 虚拟教室可在正确节点启动
- [ ] 100 条历史数据模拟中，学生在推荐节点的平均掌握率 ≥ 75%

---

### 3.7 FR-07：节点内错题闭环

**优先级**：P1 · **核心定位**：核心教学能力 · 微观学习循环 · **关联场景**：SCENE-004 / SCENE-003 / SCENE-006

**功能描述**：
学生在 SCENE-003 虚拟教室练习或 SCENE-006 作业批改中答错某题时，系统自动启动"错误诊断 → 针对性补充讲解 → 同类新题生成 → 学生作答 → 再评估"的微观学习闭环，直至学生在同类题上达到掌握标准或达到最大重试上限。闭环结束后更新节点掌握状态，并将错误数据流入 SCENE-007 学情分析。

**输入规格**：
```yaml
error_loop_trigger:
  student_id: "student_023"
  node_id: "tool_elimination_method_06"
  original_question:
    q_id: "ex_b_003"
    content: "解方程组：2x + 3y = 13，3x + 2y = 12"
    student_answer: "x = 5, y = -1"
    correct_answer: "x = 2, y = 3"
    context_session_id: "vc_20260612_001"
  max_attempts: 3
  mastery_criterion:
    consecutive_correct_required: 2          # 连续答对几道
    or_accuracy_threshold: 0.80               # 或累计正确率
```

**核心流程（四步闭环循环）**：

```
┌──────── 步骤 A：错题诊断 Agent ────────┐
│ 输入：原题 + 学生答案 + 正确答案        │
│ 诊断维度：                              │
│  · error_type: concept / computational   │
│            / reading / prerequisite      │
│  · specific_cause：自然语言描述具体原因   │
│  · severity：low / medium / high         │
│  · prerequisite_knowledge_gap：若错误    │
│    类型为 prerequisite，指出缺失的前置   │
│    节点 id                               │
│ 输出：error_diagnosis_report             │
└──────────────────┬───────────────────────┘
                   ▼
┌──────── 步骤 B：补充讲解 Agent ────────┐
│ 根据 error_type 选择讲解策略：          │
│  · concept → 返回概念层节点核心讲解     │
│  · computational → 逐行计算步骤详解+提醒│
│  · reading → 审题方法训练（圈关键词/    │
│    翻译题意/拆分子问题）                 │
│  · prerequisite → 推荐返回前序节点复习  │
│   （此时不进入后续步骤，直接跳转建议）   │
│ 输出：supplementary_lesson（含文本+      │
│      资源推荐）                          │
└──────────────────┬───────────────────────┘
                   ▼
┌──────── 步骤 C：同类题生成 Agent ──────┐
│ 同类题生成策略：                        │
│  · 保持原题考点不变（如"消元法"）       │
│  · 变换数值/情境/表述方式（避免学生     │
│    记忆答案而非理解方法）                │
│  · 难度略低于原题（给学生信心）          │
│  · 每次生成 1 道，可循环生成            │
│ 约束：同类题 Agent 3 次生成失败则降级   │
│       从题库随机抽取                    │
│ 输出：new_question（含题干+参考答案）    │
└──────────────────┬───────────────────────┘
                   ▼
┌──────── 步骤 D：评估 Agent ───────────┐
│ 学生提交新题答案后，评估 Agent：       │
│  · 对比正确答案，判定正确/错误         │
│  · 检查掌握条件：                      │
│    连续 2 次答对 → mastered            │
│    或累计正确率 ≥ 80% → mastered       │
│  · 未掌握但 attempt_count < MAX：      │
│    回到步骤 A（诊断错误原因）           │
│  · 未掌握且 attempt_count ≥ MAX：      │
│    标记 needs_teacher_attention        │
│ 输出：loop_attempt_record              │
└────────────────────────────────────────┘
```

**完整输出规格**：
```yaml
error_loop_record:
  loop_id: "err_loop_20260612_001"
  node_id: "tool_elimination_method_06"
  student_id: "student_023"
  triggered_from: "virtual_classroom"     # virtual_classroom / homework_grading
  original_question_ref: "ex_b_003"

  initial_diagnosis:
    error_type: "computational"
    specific_cause: "第二个方程在变形为 x=... 时符号处理错误，将移项后的 -2y 误写为 +2y"
    severity: "medium"
    prerequisite_knowledge_gap: null

  attempts:
    - attempt_number: 1
      new_question_id: "ex_b_003_v2"
      new_question_content: "解方程组：3x + 2y = 13，2x + 3y = 12"
      student_answer: "x = 3, y = 2"
      is_correct: true
      evaluation_notes: "学生在本次尝试中正确处理了符号，消元步骤清晰"
      mastery_after_this: false              # 仅1次正确，未达连续2次

    - attempt_number: 2
      new_question_id: "ex_b_003_v3"
      new_question_content: "解方程组：4x - 2y = 10，3x + 2y = 11"
      student_answer: "x = 3, y = 1"
      is_correct: true
      evaluation_notes: "学生成功纠正了符号错误，并熟练应用消元法"
      mastery_after_this: true               # 连续2次正确

  final_status: "mastered"                   # mastered / needs_teacher_attention /
                                             # not_mastered / prerequisite_gap
  total_attempts: 2
  accuracy_so_far: 0.67                      # 含原题在内累计正确率
  recommendation: "学生已掌握该题型。可返回原节点继续。"

  diagnostic_data_for_analytics:             # 供 FR-09 学情分析使用
    error_types_encountered: ["computational"]
    nodes_flagged_as_difficult: []
    prerequisite_gaps: []

  triggered_at: "2026-06-12T10:45:00Z"
  completed_at: "2026-06-12T10:55:00Z"
```

**关键约束**：
- 错题诊断 Agent 对标准题型的 error_type 判断准确率 ≥ 85%
- 同类题不得复用原题数值；在同一题型上可连续生成 ≥ 5 道不同题
- 默认最大重试次数 = 3；超过时标记 needs_teacher_attention 并在学情分析中高亮该节点
- 诊断为 prerequisite 类型时，直接跳转至推荐返回前置节点复习，不进入补充讲解/新题循环
- 学生主动退出闭环时，记录"主动放弃"但不标记为掌握；下次进入该节点时自动重新触发练习

**验收标准**：
- [ ] 在 10 道典型错题测试用例上，100% 触发完整闭环流程
- [ ] 同类题生成 Agent 连续生成 ≥ 5 道不同题目且保持考点一致
- [ ] 达到掌握条件时，正确更新节点掌握状态为 mastered（SCENE-005 可识别）
- [ ] 3 次失败后，正确标记 needs_teacher_attention 并记录为难点节点
- [ ] 闭环完整记录可被 SCENE-007 学情分析读取并纳入学生画像

---

### 3.8 FR-08：作业批改与评分

**优先级**：P1 · **核心定位**：核心教学能力 · 学习结果评定 · **关联场景**：SCENE-006 / SCENE-004 / SCENE-007 / SCENE-010

**功能描述**：
学生提交随堂测试/课后作业/结课考核后，系统自动对照参考答案与评分 rubric，对每道题目进行结构化批改——给出得分、逐题点评、错误类型归类。批改结果用于：(a)更新学生在相关知识节点的掌握状态；(b)触发错题闭环（FR-07）；(c)生成班级学情数据（FR-09）。同时支持教师复核：教师可覆盖自动评分、添加批注。

**输入规格**：
```yaml
homework_submission:
  homework_id: "hw_2026_06_12_001"
  assignment_type: "in_class_test"           # in_class_test / homework / final_exam
  student_id: "student_023"
  knowledge_node_ids: ["tool_formula_method_07", "tool_factorization_method_08"]
  submitted_at: "2026-06-12T11:00:00Z"

  questions_and_answers:
    - q_id: "q_001"
      content: "用公式法解方程：x^2 - 5x + 6 = 0"
      student_answer: "x = 2, x = 3"
      max_score: 5

    - q_id: "q_002"
      content: "用因式分解法解方程：x^2 - 3x - 10 = 0"
      student_answer: "x = 5, x = -2"
      max_score: 5

  reference_answers_and_rubric:
    - q_id: "q_001"
      correct_answer: "x = 2, x = 3"
      scoring_rubric: "写出判别式得1分；正确计算得2分；写出两根各1分。步骤完整且正确5分；有小错误4分；结果对但无步骤2分；结果错但公式正确1分。"

    - q_id: "q_002"
      correct_answer: "x = 5, x = -2"
      scoring_rubric: "成功因式分解得3分；正确写出两根各1分。步骤完整且正确5分。"
```

**核心流程**：
1. **答案解析**：逐题比对 student_answer 与 correct_answer。对于数值/符号类数学题，采用表达式等价判定（可调用外部数学解析工具或 LLM 辅助）；对于文本类题，由 LLM 按 rubric 判定得分
2. **逐题评分与点评**：
   - 得分：依据 rubric 给分
   - 错误类型标注：concept / computational / reading / prerequisite（复用 FR-07 的分类）
   - 点评：结构化文本，指出错误、给出正确解法、建议改进方向
3. **错题闭环触发**：答错的题目自动调用 FR-07，启动节点内错题闭环；该题批改记录关联至 error_loop_record
4. **节点掌握状态更新**：结合本次作业得分、关联节点的往期表现数据，按评估指标（FR-11 中定义的节点掌握标准）判定节点掌握状态
5. **班级汇总**：聚合全班学生的批改数据，计算平均分数、每题错误率、常见错误类型分布
6. **教师复核接口**：教师可查看每道题的自动批改结果，调整分数，添加手写批注
7. **持久化与数据上报**：批改记录写入 FR-12；节点掌握状态上报至 FR-09 学情分析；班级汇总数据写入 FR-10 教学评估的数据池

**输出规格（学生个人报告）**：
```yaml
homework_grading_result:
  homework_id: "hw_2026_06_12_001"
  student_id: "student_023"
  total_score: 9
  max_total_score: 10
  score_percentage: 0.90
  graded_at: "2026-06-12T11:02:00Z"
  grading_mode: "auto"                        # auto / teacher_reviewed / mixed

  per_question_results:
    - q_id: "q_001"
      scored: 5
      is_correct: true
      scoring_reason: "步骤完整，答案正确。判别式 Δ = 25 - 24 = 1，正确计算了 x = (5 ± 1) / 2"
      error_type: null

    - q_id: "q_002"
      scored: 4
      is_correct: true
      scoring_reason: "因式分解正确 (x - 5)(x + 2)，但步骤中缺少中间展开验证，扣1分"
      error_type: null

    - q_id: "q_003"
      scored: 0
      is_correct: false
      scoring_reason: "学生将 x^2 - 3x - 10 错误分解为 (x - 2)(x - 5)，十字相乘常数项错误"
      error_type: "concept"
      triggered_error_loop_id: "err_loop_20260612_002"

  node_mastery_after_homework:
    - node_id: "tool_formula_method_07"
      mastery_confirmed: true
      cumulative_accuracy: 0.92
      evidence: ["本作业 q_001 正确", "上一次虚拟教室正确率 90%"]

    - node_id: "tool_factorization_method_08"
      mastery_confirmed: false
      cumulative_accuracy: 0.65
      evidence: ["本作业 q_003 错误", "相关错题闭环仍在进行"]

  teacher_review:
    reviewed: false
    review_comments: []
    score_adjustments: {}

  recommended_follow_up:
    type: "advance_to_next_node"               # advance_to_next_node / stay_and_retry / error_loop_in_progress
    target_next_node: "skill_method_selection_04"
```

**班级汇总输出规格**：
```yaml
class_summary:
  homework_id: "hw_2026_06_12_001"
  total_students: 30
  submitted_count: 28
  average_score: 7.2
  max_score: 10
  score_distribution:
    "9-10分": 8
    "7-8分": 12
    "5-6分": 5
    "<5分": 3

  per_question_error_rates:
    - q_id: "q_003"
      error_rate: 0.43
      common_error_types:
        - type: "concept"
          count: 8
          description: "因式分解常数项符号错误"
        - type: "computational"
          count: 4
          description: "计算错误"

  flagged_nodes_for_attention:
    - node_id: "tool_factorization_method_08"
      class_mastery_rate: 0.57
      attention_level: "high"
```

**关键约束**：
- 同类题目评分一致性偏差 ≤ 5%（即同一评分 rubric 下重复批改同一份答案，分数差异 ≤ 5%）
- 全班平均分异常（< 40% 或 > 95%）时，自动触发告警，提示教师确认参考答案正确性或 rubric 合理性
- 批改 Agent 3 次重试后仍无法评分的题目，标记为"待人工批改"，不影响其他题目的自动批改
- 教师复核覆盖的评分，以教师分数为准，同时记录自动评分与教师评分供系统学习优化
- 批改记录必须可审计（FR-14）：保留原始学生答案、参考答案、评分 Agent 的判定过程

**验收标准**：
- [ ] 对 5 份不同类型作业样本，可完成自动评分与逐题点评
- [ ] 同类题评分一致性：同一份答案 3 次重复批改，最大分差 ≤ 0.5 分
- [ ] 错题自动触发 FR-07 闭环率 100%
- [ ] 班级平均分异常（<40% 或 >95%）正确触发告警
- [ ] 批改数据正确驱动节点掌握状态更新，可被 SCENE-005 推荐引擎使用

---

### 3.9 FR-09：学情分析（学生画像 + 班级热力图）

**优先级**：P1 · **核心定位**：核心教学能力 · 数据驱动洞察 · **关联场景**：SCENE-007 / SCENE-003 / SCENE-004 / SCENE-006 / SCENE-008

**功能描述**：
系统持续采集学生在各节点的学习数据（虚拟教室答题记录、错题闭环过程、作业批改得分、节点掌握状态与耗时），基于此为每个学生生成个性化学习画像，并在班级层面生成知识网络热力图——标注每个节点的班级掌握率与薄弱环节。分析结果用于：(a)为教师提供教学调整建议；(b)为后续节点推荐引擎提供表现分输入；(c)为教学评估提供过程性数据依据。

**输入规格（数据源聚合）**：
```yaml
learning_analytics_input:
  analysis_scope: "per_course"                 # per_course / per_unit / per_node
  knowledge_network_ref: "kn_001"
  student_ids: ["student_001", "student_002", "...", "student_030"]
  data_sources:
    - type: "virtual_classroom_sessions"
      ref: "/data/vc/sess_*/node_*.json"
    - type: "error_loop_records"
      ref: "/data/err/err_loop_*.json"
    - type: "homework_grading_results"
      ref: "/data/hw/hw_*.json"
    - type: "node_mastery_log"
      ref: "/data/mastery/student_*_node_*.json"
  analysis_timestamp: "2026-06-12T18:00:00Z"
  auto_regeneration_frequency_hours: 24         # 每日自动更新一次
```

**核心流程（数据聚合 → 学生画像 → 班级热力图 → 教学建议）**：

1. **数据聚合 Agent**：从多源数据中抽取每个学生在每个节点的以下特征：
   - 掌握状态（mastered / in_progress / not_started）
   - 累计正确率（所有相关答题的正确比例）
   - 错题闭环次数（触发过几次闭环）
   - 平均学习耗时（与节点 estimated_periods 对比）
   - 首次掌握耗时（从进入节点到首次标记掌握的时间）
   - 错误类型分布：concept / computational / reading / prerequisite 占比

2. **学生画像 Agent**：为每个学生生成结构化画像：
   - **学习速度**：基于平均耗时与掌握节点数给出快/中/慢标签
   - **优势类型**：concept 类节点表现好 → "概念型"；tool 类节点表现好 → "操作型"；skill 类节点表现好 → "应用型"
   - **薄弱节点列表**：掌握未达标的节点 + 高错误率节点
   - **偏好路径**：历史节点选择序列（反映学生偏好的学习路径模式）
   - **活跃状态**：近 7 天是否有学习活动

3. **班级热力图 Agent**：聚合全班数据，在知识网络上叠加统计：
   - **节点热力值** = 1.0 − 班级平均掌握率（掌握率越低，颜色越热）
   - **错误热点**：某节点触发错题闭环次数 > 全班平均 × 1.5 时标注为"高错误节点"
   - **层次分布表现**：concept / skill / tool 三层的平均掌握率对比（用于发现学生在哪一层有系统性困难）

4. **薄弱环节识别 Agent**：自动识别班级普遍掌握率 < 60% 的节点（薄弱节点），结合错误类型分布，给出结构化分析：
   - "全班 43% 学生在 node_X 上触发过 concept 类错误 → 建议加强概念层讲解"
   - "node_Y 平均耗时是估计课时的 2.3 倍 → 建议拆分为 2 个节点（FR-11 优化建议）"

5. **教学调整建议 Agent**：基于薄弱环节分析，为教师生成具体、可操作的教学调整建议：
   - 加强讲解（增加课堂时间）
   - 补充练习（推荐额外练习题集）
   - 重新设计节点（反馈至 FR-11 知识网络动态维护）
   - 分层教学建议（对不同画像的学生给出差异化推进路径）

**输出规格（完整学情分析报告）**：
```yaml
learning_analytics_report:
  report_id: "analytics_2026_06_12_001"
  course_ref: "kn_001"
  total_students: 30
  data_cutoff_time: "2026-06-12T18:00:00Z"
  report_generated_at: "2026-06-12T18:05:00Z"

  # ---- 学生个人画像示例 ----
  per_student_profiles:
    - student_id: "student_023"
      overall_status: "on_track"              # advanced / on_track / needs_support
      nodes_mastered_count: 7
      nodes_in_progress_count: 2
      nodes_not_started_count: 3

      average_accuracy: 0.82
      average_time_vs_estimated: 0.95          # 0.95=比预估快5%

      strength_type: "操作型"                  # 概念型 / 操作型 / 应用型
      strength_evidence:
        - "tool_formula_method_07：正确率 92%，耗时低于预估 15%"
        - "tool_factorization_method_08：首次进入即掌握"

      weak_nodes:
        - node_id: "skill_model_building_12"
          status: "in_progress"
          accuracy: 0.55
          error_loops_count: 3
          note: "在真实情境建模题上持续困难，可能需要额外辅导"

      learning_path_preference: "工具层 → 技能层（在工具层节点上表现好，但进入技能层后速度放缓）"
      active_in_last_7_days: true

  # ---- 班级知识网络热力图 ----
  class_heatmap:
    overall_class_mastery_rate: 0.71

    per_node_statistics:
      - node_id: "concept_equation_essence_01"
        class_mastery_rate: 0.80
        average_accuracy: 0.78
        average_time_minutes: 35
        error_loops_per_student: 0.4
        hotness_level: "cool"                     # cool / warm / hot
      - node_id: "skill_model_building_12"
        class_mastery_rate: 0.42
        average_accuracy: 0.48
        average_time_minutes: 90
        error_loops_per_student: 2.1
        hotness_level: "hot"                      # 红色标记，需重点关注

    layer_performance_comparison:
      concept_layer: { average_mastery_rate: 0.76, note: "概念理解整体尚可" }
      skill_layer: { average_mastery_rate: 0.58, note: "技能应用是班级主要薄弱环节" }
      tool_layer: { average_mastery_rate: 0.83, note: "操作训练效果良好" }

  # ---- 薄弱环节分析 ----
  weak_points_analysis:
    - node_id: "skill_model_building_12"
      class_mastery_rate: 0.42
      dominant_error_type: "concept"
      recommendation: "加强情境建模教学，建议在课堂增加完整建模案例演练"
      priority: "high"

  # ---- 教学调整建议 ----
  teaching_adjustment_suggestions:
    - id: "adj_001"
      target: "全班教学策略"
      suggestion: "增加 1 课时课堂建模专题练习，采用'学生出题 + 互评选做'的互动方式"
      expected_impact: "skill_model_building_12 掌握率提升至 70%+"
      priority: "high"

    - id: "adj_002"
      target: "students_tier: needs_support"
      suggestion: "为 7 名 needs_support 学生推荐从概念层重新进入相关节点，补齐概念理解根基"
      priority: "medium"

  # ---- 学生分层（供教师分组教学使用） ----
  student_tiers:
    - tier: "advanced"
      count: 5
      avg_accuracy: 0.92
      recommendation: "可提前进入概念层拓展节点或跨主题学习"
      student_ids: ["student_005", "student_012", "..."]

    - tier: "needs_support"
      count: 7
      avg_accuracy: 0.58
      recommendation: "可能存在前置知识缺口，建议从概念层重新夯实"
      student_ids: ["student_023", "..."]

  data_completeness:
    has_sufficient_data: true
    data_quality_notes: "30 名学生中有 28 名有完整的章节 1 学习数据；章节 3 数据较少"
```

**关键约束**：
- 分析引擎超时保护：单次完整分析 ≤ 2 分钟；超时则返回最近一次成功报告缓存并告警
- 数据不足策略：某节点 < 3 名学生有学习数据时，该节点的统计不纳入薄弱环节判定；报告中注明"数据不足"
- 矛盾数据检测：如同一学生在同一节点同时有 mastered 与 high_error_rate，标记为数据矛盾，提示教师人工核查
- 定期自动更新：默认每 24 小时自动生成最新学情报告；教师可手动触发重新分析
- 隐私保护：学生个人画像仅对该学生本人与授课教师可见；班级热力图对教师展示但不带学生姓名标识

**验收标准**：
- [ ] 对含 30 名学生的标准班级规模，可在 ≤ 2 分钟内生成完整报告
- [ ] 可正确识别 ≥ 2 个薄弱节点（按掌握率 < 60% 判定）
- [ ] 学生个人画像中 strength_type 与 weak_nodes 与数据一致
- [ ] 报告中包含可操作的教学调整建议（每条建议含 target / suggestion / expected_impact）
- [ ] 学情分析结果可自动影响 SCENE-005 节点推荐的表现分权重

---

### 3.10 FR-10：教学评估（课程/单元末）

**优先级**：P1 · **核心定位**：核心教学能力 · 过程性评估 · **关联场景**：SCENE-008 / SCENE-001 / SCENE-003 / SCENE-006 / SCENE-007

**功能描述**：
课程或单元结束后，使用 SCENE-001 课程规划阶段产出的评估指标体系（evaluation_metrics），对照 FR-09 学情分析、FR-08 作业批改、FR-07 错题闭环、FR-03 虚拟教室等多源过程数据，进行系统性评估——为每个指标打分、产出教学反思报告与可操作的改进建议。评估结果不是对教师的排名打分，而是服务教师专业成长的过程性反思工具。

**输入规格**：
```yaml
teaching_evaluation_input:
  evaluation_scope: "unit_end"                 # course_end / unit_end / midterm_review
  unit_or_course_ref: "unit_03"                # 或 course_id
  knowledge_network_ref: "kn_001"
  evaluation_metrics_ref: "/data/eval/kn_001_evaluation_metrics.yaml"
  data_sources:                                # 多源过程数据
    - type: "virtual_classroom_summary"
      ref: "..."
    - type: "homework_grading_class_summaries"
      ref: "..."
    - type: "learning_analytics_reports"
      ref: "..."
    - type: "teacher_feedback_from_harness"     # FR-15 Harness中记录的教师反馈
      ref: "..."
  teacher_id: "teacher_001"
  teacher_self_reflection: "学生在建模题上表现较弱，可能我在课堂上的建模案例不够多。"  # 可选
```

**核心流程（指标提取 → 数据归集 → 对照评定 → 反思生成 → 改进建议）**：
1. **指标解析 Agent**：从 evaluation_metrics_ref 读取 SCENE-001 阶段定义的评估指标，提取每个 metric 的 target_node、metric_type（observational_scale / written_test / project_rubric / interview）、content、scoring_rubric、expected_target_score
2. **数据收集 Agent**：
   - 对每个指标，从对应的数据源中提取支持证据：如 observational_scale 指标 → 读取 SCENE-003 课堂表现记录；written_test → 读取 SCENE-006 作业批改；project_rubric → 读取 SCENE-002 中项目作品评估
   - 聚合全班数据形成 metric_level 的统计量（班级平均分、掌握率、标准差）
3. **教学评估 Agent**：
   - 按 scoring_rubric 为每个 metric 产出 achieved_score（0~max_score）
   - 对比 achieved_score 与 expected_target_score，给出 status: meets_target / below_target / exceeds_target
   - 为每个 metric 附结构化 supporting_evidence 列表
4. **反思引导 Agent**：
   - 汇总整体评估 → overall_rating
   - 分析 strengths 和 areas_for_improvement（自动生成）
   - 向教师提出引导性反思问题（可选，教师手动填写回复，不强制）
5. **改进建议 Agent**：
   - 对 below_target 的指标生成具体改进建议：id / target_node / suggestion / expected_impact
   - 建议可自动反馈至：(a) SCENE-002 备课辅助（下一轮备课调整）；(b) FR-11 知识网络动态维护（节点拆分/合并/新增过渡节点建议）
6. **教师确认**：教师审阅报告，可调整分数、补充反思、覆盖建议；teacher_confirmed=true 后报告正式归档

**输出规格（完整教学评估报告）**：
```yaml
teaching_evaluation_report:
  report_id: "teach_eval_2026_06_12_001"
  scope: "unit_end"
  unit_ref: "unit_03"
  course_ref: "kn_001"
  teacher_id: "teacher_001"
  generated_at: "2026-06-12T18:30:00Z"

  metric_evaluations:
    - metric_id: "m_001"
      target_node: "concept_equation_essence_01"
      metric_type: "observational_scale"
      content: "学生能否正确判断一元二次方程并解释其一般形式的意义"
      scoring_rubric: "1-5分，5分=能独立完成并解释理由"
      max_score: 5
      achieved_score: 4.2
      target_score: 4.0
      status: "meets_target"
      supporting_evidence:
        - "全班 75% 学生能独立解释一般形式"
        - "SCENE-003 课堂问答中，68% 学生能主动指出方程定义条件"
        - "相关作业正确率 78%"
      improvement_notes: "加强对'为什么需要一般形式 ax^2 + bx + c = 0（a≠0）'的讨论"

    - metric_id: "m_002"
      target_node: "skill_model_building_12"
      metric_type: "project_rubric"
      content: "学生能否在实际情境中正确建立一元二次方程模型并求解"
      scoring_rubric: "按建模过程正确性（40%）/求解过程（30%）/合理性检验（20%）/反思总结（10%）评分"
      max_score: 5
      achieved_score: 3.2
      target_score: 4.0
      status: "below_target"
      supporting_evidence:
        - "全班平均建模得分 3.2/5"
        - "主要失分点：情境→方程的转化错误（43% 学生在此丢分）"
        - "错题闭环在该节点的平均触发次数 2.1 次/学生"
      improvement_notes: "需增加课堂建模案例；采用'教师示范 → 学生小练 → 互评'的渐进式训练方式"

    - metric_id: "m_003"
      target_node: "tool_formula_method_07"
      metric_type: "written_test"
      content: "学生能否熟练使用公式法求解标准形式的一元二次方程"
      scoring_rubric: "结果正确4分；有小错误3分；结果错但公式正确1分"
      max_score: 5
      achieved_score: 4.3
      target_score: 4.0
      status: "exceeds_target"
      supporting_evidence:
        - "相关作业正确率 92%"
        - "该节点首次尝试即掌握率 85%"
        - "平均耗时低于估计课时 15%"
      improvement_notes: "考虑给优秀学生增加含参数的变式题，保持挑战性"

  overall_summary:
    overall_rating: 3.9
    strengths:
      - "工具层训练效果良好（平均掌握率 83%）"
      - "概念层入门清晰，多数学生能理解基本定义（75% 学生能独立解释）"
      - "错题闭环有效帮助学生纠正计算错误"
    areas_for_improvement:
      - "技能应用（尤其是情境建模）是班级主要薄弱环节"
      - "从工具层到技能层的跃迁衔接不畅，30% 学生在此节点停留超过 2 倍预期课时"
      - "概念层与技能层的课堂整合不足，学生感知为两个独立主题"

  concrete_improvement_suggestions:
    - id: "imp_001"
      target_node: "skill_model_building_12"
      suggestion: "增加 2-3 个完整课堂建模案例；采用'教师示范 → 小组合作建模 → 全班展示 → 同伴评价'的流程；配套训练题难度逐步提升"
      expected_impact: "该节点掌握率从 42% 提升至 75%+"
      priority: "high"
      feedback_to: ["SCENE-002 备课辅助", "FR-11 知识网络维护建议：可将该节点拆分为 2 个子节点"]

    - id: "imp_002"
      target_node: "概念_技能跨层衔接"
      suggestion: "在 concept_equation_essence_01 和 skill_method_selection_04 之间新增 1 个过渡实践节点，让学生在掌握概念后立即进行中等难度的方法选择训练"
      expected_impact: "减少学生进入技能层的挫败感，提升衔接顺畅度"
      priority: "medium"
      feedback_to: ["FR-11 网络优化：新增 transition_node 建议"]

    - id: "imp_003"
      target_node: "class_tier_strategy"
      suggestion: "对 7 名 needs_support 学生推荐返回概念层重新夯实基础；对 5 名 advanced 学生推荐进入概念层扩展节点（如二次函数与二次方程的联系）"
      expected_impact: "分层教学可提升 needs_support 学生的后续节点表现"
      priority: "medium"

  teacher_self_reflection: "学生在建模题上表现较弱，可能我在课堂上的建模案例不够多。我计划在下一单元增加 2 课时的建模专题训练。"
  teacher_confirmed: false

  # 反哺闭环：改进建议自动关联的下游系统
  automatic_feedback_to_systems:
    - system: "SCENE-002 备课辅助"
      content: "下一单元的备课请考虑在技能层增加建模案例与渐进式训练"
    - system: "FR-11 知识网络动态维护"
      content: "建议拆分 skill_model_building_12 节点为 2 个难度递进的子节点；并在概念层与技能层间增加过渡节点"
    - system: "FR-18 Harness 模板优化"
      content: "建模题的评分 rubric 可进一步细化情境建模过程的分步给分"
```

**关键约束**：
- 评估报告输出必须严格使用 SCENE-001 阶段定义的评估指标；不允许在评估阶段"新增"未在规划阶段定义的指标
- 所有 achieved_score 必须附 supporting_evidence，证据来源必须可追溯至真实过程数据（而非空泛描述）
- overall_rating 不是各 metric 的简单平均分，而是综合考虑各指标权重、教师目标与改进潜力后的综合评定
- below_target 的指标必须至少生成 1 条可操作的改进建议（含 target_node / suggestion / expected_impact）
- 报告生成响应时间 ≤ 5 分钟

**验收标准**：
- [ ] 对含 ≥ 5 个指标的标准评估输入，可完整输出教学评估报告
- [ ] 每条 below_target 指标附 ≥ 1 条改进建议
- [ ] 改进建议自动反哺至 FR-11 网络维护与 SCENE-002 备课辅助
- [ ] 报告中所有 achieved_score 附 supporting_evidence 列表
- [ ] 教师可修改分数/补充反思，teacher_confirmed 状态变更后报告正式归档

---

### 3.11 FR-11：知识网络动态维护

**优先级**：P1 · **核心定位**：核心教学能力 · 长期优化 · **关联场景**：SCENE-009 / SCENE-001 / FR-09 / FR-10

**功能描述**：
基于学生真实学习数据（FR-09 学情分析、FR-10 教学评估），系统定期（每月/每学期或教师手动触发）对知识网络进行结构性优化建议——包括节点难度调整、节点拆分、节点合并、新增过渡节点、边关系调整等。教师审核建议后，采纳的修改触发 SCENE-001 重新设计对应子网络，变更后的知识网络版本化管理（Git 提交 + 版本号递增），确保历史可追溯与可回滚。

**输入规格**：
```yaml
network_maintenance_input:
  trigger: "monthly"                        # monthly / end_of_unit / teacher_manual
  knowledge_network_ref: "kn_001"
  current_version: "1.2"
  data_sources:
    - type: "learning_analytics_report"
      ref: "analytics_2026_06_12_001"
    - type: "teaching_evaluation_report"
      ref: "teach_eval_2026_06_12_001"
    - type: "node_mastery_performance"
      ref: "/data/mastery/kn_001_all_students.json"
  teacher_id: "teacher_001"
  auto_apply_threshold: 0.85                 # 置信度 > 0.85 的建议自动进入待采纳队列
```

**核心流程（节点性能分析 → 边关系分析 → 优化建议生成 → 教师审核 → 采纳执行 → Git 提交）**：
1. **节点性能分析 Agent**：为每个节点计算以下指标：
   - designed_difficulty（原始设计难度）vs actual_difficulty（由正确率、耗时、闭环次数综合计算）
   - deviation = actual_difficulty − designed_difficulty；|deviation| > 1 时标记为"难度与设计偏差显著"
   - class_mastery_rate；< 50% 时标记为"高难度节点"
   - average_time_vs_estimated；ratio > 2.0 时标记为"可能需拆分"
   - error_loops_per_student

2. **边关系与衔接分析 Agent**：为每条 is_prerequisite 边与跨层边计算：
   - transition_success_rate（从 source_node 到 target_node 的流畅度 = 在 source_node 掌握后直接进入 target_node 且在 ≤ 2 次循环内掌握的比例）
   - transition_success_rate < 0.4 时标记为"衔接断层"，建议在中间增加过渡节点
   - 检查是否存在孤立节点（无任何入边或出边的非入口/非汇聚节点）

3. **优化建议生成 Agent**：基于上述分析，产出结构化建议列表，每条建议含：
   - **type**: split_node / merge_node / add_transition_node / increase_difficulty / decrease_difficulty / adjust_edge
   - **target(s)**: node_id 或 (from_node, to_node)
   - **problem_description**：问题描述（用数据证据）
   - **suggestion**：具体修改建议
   - **expected_impact**：预期效果（掌握率、耗时、衔接流畅度等的量化或方向性预测）
   - **confidence**：0.0 ~ 1.0（数据证据越强，置信度越高）

4. **教师审核 Agent**：以卡片形式展示每条建议，教师可选择：
   - **approve**：采纳并触发 SCENE-001 重新设计
   - **reject**：拒绝（记录拒绝原因）
   - **revise**：修改建议内容后采纳（如"拆分为 3 个子节点而非 2 个"）
   - **delay**：延迟至下次维护评估

5. **采纳与执行 Agent**：对 approve 的建议：
   - 调用 SCENE-001 重新设计受影响的子网络（仅对该节点/边及其相关的子网络进行增量重构，而非全量重构）
   - 新网络通过 Schema 校验后，生成新的知识网络版本（version + 0.1，或重大结构变更时 + 1.0）
   - Git 提交变更，commit message 格式："maintain(kn_001 v1.2→v1.3): split node_X into node_Xa, node_Xb; add transition_node between node_A and node_B"
   - 更新决策索引（FR-18），将本次网络维护决策记录为不可变 DP

6. **回滚能力**：任何版本可一键回滚至上一版本；回滚操作同样记录为 Git commit，确保所有历史可见

**输出规格（优化建议报告 + 执行结果）**：
```yaml
network_maintenance_report:
  maintenance_id: "maint_2026_06_12_001"
  kn_ref: "kn_001"
  previous_version: "1.2"
  new_version: "1.3"
  triggered_by: "teacher_manual"
  analyzed_at: "2026-06-12T19:00:00Z"

  # --- 节点性能分析 ---
  node_performance_analysis:
    - node_id: "skill_model_building_12"
      designed_difficulty: 4
      actual_difficulty: 4.8              # 学生感知比设计难得多
      deviation: 0.8
      class_mastery_rate: 0.42
      average_time_minutes: 90
      estimated_periods: 2
      time_to_estimated_ratio: 2.25
      error_loops_per_student: 2.1
      flag: "建议拆分 + 降低难度"

    - node_id: "tool_factorization_method_08"
      designed_difficulty: 3
      actual_difficulty: 3.8
      deviation: 0.8
      class_mastery_rate: 0.57
      flag: "建议降低难度或增加前置铺垫"

  # --- 边关系分析 ---
  edge_and_transition_analysis:
    - edge: "tool_formula_method_07 → skill_method_selection_04"
      transition_success_rate: 0.38
      flag: "衔接断层，建议增加过渡节点"

  # --- 优化建议列表 ---
  optimization_suggestions:
    - id: "opt_001"
      type: "split_node"
      target: "skill_model_building_12"
      problem_description: "该节点设计难度 4，但学生实际感知难度 4.8，掌握率仅 42%，平均耗时达估计课时 2.25 倍；表明节点内容过大、难度跨度太大"
      suggestion: "拆分为 2 个子节点：skill_model_building_basic_12a（从文字情境建立方程）+ skill_model_building_advanced_12b（含多条件多变量的复杂情境建模）"
      expected_impact: "split后基本节点掌握率预计提升至 70%+；高级节点作为可选拓展"
      confidence: 0.88
      teacher_decision: "approve"

    - id: "opt_002"
      type: "add_transition_node"
      target: "tool_formula_method_07 → skill_method_selection_04"
      problem_description: "从工具层到技能层的衔接流畅度仅 38%，30% 学生在此节点停留超过 2 倍预期课时"
      suggestion: "新增 transition_node 过渡节点：'tool_to_skill_practice_07.5'，包含 5-8 道带脚手架的情境建模入门题"
      expected_impact: "衔接流畅度提升至 65%+"
      confidence: 0.75
      teacher_decision: "approve"

    - id: "opt_003"
      type: "decrease_difficulty"
      target: "tool_factorization_method_08"
      problem_description: "该节点设计难度 3 但实际难度 3.8，且班级掌握率仅 57%；因式分解对初学者的难度预期偏低"
      suggestion: "降低该节点设计难度标注至 4（或拆分为十字相乘基础 + 十字相乘进阶 2 个节点）"
      expected_impact: "降低预期可避免教师过度挤压课时；拆分则可进一步细化学习颗粒度"
      confidence: 0.65
      teacher_decision: "revise"
      teacher_note: "改为拆分为 2 个子节点，而不是降低难度标注"

  # --- 采纳与执行结果 ---
  execution_result:
    status: "completed"
    new_nodes_created: 3
    new_edges_created: 5
    nodes_removed: 1
    knowledge_network_version_bumped: "1.2 → 1.3"
    git_commit_hash: "a1b2c3d4e5f6..."
    decision_index_updated:
      new_dp_ids: ["DP-MAINT-001", "DP-MAINT-002", "DP-MAINT-003"]
      compile_status: "success"
    rollback_available: true

  # --- 数据充分性警告（如适用）---
  data_sufficiency:
    has_sufficient_data: true
    nodes_with_insufficient_data: 0
    total_nodes: 12
    warning_note: "数据覆盖充分"

  # --- 下次触发安排 ---
  next_scheduled_maintenance:
    scheduled_at: "2026-07-12T19:00:00Z"
    trigger: "monthly"
```

**关键约束**：
- 不基于单一学生数据做出结构性变更建议；需基于 30% 以上节点的 ≥ 5 名学生平均数据
- 数据不足的节点（< 5 名学生数据）不纳入结构性建议，仅在报告中标注"需持续观察"
- 任何节点/边的删除必须由教师明确 approve；系统不得自动删除已有节点
- 维护后新的知识网络必须通过 FR-05 的完整 Schema 校验方可生效
- Git 版本管理必须保留完整历史；任一版本可一键回滚，回滚操作同样记录
- 维护频率不高于每 2 周一次（避免过度调整造成学生路径不稳定）

**验收标准**：
- [ ] 可基于标准学情+评估数据生成 ≥ 2 条优化建议
- [ ] 每条建议含 type / problem_description / suggestion / expected_impact / confidence
- [ ] 采纳建议后，知识网络版本号正确递增
- [ ] Git 提交记录清晰可读（含修改摘要）
- [ ] 回滚功能可用（模拟 revert 一个版本后，网络内容与原版本一致）

---

### 3.12 FR-12：配置持久化与管理

**优先级**：P1 · **核心定位**：运营支撑 · 配置保存与版本管理 · **全系统使用**

**功能描述**：
系统中所有可持久化对象——知识网络、Agent 配置（FR-02 产出）、Harness 提示词模板（FR-15 定义）、评估指标 rubric、作业批改记录、学情分析报告、教学评估报告、网络维护历史——均需以标准化格式（YAML / JSON / Markdown）保存至本地文件系统，并支持：按条件检索、版本化管理、导入/导出、模板化复用、跨课程引用、批量操作。此外，系统维护一份全局配置注册表（System Configuration Registry），记录各配置的路径、版本、最后修改人、依赖关系，便于一致性检查与故障定位。

**配置对象分类与存储约定**：
| 配置类型 | 存储路径 | 格式 | 版本管理 | 示例 |
|---------|---------|------|---------|-----|
| 知识网络 | `/knowledge_networks/kn_{id}.yaml` | YAML | Git + version 字段 | kn_001 v1.3 |
| Agent 配置 | `/agent_configs/{scene_type}/config_{id}.yaml` | YAML | Git + semver | config_scene001_v1.2.0 |
| Harness 模板 | `/harness/templates/{template_id}.yaml` | YAML | Git + semver | tp_scene001_v1.0 |
| 评估指标 | `/evaluation/{kn_id}_metrics.yaml` | YAML | Git + version 字段 | kn_001_metrics_v1.0 |
| 学生作业/批改 | `/homework/{homework_id}/` | YAML | 不可变（写入后不可修改，教师覆盖记录为新副本） | hw_2026_06_12_001 |
| 学情分析报告 | `/analytics/{kn_id}/report_{ts}.yaml` | YAML | 时间戳命名，累积保留 | report_2026_06_12_001 |
| 教学评估报告 | `/teaching_eval/{kn_id}/report_{ts}.yaml` | YAML | 时间戳命名 + teacher_confirmed 状态 | teach_eval_2026_06_12_001 |
| 网络维护记录 | `/maintenance/{kn_id}/maint_{ts}.yaml` | YAML | Git + 关联网络版本号 | maint_2026_06_12_001 |
| 教师反馈与评分 | `/teacher_feedback/{session_id}.yaml` | YAML | 不可变写入 | sess_001_teacher_review.yaml |

**核心流程（写入 → 索引 → 查询 → 版本比较 → 模板化 → 导入/导出）**：
1. **写入代理（Persistence Agent）**：任何 FR 产出可持久化对象时，调用本 FR 的写入 API——传入对象类型 + 内容 + 元数据（版本、创建人、时间戳）；本 FR 负责按存储约定写入、生成索引条目、触发 Git 提交（对 Git 管理的对象）
2. **全局配置注册表**：系统维护 `/system/registry.json`，记录每个配置对象的：id / path / type / version / last_modified_by / last_modified_at / dependencies / git_commit_hash（如适用）；注册表在每次写入后自动更新
3. **查询代理**：提供多维度查询能力——按 type / kn_id / teacher_id / time_range / version 过滤；支持高级查询（"所有已掌握的节点+学生画像"组合查询）
4. **版本比较（diff Agent）**：对 Git 管理的配置对象（知识网络、Agent 配置、Harness 模板），提供两个版本间的结构化 diff 能力（不是纯文本 diff，而是按 YAML 字段的语义 diff——如显示"节点 X 从难度 4 改为难度 3"，"提示词模板新增了思政融合检查规则"）
5. **模板化与复用**：教师可将已确认有效的 Agent 配置/Harness 模板/知识网络片段保存为模板（标记 is_template=true），用于新课程或新教师快速启动；模板可引用/克隆/参数化
6. **导入/导出**：对任一配置对象或配置集合（如"某课程全部配置"），可导出为单文件（tar.gz 或 zip）用于备份或跨系统迁移；导入时自动进行 schema 校验，不合法内容拒绝导入

**输出规格（查询示例）**：
```yaml
system_config_registry:
  last_updated: "2026-06-12T19:30:00Z"
  registry_schema_version: "1.0"
  total_objects_tracked: 248

  registered_objects:
    - id: "kn_001"
      type: "knowledge_network"
      path: "/knowledge_networks/kn_001.yaml"
      version: "1.3"
      current_hash: "a1b2c3d4..."
      last_modified_by: "teacher_001"
      last_modified_at: "2026-06-12T19:00:00Z"
      dependencies: ["tp_scene001_v1.0", "kn_001_metrics_v1.0"]
      git_commit_hash: "a1b2c3d4e5f6..."
      is_template: false

    - id: "tp_scene001_v1.0"
      type: "harness_template"
      path: "/harness/templates/tp_scene001_v1.0.yaml"
      version: "1.0"
      current_hash: "b2c3d4e5..."
      last_modified_by: "system"
      last_modified_at: "2026-06-01T09:00:00Z"
      dependencies: []
      git_commit_hash: "b2c3d4e5f6..."
      is_template: true              # 可作为模板被新课程引用

    # ... 更多对象 ...
```

**关键约束**：
- 学生个人数据（作业批改记录、个人画像、错题闭环）不得被导出为跨系统迁移数据（隐私保护）；仅汇总匿名数据可导出
- Git 管理的配置对象：任何修改必须伴随 Git commit；不允许"游离"变更（未提交的修改不得被下游 FR 使用）
- 不可变对象（作业批改、教师反馈、学情报告）：写入后不支持修改；如需修改需写入新副本（带版本号或时间戳），并在注册表中标记为替代关系
- 配置一致性检查：每次更新注册表后，需验证所有 dependencies 引用的对象是否存在且版本兼容（如 Agent 配置引用的 Harness 模板必须存在）
- 存储容量保护：系统默认容量配额 ≤ 10 GB；超过阈值时告警并暂停非必要写入（保留核心学习数据）

**验收标准**：
- [ ] 任一 FR 产出的配置对象可正确持久化并出现在注册表中
- [ ] 多维度查询可返回正确结果（按 type + teacher_id + time_range 过滤）
- [ ] 知识网络 v1.2 与 v1.3 之间可生成结构化 diff（非纯文本）
- [ ] Harness 模板标记 is_template=true 后，可在新课程创建时被引用
- [ ] 导入的知识网络必须通过 FR-05 Schema 校验方可生效

---

### 3.13 FR-13：人机协同接口

**优先级**：P1 · **核心定位**：运营支撑 · 教师确认与反馈 · **全系统交互点**

**功能描述**：
在系统的多个关键节点——课程规划阶段确认、Agent 配置确认、备课辅助方案审阅、教学评估报告确认、网络维护优化建议审核、Harness 模板调整——系统需暂停自动化流程，向教师呈现结构化决策卡片，并支持教师"批准 / 批准并批注 / 修改内容 / 拒绝并说明原因 / 延迟决策"五类操作。教师的所有反馈、评分、批注、修改必须结构化记录，供：(a) Harness 作为高质量反馈样本（FR-15 feedback_pool）；(b) 历史审计（FR-14）；(c) 模型优化与模板迭代（FR-15 模板版本化）。

**核心交互场景（Human-in-the-Loop Points）**：
| 场景 | 触发时机 | 教师可操作 |
|------|---------|----------|
| SCENE-001 Stage 1 确认 | 教学目标设计 Agent 产出后 | approve / revise（编辑目标列表）/ reject（重新设计） |
| SCENE-001 Stage 2 确认 | 课程结构设计 Agent 产出后 | approve / revise（调整结构单元与课时）/ reject |
| SCENE-001 Stage 3 确认 | 知识网络构建 Agent 产出后 | approve / revise（节点/边调整）/ reject |
| SCENE-002 备课审阅 | 每个节点的教案+学案生成后 | approve / approve_with_comments / revise / reject |
| SCENE-008 教学评估报告 | 完整评估报告产出后 | approve / adjust_score / add_reflection / revise_suggestions |
| SCENE-009 网络优化建议 | 每条优化建议 | approve / reject / revise / delay |
| FR-15 Harness 模板版本更新 | 模板迭代提案（基于 feedback_pool 分析） | approve / reject / revise |
| FR-06 节点推荐（可选教师审核模式） | 学生节点推荐前 | 覆盖推荐结果 / 确认推荐 / 不干预 |

**交互接口规范**：
- **决策卡片（Decision Card）**：每个待确认对象以卡片形式呈现，卡片包含：
  - 对象类型与 ID
  - 当前版本号与上次确认版本的 diff 摘要
  - Agent 的产出内容摘要（不超过 200 字）
  - 支持的操作按钮（与场景匹配）
  - 文本框（用于批注/修改原因）

- **延迟决策（Delay）**：教师可将某决策标记为"延迟"，并设置提醒时间（如 3 天后提醒）。延迟期间，下游流程不阻塞（系统以"draft"版本继续运行，并在教师确认后以 confirmed 版本替换）。

- **版本化修改记录**：每次 approve/revise/reject 操作记录为一条 immutable entry，包含：actor / role / action / timestamp / current_version / new_version / content_diff / reason_or_comment

**反馈数据结构**：
```yaml
teacher_interaction_log:
  session_id: "sess_001"
  interaction_id: "ia_2026_06_12_015"
  target_object:
    type: "knowledge_network"
    id: "kn_001"
    stage: "stage_3"
    version_before: "1.2"
    version_after: "1.3"

  teacher_id: "teacher_001"
  action: "revise"
  timestamp: "2026-06-12T20:00:00Z"

  structured_feedback:
    overall_rating_to_agent_output: 0.80   # 0.0 ~ 1.0，教师对 Agent 产出的整体评分
    # 教师对节点与边的具体调整
    node_modifications:
      - node_id: "skill_model_building_12"
        field: "estimated_periods"
        old_value: 2
        new_value: 4
        reason: "该节点对学生而言难度偏大，需加倍课时"
      - node_id: "tool_factorization_method_08"
        field: "title"
        old_value: "因式分解法求解一元二次方程"
        new_value: "十字相乘法基础 + 进阶练习"
        reason: "学生在十字相乘上持续困难，需拆分节点并增加练习"

    free_text_comment: "整体结构合理，但在技能层的过渡节点设计不足。建议在后续维护中继续关注此处的衔接流畅度。"

  # 反馈流入 Harness feedback_pool 的引用
  routed_to:
    - system: "FR-15 Harness feedback_pool"
      pool_entry_id: "fb_2026_06_12_008"
    - system: "FR-14 Audit log"
      audit_entry_id: "audit_2026_06_12_015"

  downstream_actions_triggered:
    - "FR-12 配置持久化：保存 kn_001 v1.3"
    - "FR-12 Git 提交"
    - "FR-18 决策索引编译：生成 DP-MAINT-*"
```

**教师工作区仪表板（Workspace Dashboard）**：
教师登录后展示以下信息：
- 待确认决策卡片列表（按优先级排序：网络维护建议 > 教学评估 > 备课 > 课程规划）
- 最近教学评估报告（摘要 + 改进建议列表）
- 班级学情概览（薄弱节点、学生分层统计）
- 活跃课程的知识网络版本与状态
- Harness 模板更新提案（如系统建议更新模板）

**关键约束**：
- 教师交互响应时间 ≤ 1 秒（操作点击 → 操作反馈展示）
- 所有教师操作必须记录至审计日志（FR-14）；不允许"匿名"操作
- 延迟决策不得阻塞系统其他正常功能（如备课、虚拟教室）
- free_text_comment 上限 1000 字
- 教师评分（0.0 ~ 1.0）必须结构化记录至 FR-15 feedback_pool 以便后续模板优化

**验收标准**：
- [ ] 课程规划 3 个 stage 均可正确触发教师确认流程，产出的 kn_xxx.yaml 含 teacher_confirmed 字段
- [ ] 教师修改操作可正确触发版本号递增 + Git 提交
- [ ] 教师评分与批注结构化记录至 feedback_pool，可被 FR-15 读取
- [ ] 延迟决策设置 3 天提醒后，3 天后系统在教师仪表板中正确显示提醒
- [ ] 仪表板中展示的班级学情与 FR-09 最新学情分析报告一致

---

### 3.14 FR-14：可观测性与审计

**优先级**：P1 · **核心定位**：运营支撑 · 执行追踪与审计 · **全系统使用**

**功能描述**：
系统必须对所有关键操作与 Agent 执行流提供可观测性能力——包括结构化日志（非自然语言日志）、审计追踪（谁在何时做了什么决策）、执行回放（某场景从启动到完成的完整 Agent 输出序列）、系统健康指标监控、异常告警。审计日志不可篡改（采用 append-only 存储 + 每 100 条记录生成 hash 链表校验）。

**核心能力模块**：

1. **结构化日志（Structured Logging）**：
   每个 Agent 执行产出标准化日志条目：
   ```
   [agent_id] [timestamp] [log_level] [session_id] [context_tags]
   event_type: TASK_STARTED / TASK_COMPLETED / VALIDATION_PASSED /
               VALIDATION_FAILED_RETRY / EXCEPTION / HUMAN_APPROVAL_REQUIRED /
               FEEDBACK_RECEIVED / CONFIG_LOADED / DATA_SOURCE_ACCESSED
   payload: {结构化事件数据}
   ```
   - log_level: DEBUG / INFO / WARN / ERROR / CRITICAL
   - context_tags: scene=SCENE-001 / kn=kn_001 / teacher=teacher_001 等
   - 日志文件路径：`/logs/agents/{session_id}_{date}.log`

2. **审计追踪（Audit Trail）**：
   对每一次教师决策（FR-13 中定义的 approve/revise/reject/delay）生成不可变审计条目，采用 append-only 方式写入 `/logs/audit/audit_ledger_{month}.log`；每 100 条记录生成一条 hash-chain 校验记录（前 100 条的 SHA-256），用于防篡改检测。审计条目包含：
   - actor_id / role（teacher / system_admin）
   - timestamp
   - target_object + version_before + version_after
   - action + reason_or_comment
   - content_diff 摘要
   - sha256_prev（上一条记录的 hash，构成链）
   - sha256_self

3. **执行回放（Execution Playback）**：
   对任一 session_id，系统可：
   - 按时间顺序重播 Agent 输出序列（包括 Harness 校验失败、重试、教师确认等）
   - 以时间线视图展示：各 Agent 启动/完成时间、Token 使用量、关键节点耗时
   - 支持定位到具体错误或校验失败事件，并展示当时的 input/output 与 validation error

4. **系统健康指标（System Health Metrics）**：
   定期（默认每 5 分钟）采集并持久化：
   - Agent 编排成功率、平均响应时间、Token 使用量分布
   - Harness 校验通过率、各 FR 的校验失败率
   - 各知识网络的节点掌握率分布、学生活跃度分布
   - 存储使用量（是否接近容量阈值）、外部 LLM API 调用成功率/错误率

5. **异常告警（Alerting）**：
   - 规则触发：如"连续 5 个 Agent 调用 Harness 校验失败"、"LLM API 错误率 > 10%"、"存储容量 > 90%"、"某班级所有节点掌握率均 < 40%"
   - 告警渠道：写入教师仪表板 alert 区 + 系统管理员邮件通知（如配置）
   - 告警等级：info / warning / critical

**输出规格（审计条目示例）**：
```yaml
audit_entry:
  entry_id: "ae_2026_06_12_021"
  actor:
    id: "teacher_001"
    role: "teacher"
  action:
    type: "revise"
    target: { type: "knowledge_network", id: "kn_001" }
    version_before: "1.2"
    version_after: "1.3"
    summary: "拆分 skill_model_building_12 为 2 个子节点，新增过渡节点"
    reason: "技能层过渡不足，学生在此节点普遍耗时超过估计 2 倍"
  timestamp: "2026-06-12T20:00:00Z"
  content_diff_summary:
    nodes_added: 2
    nodes_removed: 1
    edges_added: 4
    edges_removed: 1
    difficulty_changed: 1
  hash_prev: "sha256:7b6d2f8e..."
  hash_self: "sha256:8c7b1e3a..."
  is_verified: true  # 系统读取该条时重新计算hash，确认与hash_self一致
```

**关键约束**：
- 审计日志必须 append-only，不允许编辑或删除历史条目
- 每 100 条审计记录必须生成 hash-chain 校验；系统启动时自动校验完整 hash 链，若发现不一致则告警
- 执行回放不得修改原数据（只读）；如需要"重新执行"，必须以新的 session_id 启动
- 系统健康指标采集对系统主流程性能影响 ≤ 2%（异步采集，后台进程）
- 学生个人敏感信息（如 free_text_comment 中含具体学生姓名）在审计日志中脱敏处理

**验收标准**：
- [ ] 一个完整 SCENE-001 课程规划 session 可生成 ≥ 50 条结构化日志（涵盖各 Agent 启动/完成/校验/反馈）
- [ ] 审计条目 hash 链在 1000 条记录的模拟写入中保持一致
- [ ] 对已完成的 session，执行回放可正确展示 Agent 输出时间线
- [ ] 系统健康指标可在仪表板中正确展示，异常告警可触发
- [ ] 学生姓名在审计日志中被脱敏（显示为 student_id 而非真实姓名）

---

### 3.15 FR-15：Harness 约束层

**优先级**：P0 · **核心定位**：约束与合规 · Agent 行为驾驭 · **全系统强制**

**功能描述**：
作为所有 Agent 执行流的强制性约束层，Harness 确保：(a) 每个 Agent 的输入/输出严格符合 schema；(b) 提示词模板结构固定、可审计、版本化；(c) 工具调用严格遵循权限白名单；(d) 输出经过内容边界过滤；(e) 教师反馈自动入池并驱动模板迭代。Harness 同时作为 FR-18 知识编译的 schema 校验引擎，确保决策索引产物格式一致。

**详细功能模块（本 FR 与 dp_arch_07 中的详细描述一一对应）**：

1. **六区块提示词模板系统（与 dp_arch_07 4.1 对应）**：
   - role_definition / task_scope / output_format / prohibited_topics / todo_template — 这 5 个区块在模板锁定后，Agent 运行时不可通过推理修改
   - dynamic_injection — 仅该区块允许在运行时注入（课程名、决策索引摘要、历史记忆摘要等）
   - 模板绑定：在 FR-02 Agent 配置生成时，为每个 Agent 指定唯一模板 ID；运行时由 Harness 校验："此 Agent 仅可使用此模板"

2. **三阶段校验管道（与 dp_arch_07 4.2 对应）**：
   - **阶段 1：Schema 校验**：JSON parse 成功 → 必填字段存在 → 类型正确 → 数值范围合法 → 枚举值合法 → 自定义规则（如"节点 layer 分布至少每层 1 个"）
   - **阶段 2：内容边界过滤**：禁止话题正则匹配 / 关键词黑名单 / 长度上限 / 主题相关性（对教师反馈内容，检查是否与当前 topic 相关）
   - **阶段 3：任务完整性检查**：待办清单覆盖检查（output 中是否包含 todo_template 中列出的所有 required 任务）；结构一致性（如 sum(单元课时) ≈ 总课时）
   - **失败重试**：校验失败自动重试 ≤ 3 次；超过阈值触发人工干预
   - 每阶段校验结果结构化记录（通过/失败 + 失败原因），入 FR-14 审计日志

3. **工具权限白名单（与 dp_arch_07 4.3 对应）**：
   - 白名单外工具调用拒绝率目标 = 100%
   - 工具参数级校验：类型/pattern/range 检查（防止参数注入）
   - 黑名单路径（如禁止访问 /etc/、/home/）
   - 沙箱执行（Shell/代码在 Modal/Deno/Daytona 沙箱中执行，主进程与 Agent 进程隔离）
   - 调用频率控制（max_calls_per_session）

4. **反馈闭环与模板版本化（与 dp_arch_07 4.4 对应）**：
   - feedback_pool：所有来自 FR-13 的教师评分与批注均结构化入池
   - 反馈分析 Agent：每月分析 feedback_pool，识别"经常被教师修改"的模板或"常见拒绝原因"，生成模板迭代提案
   - 模板更新流程：提案 → 教师审核 → 新版本发布 → 旧版本保留 30 天兼容期 → 停用
   - 模板版本 semver：patch（小修，兼容）/ minor（新增功能，兼容）/ major（不兼容变更）
   - 变更审计：每次模板版本更新入 FR-14 审计日志

5. **偏离检测与重置（与 dp_arch_07 4.5 对应）**：
   - 连续 2 次输出偏离任务主题或违反禁止事项时，Harness 自动重置该 Agent 内部状态（清空对话历史、重新加载模板），并从当前任务重新开始
   - 重置事件入审计日志；3 次重置仍失败 → 触发人工介入告警

**Schema 示例（知识网络节点校验 schema）**：
```yaml
schema:
  schema_id: "schema_kn_node_v1.0"
  for_fr: "FR-05"
  description: "知识网络单个节点的输出 schema"

  fields:
    - name: "id"
      type: "string"
      required: true
      pattern: "^(concept|skill|tool)_[a-z0-9_]+_[0-9]+$"

    - name: "layer"
      type: "enum"
      required: true
      allowed_values: ["concept", "skill", "tool"]

    - name: "title"
      type: "string"
      required: true
      max_length: 120

    - name: "bloom_level"
      type: "enum"
      required: true
      allowed_values: ["remember", "understand", "apply", "analyze", "evaluate", "create"]

    - name: "difficulty"
      type: "integer"
      required: true
      min: 1
      max: 5

    - name: "can_self_learn"
      type: "boolean"
      required: true

    - name: "estimated_periods"
      type: "integer"
      required: true
      min: 1
      max: 20

    - name: "mapped_unit"
      type: "string"
      required: true

    - name: "teaching_objectives"
      type: "object"
      required: true
      subfields:
        knowledge: { type: "list<string>", required: true }
        ability:   { type: "list<string>", required: true }
        quality:   { type: "list<string>", required: true }

  custom_rules:
    - rule_id: "layer_diversity_minimum"
      description: "知识网络中 concept/skill/tool 每层至少 1 个节点"
      check: "len(nodes where layer='concept') >= 1 AND len(nodes where layer='skill') >= 1 AND len(nodes where layer='tool') >= 1"

    - rule_id: "total_periods_reasonable"
      description: "节点总课时与 stage2 设计总课时之差应 <= 10%"
      check: "abs(sum(nodes.estimated_periods) - stage2.total_periods) / stage2.total_periods <= 0.10"
```

**关键约束**：
- 未授权工具调用拒绝率 = 100%
- 结构化输出合规率 ≥ 95%
- Harness 校验延迟 ≤ 500ms（纯本地计算，不涉及 LLM 调用）
- 模板版本更新须 ≥ 3 名教师审核通过后方可发布（P0 模板）
- 反馈池数据可匿名化用于模板优化（不暴露教师/学生姓名）

**验收标准**：
- [ ] 所有 Agent 运行时必须绑定 Harness 模板；模板缺失的 Agent 无法启动
- [ ] 三阶段校验管道可拒绝格式错误/越权调用/内容违规的输出
- [ ] feedback_pool 中累计 ≥ 100 条反馈后，系统可生成模板迭代提案
- [ ] 模板更新后，下游 Agent 可在兼容期内自动使用新版本
- [ ] 连续 2 次偏离主题的输出可触发重置（模拟测试场景下验证）

---

### 3.16 FR-16：思政融合设计与审核

**优先级**：P1 · **核心定位**：约束与合规 · 元素融合建议 · **SCENE-002 备课辅助相关**

**功能描述**：
在 SCENE-002 备课辅助阶段，系统为每个知识网络节点生成思政融合建议——基于节点主题、教学目标、当前社会热点，产出"思政元素 + 融入方式 + 课堂活动 + 课时占比"的结构化建议。思政融合设计遵循"Agent 提案 → 教师审核 → 教师确认 → 方可写入教案/学案"的双人确认流程；系统不自动写入（即使是教师批准的内容，也必须由教师执行 explicit 的"写入确认"操作）。同时，Harness 的内容边界过滤针对思政建议增加额外审核规则（FR-15 阶段 2 的扩展）。

**思政融合建议数据结构**：
```yaml
ideological_integration_suggestion:
  suggestion_id: "ideol_sugg_n001_001"
  target_node_id: "concept_equation_essence_01"
  teacher_id: "teacher_001"
  generated_at: "2026-06-12T11:00:00Z"

  # --- 1. 思政元素 ---
  ideological_element:
    category: "数学文化与数学史"  # 分类：数学文化与数学史 / 现实应用中的价值观 /
                                  #      科学精神与批判性思维 / 社会公平与公共政策 /
                                  #      文化自信与传统文化中的数学智慧 / 其他
    keywords: ["一元二次方程的历史", "中国古代数学成就", "文化自信"]
    description: "通过介绍中国古代数学典籍中对一元二次方程（如《九章算术》中的'少广'章）的早期研究，让学生了解中国数学历史成就，培养文化自信"

  # --- 2. 融入方式 ---
  integration_method: "课堂讨论 + 案例分享"  # 讲授插入 / 案例分享 / 讨论活动 / 情境任务嵌入
  # 融入位置：概念引入/例题讲解/课堂练习/课后作业/独立专题
  integration_points:
    - location: "概念引入环节"
      timing_minutes: 3
      description: "在引入 ax^2+bx+c=0 的一般形式前，用 3 分钟介绍中国古代数学家对同类问题的解法"

  # --- 3. 课堂活动 ---
  classroom_activity:
    activity_type: "short_sharing"     # short_sharing / group_discussion /
                                       # scenario_task / reflection_writing
    duration_minutes: 5
    content: "让 2-3 名学生课前预习资料，在课堂上简要分享中国古代数学家的一项相关成就；其他同学补充或提问"
    materials: ["简要资料：《九章算术》少广章摘录（1页）"]

  # --- 4. 课时占比与评估方式 ---
  time_allocation:
    total_in_class_minutes: 8
    note: "占该节点总课时的 10% 左右"
  evaluation:
    type: "participation_observation"  # participation_observation / reflection_note /
                                       # embedded_in_exam / no_explicit_eval
    description: "通过课堂分享的参与度与学生反映评估效果；不额外设置考试分值"

  # --- 5. 审核状态与流程 ---
  review_status: "pending"           # pending / approved / rejected / revised
  teacher_comments: null             # 教师填写
  teacher_confirmed_for_write: false  # 教师 explicit 的写入确认（双重确认）
  harness_content_verification: "pending"  # Harness 内容边界过滤扩展审核

  # --- 6. 沉淀与复用 ---
  can_be_template: false             # 是否可以沉淀为可复用模板（教师手动选择）
  related_template_ref: null
```

**核心流程（Agent 提案 → Harness 内容审核 → 教师审核 → 教师写入确认 → 写入教案 → 可沉淀为模板）**：
1. **思政 Agent**：基于节点内容 + 可选当前社会热点数据库（本地或教师提供关键字），按上述数据结构生成建议
2. **Harness 内容审核**：思政建议额外经过内容边界过滤扩展——检测敏感关键词、检查是否偏离学科教学范畴、确保语句无歧义且符合教育定位
3. **教师审核**：以卡片形式向教师展示 suggestion，教师可选：approve / reject / revise（修改元素/方式/活动）
4. **教师写入确认**（Double Confirmation）：教师审核通过后，系统弹出"是否将此思政建议写入该节点的教案和学案？"二次确认；教师选择"确认写入"后方写入
5. **写入教案与学案**：在 teaching_package 的教案 teaching_process 和学案中嵌入对应环节
6. **沉淀模板**：教师可将优秀设计标记 can_be_template=true，系统自动在 `/harness/templates/ideological/` 中生成模板文件，供后续课程或其他教师引用

**Harness 思政内容审核扩展规则**：
- 关键词黑名单：维护一份教育场景不宜使用的关键词清单（如政治敏感词、不当表述）
- 学科相关性检查：思政元素必须与节点的知识/技能目标相关；纯粹的"口号植入"标记为 low_quality
- 时间合理性：建议的课程占比不得超过该节点课时的 15%（避免喧宾夺主）
- 不可自动生成：教师未审核通过的建议不得出现在教学包中

**关键约束**：
- 思政建议必须通过教师 explicit 写入确认后方可进入教学包；系统永远不自动写入
- 写入操作在审计日志（FR-14）中记录为"教师写入确认"，包含 teacher_id、suggestion_id、时间戳
- 思政建议中的时间占比不得超过节点总课时 15%
- 教师可选择"本次课程不设置思政建议"（系统尊重此选择，不强制产出）

**验收标准**：
- [ ] 对 5 个不同类型节点输入，思政 Agent 可产出 5 条合法建议
- [ ] 教师未点击"确认写入"时，教案文件中不含思政建议内容
- [ ] Harness 可检测出包含不当关键词的思政建议（并在审核界面高亮标记）
- [ ] 优秀建议可被标记为模板，可在下次课程创建时被引用
- [ ] 教师可选择"不设置思政建议"，系统尊重此选择且不出相关提示

---

### 3.17 FR-17：可视化配置界面（可选）

**优先级**：P2 · **核心定位**：扩展能力 · 图形化操作 · **前端 Web 应用**

**功能描述**：
提供基于 Web 的图形化界面，让非技术背景教师可以不直接编辑 YAML/JSON 文件，通过交互式表单/拖拽操作完成：课程规划、知识网络构建与编辑、Agent 配置设置、Harness 模板调整、学情分析可视化、网络优化建议审核、教师工作区仪表板（与 FR-13 一致）。该界面为可选功能——所有核心功能在命令行/API 模式下均可工作；界面只是降低使用门槛的交互层。

**核心功能模块**：
1. **课程规划工作流（Workflow Editor）**：分三步表单——教学目标 → 课程结构 → 知识网络（最后一步以思维导图/分层树可视化）
2. **知识网络可视化编辑器**：三层节点可独立展示/折叠；节点卡片可拖拽；新增/编辑节点通过弹窗表单；边关系通过"拖拽连线+类型选择"设置；自动校验 layer 分布与边方向规则
3. **Agent 配置表单**：下拉选择角色 → 自动加载模板 → 调整 tone/specialty → 预览配置 YAML
4. **Harness 模板编辑器**：六区块分段编辑界面；版本切换与 diff 对比；历史版本回滚
5. **学情分析图表**：班级热力图（在网络图上叠加彩色高亮）、学生分层柱状图、节点掌握率分布曲线、薄弱节点列表+建议
6. **教学评估报告查看器**：指标得分雷达图、below_target 节点高亮、改进建议卡片
7. **网络优化建议审核界面**：每条建议卡片化展示，支持 approve/reject/revise/delay 四按钮
8. **教师工作区仪表板**：与 FR-13 中的仪表板一致（web 版交互增强）

**技术约束**：
- 前端：React / Vue（任一皆可，技术选型灵活）
- 后端：FastAPI / Flask（提供 RESTful API 桥接各 FR 的业务函数）
- 状态管理：前端操作提交至后端 API 后，由 FR-12 配置持久化与 Git 提交统一处理；前端不得直接操作文件系统
- 权限控制：教师仅可操作自己的课程与配置；管理员可查看系统级指标但不得修改教师内容
- 响应式设计：支持桌面端浏览器（Chrome/Firefox/Safari）与移动端（有限支持）

**输出规格（API 响应示例）**：
```yaml
api_response:
  status: "success"
  http_status_code: 200
  data:
    knowledge_network:
      id: "kn_001"
      nodes_count: 14
      edges_count: 22
      # ... 省略网络具体数据 ...
    warnings:
      - message: "节点 skill_model_building_advanced_12b 未设置前置依赖边"
        type: "edge_validation"
        severity: "warning"

  request_id: "req_api_2026_06_12_00042"
  server_timestamp: "2026-06-12T21:00:00Z"
```

**关键约束**：
- 该 FR 为 P2 优先级——v1.0 之前不强制实现；但在系统设计中必须预留 API 接口位置，以便未来接入
- 前端交互操作不得绕过 Harness 校验——所有前端提交的数据，在后端必须经过与 CLI 模式相同的校验管道
- 前端不得暴露底层实现细节（如模板内部区块 ID、Git commit hash 等）给非管理员教师
- 界面操作响应时间 ≤ 2 秒；复杂可视化（如 100 节点网络图）首次加载 ≤ 10 秒

**验收标准**：
- [ ] 通过 Web 界面创建课程规划，并与命令行方式产出等价知识网络（在结构化 diff 下一致）
- [ ] 前端提交的违规数据被后端 Harness 校验拒绝并在界面展示错误信息
- [ ] 学情分析图表在 30 节点网络上加载 ≤ 3 秒
- [ ] 教师在 Web 界面确认的思政建议被正确写入教学包（与命令行确认产出等价）
- [ ] API 文档自动生成（Swagger/OpenAPI），列出所有核心功能的接口

---

### 3.18 FR-18：知识编译与决策索引系统（方案 D）

**优先级**：P0 · **核心定位**：知识复用与上下文控制核心 · **多阶段/多场景/跨 FR 的中枢组件**

**功能描述**：
作为系统上下文管理的核心机制，FR-18 负责将各阶段/各场景/各 FR 产出的完整复杂产物（数 KB ~ 数 MB 的 YAML/Markdown），在教师确认后"编译"为极简的决策索引（Decision Index）——每个关键决策压缩为 1 条 DP 记录（≈ 100 ~ 300 Token），并关联指向完整产物的 reference_path。后续所有 Agent、所有场景的上下文注入均**不再读取完整产物**，而是直接注入决策索引。这极大降低了 LLM 调用的上下文 Token 量（通常从 4000-8000 降至 500-2000），同时确保决策一旦确认即不可变（后续场景不得"悄悄修改"先前已确认的决策）。

**DP 记录数据结构（与 dp_arch_09 中定义一致）**：
```yaml
decision_point:
  dp_id: "DP-S1-03"                         # DP-{scene_abbrev}-{3位序号}
  source_scene_or_fr: "SCENE-001-stage-1"  # 来源场景/FR
  category: "objective"                     # objective / method / structure /
                                            # node / edge / evaluation /
                                            # constraint / maintenance /
                                            # teaching_eval / ideological
  content: "教学方法 = 讲授法 + 探究法 + 项目引领"
  source_reference: "/sessions/sess_001/working/stage1_methods.yaml"
  confirmed_by: "teacher_001"
  confirmed_at: "2026-06-12T10:15:00Z"
  is_immutable: true                        # 一经确认不可修改；仅可通过新迭代生成新 DP
  revision: 1                                # 迭代版本号；首次生成 = 1
  replaces: null                            # 若为新版本迭代，此处引用被替换的旧 DP ID
  deprecated: false                         # 当被新 DP 替换后，旧 DP 标记为 deprecated

  # 可选：与其他 DP 的关系（如"这个节点 DP 依赖另一个结构 DP"）
  related_dp_ids: ["DP-S1-01", "DP-S1-02"]

  # Harness 使用的注入摘要（context_injection_summary）
  # 由 compile_agent 自动生成，确保 ≤ 300 Token
  context_injection_summary: >
    课程教学目标：1) 知识目标——理解一元二次方程的定义、一般形式、解法；
    2) 能力目标——能根据方程特征灵活选择解法、能在实际情境中建立方程并求解；
    3) 素质目标——培养抽象概括能力、逻辑推理能力、数学建模意识。
    教学方法：讲授法（基础概念）+ 探究法（发现判别式与求根公式）+
    项目引领（结课建模项目）。目标层次：概念理解 + 技能应用 + 工具操作并重。

  # Harness schema 校验：content 字段必须可被正则 ^[a-zA-Z0-9_= +,.:()?（）]+$ 匹配
  # （保证后续 Agent 注入时无格式破坏）
```

**决策索引全局结构（每个课程一份）**：
```yaml
decision_index:
  index_id: "di_kn_001"
  knowledge_network_ref: "kn_001"
  version: "1.0"
  last_updated: "2026-06-12T20:30:00Z"

  # 按来源分类组织 DP 列表
  dp_groups:
    - group_id: "scene001"
      group_name: "课程规划阶段决策"
      dp_ids: ["DP-S1-01", "DP-S1-02", "DP-S1-03", "DP-S1-04", ...]

    - group_id: "scene002"
      group_name: "备课辅助阶段决策"
      dp_ids: ["DP-S2-01", "DP-S2-02", ...]

    - group_id: "scene009"
      group_name: "网络维护决策"
      dp_ids: ["DP-MAINT-001", "DP-MAINT-002", ...]

  # 所有 DP 的平面列表（便于快速索引）
  all_dps:
    - dp_id: "DP-S1-03"
      # ... 完整 DP 记录（见上方 decision_point 结构）

  # 全局不可变声明（决策索引整体只读）
  immutability_policy:
    # 一旦编译完成并提交 Git，所有 is_immutable=true 的 DP 不可修改
    # 修改必须通过：生成新 DP -> 标记旧 DP deprecated -> 更新 index
    modification_required_new_dp_version: true

  # Harness 上下文注入摘要（全局 ≤ 800 Token，供跨场景 Agent 快速读取）
  global_context_injection_summary: >
    本课程（kn_001）核心决策摘要：教学目标涵盖知识/能力/素质三个维度，
    采用讲授法+探究法+项目引领；知识网络包含 14 个节点（concept 4 /
    skill 6 / tool 4），支持从工具层或概念层入口进入；重点难点节点为
    skill_model_building_12（已被拆分为 2 个子节点以降低难度）；
    评估指标与节点绑定；教师已确认所有关键决策。
```

**核心流程（确认触发 → 编译 → Schema 校验 → Git 提交 → 下游场景注入）**：
1. **触发编译**：当任何场景/FR 的完整产物被教师确认（teacher_confirmed=true）后，自动调用本 FR 的编译代理；触发信号含：产物类型 + 产物路径 + 教师确认信息
2. **Compile Agent**：读取完整产物，按 DP 数据结构提取关键决策（如"教学方法=X/Y/Z"、"节点 N 的 difficulty=4"、"网络中存在 4×concept/4×skill/4×tool 节点"），为每条决策生成独立 DP
3. **Harness Schema 校验**：每个 DP 经过 FR-15 的 schema_dp_v1.0 校验（content 长度上限、content 正则合规、dp_id 唯一性、replaces 合法性）
4. **生成/更新决策索引**：将新 DP 合并入全局 decision_index；如果是迭代（新 DP 替换旧 DP），设置旧 DP deprecated=true、新 DP replaces=old_dp_id
5. **生成全局上下文摘要**：Compile Agent 基于全量 DP 生成 global_context_injection_summary（由 Harness 约束 ≤ 800 Token）
6. **Git 提交**：decision_index.yaml 文件与 knowledge_wiki 页面同步提交，版本号与知识网络版本同步递增
7. **下游场景注入**：当后续场景/FR 的 Agent 启动时，Harness 自动将 global_context_injection_summary 注入 dynamic_injection 区块；如 Agent 需要更详细的决策细节，可根据 dp_id 在 decision_index 中查询（而非读取完整产物）

**决策不可变原则的执行机制**：
- 任何 DP 一旦 is_immutable=true 且已提交 Git，系统不允许通过常规编辑操作修改该 DP
- 如需修改，流程为：(a) 教师在工作区选择"迭代该决策" → (b) Compile Agent 基于修改后的完整产物生成新 DP（revision 递增，replaces 指向旧 DP）→ (c) 新 DP 经教师确认 → (d) 旧 DP 标记 deprecated → (e) decision_index 版本递增 → (f) Git 提交
- 下游场景引用 deprecated DP 时，系统提示"该决策已被新版本替换，建议使用新版"，但不强制阻止使用（以兼容已经在进行中的课程）

**Wiki 页面同步生成**：
每次 decision_index 编译后，同时生成/更新 Knowledge Wiki 页面（Markdown），结构与 dp_arch_09 5.3 一致：
- 页面标题：{课程名称} · {模块/场景名称}
- 页面元信息：版本号、编译时间、确认人、相关 DP 列表
- 决策点摘要（表格形式：DP ID / 类别 / 内容 / 引用源文件路径）
- 关键约束（来自各 FR 的非功能约束摘要）
- 风险与边界（引用源文件的风险评估）
- 相关页面（双向链接）

**Token 节省量统计**：
本 FR 自动维护一份统计——每次编译后，报告："本次决策索引共 X 条 DP，总计 Y Token；若使用完整产物，预计 Z Token；节省比例 = (Z-Y)/Z × 100%"。该数据写入 FR-14 审计日志，供未来优化参考。

**关键约束**：
- 每条 DP 的 content + context_injection_summary 合计 ≤ 300 Token（由 Harness 强制执行上限）
- decision_index 的 global_context_injection_summary ≤ 800 Token
- 不可变 DP 不得修改；任何修改必须生成新 DP（旧 DP deprecated）
- decision_index 必须与 knowledge_network 版本号同步递增
- Wiki 页面 Git 提交 message 格式："compile({scene} stage {N}): {summary}"

**验收标准**：
- [ ] 对标准课程规划输入，编译后决策索引包含 ≥ 10 条 DP，且合计 ≤ 3000 Token
- [ ] 对比完整产物，Token 节省量 ≥ 70%
- [ ] 修改一条已确认决策后，系统正确生成新 DP（revision+1、replaces 指向旧 DP）并标记旧 DP deprecated=true
- [ ] 下游 SCENE-002 Agent 启动时，Harness 正确注入 global_context_injection_summary 到 dynamic_injection 区块
- [ ] Wiki 页面正确生成且 Git 提交 message 符合格式规范
- [ ] 不可变 DP 被尝试直接修改时，系统拒绝并提示"需生成新版 DP"

---

## 四、FR 分组关系与依赖图（总结）

**平台基座（FR-01 ~ FR-04）**：负责输入路由（FR-01）→ 配置生成（FR-02）→ Agent 编排与 LLM 调用（FR-03）→ 框架协议转换（FR-04），为所有上层能力提供统一运行时环境。所有上层 FR 均依赖这一基座，但不反向依赖。

**核心教学能力（FR-05 ~ FR-11）**：负责教学内容生产与学习体验。数据流主路径：知识网络（FR-05，由 SCENE-001 产出）→ 备课辅助（SCENE-002，使用 FR-05 网络）→ 虚拟教室（SCENE-003，学生在节点学习）→ 错题闭环（FR-07 / SCENE-004，错误纠正）→ 节点推荐（FR-06 / SCENE-005，学生路径）→ 作业批改（FR-08 / SCENE-006，结果评定）→ 学情分析（FR-09 / SCENE-007，数据洞察）→ 教学评估（FR-10 / SCENE-008，过程评估）→ 网络动态维护（FR-11 / SCENE-009，长期优化）。

**约束与合规（FR-15 ~ FR-16）**：贯穿所有 Agent 执行流，Harness（FR-15）为每个 Agent 调用提供 schema 校验、提示词模板、工具白名单；思政融合（FR-16）在 SCENE-002 阶段工作。FR-15 同时是 FR-18 知识编译的 schema 引擎。

**运营支撑（FR-12 ~ FR-14）**：持久化（FR-12）保存所有产出、人机协同（FR-13）提供教师交互接口、可观测性（FR-14）提供审计与追踪。这三者构成系统的运营基础设施，被所有上层 FR 使用。

**扩展能力（FR-17）**：可视化界面（P2，可选），不影响核心功能，但显著降低教师使用门槛。

**知识编译核心（FR-18）**：知识编译与决策索引系统（方案 D）——P0 优先级，是全系统上下文管理的中枢。所有 FR 产出经教师确认后由本 FR 编译为极简索引，后续所有 Agent 上下文注入均使用索引而非完整产物。Token 节省量 ≥ 70%。

**跨 FR 数据流图**：
```
教师输入 → [FR-01 场景识别] → [FR-02 Agent 配置生成] → [FR-03 编排调度]
         ↓                                                  ↓
   [FR-12 配置持久化]                                   [FR-15 Harness 约束]
         ↓                                                  ↓
   [FR-13 人机协同]  ←── 教师确认/修改/评分/批注 ──┐       │
         ↓                                                  │
   [FR-18 知识编译 → decision_index] ←────────────────────┘
         ↓
   后续所有场景/FR 的上下文基于 decision_index 注入
   （而不再读取完整产物）
                       ↓
   [FR-05 知识网络] ──→ [SCENE-002 备课] ──→ [SCENE-003 虚拟教室]
                                                ↓
                                         [FR-07 错题闭环] <──┐
                                                │              │
                                         [FR-06 节点推荐] ───┘
                                                │
                                         [FR-08 作业批改]
                                                │
                                         [FR-09 学情分析]
                                                │
                                         [FR-10 教学评估] ──→ 反哺备课
                                                │
                                         [FR-11 网络维护] ──→ 触发FR-05重构
                                                                 │
                                                                 ↓
                                                          [FR-18 重新编译]

   [FR-14 可观测性与审计] ←── 记录所有操作与执行 ←── 所有 FR
   [FR-17 可视化界面（可选）] ←── 封装所有交互 ←── 教师
```

---

## 五、非功能需求（NFR）总览

| NFR 编号 | 指标 | 目标值 | 相关 FR |
|---------|------|--------|---------|
| NFR-01 | 场景识别响应时间 | ≤ 5 秒 | FR-01 |
| NFR-02 | 配置生成响应时间 | ≤ 10 秒 | FR-02 |
| NFR-03 | Agent 启动时间 | ≤ 30 秒 | FR-03 |
| NFR-04 | 单会话并发 Agent 数 | ≥ 10 | FR-03 |
| NFR-05 | 任务成功率 | ≥ 99% | FR-03 |
| NFR-06 | 记忆调取延迟 | ≤ 2 秒 | FR-18（decision_index 查询） |
| NFR-07 | 上下文 Token 上限 | ≤ 模型窗口 × 50% | FR-03 + FR-18 |
| NFR-08 | 上下文膨胀速率 | ≤ 5%/轮 | FR-03 |
| NFR-09 | 跨会话记忆命中率 | ≥ 70% | FR-18（决策索引 + Wiki） |
| NFR-10 | Harness 校验通过率 | ≥ 95% | FR-15 |
| NFR-11 | 未授权工具调用拦截率 | 100% | FR-15 |
| NFR-12 | Harness 校验延迟 | ≤ 500 ms | FR-15 |
| NFR-13 | 同类题目评分一致性偏差 | ≤ 5% | FR-08 |
| NFR-14 | 同类题生成 Agent 多样性 | 连续 ≥ 5 道不同题 | FR-07 |
| NFR-15 | 节点推荐解释与结果一致性 | 结构化 score_breakdown 与自然语言解释一致 | FR-06 |
| NFR-16 | 学情分析报告生成时间 | ≤ 2 分钟 | FR-09 |
| NFR-17 | 教学评估报告生成时间 | ≤ 5 分钟 | FR-10 |
| NFR-18 | 知识编译 Token 节省率 | ≥ 70% | FR-18 |
| NFR-19 | 教师操作响应时间 | ≤ 1 秒 | FR-13 |
| NFR-20 | Web 界面操作响应时间 | ≤ 2 秒（复杂可视化 ≤ 10 秒） | FR-17 |
| NFR-21 | 首次使用体验（新教师） | 15 分钟内完成首次教学场景生成 | 全系统 |
| NFR-22 | 审计日志不可篡改 | hash-chain 100% 校验通过 | FR-14 |
| NFR-23 | 学生数据隐私保护 | 个人信息脱敏，不在跨系统迁移中导出 | FR-12 + FR-14 + FR-15 |
| NFR-24 | 系统存储容量 | 默认 ≤ 10 GB（可配置） | FR-12 |
| NFR-25 | 思政建议时间占比 | ≤ 节点总课时 15% | FR-16 |
| NFR-26 | 知识网络节点迭代频率 | 不高于每 2 周一次 | FR-11 |

---

## 影响范围

- **本文件为 FR-01 ~ FR-18 的完整详细规格定义**，是所有后续架构决策（DP-ARCH-07 ~ DP-ARCH-13）与内容决策（DP-CONT-01 ~ DP-CONT-02）的基线文件
- **各场景（SCENE-001 ~ SCENE-009）的详细设计文档**引用本文件定义的 FR 编号与核心流程
- **Harness schema 版本与模板版本**：所有 schema 以本文件定义的 v1.0 为初始版本；后续修订须遵循版本化流程（FR-15）
- **知识编译产物（decision_index + Wiki 页面）**：由本文件 FR-18 定义，作为全系统上下文管理的唯一真相源


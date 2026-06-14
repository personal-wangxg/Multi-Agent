# 模块 04：功能需求（FR-01 ~ FR-18）

**父文档**：[system_requirements.md](../system_requirements.md)
**相关决策**：[DP-ARCH-06](../decisions/dp_arch_06.md)（18 FR） · [DP-ARCH-07](../decisions/dp_arch_07.md)（Harness） · [DP-ARCH-10](../decisions/dp_arch_10.md)（上下文控制）

---

## 4. 功能需求

### 4.1 功能需求总览

| 模块编号 | 模块名称 | 优先级 | 说明 |
|---------|---------|--------|------|
| FR-01 | 场景识别与分析（9 类场景） | P0 | 入口：识别当前教学场景 |
| FR-02 | Agent 配置动态生成 | P0 | 生成场景对应的 Agent 组合与配置 |
| FR-03 | Agent 编排与调度 | P0 | 运行时编排与消息路由 |
| FR-04 | 框架协议转换 | P0 | DeepAgents 与 AgentScope 之间的协议映射 |
| **FR-15** | **Harness 约束层** | **P0** | **横切约束：所有 Agent 的提示词/输出/工具权限必须受 Harness 约束** |
| FR-05 | 立体分层知识网络 | P0 | 核心数据结构：概念/技能/工具三层节点与边关系 |
| **FR-18** | **知识编译与决策索引系统** | **P0** | **将多阶段产物编译为极简 DP 索引，解决上下文膨胀问题** |
| FR-06 | 节点推荐引擎（动态学习路径） | P0 | 学生端路径推荐 |
| FR-07 | 节点内错题闭环 | P1 | 微观学习纠错循环 |
| FR-08 | 作业批改与评分 | P1 | 自动批改 + 逐题点评 |
| FR-09 | 学情分析（学生画像 + 班级热力图） | P1 | 学生画像与班级分析 |
| FR-10 | 教学评估（课程/单元末） | P1 | 教学过程反思与评估 |
| FR-11 | 知识网络动态维护（后台 meta-scenario） | P1 | 基于学习数据的网络优化建议 |
| FR-12 | 配置持久化与管理 | P1 | 配置保存与版本管理 |
| FR-13 | 人机协同接口 | P1 | 教师审批与反馈 |
| FR-14 | 可观测性与审计 | P1 | Agent 执行过程追踪与回放 |
| FR-16 | 思政融合设计与审核 | P1 | 备课阶段的思政元素融合 |
| FR-17 | 可视化配置界面（可选） | P2 | Web 界面配置能力 |

> **阅读顺序提示**：FR-15（Harness）与 FR-18（知识编译）为 P0 级横切架构决策，优先阅读以理解系统约束与上下文控制机制。其余 FR 按场景逻辑顺序排列。

### 4.2 FR-01：场景识别与分析

**功能描述**：根据用户输入的课程信息，自动识别教学场景类型并产出推荐方案。

| 需求项 | 说明 |
|--------|------|
| 输入 | 课程名称、课程简介、教学材料（可选）、用户选择模式 |
| 输出 | 场景类型、推荐 Agent 组合、初始配置模板 |
| 识别准确率 | 对预置 9 类场景的识别准确率目标 ≥ 85%（依据：基于关键词匹配 + 轻量 LLM 分类的经验基准，同类产品同类任务参考值） |
| 人工修正 | 系统推荐结果应支持教师修正覆盖 |

### 4.3 FR-02：Agent 配置动态生成

**功能描述**：根据场景类型，自动生成 Agent 定义、角色职责、通信关系与协作模式。

| 需求项 | 说明 |
|--------|------|
| Agent 角色定义 | 至少支持 teacher / student / assistant / evaluator 四类角色 |
| 框架选择 | 每个 Agent 可独立选择 DeepAgents / AgentScope / 通用框架 |
| 协作模式 | 支持主从、多角色、流水线三种基础协作模式 |
| 配置输出 | 产出标准化的 YAML/JSON 配置，供加载与执行 |
| Harness 策略绑定 | 每个 Agent 配置必须绑定对应的提示词模板、输出 schema 与工具白名单；缺省时使用框架默认策略，不得"无约束"运行 |

### 4.4 FR-03：Agent 编排与调度

**功能描述**：依据生成的配置，实际运行 Agent 并协调其间通信。

| 需求项 | 说明 |
|--------|------|
| 启动能力 | 支持一键启动多个 Agent |
| 消息路由 | Agent 间消息可按配置规则动态传递 |
| 状态同步 | 全局状态（任务进度、中间产物）在 Agent 间保持一致 |
| 失败重试 | 单 Agent 失败时应具备重试与降级机制 |
| 上下文主动控制 | 编排层在每轮交互前检查当前上下文 Token 量；超过阈值时自动触发摘要压缩/旧消息遗忘/中间产物卸载 |
| 记忆联动 | 每个 Agent 执行前，编排层应根据当前任务主题从持久记忆中检索 ≤ N 条相关记忆注入上下文（N 可配置） |
| Harness 执行绑定 | 每个 Agent 在执行前由编排层加载其对应的 Harness 约束（提示词模板、输出 schema、工具白名单），在 Agent 实例生命周期内持续生效，不可被 Agent 内部推理覆盖或绕过 |

### 4.5 FR-04：框架协议转换

**功能描述**：在 DeepAgents 与 AgentScope 之间搭建统一消息协议层，屏蔽框架差异。

| 需求项 | 说明 |
|--------|------|
| 统一消息格式 | 定义 UnifiedMessage，包含发送方、接收方、意图、内容、元数据 |
| 格式映射 | DeepAgents 的 AgentState / write_todos / VFS file 与 AgentScope 的 Message / msghub 互相映射 |
| 可扩展性 | 未来新增第三方 Agent 框架时，协议层应支持插拔式扩展 |

**DeepAgents 与 AgentScope 的适用场景区分**：

| 框架 | 典型适用场景 | 优势 |
|-----|------------|------|
| **DeepAgents** | 课程规划（SCENE-001）、备课辅助（SCENE-002）、知识网络动态维护（SCENE-009）、教学评估（SCENE-008） | 强约束的任务式流程、可审计的产物生成、状态管理清晰、Harness 约束集成更紧密；适合结构化产出驱动的场景 |
| **AgentScope** | 虚拟教室（SCENE-003）、节点内错题闭环（SCENE-004）、节点推荐引擎（SCENE-005）、作业批改（SCENE-006）、学情分析（SCENE-007） | 多智能体对话交互、消息中心广播/订阅模型、角色对话管理成熟；适合学生端动态交互与多 Agent 对话类场景 |

> 设计原则：并非强制绑定，**同一任务可混合使用两个框架**——协议转换层的核心作用就是让 DeepAgents 侧生成的"决策索引"与 AgentScope 侧的"对话交互"能无缝互通。

### 4.6 FR-15：Harness 约束层

**功能描述**：引入 Harness（驾驭层）理念——通过预设提示词模板、任务待办清单、结构化输出校验、工具权限边界与反馈闭环，将 Agent 的行为与输出严格约束在需求范围内，防止自由发散或偏离教学目标。

#### 4.6.1 提示词模板结构

每个场景对应一个模板文件（YAML/JSON），模板分为 6 个固定区块，Agent 无法通过推理修改其中任何区块的内容。

```yaml
template_id: "tpl_scene001_planner_v1.0"
scene_type: "SCENE-001"
agent_role: "课程规划 Agent"
version: "1.0"
last_updated: "2026-06-01"

# 【区块 1：角色定义 - 锁定，不可被 Agent 覆盖】
role_definition:
  role: "资深课程设计专家"
  specialty: "将课程目标分解为可执行的教学单元，擅长 K12 数学课程规划"
  tone: "专业、严谨、结构清晰"

# 【区块 2：任务边界 - 锁定】
task_scope:
  must_do:
    - "根据 {course_name} 和 {course_desc} 生成课程大纲"
    - "确保章节数量与 {total_periods} 匹配（允许 ±1 的调整容差）"
    - "每章必须包含：title、periods、objectives、key_points"
  must_not_do:
    - "不得生成超出 {course_desc} 范围的知识点"
    - "不得修改教师指定的 {total_periods}"
    - "不得在输出中包含与教学无关的内容"
    - "不得在未完成所有章节前提前结束"

# 【区块 3：输出格式规范 - 锁定】
output_format:
  format: "YAML"
  schema_ref: "schema_scene001_outline_v1.0"  # 引用下方 JSON Schema
  max_output_tokens: 4096

# 【区块 4：禁止话题列表 - 锁定】
prohibited_topics:
  - "超出 {course_desc} 范围的内容"
  - "广告、推销内容"
  - "任何形式的政治、宗教、色情、暴力内容"
  - "未经教师授权的外部链接"

# 【区块 5：待办清单模板 - 由 write_todos 驱动】
todo_template:
  - id: 1
    label: "分析课程目标"
    description: "阅读 {course_name} 和 {course_desc}，提取课程级别目标"
    required: true
  - id: 2
    label: "拆解章节结构"
    description: "根据目标数量和课时总数，将课程拆分为章节"
    required: true
  - id: 3
    label: "生成大纲草案"
    description: "为每个章节补充 title、periods、objectives"
    required: true
  - id: 4
    label: "写入 VFS"
    description: "将大纲写入 /sessions/{session_id}/working/outline_draft.md"
    required: true

# 【区块 6：注入信息 - 动态插入，不锁定】
dynamic_injection:
  system_variables:
    - course_name: "{{course_name}}"
    - course_desc: "{{course_desc}}"
    - total_periods: "{{total_periods}}"
    - difficulty: "{{difficulty}}"
  retrieved_memories: "{{retrieved_from_ltm}}"  # 从 LTM 检索注入，不超过 3 条
```

#### 4.6.2 结构化输出 Schema 示例

以下为 SCENE-001 课程规划的输出 Schema（Harness 据此执行校验）：

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "schema_id": "schema_scene001_outline_v1.0",
  "type": "object",
  "required": ["outline", "course_name", "total_periods", "created_at"],

  "properties": {
    "outline": {
      "type": "object",
      "required": ["course_name", "chapters", "progress_table"],
      "properties": {
        "course_name": {
          "type": "string",
          "minLength": 1,
          "maxLength": 100,
          "description": "课程名称，必须与输入一致"
        },
        "total_periods": {
          "type": "integer",
          "minimum": 1,
          "maximum": 100,
          "description": "总课时数，允许与输入偏差 ±1"
        },
        "chapters": {
          "type": "array",
          "minItems": 1,
          "maxItems": 20,
          "items": {
            "type": "object",
            "required": ["index", "title", "periods", "objectives", "key_points"],
            "properties": {
              "index": {
                "type": "integer",
                "minimum": 1,
                "description": "章节序号，必须连续"
              },
              "title": {
                "type": "string",
                "minLength": 2,
                "maxLength": 50,
                "description": "章节标题"
              },
              "periods": {
                "type": "integer",
                "minimum": 1,
                "maximum": 20,
                "description": "本章课时数"
              },
              "objectives": {
                "type": "array",
                "minItems": 1,
                "maxItems": 5,
                "items": { "type": "string" },
                "description": "教学目标列表，每项不超过 50 字"
              },
              "key_points": {
                "type": "array",
                "minItems": 1,
                "maxItems": 5,
                "items": { "type": "string" },
                "description": "重点知识列表"
              },
              "difficult_points": {
                "type": "array",
                "maxItems": 3,
                "items": { "type": "string" },
                "description": "难点知识列表，可为空"
              },
              "activities": {
                "type": "array",
                "maxItems": 5,
                "items": { "type": "string" },
                "description": "推荐教学活动，可为空"
              }
            }
          }
        },
        "progress_table": {
          "type": "array",
          "description": "进度计划表",
          "items": {
            "type": "object",
            "required": ["week", "content", "periods"],
            "properties": {
              "week": { "type": "integer", "minimum": 1 },
              "content": { "type": "string" },
              "periods": { "type": "integer", "minimum": 1 }
            }
          }
        }
      }
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "生成时间，ISO 8601 格式"
    }
  }
}
```

#### 4.6.3 校验管道（Validation Pipeline）

Agent 输出经由以下三阶段校验，全部通过方才交付：

```
Agent 输出
   │
   ▼
[阶段1：Schema 校验]
   ├── JSON parse 检查（输出是否为合法 JSON/YAML）
   ├── 必填字段检查（required fields）
   ├── 类型检查（string/integer/array/boolean）
   ├── 数值范围检查（minimum/maximum/length）
   ├── 枚举值检查（enum）
   └── 自定义规则检查
         │
         ├─ PASS → [阶段2]
         └─ FAIL → 重试（≤3次），记录失败原因
                     │
                     ▼
              3次失败 → 人工干预告警

[阶段2：内容边界过滤]
   ├── 禁止话题检查（prohibited_topics 命中）
   ├── 关键词过滤（自定义词表，如"广告"、"推销"）
   ├── 长度上限检查（max_output_tokens）
   └── 主题相关性检查（与 {course_topic} 的语义相似度 < 0.3 则告警）
         │
         ├─ PASS → [阶段3]
         └─ FAIL → 触发重生成，记录过滤原因

[阶段3：任务完整性检查]
   ├── 待办清单覆盖率（write_todos items_covered / total_items >= 100%）
   ├── 章节数量与课时数一致性（sum(chapters.periods) ≈ total_periods ±1）
   └── 无新增禁止任务（Agent 是否自行新增了超出模板范围的任务）
         │
         ├─ PASS → 交付给用户/下游 Agent
         └─ FAIL → 触发针对性补充或重生成
```

#### 4.6.4 工具权限白名单配置

每个 Agent 实例必须绑定一份工具白名单（Harness 在每次工具调用前校验）：

```yaml
agent_id: "agent_scene001_researcher_001"
scene_type: "SCENE-001"
framework: "DeepAgents"

# 【工具白名单 - 白名单外工具一律拒绝】
tool_whitelist:
  allowed_tools:
    - name: "read_file"
      params:
        path:
          type: "string"
          required: true
          pattern: "^/sessions/.*\\.md$"  # 仅允许读取工作目录下的 .md 文件
        max_chars:
          type: "integer"
          default: 8192
      max_calls_per_session: 50
      description: "读取 VFS 中的已有文档"

    - name: "write_file"
      params:
        path:
          type: "string"
          required: true
          pattern: "^/sessions/.*\\.md$"
        content:
          type: "string"
          required: true
          max_length: 10240
      max_calls_per_session: 20
      description: "写入中间产物到 VFS"

    - name: "search_knowledge"
      params:
        query:
          type: "string"
          required: true
          max_length: 200
        top_k:
          type: "integer"
          default: 3
      max_calls_per_session: 10
      description: "从知识库检索相关教学资料"

  # 【工具黑名单 - 明确禁止，无论是否在白名单内】
  denied_tools:
    - name: "exec_shell"
      reason: "不允许在课程规划场景中执行系统命令"
    - name: "send_external_request"
      reason: "不允许访问外部 API，防止信息泄露"
    - name: "read_file"
      # 即使 read_file 在白名单中，以下路径模式仍被禁止
      path_pattern_blacklist:
        - "^/etc/.*"
        - "^/root/.*"
        - "^/home/.*"

  # 【参数级限制 - 白名单通过后，仍需检查参数合法性】
  param_constraints:
    write_file:
      content:
        max_length: 10240                       # 单次写入不超过 10KB
        prohibited_keywords: ["password", "api_key", "secret"]  # 禁止写入敏感词

# 【沙箱配置 - Shell/Code 类工具必须在此配置】
sandbox_config:
  enabled: true
  provider: "modal"                             # modal / deno / daytona
  timeout_seconds: 30
  allowed_fqdns: ["api.eduagents.local"]        # 仅允许访问白名单域名
```

#### 4.6.5 反馈闭环机制

教师对 Agent 输出的反馈必须结构化回写，用于 Harness 持续优化：

```yaml
feedback_entry:
  feedback_id: "fb_001"
  session_id: "sess_001"
  agent_id: "agent_scene001_planner_001"
  timestamp: "2026-06-12T10:05:00Z"

  # 教师评分（0.0~1.0）
  rating: 0.6

  # 教师操作
  action: "reject"                               # approve / reject / revise

  # 拒绝/批注理由（必填）
  reason: "第2章课时分配错误：标注3课时但内容覆盖了5课时的知识点"

  # 具体批注位置
  annotations:
    - field: "outline.chapters[1].periods"
      expected_value: 5
      actual_value: 3
      comment: "这章内容很多，至少需要5课时"

  # Harness 自动处理
  auto_actions:
    - action: "inject_correction"
      target_field: "outline.chapters[1].periods"
      value: 5
      trigger_retry: true
    - action: "update_template"
      template_id: "tpl_scene001_planner_v1.0"
      note: "第2章课时判断逻辑需加强"
      new_version: "v1.1"                       # 创建新版本模板

  # 用于 LTM 更新
  ltm_update:
    memory_id: "mem_session001_conclusion"
    update_fields:
      rating: 0.6
      teacher_feedback: "第2章课时分配需更细致"
      corrected_value: "periods: 5"
```

#### 4.6.6 需求汇总表

| 需求项 | 说明 |
|--------|------|
| 场景级提示词模板 | 每个场景拥有独立的 system prompt 模板，6 个固定区块，模板可配置，不可被 Agent 内部推理覆盖 |
| 显式任务待办（todo check） | Agent 的每一步执行必须命中一条待办项；完成前不可跳过或自行新增超出模板的任务 |
| 结构化输出校验 | Agent 输出需遵循预定义 schema（JSON/YAML/教学文档结构），Harness 在输出接收阶段执行三阶段校验；校验失败自动触发重试而非交付给用户 |
| 内容边界过滤 | 对输出内容进行关键词/主题过滤，与当前教学主题无关或出现违规内容时标记为无效并触发重生成 |
| 工具权限白名单 | 每个 Agent 的可用工具由配置决定，Harness 在工具调用前做权限校验；未授权工具调用直接拒绝并记录审计 |
| 沙箱执行环境 | 代码/Shell 类调用必须在沙箱中执行，Harness 负责管理沙箱生命周期与输入输出隔离 |
| 反馈闭环 | 教师对 Agent 输出的反馈（评分、批注、拒绝）必须回写，用于迭代提示词模板或直接驱动重生成 |
| 策略可插拔 | Harness 的各条约束策略（校验 schema、过滤词表、权限配置、重试次数）应支持通过配置文件插拔与调整 |
| 约束失效告警 | 连续 N 次（默认 3 次）校验失败或超 Token 预算时，停止自动重试并转入人工干预流程 |

### 4.7 FR-05：立体分层知识网络

**功能描述**：课程规划采用三阶段设计流程：①教学目标设计（知识/能力/素质目标 + 教学方法 + 检验方式）→ ②课程结构设计（基于教学方法生成章节式/场景式/探究式结构）→ ③立体分层知识网络设计（概念层/技能层/工具层三维结构，每个知识点在不同层次投影为独立节点）。

| 需求项 | 说明 |
|--------|------|
| 阶段1：教学目标 | 输出 knowledge_goals / ability_goals / quality_goals / teaching_methods / assessment_methods |
| 阶段2：课程结构 | 输出 units 结构数组，每个 unit 含 teaching_method + estimated_periods + core_knowledge_keywords |
| 阶段3：知识网络节点类型 | concept / skill / tool 三层标记 |
| 节点属性 | bloom_level / difficulty / can_self_learn / estimated_periods / mapped_unit |
| 边关系 | 层内边（is_prerequisite）+ 跨层边（supports_understanding / enables_operation）+ 同主题边（same_topic_cross_layer） |
| 网络构建 | 教师与 Agent 共创迭代，每个阶段独立迭代确认 |
| 网络表示 | 统一 YAML/JSON 格式（含 stage1/stage2/stage3 三段结构），可序列化保存 |
| 节点掌握判定 | 每个节点有独立掌握标准（正确率/任务完成度等） |
| 多路径支持 | 网络允许多个入口节点和多条达成路径，支持分层教学 |

### 4.8 FR-18：知识编译与决策索引系统

**功能描述**（核心架构决策，已确认采纳方案D）：在多阶段/多场景的长链路 Agent 协作中，每个阶段的完整产物不直接拼入后续阶段的上下文。取而代之，由独立的"编译 Agent"将每个阶段产物自动编译为结构化决策索引（Decision Point 表），同时生成 Knowledge Wiki 页面。后续阶段以极简决策索引注入上下文，如需详细信息由 Agent 主动通过工具读取 Wiki 或完整产物。

**设计原则**（基于 LLM Wiki 思路，方案D）：

| 原则 | 说明 |
|-----|------|
| 决策前置编译，而非查询时检索 | 教师确认一个阶段的产物后，立即进行知识编译提取 DP 表；后续阶段直接消费已编译结果，不触发重新检索 |
| 决策点不可变更 | 每个 DP 一经教师确认即为不可变；修改仅通过"迭代新方案"方式生成新 DP，旧 DP 保留历史版本 |
| 上下文极简主义 | 后续阶段上下文仅注入决策索引表（预计 ≤ 300 Token），不注入完整产物全文 |
| 主动读取替代被动注入 | Agent 如需查阅决策点对应的详细上下文/推导过程，通过 `read_wiki(path)` 或 `read_yaml(path)` 工具主动获取 |
| Git 版本管理 | Knowledge Wiki 和完整产物文件均由 Git 仓库管理，支持 diff 对比、回滚、分支 |
| 人类可读，LLM 可消费 | Wiki 页面用标准 Markdown 编写，含结构化标题、DP 表格、wikilink 链接；既是人类审计对象也是 LLM 直接消费对象 |
| 知识编译不依赖向量数据库 | 决策索引与 Wiki 页面为结构化内容，查询时按文件名/DP ID 直接读取即可，不依赖向量相似度检索；**长期记忆（LTM）的跨任务历史模板检索仍需向量数据库**（具体实现可选） |

**编译 Agent（Compilation Agent）职责**：

| 步骤 | 输入 | 输出 | 约束 |
|-----|------|------|------|
| 1. 读取阶段产物 | 已确认的 kn_stage{N}.yaml 或同等完整产物文件 | — | 必须读取已由教师确认的产物，不得对草稿编译 |
| 2. 提取决策点 | 完整产物中的所有关键决策信息 | DP 表（含 decision_point_id / category / content / confirmed_by / confirmed_at） | 每个 DP 必须来自产物中的明确信息，禁止推断 |
| 3. 生成 Wiki 页面 | 完整产物 + DP 表 | `/wiki/{scene_type}/{stage_name}.md`，包含：概述、决策点表格、关键约束、边界条件、风险点、引用 | 页面格式由 Harness Schema 约束 |
| 4. 更新决策索引 | 已有的全局决策索引表 | 合并后的全局 DP 索引（如 `decision_index.json`） | 增量更新，不覆盖已有 DP |
| 5. Git 提交 | 新增/修改的文件 | 自动提交到 Git，message 格式："compile({scene} stage {N}): {summary}" | 提交前自动运行 Schema 校验 |

**决策点（Decision Point）数据结构**：

```yaml
decision_point:
  dp_id: "DP-S1-03"           # 全局唯一：DP-{scene_abbr}-{3位序号}
  scene_type: "course_planning"
  stage: "stage1_objectives"
  category: "teaching_method"   # objective / method / structure / node / edge / evaluation / constraint
  content: "教学方法采用讲授法 + 探究法 + 项目引领"
  source_reference: "kn_stage1.yaml: teaching_methods[1].name"  # 源文件中的位置
  confirmed_by: "teacher_001"
  confirmed_at: "2026-06-12T10:15:00Z"
  is_immutable: true          # 一经确认不可修改，仅可通过新迭代废弃
  revision: 1                 # 迭代版本，教师修改后递增
```

**决策索引（Decision Index）全局文件结构**：

```yaml
decision_index:
  task_id: "task_course_plan_2026_06_12_001"
  last_updated: "2026-06-12T10:45:00Z"
  current_stage: "stage3_completed"
  dp_count: 12
  decisions:
    - dp_id: "DP-S1-01"
      category: "objective"
      content: "总课时 = 12"
    - dp_id: "DP-S1-02"
      category: "method"
      content: "教学方法 = 讲授法 + 探究法 + 项目引领"
    # ... 更多 DP

  # 后续阶段 Agent 上下文注入时的极简摘要（自动生成）
  context_injection_summary:
    format: "bulleted_list"
    max_tokens: 300
    summary: |
      已确认决策（截至 stage3）：
      · 总课时12，面向初三学生
      · 教学方法：讲授法+探究法+项目引领
      · 课程结构：4个单元（引入/解法探究/建模/综合）
      · 知识网络含概念/技能/工具三层，共6个节点
      · 评估指标含课堂表现+书面作业+项目作品
```

**Knowledge Wiki 页面结构（Harness 约束格式）**：

```markdown
# 课程规划 · 阶段1：教学目标设计

**版本**：v1 · **编译时间**：2026-06-12T10:15:00Z · **确认人**：teacher_001

## 概述

本阶段完成「初中数学：一元二次方程」课程的教学目标设计，包括知识目标、能力目标、素质目标、预期学习成果、教学方法选择、学习效果检验方式。

## 决策点（DP）汇总

| DP ID | 类别 | 内容 |
|-------|------|------|
| DP-S1-01 | objective | 总课时 = 12 |
| DP-S1-02 | method | 教学方法 = 讲授法 + 探究法 + 项目引领 |
| DP-S1-03 | assessment | 检验方式 = 课堂小测 + 书面作业 + 项目作品 |
| ... | ... | ... |

## 关键约束

- 目标学生层次：初三
- 课程需体现分层教学理念（不同层次节点设计）
- 思政融合在备课阶段处理，本阶段不涉及具体思政内容

## 风险与边界

见完整产物 [kn_stage1.yaml](/data/kn_stage1.yaml) 中的风险评估部分。

## 相关页面

- [[课程规划-阶段2-课程结构]]
- [[课程规划-阶段3-知识网络]]
- [[备课辅助-单元教案]]
```

**编译 Agent 的 Harness 约束**：

| 约束项 | 要求 |
|-------|------|
| 输入验证 | 必须检查输入文件是否包含 `teacher_confirmed: true` 标记；否则拒绝编译并提示 |
| DP 提取完整性 | 产物中每一类"已确认"的信息至少提取为 1 个 DP；无遗漏 |
| DP 内容不可推断 | DP content 必须与源文件中的字段值逐字对应，禁止 LLM 推断/改写/润色 |
| Schema 校验 | Wiki 页面输出后，自动按 `wiki_page_schema.json` 执行结构化校验 |
| Git 提交规范 | 提交 message 必须包含场景、阶段、DP 数量信息 |
| DP ID 命名规范 | `DP-{scene_abbr}-{NNN}`，scene_abbr 如 S1=课程规划, S2=备课辅助等 |

**后续阶段/场景使用决策索引的方式**：

1. **Agent 启动上下文注入**：编排层自动读取当前任务的 `decision_index.json`，将 `context_injection_summary` 注入所有 Agent 的系统提示词中（≈ 300 Token）
2. **一致性检查**：Agent 在生成新方案前，必须核对方案中的字段与 DP 表中已有决策是否一致；检测到冲突时立即标记并请求教师确认
3. **主动读取详细信息**：如 Agent 需要了解某个 DP 的详细背景/推导过程，调用 `read_wiki("/wiki/course_planning/stage1.md")` 或 `read_yaml("/data/kn_stage1.yaml")` 工具获取
4. **新决策编译**：当前阶段的产物经教师确认后，触发编译 Agent 生成新的 DP 条目和 Wiki 页面，更新决策索引

**上下文窗口保障机制**：

| 机制 | 作用 | 控制目标 |
|-----|------|---------|
| 决策索引摘要 | 替代将完整产物拼入上下文 | ≤ 300 Token（与阶段数无关） |
| WM 中间产物 | 完整产物仅存在于 VFS 工作记忆中 | 单文件 ≤ 4096 Token，按需分片 |
| LTM 长期记忆 | 跨任务/跨课程复用的模板与偏好 | 单次检索注入 ≤ 1500 Token |
| LLM 调用前 Token 检查 | 发起 LLM 调用前必算 Token 量，超限不发起 | 单 Agent 输入 ≤ 窗口 50% |

**与现有三层记忆体系的关系**：

决策索引系统是**工作记忆（WM）与长期记忆（LTM）之间的桥梁**：

```
┌────────────────────────────────────────────────────────┐
│ 决策索引（Decision Index）                             │
│                                                      │
│   ┌─────────┐      ┌──────────────┐      ┌──────────┐ │
│   │ STM 会话 │ ───▶ │ WM: Wiki文件 │ ───▶ │ LTM:  │ │
│   │ 内存中  │      │ 产物+决策索引  │      │  向量检索 │ │
│   └─────────┘      └──────────────┘      └──────────┘ │
│                                                      │
│  · 决策索引在 WM 中持久化                              │
│  · 跨任务时决策索引可被提取并写入 LTM 供长期复用         │
│  · 新任务启动时，优先从 LTM 检索同主题决策索引摘要       │
└────────────────────────────────────────────────────────┘
```

### 4.9 FR-06：节点推荐引擎（动态学习路径）

**功能描述**：学生在某节点标记掌握后，基于知识网络边关系+学生表现+目标层次，自动计算推荐下一节点。

| 需求项 | 说明 |
|--------|------|
| 推荐算法 | 基于网络可达性+节点难度梯度+学生历史表现加权评分 |
| 候选数量 | 每次推荐 2-4 个候选节点供学生选择 |
| 推荐理由 | 每个候选节点需附结构化推荐理由 |
| 教师审核模式 | 教师可开启审核模式，推荐结果经教师确认后生效 |
| 目标层次匹配 | 推荐应考虑学生的整体目标层次（如对中职生优先推荐工具层节点） |
| 难度跳跃限制 | 相邻推荐节点的难度差不超过 1（1-5 难度） |
| 会话间记忆 | 节点推荐引擎需结合长期记忆，避免重复推荐已掌握节点 |

### 4.10 FR-07：节点内错题闭环

**功能描述**：学生答错时，自动启动诊断→补充讲解→同类题→再评估的微观循环，直至掌握或达重试上限。

| 需求项 | 说明 |
|--------|------|
| 错误诊断 | 自动判断错误类型：概念误解/计算错误/审题偏差/前置知识缺失 |
| 补充讲解 | 基于诊断结果生成针对性讲解内容或资源引用 |
| 同类题生成 | 生成同考点但不同情境/数值的新题目，避免记答案 |
| 掌握判定 | 连续 2 次答对 或 累计正确率 ≥ 80% 时标记为"节点内已掌握" |
| 重试上限 | 默认 3 次，可配置；达到上限标记为"需要教师关注" |
| 错题记录 | 所有错题及其闭环过程结构化记录，用于学情分析 |
| 跨节点前置诊断 | 诊断为"前置知识缺失"时，自动推荐返回前序节点复习 |

### 4.11 FR-08：作业批改与评分

**功能描述**：学生完成随堂测试/课后作业/结课考核后，系统自动批改、评分、生成逐题点评。

| 需求项 | 说明 |
|--------|------|
| 评阅类型 | 随堂测试/课后作业/结课考核三种评阅策略 |
| 评分标准 | 教师可预设评分 rubric，Agent 据此逐题打分 |
| 逐题点评 | 每题需附结构化点评：正确答案/学生答案对比/错误原因/改进建议 |
| 评分一致性 | 同类题目评分一致性偏差应 ≤ 5%（依据：基于 rubric 的结构化评分，LLM 对标准化评分任务通常可达到较高一致性；需通过 A/B 测试验证） |
| 节点掌握关联 | 作业表现应自动更新相关节点的掌握状态 |
| 教师复核 | 教师可查看自动评分、调整分数、添加批注 |
| 异常检测 | 全班平均分异常（<40% 或 >95%）自动告警 |

### 4.12 FR-09：学情分析

**功能描述**：基于各节点学习数据，生成学生个人学习画像与班级学习热力图、薄弱环节分析。

| 需求项 | 说明 |
|--------|------|
| 学生画像 | 每个学生：已掌握节点列表/薄弱节点列表/学习速率/活跃状态/目标层次 |
| 班级热力图 | 在知识网络上叠加全班平均掌握率，形成可视化热力图 |
| 学生分层 | 自动将学生分层：advanced / on_track / needs_support |
| 薄弱节点识别 | 自动识别全班普遍困难（<60% 掌握率）的节点，高亮标记 |
| 学习建议生成 | 针对每个薄弱节点自动生成教学建议（需增加讲解/需增加练习/需重新设计） |
| 定期自动更新 | 默认每周自动生成最新学情报告；教师可手动触发重新分析 |
| 与虚拟教室联动 | 学情分析结果自动影响后续节点推荐和虚拟教室设计 |

### 4.13 FR-10：教学评估（课程/单元末）

**功能描述**：使用课程规划阶段设计的评估指标，对教师教学过程进行系统评估，生成反思报告。

| 需求项 | 说明 |
|--------|------|
| 指标来源 | 评估指标从 SCENE-001 课程规划输出中自动提取 |
| 数据收集 | 自动从虚拟教室/作业批改/知识网络维护等场景收集数据 |
| 评估维度 | 指标达成度/学生表现/教学方法有效性/资源利用率 |
| 反思引导 | 自动生成引导性问题，供教师填写反思 |
| 改进建议 | 基于评估结果生成具体改进建议（如"某节点应拆分为2节点"） |
| 教师确认 | 教师可修改/补充/确认评估报告 |
| 纵向对比 | 支持与前一学期/前一单元/同类班级对比 |

### 4.14 FR-11：知识网络动态维护

**功能描述**：后台定期运行的 meta-scenario，基于学生学习数据分析并优化知识网络结构。

| 需求项 | 说明 |
|--------|------|
| 触发方式 | 每月定时自动运行 + 教师手动触发 |
| 节点性能分析 | 每个节点的实际掌握率/平均学习耗时/平均错题闭环次数 |
| 边关系分析 | 节点间迁移困难度、是否存在衔接断层 |
| 优化建议类型 | split_node（拆分）/ merge_node（合并）/ add_transition_node（新增过渡节点）/ increase_difficulty（提升难度）/ decrease_difficulty（降低难度） |
| 建议证据 | 每个建议必须附数据证据和预期效果 |
| 教师决策 | 系统只生成建议，所有网络结构变更需教师确认 |
| 版本历史 | 网络结构变更记录为版本历史，可追溯和回滚 |
| 网络规模控制 | 优化后的节点总数应在合理范围（默认 ±20%） |

### 4.15 FR-12：配置持久化与管理

**功能描述**：教学配置、知识网络、评估指标等可保存至本地文件系统，支持加载、列举、版本控制。

| 需求项 | 说明 |
|--------|------|
| 保存格式 | YAML / JSON |
| 目录结构 | 区分 knowledge_networks / teaching_packages / evaluation_metrics / feedback_entries / runtime_logs |
| 配置生命周期 | 草稿 → 预览 → 保存 / 执行 |
| 模板导出 | 支持将已保存配置导出为可复用模板 |
| 版本控制 | 每个配置带版本号，支持 diff 查看变更 |
| 多课程隔离 | 不同课程的配置完全隔离 |

### 4.16 FR-13：人机协同接口

**功能描述**：在关键节点引入人类教师的确认、反馈与干预。

| 需求项 | 说明 |
|--------|------|
| 人工审批 | Agent 发起的关键决策需教师确认（如知识网络结构变更） |
| 反馈收集 | 支持对 Agent 输出进行评分与批注 |
| 实时打断 | 运行过程中教师可中断指定 Agent |
| 动态调整 | 运行时可调整 Agent 数量、角色、策略 |
| 审核模式开关 | 教师可在节点粒度上开启/关闭审核模式 |
| 结构化反馈 | 教师反馈必须结构化记录，用于 Harness 持续优化 |

### 4.17 FR-14：可观测性与审计

**功能描述**：Agent 执行过程可追踪、可回放、可审计。

| 需求项 | 说明 |
|--------|------|
| 日志记录 | 记录每个 Agent 的输入、输出、决策依据 |
| 运行状态 | 可视化展示当前任务进度与 Agent 状态 |
| 审计回放 | 支持按时间轴回放完整执行过程 |
| Harness 统计 | 记录每次校验通过率、失败原因分布 |
| Token 统计 | 记录每次会话 Token 消耗量，与预算对比 |
| 节点掌握历史 | 每个学生在各节点的学习过程完整可追溯 |

### 4.18 FR-16：思政融合设计与审核

**功能描述**：在备课辅助阶段，系统自动为每个节点生成思政元素融合建议，教师确认后落到教案与学案。

| 需求项 | 说明 |
|--------|------|
| 建议生成 | Agent 为每个节点生成结构化建议：目标节点/思政元素/融入方式/预计时长/活动设计 |
| 教师确认 | 教师可 approve/reject/revise 每条建议；系统记录每次决策 |
| 内容审核 | 思政内容须经额外 Harness 检查：不允许包含敏感/不适当内容 |
| 融入痕迹 | 教案/学案中标注"本节包含思政设计"，保留可追溯性 |
| 模板沉淀 | 优秀思政设计可沉淀为模板，后续同类课程复用 |
| 严禁自动输出 | Agent 只能"建议"，最终内容必须经教师手动确认后写入教案 |

### 4.19 FR-17：可视化配置界面（可选）

**功能描述**：通过 Web 界面（React/Vue）提供图形化配置能力，降低技术门槛。

| 需求项 | 说明 |
|--------|------|
| 场景选择 | 图形化选择教学场景 |
| Agent 拖拽编排 | 通过拖拽方式调整 Agent 组合与关系 |
| 实时预览 | 配置修改后可即时预览效果 |
| REST API 暴露 | 后端通过 FastAPI 暴露接口供前端调用 |

### 4.20 FR 间依赖关系矩阵

下表列出各 FR 之间的依赖关系，供开发团队确定实现顺序与迭代计划。

| 功能需求 | 直接依赖 | 被依赖方 | 说明 |
|---------|---------|---------|------|
| FR-01 场景识别 | 无 | FR-02 | 识别场景后触发配置生成 |
| FR-02 Agent 配置生成 | FR-01 | FR-03 | 配置需传入编排层执行 |
| FR-03 Agent 编排与调度 | FR-02 | FR-05 ~ FR-11, FR-15 | 编排层为所有场景 Agent 提供运行时环境 |
| FR-04 框架协议转换 | FR-02, FR-03 | — | 跨框架通信需先有 Agent 定义与编排 |
| FR-05 立体分层知识网络 | FR-03 | FR-06, FR-07, FR-08, FR-09, FR-10, FR-11 | 知识网络是节点层所有功能的基础数据结构 |
| FR-06 节点推荐引擎 | FR-05, FR-07 | FR-08, FR-09 | 推荐需节点结构 + 学习状态数据 |
| FR-07 节点内错题闭环 | FR-05 | FR-06, FR-08, FR-09 | 错题闭环产生的学习状态数据供推荐/学情/评估使用 |
| FR-08 作业批改与评分 | FR-05, FR-07 | FR-09, FR-10 | 批改结果影响节点掌握状态，供学情与评估使用 |
| FR-09 学情分析 | FR-05, FR-07, FR-08 | FR-10, FR-11 | 学情数据供教学评估与网络维护参考 |
| FR-10 教学评估 | FR-05, FR-09 | — | 评估报告为终端输出 |
| FR-11 知识网络动态维护 | FR-05, FR-09, FR-10 | FR-06, FR-07, FR-08 | 维护结果更新知识网络结构，反哺节点层功能 |
| FR-12 配置持久化与管理 | FR-02 | FR-13, FR-14 | 持久化配置供人机协同与可观测性使用 |
| FR-13 人机协同接口 | FR-03, FR-12 | FR-11, FR-16 | 教师确认/反馈需在运行时环境内完成 |
| FR-14 可观测性与审计 | FR-03, FR-12 | — | 日志与审计为横切关注点，依赖运行时与配置 |
| FR-15 Harness 约束层 | FR-02, FR-03 | FR-01 ~ FR-14 全部 | 所有 Agent 输出与工具调用均需经 Harness 校验 |
| FR-16 思政融合设计与审核 | FR-05, FR-13 | — | 需知识网络节点结构 + 教师确认能力 |
| FR-17 可视化配置界面 | FR-02, FR-12 | — | 可选功能，需配置生成与持久化能力 |
| FR-18 知识编译与决策索引 | FR-03, FR-05 | FR-06 ~ FR-14 | 多阶段 Agent 协作需编译决策索引来减少上下文膨胀 |

**推荐实现顺序（按依赖分层）**：

```
第 1 层（P0 基础架构）：FR-02(配置生成) → FR-03(编排) → FR-04(协议转换) → FR-15(Harness)
第 2 层（P0 核心数据）：FR-05(知识网络) → FR-18(知识编译)
第 3 层（P0 核心路径）：FR-07(错题闭环) → FR-06(节点推荐)
第 4 层（P1 扩展功能）：FR-08(批改) → FR-09(学情) → FR-10(评估) → FR-11(维护)
第 5 层（P1 横切关注点）：FR-12(持久化) → FR-13(协同) → FR-14(观测) → FR-16(思政)
第 6 层（P2 可选增强）：FR-17(可视化界面) → FR-01(场景识别，可延后至有足够样本时实现)
```

---


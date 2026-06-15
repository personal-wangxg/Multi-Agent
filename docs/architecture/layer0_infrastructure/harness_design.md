# Harness 约束层详细设计

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-15（Harness约束层）

---

## 1. 设计目标

Harness 约束层的核心目标是将 Agent 的行为与输出**严格约束在需求范围内**，防止自由发散或偏离教学目标。

| 设计原则 | 说明 |
|---------|------|
| **不可绕过性** | Harness 约束在 Agent 实例生命周期内持续生效，不可被 Agent 内部推理覆盖 |
| **可配置性** | 约束策略（校验规则、过滤词表、权限配置）支持通过配置文件插拔 |
| **可观测性** | 所有校验结果、失败原因、重试次数均需记录，支持审计与优化 |
| **渐进式约束** | 支持按场景/Agent类型定制约束强度 |

---

## 2. 架构组件

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Harness 约束层架构                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│   │ 提示词模板   │    │ 输出Schema   │    │ 工具白名单   │    │
│   │   引擎       │    │    校验器    │    │    管理器    │    │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    │
│          │                   │                   │             │
│          ▼                   ▼                   ▼             │
│   ┌──────────────────────────────────────────────────────┐    │
│   │              Harness 执行引擎                        │    │
│   │   ┌─────────────────────────────────────────────┐    │    │
│   │   │ 校验管道：Schema → 内容边界 → 任务完整性     │    │    │
│   │   └─────────────────────────────────────────────┘    │    │
│   └───────────────────┬──────────────────────────────────┘    │
│                       │                                        │
│          ┌────────────┼────────────┐                           │
│          ▼            ▼            ▼                           │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                    │
│   │ 反馈闭环 │  │  记忆更新 │  │  审计日志 │                    │
│   │   模块   │  │    模块   │  │    模块   │                    │
│   └──────────┘  └──────────┘  └──────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 组件职责

| 组件 | 职责 | 核心功能 |
|-----|------|---------|
| **提示词模板引擎** | 管理场景级提示词模板 | 模板加载、动态变量注入、模板版本管理 |
| **输出 Schema 校验器** | 校验 Agent 输出结构 | JSON/YAML解析、必填字段检查、类型/范围校验 |
| **工具白名单管理器** | 管理 Agent 工具权限 | 权限校验、参数约束、沙箱配置 |
| **Harness 执行引擎** | 协调各组件执行 | 三阶段校验管道、重试逻辑、人工干预触发 |
| **反馈闭环模块** | 处理教师反馈 | 反馈结构化、模板迭代、重生成触发 |
| **记忆更新模块** | 更新长期记忆 | DP提取、Wiki生成、决策索引更新 |
| **审计日志模块** | 记录执行过程 | Token统计、校验结果、失败原因追踪 |

---

## 3. 提示词模板引擎设计

### 3.1 模板结构

每个场景对应一个模板文件（YAML格式），包含 6 个固定区块：

```yaml
template_id: "tpl_scene001_planner_v1.0"
scene_type: "SCENE-001"
agent_role: "课程规划 Agent"
version: "1.0"
last_updated: "2026-06-01"

# 区块1：角色定义（锁定）
role_definition:
  role: "资深课程设计专家"
  specialty: "将课程目标分解为可执行的教学单元"
  tone: "专业、严谨、结构清晰"

# 区块2：任务边界（锁定）
task_scope:
  must_do:
    - "根据 {course_name} 和 {course_desc} 生成课程大纲"
    - "确保章节数量与 {total_periods} 匹配（允许 ±1 调整）"
  must_not_do:
    - "不得生成超出 {course_desc} 范围的知识点"
    - "不得修改教师指定的 {total_periods}"

# 区块3：输出格式规范（锁定）
output_format:
  format: "YAML"
  schema_ref: "schema_scene001_outline_v1.0"
  max_output_tokens: 4096

# 区块4：禁止话题列表（锁定）
prohibited_topics:
  - "超出 {course_desc} 范围的内容"
  - "广告、推销内容"
  - "政治、宗教、色情、暴力内容"

# 区块5：待办清单模板（write_todos驱动）
todo_template:
  - id: 1
    label: "分析课程目标"
    description: "提取课程级别目标"
    required: true
  - id: 2
    label: "拆解章节结构"
    description: "根据目标数量拆分章节"
    required: true

# 区块6：注入信息（动态）
dynamic_injection:
  system_variables:
    - course_name: "{{course_name}}"
    - course_desc: "{{course_desc}}"
  retrieved_memories: "{{retrieved_from_ltm}}"
```

### 3.2 模板引擎核心接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `load_template(scene_type)` | 加载场景模板 | scene_type: str | Template 对象 |
| `inject_variables(template, variables)` | 注入动态变量 | template: Template, variables: dict | 注入后的模板字符串 |
| `validate_template(template)` | 校验模板格式 | template: Template | 校验结果 |
| `get_template_version(template_id)` | 获取模板版本 | template_id: str | version: str |

### 3.3 模板版本管理

```
template_repository/
├── tpl_scene001_planner/
│   ├── v1.0.yaml
│   ├── v1.1.yaml
│   └── latest -> v1.1.yaml
├── tpl_scene002_prep/
│   └── v1.0.yaml
└── template_index.json
```

---

## 4. Schema 校验器设计

### 4.1 三阶段校验管道

```
Agent 输出
   │
   ▼
[阶段1：Schema校验]
   ├── JSON/YAML parse 检查
   ├── 必填字段检查（required fields）
   ├── 类型检查（string/integer/array/boolean）
   ├── 数值范围检查（minimum/maximum/length）
   └── 枚举值检查（enum）
         │
         ├─ PASS → [阶段2]
         └─ FAIL → 重试（≤3次）→ 人工干预

[阶段2：内容边界过滤]
   ├── 禁止话题检查（prohibited_topics命中检测）
   ├── 关键词过滤（自定义词表）
   ├── 长度上限检查（max_output_tokens）
   └── 主题相关性检查（语义相似度）
         │
         ├─ PASS → [阶段3]
         └─ FAIL → 触发重生成

[阶段3：任务完整性检查]
   ├── 待办清单覆盖率（items_covered/total_items >= 100%）
   ├── 数据一致性检查（如课时数匹配）
   └── 无新增禁止任务检查
         │
         ├─ PASS → 交付给用户/下游Agent
         └─ FAIL → 触发针对性补充或重生成
```

### 4.2 校验器核心接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `validate_schema(output, schema)` | Schema 结构校验 | output: dict, schema: dict | ValidationResult |
| `filter_content(output, prohibited_topics)` | 内容边界过滤 | output: str, prohibited_topics: list | FilterResult |
| `check_task_completeness(output, todo_items)` | 任务完整性检查 | output: dict, todo_items: list | CompletenessResult |
| `run_validation_pipeline(output, harness_config)` | 执行完整校验管道 | output: dict, config: HarnessConfig | PipelineResult |

### 4.3 校验结果数据结构

```yaml
validation_result:
  success: true/false
  stage: "schema/content/completeness"
  errors:
    - field: "outline.chapters[1].periods"
      error_type: "range_violation"
      message: "值 3 超出范围 [5, 20]"
      expected: 5-20
      actual: 3
  warnings: []
  retry_count: 0
  max_retries: 3
```

---

## 5. 工具白名单管理器设计

### 5.1 白名单配置结构

```yaml
agent_id: "agent_scene001_researcher_001"
scene_type: "SCENE-001"
framework: "DeepAgents"

tool_whitelist:
  allowed_tools:
    - name: "read_file"
      params:
        path:
          type: "string"
          pattern: "^/sessions/.*\\.md$"
        max_chars:
          type: "integer"
          default: 8192
      max_calls_per_session: 50
      description: "读取VFS中的文档"

    - name: "write_file"
      params:
        path:
          type: "string"
          pattern: "^/sessions/.*\\.md$"
        content:
          type: "string"
          max_length: 10240
      max_calls_per_session: 20
      description: "写入中间产物"

  denied_tools:
    - name: "exec_shell"
      reason: "不允许执行系统命令"
    - name: "send_external_request"
      reason: "不允许访问外部API"

  param_constraints:
    write_file:
      content:
        prohibited_keywords: ["password", "api_key", "secret"]

sandbox_config:
  enabled: true
  provider: "modal"
  timeout_seconds: 30
  allowed_fqdns: ["api.eduagents.local"]
```

### 5.2 权限校验流程

```
Agent 发起工具调用
       │
       ▼
[检查工具是否在白名单中]
       │
       ├─ 否 → 拒绝调用，记录审计日志
       │
       ▼ 是
[检查工具是否在黑名单中]
       │
       ├─ 是 → 拒绝调用，记录审计日志
       │
       ▼ 否
[校验参数合法性]
       │
       ├─ 失败 → 拒绝调用，记录审计日志
       │
       ▼ 通过
[检查调用次数限制]
       │
       ├─ 超限 → 拒绝调用，记录审计日志
       │
       ▼ 未超限
[检查沙箱配置（如需要）]
       │
       ▼
[允许调用，记录审计日志]
```

---

## 6. 反馈闭环模块设计

### 6.1 反馈数据结构

```yaml
feedback_entry:
  feedback_id: "fb_001"
  session_id: "sess_001"
  agent_id: "agent_scene001_planner_001"
  timestamp: "2026-06-12T10:05:00Z"

  rating: 0.6                            # 教师评分（0.0~1.0）
  action: "reject"                        # approve / reject / revise
  reason: "第2章课时分配错误"

  annotations:
    - field: "outline.chapters[1].periods"
      expected_value: 5
      actual_value: 3
      comment: "这章内容很多，至少需要5课时"

  auto_actions:
    - action: "inject_correction"
      target_field: "outline.chapters[1].periods"
      value: 5
      trigger_retry: true
    - action: "update_template"
      template_id: "tpl_scene001_planner_v1.0"
      note: "课时判断逻辑需加强"
      new_version: "v1.1"

  ltm_update:
    memory_id: "mem_session001_conclusion"
    update_fields:
      rating: 0.6
      teacher_feedback: "课时分配需更细致"
```

### 6.2 反馈处理流程

```
教师提交反馈
       │
       ▼
[解析反馈内容]
       │
       ▼
[根据action执行对应操作]
       │
       ├─ approve → 更新记忆，标记完成
       │
       ├─ reject → 触发重生成，注入修正
       │
       └─ revise → 应用教师修改，更新模板
       │
       ▼
[更新长期记忆]
       │
       ▼
[更新模板版本（如需要）]
       │
       ▼
[记录审计日志]
```

---

## 7. 集成与部署

### 7.1 技术栈选择

| 组件 | 推荐技术 | 理由 |
|-----|---------|------|
| 模板管理 | YAML + Jinja2 | 结构化配置 + 动态变量支持 |
| Schema校验 | jsonschema (Python) | 标准JSON Schema支持 |
| 权限管理 | 自定义RBAC | 场景级细粒度权限控制 |
| 持久化 | SQLite（开发）/ PostgreSQL（生产） | 轻量启动 + 生产级扩展 |
| 日志 | Structlog + ELK | 结构化日志 + 可观测性 |

### 7.2 目录结构

```
eduagents/
├── harness/
│   ├── __init__.py
│   ├── template_engine.py      # 提示词模板引擎
│   ├── schema_validator.py     # Schema校验器
│   ├── tool_whitelist.py       # 工具白名单管理器
│   ├── execution_engine.py     # Harness执行引擎
│   ├── feedback_loop.py        # 反馈闭环模块
│   ├── memory_updater.py       # 记忆更新模块
│   └── audit_logger.py         # 审计日志模块
├── templates/                  # 场景模板目录
│   ├── tpl_scene001.yaml
│   ├── tpl_scene002.yaml
│   └── ...
├── schemas/                    # 输出Schema目录
│   ├── schema_scene001.json
│   ├── schema_scene002.json
│   └── ...
└── config/
    └── harness_config.yaml
```

### 7.3 与其他模块的接口

| 调用方 | 接口 | 说明 |
|-------|------|------|
| 编排层 | `harness.load_and_inject(scene_type, variables)` | 加载模板并注入变量 |
| Agent | `harness.validate_output(output, scene_type)` | 校验Agent输出 |
| 编排层 | `harness.check_tool_permission(agent_id, tool_name, params)` | 检查工具调用权限 |
| 人机协同层 | `harness.process_feedback(feedback)` | 处理教师反馈 |

---

## 8. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| 模板锁定机制 | 前5个区块锁定，第6个动态注入 | 保证约束的不可绕过性，同时支持动态上下文 |
| 重试策略 | 最多3次重试 | 平衡Agent自主性与人工干预成本 |
| 权限粒度 | 场景级 + Agent级 | 灵活控制不同场景的工具访问权限 |
| 沙箱配置 | 可选启用 | 根据场景需求决定是否启用沙箱隔离 |
| 反馈闭环 | 结构化记录 + 自动迭代 | 支持Harness持续优化，减少人工维护成本 |
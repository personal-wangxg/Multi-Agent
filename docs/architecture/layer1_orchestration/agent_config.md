# Agent 配置动态生成设计

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-02（Agent配置动态生成）

---

## 1. 设计目标

FR-02 Agent 配置动态生成的核心目标是根据教学场景需求，动态生成并管理 Agent 的完整配置，确保每个 Agent 绑定正确的 Harness 约束、Schema 校验规则和工具白名单。

| 设计原则 | 说明 |
|---------|------|
| **动态性** | 根据场景类型、任务阶段动态生成 Agent 配置 |
| **约束绑定** | 每个 Agent 必须绑定 Harness 模板 + Schema + 工具白名单 |
| **可覆盖性** | 教师可覆盖默认配置，优先级：教师覆盖 > 场景配置 > 默认值 |
| **可追溯性** | 配置变更历史完整记录，支持版本回滚 |

---

## 2. 架构组件

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent 配置动态生成架构                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  场景配置    │    │  角色模板    │    │  教师覆盖    │      │
│  │   仓库       │    │   仓库       │    │    接口      │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              配置合并引擎                                 │    │
│  │   ┌─────────────────────────────────────────────────┐   │    │
│  │   │  合并策略：默认 → 场景 → 角色模板 → 教师覆盖      │   │    │
│  │   └─────────────────────────────────────────────────┘   │    │
│  └───────────────────────────┬─────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              配置验证器                                   │    │
│  │   ┌─────────────────────────────────────────────────┐   │    │
│  │   │  Schema校验 / 约束冲突检测 / 工具权限验证         │   │    │
│  │   └─────────────────────────────────────────────────┘   │    │
│  └───────────────────────────┬─────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  配置序列化  │    │  配置版本    │    │  配置下发    │      │
│  │   器         │    │   管理器     │    │    器        │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 组件职责

| 组件 | 职责 | 核心功能 |
|-----|------|---------|
| **场景配置仓库** | 存储各场景的默认配置模板 | 配置加载、场景匹配、默认值提供 |
| **角色模板仓库** | 存储 Agent 角色定义模板 | 角色模板加载、模板组合 |
| **教师覆盖接口** | 接收教师配置覆盖 | 覆盖字段解析、优先级判定 |
| **配置合并引擎** | 执行多源配置合并 | 深度合并、冲突检测、覆盖逻辑 |
| **配置验证器** | 校验最终配置合法性 | Schema 校验、约束冲突检测 |
| **配置版本管理器** | 管理配置历史版本 | 版本记录、回滚支持 |
| **配置下发器** | 将配置传递给 Agent 工厂 | 序列化、格式转换、下发执行 |

---

## 3. Agent 配置结构

### 3.1 完整配置模型

```yaml
agent_config:
  # ========== 基础标识 ==========
  agent_id: "agent_scene001_planner_001"
  name: "课程规划 Agent"
  scene_type: "SCENE-001"              # 场景类型
  version: "1.0.0"                     # 配置版本

  # ========== 角色定义 ==========
  role:
    type: "teacher"                    # teacher / student / assistant / evaluator
    specialty: "课程规划专家"
    collaboration_mode: "master_slave"  # pipeline / peer / master_slave

  # ========== 框架绑定 ==========
  framework:
    name: "DeepAgents"                 # DeepAgents / AgentScope / generic
    adapter_version: "1.0"
    runtime_config:
      max_concurrent_actions: 3
      timeout_seconds: 300

  # ========== Harness 约束绑定 ==========
  harness:
    template_id: "tpl_scene001_planner_v1.0"
    schema_id: "schema_scene001_outline_v1.0"
    tool_whitelist_id: "wl_scene001"
    constraint_level: "strict"         # strict / moderate / lenient

  # ========== 模型配置 ==========
  model:
    provider: "openai"
    name: "gpt-4o"
    parameters:
      temperature: 0.7
      max_tokens: 4096
      top_p: 0.9
    context_window: 128000

  # ========== 工具列表 ==========
  tools:
    - name: "read_file"
      enabled: true
      params:
        max_chars: 8192
      description: "读取VFS中的文档"

    - name: "write_file"
      enabled: true
      params:
        max_length: 10240
      description: "写入中间产物"

    - name: "search_knowledge"
      enabled: true
      params:
        top_k: 5
        threshold: 0.7
      description: "搜索知识网络"

  # ========== 协作关系 ==========
  collaboration:
    mode: "master_slave"
    peers: []                          # peer 模式下使用
    master_id: null                   # master_slave 模式下使用
    slaves: ["agent_scene001_researcher_001"]

    routing:
      send_to:
        - "agent_scene001_researcher_001"
      receive_from:
        - "agent_scene001_researcher_001"
        - "human_teacher"

  # ========== 上下文注入 ==========
  context_injection:
    include_knowledge: true
    include_decision_index: true
    include_teacher_override: true
    max_context_tokens: 64000         # 窗口50%限制

  # ========== 状态管理 ==========
  state:
    persistence: "session"             # session / permanent
    checkpoint_enabled: true
    checkpoint_interval: 60
```

### 3.2 配置字段说明

| 字段路径 | 类型 | 必填 | 说明 |
|---------|------|------|------|
| `agent_id` | string | 是 | 全局唯一标识，格式：`agent_{scene}_{role}_{seq}` |
| `role.type` | enum | 是 | teacher/student/assistant/evaluator |
| `role.collaboration_mode` | enum | 是 | pipeline/peer/master_slave |
| `framework.name` | enum | 是 | DeepAgents/AgentScope/generic |
| `harness.*` | object | 是 | 三个约束必须全部绑定 |
| `model.context_window` | integer | 是 | 用于计算上下文限制 |
| `tools` | array | 是 | 至少包含一个工具 |
| `context_injection.max_context_tokens` | integer | 是 | 不得超过窗口50% |

---

## 4. 协作模式详解

### 4.1 三种协作模式

| 模式 | 结构 | 消息流向 | 适用场景 |
|-----|------|---------|---------|
| **pipeline** | A → B → C → D | 单向顺序传递 | 备课流程：规划 → 教案 → 学案 → 习题 |
| **peer** | A ↔ B ↔ C | 平等双向交换 | 虚拟教室：教师 ↔ 学生 ↔ 助教 |
| **master_slave** | M → S1, S2, S3 | 主控单向下发 | 课程规划：主规划 → 研究助理/资料助理 |

### 4.2 Pipeline 模式

```
┌─────────────────────────────────────────────────────────────┐
│                    Pipeline 协作模式                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐    msg    ┌─────────┐    msg    ┌─────────┐  │
│  │ Planner │ ────────▶ │ Builder │ ────────▶ │  Writer │  │
│  └─────────┘           └─────────┘           └─────────┘  │
│       │                     │                     │        │
│       ▼                     ▼                     ▼        │
│  [输出大纲]            [输出教案]              [输出学案]   │
│                                                             │
│  特征：单向顺序，每个Agent专注单一任务，上游输出是下游输入   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Peer 模式

```
┌─────────────────────────────────────────────────────────────┐
│                      Peer 协作模式                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│       ┌─────────┐                                           │
│       │Teacher  │◀──────────────────────────┐               │
│       └────┬────┘                           │               │
│            │ msg                             │ msg          │
│       ┌────┴────┐                     ┌─────┴────┐         │
│       │ Student │◀────────────────────▶│  Tutor   │         │
│       └────┬────┘                     └─────┬────┘         │
│            │ msg                             │ msg          │
│            └────────────────────────────────┘              │
│                                                             │
│  特征：平等协作，消息广播/订阅，支持多轮对话                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.4 Master-Slave 模式

```
┌─────────────────────────────────────────────────────────────┐
│                   Master-Slave 协作模式                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│       ┌─────────────────┐                                   │
│       │   Master Agent  │                                   │
│       │ (课程规划主控)   │                                   │
│       └────────┬────────┘                                   │
│                │ msg (任务下发)                              │
│       ┌────────┼────────┐                                   │
│       ▼        ▼        ▼                                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                       │
│  │ Slave 1 │ │ Slave 2 │ │ Slave 3 │                       │
│  │研究助理 │ │资料助理 │ │格式助理 │                       │
│  └────┬────┘ └────┬────┘ └────┬────┘                       │
│       │ msg (结果汇报)         │                             │
│       └────────┴────────────────┘                            │
│                                                             │
│  特征：主控统一协调，从Agent执行子任务，结果汇总到主控       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. 消息路由规则

### 5.1 路由配置结构

```yaml
routing_rules:
  # 点对点路由
  direct_routes:
    - from: "agent_planner_001"
      to: "agent_researcher_001"
      priority: 1
      transform: "deepagents_to_unified"

  # 主题订阅路由
  topic_routes:
    - topic: "scene001/knowledge_result"
      subscribers:
        - "agent_planner_001"
        - "agent_builder_001"
      transform: "unified_to_deepagents"

  # 广播路由
  broadcast_routes:
    - from: "human_teacher"
      scope: "scene001"
      exclude: []
```

### 5.2 路由决策流程

```
Agent 发送消息
       │
       ▼
[解析接收方列表]
       │
       ├── 点对点 → 直接路由
       ├── 主题匹配 → 查找订阅者
       └── 广播 → 查找所有相关 Agent
       │
       ▼
[应用转换规则]
       │
       ├─ 同框架 → 直接转发
       ├─ DeepAgents → UnifiedMessage → AgentScope
       └─ AgentScope → UnifiedMessage → DeepAgents
       │
       ▼
[消息投递]
       │
       ├── 成功 → 记录审计日志
       └── 失败 → 重试队列
```

---

## 6. 上下文变量注入

### 6.1 注入配置结构

```yaml
context_injection:
  # 知识网络注入
  knowledge_network:
    enabled: true
    scope: "current_chapter"
    max_nodes: 20
    include_edges: true

  # 决策索引注入
  decision_index:
    enabled: true
    max_tokens: 300           # DP-ARCH-01 限制 ≤300 Token
    scope: "relevant_dp"
    format: "compact"          # full / compact / reference

  # 教师覆盖注入
  teacher_override:
    enabled: true
    fields:
      - "harness.constraint_level"
      - "model.temperature"
    priority: "highest"

  # 记忆片段注入
  memory:
    enabled: true
    sources:
      - type: "session"
        max_tokens: 16000
      - type: "long_term"
        query_strategy: "semantic"
        max_results: 3
        max_tokens: 8000
```

### 6.2 注入流程

```
配置合并完成
       │
       ▼
[收集注入变量]
       │
       ├── 知识网络节点 → 从知识库查询
       ├── 决策索引 → 从索引库获取
       ├── 教师覆盖 → 从覆盖接口获取
       └── 记忆片段 → 从记忆系统检索
       │
       ▼
[计算总 Token 量]
       │
       ├─ 未超限 → 直接注入
       │
       ▼ 超限
[触发上下文压缩]
       │
       ├─ 决策索引优先保留（≤300 Token）
       ├─ 知识网络按相关性裁剪
       └─ 记忆片段按时间/重要性裁剪
       │
       ▼
[组装上下文]
       │
       ▼
[注入 Agent 运行环境]
```

---

## 7. 教师覆盖合并机制

### 7.1 合并优先级

| 优先级 | 来源 | 说明 |
|-------|------|------|
| 1（最高） | 教师手动覆盖 | 人工介入的即时修改 |
| 2 | 场景配置 | SCENE-XXX 特定配置 |
| 3 | 角色模板 | role_type 默认配置 |
| 4（最低） | 系统默认值 | 系统级默认参数 |

### 7.2 合并策略

```yaml
merge_strategies:
  # 深度合并（用于嵌套对象）
  deep_merge:
    - "harness"
    - "model.parameters"
    - "tools"
    - "context_injection"

  # 替换合并（用于简单值）
  replace:
    - "agent_id"
    - "version"
    - "framework.name"

  # 数组合并（追加而非覆盖）
  append:
    - "tools"
    - "collaboration.routing.send_to"
    - "collaboration.routing.receive_from"

  # 教师覆盖特殊处理
  teacher_override:
    merge_mode: "replace"      # 教师覆盖直接替换，不合并
    require_confirmation: true
    log_changes: true
```

### 7.3 覆盖合并流程

```
教师发起覆盖请求
       │
       ▼
[解析覆盖字段路径]
       │
       ├── 例：model.temperature → {"model": {"temperature": 0.5}}
       │
       ▼
[读取当前配置]
       │
       ▼
[应用合并策略]
       │
       ├─ replace → 直接替换
       ├─ deep_merge → 深度合并
       └─ append → 数组追加
       │
       ▼
[验证合并结果]
       │
       ├─ Schema 校验
       ├─ 约束冲突检测
       └─ 工具权限验证
       │
       ├─ 验证通过 → 保存新版本
       └─ 验证失败 → 拒绝覆盖，返回错误
       │
       ▼
[记录覆盖历史]
       │
       ▼
[通知相关 Agent 配置变更]
```

---

## 8. 核心接口

### 8.1 配置生成接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `generate_config(scene_type, role_type, teacher_overrides)` | 生成完整 Agent 配置 | scene_type: str, role_type: str, overrides: dict | AgentConfig |
| `merge_configs(base_config, override_config, strategy)` | 合并多个配置 | base: dict, override: dict, strategy: str | MergedConfig |
| `validate_config(config)` | 校验配置合法性 | config: AgentConfig | ValidationResult |
| `apply_teacher_override(agent_id, overrides)` | 应用教师覆盖 | agent_id: str, overrides: dict | OperationResult |

### 8.2 配置管理接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `get_config(agent_id, version)` | 获取指定版本配置 | agent_id: str, version: str | AgentConfig |
| `list_config_versions(agent_id)` | 列出配置版本历史 | agent_id: str | VersionList |
| `rollback_config(agent_id, target_version)` | 回滚到指定版本 | agent_id: str, version: str | OperationResult |
| `export_config(agent_id, format)` | 导出配置 | agent_id: str, format: str | ConfigData |

### 8.3 下发与同步接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `deploy_config(agent_id)` | 下发配置到 Agent | agent_id: str | DeploymentResult |
| `sync_config_to_peers(agent_ids)` | 同步配置到对等 Agent | agent_ids: list | SyncResult |
| `notify_config_change(agent_id, change_info)` | 通知配置变更 | agent_id: str, change: dict | NotificationResult |

---

## 9. 目录结构

```
orchestration/
├── __init__.py
├── config_generator/
│   ├── __init__.py
│   ├── scene_config_repo.py      # 场景配置仓库
│   ├── role_template_repo.py     # 角色模板仓库
│   ├── merger.py                 # 配置合并引擎
│   ├── validator.py              # 配置验证器
│   └── serializer.py            # 配置序列化器
├── config_manager/
│   ├── __init__.py
│   ├── version_manager.py        # 版本管理器
│   ├── history_logger.py         # 变更历史记录
│   └── rollback.py               # 回滚管理器
├── interfaces/
│   ├── __init__.py
│   ├── teacher_override.py       # 教师覆盖接口
│   ├── config_deployer.py        # 配置下发接口
│   └── notification.py           # 变更通知接口
└── templates/
    ├── scene_configs/            # 场景配置模板
    │   ├── scene001.yaml
    │   ├── scene002.yaml
    │   └── ...
    └── role_templates/          # 角色模板
        ├── teacher.yaml
        ├── student.yaml
        ├── assistant.yaml
        └── evaluator.yaml
```

---

## 10. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| 配置格式 | YAML/JSON 双支持 | YAML 便于人工编辑，JSON 便于程序处理 |
| 合并策略 | 四层优先级 + 字段级策略 | 兼顾灵活性与可控性 |
| 约束绑定 | 强制三绑定 | 确保 Harness 约束无处不在 |
| 教师覆盖 | 直接替换模式 | 教师意图优先，避免复杂合并导致预期外行为 |
| 版本管理 | 每次变更记录版本 | 支持审计回溯，符合教育场景合规要求 |
| 上下文注入 | 决策索引优先保留 | DP-ARCH-01 核心约束 ≤300 Token |

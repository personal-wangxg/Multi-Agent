# 框架协议转换设计

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-04（框架协议转换）

---

## 1. 设计目标

FR-04 框架协议转换的核心目标是实现 DeepAgents 与 AgentScope 两大框架之间的无缝通信，通过 UnifiedMessage 统一消息协议屏蔽底层框架差异，支持跨框架 Agent 协作。

| 设计原则 | 说明 |
|---------|------|
| **协议统一** | 所有框架通信统一使用 UnifiedMessage 格式 |
| **双向转换** | 支持 DeepAgents ↔ AgentScope 双向转换 |
| **无损转换** | 转换过程不丢失关键语义信息 |
| **可扩展性** | 支持未来新增框架（如 LangChain、AutoGen） |
| **状态同步** | 跨框架决策索引同步机制 |

---

## 2. 架构组件

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                   框架协议转换架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐         ┌──────────────┐                    │
│  │ DeepAgents   │         │  AgentScope   │                    │
│  │    Agent      │         │    Agent      │                    │
│  └──────┬───────┘         └──────┬───────┘                    │
│         │                         │                             │
│         ▼                         ▼                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              框架适配器层                                 │    │
│  │  ┌──────────────┐         ┌──────────────┐             │    │
│  │  │DeepAgents    │         │AgentScope     │             │    │
│  │  │Adapter       │         │Adapter        │             │    │
│  │  └──────┬───────┘         └──────┬───────┘             │    │
│  └─────────┼────────────────────────┼──────────────────────┘    │
│            │                         │                           │
│            └─────────┬───────────────┘                           │
│                      ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              UnifiedMessage 消息中心                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │    │
│  │  │  消息路由    │  │  协议转换    │  │  状态同步    │  │    │
│  │  │     引擎     │  │     引擎     │  │     引擎     │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                      │                                             │
│                      ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              决策索引同步层                               │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │    │
│  │  │ 索引生成器   │  │  索引对齐    │  │  冲突解决    │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 组件职责

| 组件 | 职责 | 核心功能 |
|-----|------|---------|
| **DeepAgents 适配器** | DeepAgents 框架专有协议处理 | AgentState 转换、write_todos 映射、VFS 文件引用 |
| **AgentScope 适配器** | AgentScope 框架专有协议处理 | MessageHub 映射、msghub 订阅机制 |
| **UnifiedMessage 消息中心** | 统一消息格式管理 | 消息路由、协议转换核心、状态追踪 |
| **决策索引同步引擎** | 跨框架决策索引一致性 | 索引生成、对齐、冲突解决 |
| **协议扩展管理器** | 支持新增框架协议 | 框架注册、适配器工厂 |

---

## 3. UnifiedMessage 统一消息格式

### 3.1 消息结构定义

```yaml
unified_message:
  # ========== 消息标识 ==========
  message_id: "msg_20260615_001_a1b2c3"
  conversation_id: "conv_scene001_planning_001"
  session_id: "sess_20260615_001"
  timestamp: "2026-06-15T10:05:00.123Z"
  trace_id: "trace_001"                    # 用于跨框架追踪

  # ========== 发送方信息 ==========
  sender:
    agent_id: "agent_scene001_planner_001"
    agent_name: "课程规划 Agent"
    role: "teacher"
    framework: "DeepAgents"                # DeepAgents / AgentScope
    framework_version: "1.0"
    node_id: "node_c001"                   # 知识网络节点关联

  # ========== 接收方信息 ==========
  receiver:
    agent_id: "agent_scene001_researcher_001"
    agent_name: "研究助理 Agent"
    role: "assistant"
    framework: "AgentScope"
    framework_version: "2.1"
    node_id: "node_c002"

  # ========== 协议映射元数据 ==========
  protocol_metadata:
    from_framework: "DeepAgents"
    from_protocol: "AgentState"
    to_framework: "AgentScope"
    to_protocol: "MessageHub"

  # ========== 消息意图 ==========
  intent:
    type: "request"                        # request / response / broadcast / notification / error
    action: "search_knowledge"              # 具体动作
    priority: "normal"                     # high / normal / low
    expecting_response: true
    response_deadline: "2026-06-15T10:15:00Z"

  # ========== 消息内容 ==========
  content:
    type: "task"                           # task / data / control / file / memory
    data:
      task_id: "task_001"
      action: "search_knowledge"
      parameters:
        query: "一元二次方程教学方法"
        top_k: 3
        scope: "current_chapter"
      constraints:
        max_results: 10
        timeout_seconds: 30

  # ========== 上下文追踪 ==========
  context_trace:
    decision_index_refs:                   # 引用决策索引 ≤300 Token
      - "dp_001"
      - "dp_002"
    knowledge_node_refs:                   # 引用知识节点
      - "node_c001"
      - "node_s002"
    conversation_history:                  # 最近对话历史（摘要）
      - turn: 1
        speaker: "agent_scene001_planner_001"
        summary: "请求搜索教学方法"
      - turn: 2
        speaker: "agent_scene001_researcher_001"
        summary: "返回3条相关教学资源"

  # ========== 附件 ==========
  attachments:
    - type: "file"
      name: "outline_draft.yaml"
      path: "/sessions/sess_001/outline_draft.yaml"
      size: 2048
      format: "yaml"

  # ========== 扩展字段 ==========
  extensions:
    custom_field: "value"
    # 用于框架特有信息的桥接
```

### 3.2 消息类型定义

| 类型 | 说明 | 适用场景 |
|-----|------|---------|
| **task** | 任务请求/响应 | Agent 间任务分发与执行 |
| **data** | 数据传输 | 知识节点、决策索引同步 |
| **control** | 控制指令 | 启动/停止/暂停 Agent |
| **file** | 文件传输 | VFS 文件引用传递 |
| **memory** | 记忆操作 | 记忆读写、同步 |

### 3.3 意图类型定义

| 类型 | 说明 | 期望响应 |
|-----|------|---------|
| **request** | 请求执行动作 | 必须 response |
| **response** | 响应请求结果 | 无 |
| **broadcast** | 广播消息 | 可选 response |
| **notification** | 单向通知 | 不需要响应 |
| **error** | 错误报告 | 可选 response |

---

## 4. DeepAgents ↔ AgentScope 映射规则

### 4.1 核心概念映射表

| DeepAgents 概念 | AgentScope 概念 | UnifiedMessage 映射 | 转换说明 |
|----------------|----------------|---------------------|---------|
| **AgentState** | Message | `unified_message.content` | AgentState 状态 → Message 内容 |
| **write_todos** | MessageHub.publish | `intent.type = "broadcast"` | todos 变更广播 |
| **VFS file reference** | - | `content.type = "file"` | 文件引用统一包装 |
| **AgentState.state** | message.content | `content.data` | 状态数据平铺 |
| **AgentState.observations** | - | `context_trace` | 观察历史转入上下文 |
| **-** | msghub.subscribe | `receiver` 订阅机制 | AgentScope 订阅 → Unified 订阅 |
| **memory.read** | Memory.read | `content.type = "memory"` | 记忆操作统一 |
| **decision_point** | - | `context_trace.decision_index_refs` | 决策索引引用 |

### 4.2 DeepAgents → UnifiedMessage 转换

```
DeepAgents AgentState
       │
       ▼
[提取 agent_id, role, framework]
       │
       ▼
[转换 state 字段]
       │
       ├─ 若为 todo 更新 → intent.type = "broadcast"
       ├─ 若为文件引用 → content.type = "file"
       └─ 否则 → content.type = "task"
       │
       ▼
[转换 observations 到 context_trace]
       │
       ▼
[添加 protocol_metadata]
       │
       ▼
UnifiedMessage
```

**转换示例**：

```yaml
# DeepAgents AgentState (输入)
deepagents_state:
  agent_id: "agent_planner_001"
  state:
    current_task: "search_knowledge"
    result: "找到3条教学方法"
  todos:
    - id: 1
      content: "分析课程目标"
      status: "completed"
    - id: 2
      content: "搜索教学方法"
      status: "in_progress"
  observations:
    - "学生基础薄弱"
    - "需要补充基础概念"

# UnifiedMessage (输出)
unified_message:
  message_id: "msg_auto_001"
  sender:
    agent_id: "agent_planner_001"
    framework: "DeepAgents"
  intent:
    type: "broadcast"
    action: "update_todos"
  content:
    type: "task"
    data:
      todos_update:
        - id: 1
          status: "completed"
        - id: 2
          status: "in_progress"
  context_trace:
    observations:
      - "学生基础薄弱"
      - "需要补充基础概念"
```

### 4.3 AgentScope → UnifiedMessage 转换

```
AgentScope MessageHub Message
       │
       ▼
[提取 source_id, content, channel]
       │
       ▼
[映射 channel 到 intent.type]
       │
       ├─ "broadcast" → intent.type = "broadcast"
       ├─ "direct" → intent.type = "request"
       └─ "notification" → intent.type = "notification"
       │
       ▼
[转换 content 到 content.data]
       │
       ▼
[添加 protocol_metadata]
       │
       ▼
UnifiedMessage
```

**转换示例**：

```yaml
# AgentScope MessageHub Message (输入)
agentscope_message:
  source_id: "tutor_001"
  channel: "direct"
  content:
    type: "text"
    text: "请搜索教学方法"
    metadata:
      intent: "search"

# UnifiedMessage (输出)
unified_message:
  message_id: "msg_auto_002"
  sender:
    agent_id: "agent_tutor_001"
    framework: "AgentScope"
  intent:
    type: "request"
    action: "search_knowledge"
  content:
    type: "task"
    data:
      query: "教学方法"
  protocol_metadata:
    from_framework: "AgentScope"
    from_protocol: "MessageHub"
    to_framework: "DeepAgents"
    to_protocol: "AgentState"
```

### 4.4 UnifiedMessage → 目标框架转换

```
UnifiedMessage
       │
       ▼
[读取 protocol_metadata.to_framework]
       │
       ├─ DeepAgents → 调用 DeepAgents 适配器
       └─ AgentScope → 调用 AgentScope 适配器
       │
       ▼
[根据 intent.type 执行映射]
       │
       ├─ broadcast → 转换为目标框架的广播机制
       ├─ request → 转换为目标框架的请求机制
       └─ notification → 转换为目标框架的通知机制
       │
       ▼
[填充目标框架特有字段]
       │
       ▼
目标框架原生消息格式
```

---

## 5. 跨框架消息转换流程

### 5.1 完整转换流程图

```
Agent A (DeepAgents) 发送消息
           │
           ▼
┌─────────────────────────────────────┐
│       DeepAgents 适配器              │
│  1. 解析 AgentState                  │
│  2. 提取关键字段                     │
│  3. 映射到 UnifiedMessage 结构       │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│       协议转换核心                   │
│  1. 消息类型识别                     │
│  2. 意图解析                         │
│  3. 上下文压缩（如需要）             │
│  4. 决策索引引用注入                 │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│       消息路由引擎                   │
│  1. 确定接收方                       │
│  2. 查找目标框架适配器               │
│  3. 应用路由规则                     │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│       AgentScope 适配器              │
│  1. 转换为 MessageHub 格式          │
│  2. 填充目标框架特有字段             │
│  3. 生成原生 Message 对象            │
└─────────────────┬───────────────────┘
                  │
                  ▼
Agent B (AgentScope) 接收消息
```

### 5.2 消息转换器核心接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `to_unified(framework, native_message)` | 转换为 UnifiedMessage | framework: str, message: object | UnifiedMessage |
| `from_unified(unified_message, target_framework)` | 从 UnifiedMessage 转换 | message: UnifiedMessage, framework: str | NativeMessage |
| `validate_unified(message)` | 校验 UnifiedMessage | message: dict | ValidationResult |
| `compress_context(message, max_tokens)` | 压缩上下文 | message: UnifiedMessage, max_tokens: int | CompressedMessage |

### 5.3 框架适配器接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `adapt_from_native(adapter, native_message)` | 从原生格式转入 | adapter: Adapter, message: object | UnifiedMessage |
| `adapt_to_native(adapter, unified_message)` | 从 UnifiedMessage 转出 | adapter: Adapter, message: UnifiedMessage | NativeMessage |
| `register_adapter(framework, adapter)` | 注册适配器 | framework: str, adapter: Adapter | RegistrationResult |
| `get_adapter(framework)` | 获取适配器 | framework: str | Adapter |

---

## 6. 决策索引同步机制

### 6.1 同步架构

```
┌─────────────────────────────────────────────────────────────┐
│                   决策索引同步架构                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   DeepAgents 端              Unified Layer         AgentScope端 │
│   ┌─────────────┐          ┌─────────────┐        ┌─────────────┐
│   │ 决策索引    │────────▶│  索引聚合器  │◀───────│ 决策索引    │
│   │ 本地缓存    │          │             │        │ 本地缓存    │
│   └─────────────┘          └──────┬──────┘        └─────────────┘
│                                  │                          │
│                                  ▼                          │
│                          ┌─────────────┐                    │
│                          │  索引对齐引擎│                    │
│                          │  冲突检测    │                    │
│                          │  合并策略   │                    │
│                          └─────────────┘                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 索引同步消息格式

```yaml
decision_index_sync:
  sync_id: "sync_001"
  timestamp: "2026-06-15T10:05:00Z"
  source_framework: "DeepAgents"
  target_framework: "AgentScope"

  # 同步的决策索引（≤300 Token 总限制）
  indices:
    - dp_id: "dp_001"
      dp_content: "当学生基础薄弱时，优先补充基础概念而非深入难点"
      confidence: 0.95
      source: "teacher_feedback"
      created_at: "2026-06-14T10:00:00Z"

    - dp_id: "dp_002"
      dp_content: "教学方法选择：讲解→演示→练习，符合布鲁姆认知层次"
      confidence: 0.88
      source: "auto_generated"
      created_at: "2026-06-15T09:00:00Z"

  # 对齐状态
  alignment:
    status: "aligned"                  # aligned / conflict / pending
    conflicts: []                      # 冲突列表（如果有）
    merge_strategy: "confidence_based"  # confidence_based / latest_wins / manual

  # 引用计数（用于缓存管理）
  reference_counts:
    node_c001: 3
    node_s002: 1
```

### 6.3 同步流程

```
决策索引变更触发
       │
       ▼
[生成同步消息]
       │
       ├─ 提取变更的 DP
       ├─ 压缩到 ≤300 Token
       └─ 计算引用计数
       │
       ▼
[发送到索引聚合器]
       │
       ▼
[索引对齐引擎处理]
       │
       ├─ 检测冲突
       │     │
       │     ├─ 有冲突 → 应用合并策略
       │     └─ 无冲突 → 标记 aligned
       │
       ▼
[广播到目标框架]
       │
       ├─ DeepAgents 适配器 → 更新本地缓存
       └─ AgentScope 适配器 → 更新本地缓存
       │
       ▼
[确认同步完成]
       │
       ▼
[更新引用计数]
```

### 6.4 冲突解决策略

| 策略 | 说明 | 适用场景 |
|-----|------|---------|
| **confidence_based** | 信任度高的优先 | 教师反馈 vs 自动生成 |
| **latest_wins** | 最新版本优先 | 版本迭代场景 |
| **manual** | 人工介入解决 | 高重要性冲突 |

---

## 7. 协议扩展机制

### 7.1 新框架接入流程

```
新框架接入请求
       │
       ▼
[定义框架标识符]
       │
       ├─ 例：framework_id = "LangChain"
       └─ framework_version = "0.1"
       │
       ▼
[实现框架适配器]
       │
       ├─ 实现 `adapt_from_native()`
       ├─ 实现 `adapt_to_native()`
       └── 实现 `validate_native()`
       │
       ▼
[注册到适配器工厂]
       │
       └─ protocol_converter.register_adapter("LangChain", adapter)
       │
       ▼
[定义概念映射表]
       │
       ├─ 填写映射规则
       └─ 注册到映射表
       │
       ▼
[测试转换链路]
       │
       ├─ 原生 → Unified → 原生（往返测试）
       └─ 语义一致性校验
       │
       ▼
新框架接入完成
```

### 7.2 扩展配置结构

```yaml
framework_extensions:
  - framework_id: "LangChain"
    framework_version: "0.1"
    adapter_class: "LangChainAdapter"
    concept_mappings:
      - local_concept: "Agent"
        unified_concept: "agent"
      - local_concept: "Chain"
        unified_concept: "pipeline"
      - local_concept: "Memory"
        unified_concept: "memory"
    capabilities:
      - "multi_modal"
      - "tool_use"
    status: "experimental"
```

---

## 8. 核心接口

### 8.1 协议转换核心接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `convert_to_unified(framework, message)` | 转换为统一格式 | framework: str, message: object | UnifiedMessage |
| `convert_from_unified(message, target_framework)` | 从统一格式转换 | message: UnifiedMessage, framework: str | NativeMessage |
| `route_message(message, routing_rules)` | 路由消息 | message: UnifiedMessage, rules: dict | RouteResult |
| `transform_payload(payload, from_format, to_format)` | 负载格式转换 | payload: object, from: str, to: str | TransformedPayload |

### 8.2 状态同步接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `sync_decision_index(sync_message)` | 同步决策索引 | sync: DecisionIndexSync | SyncResult |
| `get_local_index(framework)` | 获取本地索引 | framework: str | IndexSnapshot |
| `resolve_conflict(conflict_id, strategy)` | 解决冲突 | conflict_id: str, strategy: str | ResolutionResult |
| `get_alignment_status()` | 获取对齐状态 | - | AlignmentStatus |

### 8.3 适配器管理接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `register_adapter(framework, adapter)` | 注册适配器 | framework: str, adapter: Adapter | RegistrationResult |
| `unregister_adapter(framework)` | 注销适配器 | framework: str | OperationResult |
| `list_supported_frameworks()` | 列出支持的框架 | - | FrameworkList |
| `get_adapter_capabilities(framework)` | 获取框架能力 | framework: str | CapabilityList |

---

## 9. 目录结构

```
orchestration/
├── protocol_converter/
│   ├── __init__.py
│   ├── unified_message.py           # UnifiedMessage 定义
│   ├── message_center.py            # 消息中心
│   ├── router.py                    # 消息路由引擎
│   ├── context_compressor.py        # 上下文压缩
│   └── adapters/
│       ├── __init__.py
│       ├── base_adapter.py           # 适配器基类
│       ├── deepagents_adapter.py     # DeepAgents 适配器
│       ├── agentscope_adapter.py     # AgentScope 适配器
│       └── adapter_factory.py       # 适配器工厂
├── decision_index_sync/
│   ├── __init__.py
│   ├── index_aggregator.py           # 索引聚合器
│   ├── alignment_engine.py          # 对齐引擎
│   ├── conflict_resolver.py         # 冲突解决
│   └── sync_protocol.py             # 同步协议
└── schemas/
    ├── unified_message_schema.json   # UnifiedMessage JSON Schema
    ├── sync_message_schema.json      # 同步消息 Schema
    └── adapter_registry_schema.json  # 适配器注册 Schema
```

---

## 10. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| 消息格式 | UnifiedMessage 统一格式 | 屏蔽框架差异，支持跨框架通信 |
| 转换方向 | 双向转换适配器 | 支持任意框架组合的通信 |
| 上下文限制 | 决策索引 ≤300 Token | DP-ARCH-01 核心约束 |
| 状态同步 | 最终一致性 | 允许短暂不一致，保证可用性 |
| 冲突策略 | 多策略可选 | 适应不同场景需求 |
| 扩展机制 | 适配器工厂模式 | 新框架接入无需修改核心代码 |
| 追踪机制 | trace_id 贯穿全程 | 跨框架问题排查必备 |

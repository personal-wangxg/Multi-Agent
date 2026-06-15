# Agent 消息数据模型设计

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-08（Agent 消息协议）

---

## 1. 设计目标

定义 EduAgents 框架内 Agent 之间及 Agent 与外部系统之间消息传递的标准化格式：
- UnifiedMessage 统一消息格式
- 框架映射规则
- 消息生命周期
- 错误处理机制

---

## 2. 统一消息格式（UnifiedMessage）

### 2.1 完整字段定义

```yaml
unified_message:
  # ========== 消息标识 ==========
  message_id: "msg_20260615_001"         # 全局唯一消息ID
  conversation_id: "conv_001"            # 所属会话ID
  parent_message_id: "msg_20260615_000"  # 父消息ID（用于消息树）
  reply_to: "msg_20260615_000"          # 回复目标（可选）
  
  # ========== 发送者/接收者 ==========
  sender:
    agent_id: "agent_scene001_planner_001"
    role: "planner"
    scene_type: "SCENE-001"
  receiver:
    agent_id: "agent_scene002_researcher_001"  # null 表示广播
    role: "researcher"
    scene_type: "SCENE-002"
  
  # ========== 消息内容 ==========
  message_type: "task_request"           # 消息类型
  action: "execute_task"                 # 操作类型
  content:
    task: "research_knowledge_points"
    task_id: "task_001"
    payload:
      topic: "一元二次方程"
      depth: "concept+skill+tool"
      constraints:
        max_nodes: 10
        required_layers: ["concept", "skill", "tool"]
    context:
      decision_summary: "总课时12，面向初三学生..."
      relevant_dps:
        - "DP-CP-001"
        - "DP-CP-002"
  
  # ========== 元数据 ==========
  metadata:
    created_at: "2026-06-15T10:00:00Z"
    expires_at: "2026-06-15T11:00:00Z"   # 过期时间（可选）
    priority: "normal"                    # low / normal / high / urgent
    correlation_id: "req_001"            # 关联请求ID（用于追踪）
    trace_id: "trace_abc123"             # 分布式追踪ID
  
  # ========== 框架映射 ==========
  framework_mapping:
    source_framework: "LangChain"
    source_message_type: "HumanMessage"
    mapped_to: "UnifiedMessage"
  
  # ========== 状态 ==========
  status: "delivered"                    # pending / sent / delivered / processed / failed
  retry_count: 0
  max_retries: 3
```

### 2.2 消息类型分类

| message_type | 说明 | 典型用途 |
|-------------|------|---------|
| `task_request` | 任务请求 | 编排层向 Agent 下发任务 |
| `task_response` | 任务响应 | Agent 返回任务结果 |
| `task_progress` | 任务进度 | Agent 报告执行进度 |
| `feedback` | 反馈消息 | 教师或系统反馈 |
| `system_notification` | 系统通知 | 系统级事件通知 |
| `agent_communication` | Agent间通信 | Agent 之间直接消息 |
| `error_report` | 错误报告 | 错误或异常信息 |
| `heartbeat` | 心跳消息 | Agent 存活检测 |

### 2.3 action 操作类型

| message_type | 适用 action | 说明 |
|-------------|------------|------|
| `task_request` | execute_task / query_status / cancel_task / pause_task | 任务操作 |
| `task_response` | success / partial_success / failure | 任务结果 |
| `task_progress` | started / in_progress / completed / waiting_input | 进度状态 |
| `feedback` | approve / revise / reject / delay / approve_with_comments | 人机协同 |
| `system_notification` | shutdown / restart / config_update / alert | 系统事件 |
| `agent_communication` | query / response / request_help / provide_help | Agent 交互 |

---

## 3. 框架映射规则

### 3.1 支持的框架

| 框架 | 映射支持 |
|-----|---------|
| LangChain | HumanMessage / AIMessage / ToolMessage → UnifiedMessage |
| AutoGen | ChatMessage / Message → UnifiedMessage |
| CrewAI | Message / Task → UnifiedMessage |
| Custom | 自定义消息 → UnifiedMessage |

### 3.2 LangChain 映射示例

```yaml
# LangChain HumanMessage
langchain_human_message:
  type: "human"
  content: "请生成一元二次方程的知识网络"
  name: "planner"
  
# 转换为 UnifiedMessage
mapped_unified_message:
  message_type: "task_request"
  action: "execute_task"
  sender:
    agent_id: "human_planner"
    role: "user"
  content:
    task: "generate_knowledge_network"
    payload:
      topic: "一元二次方程"
    context: {}
  framework_mapping:
    source_framework: "LangChain"
    source_message_type: "HumanMessage"
    original_content: "请生成一元二次方程的知识网络"
```

### 3.3 AutoGen 映射示例

```yaml
# AutoGen ChatMessage
autogen_chat_message:
  role: "assistant"
  content: "已生成知识网络，包含6个节点..."
  metadata:
    agent: "researcher"
    
# 转换为 UnifiedMessage
mapped_unified_message:
  message_type: "task_response"
  action: "success"
  sender:
    agent_id: "agent_autogen_researcher_001"
    role: "researcher"
  content:
    task_id: "task_001"
    result:
      nodes_count: 6
      edges_count: 5
    payload:
      network_id: "network_001"
  framework_mapping:
    source_framework: "AutoGen"
    source_message_type: "ChatMessage"
    original_content: "已生成知识网络，包含6个节点..."
```

---

## 4. 消息生命周期

### 4.1 消息状态流转

```
                              ┌──────────────┐
                              │   pending    │ ← 创建后初始状态
                              └──────┬───────┘
                                     │ 发送成功
                                     ▼
                              ┌──────────────┐
                              │     sent     │ ← 已发送到目标
                              └──────┬───────┘
                                     │ 目标接收成功
                                     ▼
                              ┌──────────────┐
                              │   delivered  │ ← 消息已投递给接收方
                              └──────┬───────┘
                                     │ 接收方处理完成
                                     ▼
                              ┌──────────────┐
                              │   processed  │ ← 最终成功状态
                              └──────────────┘

         ┌──────────────────────────────────────────────────────┐
         │                     失败路径                          │
         └──────────────────────────────────────────────────────┘

         pending/sent/delivered ──[处理失败]──> ┌──────────────┐
                                                  │    failed    │
                                                  └──────┬───────┘
                                                         │ 重试次数未达上限
                                                         ▼
                                                  ┌──────────────┐
                                                  │   pending    │ ← 重新入队
                                                  └──────────────┘
```

### 4.2 状态说明

| 状态 | 说明 | 可转换状态 |
|-----|------|---------|
| `pending` | 等待发送 | sent, failed |
| `sent` | 已发送 | delivered, failed |
| `delivered` | 已投递到接收方 | processed, failed |
| `processed` | 接收方处理完成 | （终态） |
| `failed` | 处理失败 | pending（可重试）, discarded |

### 4.3 消息超时与重试

| 配置项 | 默认值 | 说明 |
|-------|--------|------|
| `message_timeout` | 300s | 消息处理超时时间 |
| `max_retries` | 3 | 最大重试次数 |
| `retry_delay` | 5s | 重试间隔（指数退避） |

```yaml
retry_policy:
  max_retries: 3
  retry_delay_base: 5                          # 基础延迟（秒）
  retry_delay_multiplier: 2                    # 延迟倍数
  retry_delays: [5, 10, 20]                    # 具体延迟列表
  retry_on_errors:
    - "timeout"
    - "connection_error"
    - "queue_full"
  do_not_retry_on_errors:
    - "invalid_message"
    - "unauthorized"
    - "forbidden"
```

---

## 5. 错误处理机制

### 5.1 错误分类

| 错误类别 | 说明 | 处理策略 |
|---------|------|---------|
| `validation_error` | 消息格式校验失败 | 不重试，记录并告警 |
| `timeout_error` | 消息处理超时 | 重试（≤3次） |
| `connection_error` | 网络/连接错误 | 重试（≤3次） |
| `queue_error` | 队列满或不可用 | 重试（≤3次） |
| `unauthorized_error` | 认证/授权失败 | 不重试，返回错误 |
| `rate_limit_error` | 限流触发 | 退避后重试 |
| `internal_error` | 系统内部错误 | 重试（≤3次） |

### 5.2 错误消息结构

```yaml
error_report:
  message_id: "msg_20260615_001"
  error:
    code: "TIMEOUT_ERROR"
    category: "timeout_error"
    message: "消息处理超时（300秒）"
    details:
      timeout_seconds: 300
      actual_duration: 300
    cause: "Agent 执行时间过长"
    recoverable: true                          # 是否可恢复
    
  original_message:
    message_id: "msg_20260615_001"
    message_type: "task_request"
    action: "execute_task"
    
  resolution:
    action: "retry"                           # retry / discard / escalate / notify
    retry_after: 10                           # 秒
    escalation_target: "system_admin"
    
  metadata:
    occurred_at: "2026-06-15T10:05:00Z"
    trace_id: "trace_abc123"
    retry_count: 1
```

### 5.3 错误处理流程

```
消息处理失败
       │
       ▼
[判断错误类型]
       │
       ├─ validation_error/unauthorized/forbidden
       │       └─ 不重试，直接返回错误
       │
       ├─ timeout/connection/queue/internal
       │       └─ 检查重试次数
       │              │
       │              ├─ < max_retries → 退避重试
       │              │
       │              └─ >= max_retries → 标记失败，告警
       │
       └─ rate_limit
              └─ 等待后重试
```

---

## 6. 消息队列配置

### 6.1 队列类型

| 队列类型 | 用途 | 持久化 | 优先级支持 |
|---------|------|--------|----------|
| `task_queue` | 任务消息 | 是 | 是 |
| `response_queue` | 响应消息 | 是 | 是 |
| `feedback_queue` | 反馈消息 | 是 | 否 |
| `system_queue` | 系统消息 | 否 | 是 |

### 6.2 队列配置示例

```yaml
queue_config:
  task_queue:
    name: "eduagents.tasks"
    durable: true
    max_length: 10000
    message_ttl: 3600                         # 秒
    dead_letter_queue: "eduagents.tasks.dlq"
    
  response_queue:
    name: "eduagents.responses"
    durable: true
    max_length: 10000
    message_ttl: 1800
    
  feedback_queue:
    name: "eduagents.feedback"
    durable: true
    max_length: 5000
    message_ttl: 86400
    
  system_queue:
    name: "eduagents.system"
    durable: false
    max_length: 1000
    message_ttl: 300
```

---

## 7. 安全与认证

### 7.1 消息签名

```yaml
message_signature:
  algorithm: "HMAC-SHA256"
  secret_key_ref: "vault:secret/eduagents/message_signing_key"
  signed_fields:
    - "message_id"
    - "sender.agent_id"
    - "created_at"
    - "content"
  signature: "base64_encoded_signature"
  verified_at: "2026-06-15T10:00:01Z"
```

### 7.2 认证头

```yaml
auth_headers:
  Authorization: "Bearer <jwt_token>"
  X-Agent-ID: "agent_scene001_planner_001"
  X-Task-ID: "task_001"
  X-Trace-ID: "trace_abc123"
```

---

## 8. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| 消息格式 | 统一为 UnifiedMessage | 跨框架兼容，便于集成 |
| 消息 ID | `msg_{timestamp}_{seq}` | 全局唯一，可排序 |
| 状态管理 | pending → sent → delivered → processed | 完整的状态追踪 |
| 重试策略 | 指数退避，最多重试3次 | 平衡可靠性与资源消耗 |
| 错误分类 | 按是否可恢复分类 | 差异化处理策略 |
| 队列持久化 | 关键队列启用持久化 | 保证消息不丢失 |

---

## 9. 文件目录结构

```
eduagents/
├── messaging/
│   ├── __init__.py
│   ├── unified_message.py           # 统一消息模型
│   ├── message_queue.py             # 消息队列管理
│   ├── frame_mapper.py              # 框架映射器
│   ├── error_handler.py             # 错误处理
│   └── message_validator.py          # 消息校验
├── config/
│   └── messaging_config.yaml         # 消息配置
└── docs/architecture/data_models/
    └── agent_message.md             # 本文档
```

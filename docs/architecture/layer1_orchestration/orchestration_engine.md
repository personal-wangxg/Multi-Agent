# Agent 编排调度引擎设计

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-03（Agent编排与调度）、FR-04（框架协议转换）

---

## 1. 设计目标

编排层负责 Agent 的运行时管理，支持：
- 多 Agent 启动与生命周期管理
- Agent 间消息路由与通信
- 全局状态同步
- 上下文主动控制
- 跨框架协议转换

| 设计原则 | 说明 |
|---------|------|
| **框架无关性** | 支持 DeepAgents、AgentScope 及未来扩展 |
| **可扩展性** | 支持新增 Agent 角色和协作模式 |
| **可靠性** | 失败重试与降级机制 |
| **可观测性** | 完整的执行追踪与审计 |

---

## 2. 架构组件

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent 编排调度引擎                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │  Agent 配置  │────▶│  配置解析器  │────▶│  Agent 工厂  │    │
│  └──────────────┘     └──────────────┘     └──────┬───────┘    │
│                                                   │              │
│                                                   ▼              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   消息中心   │◀───▶│  编排调度器  │◀───▶│  状态管理器  │    │
│  └──────┬───────┘     └──────────────┘     └──────────────┘    │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │  协议转换层  │     │  上下文管理器│     │  可观测性层  │    │
│  │ (DeepAgents │     │ (Token控制  │     │ (日志/追踪   │    │
│  │  ↔AgentScope)│     │  /记忆联动) │     │  /审计)     │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 组件职责

| 组件 | 职责 | 核心功能 |
|-----|------|---------|
| **配置解析器** | 解析 Agent 配置 | YAML/JSON 解析、配置校验、默认值填充 |
| **Agent 工厂** | 创建 Agent 实例 | 根据框架类型创建对应 Agent |
| **编排调度器** | 协调 Agent 执行 | 任务分配、流程控制、失败重试 |
| **消息中心** | Agent 间通信 | 消息路由、广播/订阅、消息持久化 |
| **状态管理器** | 全局状态同步 | 任务进度、中间产物、上下文状态 |
| **协议转换层** | 跨框架通信 | UnifiedMessage 定义、框架适配器 |
| **上下文管理器** | 上下文控制 | Token 检查、摘要压缩、记忆注入 |
| **可观测性层** | 执行追踪 | 日志记录、性能监控、审计回放 |

---

## 3. Agent 配置模型

### 3.1 Agent 配置结构

```yaml
agent_config:
  agent_id: "agent_scene001_planner_001"
  name: "课程规划 Agent"
  role: "teacher"                 # teacher / student / assistant / evaluator
  framework: "DeepAgents"         # DeepAgents / AgentScope / generic
  description: "负责课程规划的智能体"
  
  # Harness 约束绑定
  harness:
    template_id: "tpl_scene001_planner_v1.0"
    schema_id: "schema_scene001_outline_v1.0"
    tool_whitelist_id: "wl_scene001"
  
  # 配置参数
  config:
    model: "gpt-4o"
    temperature: 0.7
    max_tokens: 4096
  
  # 协作关系
  communication:
    send_to: ["agent_scene001_researcher_001"]
    receive_from: ["agent_scene001_researcher_001", "human_teacher"]
  
  # 工具列表
  tools:
    - name: "read_file"
      params: {}
    - name: "write_file"
      params: {}
    - name: "search_knowledge"
      params: {}
```

### 3.2 协作模式

| 模式 | 说明 | 适用场景 |
|-----|------|---------|
| **主从模式** | 一个主 Agent 控制多个从 Agent | 课程规划（主规划 + 研究助理） |
| **多角色模式** | 多个 Agent 平等协作 | 虚拟教室（教师 + 学生 + 助教） |
| **流水线模式** | Agent 按顺序执行 | 备课流程（规划 → 教案 → 学案） |

---

## 4. 消息协议设计

### 4.1 UnifiedMessage 统一消息格式

```yaml
unified_message:
  message_id: "msg_001"
  timestamp: "2026-06-12T10:05:00Z"
  
  # 发送方
  sender:
    agent_id: "agent_scene001_planner_001"
    role: "teacher"
    framework: "DeepAgents"
  
  # 接收方
  receiver:
    agent_id: "agent_scene001_researcher_001"
    role: "assistant"
    framework: "DeepAgents"
  
  # 消息意图
  intent: "request"               # request / response / broadcast / notification
  
  # 消息内容
  content:
    type: "task"
    data:
      task_id: "task_001"
      action: "search_knowledge"
      parameters:
        query: "一元二次方程教学方法"
        top_k: 3
  
  # 元数据
  metadata:
    conversation_id: "conv_001"
    session_id: "sess_001"
    priority: "normal"            # high / normal / low
    expires_at: "2026-06-12T10:15:00Z"
```

### 4.2 框架协议映射

| DeepAgents 概念 | AgentScope 概念 | UnifiedMessage 映射 |
|----------------|----------------|-------------------|
| AgentState | Message | unified_message.content |
| write_todos | MessageHub.publish | unified_message.intent = "broadcast" |
| VFS file | - | unified_message.content.type = "file" |
| - | msghub.subscribe | 消息中心订阅机制 |

---

## 5. 编排流程

### 5.1 Agent 启动流程

```
输入：Agent 配置列表
       │
       ▼
[配置解析器解析配置]
       │
       ▼
[Agent 工厂创建实例]
       │
       ├─ DeepAgents → 创建 DeepAgents Agent
       ├─ AgentScope → 创建 AgentScope Agent
       └─ generic → 创建通用 Agent 包装器
       │
       ▼
[加载 Harness 约束]
       │
       ├─ 注入提示词模板
       ├─ 绑定输出 Schema
       └─ 设置工具白名单
       │
       ▼
[注册到消息中心]
       │
       └─ 订阅相关消息主题
       │
       ▼
[启动 Agent 事件循环]
       │
       ▼
Agent 就绪
```

### 5.2 消息路由流程

```
Agent A 发送消息
       │
       ▼
[消息中心接收消息]
       │
       ▼
[路由规则匹配]
       │
       ├─ 点对点 → 直接发送给接收方
       ├─ 广播 → 发送给所有订阅者
       └─ 模式匹配 → 发送给匹配的 Agent
       │
       ▼
[协议转换（如需要）]
       │
       ├─ DeepAgents → UnifiedMessage
       ├─ AgentScope → UnifiedMessage
       └─ UnifiedMessage → 目标框架格式
       │
       ▼
[消息投递]
       │
       ▼
Agent B 接收消息
```

### 5.3 上下文主动控制流程

```
每轮交互前
       │
       ▼
[检查当前上下文 Token 量]
       │
       ├─ 未超限 → 继续执行
       │
       ▼ 超限
[触发上下文管理策略]
       │
       ├─ 策略A：摘要压缩（保留关键信息）
       ├─ 策略B：旧消息遗忘（移除最早消息）
       └─ 策略C：中间产物卸载（写入 VFS）
       │
       ▼
[从持久记忆检索相关内容]
       │
       ├─ 根据当前任务主题检索
       ├─ 注入 ≤ N 条相关记忆
       └─ N 可配置（默认 3）
       │
       ▼
[更新上下文，继续执行]
```

---

## 6. 核心接口

### 6.1 编排引擎接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `start_agents(configs)` | 启动多个 Agent | configs: list | Agent 实例列表 |
| `stop_agents(agent_ids)` | 停止指定 Agent | agent_ids: list | 操作结果 |
| `send_message(message)` | 发送消息 | message: UnifiedMessage | 消息 ID |
| `broadcast_message(topic, content)` | 广播消息 | topic: str, content: dict | 接收者数量 |
| `get_agent_status(agent_id)` | 获取 Agent 状态 | agent_id: str | AgentStatus |
| `get_session_status(session_id)` | 获取会话状态 | session_id: str | SessionStatus |
| `retry_agent(agent_id)` | 重试失败的 Agent | agent_id: str | 操作结果 |
| `inject_context(session_id, context)` | 注入上下文 | session_id: str, context: dict | 操作结果 |

### 6.2 消息中心接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `register_agent(agent)` | 注册 Agent | agent: Agent | 注册结果 |
| `subscribe(topic, agent_id)` | 订阅主题 | topic: str, agent_id: str | 订阅结果 |
| `unsubscribe(topic, agent_id)` | 取消订阅 | topic: str, agent_id: str | 操作结果 |
| `publish(message)` | 发布消息 | message: UnifiedMessage | 投递结果 |
| `get_messages(session_id)` | 获取会话消息 | session_id: str | 消息列表 |

---

## 7. 容错与降级

### 7.1 失败重试机制

| 失败类型 | 重试策略 | 最大重试次数 |
|---------|---------|-------------|
| LLM 调用失败 | 指数退避重试 | 3 |
| 工具调用失败 | 立即重试 | 2 |
| 消息投递失败 | 队列重试 | 5 |
| Agent 崩溃 | 重启 Agent | 1 |

### 7.2 降级策略

```
Agent 失败
       │
       ▼
[检查重试次数是否超限]
       │
       ├─ 否 → 重试
       │
       ▼ 是
[触发降级]
       │
       ├─ 通知编排层
       ├─ 记录失败原因
       └─ 执行降级策略
             │
             ├─ 备选 Agent（如有）→ 切换到备选
             ├─ 简化输出 → 生成简化版结果
             └─ 人工干预 → 通知教师介入
```

---

## 8. 目录结构

```
orchestration/
├── __init__.py
├── config_parser.py           # 配置解析器
├── agent_factory.py           # Agent 工厂
├── orchestrator.py            # 编排调度器
├── message_hub.py             # 消息中心
├── state_manager.py           # 状态管理器
├── protocol_converter.py      # 协议转换层
├── context_manager.py         # 上下文管理器
├── observability.py           # 可观测性层
└── adapters/
    ├── __init__.py
    ├── deepagents_adapter.py  # DeepAgents 适配器
    └── agentscope_adapter.py  # AgentScope 适配器
```

---

## 9. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| 消息格式 | UnifiedMessage 统一格式 | 屏蔽框架差异，支持跨框架通信 |
| 上下文控制 | 主动检查 + 多策略 | 防止 Token 超限，保证系统稳定 |
| 重试策略 | 指数退避 + 差异化次数 | 平衡重试成本与成功率 |
| 降级策略 | 多级别降级 | 根据场景选择合适的降级方式 |
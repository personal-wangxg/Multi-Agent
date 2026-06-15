# 技术选型总览

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-12（配置持久化）、FR-14（可观测性）

---

## 1. 设计目标

定义 EduAgents 框架各层的技术选型，确保：
- 各层技术栈协调一致
- 支持 Git 版本管理配置
- 提供可观测性保障
- 灵活适配不同规模部署

---

## 2. 技术选型总览

### 2.1 分层技术栈总表

| 层级 | 核心组件 | 技术选型 | 优先级 |
|-----|---------|---------|--------|
| **L0 基础设施层** | Harness 约束 | Python + Jinja2 + jsonschema | P0 |
| **L1 编排层** | 任务编排 | Python + asyncio | P0 |
| **L2 知识层** | 知识网络 | Python + Pydantic | P0 |
| **L3 Agent 层** | Agent 运行时 | LangChain / AutoGen / 自研 | P0 |
| **L4 人机协同层** | 教师协作 | FastAPI + WebSocket | P1 |
| **L5 可视化层** | Web UI | React + TypeScript | P2 |
| **存储层** | 配置/产物 | Git + YAML + JSON | P0 |
| **存储层** | 运行时数据 | SQLite / PostgreSQL | P1 |
| **向量存储** | 知识检索 | （方案D，非必须） | P2 |

### 2.2 核心技术栈

```
┌─────────────────────────────────────────────────────────────────┐
│                        核心技术栈架构                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │                    Python 3.11+                         │    │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │    │
│   │  │ asyncio │  │ Pydantic│  │ jsonschema│  │ Jinja2  │     │    │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │    │
│   └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│   │   LangChain  │  │   AutoGen    │  │   自研       │           │
│   │  (可选)      │  │  (可选)      │  │  (推荐)      │           │
│   └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 各层详细技术栈

### 3.1 L0 基础设施层（Harness 约束层）

| 组件 | 技术选型 | 说明 |
|-----|---------|------|
| **约束引擎** | Python 3.11+ | 核心执行环境 |
| **模板引擎** | Jinja2 | 提示词模板渲染 |
| **Schema 校验** | jsonschema | Agent 输出结构校验 |
| **配置管理** | Pydantic | 数据模型验证 |
| **日志** | Structlog | 结构化日志输出 |
| **测试** | pytest | 单元测试框架 |

### 3.2 L1 编排层

| 组件 | 技术选型 | 说明 |
|-----|---------|------|
| **任务编排** | asyncio + 自研 Workflow Engine | 协程异步任务流 |
| **状态管理** | 内存状态机 + SQLite | 轻量状态追踪 |
| **消息队列** | Redis Queue / 自研 | 异步任务分发 |
| **API** | FastAPI | 对外 REST 接口 |

### 3.3 L2 知识层

| 组件 | 技术选型 | 说明 |
|-----|---------|------|
| **知识网络** | NetworkX + 自研图引擎 | 知识图谱管理 |
| **数据验证** | Pydantic | 节点/边数据校验 |
| **版本管理** | GitPython | Git 集成 |
| **序列化** | YAML + JSON | 人类可读格式 |

### 3.4 L3 Agent 层

| 组件 | 技术选型 | 说明 |
|-----|---------|------|
| **Agent 框架** | 自研（推荐） / LangChain / AutoGen | Agent 运行时 |
| **LLM 集成** | OpenAI SDK / Anthropic SDK | 模型调用 |
| **工具调用** | 自研 Tool Registry | 工具注册与管理 |
| **沙箱** | Modal / Docker（可选） | 工具执行隔离 |

### 3.5 L4 人机协同层

| 组件 | 技术选型 | 说明 |
|-----|---------|------|
| **API 框架** | FastAPI | REST API + WebSocket |
| **实时通信** | WebSocket (Socket.IO) | 任务状态推送 |
| **ORM** | SQLAlchemy | 数据库抽象 |
| **API 文档** | OpenAPI 3.0 / Swagger | 接口标准化 |

### 3.6 L5 可视化层

| 组件 | 技术选型 | 说明 |
|-----|---------|------|
| **前端框架** | React 18 + TypeScript | UI 开发 |
| **状态管理** | Zustand | 前端状态 |
| **UI 组件** | Ant Design Pro | 企业级组件 |
| **可视化** | D3.js + ECharts | 知识网络图表 |
| **构建** | Vite | 前端构建工具 |

---

## 4. LLM 提供商选择

### 4.1 支持的 LLM 提供商

| 提供商 | 模型 | 支持状态 | 备注 |
|-------|-----|---------|------|
| **OpenAI** | GPT-4o, GPT-4o-mini, GPT-4-turbo | P0 支持 | 默认推荐 |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus | P0 支持 | 备选方案 |
| **Azure OpenAI** | GPT-4o, GPT-4 | P1 支持 | 企业部署 |
| **Google AI** | Gemini Pro | P1 支持 | 未来扩展 |
| **Ollama** | Llama 3, Mistral | P2 支持 | 本地部署 |
| **vLLM** | 开源模型 | P2 支持 | 自托管 |

### 4.2 多模型配置

```yaml
llm_providers:
  openai:
    default: true
    api_key_ref: "vault:secret/openai_api_key"
    models:
      gpt-4o:
        context_window: 128000
        max_output_tokens: 4096
        cost_per_1k_input: 0.005
        cost_per_1k_output: 0.015
      gpt-4o-mini:
        context_window: 128000
        max_output_tokens: 4096
        cost_per_1k_input: 0.0015
        cost_per_1k_output: 0.006
        
  anthropic:
    api_key_ref: "vault:secret/anthropic_api_key"
    models:
      claude-3-5-sonnet:
        context_window: 200000
        max_output_tokens: 4096
        cost_per_1k_input: 0.003
        cost_per_1k_output: 0.015
```

### 4.3 模型选择策略

| 场景 | 推荐模型 | 理由 |
|-----|---------|------|
| 复杂规划任务 | GPT-4o / Claude 3.5 Sonnet | 强推理能力 |
| 快速生成任务 | GPT-4o-mini | 低延迟低成本 |
| 结构化输出任务 | GPT-4-turbo | 稳定输出 |
| 本地/离线场景 | Ollama + Llama 3 | 隐私保护 |

---

## 5. 存储方案

### 5.1 存储层次

| 存储类型 | 用途 | 技术选型 | 持久化 | 说明 |
|---------|------|---------|--------|------|
| **配置存储** | 配置文件、模板 | Git + YAML | 是 | 版本化管理 |
| **产物存储** | 阶段产物、知识网络 | Git + JSON/YAML | 是 | 可追溯 |
| **运行时存储** | 任务状态、消息 | SQLite（开发）/ PostgreSQL（生产） | 是 | 结构化数据 |
| **缓存** | 短期数据 | Redis | 否 | 性能优化 |
| **向量存储** | 知识检索（方案D） | Milvus / Chroma（可选） | 是 | 非必须 |

### 5.2 Git 版本管理方案

```yaml
git_config:
  repository:
    url: "/repo/eduagents-config.git"
    default_branch: "main"
    
  structure:
    - path: "templates/"
      description: "Harness 提示词模板"
    - path: "schemas/"
      description: "输出 Schema 定义"
    - path: "knowledge_networks/"
      description: "知识网络定义"
    - path: "decision_index/"
      description: "决策索引"
    - path: "agent_configs/"
      description: "Agent 配置"
      
  commit_rules:
    message_format: "{action}({scope}): {description}"
    require_review: false                  # 开发阶段无需 review
    auto_deploy_branches:
      - "main"                             # 主分支自动同步到生产
```

### 5.3 数据库方案

#### 开发环境

```yaml
# SQLite 配置（开发环境）
database:
  development:
    engine: "sqlite"
    path: "./data/eduagents_dev.db"
    echo: false
    pool_size: 5
    
# 表结构示例
tables:
  tasks:
    - task_id: TEXT PRIMARY KEY
    - task_name: TEXT
    - status: TEXT
    - created_at: TIMESTAMP
    - updated_at: TIMESTAMP
      
  messages:
    - message_id: TEXT PRIMARY KEY
    - conversation_id: TEXT
    - sender_id: TEXT
    - content: TEXT
    - created_at: TIMESTAMP
```

#### 生产环境

```yaml
# PostgreSQL 配置（生产环境）
database:
  production:
    engine: "postgresql"
    host: "localhost"
    port: 5432
    database: "eduagents"
    username: "eduagents_user"
    password_ref: "vault:secret/postgres_password"
    pool_size: 20
    max_overflow: 10
    ssl_mode: "require"
```

---

## 6. 向量数据库方案（方案D）

### 6.1 概述

向量数据库用于知识检索，属于 P2 非必须功能。仅当需要语义相似度检索时启用。

### 6.2 技术选型

| 方案 | 适用场景 | 部署复杂度 | 推荐度 |
|-----|---------|-----------|--------|
| **Chroma** | 个人/小规模 | 低 | 开发测试推荐 |
| **Milvus** | 中等规模 | 中 | 生产推荐 |
| **Pinecone** | 大规模/云原生 | 低（托管） | 云部署推荐 |
| **Qdrant** | 中等规模 | 中 | 自托管推荐 |

### 6.3 配置示例

```yaml
# 向量存储配置（非必须，方案D）
vector_store:
  enabled: false                           # 默认关闭
  
  provider: "chroma"                       # chroma / milvus / pinecone / qdrant
  
  chroma:
    persist_directory: "./data/chroma"
    collection_name: "eduagents_knowledge"
    
  # 用于生成向量的嵌入模型
  embedding:
    provider: "openai"
    model: "text-embedding-3-small"
    dimension: 1536
```

---

## 7. 监控与可观测性

### 7.1 日志方案

| 组件 | 技术选型 | 说明 |
|-----|---------|------|
| **结构化日志** | Structlog | 统一日志格式 |
| **日志输出** | JSON + stdout | 便于收集 |
| **日志聚合** | ELK Stack / Loki | 可选生产配置 |
| **链路追踪** | OpenTelemetry | 分布式追踪 |

### 7.2 日志配置

```yaml
logging:
  version: 1
  level: "INFO"
  format: "json"                            # json / text
  
  structlog:
    processors:
      - "add_log_level"
      - "add_timestamp"
      - "add_logger_name"
      - "add_trace_id"
      - "hash_chain"                        # FR-14: 结构化日志 hash-chain
      
    output:
      console:
        enabled: true
      file:
        enabled: true
        path: "./logs/eduagents.log"
        rotation: "daily"
        retention_days: 30
```

### 7.3 指标监控

| 指标类型 | 采集方式 | 存储 |
|---------|---------|------|
| **系统指标** | Prometheus client | Prometheus |
| **业务指标** | 自定义埋点 | PostgreSQL |
| **追踪数据** | OpenTelemetry | Jaeger |
| **审计日志** | 写入日志 + 数据库 | PostgreSQL |

---

## 8. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| 核心语言 | Python 3.11+ | LLM 生态成熟，异步支持好 |
| Agent 框架 | 自研为主 | 更好控制约束层集成 |
| 配置格式 | YAML + JSON | 人类可读，Git 友好 |
| 数据库 | SQLite → PostgreSQL | 开发轻量，生产可扩展 |
| 向量存储 | 默认关闭，方案D | 非核心功能，按需启用 |
| 日志格式 | 结构化 JSON | 便于聚合分析 |

---

## 9. 文件目录结构

```
eduagents/
├── harness/                              # L0: Harness 约束层
│   ├── template_engine.py
│   ├── schema_validator.py
│   └── ...
├── orchestration/                         # L1: 编排层
│   ├── workflow_engine.py
│   └── task_manager.py
├── knowledge/                            # L2: 知识层
│   ├── knowledge_network.py
│   └── decision_index.py
├── agents/                               # L3: Agent 层
│   ├── agent_runtime.py
│   └── tool_registry.py
├── api/                                   # L4: 人机协同层
│   └── v1/
├── ui/                                    # L5: 可视化层
│   └── src/
├── storage/                               # 存储层
│   ├── git/
│   ├── sqlite/
│   └── postgres/
├── config/                                # 配置
│   ├── llm_providers.yaml
│   ├── database.yaml
│   └── logging.yaml
└── docs/architecture/deployment/
    └── tech_stack.md                     # 本文档
```

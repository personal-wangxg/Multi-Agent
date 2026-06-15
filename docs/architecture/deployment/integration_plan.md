# 系统集成与部署计划

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-12（配置持久化）、FR-14（可观测性）

---

## 1. 设计目标

定义 EduAgents 框架各层组件的集成顺序、依赖关系和部署流程，确保：
- 各层按正确顺序集成
- 依赖关系清晰明确
- 部署流程可重复
- 测试策略完备

---

## 2. 集成顺序规划

### 2.1 各层优先级

| 层级 | 组件 | 集成优先级 | 依赖关系 |
|-----|------|-----------|---------|
| **L0** | Harness 约束层 | P0（最先） | 无 |
| **L2** | 知识网络 | P0 | L0（Harness 校验） |
| **L1** | 编排层 | P0 | L0, L2 |
| **L3** | Agent 层 | P0 | L0, L1, L2 |
| **L4** | 人机协同层 | P1 | L0, L1, L2, L3 |
| **L5** | 可视化层 | P2 | L4 |

### 2.2 集成阶段划分

```
阶段 1：核心层（基础设施 + 知识 + 编排）
        │
        ├── 1.1 Harness 约束层
        ├── 1.2 知识网络管理
        └── 1.3 任务编排引擎

阶段 2：Agent 层
        │
        └── 2.1 Agent 运行时

阶段 3：人机协同层
        │
        ├── 3.1 反馈处理
        └── 3.2 API 服务

阶段 4：可视化层（可选）
        │
        ├── 4.1 Web API
        └── 4.2 前端 UI
```

---

## 3. 各层集成详情

### 3.1 阶段 1.1：Harness 约束层集成

#### 3.1.1 集成步骤

| 步骤 | 内容 | 验证方式 |
|-----|------|---------|
| 1 | 引入 Jinja2 模板引擎 | 模板渲染测试 |
| 2 | 实现 Schema 校验器 | 校验用例测试 |
| 3 | 实现工具白名单管理器 | 权限校验测试 |
| 4 | 实现反馈闭环模块 | 反馈处理流程测试 |
| 5 | 集成日志模块（hash-chain） | 日志格式验证 |
| 6 | 端到端 Harness 执行测试 | 完整约束流程测试 |

#### 3.1.2 依赖组件

| 组件 | 版本要求 | 来源 |
|-----|---------|------|
| Python | >= 3.11 | 系统依赖 |
| Jinja2 | >= 3.1 | PyPI |
| jsonschema | >= 4.17 | PyPI |
| Pydantic | >= 2.0 | PyPI |
| Structlog | >= 23.0 | PyPI |

#### 3.1.3 集成检查点

```
✓ 模板引擎支持动态变量注入
✓ Schema 校验器能检测所有定义的错误类型
✓ 工具白名单能正确拦截未授权调用
✓ 反馈闭环能将教师反馈转化为模板更新
✓ 日志输出符合 hash-chain 结构化格式
```

### 3.2 阶段 1.2：知识网络管理集成

#### 3.2.1 集成步骤

| 步骤 | 内容 | 验证方式 |
|-----|------|---------|
| 1 | 实现节点/边数据模型（Pydantic） | 模型校验测试 |
| 2 | 实现知识网络 CRUD 操作 | API 测试 |
| 3 | 集成 Git 版本管理 | Git 操作测试 |
| 4 | 实现决策索引更新器 | 索引生成测试 |
| 5 | 与 Harness 集成（节点/边 Schema 校验） | 联合测试 |

#### 3.2.2 依赖组件

| 组件 | 版本要求 | 来源 |
|-----|---------|------|
| NetworkX | >= 3.0 | PyPI |
| GitPython | >= 3.1 | PyPI |
| PyYAML | >= 6.0 | PyPI |

#### 3.2.3 集成检查点

```
✓ 节点 ID 命名符合 {domain}_{topic}_{layer}_{seq} 规范
✓ 边关系类型支持 5 种基础类型
✓ 知识网络支持 YAML/JSON 序列化
✓ Git 提交能自动生成 DP 并更新索引
✓ 与 Harness Schema 校验集成
```

### 3.3 阶段 1.3：任务编排层集成

#### 3.3.1 集成步骤

| 步骤 | 内容 | 验证方式 |
|-----|------|---------|
| 1 | 实现任务状态机 | 状态转换测试 |
| 2 | 实现工作流引擎（asyncio） | 并发执行测试 |
| 3 | 实现消息队列 | 消息投递测试 |
| 4 | 集成 Harness（模板加载、输出校验） | 联合测试 |
| 5 | 集成知识网络（读取 DP） | DP 注入测试 |

#### 3.3.2 集成检查点

```
✓ 任务状态机能正确追踪 pending→running→completed/failed
✓ 工作流引擎支持并行/串行任务执行
✓ 决策索引摘要能正确注入到 Agent context
✓ Harness 校验结果能触发重试或人工干预
```

### 3.4 阶段 2：Agent 层集成

#### 3.4.1 集成步骤

| 步骤 | 内容 | 验证方式 |
|-----|------|---------|
| 1 | 实现 Agent 运行时框架 | 框架测试 |
| 2 | 集成 LLM 提供商（OpenAI/Anthropic） | API 调用测试 |
| 3 | 实现工具注册与调用机制 | 工具调用测试 |
| 4 | 集成 Harness 约束（提示词注入、输出校验） | 联合测试 |
| 5 | 端到端 Agent 执行测试 | 完整流程测试 |

#### 3.4.2 集成检查点

```
✓ Agent 能正确加载 Harness 约束的提示词模板
✓ Agent 输出能通过 Harness 三阶段校验
✓ 工具调用能通过白名单校验
✓ Agent 能读取决策索引摘要并保持一致
```

### 3.5 阶段 3：人机协同层集成

#### 3.5.1 集成步骤

| 步骤 | 内容 | 验证方式 |
|-----|------|---------|
| 1 | 实现 FastAPI REST API | API 端点测试 |
| 2 | 实现 WebSocket 实时通信 | 消息推送测试 |
| 3 | 实现 5 种反馈操作处理 | 反馈处理测试 |
| 4 | 集成编排层（任务状态同步） | 联合测试 |
| 5 | 集成日志模块（可观测性 API） | 日志查询测试 |

#### 3.5.2 集成检查点

```
✓ 教师能通过 API 审批/打回阶段产物
✓ WebSocket 能实时推送任务状态变更
✓ 5 种反馈操作（approve/revise/reject/delay/approve_with_comments）均正常工作
✓ 执行日志和审计追踪可查询
```

### 3.6 阶段 4：可视化层集成（P2 可选）

#### 3.6.1 集成步骤

| 步骤 | 内容 | 验证方式 |
|-----|------|---------|
| 1 | 实现 Web API（对接 L4） | API 对接测试 |
| 2 | 实现前端 React 项目结构 | 组件渲染测试 |
| 3 | 实现课程规划工作流界面 | E2E 测试 |
| 4 | 实现知识网络可视化编辑器 | 可视化测试 |
| 5 | 实现教师工作区仪表板 | 功能测试 |

#### 3.6.2 集成检查点

```
✓ Web API 能正确代理 L4 人机协同层 API
✓ 知识网络可视化能正确渲染三层结构
✓ 教师能在界面上完成审批操作
✓ 仪表板能显示任务状态和待办事项
```

---

## 4. 依赖关系详解

### 4.1 层间依赖

```
┌─────────┐
│   L5    │ ← 可选，可独立于 L4 存在
└────┬────┘
     │ REST/WebSocket
     ▼
┌─────────┐
│   L4    │ ← 依赖 L0, L1, L2, L3
└────┬────┘
     │ API 调用
     ▼
┌─────────┐
│   L3    │ ← 依赖 L0, L1, L2
└────┬────┘
     │ Harness 约束
     ▼
┌─────────┐
│   L1    │ ← 依赖 L0, L2
└────┬────┘
     │ 任务下发/结果收集
     ▼
┌─────────┐
│   L0    │ ← 基础层，无依赖
└─────────┘
     ▲
     │
┌─────────┐
│   L2    │ ← 可独立验证
└─────────┘
```

### 4.2 组件依赖矩阵

| 组件 | 依赖组件 | 依赖类型 |
|-----|---------|---------|
| Harness 执行引擎 | 模板引擎、Schema 校验器、工具白名单 | 内部调用 |
| 工作流引擎 | asyncio、消息队列 | 异步任务 |
| Agent 运行时 | LLM SDK、Harness 引擎 | 模型调用、约束注入 |
| FastAPI 服务 | Pydantic、SQLAlchemy、WebSocket | API 框架 |
| 知识网络 | GitPython、NetworkX | 图计算、版本管理 |

---

## 5. 部署流程

### 5.1 开发环境部署

```bash
# 1. 克隆代码仓库
git clone https://github.com/eduagents/core.git
cd eduagents

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入必要的 API Key

# 5. 初始化数据库（SQLite 开发）
python -m eduagents init-db

# 6. 启动开发服务器
python -m eduagents dev
```

### 5.2 生产环境部署

```bash
# 1. 服务器准备
# - Ubuntu 22.04 LTS
# - 最低配置: 2 CPU, 4GB RAM
# - 推荐配置: 4 CPU, 16GB RAM

# 2. 安装系统依赖
apt update && apt upgrade -y
apt install -y python3.11 python3.11-venv git docker.io

# 3. 部署应用
git clone https://github.com/eduagents/core.git /opt/eduagents
cd /opt/eduagents
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. 配置（使用环境变量或 Vault）
export OPENAI_API_KEY="your-api-key"
export DATABASE_URL="postgresql://user:pass@localhost/eduagents"

# 5. 数据库迁移
python -m eduagents migrate

# 6. 启动服务（使用 systemd 或 docker-compose）
systemctl start eduagents

# 7. 验证部署
curl http://localhost:8000/health
```

### 5.3 Docker 部署（推荐）

```yaml
# docker-compose.yml
version: '3.8'

services:
  eduagents:
    image: eduagents/core:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/eduagents
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./config:/app/config
      - ./data:/app/data

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=eduagents
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

```bash
# 启动命令
docker-compose up -d
```

---

## 6. 测试策略

### 6.1 测试分层

| 测试层级 | 覆盖范围 | 测试工具 | 执行频率 |
|---------|---------|---------|---------|
| **单元测试** | 各组件内部逻辑 | pytest | 每次提交 |
| **集成测试** | 层间接口交互 | pytest + Testcontainers | 每日 |
| **E2E 测试** | 完整业务流程 | Playwright / Selenium | 每周 |
| **压力测试** | 高并发场景 | Locust | 每月 |

### 6.2 单元测试覆盖要求

| 组件 | 覆盖率要求 | 关键测试点 |
|-----|----------|----------|
| Harness 模板引擎 | >= 90% | 变量注入、模板版本 |
| Schema 校验器 | >= 95% | 各错误类型检测 |
| 知识网络 CRUD | >= 90% | 节点/边操作、版本管理 |
| 任务状态机 | >= 95% | 状态转换、边界条件 |
| Agent 运行时 | >= 80% | 工具调用、约束校验 |

### 6.3 关键集成测试用例

| 用例 ID | 用例描述 | 前置条件 | 预期结果 |
|---------|---------|---------|---------|
| INT-001 | 完整课程规划流程 | Harness+L1+L2+L3 集成 | 各阶段产物正确生成 |
| INT-002 | 教师反馈更新知识网络 | 人机协同层集成 | DP 更新、Wiki 生成 |
| INT-003 | Agent 输出校验失败重试 | Harness+L3 集成 | 最多重试3次后触发人工 |
| INT-004 | 决策索引摘要注入 | L1+L2 集成 | 上下文 Token 受控 |
| INT-005 | 并发任务执行 | L1 编排层 | 任务正确隔离 |

### 6.4 测试执行命令

```bash
# 运行所有测试
pytest tests/ -v

# 运行单元测试
pytest tests/unit/ -v

# 运行集成测试
pytest tests/integration/ -v

# 运行带覆盖率测试
pytest tests/ --cov=eduagents --cov-report=html

# 运行 E2E 测试
playwright test

# 运行压力测试
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

---

## 7. 部署检查清单

### 7.1 部署前检查

| 检查项 | 说明 | 验证方式 |
|-------|------|---------|
| 依赖版本 | 确认所有依赖版本兼容 | `pip check` |
| 配置完整性 | 确认所有必要配置项已填写 | 配置审计脚本 |
| 环境变量 | 确认 API Key 等敏感信息已配置 | 环境变量检查 |
| 存储准备 | 确认数据库、Git 仓库路径存在 | 路径验证 |
| 日志路径 | 确认日志输出目录可写 | 权限检查 |

### 7.2 部署后验证

| 检查项 | 说明 | 验证方式 |
|-------|------|---------|
| 服务启动 | 确认进程运行正常 | `ps aux \| grep eduagents` |
| 健康检查 | 确认 /health 端点返回 200 | `curl /health` |
| 数据库连接 | 确认能正常读写数据库 | 健康检查日志 |
| LLM 连接 | 确认能正常调用 LLM API | 测试 API 调用 |
| 日志输出 | 确认日志正常写入 | 检查日志文件 |

### 7.3 回滚方案

```bash
# 回滚到上一版本
git revert HEAD
pip install -r requirements.txt
python -m eduagents migrate --downgrade
systemctl restart eduagents

# 或者使用 Docker
docker-compose down
docker-compose -f docker-compose.backup.yml up -d
```

---

## 8. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| 集成顺序 | L0→L2→L1→L3→L4→L5 | 依赖关系决定，底层先验证 |
| 测试策略 | 单元→集成→E2E | 问题早发现，降低修复成本 |
| 部署方式 | Docker Compose（推荐） | 环境一致，部署简单 |
| 回滚策略 | Git revert + 数据库迁移 | 可重复、可验证 |
| 验证方式 | 健康检查端点 + 日志 | 快速定位问题 |

---

## 9. 文件目录结构

```
eduagents/
├── integration/                           # 集成测试
│   ├── test_harness.py
│   ├── test_knowledge_network.py
│   ├── test_orchestration.py
│   └── test_agent_runtime.py
├── deployment/                           # 部署配置
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── ansible/                           # 自动化部署
│   │   └── playbook.yml
│   └── scripts/
│       ├── init-db.sh
│       └── health-check.sh
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── requirements.txt                      # Python 依赖
└── docs/architecture/deployment/
    └── integration_plan.md              # 本文档
```

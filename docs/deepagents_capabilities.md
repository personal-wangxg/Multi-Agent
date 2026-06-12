# DeepAgents 核心能力

## 四层架构

### 1. 入口层（Harness）

- `create_deep_agent` 工厂函数，一行生成完整 Agent
- 内置系统提示词模板，规范思考/行动/输出格式

### 2. 核心能力层（四大支柱）

#### 显式规划（Planning）
- 内置 `write_todos`，把目标拆成待办列表
- 状态追踪：pending/in_progress/completed
- 每步审查 + 更新，失败调整计划而非盲目重试

#### 上下文管理（Context）
- **虚拟文件系统（VFS）**：`ls/read_file/write_file/edit_file`
- 大上下文卸载到文件，突破窗口限制
- 自动摘要：长会话自动压缩旧消息，降低 token 占用

#### 层级子 Agent（Subagents）
- `task` 工具生成独立上下文子 Agent
- 主 Agent 只做编排 + 汇总，避免上下文污染

#### 持久记忆（Memory）
- 基于 LangGraph Store/PostgreSQL
- 跨会话、跨线程保存状态、文件、偏好

### 3. 工具与执行层

- **Shell 执行**：沙箱（Modal/Deno/Daytona）中运行
- **MCP 协议**：接入任意 MCP Server
- **Skill 系统**：可复用能力包，固化经验

### 4. 生产运行时（Runtime）

- **持久化执行**：崩溃/部署后断点续跑
- **人机闭环**：关键操作人工审批/编辑/拒绝
- **可观测性**：日志、追踪、审计，全链路可查
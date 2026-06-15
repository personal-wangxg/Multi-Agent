# 可观测性与审计设计

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-14（可观测性与审计）

---

## 1. 设计目标

构建完整的可观测性体系，支持：
- Agent 执行过程追踪
- 运行状态可视化
- 审计回放
- Token 统计与预算管理
- 节点掌握历史追溯

| 设计原则 | 说明 |
|---------|------|
| **全面覆盖** | 记录所有关键操作和状态变化 |
| **结构化日志** | 统一日志格式，便于分析 |
| **实时监控** | 提供实时状态查询能力 |
| **可追溯性** | 支持完整执行过程回放 |

---

## 2. 架构组件

### 2.1 可观测性架构

```
┌─────────────────────────────────────────────────────────────────┐
│                       可观测性体系                             │
├─────────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   日志收集器  │────▶│   日志存储   │────▶│   日志查询   │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   指标收集器  │────▶│   指标存储   │────▶│   监控面板   │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   追踪收集器  │────▶│   追踪存储   │────▶│   审计回放   │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 组件职责

| 组件 | 职责 | 核心功能 |
|-----|------|---------|
| **日志收集器** | 收集 Agent 执行日志 | 结构化日志输出、日志级别控制 |
| **日志存储** | 持久化日志数据 | 按时间索引、支持查询 |
| **日志查询** | 查询和分析日志 | 关键词搜索、时间范围过滤 |
| **指标收集器** | 收集性能指标 | Token 使用、执行时间、成功率 |
| **指标存储** | 持久化指标数据 | 时序数据存储 |
| **监控面板** | 可视化监控 | 实时状态、趋势图表 |
| **追踪收集器** | 收集执行追踪 | 分布式追踪、链路分析 |
| **追踪存储** | 持久化追踪数据 | 完整执行链路存储 |
| **审计回放** | 回放执行过程 | 按时间轴回放、状态还原 |

---

## 3. 日志系统设计

### 3.1 日志结构

```yaml
log_entry:
  log_id: "log_001"
  timestamp: "2026-06-12T10:05:00Z"
  level: "INFO"                    # DEBUG / INFO / WARN / ERROR
  source: "agent_scene001_planner"
  category: "execution"            # execution / validation / tool_call / feedback
  
  # 上下文信息
  context:
    session_id: "sess_001"
    conversation_id: "conv_001"
    agent_id: "agent_scene001_planner_001"
    task_id: "task_course_plan_001"
  
  # 日志内容
  message: "开始执行课程规划任务"
  
  # 详细数据
  details:
    action: "start_task"
    input: { "course_name": "初三数学", "total_periods": 12 }
    output: null
    duration_ms: 0
  
  # 错误信息（如有）
  error:
    type: null
    message: null
    stack_trace: null
```

### 3.2 日志分类

| 分类 | 内容 | 示例 |
|-----|------|------|
| **execution** | Agent 执行过程 | 任务开始/结束、状态变化 |
| **validation** | Harness 校验结果 | Schema 校验通过/失败 |
| **tool_call** | 工具调用记录 | 读取文件、写入文件 |
| **feedback** | 教师反馈 | 评分、批注、拒绝理由 |
| **memory** | 记忆操作 | LTM 检索、WM 写入 |
| **token** | Token 使用 | Token 消耗统计、预算告警 |

---

## 4. 指标系统设计

### 4.1 核心指标

| 指标类别 | 指标名称 | 说明 | 单位 |
|---------|---------|------|------|
| **Token** | token_usage_total | 会话总 Token 消耗 | 个 |
| **Token** | token_usage_input | 输入 Token 消耗 | 个 |
| **Token** | token_usage_output | 输出 Token 消耗 | 个 |
| **Token** | token_budget_remaining | 剩余 Token 预算 | 个 |
| **性能** | execution_time_ms | 任务执行时间 | 毫秒 |
| **性能** | llm_call_count | LLM 调用次数 | 次 |
| **性能** | llm_call_duration_ms | LLM 调用耗时 | 毫秒 |
| **成功率** | task_success_rate | 任务成功率 | % |
| **成功率** | validation_pass_rate | 校验通过率 | % |
| **成功率** | tool_call_success_rate | 工具调用成功率 | % |
| **用户行为** | feedback_count | 教师反馈次数 | 次 |
| **用户行为** | feedback_positive_rate | 正面反馈率 | % |

### 4.2 指标收集频率

| 指标 | 收集频率 | 存储周期 |
|-----|---------|---------|
| Token 使用 | 每次 LLM 调用后 | 30天 |
| 执行时间 | 任务结束后 | 30天 |
| 成功率 | 每小时汇总 | 90天 |
| 教师反馈 | 每次反馈后 | 永久 |

---

## 5. 追踪系统设计

### 5.1 追踪数据结构

```yaml
trace_entry:
  trace_id: "trace_001"
  span_id: "span_001"
  parent_span_id: null
  
  # 时间信息
  start_time: "2026-06-12T10:05:00Z"
  end_time: "2026-06-12T10:06:30Z"
  duration_ms: 90000
  
  # 操作信息
  operation_name: "course_planning_stage1"
  operation_type: "task"            # task / tool_call / llm_call / validation
  
  # 相关实体
  agent_id: "agent_scene001_planner_001"
  session_id: "sess_001"
  task_id: "task_course_plan_001"
  
  # 输入输出
  input: { "course_name": "初三数学" }
  output: { "outline": {...} }
  
  # 状态
  status: "success"                 # success / failed / pending
  error_message: null
  
  # 子 span（嵌套操作）
  child_spans:
    - span_id: "span_002"
      operation_name: "validate_output"
      status: "success"
    - span_id: "span_003"
      operation_name: "write_file"
      status: "success"
```

### 5.2 追踪链路示例

```
trace_001 (course_planning)
    │
    ├─ span_001 (stage1: objectives)
    │       ├─ span_002 (llm_call: generate_objectives)
    │       └─ span_003 (validation: schema_check)
    │
    ├─ span_004 (stage2: structure)
    │       ├─ span_005 (llm_call: generate_structure)
    │       └─ span_006 (validation: completeness_check)
    │
    └─ span_007 (stage3: network)
            ├─ span_008 (llm_call: generate_network)
            ├─ span_009 (validation: edge_check)
            └─ span_010 (write_file: kn_stage3.yaml)
```

---

## 6. 审计回放设计

### 6.1 回放流程

```
请求回放
       │
       ▼
[读取追踪数据]
       │
       ▼
[按时间轴排序]
       │
       ▼
[重建状态]
       │
       ├─ 恢复 Agent 状态
       ├─ 恢复上下文内容
       └─ 恢复中间产物
       │
       ▼
[逐步骤回放]
       │
       ├─ 显示每个操作
       ├─ 显示输入输出
       └─ 显示耗时
```

### 6.2 回放控制

| 控制项 | 功能 |
|-------|------|
| 播放/暂停 | 控制回放进度 |
| 快进/慢放 | 调整回放速度 |
| 跳转到时间点 | 直接定位到特定时间 |
| 显示/隐藏详情 | 控制信息展示级别 |

---

## 7. Token 预算管理

### 7.1 预算配置

```yaml
token_budget:
  session_id: "sess_001"
  total_budget: 100000              # 会话总预算
  used_tokens: 15000                # 已使用
  remaining_tokens: 85000           # 剩余
  
  # 告警阈值
  warning_threshold: 0.8            # 80% 告警
  critical_threshold: 0.95          # 95% 暂停
  
  # 消费记录
  consumption_log:
    - timestamp: "2026-06-12T10:05:00Z"
      agent_id: "agent_scene001_planner_001"
      action: "llm_call"
      tokens_used: 3000
      reason: "生成课程大纲"
```

### 7.2 预算告警流程

```
每次 LLM 调用后
       │
       ▼
[更新 Token 使用量]
       │
       ▼
[检查阈值]
       │
       ├─ < 80% → 正常执行
       │
       ├─ 80% ~ 95% → 发送警告日志
       │              通知编排层
       │
       └─ ≥ 95% → 暂停 LLM 调用
                  通知教师
                  等待预算调整
```

---

## 8. 技术选型

| 组件 | 推荐技术 | 理由 |
|-----|---------|------|
| 日志收集 | Structlog | 结构化日志、灵活配置 |
| 日志存储 | Elasticsearch | 全文搜索、时序查询 |
| 指标收集 | Prometheus | 时序指标、灵活查询 |
| 指标展示 | Grafana | 可视化图表、告警 |
| 分布式追踪 | OpenTelemetry | 标准化追踪协议 |
| 追踪存储 | Jaeger | 分布式追踪存储与查询 |

---

## 9. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| 日志格式 | 结构化 JSON | 便于机器解析和查询 |
| 指标存储 | 时序数据库 | 支持时间序列分析 |
| 追踪协议 | OpenTelemetry | 标准化、可扩展 |
| Token 预算 | 会话级限制 | 控制成本、防止滥用 |
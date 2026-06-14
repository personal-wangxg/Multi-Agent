# 模块 05：非功能需求与记忆体系

**父文档**：[system_requirements.md](../system_requirements.md)
**相关决策**：[DP-ARCH-09](../decisions/dp_arch_09.md)（三层记忆） · [DP-ARCH-10](../decisions/dp_arch_10.md)（上下文控制） · [DP-ARCH-01](../decisions/dp_arch_01.md)（方案D）

---

## 5. 非功能需求

### 5.1 性能指标

| 指标 | 目标值 | 说明 |
|-----|--------|------|
| 场景识别响应时间 | ≤ 5 秒 | 从用户提交到产出推荐结果 |
| 配置生成响应时间 | ≤ 10 秒 | 完成初始 Agent 配置生成 |
| Agent 启动时间 | ≤ 30 秒 | 完成一次多 Agent 环境初始化 |
| 单会话并发 Agent 数 | ≥ 10 | 同时在线运行的 Agent 数量 |
| 运行稳定性 | ≥ 99% | 在正常运行时间内的任务成功率 |
| 记忆调取延迟 | ≤ 2 秒 | 从持久记忆检索一条相关信息的端到端延迟 |
| 单 Agent 输入上下文 Token 上限 | ≤ 模型窗口的 50% | 每个 Agent 每次调用 LLM 的输入 Token 不得超过模型上下文窗口的一半 |
| 全局上下文膨胀速率 | ≤ 5% / 轮 | 每轮 Agent 交互后，活动上下文 Token 增量不超过当前量的 5% |
| 跨会话记忆命中率 | ≥ 70% | 对重复出现的教学主题，能从持久记忆中检索到相关信息的比例 |
| Harness 输出校验通过率 | ≥ 95% | Agent 首次输出即通过结构化校验的比例（失败则由 Harness 自动重试） |
| Harness 校验延迟 | ≤ 500 ms | Harness 对单条 Agent 输出执行结构化/内容/权限校验的总耗时 |
| 未授权工具调用拦截率 | 100% | 不在白名单内的工具调用必须全部被 Harness 拦截，不得有漏网 |

### 5.2 可用性与易用性

| 需求项 | 目标 |
|--------|------|
| 配置门槛 | 教师无需编程背景即可完成基础配置 |
| 首次使用体验 | 新用户 15 分钟内完成首次教学场景生成 |
| 文档支持 | 提供完整的使用手册与示例场景库 |

### 5.3 可扩展性

| 需求项 | 说明 |
|--------|------|
| 新增场景类型 | 支持通过配置/插件方式新增第 6 类及以后的教学场景 |
| 新增 Agent 框架 | 协议层应预留扩展点，未来可集成其他 Agent 框架 |
| 模型接入 | 支持不同厂商 LLM API 的插拔式接入 |

### 5.4 安全性与合规

| 需求项 | 说明 |
|--------|------|
| 敏感信息保护 | API Key、用户数据不得以明文出现在日志或配置文件中 |
| 沙箱执行 | Agent 运行 Shell/代码时需在沙箱环境中执行 |
| 内容合规 | Agent 输出内容应符合教育场景合规要求（建议接入内容审核） |
| 数据隔离 | 不同用户的会话数据应严格隔离 |

### 5.5 可观测性

| 需求项 | 说明 |
|--------|------|
| 日志级别 | 支持 debug / info / warn / error 四级日志 |
| 链路追踪 | 支持 OpenTelemetry 全链路追踪 |
| 监控指标 | 暴露任务成功率、响应时间、Token 消耗等核心指标 |

### 5.6 记忆与上下文管理

**功能描述**：在多 Agent 长链路协作中，必须保证记忆可被高效检索、上下文不随轮次无限膨胀，并始终控制在模型窗口安全范围内。本节给出具体的数据结构、计算公式与触发条件。

#### 5.6.1 三层记忆体系架构

```
┌─────────────────────────────────────────────────────────────┐
│                      长期记忆层 (LTM)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  向量数据库 (Vector Store)                           │   │
│  │  索引：course_topic × teacher_id × chapter_ref      │   │
│  │  内容：历史大纲、教案模板、教师偏好、成功配置快照    │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ▲                                   │
│                      检索结果（Top-K, K=3）                   │
└──────────────────────────┼─────────────────────────────────┘
                           │
┌──────────────────────────┼─────────────────────────────────┐
│                      工作记忆层 (WM)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  VFS 文件系统                                        │   │
│  │  路径：/sessions/{session_id}/working/               │   │
│  │  内容：中间产物 + Knowledge Wiki 页面 + Decision Index 决策索引表
│  │  摘要上限：≤ 300 Token / 文件                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ▲                                  │
│                      Agent 上下文引用                         │
└──────────────────────────┼─────────────────────────────────┘
                           │
┌──────────────────────────┼─────────────────────────────────┐
│                      短期记忆层 (STM)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  当前会话消息队列 (Message Queue)                     │   │
│  │  内容：Agent 间消息历史、最近 N 条对话、当前待办清单  │   │
│  │  淘汰策略：超过 MAX_STM_MESSAGES 条时触发压缩        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### 5.6.2 分层定义与存储规格

| 层次 | 存储位置 | 内容范围 | 生命周期 | 最大容量 |
|------|---------|---------|---------|---------|
| **短期记忆 STM** | Agent 实例内存 / 消息队列 | 当前会话内所有 Agent 消息、当前 write_todos 状态、最近 LLM 调用输入/输出 | 会话内，退出后清除 | MAX_STM_MESSAGES = 50 条消息，或 ≤ 8192 Token（取两者较小值） |
| **工作记忆 WM** | VFS 文件系统 `/sessions/{id}/working/` + `/wiki/` + `/data/` | 各 Agent 生成的中间产物 + Knowledge Wiki 页面 + Decision Index 决策索引表 + 完整阶段产物文件 | 会话结束后 Wiki/决策索引永久保留，中间产物保留默认 7 天 | WM 文件 ≤ 4096 Token；Decision Index ≤ 300 Token；Wiki 页面 ≤ 2000 Token |
| **长期记忆 LTM** | 向量数据库（如 ChromaDB / PGVector） | 历史大纲、教案模板、教师反馈、成功配置快照、最佳 Agent 组合 | 永久保留（教师可手动删除） | 无硬性限制，按向量维度 × 数量估算 |

#### 5.6.3 Token 计算与上下文窗口控制

**Token 计算公式**

```
input_tokens = tokens(system_prompt)
             + tokens(current_todos)
             + tokens(messages[-N:])     # 最近 N 条消息，N 由压缩状态决定
             + tokens(retrieved_memories) # 从 LTM 检索注入的记忆片段
             + tokens(mid_products_refs)  # 中间产物路径 + 元摘要（≤ 300 Token）

safety_threshold = model_context_window * 0.5
llm_call_max_input = safety_threshold
```

**硬约束触发条件**

| 触发条件 | 阈值 | 动作 |
|---------|------|------|
| 任一 Agent 单次 LLM 调用输入 Token | > model_context_window × 50% | 拒绝调用，强制执行压缩流程（见 5.6.4） |
| 会话级 Token 预算 | ≥ 80% | 触发 WARNING 告警，写入日志，推送通知教师 |
| 会话级 Token 预算 | = 100% | 暂停所有 Agent，强制压缩至 60% 以下后恢复 |
| STM 消息数量 | > MAX_STM_MESSAGES (50) | 自动触发 STM→WM 压缩，写入 VFS 摘要，清空 STM |
| WM 单文件 Token | > 4096 | 自动分片为 `{filename}_part{N}.txt`，上下文仅引用路径 |

**示例（以通义千问 Qwen-Max，context_window = 128K Token 为例）**

```
safety_threshold = 128000 * 0.5 = 64000 Token
llm_call_max_input = 64000 Token

场景：SCENE-001 课程规划，运行至第 15 轮时：
  system_prompt (模板): 2000 Token
  current_todos: 150 Token
  messages[-50:]: 28000 Token
  retrieved_memories: 3 * 500 = 1500 Token
  mid_product_refs: 2 * 300 = 600 Token
  ─────────────────────────────────
  total = 32250 Token ✓ 通过，可在阈值内调用 LLM

若 messages[-50:] = 55000 Token：
  total = 59500 Token > 64000 → 触发强制压缩
```

#### 5.6.4 上下文压缩策略（优先级排序）

压缩由编排层在 LLM 调用前主动触发，执行以下优先级策略：

**策略 A：中间产物卸载（最高优先级，执行速度最快）**

```
触发条件：total_tokens > safety_threshold - 4096

操作：
  1. 识别总 Token > 4096 的中间产物文件
  2. 生成元摘要（prompt: "请将以下内容压缩为 ≤ 300 Token 的摘要，包含核心结论和关键数据"）
  3. 元摘要写入上下文，中间产物全文写入 VFS
  4. 在上下文中保留引用格式：[{file_path}, summary: "..."]

上下文格式变更：
  - 压缩前：mid_product_content: "这里是2000字的大纲草案全文..."
  - 压缩后：mid_product_ref: "/sessions/s001/working/outline_draft.md", summary: "大纲共3章，覆盖概念引入、配方法..."（≤300 Token）
```

**策略 B：STM 压缩（次优先级）**

```
触发条件：策略 A 执行后 total_tokens 仍 > safety_threshold

操作：
  1. 将当前消息队列中的旧消息写入 WM（VFS）：/sessions/{id}/working/stm_archive_turn_{N}.txt
  2. 保留最近的消息子集（保留量 = safety_threshold 剩余空间 / 平均消息 Token）
  3. 插入压缩摘要消息："[以下为历史对话摘要：{LLM_generated_summary}]"
```

**策略 C：LTM 检索结果裁剪（最低优先级）**

```
触发条件：策略 A+B 执行后 total_tokens 仍 > safety_threshold

操作：
  1. 按 relevance_score 从低到高裁剪 LTM 检索结果
  2. 优先保留 Top-1 最高相关记忆，裁剪其余
  3. 若仍超限，放弃 LTM 注入本次调用
```

**降级路径（策略全部失败）**

```
触发条件：压缩后 total_tokens > safety_threshold 且无法继续压缩

操作：
  1. 暂停 Agent 运行，不发起 LLM 调用
  2. 推送告警给教师："上下文已达上限，当前 Agent 无法继续执行，请手动清理或保存进度"
  3. 教师可选择：(a) 手动批准继续（强制截断），(b) 保存进度并关闭会话
```

#### 5.6.5 长期记忆（LTM）检索与索引规格

**向量索引结构**

```yaml
collection_name: "eduagents_memory"
embedding_model: "text-embedding-3-small"  # 或其他兼容模型
dimension: 1536
index_type: "HNSW"                          # Hierarchical NSW，近似最近邻

metadata_schema:
  - field: "course_topic"
    type: "string"                           # 精确过滤
    filterable: true
  - field: "chapter_ref"
    type: "string"
    filterable: true
  - field: "teacher_id"
    type: "string"
    filterable: true
  - field: "scene_type"
    type: "string"                           # SCENE-001 ~ SCENE-005
    filterable: true
  - field: "created_at"
    type: "datetime"
    sortable: true
  - field: "rating"
    type: "float"                            # 教师评分 0.0~1.0，过滤高质量记忆
    filterable: true
    range: [0.0, 1.0]
  - field: "dp_ids"
    type: "array[string]"                    # 该记忆条目中包含的决策点 ID 列表。用于跨任务时按 DP 精确检索相关记忆
    filterable: true
    example: ["DP-S1-01", "DP-S1-05", "DP-S2-02"]

retrieval_config:
  mode: "hybrid"                             # 向量相似度 + 关键词过滤
  vector_weight: 0.6
  keyword_weight: 0.4
  top_k: 3                                   # 每次最多注入 3 条记忆
  min_relevance_score: 0.6                   # relevance < 0.6 的结果丢弃
  max_total_tokens: 1500                      # 注入上下文不超过 1500 Token
```

**检索流程**

```
1. 构建检索 Query
   query_text = f"当前任务：{scene_type}，章节：{chapter_ref}，教学主题：{course_topic}"

2. 混合检索（向量 + 关键词）
   results = vector_db.query(
       query_text,
       filter={"teacher_id": teacher_id, "scene_type": scene_type},
       top_k=5
   )

3. 重排序与过滤
   filtered = [r for r in results if r.score >= min_relevance_score]
   deduped = deduplicate_by_content(filtered)
   final = deduped[:top_k]

4. Token 控制
   total_memory_tokens = sum(tokens(r.content) for r in final)
   if total_memory_tokens > max_total_tokens:
       final = truncate_by_tokens(final, max_total_tokens)

5. 注入上下文
   memory_section = "【相关历史经验】\n" + "\n".join(f"- {r.content}" for r in final)
   append_to_system_prompt(memory_section)
```

#### 5.6.6 记忆写入时机与内容规范

| 时机 | 写入内容 | 目标层 | 示例 |
|-----|---------|-------|------|
| 会话正常完成 | 关键结论 + 教师最终评分 + 成功配置快照 | LTM | `{"content": "课程规划成功，10课时分配：3+3+4...", "scene_type": "SCENE-001", "rating": 0.9}` |
| 会话异常中断 | 已完成部分 + 中断原因 + 教师反馈（如有） | WM（临时） | `/sessions/s002/interrupted.md` |
| 教师评分/反馈 | 评分 + 反馈理由 + 被拒绝的 Agent 输出 | LTM（更新） | 同一 `memory_id` 的 `rating` 字段更新 |
| 配置保存 | 完整 Agent 配置 YAML + 模板版本 | LTM（配置模板库） | `/templates/user_saved/lesson_prep_v2.yaml` |
| 每日定时 | 会话统计（Token 消耗、成功/失败次数） | WM（日志） | `/logs/daily_stats/20260612.json` |

#### 5.6.7 分层记忆体系需求汇总

| 需求项 | 说明 |
|--------|------|
| 分层记忆体系 | 短期 / 工作 / 长期记忆三层，各层存储介质、生命周期、容量约束明确 |
| 记忆检索策略 | 长期记忆需支持向量相似度检索 + 结构化关键词过滤，优先返回与当前任务最相关的片段 |
| 上下文窗口控制（硬约束） | 每个 Agent 在发起 LLM 调用前，必须计算当前输入 Token 数；若超过"模型窗口 × 50%"，需执行压缩/截断/卸载，确保在安全阈值内再发起调用 |
| 上下文压缩策略 | 至少实现：(a) 摘要重写——由 LLM 将长对话重写为简明摘要；(b) 旧消息遗忘——按时间或 relevance 淘汰最早消息；(c) 文件卸载——将大段中间产物写入 VFS/文件，仅在上下文中保留引用 |
| 上下文精简原则 | 进入上下文的信息应遵循"必要且精简"——禁止将原始 VFS 文件全文、超长中间产物或未过滤历史直接拼入上下文 |
| 中间产物卸载 | Agent 生成的长文本（如章节教案、长报告、代码块）默认写入文件系统，上下文中仅保留文件路径 + 元摘要（≤ 300 Token） |
| Token 预算与告警 | 每个会话应配置 Token 预算，接近 80% 时告警，达到预算上限时强制启动压缩流程并提示教师 |
| 记忆写入时机 | 会话完成/中断时，必须将关键结论、教师反馈、成功配置写入持久记忆，供下次同主题任务复用 |

### 5.7 Harness 约束有效性

**功能描述**：Harness 不仅是接口层的装饰，必须作为 Agent 执行流中的强制环节，确保每一次 LLM 调用与工具调用都在约束范围内。

| 需求项 | 说明 |
|--------|------|
| 提示词模板不可绕过 | Agent 实例必须由模板工厂创建，模板注入 system prompt 后即锁定；Agent 无法通过自身推理修改或绕过模板约束 |
| 输出校验强制前置 | Agent 输出必须先经过 Harness 校验管道（schema → 内容边界 → 长度/格式），校验通过后方可流入下游环节或交付用户 |
| 待办清单驱动 | Agent 的任务推进必须基于 write_todos 生成的待办清单；每一步执行需标记对应 todo 项，清单外的行动视为无效 |
| 工具调用权限强制校验 | Harness 在工具调用前执行白名单校验 + 参数合法性校验；拒绝调用时向 Agent 返回明确错误信息并记录审计 |
| 偏离检测 | 当 Agent 连续 2 次输出偏离当前任务主题或违反禁止事项时，Harness 应自动重置该 Agent 的内部状态并重新加载模板 |
| 教师反馈回写 | 教师对 Agent 输出的评分、批注、拒绝理由必须回写入 Harness 反馈池，用于下一轮重生成或模板迭代 |
| 模板版本管理 | 提示词模板 / 校验 schema / 权限配置支持版本化，便于 A/B 测试与效果追溯 |

### 5.8 技术约束

| 约束项 | 说明 |
|--------|------|
| 编程语言 | Python 3.10+ |
| Agent 框架 | 必须集成 DeepAgents 与 AgentScope |
| 配置格式 | YAML / JSON |
| 前端（可选） | React 或 Vue |
| 接口层（可选） | FastAPI |

---


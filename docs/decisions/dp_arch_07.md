# DP-ARCH-07：Harness 约束层

**确认日期**：2026-06-12 · **确认人**：项目核心团队 · **决策类别**：架构

---

## 决策摘要

Harness（驾驭层）是确保所有 Agent 行为与输出被严格约束在需求范围内的核心机制。通过提示词模板、任务待办清单、结构化输出 Schema、工具白名单与反馈闭环，Agent 的输出必须经由三阶段校验管道（Schema 校验 → 内容边界过滤 → 任务完整性检查）。校验失败触发自动重试（≤3 次），超过阈值触发人工干预。未授权工具调用拒绝率 = 100%，结构化输出合规率 ≥ 95%。

## 核心设计原则

1. **三阶段校验：Schema → 内容边界 → 任务完整性，顺序不可调换，
2. **提示词模板锁定：6 区块模板中的 5 个为锁定区块，Agent 推理不可覆盖，
3. **工具白名单 + 参数约束双保险：白名单外工具 100% 拦截，白名单内工具参数仍受 pattern 校验，
4. **反馈闭环持续优化：教师反馈触发模板版本化，
5. **失败重试上限：单 Agent 同一校验失败最多 3 次，后触发人工干预。

## 关键细节

### 6 区块提示词模板（system_requirements.md §4.10.1）

| 区块编号 | 区块名称 | 是否锁定 | 关键内容 |
|---------|---------|---------|---------|
| 区块 1 | role_definition | 锁定 | role / specialty / tone |
| 区块 2 | task_scope | 锁定 | must_do / must_not_do |
| 区块 3 | output_format | 锁定 | format / schema_ref / max_output_tokens |
| 区块 4 | prohibited_topics | 锁定 | 禁止话题清单 |
| 区块 5 | todo_template | 锁定，绑定 write_todos | id / label / description / required |
| 区块 6 | dynamic_injection | 不锁定 | system_variables / retrieved_memories |

### 三阶段校验管道（system_requirements.md §4.10.3）

```
Agent 输出
   │
   ▼
[阶段1：Schema 校验]
   ├── JSON parse 检查
   ├── 必填字段检查（required fields）
   ├── 类型检查
   ├── 数值范围检查
   ├── 枚举值检查
   └── 自定义规则检查
         │
         ├─ PASS → [阶段2]
         └─ FAIL → 重试（≤3次），记录失败原因
                     │
                     ▼
               3次失败 → 人工干预告警

[阶段2：内容边界过滤]
   ├── 禁止话题检查（prohibited_topics）
   ├── 关键词过滤（自定义词表）
   ├── 长度上限检查（max_output_tokens）
   └── 主题相关性检查（与 {course_topic} 语义相似度 < 0.3 则告警）
         │
         ├─ PASS → [阶段3]
         └─ FAIL → 触发重生成，记录过滤原因

[阶段3：任务完整性检查]
   ├── 待办清单覆盖率（items_covered / total_items >= 100%）
   ├── 结构一致性（如 sum(chapters.periods) ≈ total_periods ±1）
   └── 无新增禁止任务（Agent 未自行新增模板范围外任务）
         │
         ├─ PASS → 交付
         └─ FAIL → 触发针对性补充或重生成
```

### 工具白名单（system_requirements.md §4.10.4）

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
          required: true
          pattern: "^/sessions/.*\\.md$"
```

### 指标目标

| 指标 | 目标值 | 说明 |
|-----|--------|------|
| 未授权工具调用拒绝率 | 100% | 白名单外工具一律拒绝 |
| 结构化输出合规率 | ≥ 95% | 通过三阶段校验的输出比例 |
| 单失败重试上限 | 3 次 | 超过触发人工干预 |
| 任务待办完成率 | 100% | write_todos items_covered = total_items |

## 影响范围

- 关联 FR：FR-15（Harness 约束层）；
- 关联场景：全部 SCENE-001~009；
- 关联决策：DP-ARCH-06（FR 基线）、DP-ARCH-10（上下文窗口控制）。

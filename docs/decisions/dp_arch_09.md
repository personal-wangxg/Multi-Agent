# DP-ARCH-09：三层记忆体系

**确认日期**：2026-06-12 · **确认人**：项目核心团队 · **决策类别**：架构

---

## 决策摘要

系统采用**短期记忆（STM）→ 工作记忆（WM）→ 长期记忆（LTM）**三层架构管理 Agent 的记忆与知识。STM 为会话级内存与消息队列；WM 为 VFS 文件系统（中间产物 + Knowledge Wiki + 决策索引表）；LTM 为向量数据库（历史大纲/教案模板/教师反馈/成功配置快照）。**决策索引是 WM 与 LTM 的桥梁**，在 WM 中持久化并可增量写入 LTM。

## 核心设计原则

1. **分层递增：STM 负责即时消息 → WM 负责当前任务结构化产物 → LTM 负责跨任务复用，
2. **决策索引作为桥梁：WM 中的 decision_index.json 可提取摘要写入 LTM，
3. **主动读取替代被动注入：WM 中完整产物由 Agent 通过 `read_wiki(path)` / `read_yaml(path)` 主动读取，
4. **Git 版本管理：WM 产物由 Git 仓库管理，支持 diff、回滚、分支，
5. **Token 预算分层约束：不同层级的 Token 注入上限不同（见 DP-ARCH-10）。

## 关键细节

### 三层架构总览

```
┌────────────────────────────────────────────────────────────┐
│ STM（短期记忆）                                           │
│   · 存放位置：Agent 实例内存 / Message Hub 消息队列       │
│   · 内容：当前会话内的即时消息、LLM 对话历史              │
│   · 生命周期：会话级，任务结束后不保留                     │
│   · 控制目标：受上下文窗口 50% 硬约束（见 DP-ARCH-10）   │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ WM（工作记忆）                                             │
│   · 存放位置：VFS（Virtual File System）                   │
│   · 内容 1：当前任务中间产物（kn_stage{N}.yaml 等）        │
│   · 内容 2：Knowledge Wiki 页面（Markdown，Git 管理）     │
│   · 内容 3：决策索引表 decision_index.json                │
│   · 生命周期：当前任务全程，任务结束后归档                 │
│   · 单文件 Token 上限：≤ 4096 Token，按需分片             │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ LTM（长期记忆）                                           │
│   · 存放位置：向量数据库 + 结构化索引                    │
│   · 内容：历史课程大纲、教案模板、教师反馈偏好、          │
│           成功配置快照、跨任务决策索引摘要                │
│   · 生命周期：跨任务/跨课程可复用                        │
│   · 单次检索注入上限：≤ 1500 Token                       │
└────────────────────────────────────────────────────────────┘
```

### 决策索引作为 WM 与 LTM 桥梁（system_requirements.md §4.8.5）

```
任务启动：
  └→ 从 LTM 检索同主题决策索引摘要（≤ 1500 Token）
       └→ 注入当前任务 STM 上下文

任务进行中（阶段产物确认后）：
  └→ 编译 Agent 编译产物为 DP 条目 + Wiki 页面
       └→ 更新 WM 的 decision_index.json（增量更新）
            └→ 更新 WM 的 context_injection_summary（≤ 300 Token）

任务结束：
  └→ WM 产物归档
       └→ 决策索引摘要写入 LTM 供未来任务复用
```

### decision_index.json 关键结构

```yaml
decision_index:
  task_id: "task_course_plan_2026_06_12_001"
  last_updated: "2026-06-12T10:45:00Z"
  current_stage: "stage3_completed"
  dp_count: 12
  decisions:
    - dp_id: "DP-S1-01"
      category: "objective"
      content: "总课时 = 12"
    - dp_id: "DP-S1-02"
      category: "method"
      content: "教学方法 = 讲授法 + 探究法 + 项目引领"

  context_injection_summary:
    format: "bulleted_list"
    max_tokens: 300
    summary: |
      已确认决策（截至 stage3）：
      · 总课时12，面向初三学生
      · 教学方法：讲授法+探究法+项目引领
      · 课程结构：4个单元
      · 知识网络含概念/技能/工具三层，共6节点
      · 评估指标含课堂表现+书面作业+项目作品
```

### Knowledge Wiki 页面结构（Harness 约束格式）

```markdown
# {场景名称} · {阶段名称}

**版本**：v{N} · **编译时间**：{datetime} · **确认人**：{teacher_id}

## 概述
{该阶段完成的任务概述}

## 决策点（DP）汇总
| DP ID | 类别 | 内容 |
|-------|------|------|
| DP-xxx | {category} | {content} |

## 关键约束
{关键约束与边界条件}

## 风险与边界
{风险评估与边界情况，引用源文件}

## 相关页面
- [[wikilink 1]]
- [[wikilink 2]]
```

## 影响范围

- 关联 FR：FR-12（配置持久化）、FR-18（知识编译与决策索引）；
- 关联决策：DP-ARCH-10（上下文窗口控制）、DP-ARCH-07（Harness 校验 Wiki Schema）；
- 关联产物：decision_index.json、Knowledge Wiki 页面、VFS 中间产物文件。

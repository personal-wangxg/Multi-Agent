# 知识编译与决策索引系统设计

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-18（知识编译与决策索引系统）

---

## 1. 设计目标

解决多阶段/多场景长链路 Agent 协作中的**上下文膨胀问题**：

| 问题 | 解决方案 |
|-----|---------|
| 完整产物直接拼入上下文导致 Token 超限 | 仅注入极简决策索引（≤300 Token） |
| 中间信息被"Lost in Middle"稀释 | 决策点前置编译，而非查询时检索 |
| 知识无法复用与追溯 | Git 版本管理 + Knowledge Wiki |
| 决策不一致 | 决策点一经确认不可变更，版本化管理 |

---

## 2. 核心设计原则

| 原则 | 说明 |
|-----|------|
| **决策前置编译** | 教师确认阶段产物后立即编译，后续阶段直接消费已编译结果 |
| **决策点不可变更** | 一经确认即为不可变，修改通过迭代新方案生成新 DP |
| **上下文极简主义** | 仅注入决策索引摘要，详细信息按需主动读取 |
| **主动读取替代被动注入** | Agent 通过工具主动读取 Wiki 或完整产物 |
| **Git 版本管理** | Wiki 和产物文件由 Git 管理，支持 diff、回滚、分支 |
| **人类可读，LLM 可消费** | Wiki 页面用标准 Markdown 编写 |

---

## 3. 架构组件

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    知识编译与决策索引系统                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐     ┌──────────────────┐                  │
│  │   阶段产物输入    │────▶│   编译 Agent     │                  │
│  │  (已确认的YAML)   │     │                  │                  │
│  └──────────────────┘     └────────┬─────────┘                  │
│                                    │                            │
│          ┌─────────────────────────┼─────────────────────────┐  │
│          ▼                         ▼                         ▼  │
│  ┌──────────────┐        ┌──────────────┐        ┌──────────────┐│
│  │   DP 表      │        │ Knowledge   │        │ 决策索引     ││
│  │ (决策点表)    │        │   Wiki      │        │  (全局)      ││
│  └──────────────┘        └──────────────┘        └──────────────┘│
│          │                         │                         │   │
│          └─────────────────────────┼─────────────────────────┘   │
│                                    │                            │
│                                    ▼                            │
│                         ┌──────────────────┐                    │
│                         │    Git 仓库      │                    │
│                         │ (版本管理)       │                    │
│                         └──────────────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 编译 Agent 职责

| 步骤 | 输入 | 输出 | 约束 |
|-----|------|------|------|
| 1. 读取阶段产物 | 已确认的 `kn_stage{N}.yaml` | — | 必须读取教师已确认的产物 |
| 2. 提取决策点 | 完整产物中的关键决策信息 | DP 表 | 每个 DP 必须来自产物中的明确信息 |
| 3. 生成 Wiki 页面 | 完整产物 + DP 表 | `/wiki/{scene_type}/{stage_name}.md` | 页面格式由 Harness Schema 约束 |
| 4. 更新决策索引 | 已有全局决策索引表 | 合并后的全局 DP 索引 | 增量更新 |
| 5. Git 提交 | 新增/修改的文件 | 自动提交 | 提交前执行 Schema 校验 |

---

## 4. 数据模型

### 4.1 决策点（Decision Point）

```yaml
decision_point:
  dp_id: "DP-S1-03"              # 全局唯一：DP-{scene_abbr}-{3位序号}
  scene_type: "course_planning"
  stage: "stage1_objectives"
  category: "teaching_method"     # objective / method / structure / node / edge / evaluation / constraint
  content: "教学方法采用讲授法 + 探究法 + 项目引领"
  source_reference: "kn_stage1.yaml: teaching_methods[1].name"  # 源文件位置
  confirmed_by: "teacher_001"
  confirmed_at: "2026-06-12T10:15:00Z"
  is_immutable: true              # 一经确认不可修改
  revision: 1                     # 迭代版本
```

### 4.2 决策索引（Decision Index）

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
    # ... 更多 DP

  # 上下文注入摘要（自动生成）
  context_injection_summary:
    format: "bulleted_list"
    max_tokens: 300
    summary: |
      已确认决策（截至 stage3）：
      · 总课时12，面向初三学生
      · 教学方法：讲授法+探究法+项目引领
      · 课程结构：4个单元（引入/解法探究/建模/综合）
      · 知识网络含概念/技能/工具三层，共6个节点
      · 评估指标含课堂表现+书面作业+项目作品
```

### 4.3 Wiki 页面结构

```markdown
# 课程规划 · 阶段1：教学目标设计

**版本**：v1 · **编译时间**：2026-06-12T10:15:00Z · **确认人**：teacher_001

## 概述

本阶段完成「初中数学：一元二次方程」课程的教学目标设计，包括知识目标、能力目标、素质目标、预期学习成果、教学方法选择、学习效果检验方式。

## 决策点（DP）汇总

| DP ID | 类别 | 内容 |
|-------|------|------|
| DP-S1-01 | objective | 总课时 = 12 |
| DP-S1-02 | method | 教学方法 = 讲授法 + 探究法 + 项目引领 |
| DP-S1-03 | assessment | 检验方式 = 课堂小测 + 书面作业 + 项目作品 |
| ... | ... | ... |

## 关键约束

- 目标学生层次：初三
- 课程需体现分层教学理念（不同层次节点设计）
- 思政融合在备课阶段处理，本阶段不涉及具体思政内容

## 风险与边界

见完整产物 [kn_stage1.yaml](/data/kn_stage1.yaml) 中的风险评估部分。

## 相关页面

- [[课程规划-阶段2-课程结构]]
- [[课程规划-阶段3-知识网络]]
- [[备课辅助-单元教案]]
```

---

## 5. 编译流程

### 5.1 完整编译流程

```
教师确认阶段产物
       │
       ▼
[检查是否包含 teacher_confirmed: true 标记]
       │
       ├─ 否 → 拒绝编译，提示确认
       │
       ▼ 是
[提取决策点]
       │
       ├─ 遍历产物中的所有已确认字段
       ├─ 每个字段生成一个 DP 条目
       └─ 确保 DP content 与源文件逐字对应
       │
       ▼
[生成 Wiki 页面]
       │
       ├─ 按预设模板生成 Markdown
       ├─ 包含 DP 表格和关键约束
       └─ 添加 wikilink 链接
       │
       ▼
[更新全局决策索引]
       │
       ├─ 增量合并新 DP 条目
       ├─ 更新 context_injection_summary
       └─ 保持索引 ≤ 300 Token
       │
       ▼
[Schema 校验]
       │
       ├─ 校验 Wiki 页面格式
       └─ 校验决策索引结构
       │
       ▼
[Git 提交]
       │
       └─ message 格式："compile({scene} stage {N}): {summary}"
```

### 5.2 后续阶段使用决策索引的方式

```
Agent 启动
       │
       ▼
[编排层自动注入决策索引摘要]
       │
       ├─ 读取 decision_index.json
       ├─ 提取 context_injection_summary
       └─ 注入 Agent 的 system prompt（≈ 300 Token）
       │
       ▼
Agent 执行任务
       │
       ├─ [一致性检查] 核对方案与 DP 表是否一致
       │       └─ 冲突 → 请求教师确认
       │
       └─ [按需读取] 如需详细信息，调用工具读取 Wiki 或完整产物
       │
       ▼
当前阶段产物确认
       │
       └─ 触发编译 Agent 生成新 DP 和 Wiki 页面
```

---

## 6. 上下文窗口保障机制

| 机制 | 作用 | 控制目标 |
|-----|------|---------|
| 决策索引摘要 | 替代完整产物拼入上下文 | ≤ 300 Token（与阶段数无关） |
| WM 中间产物 | 完整产物仅存在于 VFS | 单文件 ≤ 4096 Token |
| LTM 长期记忆 | 跨任务复用的模板与偏好 | 单次检索注入 ≤ 1500 Token |
| Token 预检查 | LLM 调用前计算 Token 量 | 单 Agent 输入 ≤ 窗口 50% |

---

## 7. 与记忆体系的关系

```
┌────────────────────────────────────────────────────────────────┐
│                    决策索引与记忆体系关系                       │
├────────────────────────────────────────────────────────────────┤
│                                                               │
│   ┌─────────┐      ┌──────────────┐      ┌──────────┐         │
│   │ STM 会话 │ ───▶ │ WM: Wiki文件 │ ───▶ │ LTM:  │         │
│   │ 内存中  │      │ 产物+决策索引  │      │  向量检索 │         │
│   └─────────┘      └──────────────┘      └──────────┘         │
│                                                               │
│  · 决策索引在 WM 中持久化                                      │
│  · 跨任务时决策索引可被提取并写入 LTM 供长期复用                 │
│  · 新任务启动时，优先从 LTM 检索同主题决策索引摘要               │
│                                                               │
└────────────────────────────────────────────────────────────────┘
```

---

## 8. 核心接口

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `compile_stage_product(product_path)` | 编译阶段产物 | product_path: str | CompilationResult |
| `extract_decision_points(product)` | 提取决策点 | product: dict | DP 列表 |
| `generate_wiki_page(dp_list, product)` | 生成 Wiki 页面 | dp_list: list, product: dict | Wiki 内容 |
| `update_decision_index(new_dps)` | 更新决策索引 | new_dps: list | 更新后的索引 |
| `inject_context_summary(task_id)` | 获取上下文注入摘要 | task_id: str | summary: str |
| `validate_compilation(result)` | 校验编译结果 | result: CompilationResult | ValidationResult |

---

## 9. 文件目录结构

```
knowledge_compilation/
├── compiler/
│   ├── __init__.py
│   ├── dp_extractor.py          # 决策点提取器
│   ├── wiki_generator.py        # Wiki 页面生成器
│   ├── index_updater.py         # 决策索引更新器
│   └── git_integrator.py        # Git 集成模块
├── wiki/                        # Knowledge Wiki 目录
│   ├── course_planning/
│   │   ├── stage1_objectives.md
│   │   ├── stage2_structure.md
│   │   └── stage3_network.md
│   ├── lesson_prep/
│   │   └── ...
│   └── index.md
├── decision_index.json          # 全局决策索引
└── config/
    └── compiler_config.yaml
```

---

## 10. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| DP ID 命名 | `DP-{scene_abbr}-{NNN}` | 全局唯一，便于追溯 |
| 决策点不可变更 | 仅可通过新迭代废弃 | 保证决策一致性和可审计性 |
| 上下文注入 | 仅注入摘要（≤300 Token） | 控制上下文膨胀 |
| Wiki 格式 | 标准 Markdown + wikilink | 人类可读，LLM 可消费 |
| 版本管理 | Git | 支持 diff、回滚、协作 |
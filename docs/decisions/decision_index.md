# EduAgents 需求文档 · 决策索引（Decision Index）

**版本**：v1.0 · **最后更新**：2026-06-12 · **维护者**：项目核心团队

---

## 概述

本文档是 EduAgents 多 Agent 教学框架需求文档的**所有已确认决策点索引**。在后续修改需求文档、讨论新场景或调整架构时，**应首先读取本文件**（约 300-500 Token），而非直接加载 2,783 行的完整主文档。

本索引遵循方案D 设计原则：
- **决策前置编译**：教师确认后立即提取为决策点
- **决策点不可变更**：一经确认即为不可变，修改仅通过"迭代新方案"生成新 DP
- **上下文极简主义**：每次修改仅加载本索引（≈ 300 Token）+ 目标模块
- **主动读取替代被动注入**：如需了解决策详情，主动读取对应 dp_arch_*.md 文件

---

## 架构决策（Architecture Decisions）

| DP ID | 决策摘要 | 关键词 | 确认状态 | 详情页面 |
|-------|---------|--------|---------|---------|
| DP-ARCH-01 | 采纳方案D：知识编译 + 决策索引 + Knowledge Wiki + Git，不需要向量数据库 | knowledge-compilation, decision-index | ✅ 已确认 | [dp_arch_01.md](dp_arch_01.md) |
| DP-ARCH-02 | 9 个典型业务场景确认：SCENE-001~SCENE-009 | scenes, 9-scenes | ✅ 已确认 | [dp_arch_02.md](dp_arch_02.md) |
| DP-ARCH-03 | 课程规划采用三阶段设计：教学目标 → 课程结构 → 知识网络 | course-planning, three-stage | ✅ 已确认 | [dp_arch_03.md](dp_arch_03.md) |
| DP-ARCH-04 | 知识网络节点采用三层结构：概念层 / 技能层 / 工具层 | knowledge-network, three-layer | ✅ 已确认 | [dp_arch_04.md](dp_arch_04.md) |
| DP-ARCH-05 | 动态学习路径：非课前规划，由"节点掌握→推荐→学生选择→移动"迭代涌现 | dynamic-path, student-choice | ✅ 已确认 | [dp_arch_05.md](dp_arch_05.md) |
| DP-ARCH-06 | 18 个功能需求：FR-01~FR-18，FR-18 知识编译为 P0 架构需求 | functional-requirements, 18-FR | ✅ 已确认 | [dp_arch_06.md](dp_arch_06.md) |
| DP-ARCH-07 | Harness 约束：每个 Agent 输出必须通过结构化 Schema 校验 | harness, schema-validation | ✅ 已确认 | [dp_arch_07.md](dp_arch_07.md) |
| DP-ARCH-08 | 思政融合：在备课阶段设计，Agent 提出"在哪个节点/融什么/如何融" | ideological-political, lesson-prep | ✅ 已确认 | [dp_arch_08.md](dp_arch_08.md) |
| DP-ARCH-09 | 三层记忆体系：STM（短期） + WM（工作） + LTM（长期），决策索引是 WM 与 LTM 桥梁 | memory-system, three-layer | ✅ 已确认 | [dp_arch_09.md](dp_arch_09.md) |
| DP-ARCH-10 | 上下文窗口控制：单 Agent 输入 Token ≤ 模型窗口的 50%；决策索引注入 ≤ 300 Token | context-control, token-budget | ✅ 已确认 | [dp_arch_10.md](dp_arch_10.md) |
| DP-ARCH-11 | 教学评估指标在课程规划阶段设计，而非事后补做；评估与节点绑定 | evaluation-metrics, design-upfront | ✅ 已确认 | [dp_arch_11.md](dp_arch_11.md) |
| DP-ARCH-12 | 节点内错题闭环：错误诊断 → 补充讲解 → 同类新题 → 再评估 | error-loop, node-mastery | ✅ 已确认 | [dp_arch_12.md](dp_arch_12.md) |
| DP-ARCH-13 | 知识网络动态维护：后台 meta-scenario，基于学生数据持续优化网络结构 | network-maintenance, meta-scenario | ✅ 已确认 | [dp_arch_13.md](dp_arch_13.md) |

---

## 内容决策（Content Decisions）

| DP ID | 决策摘要 | 关键词 | 确认状态 | 详情页面 |
|-------|---------|--------|---------|---------|
| DP-CONT-01 | 教学方法 8 种：讲授法 / 问答法 / 讨论法 / 演示法 / 实验法 / 探究法 / 情境法 / 项目引领 | teaching-methods, 8-methods | ✅ 已确认 | [dp_cont_01.md](dp_cont_01.md) |
| DP-CONT-02 | 课程规划完整产物包含：stage1 教学目标体系 + stage2 课程结构 + stage3 知识网络 + 评估指标体系 | course-output, 3-stages-output | ✅ 已确认 | [dp_cont_02.md](dp_cont_02.md) |

---

## 使用说明

### Agent 工作流

```
【任务：修改/讨论/新增需求文档内容】

1. 读取本文件（decision_index.md）
   → 获得所有已确认决策点摘要（≈ 300 Token）

2. 读取主索引（system_requirements.md）
   → 了解文档的模块化结构，定位目标章节（≈ 800 Token）

3. 按需读取目标模块文件
   → 例如修改场景1 → 读取 /modules/03_scenes/scene_001_course_planning.md
   → 每个模块约 300-1500 Token

4. 如需了解某个决策点的详细背景
   → 读取对应 dp_arch_*.md 文件
   → 每个决策详情约 50-200 Token

5. 执行修改后
   → 如产生新架构决策：更新本 decision_index.md
   → 如修改模块：更新对应模块文件
   → 不要直接修改完整旧版主文档（该文件将被新索引替代）
```

### 文档结构总览

```
/workspace/docs/
├── system_requirements.md       ← 主索引（仅目录+链接，≈ 300行）
├── decisions/
│   ├── decision_index.md        ← 本文件（决策点索引）
│   ├── dp_arch_*.md            ← 架构决策详情（13个文件）
│   └── dp_cont_*.md            ← 内容决策详情（2个文件）
└── modules/
    ├── 01_overview.md           ← 文档概述 + 术语约定
    ├── 02_background.md         ← 业务背景 + 建设目标
    ├── 03_scenes/               ← 9 个场景独立文件
    │   ├── scene_001_course_planning.md
    │   ├── scene_002_lesson_prep.md
    │   └── ... (7个文件)
    ├── 04_functional_requirements.md   ← FR-01~FR-18
    ├── 05_non_functional.md     ← 非功能需求 + 记忆体系
    ├── 06_boundary.md           ← 系统边界与外部依赖
    ├── 07_acceptance.md         ← 验收标准
    ├── 08_roadmap.md            ← 版本路线图
    ├── 09_risks.md              ← 风险与待决事项
    └── 10_references.md         ← 参考文档
```

---

## 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0 | 2026-06-12 | 首次创建：从 2,783 行完整需求文档中提取 15 个核心决策点 |

# EduAgents 多智能体教学框架 — 系统需求文档（模块化索引版）

**版本**：v2.0（模块化） · **日期**：2026-06-12
**文档状态**：核心团队已确认 · **阅读优先顺序**：决策索引 → 对应模块

---

## 快速开始

### Agent 修改/讨论本文档的标准工作流

```
【任务：修改/讨论/新增需求文档内容】

1. 读取本文件（system_requirements.md）
   → 了解文档的模块化结构，定位目标章节（≈ 800 Token）

2. 读取 decision_index.md
   → 获得所有已确认决策点摘要（≈ 300 Token）

3. 按需读取目标模块文件
   → 例如修改课程规划 → 读取 /modules/03_scenes/scene_001_course_planning.md
   → 每个模块约 300-1500 Token

4. 如需了解某个决策点的详细背景
   → 读取对应 dp_arch_*.md 文件
   → 每个决策详情约 50-200 Token

5. 执行修改后
   → 如产生新架构决策：更新 decision_index.md
   → 如修改模块：更新对应模块文件
   → 不再维护完整旧版主文档（该文档已模块化拆分）
```

### 每次修改的 Token 量对比

| 项目 | 旧版（单一长文件） | 新版（模块化+决策索引） | 缩减率 |
|------|-------------------|------------------------|--------|
| 单次修改总 Token | ≈ 6,000-8,000 | ≈ 1,000-2,500 | **~70%** |
| 加载主文档 | 2,783 行 ≈ 6,000 Token | 本文件 ≈ 800 Token | **~87%** |
| 上下文膨胀风险 | 高（多场景内容互相干扰） | 低（每次只读目标模块） | **显著降低** |
| 幻觉风险 | 高（大量信息超出注意力窗口） | 低（信息分模块，Agent 只读取需要的内容） | **显著降低** |

---

## 文档结构总览

```
docs/
├── system_requirements.md       ← 本文件（目录索引，≈ 300 行）
│
├── decisions/                    ← 决策点目录（15 个决策点文件）
│   ├── decision_index.md         ← 决策点主索引（必读）
│   ├── dp_arch_01.md             ← 方案D：知识编译+决策索引
│   ├── dp_arch_02.md             ← 9 个典型业务场景
│   ├── dp_arch_03.md             ← 课程规划三阶段设计
│   ├── dp_arch_04.md             ← 知识网络三层节点结构
│   ├── dp_arch_05.md             ← 动态学习路径
│   ├── dp_arch_06.md             ← 18 个功能需求
│   ├── dp_arch_07.md             ← Harness 约束层
│   ├── dp_arch_08.md             ← 思政融合设计
│   ├── dp_arch_09.md             ← 三层记忆体系
│   ├── dp_arch_10.md             ← 上下文窗口控制
│   ├── dp_arch_11.md             ← 评估指标在课程规划阶段设计
│   ├── dp_arch_12.md             ← 节点内错题闭环
│   ├── dp_arch_13.md             ← 知识网络动态维护
│   ├── dp_cont_01.md             ← 8 种教学方法
│   └── dp_cont_02.md             ← 课程规划完整产物结构
│
└── modules/                      ← 内容模块目录（10 大模块）
    ├── 01_overview.md            ← 文档概述 + 术语约定（1.1~1.3）
    ├── 02_background.md          ← 业务背景 + 建设目标（2.1~2.3）
    ├── 03_user_roles_scenes_index.md  ← 用户角色 + 9 场景总览（3.1~3.2）
    ├── 03_scenes/                ← 9 个场景独立文件
    │   ├── scene_001_course_planning.md        ← 课程规划（最大，452 行）
    │   ├── scene_002_lesson_prep.md            ← 备课辅助
    │   ├── scene_003_virtual_classroom.md      ← 虚拟教室
    │   ├── scene_004_error_loop.md             ← 节点内错题闭环
    │   ├── scene_005_node_recommendation.md    ← 节点推荐引擎
    │   ├── scene_006_homework_grading.md       ← 作业批改
    │   ├── scene_007_learning_analytics.md     ← 学情分析
    │   ├── scene_008_teaching_evaluation.md    ← 教学评估
    │   └── scene_009_network_maintenance.md    ← 知识网络动态维护
    ├── 04_functional_requirements.md           ← 功能需求（FR-01 ~ FR-18）
    ├── 05_non_functional.md                    ← 非功能需求 + 记忆体系
    ├── 06_boundary.md                          ← 系统边界与外部依赖
    ├── 07_acceptance.md                        ← 验收标准
    ├── 08_roadmap.md                           ← 版本路线图
    ├── 09_risks.md                             ← 风险与待决事项
    └── 10_references.md                        ← 参考文档
```

---

## 目录导航

### 第一部分：决策索引（必读）

| 文件 | 内容 | 优先级 | 预估 Token |
|------|------|--------|-----------|
| [decisions/decision_index.md](decisions/decision_index.md) | 13 个架构决策 + 2 个内容决策的极简汇总 | **P0 必读** | ≈ 300 |

### 第二部分：内容模块

| 模块 | 文件 | 主要内容 | 预估 Token |
|------|------|---------|-----------|
| **01** 概述 | [modules/01_overview.md](modules/01_overview.md) | 文档目的、适用读者、术语约定（20+ 术语） | ≈ 2,500 |
| **02** 背景 | [modules/02_background.md](modules/02_background.md) | 业务背景（8 条结构性不足） + 建设目标（13+ 目标） | ≈ 1,100 |
| **03** 场景索引 | [modules/03_user_roles_scenes_index.md](modules/03_user_roles_scenes_index.md) | 用户角色定义 + 9 场景总览表 | ≈ 700 |
| **03.01** | [modules/03_scenes/scene_001_course_planning.md](modules/03_scenes/scene_001_course_planning.md) | **核心场景**：课程规划三阶段设计 + 完整 YAML 输出示例 | ≈ 10,000 |
| **03.02** | [modules/03_scenes/scene_002_lesson_prep.md](modules/03_scenes/scene_002_lesson_prep.md) | 备课辅助：为节点生成教案/学案/资源/思政融合 | ≈ 4,600 |
| **03.03** | [modules/03_scenes/scene_003_virtual_classroom.md](modules/03_scenes/scene_003_virtual_classroom.md) | 虚拟教室：学生在单个节点上的学习体验 | ≈ 3,400 |
| **03.04** | [modules/03_scenes/scene_004_error_loop.md](modules/03_scenes/scene_004_error_loop.md) | 节点内错题闭环：诊断 → 补充讲解 → 同类题 → 再评估 | ≈ 3,300 |
| **03.05** | [modules/03_scenes/scene_005_node_recommendation.md](modules/03_scenes/scene_005_node_recommendation.md) | 节点推荐引擎：基于网络依赖 + 学生表现 + 目标层次的推荐 | ≈ 1,700 |
| **03.06** | [modules/03_scenes/scene_006_homework_grading.md](modules/03_scenes/scene_006_homework_grading.md) | 作业批改：批改 Agent 输出 + 评分 + 逐题点评 | ≈ 2,100 |
| **03.07** | [modules/03_scenes/scene_007_learning_analytics.md](modules/03_scenes/scene_007_learning_analytics.md) | 学情分析：学生画像 + 班级热力图 + 薄弱环节分析 | ≈ 1,300 |
| **03.08** | [modules/03_scenes/scene_008_teaching_evaluation.md](modules/03_scenes/scene_008_teaching_evaluation.md) | 教学评估：使用课程规划阶段设计的指标进行评估 | ≈ 1,200 |
| **03.09** | [modules/03_scenes/scene_009_network_maintenance.md](modules/03_scenes/scene_009_network_maintenance.md) | 知识网络动态维护：后台 meta-scenario 优化建议 | ≈ 1,700 |
| **04** FR | [modules/04_functional_requirements.md](modules/04_functional_requirements.md) | 18 个功能需求详细定义（FR-01 ~ FR-18） | ≈ 17,000 |
| **05** NFR | [modules/05_non_functional.md](modules/05_non_functional.md) | 非功能需求 + 三层记忆体系（STM/WM/LTM） | ≈ 7,000 |
| **06** 边界 | [modules/06_boundary.md](modules/06_boundary.md) | 系统边界、外部依赖、技术栈声明 | ≈ 900 |
| **07** 验收 | [modules/07_acceptance.md](modules/07_acceptance.md) | 各场景/FR 的验收标准 | ≈ 1,900 |
| **08** 路线图 | [modules/08_roadmap.md](modules/08_roadmap.md) | v0.1 ~ v1.0 版本路线 | ≈ 400 |
| **09** 风险 | [modules/09_risks.md](modules/09_risks.md) | 13 项风险 + 待决事项 | ≈ 600 |
| **10** 参考 | [modules/10_references.md](modules/10_references.md) | 参考文档列表 | ≈ 400 |

---

## 决策点快速索引

### 架构决策

| 编号 | 决策名称 | 文件 | 一句话说明 |
|------|---------|------|----------|
| DP-ARCH-01 | 采纳方案D | [link](decisions/dp_arch_01.md) | 知识编译+决策索引+Wiki+Git，不需要向量数据库 |
| DP-ARCH-02 | 9 个典型场景 | [link](decisions/dp_arch_02.md) | 课程规划 → 备课 → 虚拟教室 → 错题闭环 → 推荐 → 批改 → 学情 → 评估 → 维护 |
| DP-ARCH-03 | 三阶段课程规划 | [link](decisions/dp_arch_03.md) | 教学目标 → 课程结构 → 知识网络 |
| DP-ARCH-04 | 三层知识网络 | [link](decisions/dp_arch_04.md) | 概念层/技能层/工具层，每个知识点在不同层次投影为独立节点 |
| DP-ARCH-05 | 动态学习路径 | [link](decisions/dp_arch_05.md) | 非课前规划，由"掌握→推荐→选择→移动"迭代涌现 |
| DP-ARCH-06 | 18 个功能需求 | [link](decisions/dp_arch_06.md) | FR-01~FR-18，包含 3 个 P0 需求 |
| DP-ARCH-07 | Harness 约束层 | [link](decisions/dp_arch_07.md) | 提示词模板+Schema校验+工具白名单，结构化输出≥95% |
| DP-ARCH-08 | 思政融合设计 | [link](decisions/dp_arch_08.md) | 在备课阶段，Agent 提出+教师确认 |
| DP-ARCH-09 | 三层记忆体系 | [link](decisions/dp_arch_09.md) | STM / WM / LTM，决策索引为桥梁 |
| DP-ARCH-10 | 上下文窗口控制 | [link](decisions/dp_arch_10.md) | 单 Agent 输入 ≤ 模型窗口 50%，膨胀速率 ≤ 5%/轮 |
| DP-ARCH-11 | 评估指标在规划阶段设计 | [link](decisions/dp_arch_11.md) | 与知识网络节点绑定，非事后补做 |
| DP-ARCH-12 | 节点内错题闭环 | [link](decisions/dp_arch_12.md) | 诊断→补充→新题→再评估，连续 2 次正确为掌握 |
| DP-ARCH-13 | 知识网络动态维护 | [link](decisions/dp_arch_13.md) | 后台 meta-scenario，基于学生数据生成优化建议 |

### 内容决策

| 编号 | 决策名称 | 文件 | 一句话说明 |
|------|---------|------|----------|
| DP-CONT-01 | 8 种教学方法 | [link](decisions/dp_cont_01.md) | 讲授/问答/讨论/演示/实验/探究/情境/项目引领 |
| DP-CONT-02 | 课程规划完整产物 | [link](decisions/dp_cont_02.md) | stage1 目标 + stage2 结构 + stage3 知识网络 + 评估指标 |

---

## 文档版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v2.0 | 2026-06-12 | **模块化重构**：原 2,783 行单一文档 → 拆分 1 个索引 + 15 个决策点 + 10 大模块 + 9 场景（共 35 个文件） |
| v1.4 | 2026-06-12 | 采纳方案D，新增决策索引和知识编译机制（FR-18） |
| v1.3 | 2026-06-12 | SCENE-001 重构为三阶段设计，所有场景扩展为 Agent 角色定义 + 交互流程 + I/O 规格 |
| v1.2 | 2026-06-12 | 扩展 FR 至 18 项，新增方案D 架构决策 |
| v1.1 | 2026-06-12 | 补充非功能需求中记忆调取、Harness 约束和知识网络内容 |
| v1.0 | 2026-06-12 | 初版发布 |

---

## 附录：全文统计

| 指标 | 旧版 | 新版（模块化） |
|------|------|--------------|
| 主文档行数 | 2,783 | ≈ 300 |
| 文件总数 | 1 | **35** |
| 决策点文件 | 0 | 15（13 架构 + 2 内容） |
| 内容模块文件 | 0 | 10 |
| 场景独立文件 | 0 | 9 |
| 每次修改 Token 量 | ≈ 6,000-8,000 | ≈ 1,000-2,500 |
| 上下文膨胀风险 | 高 | 低 |
| Agent 幻觉风险 | 高 | 低 |

---

**说明**：本文档采用 [DP-ARCH-01 方案D](decisions/dp_arch_01.md) 的知识编译与决策索引架构，将完整的 2,783 行需求文档重构为"索引 + 模块化内容"的轻量级系统。如需完整浏览内容，请从 [decision_index.md](decisions/decision_index.md) 开始，按链接导航至对应模块文件。

原完整内容已备份为 [system_requirements_full.md](system_requirements_full.md)，仅供历史查阅。

# EduAgent —— 面向教学辅助的多智能体协同平台

EduAgent 是一个面向教学辅助场景的多智能体协同平台，基于 **DeepAgents** 与 **AgentScope** 两类框架构建，聚焦于教师备课、课程规划、虚拟教室、学习路径推荐、学情分析、作业批改等教学全链路。

## 目录

1. [概述](modules/01_overview.md)
2. [项目背景与目标](modules/02_background.md)
3. [核心场景](modules/03_scenes/)
   - [SCENE-001：课程规划](modules/03_scenes/scene_001_course_planning.md)
   - [SCENE-002：备课辅助](modules/03_scenes/scene_002_lesson_prep.md)
   - [SCENE-003：虚拟教室](modules/03_scenes/scene_003_virtual_classroom.md)
   - [SCENE-004：节点内错题闭环](modules/03_scenes/scene_004_error_loop.md)
   - [SCENE-005：节点推荐引擎](modules/03_scenes/scene_005_node_recommendation.md)
   - [SCENE-006：作业批改](modules/03_scenes/scene_006_homework_grading.md)
   - [SCENE-007：学情分析](modules/03_scenes/scene_007_learning_analytics.md)
   - [SCENE-008：教学评估](modules/03_scenes/scene_008_teaching_evaluation.md)
   - [SCENE-009：知识网络动态维护](modules/03_scenes/scene_009_network_maintenance.md)
4. [功能需求（FR）](modules/04_functional_requirements.md)
5. [非功能需求（NFR）](modules/05_non_functional.md)

## 核心架构

EduAgent 的核心设计围绕 **立体分层知识网络**（概念层 / 技能层 / 工具层）与 **Harness 驾驭层** 展开：

- **知识网络**：每个知识点在不同认知层次上投影为独立节点，支持多路径教学与分层教学。
- **Harness 约束层**：通过提示词模板、结构化输出 Schema、校验管道、工具权限白名单、反馈闭环等手段，将 Agent 的行为严格约束在教学目标范围内，防止自由发散。
- **DeepAgents + AgentScope 协同**：DeepAgents 负责结构化产物生成场景（课程规划、备课、评估、知识网络维护），AgentScope 负责多角色对话交互场景（虚拟教室、错题闭环、节点推荐、作业批改、学情分析），两者通过协议转换层无缝互通。
- **知识编译与决策索引**：将多阶段产物编译为极简 DP 索引，解决上下文膨胀问题。

## 快速开始

- 如需了解平台整体能力与理论基础，请从 [概述](modules/01_overview.md) 开始。
- 如需了解系统约束与 Harness 设计，请优先阅读 [功能需求](modules/04_functional_requirements.md) 中的 **FR-15（Harness 约束层）** 与 **FR-18（知识编译与决策索引系统）**。
- 如需了解单个教学场景的设计细节，请进入 [核心场景](modules/03_scenes/) 目录。

## 许可协议

本项目采用 **CC BY-NC-SA 4.0（知识共享 署名-非商业性使用-相同方式共享 4.0 国际许可协议）**。

- ✅ 允许：个人学习、研究、教学演示（非商业场景）
- ❌ 禁止：**未经权利人书面授权，不得用于商业目的**
- ⚖️ 约束：如对本作品进行改编或基于本作品构建衍生作品，必须以相同或兼容许可协议分发

完整许可证文本请参见项目根目录的 [LICENSE.md](../LICENSE.md)。如需商用授权，请按照 LICENSE.md 中的"商用授权申请"章节联系权利人。

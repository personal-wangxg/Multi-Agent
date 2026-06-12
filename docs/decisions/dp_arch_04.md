# DP-ARCH-04：知识网络三层节点结构

**确认日期**：2026-06-12 · **确认人**：项目核心团队
**决策类别**：架构 · **优先级**：P0

---

## 决策摘要

知识网络是 EduAgents 教学框架的核心数据结构。不同于传统的线性章节组织方式，本系统采用**立体分层知识网络**：每一个抽象的知识点在**概念层（Concept Layer）**、**技能层（Skill Layer）**、**工具层（Tool Layer）**三个层次上分别投影为独立节点，并通过层内边、跨层边、同主题边三类关系形成有向图。学习路径可在同一知识点内跨越层次推进（如工具层 → 技能层 → 概念层），也可在同层次内沿依赖关系前进。

## 核心设计原则

1. **三层分层，培养目标对齐**
   - 工具层（Tool）：关注"怎么操作"——掌握固定步骤、标准流程、模板化使用。对应专中职/工具性操作学习目标
   - 技能层（Skill）：关注"何时用"——能在不同情境中判断何时使用、灵活迁移、选择策略。对应高职/本科学习目标
   - 概念层（Concept）：关注"为什么"——理解本质、原理、推导与内在机制。对应研究生/研究型学习目标

2. **同一知识点多节点，路径灵活**
   - 同一个抽象知识点（如"一元二次方程"）在三个层次上可能有 1~3 个节点
   - 学生可根据目标层次选择从工具层进入（先会操作再理解），或从概念层进入（先理解本质再操作）
   - 跨层边允许在同一知识点内切换层次

3. **边关系显式建模，驱动推荐引擎**
   - 层内边 is_prerequisite：描述同一层次内节点的前置/后继依赖，是节点推荐引擎的主干依据
   - 跨层边 supports_understanding / enables_operation：描述概念支撑技能、技能支撑工具的递进关系
   - 同主题边 same_topic_cross_layer：标记同一知识点在三层间的对应关系，用于学习体验的纵向穿梭

4. **节点携带元数据，不只是名称**
   - bloom_level：该节点对应的布鲁姆分类层级，影响练习题目与评估标准
   - difficulty：1~5 的难度标记，影响推荐时的路径平滑度
   - can_self_learn：标记是否支持学生自学掌握，影响是否需要教师讲授
   - estimated_periods：预计课时，供课程结构与教学安排使用

5. **网状结构，多起点多路径**
   - 知识网络不是一条直线，存在多条从起点到汇聚节点的可选路径
   - 每个节点可标记"入口难度"，不同学生可从不同节点进入
   - 多个节点可汇聚为"学习效果达成"的标志节点

## 关键细节

### 节点字段规范

```yaml
nodes:
  - id: "concept_equation_essence"          # 命名建议：{layer}_{topic}_{detail}
    layer: "concept"                        # concept / skill / tool
    title: "理解一元二次方程的本质"
    bloom_level: "analyze"                  # remember/understand/apply/analyze/evaluate/create
    difficulty: 4                           # 1~5
    can_self_learn: false
    estimated_periods: 1
    mapped_unit: "unit_01"                   # 对应 stage2 的结构单元
    teaching_objectives:
      knowledge: ["理解一元二次方程的定义与一般形式"]
      ability: ["能判断一个方程是否为一元二次方程"]
      quality: ["培养抽象概括能力"]
```

### 边关系字段规范

```yaml
edges:
  # 层内边：同层次的先后依赖
  - from: "concept_equation_essence"
    to: "concept_discriminant_meaning"
    relation_type: "is_prerequisite"

  # 跨层边：概念 → 技能 → 工具 的支撑关系
  - from: "concept_equation_essence"
    to: "skill_method_selection"
    relation_type: "supports_understanding"

  # 跨层边：技能 → 工具 的操作支撑
  - from: "skill_method_selection"
    to: "tool_formula_method"
    relation_type: "enables_operation"

  # 同主题边：同一知识点在三层间的关联
  - from: "concept_equation_essence"
    to: "skill_method_selection"
    relation_type: "same_topic_cross_layer"
```

### 层次与布鲁姆层级的参考映射

| 层次 | 典型 bloom_level | 典型评估标准 | 示例 |
|-----|----------------|------------|------|
| tool | apply | 正确率 ≥ 80%，按标准流程完成操作 | 记忆求根公式、使用因式分解法求解 |
| skill | analyze | 能根据情境选择合适解法，迁移应用 | 根据方程特征灵活选择解法、在真实情境中建模 |
| concept | analyze/evaluate/create | 能解释本质与原理，进行推导 | 理解判别式的意义、论证解的合理性 |

### 网络结构说明

- `network_notes`：描述网络的入口节点、汇聚节点、典型路径等信息
- 至少保证三个层次各有 ≥ 1 个节点（Harness Schema 约束 layer_distribution）
- 节点 `mapped_unit` 必须与 stage2 课程结构中定义的单元 id 有映射关系

## 影响范围

- DP-ARCH-03 课程规划三阶段（特别是 stage3）
- DP-ARCH-05 动态学习路径（节点层次决定推荐策略）
- SCENE-002 备课辅助（按节点生成教案/学案/资源）
- SCENE-003 虚拟教室（节点上的教学体验受 layer/can_self_learn 影响）
- SCENE-005 节点推荐引擎（is_prerequisite 边为主要推荐依据）
- SCENE-004 节点内错题闭环（错误类型与层次关联）
- SCENE-009 知识网络动态维护（基于学生数据调整节点拆分/合并）
- FR-09（教学方法选择与节点层次对齐）、FR-10（个性化学习路径支持不同层次）

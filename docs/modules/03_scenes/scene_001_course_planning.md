# SCENE-001：课程规划

**父文档**：[system_requirements.md](../../system_requirements.md) · [场景索引](../03_user_roles_scenes_index.md)
**相关决策**：[dp_arch_03](../../decisions/dp_arch_03.md), [dp_arch_04](../../decisions/dp_arch_04.md), [dp_arch_05](../../decisions/dp_arch_05.md), [dp_arch_11](../../decisions/dp_arch_11.md), [dp_cont_02](../../decisions/dp_cont_02.md)

---

### 3.2.1 SCENE-001：课程规划

**场景目标**：教师输入课程基本信息后，教师与 Agent 协同迭代，依次完成**教学目标设计 → 课程结构设计 → 知识网络设计**三个阶段，最终产出：教学目标体系（知识/能力/素质）+ 教学方法选择 + 学习效果检验方式 + 立体分层知识网络 + 教学评估指标体系。

**核心设计原则**：
1. **教师与 Agent 共创**而非 Agent 单向输出：Agent 生成方案 → 教师标注修改意见 → Agent 迭代生成新版本 → 教师确认（与本需求文档的讨论过程一致）。课程方向由人类教师最后确定，确定过程不是简单"选择"，而是迭代共创
2. 知识网络是**立体分层**而非线性章节：概念层（为什么）→ 技能层（何时用）→ 工具层（怎么操作），每个知识点在不同层次上形成独立节点
3. 知识网络是**网状**而非一条线：考虑分层教学需要，不同学生起点不同、目标不同，到达终点的路径不唯一
4. 评估指标在**规划阶段**完成，而非事后补做
5. 每个节点都有独立的布鲁姆分类、难度标记、是否可自学标记

#### Agent 角色定义

| Agent 角色 | 框架 | 职责边界 | 提示词关键词 |
|-----------|------|---------|------------|
| 教学目标设计 Agent | DeepAgents | 阶段1：设计教学目标体系 + 预期学习效果 + 教学方法 + 检验方式 | "你是教育目标设计专家，按布鲁姆分类法设计分层次学习目标" |
| 课程结构设计 Agent | DeepAgents | 阶段2：基于教学方法设计课程结构（章节/场景/项目等） | "你是资深课程设计专家，擅长将教学目标映射为合理的课程结构" |
| 知识网络构建 Agent | DeepAgents | 阶段3：为课程结构设计概念/技能/工具三层节点及边关系 | "你是课程设计专家，擅长将课程内容分解为概念/技能/工具三层节点体系" |
| 评估指标设计 Agent | DeepAgents | 贯穿阶段1~3：同步设计与阶段产物匹配的评估指标体系 | "你是教育评估专家，能为知识网络设计配套评估指标" |

#### 交互流程（三阶段迭代共创）

本场景采用**分阶段迭代**模式。每一阶段遵循相同的共创闭环：

```
Agent 生成方案 v1
    │
    ▼
教师审阅（提出修改意见 / 接受 / 调整）
    │
    ▼
Agent 吸收意见，生成方案 v2
    │
    ▼
（多轮迭代，直到教师确认）
    │
    ▼
本阶段产物确认 → 进入下一阶段
```

**完整阶段流程**：

```
教师输入课程信息
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│ 阶段1：教学目标设计                                       │
│                                                          │
│ 教学目标设计 Agent 生成方案：                            │
│   · 知识目标：课程完成后学生应掌握的知识内容              │
│   · 能力目标：学生应具备的分析/应用/解决问题能力          │
│   · 素质目标：学生应培养的学科素养与思维品质              │
│   · 预期学习效果：可观测的学习产出描述                    │
│   · 教学方法推荐：讲授法/问答法/讨论法/演示法/实验法/     │
│                   探究法/情境法/项目引领（可多选）         │
│   · 学习效果检验方式：课堂检测/作业/项目作品/口头表达等   │
│                                                          │
│ 评估指标设计 Agent 同步产出：与教学目标匹配的评估量表      │
│                                                          │
│ → 教师审阅 → 修改意见 → Agent 修订 → 教师确认           │
│   （可多轮迭代）                                           │
└─────────────────────────────┬────────────────────────────┘
    阶段1产物：教学目标体系 + 教学方法 + 检验方式 + 评估指标
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│ 阶段2：课程结构设计                                       │
│                                                          │
│ 课程结构设计 Agent 基于阶段1的教学方法，产出课程结构：    │
│                                                          │
│   【如采用讲授法/讨论法】→ 章节式结构：                   │
│     · 第1章：×××（覆盖知识点 A/B/C）                      │
│     · 第2章：×××（覆盖知识点 D/E）                        │
│     · ...                                                │
│                                                          │
│   【如采用情境法/项目引领】→ 场景式结构：                   │
│     · 场景1：×××情境（覆盖知识点 A/B/C，驱动任务：×××）    │
│     · 场景2：×××情境（覆盖知识点 D/E，驱动任务：×××）      │
│     · ...                                                │
│                                                          │
│   【如采用实验法/探究法】→ 探究式结构（含问题链 + 活动链）  │
│                                                          │
│   · 每个结构单元标注：计划课时、核心知识点关键词、建议教学法│
│                                                          │
│ 评估指标设计 Agent 同步调整：与结构单元匹配的观测点/量表    │
│                                                          │
│ → 教师审阅 → 修改意见 → Agent 修订 → 教师确认           │
│   （可多轮迭代）                                           │
└─────────────────────────────┬────────────────────────────┘
    阶段2产物：课程结构（章节/场景/项目）+ 单元-知识点映射
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│ 阶段3：知识网络设计（核心产物）                            │
│                                                          │
│ 知识网络构建 Agent 为阶段2每个结构单元设计三层节点：        │
│                                                          │
│   每个知识点 → 拆分为：                                    │
│   · 概念层节点（为什么）：理解学科本质、原理、逻辑          │
│   · 技能层节点（何时用）：判断适用情境、建立模型、迁移应用  │
│   · 工具层节点（怎么操作）：具体步骤、公式、操作方法        │
│                                                          │
│   每个节点附：                                            │
│   · bloom_level（remember/understand/apply/analyze/      │
│                       evaluate/create）                   │
│   · difficulty（1~5）                                      │
│   · can_self_learn（true/false，判断是否可自学掌握）        │
│   · estimated_periods（预计课时）                           │
│                                                          │
│   节点间边关系：                                            │
│   · 层内边：is_prerequisite（同层次内的先后依赖）          │
│   · 跨层边：supports_understanding（概念支撑技能，         │
│              技能支撑工具的理解）                           │
│   · 同主题边：same_topic（同一知识点在三层间的对应关系）     │
│                                                          │
│   网络结构特征：                                            │
│   · 非一条直线，允许多起点与多路径                          │
│   · 每个节点可标记"入口难度"，不同学生可从不同节点进入      │
│   · 多个节点可汇聚为"学习效果达成"的标志点                  │
│                                                          │
│ 评估指标设计 Agent 同步产出：与节点绑定的评估项/量表        │
│                                                          │
│ → 教师审阅 → 修改意见 → Agent 修订 → 教师确认           │
│   （可多轮迭代）                                           │
└─────────────────────────────┬────────────────────────────┘
    阶段3产物：立体分层知识网络（节点 + 边 + 评估指标）
    │
    ▼
教师最终确认 → 写入 VFS 持久化
输出：完整课程规划 JSON
    │
    ▼
Harness Schema 校验：
    │
┌──┴──┐
│ 通过  │ 不通过
▼      ▼
保存配置  自动重试（≤3次）
    │
    ▼
人工干预提示
```

#### 输入规格

```yaml
course_name: "初中数学：一元二次方程"        # 必填，课程名称
course_desc: "面向初三学生，讲解一元二次方程的求解与应用"  # 必填
target_student_level: "初中三年级"                 # 必填，目标学生层次，影响节点的深度与难度配置
teaching_periods: 12                              # 必填，总课时数
teacher_id: "t_001"                               # 必填
```

#### 输出规格（课程规划完整产物，三阶段汇总）

```yaml
course_planning:
  metadata:
    course_name: "初中数学：一元二次方程"
    target_level: "初中三年级"
    total_periods: 12
    version: "1.0"
    created_at: "2026-06-12T10:00:00Z"
    teacher_id: "t_001"

  # ============== 阶段1产物：教学目标体系 ==============
  stage1_teaching_objectives:
    knowledge_goals:
      - "理解一元二次方程的定义与一般形式"
      - "掌握一元二次方程的多种解法（直接开方/配方法/公式法/因式分解）"
      - "理解判别式与解的关系"
      - "能运用一元二次方程解决实际问题"

    ability_goals:
      - "能根据实际情境建立一元二次方程模型"
      - "能根据方程特征灵活选择解法"
      - "能分析与检验解的合理性"

    quality_goals:
      - "培养逻辑推理与严谨思维"
      - "体会数学建模的价值与应用美"
      - "培养实事求是、勇于探究的科学态度"

    expected_learning_outcomes:
      - "学生能独立完成一元二次方程的求解过程"
      - "学生能在真实情境中建立并求解一元二次方程"
      - "学生能解释解法选择的理由与判别式的意义"

    teaching_methods:              # 从预置集合中选择（可多选）
      - method_id: "lecture"
        name: "讲授法"
        applicable_structure: "章节式"
      - method_id: "inquiry"
        name: "探究法"
        applicable_structure: "探究式"
      - method_id: "project"
        name: "项目引领"
        applicable_structure: "场景式"

    assessment_methods:            # 学习效果检验方式
      - "课堂小检测"
      - "书面作业"
      - "项目作品"
      - "口头表达与讨论参与"

  # ============== 阶段2产物：课程结构 ==============
  stage2_course_structure:
    structure_type: "mixed"           # chapter / scene / inquiry / mixed

    units:
      - unit_id: "unit_01"
        title: "一元二次方程的引入"
        teaching_method: "讲授法 + 讨论法"
        estimated_periods: 2
        core_knowledge_keywords: ["定义", "一般形式", "判别式"]

      - unit_id: "unit_02"
        title: "方程的解法探究"
        teaching_method: "探究法 + 演示法"
        estimated_periods: 4
        core_knowledge_keywords: ["直接开方", "配方法", "公式法", "因式分解"]

      - unit_id: "unit_03"
        title: "实际问题建模"
        teaching_method: "情境法 + 项目引领"
        estimated_periods: 4
        core_knowledge_keywords: ["建模", "应用题", "解的合理性检验"]

      - unit_id: "unit_04"
        title: "综合练习与反思"
        teaching_method: "讲授法 + 问答法"
        estimated_periods: 2
        core_knowledge_keywords: ["综合应用", "错误归因", "方法比较"]

  # ============== 阶段3产物：立体分层知识网络 ==============
  stage3_knowledge_network:
    nodes:
      # 概念层节点（为什么）
      - id: "concept_equation_essence"
        layer: "concept"
        title: "理解一元二次方程的本质"
        bloom_level: "analyze"
        difficulty: 4
        can_self_learn: false
        estimated_periods: 1
        mapped_unit: "unit_01"
        teaching_objectives:
          knowledge: ["理解一元二次方程的定义与一般形式"]
          ability: ["能判断一个方程是否为一元二次方程"]
          quality: ["培养抽象概括能力"]

      - id: "concept_discriminant_meaning"
        layer: "concept"
        title: "理解判别式的意义"
        bloom_level: "understand"
        difficulty: 3
        can_self_learn: true
        estimated_periods: 1
        mapped_unit: "unit_01"
        teaching_objectives:
          knowledge: ["理解判别式与解的关系"]
          ability: ["能根据判别式判断解的个数与类型"]

      # 技能层节点（何时用）
      - id: "skill_method_selection"
        layer: "skill"
        title: "根据方程特征灵活选择解法"
        bloom_level: "apply"
        difficulty: 4
        can_self_learn: false
        estimated_periods: 2
        mapped_unit: "unit_02"
        teaching_objectives:
          knowledge: ["掌握各解法的适用条件"]
          ability: ["能根据方程结构选择最优解法"]

      - id: "skill_model_building"
        layer: "skill"
        title: "根据实际问题建立数学模型"
        bloom_level: "create"
        difficulty: 5
        can_self_learn: false
        estimated_periods: 3
        mapped_unit: "unit_03"
        teaching_objectives:
          knowledge: ["理解建模的一般步骤"]
          ability: ["能在真实情境中抽象出一元二次方程"]
          quality: ["体会数学建模的价值"]

      # 工具层节点（怎么操作）
      - id: "tool_formula_method"
        layer: "tool"
        title: "公式法求解一元二次方程"
        bloom_level: "apply"
        difficulty: 2
        can_self_learn: true
        estimated_periods: 2
        mapped_unit: "unit_02"
        teaching_objectives:
          knowledge: ["记住求根公式"]
          ability: ["能正确代入求解"]

      - id: "tool_factorization_method"
        layer: "tool"
        title: "因式分解法求解一元二次方程"
        bloom_level: "apply"
        difficulty: 3
        can_self_learn: true
        estimated_periods: 2
        mapped_unit: "unit_02"
        teaching_objectives:
          knowledge: ["理解因式分解法的原理"]
          ability: ["能对可分解的方程进行因式分解求解"]

    edges:
      # 层内边（同层次内的先后依赖）
      - from: "concept_equation_essence"
        to: "concept_discriminant_meaning"
        relation_type: "is_prerequisite"

      - from: "tool_formula_method"
        to: "tool_factorization_method"
        relation_type: "is_prerequisite"

      # 跨层边（概念支撑技能，技能支撑工具）
      - from: "concept_equation_essence"
        to: "skill_method_selection"
        relation_type: "supports_understanding"

      - from: "concept_discriminant_meaning"
        to: "skill_method_selection"
        relation_type: "supports_understanding"

      - from: "skill_method_selection"
        to: "tool_formula_method"
        relation_type: "enables_operation"

      - from: "skill_model_building"
        to: "tool_formula_method"
        relation_type: "enables_operation"

      # 同主题边（同一知识点在三层间的对应关系）
      - from: "concept_equation_essence"
        to: "skill_method_selection"
        relation_type: "same_topic_cross_layer"

    # 网络结构特征（多路径入口说明）
    network_notes:
      - "学生可从 concept_equation_essence（基础较好）或 tool_formula_method（基础一般）进入网络"
      - "到达 skill_model_building 可通过多条路径：概念→工具→技能，或工具→技能"
      - "skill_model_building 是课程学习效果达成的汇聚节点"

  # ============== 贯穿产物：评估指标体系 ==============
  evaluation_metrics:
    - metric_id: "m_001"
      target_node: "concept_equation_essence"
      metric_type: "observational_scale"
      content: "学生能否正确判断一元二次方程并解释其一般形式的意义"
      observation_target: "课堂表现 + 课堂小检测"
      scoring_rubric: "1-5分，5分=能独立完成并解释理由"

    - metric_id: "m_002"
      target_node: "skill_model_building"
      metric_type: "project_rubric"
      content: "学生能否在实际情境中正确建立一元二次方程模型并求解"
      observation_target: "项目作品 + 书面作业"
      scoring_rubric: "按建模过程/求解过程/合理性检验/反思总结四维度评分"

    - metric_id: "m_003"
      target_node: "tool_formula_method"
      metric_type: "written_test"
      content: "学生能否正确使用公式法求解一元二次方程"
      observation_target: "课堂小检测 + 作业"
      scoring_rubric: "正确率 ≥ 80% 为掌握"

agent_session_id: "sess_course_planning_001"
iteration_counts:
  stage1: 2      # 阶段1迭代次数
  stage2: 1      # 阶段2迭代次数
  stage3: 3      # 阶段3迭代次数

created_at: "2026-06-12T10:15:00Z"
```

#### 校验规则（Harness）

```json
{
  "required": ["course_planning"],
  "properties": {
    "stage1_teaching_objectives": {
      "required": ["knowledge_goals", "ability_goals", "quality_goals",
                   "expected_learning_outcomes", "teaching_methods", "assessment_methods"],
      "minItems_knowledge": 2,
      "minItems_ability": 2,
      "minItems_quality": 1
    },
    "stage2_course_structure": {
      "required": ["structure_type", "units"],
      "units_minItems": 2,
      "units_items_required": ["unit_id", "title", "teaching_method",
                               "estimated_periods", "core_knowledge_keywords"]
    },
    "stage3_knowledge_network": {
      "nodes": {
        "type": "array",
        "minItems": 3,
        "items": {
          "required": ["id", "layer", "title", "bloom_level",
                       "difficulty", "can_self_learn", "estimated_periods"],
          "layer_enum": ["concept", "skill", "tool"],
          "bloom_level_enum": ["remember", "understand", "apply",
                               "analyze", "evaluate", "create"]
        }
      },
      "edges": {
        "type": "array",
        "items": {
          "required": ["from", "to", "relation_type"]
        }
      },
      "layer_distribution": {
        "concept_min": 1,
        "skill_min": 1,
        "tool_min": 1
      }
    },
    "evaluation_metrics": {
      "type": "array",
      "minItems": 2
    }
  }
}
```

#### 边界与异常

| 异常场景 | 系统行为 |
|---------|---------|
| 输入课程名为空 | 返回错误码 ERR-INPUT-001，拒绝执行 |
| 阶段1教学方法未指定 | 提示教师选择或默认推荐"讲授法+讨论法" |
| 阶段2结构单元与总课时不匹配 | 触发教师确认：结构单元累计课时 M 与输入 total_periods 差距较大，是否调整？ |
| 阶段3节点缺少某一层（全为工具层无概念层） | 触发告警：建议补充概念层节点设计 |
| 节点的 mapped_unit 与阶段2结构单元无映射关系 | 提示教师检查节点是否分配到正确的结构单元 |
| 教师连续3次对同一方案提出修改 | 记录为"争议方案"，标记可能需要教师进一步澄清设计意图 |
| Harness 校验失败（字段缺失/格式错误） | 自动触发重试（≤3次），记录失败原因 |
| 单阶段迭代超过5次仍未确认 | 记录为阶段性搁置，提示教师可能需重新审视本阶段设计范围 |
| Token 超预算 | 将阶段产物拆分输出后重试（如先输出节点再输出边） |

---


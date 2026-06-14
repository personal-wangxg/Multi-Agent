# DP-CONT-01：教学方法 8 种

**确认日期**：2026-06-12 · **确认人**：项目核心团队 · **决策类别**：内容

---

## 决策摘要

系统定义 8 种教学方法，用于课程规划阶段（SCENE-001）stage1 中 teaching_methods 选择。不同教学方法影响 stage2 中课程结构的设计模式（章节式 / 场景式 / 探究式）。教师与 Agent 在共创过程中选择并组合这些方法，评估指标在规划阶段同步产出。

## 核心设计原则

1. **8 种方法可多选组合：教师可组合多种方法，
2. **不同方法影响课程结构设计模式：讲授法/问答法 → 章节式；情境法/项目引领 → 场景式；探究法/实验法 → 探究式，
3. **每个方法绑定评估方式：方法选择与评估方式同步设计，
4. **结构化标签：每种方法有 method_id / name / applicable_structure 三字段，
5. **方法选择影响教学节奏设计（如讲授法节奏紧凑，探究法节奏宽松）。

## 关键细节

### 8 种教学方法总览

| method_id | 中文名称 | 典型课程结构 | 核心特征 |
|-----------|---------|-------------|---------|
| lecture | 讲授法 | 章节式 chapter | 教师系统讲解知识要点，节奏紧凑 |
| qa | 问答法 | 章节式 chapter | 通过提问引导学生思考与表达 |
| discussion | 讨论法 | 章节式 chapter | 学生之间或师生之间就某主题展开讨论 |
| demo | 演示法 | 章节式 / 场景式 | 教师示范操作/过程，学生观察并模仿 |
| experiment | 实验法 | 探究式 inquiry | 学生动手实验，观察现象，验证假设 |
| inquiry | 探究法 | 探究式 inquiry | 围绕问题链推进，学生自主探究并形成结论 |
| situational | 情境法 | 场景式 scene | 设置真实情境/案例，在情境中推进学习 |
| project | 项目引领 | 场景式 scene | 以项目作品为驱动，多知识多技能综合应用 |

### teaching_methods 在 course_planning 中的字段结构

```yaml
stage1_teaching_objectives:
  # ... 其他字段省略 ...

  teaching_methods:
    - method_id: "lecture"
      name: "讲授法"
      applicable_structure: "chapter"
    - method_id: "inquiry"
      name: "探究法"
      applicable_structure: "inquiry"
    - method_id: "project"
      name: "项目引领"
      applicable_structure: "scene"
```

### 方法 → 课程结构映射（影响 stage2）

| 主要教学方法 | 推荐 structure_type | units 设计特征 |
|-------------|---------------------|----------------|
| 讲授法 + 问答法 + 讨论法 | chapter（章节式） | 按知识体系线性分章，每章含清晰知识点序列 |
| 情境法 + 项目引领 | scene（场景式） | 以情境/项目为组织单元，每个 unit 是完整场景，驱动多知识点综合应用 |
| 实验法 + 探究法 | inquiry（探究式） | 以问题链 + 活动链组织，每个 unit 含问题→假设→探究→结论的完整流程 |
| 多方法混合 | mixed（混合式） | 单元组合使用多种结构类型 |

### 评估方式与方法匹配（assessment_methods）

```yaml
assessment_methods:
  - "课堂小检测"          # 适用于讲授法/问答法
  - "书面作业"            # 适用于所有方法
  - "项目作品"            # 适用于项目引领/情境法
  - "口头表达与讨论参与"   # 适用于讨论法/探究法
  - "实验报告"            # 适用于实验法/探究法
  - "演示与操作考核"       # 适用于演示法/实验法
```

## 影响范围

- 关联 FR：FR-05（立体分层知识网络）；
- 关联场景：SCENE-001（课程规划）stage1 与 stage2；
- 关联决策：DP-CONT-02（课程规划完整产物结构）；
- 关联产物：course_planning.stage1_teaching_objectives.teaching_methods、course_planning.stage2_course_structure.structure_type 与 units。

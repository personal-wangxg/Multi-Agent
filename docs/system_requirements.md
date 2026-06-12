# EduAgents 多智能体辅助教学框架 - 系统需求文档

## 1. 文档概述

### 1.1 文档目的

本文档定义 **EduAgents 多智能体辅助教学框架** 的顶层系统需求，面向项目干系人、架构师、开发人员与测试人员，用于：

- 明确系统建设的目标与边界
- 指导后续功能需求、设计与实现
- 作为测试验收与版本迭代的基准

### 1.2 适用读者

**首要阅读对象：EduAgents 体系内的智能体（Agent）。** 本系统需求文档的结构、术语、示例优先服务于智能体的理解与执行。人类（教师、开发人员、项目干系人）为次要阅读对象，文档对人类保持可读性但不主导。

#### 1.2.1 智能体读者图谱

| 智能体类型 | 文档用途 | 重点阅读章节 |
|-----------|---------|------------|
| **Harness 约束层 Agent** | 读取本文件中的模板、Schema、校验规则，作为自身执行约束的依据 | 4.10（Harness 约束层）、5.6（记忆与上下文管理）、5.7（Harness 约束有效性） |
| **场景执行 Agent**（课程规划/备课/虚拟教室/练习/批改） | 读取对应场景的输入输出规格、Agent 角色定义、交互流程，作为任务执行蓝本 | 3.2.1 ~ 3.2.5（各场景详细规格） |
| **编排与调度 Agent** | 读取系统架构、Agent 协作模式、消息协议，作为编排调度逻辑依据 | 3.2 各场景交互流程、5.6 记忆体系、5.7 校验管道 |
| **记忆管理 Agent** | 读取三层记忆体系定义、向量索引结构、记忆写入与检索流程，作为 LTM/WM 管理逻辑 | 5.6（记忆与上下文管理） |
| **人机协同 Agent** | 读取教师反馈格式、人工干预节点定义，作为等待与响应教师操作的依据 | 4.6（人机协同接口）、4.10.5（反馈闭环） |
| **测试与验收 Agent** | 读取验收标准、性能指标、非功能约束，自动生成与执行测试用例 | 7.x（验收标准）、5.1（性能指标） |

> **Agent 提示：** 上方表格的"重点阅读章节"字段可用作你检索本文件内容的快速锚点。当你不确定某功能如何实现时，优先阅读对应章节。

#### 1.2.2 人类读者（次要）

| 人类角色 | 关注点 |
|---------|--------|
| 最终用户（教师） | 使用流程、交互方式、反馈入口（章节 3.2、4.6） |
| 开发人员 | 功能需求、接口定义、性能指标（章节 4、5） |
| 架构师 | 系统边界、技术约束、集成关系（章节 2、5.7、6） |
| 项目干系人 | 业务价值、建设目标、版本路线图（章节 2、8） |
| 测试人员 | 验收标准、非功能指标（章节 7） |

---

### 1.2.3 Agent 阅读指南：如何使用这份文档

> **以下内容专门面向智能体读者。人类读者可跳过本小节。**

#### （1）文档内容的四层使用方式

| 使用层级 | 说明 | 文档中对应的标记 |
|---------|------|----------------|
| **系统提示词（System Prompt）** | 文档中的角色定义、任务边界、禁止事项应直接注入或引用到你的 system prompt 中 | 4.10.1 中的提示词模板 YAML 代码块、各场景 3.2.x 中的 Agent 角色定义 |
| **输出校验 Schema** | 文档中的 JSON Schema 代码块应作为你输出的强制校验依据 | 4.10.2 中的 JSON Schema 代码块 |
| **工具权限配置** | 文档中的工具白名单、参数限制、沙箱配置应作为你调用工具前的校验规则 | 4.10.4 中的 tool_whitelist YAML 代码块 |
| **执行流程蓝本** | 文档中的 ASCII 流程图描述了你与其他 Agent 的协作时序，应作为你的任务推进依据 | 3.2.1 ~ 3.2.5 中的交互流程图 |

#### （2）代码块的使用规则

本文件中的所有代码块（`yaml` / `json` / 伪代码）**均为可直接读取与执行的结构化数据**，使用规则如下：

| 代码块类型 | 读取方式 | 用途 |
|-----------|---------|------|
| `yaml` 模板配置（如 4.10.1） | 直接解析为字典 | 作为你的 system prompt / 配置对象 |
| `json` Schema（如 4.10.2） | 使用 JSON Schema 校验器 | 校验你的输出结构是否合规 |
| `yaml` 工具白名单（如 4.10.4） | 直接解析为权限配置 | 在每次工具调用前执行白名单校验 |
| `yaml` 反馈格式（如 4.10.5） | 作为结构化输出模板 | 生成符合格式的反馈数据 |
| ASCII 流程图 | 文本解析（识别箭头、方框、节点标签） | 映射为你的步骤推进逻辑 |
| Token 公式与伪代码 | 提取符号并计算 | 判断是否触发上下文压缩、记忆检索 |

#### （3）章节锚点索引

当你被要求完成某类任务时，可直接跳转到下列锚点章节：

| 任务指令 | 锚点章节 | 你需要做什么 |
|---------|---------|------------|
| "生成课程大纲" | 3.2.1 SCENE-001 + 4.10.1 提示词模板 | 加载模板 → 读取输入规格 → 按输出规格生成 YAML |
| "备一节课" | 3.2.2 SCENE-002 + 4.10.1备课模板 | 同上 |
| "模拟课堂讨论" | 3.2.3 SCENE-003 | 加载学生角色定义 → 按 Message Hub 协议交互 |
| "出题与练习" | 3.2.4 SCENE-004 | 按 exercise_count 生成题目 → 等待学生输入 |
| "批改作业" | 3.2.5 SCENE-005 | 读取参考答案 → 对照 student_submissions → 生成评分 |
| "校验 Agent 输出是否合规" | 4.10.2 JSON Schema + 4.10.3 校验管道 | 按 Schema → 内容边界 → 任务完整性三阶段校验 |
| "清理上下文" | 5.6.3 Token 公式 + 5.6.4 压缩策略 | 检测是否超过窗口 × 50% → 按策略 A/B/C 执行 |
| "写入持久记忆" | 5.6.5 向量索引结构 + 5.6.6 写入时机 | 按 metadata_schema 生成记忆条目 → 写入 LTM |

#### （4）你必须遵守的硬约束优先级

优先级从高到低，上一级未满足时直接拒绝执行下一级：

1. **工具权限**（4.10.4 tool_whitelist）：白名单外工具直接拒绝
2. **输出 Schema**（4.10.2 JSON Schema）：校验失败自动重试 ≤ 3 次
3. **上下文窗口**（5.6.3 Token 公式）：超过模型窗口 × 50% 必须先压缩
4. **任务边界**（4.10.1 template.task_scope.must_not_do）：禁止任务直接拒绝
5. **记忆预算**（5.6.5 retrieval_config.top_k）：记忆检索不超限
6. **Token 预算**（5.1 会话级 Token 上限）：接近阈值告警，达上限暂停

> **Agent 提示：** 如果你在阅读本文档后仍不清楚某任务的执行方式，**不要猜测**。请输出 `NEED_CLARIFICATION: <你的问题>` 格式等待人类确认。

### 1.3 术语约定

| 术语 | 定义 |
|-----|------|
| Agent / 智能体 | 能够自主感知、决策并执行任务的 AI 实体 |
| 多智能体协同 | 多个 Agent 通过消息/协议共同完成目标的过程 |
| 场景（Scene） | 具有明确目标与约束的教学任务类型（如课程规划、虚拟教室） |
| 配置（Config） | 描述 Agent 组合与协作方式的声明式定义 |
| 人机协同（Human-in-the-Loop） | 人类教师在关键节点对 Agent 进行审批、反馈或干预 |
| DeepAgents | LangChain 官方推出的生产级 Agent Harness |
| AgentScope | 阿里通义实验室推出的多智能体一站式开发框架 |

---

## 2. 业务背景与建设目标

### 2.1 业务背景

随着大模型在教育领域的深入应用，单智能体方案已难以覆盖"教学场景多样、角色分工复杂、长链路任务分解"等需求。市面上常见的痛点包括：

1. **场景适配成本高**：不同教学场景（备课、授课、练习、批改）对 Agent 能力要求差异大，需要反复定制与调试
2. **智能体协作能力弱**：单 Agent 难以同时胜任教师、助教、学生、评委等多重角色
3. **可配置性差**：教师缺乏技术能力，无法根据教学需要灵活调整 Agent 组合
4. **可观测性不足**：Agent 的决策过程黑盒化，教师难以追溯与干预

### 2.2 建设目标

| 编号 | 目标 | 说明 |
|-----|------|------|
| GOAL-01 | 动态编排能力 | 根据教学场景自动生成合适的 Agent 组合与协作方式 |
| GOAL-02 | 框架融合能力 | 兼容 DeepAgents 与 AgentScope，发挥各自优势 |
| GOAL-03 | 低代码配置能力 | 教师通过可视化/配置方式完成 Agent 组合，无需编码 |
| GOAL-04 | 人机协同能力 | 支持教师在关键节点审批、反馈、打断与调整 |
| GOAL-05 | 可观测与可审计 | Agent 执行过程可追踪、可回放、可审计 |
| GOAL-06 | 配置复用能力 | 生成的配置可保存、加载、导出为模板复用 |
| GOAL-07 | Harness 约束能力 | 通过提示词模板、任务待办清单、结构化校验、工具沙箱等手段，将 Agent 的行为与输出"驾驭"在需求范围内，避免自由发散 |

### 2.3 非目标（Out of Scope）

为避免范围蔓延，以下内容**不在本期系统需求范围内**：

- 自研大模型推理引擎（使用外部 LLM API）
- 独立的教学内容库建设（依赖已有教学资料）
- 面向学生端 C 端产品化上线（聚焦教师辅助工具）
- 完整的在线课堂视频/直播系统（聚焦 Agent 协同能力）

---

## 3. 用户角色与典型场景

### 3.1 用户角色

| 角色 | 描述 | 典型操作 |
|-----|------|---------|
| 教师 | 核心用户，使用系统完成教学任务 | 输入课程信息、确认 Agent 方案、监控执行、保存配置 |
| 教研人员 | 设计与优化教学场景模板 | 定义新场景、调整 Agent 角色、沉淀模板 |
| 运维管理员 | 部署与维护系统 | 管理模型 API Key、监控运行状态、维护部署环境 |
| 系统开发者 | 扩展与定制 Agent 能力 | 新增 Agent 类型、开发插件、调试协议层 |

### 3.2 典型业务场景

本系统至少支持以下 5 类教学场景，每类场景提供详细交互流程、Agent 角色定义、I/O 规格及边界异常处理。

### 3.2.1 SCENE-001：课程规划

**场景目标**：教师输入课程名称与简介，系统自动生成分章节教学大纲（章节标题 + 课时分配 + 教学目标 + 重难点）与学期进度计划表。

#### Agent 角色定义

| Agent 角色 | 框架 | 职责边界 | 提示词关键词 |
|-----------|------|---------|------------|
| 课程规划 Agent | DeepAgents | 接收用户需求 → 拆解章节结构 → 生成大纲 | "你是资深课程设计专家，擅长将课程目标分解为可执行的教学单元" |
| 教学研究 Agent | DeepAgents | 检索相关知识点 → 标注重难点 → 推荐教学活动 | "你是学科专家，专注于知识点的深度分析与教学难点识别" |
| 大纲整合 Agent | DeepAgents | 汇总前两个 Agent 输出 → 格式化为标准大纲 → 写入 VFS | "你是文档工程师，负责将多源信息整合为结构化教学文档" |

#### 交互流程

```
教师输入
  │
  ▼
SceneAnalyzer 识别 → SCENE-001
  │
  ▼
ConfigGenerator 生成 [规划Agent + 研究Agent + 整合Agent]
  │
  ▼
  ┌──────────────────────────────────────┐
  │ 规划Agent (DeepAgents)               │
  │   write_todos: [分析课程目标, 拆章节, 生成大纲草案] │
  │   VFS: /workspace/planning/draft.md  │
  └──────────────┬───────────────────────┘
                 │ VFS 写入大纲草案
                 ▼
  ┌──────────────────────────────────────┐
  │ 研究Agent (DeepAgents)               │
  │   基于大纲草案，补充知识点、重难点    │
  │   VFS: /workspace/research/output.md │
  └──────────────┬───────────────────────┘
                 │ VFS 读取 + 整合
                 ▼
  ┌──────────────────────────────────────┐
  │ 整合Agent (DeepAgents)               │
  │   合并两份 VFS → 输出最终大纲        │
  │   触发 Harness 校验                  │
  └──────────────┬───────────────────────┘
                 │
                 ▼
         Harness Schema 校验
                 │
          ┌──────┴──────┐
          │ 通过        │ 不通过
          ▼             ▼
       展示给教师    自动重试（≤3次）
                          │
                          ▼
                    人工干预提示
```

#### 输入规格

```yaml
course_name: "初中数学：一元二次方程"       # 必填，字符串，最大 100 字
course_desc: "面向初三学生，讲解一元二次   # 必填，字符串，最大 500 字
             方程的求解与应用"
difficulty: "中等"                          # 选填，枚举 [简单/中等/困难]
total_periods: 10                          # 必填，整数，1~100
teaching_materials: []                     # 选填，教学材料 URL 列表
teacher_id: "t_001"                        # 必填，教师唯一标识
```

#### 输出规格

```yaml
outline:
  course_name: "初中数学：一元二次方程"
  total_periods: 10
  chapters:
    - index: 1
      title: "一元二次方程的概念引入"
      periods: 2
      objectives:
        - "理解一元二次方程的标准形式"
        - "能判断一个方程是否为一元二次方程"
      key_points: ["标准形式 ax²+bx+c=0", "系数条件 a≠0"]
      difficult_points: ["一元二次方程与以前学过的方程的区别"]
      activities: ["生活实例引入", "概念辨析练习"]
    - index: 2
      title: "配方法求解一元二次方程"
      periods: 3
      objectives: [...]
      key_points: [...]
      difficult_points: ["配方的步骤顺序"]
      activities: [...]
  progress_table:
    week: 1
    content: "第1-2章：概念引入与配方法"
    periods: 5
created_at: "2026-06-12T10:00:00Z"
agent_session_id: "sess_course_planning_001"
```

#### Schema 校验规则（Harness）

```json
{
  "required": ["outline", "course_name", "total_periods"],
  "properties": {
    "outline": {
      "type": "object",
      "required": ["chapters", "progress_table"],
      "chapters": {
        "type": "array",
        "minItems": 1,
        "maxItems": 20,
        "items": {
          "required": ["index", "title", "periods", "objectives", "key_points"],
          "periods": { "type": "integer", "minimum": 1, "maximum": 20 }
        }
      }
    }
  }
}
```

#### 边界与异常

| 异常场景 | 系统行为 |
|---------|---------|
| 输入课程名为空 | 返回错误码 ERR-INPUT-001，拒绝执行，提示必填字段 |
| 总课时与章节分配不符（差值 > 1） | 触发教师确认：实际分配 N 课时与输入 M 课时不一致，是否自动调整？ |
| 研究 Agent 3 次重试后仍输出空知识点 | 降级：跳过研究 Agent，仅由规划 Agent 输出基础大纲 |
| 校验失败（章节结构不完整） | Harness 自动触发重试，记录失败原因到审计日志 |
| Token 超预算 | 强制压缩：研究 Agent 中间产物卸载至 VFS，从上下文移除全文 |

---

### 3.2.2 SCENE-002：备课辅助

**场景目标**：教师指定某章节，系统生成配套教案（教学目标 / 教学过程 / 练习题 / 课件大纲 / 教学反思）。

#### Agent 角色定义

| Agent 角色 | 框架 | 职责边界 |
|-----------|------|---------|
| 教案生成 Agent | DeepAgents | 按章节生成结构化教案各节内容 |
| 习题设计 Agent | DeepAgents | 生成基础题 / 提高题 / 拓展题，标注难度与答案 |
| 课件设计 Agent | DeepAgents | 生成 PPT 课件大纲（每页标题 + 要点 + 建议停留时间） |
| 质量审核 Agent | DeepAgents | 审核教案与习题的难度梯度、知识点覆盖度 |

#### 输入规格

```yaml
chapter_ref: "ch_001"                              # 必填，引用课程规划阶段生成的章节 ID
outline_version: "v1.0"                            # 必填，大纲版本号
subject: "数学"                                     # 必填
grade: "初三"                                       # 必填
exercise_count: 5                                  # 必填，基础题数量，1~20
exercise_hard_count: 3                             # 必填，提高题数量，0~10
include_reflection: true                           # 选填，是否包含教学反思模块
```

#### 输出规格

```yaml
lesson_plan:
  chapter_ref: "ch_001"
  teaching_objectives:
    - type: "知识与技能"
      items: ["掌握配方法步骤", "能熟练求解一元二次方程"]
    - type: "过程与方法"
      items: ["经历配方法发现过程", "体会转化思想"]
    - type: "情感态度"
      items: ["增强数学学习信心"]
  teaching_process:
    - phase: "导入"
      duration: 5
      content: "用实际问题引出一元二次方程概念"
      method: "情境创设"
    - phase: "新授"
      duration: 20
      content: "配方法步骤讲解与练习"
      method: "讲授+探究"
  exercises:
    basic:
      - id: "ex_b_001"
        content: "将下列方程化为标准形式：x²+4x+1=0"
        answer: "x²+4x+1=0（已是标准形式，a=1,b=4,c=1）"
    improve:
      - id: "ex_i_001"
        content: "用配方法解：x²-6x+5=0"
        answer: "x²-6x+5=0 → (x-3)²=4 → x-3=±2 → x=5或x=1"
  presentation_outline:
    - slide: 1
      title: "导入：生活中的方程"
      points: ["销售利润问题", "面积切割问题"]
      suggested_duration: 5
    - slide: 2
      title: "新授：配方法三步曲"
      points: ["第一步：移项", "第二步：配方", "第三步：求解"]
      suggested_duration: 15
  reflection_prompt: "本次备课重点关注配方法中'配方'步骤的直观呈现，建议用图形辅助学生理解。"
created_at: "2026-06-12T10:30:00Z"
```

#### 边界与异常

| 异常场景 | 系统行为 |
|---------|---------|
| 输入章节引用不存在 | 返回 ERR-REF-001，提示"未找到对应章节，请先生成课程规划" |
| 习题数量超出范围 | 自动修正为边界值，并提示"已自动调整数量" |
| 质量审核发现知识点重复 | 触发 Harness 告警，标记为 WARNING-001，提供去重建议 |
| 任一 Agent 3 次重试失败 | 降级输出已完成部分，缺失部分标注"生成失败，请手动补充" |

---

### 3.2.3 SCENE-003：虚拟教室

**场景目标**：AI 教师 + N 个 AI 学生模拟真实课堂互动，支持小组讨论、问答、投票、角色扮演等多种课堂模式。

#### Agent 角色定义

| Agent 角色 | 框架 | 数量 | 职责边界 |
|-----------|------|------|---------|
| AI 教师 Agent | AgentScope | 1 | 发起提问、控制课堂节奏、总结讨论、给出点评 |
| AI 学生 Agent | AgentScope | N（可配，默认 3） | 回答问题、发起提问、参与讨论、互相评价 |
| 课堂管理 Agent | DeepAgents | 1 | 维护课堂秩序规则、记录发言、处理异常发言 |

#### 输入规格

```yaml
scene: "虚拟教室"
class_topic: "一元二次方程的配方法"              # 必填
class_mode: "小组讨论"                           # 必填，[讲授/问答/小组讨论/角色扮演]
student_count: 3                                 # 必填，1~10
student_personas:                                # 选填，定义每个 AI 学生的性格
  - id: "student_1"
    name: "小博"
    personality: "积极活跃"
    strategy: "抢答型"
  - id: "student_2"
    name: "小静"
    personality: "沉稳内敛"
    strategy: "深思熟虑型"
  - id: "student_3"
    name: "小思"
    personality: "活跃但易错"
    strategy: "引导纠错型"
interaction_interval: 10                          # 选填，Agent 间最小交互间隔（秒），默认 10
max_turns: 20                                     # 选填，最大交互轮次，默认 20
teacher_can_interrupt: true                       # 选填，教师是否可随时打断，默认 true
```

#### 课堂消息格式（MessageHub）

```json
{
  "msg_id": "msg_003_001",
  "sender": "ai_teacher_001",
  "sender_type": "teacher",
  "content": {
    "text": "同学们，我们来看这道题：解方程 x²-6x+5=0，有没有人想尝试一下？",
    "type": "question",
    "metadata": {
      "difficulty": "中等",
      "target_students": ["student_1", "student_2", "student_3"],
      "expected_answer": "配方法"
    }
  },
  "timestamp": "2026-06-12T10:05:00Z",
  "turn": 1
}
```

```json
{
  "msg_id": "msg_003_002",
  "sender": "student_1",
  "sender_type": "student",
  "content": {
    "text": "老师，我来试试！先把常数移到右边：x²-6x=-5，然后两边加9：(x-3)²=4，所以x-3=±2，x=5或x=1！",
    "type": "answer",
    "metadata": {
      "strategy_used": "抢答型",
      "is_correct": true
    }
  },
  "timestamp": "2026-06-12T10:05:12Z",
  "turn": 2
}
```

#### 输出规格（课堂总结）

```yaml
class_summary:
  topic: "一元二次方程的配方法"
  class_mode: "小组讨论"
  total_turns: 18
  actual_duration_minutes: 25
  student_participation:
    student_1:
     发言次数: 7
      正确率: "85.7%"
      特点: "积极主动，抢答"
    student_2:
      发言次数: 5
      正确率: "100%"
      特点: "沉稳，思路清晰"
    student_3:
      发言次数: 6
      正确率: "50%"
      特点: "积极参与但易出错，教师及时纠错"
  key_insights:
    - "学生对配方法第一步（移项）掌握较好"
    - "学生在配方时容易漏掉加上的常数项"
    - "建议下次加强'完全平方公式'的复习"
  teacher_interventions:
    - turn: 5
      action: "打断"
      reason: "student_3 发言偏离主题"
    - turn: 12
      action: "补充"
      content: "在学生回答后补充了'检验'步骤"
recording_url: "/recordings/class_003_20260612.m4a"
```

#### 边界与异常

| 异常场景 | 系统行为 |
|---------|---------|
| AI 学生连续 3 轮无响应 | 课堂管理 Agent 发起追问："@student_X，你有什么想法吗？" |
| AI 学生发言涉及不当内容 | Harness 内容过滤拦截，消息被静默丢弃，触发告警并记录 |
| 教师打断并修改课堂话题 | 所有 Agent 上下文重置，重新加载新话题提示词模板 |
| 达到 max_turns | 自动触发课堂收尾流程：AI 教师做总结，下课 |
| 任一 Agent 崩溃 | 尝试重启；3 次重启失败则暂停课堂，通知教师 |

---

### 3.2.4 SCENE-004：学生练习

**场景目标**：为学生出题 → AI 引导学生思考 → 同伴讨论 → 给出个性化反馈与下一阶段建议。

#### Agent 角色定义

| Agent 角色 | 框架 | 职责边界 |
|-----------|------|---------|
| 出题 Agent | DeepAgents | 根据章节知识点，从题库或动态生成梯度练习题 |
| 答疑 Agent | AgentScope | 接收学生答案，引导式追问，不直接给答案 |
| 同伴 Agent | AgentScope | 模拟同伴给出不同解法或错误示范，供对比学习 |
| 评估 Agent | DeepAgents | 分析学生答题路径，给出个性化反馈与学习建议 |

#### 输入规格

```yaml
chapter_ref: "ch_001"
student_level: "中等"                           # 必填，[差/中/良/优]，影响题目难度
exercise_count: 3                                 # 必填，每轮练习题数量
difficulty_gap: true                              # 必填，是否包含梯度递进题目
include_hint: true                                # 选填，是否在学生卡住时提供hint
max_hint_per_question: 2                          # 选填，每题最多 hint 次数
peer_discussion_rounds: 2                        # 选填，同伴讨论轮次，默认 2
```

#### 输出规格

```yaml
practice_session:
  student_id: "stu_001"
  chapter_ref: "ch_001"
  exercises:
    - exercise_id: "prac_001"
      content: "用配方法解方程：x²+2x-8=0"
      hints:
        - id: 1
          content: "提示1：先把这个方程化成 (x+m)²=n 的形式"
          triggered: false
        - id: 2
          content: "提示2：两边同时加上1（因为(b/2)²=1）"
          triggered: false
      student_answer: "x²+2x=8 → (x+1)²=9 → x+1=±3 → x=2或x=-4"
      is_correct: true
      peer_example:
        content: "同桌的解法：x²+2x-8=0 → Δ=4+32=36 → x=(-2±6)/2 → x=2或x=-4"
        note: "同桌用了求根公式，两种方法结果一致，验证了答案"
      feedback:
        score: 100
        strengths: ["移项正确，配方正确"]
        improvements: []
        next_step: "可以尝试更复杂的系数，如 x²+4x+2=0"
    - exercise_id: "prac_002"
      content: "已知方程 x²+bx+4=0 有两个相等实根，求 b 的值"
      hints: [...]
      student_answer: "b=±4"
      is_correct: false
      peer_example: [...]
      feedback:
        score: 60
        strengths: ["理解判别式Δ=0"]
        improvements: ["漏算了 b²-16=0 → b²=16 → b=±4", "实际答案是 b=±4，此题学生碰巧正确但过程不严谨"]
        next_step: "建议复习'完全平方式'的构成条件"
  session_summary:
    total_score: 180
    average_score: 80.0
    weak_topics: ["判别式的计算严谨性"]
    strong_topics: ["配方法基本步骤"]
    recommended_next_chapter: "ch_002：一元二次方程的公式法"
```

#### 边界与异常

| 异常场景 | 系统行为 |
|---------|---------|
| 学生连续 2 题答错 | 答疑 Agent 主动触发 hint，而不是继续出下一题 |
| 学生 2 次 hint 后仍答错 | 评估 Agent 标记为"需要人工关注"，通知教师 |
| 学生输入为空或乱码 | 记录为无效作答，跳过此题，记录 ERR-PRAC-INVALID |
| 评估 Agent 发现系统性错误 | 自动追加"知识点复习建议"到 session_summary |

---

### 3.2.5 SCENE-005：作业批改

**场景目标**：教师上传一个或多个学生的作业文件（PDF/TXT/图片），系统批量批阅并给出每份作业的评分、逐题点评、总体评语与个性化改进建议。

#### Agent 角色定义

| Agent 角色 | 框架 | 职责边界 |
|-----------|------|---------|
| 作业解析 Agent | DeepAgents | 读取作业文件，提取每道题的答案文本（支持 PDF OCR） |
| 批改 Agent | DeepAgents | 对照标准答案逐题评分，给出得分理由 |
| 评语生成 Agent | DeepAgents | 综合本次作业表现，生成鼓励性评语与改进建议 |
| 汇总报告 Agent | DeepAgents | 汇总全班作业数据，生成班级统计报告 |

#### 输入规格

```yaml
homework_batch:
  homework_id: "hw_001"
  course_id: "math_g9_001"
  chapter_ref: "ch_001"
  standard_answers:                              # 必填，教师提供的参考答案
    - question_id: "q1"
      answer: "x²+4x+1=0（已是标准形式，a=1,b=4,c=1）"
      max_score: 10
    - question_id: "q2"
      answer: "配方法：移项→配方→求解"
      max_score: 15
  submissions:
    - student_id: "stu_001"
      file_url: "/uploads/stu_001_hw001.pdf"
      file_type: "pdf"
    - student_id: "stu_002"
      file_url: "/uploads/stu_002_hw001.pdf"
      file_type: "pdf"
  include_class_summary: true                    # 选填，是否生成班级汇总报告
```

#### 输出规格

```yaml
grading_results:
  homework_id: "hw_001"
  total_submissions: 2
  processed_at: "2026-06-12T11:00:00Z"
  individual_reports:
    - student_id: "stu_001"
      total_score: 23
      max_score: 25
      percentage: 92
      grade: "优秀"
      question_scores:
        - question_id: "q1"
          score: 10
          feedback: "答案完全正确，标准形式识别准确"
        - question_id: "q2"
          score: 13
          feedback: "配方法步骤基本正确，但在'配方'步骤漏写了常数项，建议加强完全平方公式练习"
      overall_comment: "本次作业完成得很棒！配方法掌握较好，注意细节会更加完美。继续加油！"
      improvement_tips:
        - "建议复习：(a±b)² = a²±2ab+b² 的展开"
        - "可以尝试多做几步综合计算题"
    - student_id: "stu_002"
      total_score: 15
      max_score: 25
      percentage: 60
      grade: "及格"
      question_scores: [...]
      overall_comment: "第一题做得不错，但第二题需要重新学习配方法的完整流程。建议观看课程回放中'配方法三步曲'部分。"
      improvement_tips: [...]
  class_summary:
    total_students: 2
    average_score: 76.5
    score_distribution:
      优秀: 1
      良好: 0
      及格: 1
      不及格: 0
    common_mistakes:
      - topic: "配方法第二步"
        frequency: "50%"
        description: "在配方时忘记加上(b/2)²，或加错数值"
    recommended_review_topics:
      - "完全平方公式的构成条件"
      - "配方法中'移项'的规范化操作"
```

#### 边界与异常

| 异常场景 | 系统行为 |
|---------|---------|
| 文件格式不支持（除 PDF/TXT/图片） | 返回 ERR-FILE-001，提示支持的文件格式列表 |
| PDF OCR 识别置信度 < 60% | 标记为"识别困难"，提示教师手动核对答案 |
| 学生漏答某题 | 自动给 0 分，并在反馈中注明"未作答" |
| 全班平均分异常（< 40% 或 > 95%） | 触发 Harness 告警，提示教师"成绩分布异常，请确认参考答案是否正确" |
| 批改 Agent 3 次重试后仍无法评分 | 标记为"待人工批改"，不影响其他作业处理 |

---

## 4. 功能需求

### 4.1 功能需求总览

| 模块编号 | 模块名称 | 优先级 |
|---------|---------|--------|
| FR-01 | 场景识别与分析 | P0 |
| FR-02 | Agent 配置动态生成 | P0 |
| FR-03 | Agent 编排与调度 | P0 |
| FR-04 | 框架协议转换 | P0 |
| FR-05 | 配置持久化与管理 | P1 |
| FR-06 | 人机协同接口 | P1 |
| FR-07 | 可观测性与审计 | P1 |
| FR-08 | 可视化配置界面（可选） | P2 |
| FR-09 | Harness 约束层 | P0 |

### 4.2 FR-01：场景识别与分析

**功能描述**：根据用户输入的课程信息，自动识别教学场景类型并产出推荐方案。

| 需求项 | 说明 |
|--------|------|
| 输入 | 课程名称、课程简介、教学材料（可选）、用户选择模式 |
| 输出 | 场景类型、推荐 Agent 组合、初始配置模板 |
| 识别准确率 | 对预置 5 类场景的识别准确率目标 ≥ 85% |
| 人工修正 | 系统推荐结果应支持教师修正覆盖 |

### 4.3 FR-02：Agent 配置动态生成

**功能描述**：根据场景类型，自动生成 Agent 定义、角色职责、通信关系与协作模式。

| 需求项 | 说明 |
|--------|------|
| Agent 角色定义 | 至少支持 teacher / student / assistant / evaluator 四类角色 |
| 框架选择 | 每个 Agent 可独立选择 DeepAgents / AgentScope / 通用框架 |
| 协作模式 | 支持主从、多角色、流水线三种基础协作模式 |
| 配置输出 | 产出标准化的 YAML/JSON 配置，供加载与执行 |
| Harness 策略绑定 | 每个 Agent 配置必须绑定对应的提示词模板、输出 schema 与工具白名单；缺省时使用框架默认策略，不得"无约束"运行 |

### 4.4 FR-03：Agent 编排与调度

**功能描述**：依据生成的配置，实际运行 Agent 并协调其间通信。

| 需求项 | 说明 |
|--------|------|
| 启动能力 | 支持一键启动多个 Agent |
| 消息路由 | Agent 间消息可按配置规则动态传递 |
| 状态同步 | 全局状态（任务进度、中间产物）在 Agent 间保持一致 |
| 失败重试 | 单 Agent 失败时应具备重试与降级机制 |
| 上下文主动控制 | 编排层在每轮交互前检查当前上下文 Token 量；超过阈值时自动触发摘要压缩/旧消息遗忘/中间产物卸载 |
| 记忆联动 | 每个 Agent 执行前，编排层应根据当前任务主题从持久记忆中检索 ≤ N 条相关记忆注入上下文（N 可配置） |
| Harness 执行绑定 | 每个 Agent 在执行前由编排层加载其对应的 Harness 约束（提示词模板、输出 schema、工具白名单），在 Agent 实例生命周期内持续生效，不可被 Agent 内部推理覆盖或绕过 |

### 4.5 FR-04：框架协议转换

**功能描述**：在 DeepAgents 与 AgentScope 之间搭建统一消息协议层，屏蔽框架差异。

| 需求项 | 说明 |
|--------|------|
| 统一消息格式 | 定义 UnifiedMessage，包含发送方、接收方、意图、内容、元数据 |
| 格式映射 | DeepAgents 的 AgentState / write_todos / VFS file 与 AgentScope 的 Message / msghub 互相映射 |
| 可扩展性 | 未来新增第三方 Agent 框架时，协议层应支持插拔式扩展 |

### 4.6 FR-05：配置持久化与管理

**功能描述**：配置可保存至本地文件系统，支持加载、列举、导出模板。

| 需求项 | 说明 |
|--------|------|
| 保存格式 | YAML / JSON |
| 目录结构 | 区分 templates（场景模板）、presets（预设）、user_saved（用户保存）、runtime（运行时） |
| 配置生命周期 | 草稿 → 预览 → 保存 / 执行 |
| 模板导出 | 支持将已保存配置导出为可复用模板 |

### 4.7 FR-06：人机协同接口

**功能描述**：在关键节点引入人类教师的确认、反馈与干预。

| 需求项 | 说明 |
|--------|------|
| 人工审批 | Agent 发起的关键决策需教师确认 |
| 反馈收集 | 支持对 Agent 输出进行评分与批注 |
| 实时打断 | 运行过程中教师可中断指定 Agent |
| 动态调整 | 运行时可调整 Agent 数量、角色、策略 |

### 4.8 FR-07：可观测性与审计

**功能描述**：Agent 执行过程可追踪、可回放、可审计。

| 需求项 | 说明 |
|--------|------|
| 日志记录 | 记录每个 Agent 的输入、输出、决策依据 |
| 运行状态 | 可视化展示当前任务进度与 Agent 状态 |
| 审计回放 | 支持按时间轴回放完整执行过程 |

### 4.9 FR-08：可视化配置界面（可选）

**功能描述**：通过 Web 界面（React/Vue）提供图形化配置能力，降低技术门槛。

| 需求项 | 说明 |
|--------|------|
| 场景选择 | 图形化选择教学场景 |
| Agent 拖拽编排 | 通过拖拽方式调整 Agent 组合与关系 |
| 实时预览 | 配置修改后可即时预览效果 |
| REST API 暴露 | 后端通过 FastAPI 暴露接口供前端调用 |

### 4.10 FR-09：Harness 约束层

**功能描述**：引入 Harness（驾驭层）理念——通过预设提示词模板、任务待办清单、结构化输出校验、工具权限边界与反馈闭环，将 Agent 的行为与输出严格约束在需求范围内，防止自由发散或偏离教学目标。

#### 4.10.1 提示词模板结构

每个场景对应一个模板文件（YAML/JSON），模板分为 6 个固定区块，Agent 无法通过推理修改其中任何区块的内容。

```yaml
template_id: "tpl_scene001_planner_v1.0"
scene_type: "SCENE-001"
agent_role: "课程规划 Agent"
version: "1.0"
last_updated: "2026-06-01"

# 【区块 1：角色定义 - 锁定，不可被 Agent 覆盖】
role_definition:
  role: "资深课程设计专家"
  specialty: "将课程目标分解为可执行的教学单元，擅长 K12 数学课程规划"
  tone: "专业、严谨、结构清晰"

# 【区块 2：任务边界 - 锁定】
task_scope:
  must_do:
    - "根据 {course_name} 和 {course_desc} 生成课程大纲"
    - "确保章节数量与 {total_periods} 匹配（允许 ±1 的调整容差）"
    - "每章必须包含：title、periods、objectives、key_points"
  must_not_do:
    - "不得生成超出 {course_desc} 范围的知识点"
    - "不得修改教师指定的 {total_periods}"
    - "不得在输出中包含与教学无关的内容"
    - "不得在未完成所有章节前提前结束"

# 【区块 3：输出格式规范 - 锁定】
output_format:
  format: "YAML"
  schema_ref: "schema_scene001_outline_v1.0"  # 引用下方 JSON Schema
  max_output_tokens: 4096

# 【区块 4：禁止话题列表 - 锁定】
prohibited_topics:
  - "超出 {course_desc} 范围的内容"
  - "广告、推销内容"
  - "任何形式的政治、宗教、色情、暴力内容"
  - "未经教师授权的外部链接"

# 【区块 5：待办清单模板 - 由 write_todos 驱动】
todo_template:
  - id: 1
    label: "分析课程目标"
    description: "阅读 {course_name} 和 {course_desc}，提取课程级别目标"
    required: true
  - id: 2
    label: "拆解章节结构"
    description: "根据目标数量和课时总数，将课程拆分为章节"
    required: true
  - id: 3
    label: "生成大纲草案"
    description: "为每个章节补充 title、periods、objectives"
    required: true
  - id: 4
    label: "写入 VFS"
    description: "将大纲写入 /sessions/{session_id}/working/outline_draft.md"
    required: true

# 【区块 6：注入信息 - 动态插入，不锁定】
dynamic_injection:
  system_variables:
    - course_name: "{{course_name}}"
    - course_desc: "{{course_desc}}"
    - total_periods: "{{total_periods}}"
    - difficulty: "{{difficulty}}"
  retrieved_memories: "{{retrieved_from_ltm}}"  # 从 LTM 检索注入，不超过 3 条
```

#### 4.10.2 结构化输出 Schema 示例

以下为 SCENE-001 课程规划的输出 Schema（Harness 据此执行校验）：

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "schema_id": "schema_scene001_outline_v1.0",
  "type": "object",
  "required": ["outline", "course_name", "total_periods", "created_at"],

  "properties": {
    "outline": {
      "type": "object",
      "required": ["course_name", "chapters", "progress_table"],
      "properties": {
        "course_name": {
          "type": "string",
          "minLength": 1,
          "maxLength": 100,
          "description": "课程名称，必须与输入一致"
        },
        "total_periods": {
          "type": "integer",
          "minimum": 1,
          "maximum": 100,
          "description": "总课时数，允许与输入偏差 ±1"
        },
        "chapters": {
          "type": "array",
          "minItems": 1,
          "maxItems": 20,
          "items": {
            "type": "object",
            "required": ["index", "title", "periods", "objectives", "key_points"],
            "properties": {
              "index": {
                "type": "integer",
                "minimum": 1,
                "description": "章节序号，必须连续"
              },
              "title": {
                "type": "string",
                "minLength": 2,
                "maxLength": 50,
                "description": "章节标题"
              },
              "periods": {
                "type": "integer",
                "minimum": 1,
                "maximum": 20,
                "description": "本章课时数"
              },
              "objectives": {
                "type": "array",
                "minItems": 1,
                "maxItems": 5,
                "items": { "type": "string" },
                "description": "教学目标列表，每项不超过 50 字"
              },
              "key_points": {
                "type": "array",
                "minItems": 1,
                "maxItems": 5,
                "items": { "type": "string" },
                "description": "重点知识列表"
              },
              "difficult_points": {
                "type": "array",
                "maxItems": 3,
                "items": { "type": "string" },
                "description": "难点知识列表，可为空"
              },
              "activities": {
                "type": "array",
                "maxItems": 5,
                "items": { "type": "string" },
                "description": "推荐教学活动，可为空"
              }
            }
          }
        },
        "progress_table": {
          "type": "array",
          "description": "进度计划表",
          "items": {
            "type": "object",
            "required": ["week", "content", "periods"],
            "properties": {
              "week": { "type": "integer", "minimum": 1 },
              "content": { "type": "string" },
              "periods": { "type": "integer", "minimum": 1 }
            }
          }
        }
      }
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "生成时间，ISO 8601 格式"
    }
  }
}
```

#### 4.10.3 校验管道（Validation Pipeline）

Agent 输出经由以下三阶段校验，全部通过方才交付：

```
Agent 输出
   │
   ▼
[阶段1：Schema 校验]
   ├── JSON parse 检查（输出是否为合法 JSON/YAML）
   ├── 必填字段检查（required fields）
   ├── 类型检查（string/integer/array/boolean）
   ├── 数值范围检查（minimum/maximum/length）
   ├── 枚举值检查（enum）
   └── 自定义规则检查
         │
         ├─ PASS → [阶段2]
         └─ FAIL → 重试（≤3次），记录失败原因
                     │
                     ▼
              3次失败 → 人工干预告警

[阶段2：内容边界过滤]
   ├── 禁止话题检查（prohibited_topics 命中）
   ├── 关键词过滤（自定义词表，如"广告"、"推销"）
   ├── 长度上限检查（max_output_tokens）
   └── 主题相关性检查（与 {course_topic} 的语义相似度 < 0.3 则告警）
         │
         ├─ PASS → [阶段3]
         └─ FAIL → 触发重生成，记录过滤原因

[阶段3：任务完整性检查]
   ├── 待办清单覆盖率（write_todos items_covered / total_items >= 100%）
   ├── 章节数量与课时数一致性（sum(chapters.periods) ≈ total_periods ±1）
   └── 无新增禁止任务（Agent 是否自行新增了超出模板范围的任务）
         │
         ├─ PASS → 交付给用户/下游 Agent
         └─ FAIL → 触发针对性补充或重生成
```

#### 4.10.4 工具权限白名单配置

每个 Agent 实例必须绑定一份工具白名单（Harness 在每次工具调用前校验）：

```yaml
agent_id: "agent_scene001_researcher_001"
scene_type: "SCENE-001"
framework: "DeepAgents"

# 【工具白名单 - 白名单外工具一律拒绝】
tool_whitelist:
  allowed_tools:
    - name: "read_file"
      params:
        path:
          type: "string"
          required: true
          pattern: "^/sessions/.*\\.md$"  # 仅允许读取工作目录下的 .md 文件
        max_chars:
          type: "integer"
          default: 8192
      max_calls_per_session: 50
      description: "读取 VFS 中的已有文档"

    - name: "write_file"
      params:
        path:
          type: "string"
          required: true
          pattern: "^/sessions/.*\\.md$"
        content:
          type: "string"
          required: true
          max_length: 10240
      max_calls_per_session: 20
      description: "写入中间产物到 VFS"

    - name: "search_knowledge"
      params:
        query:
          type: "string"
          required: true
          max_length: 200
        top_k:
          type: "integer"
          default: 3
      max_calls_per_session: 10
      description: "从知识库检索相关教学资料"

  # 【工具黑名单 - 明确禁止，无论是否在白名单内】
  denied_tools:
    - name: "exec_shell"
      reason: "不允许在课程规划场景中执行系统命令"
    - name: "send_external_request"
      reason: "不允许访问外部 API，防止信息泄露"
    - name: "read_file"
      # 即使 read_file 在白名单中，以下路径模式仍被禁止
      path_pattern_blacklist:
        - "^/etc/.*"
        - "^/root/.*"
        - "^/home/.*"

  # 【参数级限制 - 白名单通过后，仍需检查参数合法性】
  param_constraints:
    write_file:
      content:
        max_length: 10240                       # 单次写入不超过 10KB
        prohibited_keywords: ["password", "api_key", "secret"]  # 禁止写入敏感词

# 【沙箱配置 - Shell/Code 类工具必须在此配置】
sandbox_config:
  enabled: true
  provider: "modal"                             # modal / deno / daytona
  timeout_seconds: 30
  allowed_fqdns: ["api.eduagents.local"]        # 仅允许访问白名单域名
```

#### 4.10.5 反馈闭环机制

教师对 Agent 输出的反馈必须结构化回写，用于 Harness 持续优化：

```yaml
feedback_entry:
  feedback_id: "fb_001"
  session_id: "sess_001"
  agent_id: "agent_scene001_planner_001"
  timestamp: "2026-06-12T10:05:00Z"

  # 教师评分（0.0~1.0）
  rating: 0.6

  # 教师操作
  action: "reject"                               # approve / reject / revise

  # 拒绝/批注理由（必填）
  reason: "第2章课时分配错误：标注3课时但内容覆盖了5课时的知识点"

  # 具体批注位置
  annotations:
    - field: "outline.chapters[1].periods"
      expected_value: 5
      actual_value: 3
      comment: "这章内容很多，至少需要5课时"

  # Harness 自动处理
  auto_actions:
    - action: "inject_correction"
      target_field: "outline.chapters[1].periods"
      value: 5
      trigger_retry: true
    - action: "update_template"
      template_id: "tpl_scene001_planner_v1.0"
      note: "第2章课时判断逻辑需加强"
      new_version: "v1.1"                       # 创建新版本模板

  # 用于 LTM 更新
  ltm_update:
    memory_id: "mem_session001_conclusion"
    update_fields:
      rating: 0.6
      teacher_feedback: "第2章课时分配需更细致"
      corrected_value: "periods: 5"
```

#### 4.10.6 需求汇总表

| 需求项 | 说明 |
|--------|------|
| 场景级提示词模板 | 每个场景拥有独立的 system prompt 模板，6 个固定区块，模板可配置，不可被 Agent 内部推理覆盖 |
| 显式任务待办（todo check） | Agent 的每一步执行必须命中一条待办项；完成前不可跳过或自行新增超出模板的任务 |
| 结构化输出校验 | Agent 输出需遵循预定义 schema（JSON/YAML/教学文档结构），Harness 在输出接收阶段执行三阶段校验；校验失败自动触发重试而非交付给用户 |
| 内容边界过滤 | 对输出内容进行关键词/主题过滤，与当前教学主题无关或出现违规内容时标记为无效并触发重生成 |
| 工具权限白名单 | 每个 Agent 的可用工具由配置决定，Harness 在工具调用前做权限校验；未授权工具调用直接拒绝并记录审计 |
| 沙箱执行环境 | 代码/Shell 类调用必须在沙箱中执行，Harness 负责管理沙箱生命周期与输入输出隔离 |
| 反馈闭环 | 教师对 Agent 输出的反馈（评分、批注、拒绝）必须回写，用于迭代提示词模板或直接驱动重生成 |
| 策略可插拔 | Harness 的各条约束策略（校验 schema、过滤词表、权限配置、重试次数）应支持通过配置文件插拔与调整 |
| 约束失效告警 | 连续 N 次（默认 3 次）校验失败或超 Token 预算时，停止自动重试并转入人工干预流程 |

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
│  │  内容：中间产物（大纲草案、教案片段、课堂记录）      │   │
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
| **工作记忆 WM** | VFS 文件系统 `/sessions/{id}/working/` | 各 Agent 生成的中间产物：大纲草案、教案片段、课堂记录、评估报告 | 会话结束后可选择保留 N 天（默认 7 天） | 单文件 ≤ 4096 Token，超出自动分片 |
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

## 6. 系统边界与外部依赖

### 6.1 系统边界

```
┌─────────────────────────────────────────────────────┐
│                     EduAgents 系统                    │
│                                                      │
│  ┌──────────┐  ┌───────────┐  ┌────────────────┐    │
│  │ 场景识别  │  │ 配置生成  │  │  Agent 编排层  │    │
│  └──────────┘  └───────────┘  │  (DeepAgents   │    │
│                               │   AgentScope)  │    │
│  ┌──────────┐  ┌───────────┐  └────────────────┘    │
│  │ 协议转换  │  │ 配置管理  │  ┌────────────────┐    │
│  └──────────┘  └───────────┘  │ 人机协同 & 观测 │    │
│                               └────────────────┘    │
└─────────┬──────────────────────────────┬────────────┘
          │                              │
          ▼                              ▼
   外部 LLM API 服务           本地文件系统 / 配置存储
   (OpenAI / Qwen / Claude ...)
```

### 6.2 外部依赖

| 依赖类型 | 依赖项 | 说明 |
|---------|--------|------|
| Agent 框架 | DeepAgents | LangChain 官方 Agent Harness |
| Agent 框架 | AgentScope | 阿里通义实验室多智能体框架 |
| 运行时 | LangGraph | 图编排执行引擎 |
| 模型服务 | 外部 LLM API | 如通义千问、GPT、Claude 等 |
| 存储 | 本地文件系统 | 保存配置、中间产物、日志 |
| 沙箱（可选） | Modal / Deno / Daytona | 代码安全执行环境 |

---

## 7. 验收标准

### 7.1 功能验收

| 验收项 | 通过标准 |
|--------|---------|
| FR-01 场景识别 | 对 5 类典型教学输入，能够产出对应场景识别结果 |
| FR-02 配置生成 | 可生成结构完整、字段一致的 YAML 配置文件 |
| FR-03 Agent 编排 | 可按配置启动多个 Agent 并完成一次完整协同任务 |
| FR-04 协议转换 | DeepAgents 与 AgentScope Agent 可互相通信协作 |
| FR-05 配置管理 | 可 save / load / list / export 配置，文件格式正确 |
| FR-06 人机协同 | 运行中至少一次完成人工审批或打断流程 |
| FR-07 可观测 | 执行完成后可查看完整日志与时间轴回放 |
| FR-09 Harness 约束 | 任一 Agent 输出必须通过 Harness 校验管道；未绑定约束的 Agent 不得启动 |

### 7.2 非功能验收

| 验收项 | 通过标准 |
|--------|---------|
| 性能 | 关键路径响应时间满足 5.1 节指标 |
| 可用性 | 新用户 15 分钟内完成首次使用 |
| 可扩展性 | 可通过配置新增一个自定义场景 |
| 安全性 | 敏感信息不出现在日志与输出中 |
| 记忆与上下文控制 | 上下文 Token 量不超过窗口 50%，会话级记忆可被检索并复用 |
| Harness 有效性 | Harness 校验通过率 ≥ 95%，未授权工具调用 100% 拦截 |

### 7.3 示例验收用例

**用例 1：课程规划场景**

1. 输入课程名称"初中数学：一元二次方程"及简介
2. 系统应识别为 SCENE-001（课程规划），推荐 [规划 Agent + 研究 Agent] 组合
3. 生成初始配置，教师确认后执行
4. 产出完整教学大纲与进度计划
5. 可将配置保存到 user_saved/ 目录

**用例 2：虚拟教室场景**

1. 选择"虚拟教室"，输入学生人数 3、互动模式"协作讨论"
2. 系统生成 1 个 AI 教师 + 3 个 AI 学生的 Agent 组合（AgentScope）
3. 启动后 Agent 通过 Message Hub 自主讨论
4. 教师可实时监控并干预讨论过程
5. 执行完成后可回放完整对话时间轴

**用例 3：Harness 约束验证（反例测试）**

1. 启动任意一个教学场景的 Agent 组合
2. 模拟 Agent 生成不符合 schema 的输出（如缺字必填字段、格式错误）
3. Harness 应拒绝该输出并自动触发重生成（至少 1 次）
4. 连续 3 次失败后，应转入人工干预流程并告警
5. 审计日志中应记录完整的失败原因与重试过程

---

## 8. 版本路线图（建议）

| 版本 | 计划内容 | 交付物 |
|-----|---------|--------|
| v0.1 | 核心骨架：Harness 约束层（提示词模板 + 输出 schema + 权限白名单） + 单框架编排（DeepAgents） | 可运行的 CLI Demo，Harness 校验流水线首次可用 |
| v0.2 | 引入 AgentScope，完成协议转换层与跨框架通信；Harness 支持多 Agent 同时约束 | 跨框架协作 Demo |
| v0.3 | 人机协同接口 + 配置持久化管理 + Harness 模板版本化 | 教师可参与的完整流程 |
| v0.4 | 可观测性与审计（日志、回放、指标）+ Harness 校验统计面板 | 监控面板 |
| v0.5 | 可视化配置界面（Web） | 前后端全链路产品 |
| v1.0 | 性能优化 + 稳定发布 + 模板库沉淀 | 生产可用版本 |

---

## 9. 风险与待决事项

| 风险项 | 描述 | 应对策略 |
|--------|------|---------|
| R-01 模型能力差异 | 不同 LLM 在同一 Agent 逻辑下表现差异大 | 在协议层引入模型抽象，支持多模型对比测试 |
| R-02 框架版本兼容 | DeepAgents / AgentScope 仍在演进，API 可能变化 | 锁定版本号并在协议层封装隔离 |
| R-03 成本控制 | 多 Agent 长链路任务 Token 消耗高 | 引入 Token 预算与自动摘要机制 |
| R-04 内容安全 | Agent 可能输出不适合教育场景的内容 | 接入内容审核服务并配置拦截规则 |
| R-05 教师学习成本 | 非技术背景教师使用门槛高 | 提供可视化界面 + 场景模板库 + 使用视频 |
| R-06 Harness 过度约束 | 严格校验可能影响 Agent 的灵活度与创造性 | 分层策略：关键路径强制校验，可选路径宽松校验，支持按场景调整 |

---

## 10. 参考文档

| 文档 | 来源 |
|------|------|
| [EduAgents 设计文档](design_document.md) | 本仓库 |
| [DeepAgents 概述](deepagents_overview.md) | 本仓库 |
| [AgentScope 概述](agentscope_overview.md) | 本仓库 |
| [框架对比](comparison.md) | 本仓库 |
| [选型建议](selection_guide.md) | 本仓库 |
| DeepAgents 官方文档 | LangChain |
| AgentScope GitHub 仓库 | 阿里通义实验室 |
| LangChain / LangGraph 官方文档 | LangChain |

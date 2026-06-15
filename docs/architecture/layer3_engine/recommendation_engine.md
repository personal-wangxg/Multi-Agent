# 节点推荐引擎详细设计

**文档版本**：v1.0  
**创建日期**：2026-06-15  
**父文档**：[roadmap.md](../roadmap.md)  
**相关需求**：FR-06（节点推荐引擎）

---

## 1. 设计目标

节点推荐引擎是 EduAgents 动态学习路径的核心组件，负责在学生完成当前节点学习后，推荐下一个最适合的学习节点。

| 设计原则 | 说明 |
|---------|------|
| **网络结构优先** | 优先推荐知识网络中结构上重要的节点（前置依赖、跨层关系） |
| **表现驱动** | 基于学生历史表现数据动态调整推荐权重 |
| **层次匹配** | 推荐节点需与学生的目标学习层次匹配 |
| **可解释性** | 每个推荐必须附带清晰的推荐理由，支持学生做出知情选择 |

---

## 2. 架构组件

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    节点推荐引擎架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│   │ 候选生成器   │    │  权重计算器  │    │ 多样性保证   │    │
│   │              │    │              │    │    模块      │    │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    │
│          │                   │                   │             │
│          ▼                   ▼                   ▼             │
│   ┌──────────────────────────────────────────────────────┐    │
│   │                  推荐推理引擎                        │    │
│   │   ┌─────────────────────────────────────────────┐   │    │
│   │   │  评分公式: S = Wn×Sn + Wp×Sp + Wh×Sh       │   │    │
│   │   └─────────────────────────────────────────────┘   │    │
│   └───────────────────┬──────────────────────────────────┘    │
│                       │                                        │
│          ┌────────────┼────────────┐                           │
│          ▼            ▼            ▼                           │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                    │
│   │ 推荐解释 │  │ 选择记录 │  │ 路径更新 │                    │
│   │ 生成器   │  │   模块   │  │   模块   │                    │
│   └──────────┘  └──────────┘  └──────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 组件职责

| 组件 | 职责 | 核心功能 |
|-----|------|---------|
| **候选生成器** | 根据当前节点和知识网络生成候选节点集 | 前置节点扩展、跨层节点获取、同主题节点 |
| **权重计算器** | 计算候选节点的各项评分权重 | 网络结构分、表现分、层次匹配分 |
| **多样性保证模块** | 确保推荐结果的多样性和平衡性 | 层间平衡、难度梯度、主题分散 |
| **推荐推理引擎** | 综合权重计算最终推荐分数 | 归一化处理、分级排序、Top-K筛选 |
| **推荐解释生成器** | 生成可理解的推荐理由 | 三要素提取、自然语言生成 |
| **选择记录模块** | 记录学生选择行为用于后续优化 | 选择追踪、反馈收集 |
| **路径更新模块** | 更新学生学习路径状态 | 路径记录、掌握状态同步 |

---

## 3. 输入规格

### 3.1 推荐请求数据结构

```yaml
recommendation_request:
  request_id: "req_001"
  timestamp: "2026-06-15T10:00:00Z"
  
  # 学生标识
  student_id: "student_001"
  
  # 当前节点信息
  current_node:
    node_id: "node_math_quadratic_tool_001"
    layer: "tool"
    mastery_status: "mastered"          # not_started / in_progress / mastered / needs_attention
  
  # 已掌握的节点列表
  mastery_confirmed:
    - node_id: "node_math_linear_tool_001"
      mastered_at: "2026-06-10T14:30:00Z"
    - node_id: "node_math_linear_skill_001"
      mastered_at: "2026-06-11T09:00:00Z"
  
  # 目标学习层次
  target_level: "skill"                # concept / skill / tool
  
  # 知识网络引用
  knowledge_network:
    network_id: "network_math_grade9_2026"
    version: "v1.0"
```

### 3.2 输入字段说明

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| request_id | string | 是 | 推荐请求唯一标识 |
| timestamp | datetime | 是 | 请求时间戳 |
| student_id | string | 是 | 学生唯一标识 |
| current_node | object | 是 | 当前节点信息 |
| current_node.node_id | string | 是 | 当前节点ID |
| current_node.layer | enum | 是 | 当前节点层次 |
| current_node.mastery_status | enum | 是 | 当前节点掌握状态 |
| mastery_confirmed | array | 是 | 已掌握节点列表（最近30天） |
| target_level | enum | 是 | 目标学习层次 |
| knowledge_network | object | 是 | 知识网络引用 |

---

## 4. 推荐算法

### 4.1 评分公式

推荐引擎采用加权评分公式，综合考虑网络结构、表现匹配和层次匹配三个维度：

```
S_total = Wn × Sn + Wp × Sp + Wh × Sh
```

| 符号 | 含义 | 默认权重 |
|-----|------|---------|
| S_total | 总评分 | - |
| Wn | 网络结构权重 | 0.60 (60%) |
| Wp | 表现分权重 | 0.30 (30%) |
| Wh | 层次匹配权重 | 0.10 (10%) |
| Sn | 网络结构分 | 0.0~1.0 |
| Sp | 表现匹配分 | 0.0~1.0 |
| Sh | 层次匹配分 | 0.0~1.0 |

### 4.2 网络结构分 (Sn)

网络结构分反映节点在知识网络中的重要性和可达性：

```yaml
sn_calculation:
  # 前置依赖得分（前置节点已掌握则加分）
  prerequisite_score:
    formula: "掌握的前置节点数 / 总前置节点数"
    weight: 0.4
  
  # 后继广度得分（可解锁的下一层节点数量）
  breadth_score:
    formula: "min(可解锁后继节点数 / 5, 1.0)"
    weight: 0.3
  
  # 跨层连接得分（与上下层的连接数）
  cross_layer_score:
    formula: "跨层边数 / 平均跨层边数"
    weight: 0.3
```

### 4.3 表现匹配分 (Sp)

表现匹配分基于学生在同层或相关节点的历史表现：

```yaml
sp_calculation:
  # 同层历史正确率
  same_layer_accuracy:
    source: "同层节点的历史测验正确率"
    weight: 0.5
  
  # 主题相关正确率
  topic_related_accuracy:
    source: "同一主题不同层节点的历史正确率"
    weight: 0.3
  
  # 学习曲线趋势
  learning_trend:
    source: "最近5次学习的正确率趋势"
    weight: 0.2
    # 趋势上升取高值，下降取低值
```

### 4.4 层次匹配分 (Sh)

层次匹配分评估候选节点与目标层次的匹配程度：

```yaml
sh_calculation:
  # 精确匹配
  exact_match:
    condition: "candidate.layer == target_level"
    score: 1.0
  
  # 跨一层匹配（skill→concept 或 skill→tool）
  cross_one_layer:
    condition: "abs(candidate.layer - target_level) == 1"
    score: 0.6
  
  # 跨多层匹配
  cross_multi_layer:
    condition: "abs(candidate.layer - target_level) > 1"
    score: 0.2
```

### 4.5 候选筛选流程

```
推荐请求
    │
    ▼
[阶段1：候选生成]
    │
    ├── 获取当前节点的后继节点（跨层边）
    ├── 获取前置节点（前置依赖边）
    ├── 获取同主题节点（跨层）
    │
    ▼
[阶段2：过滤筛选]
    │
    ├── 过滤已掌握节点（mastery_confirmed中存在）
    ├── 过滤不满足前置条件的节点
    ├── 过滤超出学生能力范围的节点（难度差距>2级）
    │
    ▼
[阶段3：权重计算]
    │
    ├── 计算 Sn（网络结构分）
    ├── 计算 Sp（表现匹配分）
    ├── 计算 Sh（层次匹配分）
    ├── 计算 S_total
    │
    ▼
[阶段4：多样性保证]
    │
    ├── 层间平衡（各层候选比例≥20%）
    ├── 难度梯度（高/中/低难度均有覆盖）
    ├── 主题分散（同一主题最多2个候选）
    │
    ▼
推荐结果
```

---

## 5. 推荐解释生成

### 5.1 推荐理由三要素

每个推荐结果必须包含以下三要素：

```yaml
recommendation_reason:
  # 要素1：知识网络依赖
  knowledge_dependency:
    description: "说明为什么推荐这个节点"
    example: "该节点是学习『二次方程应用』的前置条件"
  
  # 要素2：表现匹配
  performance_match:
    description: "基于学生历史表现的匹配理由"
    example: "你在『一次函数』的测验中正确率达92%，适合学习相关技能"
  
  # 要素3：层次匹配
  level_match:
    description: "与目标学习层次的匹配关系"
    example: "当前目标层次为skill，该节点正好是skill层"
```

### 5.2 解释生成模板

```yaml
explanation_template:
  format: "自然语言"
  template: |
    推荐学习「{node_name}」
    
    原因：
    1. 知识网络：「{prerequisite_relation}」，{knowledge_explanation}
    2. 表现匹配：{performance_explanation}，适合度{ suitability_score }
    3. 层次匹配：{level_explanation}
    
    预估学习时长：{estimated_periods}分钟
    预估难度：{difficulty}（1-5级）

  variables:
    - node_name          # 节点名称
    - prerequisite_relation  # 前置依赖关系
    - knowledge_explanation   # 知识说明
    - performance_explanation # 表现说明
    - suitability_score       # 适合度评分
    - level_explanation       # 层次说明
    - estimated_periods       # 预估时长
    - difficulty              # 难度等级
```

---

## 6. 学生选择与记录

### 6.1 学生选择流程

```
推荐展示
    │
    ▼
学生查看推荐理由
    │
    ▼
学生选择节点 / 拒绝推荐 / 自选节点
    │
    ▼
记录选择行为
    │
    ▼
更新学习路径
```

### 6.2 选择记录数据结构

```yaml
learning_choice_record:
  record_id: "choice_001"
  request_id: "req_001"                    # 对应的推荐请求
  student_id: "student_001"
  
  # 推荐结果
  recommended_candidates:
    - node_id: "node_math_quadratic_skill_001"
      score: 0.85
      reason: "前置依赖+表现匹配"
    - node_id: "node_math_quadratic_concept_001"
      score: 0.72
      reason: "概念理解优先"
  
  # 学生选择
  student_choice:
    selected_node_id: "node_math_quadratic_skill_001"  # 或 null 表示拒绝
    selection_type: "recommended" / "rejected" / "self_selected"
    self_selected_node_id: "node_xxx"   # 如果 selection_type == "self_selected"
    rejection_reason: "太难了"          # 可选
  
  # 时间戳
  timestamp: "2026-06-15T10:05:00Z"
```

---

## 7. 输出规格

### 7.1 推荐响应数据结构

```yaml
recommendation_response:
  response_id: "resp_001"
  request_id: "req_001"
  timestamp: "2026-06-15T10:00:05Z"
  processing_time_ms: 850                 # 处理时长（毫秒）
  
  # 推荐候选列表（按分数降序）
  candidates:
    - rank: 1
      node_id: "node_math_quadratic_skill_001"
      node_name: "二次方程的建模应用"
      layer: "skill"
      difficulty: 3
      estimated_periods: 45
      
      # 分项得分
      score_breakdown:
        total_score: 0.85
        network_score: 0.52               # Sn × Wn = 0.87 × 0.6
        performance_score: 0.26           # Sp × Wp = 0.85 × 0.3
        level_score: 0.07                  # Sh × Wh = 1.0 × 0.1
      
      # 推荐理由
      reason:
        knowledge_dependency: "该节点前置依赖『一元二次方程概念』，你已掌握"
        performance_match: "同主题tool层正确率88%，表现良好"
        level_match: "精确匹配目标层次skill"
      
      # 推荐解释（自然语言）
      explanation: |
        推荐学习「二次方程的建模应用」
        
        原因：
        1. 知识网络：前置依赖「一元二次方程概念」，你已在6月12日掌握
        2. 表现匹配：同主题tool层测验正确率达88%，表现良好
        3. 层次匹配：精确匹配你的目标层次skill
        
        预估学习时长：45分钟
        预估难度：3级（中等）
      
      # 多样性标签（用于展示平衡）
      diversity_tags:
        - "skill层"
        - "中等难度"
        - "建模应用"
    
    - rank: 2
      node_id: "node_math_quadratic_concept_001"
      node_name: "一元二次方程的本质"
      layer: "concept"
      difficulty: 4
      estimated_periods: 60
      # ... 同上结构

  # 统计信息
  statistics:
    total_candidates: 5
    layers_represented: ["skill", "concept"]  # 保证≥2层
    difficulty_range: [2, 4]                  # 保证难度梯度
```

### 7.2 输出字段说明

| 字段 | 类型 | 说明 |
|-----|------|------|
| response_id | string | 响应唯一标识 |
| request_id | string | 对应请求标识 |
| processing_time_ms | integer | 处理时长（毫秒） |
| candidates | array | 推荐候选列表 |
| candidates[].rank | integer | 排名 |
| candidates[].score_breakdown | object | 分项得分 |
| candidates[].reason | object | 推荐理由三要素 |
| candidates[].explanation | string | 自然语言解释 |
| statistics | object | 统计信息 |

---

## 8. 关键约束

### 8.1 性能约束

| 约束项 | 要求 | 说明 |
|-------|------|------|
| **推荐响应时间** | ≤10秒 | 从接收到返回推荐结果 |
| **候选节点数量** | 3-10个 | 推荐候选数量范围 |
| **候选多样性** | ≥2层 | 推荐列表必须覆盖至少2个不同层次 |

### 8.2 质量约束

| 约束项 | 要求 | 说明 |
|-------|------|------|
| **前置条件检查** | 100% | 所有推荐节点必须满足前置条件 |
| **已掌握节点过滤** | 100% | 不得推荐已掌握节点 |
| **推荐理由完整性** | 100% | 每个候选必须包含三要素 |

### 8.3 数据约束

| 约束项 | 要求 | 说明 |
|-------|------|------|
| **历史数据窗口** | 30天 | 用于计算表现分的有效期 |
| **最小样本量** | 3次 | 计算正确率所需的最少尝试次数 |

---

## 9. 集成与接口

### 9.1 与其他模块的接口

| 调用方 | 接口 | 说明 |
|-------|------|------|
| 虚拟教室 | `recommend_next_node(request)` | 获取下一节点推荐 |
| 学习路径追踪 | `record_choice(record)` | 记录学生选择 |
| 学情分析 | `get_recommendation_history(student_id)` | 获取推荐历史 |
| 知识网络 | `get_network_structure(network_id)` | 获取网络结构 |

### 9.2 核心API

| 接口 | 功能 | 参数 | 返回值 |
|-----|------|------|--------|
| `get_recommendation(request)` | 获取推荐 | RecommendationRequest | RecommendationResponse |
| `record_student_choice(record)` | 记录选择 | LearningChoiceRecord | 操作结果 |
| `get_candidate_explanation(node_id, student_id)` | 获取解释 | node_id, student_id | Explanation |

---

## 10. 关键设计决策

| 决策点 | 设计选择 | 理由 |
|-------|---------|------|
| 权重分配 | 网络结构60% / 表现30% / 层次10% | 保证推荐基于知识网络拓扑结构，同时考虑个体差异 |
| 候选数量 | 3-10个 | 足够多样性展示，避免选择困难 |
| 表现分计算 | 30天滑动窗口 | 平衡历史数据相关性与数据时效性 |
| 多样性保证 | 层间平衡+难度梯度+主题分散 | 确保推荐的系统性和可探索性 |
| 推荐理由 | 三要素结构 | 提供可解释、可追溯的推荐依据 |

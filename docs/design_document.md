# 多智能体辅助教学框架 - 设计文档

## 1. 项目概述

### 1.1 项目名称
**EduAgents** - 智能教学多智能体协同框架

### 1.2 项目愿景
构建一个**动态可配置**的多智能体教学辅助平台，能够根据教学场景自动设计Agent组合与协作机制，减少人工配置成本，提升教学效率。

### 1.3 核心价值
- **动态编排**：根据场景自动生成Agent配置
- **框架融合**：兼收并蓄DeepAgents与AgentScope优势
- **人机协同**：支持人类教师全程参与和引导
- **配置复用**：生成配置可保存、加载、复用

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                           用户界面层                                  │
│              (Web CLI / API / 可视化配置工具)                        │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────────┐
│                         场景识别引擎                                  │
│              (分析任务类型 → 选择Agent组合 → 生成配置)                 │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────────┐
│                        Agent 编排层                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │
│  │   规划型Agent    │  │   协作型Agent   │  │   执行型Agent   │       │
│  │  (DeepAgents)   │  │ (AgentScope)   │  │   (通用)        │       │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘       │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────────┐
│                        统一协议层                                     │
│           (数据转换 消息路由 状态同步)                                │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────────┐
│                       配置管理层                                      │
│              (YAML/JSON持久化 配置加载 配置预览)                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 技术选型

| 组件 | 技术 | 说明 |
|-----|------|-----|
| 核心框架 | DeepAgents + AgentScope | 兼收并蓄 |
| 编程语言 | Python 3.10+ | |
| 配置格式 | YAML / JSON | 本地持久化 |
| 消息协议 | 自定义统一协议 | 见第4章 |
| 接口层 | FastAPI | 可选 REST API |
| 前端(可选) | React/Vue | 可视化配置 |

---

## 3. 核心模块设计

### 3.1 模块列表

| 模块 | 职责 |
|-----|------|
| SceneAnalyzer | 场景识别与分析 |
| ConfigGenerator | Agent配置动态生成 |
| AgentOrchestrator | Agent编排与调度 |
| ProtocolConverter | 协议转换与适配 |
| ConfigPersistence | 配置持久化管理 |
| HumanInLoop | 人机协同接口 |

### 3.2 场景识别引擎 (SceneAnalyzer)

#### 输入
- 课程名称
- 课程简介
- 教学材料（可选）
- 用户选择模式

#### 输出
- 场景类型枚举
- 推荐Agent组合
- 初始配置模板

#### 场景类型

| 场景ID | 场景名称 | Agent模式 | 适用框架 |
|-------|---------|----------|----------|
| SCENE_001 | 课程规划 | 规划型 | DeepAgents |
| SCENE_002 | 备课辅助 | 主从型 | DeepAgents |
| SCENE_003 | 虚拟教室 | 多角色型 | AgentScope |
| SCENE_004 | 学生练习 | 协作型 | AgentScope |
| SCENE_005 | 作业批改 | 执行型 | 通用 |

### 3.3 配置生成器 (ConfigGenerator)

#### 功能
1. 根据场景类型生成Agent定义
2. 动态分配Agent角色与职责
3. 生成Agent间通信关系
4. 输出标准化配置

#### 配置模板结构

```yaml
scene_type: "虚拟教室"
agents:
  - name: "AI教师"
    type: "teacher"
    framework: "AgentScope"
    capabilities:
      - 讲解知识
      - 提问互动
      - 课堂管理
    count: 1
    
  - name: "AI同学"
    type: "student"
    framework: "AgentScope"
    capabilities:
      - 回答问题
      - 协作讨论
      - 展示思路
    count: 3  # 可动态调整
    
collaboration:
  mode: "动态分配"
  routing: "MessageHub"
```

---

## 4. 统一数据协议设计

### 4.1 核心消息格式

```python
class UnifiedMessage:
    id: str                    # 消息唯一标识 (UUID)
    sender: AgentIdentity     # 发送方身份
    receivers: list[AgentIdentity]  # 接收方列表
    content: MessageContent    # 消息内容
    intent: IntentTag          # 意图标签
    context: ContextRef        # 上下文引用
    metadata: dict             # 元数据
    state: MessageState        # 消息状态

class AgentIdentity:
    id: str                    # Agent ID
    name: str                  # Agent 名称
    role: str                  # 角色 (teacher/student/assistant)
    framework: str            # 来源框架

class IntentTag:
    category: str              # 类别 (teach/learn/discuss/manage)
    action: str                # 动作 (explain/ask/answer/summarize)
    priority: int              # 优先级 1-5

class MessageContent:
    text: str                   # 文本内容
    media: list[str]           # 媒体资源 (URLs)
    format: str                # 格式类型
```

### 4.2 协议转换映射

| DeepAgents 格式 | AgentScope 格式 | 统一协议 |
|----------------|----------------|---------|
| AgentState | Message | UnifiedMessage |
| write_todos | task | IntentTag |
| VFS file | URL reference | ContextRef |
| SubAgent context | msghub message | AgentIdentity |

---

## 5. Agent协作机制

### 5.1 协作模式

#### 模式一：主从模式（Master-Slave）
- **适用场景**：备课辅助、出题审题
- **结构**：一个主Agent协调，多个子Agent执行具体任务
- **框架**：DeepAgents (write_todos + Subagents)

#### 模式二：多角色模式（Multi-Role）
- **适用场景**：虚拟教室、学生练习
- **结构**：多个平等Agent，各司其职
- **框架**：AgentScope (MessageHub)

#### 模式三：流水线模式（Pipeline）
- **适用场景**：教学材料解析、方案迭代
- **结构**：输入→处理Agent链→输出
- **框架**：两者均可

### 5.2 动态配置示例

**场景：学生做数学练习**

```yaml
scenario: "学生练习"
context:
  subject: "数学"
  topic: "一元二次方程"
  difficulty: "中等"

agents:
  - role: "出题Agent"
    framework: "DeepAgents"
    mode: "pipeline"
    
  - role: "AI同学A"
    framework: "AgentScope"
    personality: "鼓励型"
    strategy: "引导思考"
    
  - role: "AI同学B"
    framework: "AgentScope"
    personality: "严谨型"
    strategy: "展示规范解法"
    
  - role: "评判Agent"
    framework: "通用"
    mode: "execute"
```

---

## 6. 配置管理

### 6.1 配置文件结构

```
config/
├── templates/           # 场景模板
│   ├── course_planning.yaml
│   ├── lesson_prep.yaml
│   ├── virtual_classroom.yaml
│   └── student_practice.yaml
│
├── presets/            # 预设配置
│   └── default_preset.yaml
│
├── user_saved/         # 用户保存配置
│   └── my_config_001.yaml
│
└── runtime/            # 运行时配置
    └── current_session.yaml
```

### 6.2 配置生命周期

```
┌──────────┐    生成     ┌──────────┐    编辑     ┌──────────┐
│  场景分析  │ ────────▶ │   草稿    │ ────────▶ │  预览    │
└──────────┘            └──────────┘            └──────────┘
                                                     │
                                          ┌──────────┴──────────┐
                                          ▼                     ▼
                                    ┌──────────┐          ┌──────────┐
                                    │   保存    │          │   执行   │
                                    └──────────┘          └──────────┘
```

### 6.3 配置保存接口

```python
class ConfigManager:
    def save(self, config: AgentConfig, path: str) -> None:
        """保存配置到本地"""
        
    def load(self, path: str) -> AgentConfig:
        """从本地加载配置"""
        
    def list_presets(self) -> list[ConfigMeta]:
        """列出所有预设配置"""
        
    def export_template(self, config: AgentConfig) -> str:
        """导出为可复用的模板"""
```

---

## 7. 人机协同

### 7.1 交互节点

| 阶段 | 人类角色 | 交互方式 |
|-----|---------|---------|
| 课程规划 | 确认/调整教学方向 | 确认提示 |
| 方案迭代 | 提供反馈 | 评分/批注 |
| 虚拟教室 | 监控/干预 | 实时查看 |
| 课堂管理 | 最终决策 | 审批/打断 |

### 7.2 Human-in-the-Loop 实现

```python
class HumanInLoop:
    def request_approval(self, decision: Decision) -> bool:
        """请求人工审批"""
        
    def collect_feedback(self, plan: Plan) -> Feedback:
        """收集反馈意见"""
        
    def interrupt(self, agent_id: str, reason: str):
        """中断指定Agent"""
        
    def adjust_config(self, changes: dict):
        """调整运行配置"""
```

---

## 8. 使用流程

### 8.1 典型流程：课程规划

```
1. 输入课程信息
   └─▶ 课程名称: "初中数学"
       简介: "一元二次方程讲解"

2. 场景分析 (SceneAnalyzer)
   └─▶ 识别为 SCENE_001 (课程规划)
       推荐组合: [规划Agent, 研究Agent]

3. 配置生成 (ConfigGenerator)
   └─▶ 生成初始配置
       agents:
         - 规划Agent (DeepAgents)
         - 研究Agent (DeepAgents)

4. 人机确认
   └─▶ 用户确认/调整教学方向
       可选: 添加更多教学方向

5. 执行与迭代
   └─▶ 生成教学方案
       用户反馈 → 调整 → 再次生成

6. 保存配置
   └─▶ 保存到 user_saved/
```

### 8.2 典型流程：虚拟教室

```
1. 选择场景
   └─▶ 虚拟教室

2. 输入上下文
   └─▶ 课程: 一元二次方程
       学生人数: 30人
       互动模式: 协作讨论

3. 动态配置
   └─▶ AI教师: 1个
       AI同学: 3个 (可调整)
       角色分配: 自动生成

4. 启动虚拟教室
   └─▶ AgentScope MessageHub 启动
       实时渲染教室状态

5. 人类监控
   └─▶ 教师可随时干预
       可调整AI同学数量
```

---

## 9. 后续章节预览

- **第10章**: API 接口设计
- **第11章**: 数据库设计
- **第12章**: 部署架构
- **第13章**: 测试策略

---

## 10. 附录

### A. 术语表

| 术语 | 定义 |
|-----|------|
| Agent | 智能体，能够自主决策和执行任务的AI实体 |
| 编排 | Orchestration，协调多个Agent工作的过程 |
| 场景 | Scene，具有特定目标和约束的教学任务类型 |
| 配置 | Config，描述Agent组合和协作方式的声明式定义 |

### B. 参考资料

- DeepAgents 官方文档
- AgentScope GitHub 仓库
- LangChain/LangGraph 文档

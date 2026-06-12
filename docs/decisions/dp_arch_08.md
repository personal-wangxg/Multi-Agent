# DP-ARCH-08：思政融合设计

**确认日期**：2026-06-12 · **确认人**：项目核心团队 · **决策类别**：架构

---

## 决策摘要

思政融合不是一个独立场景，而是**备课辅助（SCENE-002）阶段中的一个输出字段（ideological_integration_suggestion）**。由思政融合 Agent 提出结构化建议（在哪个节点、融什么、如何融），教师最终确认内容合规性。Agent 只能"建议"，最终内容必须经教师手动确认后写入教案/学案。

## 核心设计原则

1. **Agent 提案，教师最终确认**：Agent 不直接输出思政内容，仅产出结构化建议，
2. **非独立场景，备课阶段的一个字段**：ideological_integration_suggestion 嵌入教学包，
3. **额外 Harness 内容检查**：思政内容须经额外敏感/不当内容过滤，
4. **可追溯痕迹**：教案/学案中标注"本节包含思政设计"，保留审计线索，
5. **优秀设计沉淀模板**：教师确认后的优秀设计可沉淀为模板，后续复用。

## 关键细节

### 输出字段（SCENE-002 teaching_package）

```yaml
ideological_integration_suggestion:
  target_node_id: "tool_elimination_method"        # 建议融入的节点
  element: "用数学建模解决实际问题的价值观"          # 建议融入的思政元素
  approach: "在导入环节用真实校园购物问题引入"       # 融入方式说明
  activity: "小组讨论：校园食堂预算问题建模求解"     # 活动设计
  duration_minutes: 5                               # 建议时长
  teacher_confirmation: "pending"                   # pending/confirmed/rejected/revised
```

### 决策流程

```
备课辅助 Agent 生成教案 → 思政融合 Agent 生成建议
         │                                │
         ▼                                ▼
   教师审阅 + 修改 + 确认（approve / reject / revise）
         │
         ▼
   teacher_confirmation = "confirmed"/"revised"
         │
         ▼
   Harness Schema 校验（含内容过滤）
         │
         ▼
   写入 teaching_package → 持久化
```

### 教师确认矩阵

| teacher_confirmation 值 | 含义 | 是否写入教案 |
|-------------------------|------|-------------|
| pending | 等待教师审阅 | 否 |
| confirmed | 教师直接确认建议 | 是 |
| revised | 教师修改后确认 | 是（记录修改） |
| rejected | 教师拒绝该建议 | 否 |

## 影响范围

- 关联 FR：FR-16（思政融合设计与审核）；
- 关联场景：SCENE-002（备课辅助）；
- 关联产物：teaching_package 中的 ideological_integration_suggestion 字段。

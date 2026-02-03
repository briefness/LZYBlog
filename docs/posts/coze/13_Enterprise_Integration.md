# Coze 零基础精通系列 13：企业级集成 —— Agent Office 与办公自动化

> **上一篇回顾**：掌握了 Skill Store 的买卖逻辑。
> **本篇目标**：将视野放大到企业级应用。如何让 Agent 不仅仅陪聊，而是真正协助在 **Word、Excel、PPT** 里工作。

---

## 1. 什么是 Agent Office？

在 Coze 2.0 发布会上，最让打工人沸腾的功能莫过于 **Agent Office**（智能办公助手）。
它不再是一个独立的聊天窗口，而是直接嵌入到了办公软件里。

**场景举例**：
*   **Word 中**：用户写了个标题“季度总结”，Agent 自动协助补全剩下的 5000 字，并插入数据图表。
*   **Excel 中**：用户提供一张乱糟糟的财务表，指令“帮我把亏损的项目标红，并算出总亏损额”，它自动写公式搞定。
*   **PPT 中**：用户指令“帮我根据这个 Word 文档生成一个 10 页的 PPT”，它自动排版、配图。

这不是科幻，这是 Coze 2.0 与飞书/字节办公套件深度集成后的能力。

## 2. 核心原理：Embedded Agent (嵌入式智能体)

要实现这一点，需要用到 Coze 的 **On-Premise (私有化部署)** 或 **SaaS 集成** 能力。

```mermaid
graph TD
    User[用户在飞书文档] -->|点击 'AI 续写'| Plugin_Feishu[飞书插件端]
    
    Plugin_Feishu -->|API 调用| Coze_Agent[你的 Coze Agent]
    
    subgraph Coze_Processing
        Coze_Agent -->|解析文档内容| Document_Reader
        Document_Reader -->|理解意图| LLM
        LLM -->|生成内容| Generator
    end
    
    Generator -->|返回 Markdown| Plugin_Feishu
    Plugin_Feishu -->|渲染到文档| User
```

关键在于：**上下文 (Context) 的无缝传递**。
Agent 不仅读到了 Prompt，还读到了当前光标所在的文档内容。

## 3. 实战：打造一个“合同审核助手”

**需求**：销售经常在飞书里发合同草稿，需要一个法务 AI 自动审核风险。

### 第一步：创建 Agent
1.  在 Coze 创建一个 Agent `Law_Reviewer`。
2.  上传知识库：`公司法务合规手册.pdf`, `风险条款清单.xlsx`。
3.  Prompt：
    > “你是一个严谨的法务。接收用户发送的合同文本，根据知识库逐条审查。重点标注：赔偿金额过高、管辖法院非本地等风险。”

### 第二步：配置发布渠道
1.  在发布页面，选择 **“飞书 (Feishu)”**。
2.  配置权限：允许读取 **云文档 (Docs)** 权限。
3.  发布。

### 第三步：在飞书中使用
1.  打开一份合同文档。
2.  选中全文。
3.  点击浮动菜单栏的 **“Ask AI”**。
4.  选择刚才发布的 `Law_Reviewer`。
5.  点击运行。

**结果**：Agent 会并在文档右侧的批注栏里，生成密密麻麻的修改建议。只需点击“采纳”，文档就会自动修改。

## 4. 进阶：API 集成到自研系统

如果公司不用飞书，用的是自研的 OA 系统，怎么办？
**Coze API** 是通用的。

需开发一个简单的中间件：
1.  **Frontend**：在 OA 的富文本编辑器里加一个“AI 润色”按钮。
2.  **Backend**：
    *   当按钮点击时，把编辑器里的文本打包。
    *   调用 `POST https://api.coze.cn/v3/chat`。
    *   将 `query` 设置为编辑器文本。
    *   将 `bot_id` 设置为 Coze Agent ID。
3.  **Callback**：收到 API 返回的 JSON 后，替换编辑器里的文本。

只需要几行代码，旧 OA 系统瞬间就拥有了 GPT-4 的能力。

---

## 5. 系列大结局：AI 的未来

至此，**《Coze 零基础精通系列》** 全 13 篇圆满结束。

从最简单的对话，讲到了工作流、数据库、代码节点、Vibe Coding，最后到了企业级集成。
Coze 2.0 把 AI 的门槛降到了地板上，但把天花板抬到了平流层。

**给开发者的最后建议**：
*   **不要迷信 Prompt**：Prompt 只是起点，Workflow 才是护城河。
*   **不要重复造轮子**：多逛 Skill Store。
*   **保持好奇心**：AI 原生应用 (AI-Native Apps) 的形态还在爆发期，今天的最佳实践可能明天就被颠覆。

祝在 AI 的浪潮里，乘风破浪！🌊

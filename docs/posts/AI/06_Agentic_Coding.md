# 06. 编程新范式：从 Copilot 到 Agent (Antigravity & MCP)

> [!IMPORTANT]
> **构建全自动化的 AI 研发团队**
> 
> 本文探讨如何通过 **Antigravity / Claude Code** 和 **MCP (Model Context Protocol)**，让 AI 真正接管项目。
> 重点在于配置 **.agent/rules** 和编写 **MCP Server**。

## 1. 架构演进：从 “补全” 到 “循环”

### Copilot 的局限 (Stateless)
传统的 Copilot 是**无状态**的。它仅关注当前文件的光标位置 + 最近打开的 Tabs。
类似于一个**健忘的实习生**：告诉它改了 A 文件，它下一秒去 B 文件时就忘了 A 的改动。

### Agent 的核心：OODA 循环
Antigravity 和 Claude Code 引入了 **OODA Loop (Observe-Orient-Decide-Act)**。

```mermaid
stateDiagram-v2
    State1: Observe (观察)
    State2: Orient (定位/思考)
    State3: Decide (决策)
    State4: Act (行动)
    
    [*] --> State1
    State1 --> State2 : 读取文件/终端报错
    State2 --> State3 : 利用Skills分析原因
    State3 --> State4 : 调用Tool修改代码
    State4 --> State1 : 运行测试，观察结果
    
    State1 --> [*] : 测试通过
```

*   **持久化记忆 (Memory)**：它会维护一个 `context` 窗口，记录多轮操作历史。
*   **主动式终端 (Active Terminal)**：它不光会生成代码，还会**真的运行** `ls`, `grep`, `npm test` 来验证假设。

> [!CAUTION]
> **Safety First: 沙盒与权限**
> 
> 赋予 Agent 终端权限存在风险。
> 1.  **Sandboxing (沙盒)**: 生产环境必须在 Docker 容器或受限环境中运行。
> 2.  **Human Verification**: 对于删除文件、Push 代码等操作，必须有人类确认卡点。

---

## 2. 核心配置：Rules (构建 AI 宪法)

Antigravity/Cursor 允许用户通过配置文件定义 AI 的行为准则。不仅是提示词，更是**系统级约束**。

### 实战：编写一个生产级的 `.agent/rules`

在项目根目录创建文件，明确技术栈和行为准则：

```markdown
# Project Context
Stack: Next.js 14, TailwindCSS, PostgreSQL, Prisma.
State Management: Zustand only (No Redux).

# Code Style (强制执行)
1. **Functional Components**: Use `const Component = () => {}` syntax.
2. **Types**: 
   - Strict TypeScript everywhere. 
   - interfaces usually prefixed with `I`.
   - No `any`, use `unknown` if unsure.
3. **Error Handling**:
   - Backend: All API routes must act within a `try/catch` block.
   - Frontend: Use `react-hot-toast` for user-facing errors.

# Agent Behavior
1. **Always Verify**: After writing code, ALWAYS run `npm run lint` before returning control to user.
2. **Think in Steps**: If a task involves >2 files, list the plan first.
3. **No Placeholders**: Never leave comments like `// ... rest of code`. Write full code.
```

**Rule 是提效杠杆率最高的地方**。如果没规则，AI 可能生成过时的 Class Component，或者让你手动修 import 错误。

---

## 3. 连接万物：MCP (Model Context Protocol) 详解

MCP 是 Anthropic 提出的开放标准，旨在解决“AI 无法访问外部数据”的痛点。
它采用了 **Client-Host-Server** 架构：

*   **Client**: IDE (Cursor/Antigravity)。
*   **Host**: 运行环境。
*   **Server**: 实际连接数据源的插件 (Git, Postgres, Filesystem)。

### 实战：通过 MCP 连接 PostgreSQL

不仅是查天气，MCP 还能直接连你的生产数据库查数据。

**1. 安装 PostgreSQL MCP Server**
使用官方提供的 Docker 镜像或 Python 包。

**2. 在 IDE 配置中挂载**
```json
{
  "mcpServers": {
    "postgres": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", 
        "-e", "POSTGRES_CONNECTION_STRING=postgresql://user:password@localhost:5432/mydb",
        "mcp/postgres" 
      ]
    }
  }
}
```

**3. 效果**
现在的 Agent 可以直接阅读你的数据库 Schema！
你可以直接问：“帮我写一个 SQL 查询过去 7 天活跃度最高的用户”，它会自动读取表结构并生成正确的 SQL。这就是 MCP 的威力。

---

## 4. 技能与工作流 (Skills & Workflows)

### Skills: 封装好的能力块
在 Antigravity 中，Skill 是一组预定义的 Prompt + Tools 集合。
前端常用的 `frontend-design` skill 可能包含：
*   **Prompt**: "你是一位获得 awwwards 奖项的设计师..."
*   **Tool**: 调用 `Pencil` MCP 生成线框图。
*   **Knowledge**: 内置了 Material Design, Tailwind 配色表的知识。

### Workflows: 将 SOP 代码化
Workflow 是将复杂的任务流程化。比如一个 **Feature Dev Workflow**：

1.  **Requirement**: 调用 `/brainstorm` skill，分析出 User Stories。
2.  **Design**: 使用 `frontend-design` skill 生成组件结构。
3.  **Code**: 写代码，并自动应用 Rules。
4.  **Verify**: 运行 `npm test`。如果有错，自动进入 Debug Loop。

## 5. 开发者角色的转变：从 Writer 到 Reviewer

在 Agentic Coding 时代，开发者的角色从单纯的代码**撰写者 (Writer)**，转化为：

1.  **Product Manager**: 定义清晰的 `.agent/rules` 和需求文档。
2.  **System Architect**: 设计 MCP 架构，决定 Agent 能连接什么数据。
3.  **Code Reviewer**: **这是最重要的工作**。AI 生成越快，幻觉越隐蔽。必须具备极强的 Code Review 能力，为安全性兜底。

## 小结

1.  **Rules** 是基本宪法。
2.  **MCP** 是感知器官。
3.  **Skills** 是专业技能。
4.  **Workflows** 是标准流程。

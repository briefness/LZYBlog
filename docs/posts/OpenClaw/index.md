# OpenClaw 原理拆解

> OpenClaw 很火，但它到底是怎么运转的？
> 本系列从零拆解 OpenClaw 的架构原理——Agent 循环、四层架构、Tool Calling、记忆机制、Skill 生态、安全模型。
> 面向小白，图文并茂，不写代码也能看懂。

## 目录

### 基础概念
- **[01. 从聊天机器人到自主 Agent](./01_Agent_vs_Chatbot.md)**
    - AI Agent 与 API 调用的本质区别
    - OpenClaw 的定位与核心能力
    - 一个完整请求的生命周期

### 架构拆解
- **[02. 四层架构拆解](./02_Architecture.md)**
    - Hub-and-Spoke 架构总览
    - 输入层、编排层、智能层、执行层逐层解析
    - 一条消息的完整数据流
- **[03. Agent 循环与 Tool Calling](./03_ReAct_and_ToolCalling.md)**
    - ReAct 循环（思考 → 行动 → 观察）
    - Tool Calling 完整链路：定义、调用、回传
    - System Prompt 的四大 Markdown 配置文件

### 认知与记忆
- **[04. Context Window 与记忆机制](./04_Context_and_Memory.md)**
    - Context Window 为什么是最核心的约束
    - 短期记忆 vs 长期记忆
    - 管理策略：滑动窗口、摘要压缩、分层注入

### 生态与安全
- **[05. Skill 生态与扩展机制](./05_Skill_Ecosystem.md)**
    - Tool（能力）vs Skill（方法论）
    - SKILL.md 的内部结构与触发机制
    - ClawHub 社区生态与供应链风险
- **[06. 安全模型与权限边界](./06_Security.md)**
    - ClawJacked 漏洞攻击链拆解
    - 原生安全机制：DM 控制、Tool 白名单、沙箱隔离
    - Agent 权限模型的设计挑战

---

## 相关系列

- **[AI 认知与实战](/posts/AI/index)** —— AI 通用原理（Transformer、Agent FSM、MCP 协议）
- **[Coze 零基础精通](/posts/coze/index)** —— Coze 平台操作（部署、配置、Skill 安装）

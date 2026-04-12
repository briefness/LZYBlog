# Agent 实战：从原理到生产

会写 Python 但没碰过 LLM？这个系列用 17 篇文章，把你从"AI Agent 是什么"带到"能独立交付三个生产级 Agent 项目"。以 PydanticAI 为主力框架，LangGraph 做多 Agent 编排，MCP 协议做工具集成标准。每一篇都配 Mermaid 架构图和可运行代码，核心原理提供 CSS 动画组件可视化演示。

> **环境：** Python 3.12+, PydanticAI 1.70+, LangGraph 1.1+, MCP Spec 2025-11-25, uv 0.11+

## 📚 目录导航

### 第一阶段：认知与地基

从零建立对 LLM 和 Agent 的正确心智模型。这个阶段不用任何框架，纯 Python 手撕一个最小 Agent，彻底搞懂底层运作。

- **[01. Agent 全景：从对话到自主行动](./01_Agent_Overview.md)**
  - Agent vs Chatbot 的本质区别
  - ReAct 循环：Thought → Action → Observation 状态机
  - Agent 能力光谱：感知、推理、规划、行动、反思
  - 🎨 CSS 动画：ReAct 循环的动态执行过程

- **[02. LLM API 与 Function Calling：Agent 的神经系统](./02_LLM_API_and_Function_Calling.md)**
  - OpenAI / Anthropic / 开源模型 API 调用（统一接口）
  - Token 经济学：计费、上下文窗口与截断策略
  - Function Calling 机制：JSON Schema 定义、模型如何"决定"调用工具
  - 流式输出（SSE）与 Tool Call 的流式处理

- **[03. 从零手写 Agent：不依赖框架的 ReAct 实现](./03_Build_Agent_From_Scratch.md)**
  - 用纯 Python + LLM API 实现完整的 ReAct Agent
  - 工具注册表、消息历史管理、循环终止条件
  - 对话记忆与上下文窗口管理策略
  - 为什么需要框架：手写方案的局限性分析

### 第二阶段：PydanticAI 核心

把手写的 Agent 升级到工程级别。PydanticAI 的设计哲学是"用 Python 的方式写 Agent"——类型安全、依赖注入、零魔法。

- **[04. PydanticAI 入门：第一个类型安全的 Agent](./04_PydanticAI_Basics.md)**
  - 框架设计哲学：为什么不选 LangChain
  - Agent 定义、System Prompt、Model 配置
  - @agent.tool 装饰器与工具注册
  - 运行模式：run_sync / run / run_stream

- **[05. 结构化输出与多模型切换](./05_Structured_Output.md)**
  - Pydantic BaseModel 作为 Agent 的返回类型（结构化输出）
  - 多模型适配：OpenAI、Anthropic、Gemini、Ollama 无缝切换
  - 动态 System Prompt 与上下文注入
  - 结果验证与自动重试机制

- **[06. 依赖注入与工程化测试](./06_Dependency_Injection_and_Testing.md)**
  - PydanticAI 的 DI 系统：deps 参数与 RunContext
  - 使用 TestModel / FunctionModel 做单元测试
  - Agent 的可观测性：Logfire 集成与调用链追踪
  - 生产级 Agent 的代码组织模式

### 第三阶段：工具生态与知识

Agent 的核心竞争力来自它能连接的外部世界。MCP 协议让工具接入标准化，RAG 让 Agent 拥有领域知识。

- **[07. MCP 协议：标准化的工具集成层](./07_MCP_Protocol.md)**
  - MCP 架构：Client-Server 模型、传输层（stdio / SSE / Streamable HTTP）
  - 从零实现一个 MCP Server（Python SDK）
  - PydanticAI 集成 MCP：mcp_server() 桥接
  - 社区 MCP Server 接入实战（文件系统、数据库、GitHub）

- **[08. RAG + Agent：让 Agent 拥有领域记忆](./08_RAG_Agent.md)**
  - 向量检索原理速览：Embedding、相似度搜索、HNSW
  - 用 ChromaDB / Qdrant 构建本地向量知识库
  - Agent + RAG 的集成模式：检索即工具
  - 分块策略、重排序与检索质量评估

### 第四阶段：多 Agent 系统

单个 Agent 有其能力天花板。当任务需要角色分工、并行执行和动态路由时，多 Agent 编排登场。

- **[09. 多 Agent 协作：Handoff 与角色分工](./09_Multi_Agent_Handoff.md)**
  - 单 Agent 的天花板：上下文污染与能力漂移
  - PydanticAI 的 Agent Handoff 机制
  - 路由 Agent + 专家 Agent 的委派模式
  - 🎨 CSS 动画：多 Agent 协作通信全流程
  - 共享状态 vs 消息传递：两种协作范式的 Trade-off

- **[10. LangGraph 编排：图论驱动的复杂工作流](./10_LangGraph_Orchestration.md)**
  - LangGraph 核心概念：StateGraph、Nodes、Edges、Checkpointer
  - 条件路由与循环工作流（Cyclic Workflows）
  - Human-in-the-Loop：中断、审批与恢复
  - LangGraph vs PydanticAI：何时用哪个的架构决策
  - 🎨 CSS 动画：图状态流转的动态可视化

### 第五阶段：三大实战项目

前四个阶段的所有知识在这里汇聚。三个项目难度递进，每个项目都是生产级别的完整实现。

- **[11. 实战（一）：智能客服系统](./11_Project_Customer_Service.md)**
  - 需求分析与架构设计（RAG + 多工具 + 多轮对话）
  - 知识库构建：文档导入、自动分块、向量化
  - 工具集成：订单查询、退款流程、工单创建
  - 对话管理：意图识别、槽位填充、上下文保持
  - Guardrails：敏感信息过滤、幻觉检测

- **[12. 实战（二）：数据分析助手](./12_Project_Data_Analyst.md)**
  - 需求分析与架构设计（Code Agent + SQL + 可视化）
  - 自然语言转 SQL：Schema 感知的查询生成
  - 沙箱执行：安全运行 Agent 生成的 Python 代码
  - 可视化输出：自动生成图表与分析报告
  - 错误自修复：执行失败后的自动诊断与重试

- **[13. 实战（三）：开发辅助 Copilot](./13_Project_Dev_Copilot.md)**
  - 需求分析与架构设计（MCP + 多 Agent 协作）
  - MCP Server 接入：Git、文件系统、终端命令
  - 多 Agent 流水线：需求分析 → 代码生成 → Code Review → 测试
  - LangGraph 编排：带循环的质量门控工作流
  - A2A 协议初探：跨系统的 Agent 互操作

### 第六阶段：生产化与架构

从"能跑"到"能上线"的最后一公里。安全、可观测性、性能——生产环境的三座大山。

- **[14. Agent 生产化：部署、监控与安全](./14_Production_Deployment.md)**
  - 部署架构：FastAPI + Agent 的服务化封装
  - 可观测性：结构化日志、分布式追踪、指标监控
  - 安全加固：Prompt Injection 防御、工具权限控制、输出过滤
  - 成本控制：Token 用量追踪、缓存策略、模型降级
  - Docker Compose 完整部署方案

- **[15. Agent 设计模式与架构决策](./15_Design_Patterns.md)**
  - 六大 Agent 架构模式：Router / Pipeline / Supervisor / Swarm / Evaluator / Orchestrator
  - 框架选型决策树：PydanticAI vs LangGraph vs OpenAI SDK vs 手写
  - Agent 评估体系：如何量化 Agent 的准确性与可靠性
  - 2026 生态全景：A2A、MCP、ACP 协议的演进方向
  - Agent 系统的技术债与演进策略

### 补充篇：核心专题深化

以下四篇是对照 DataWhale LLM Cookbook 及 Learn Claude Code 系列后补充的关键专题，覆盖 Prompt 工程、记忆/评估、执行控制面和上下文工程四个维度。

- **[16. Agent Prompt Engineering：System Prompt 与工具描述的设计模式](./16_Agent_Prompt_Engineering.md)**
  - Agent Prompt 的三个控制面：System Prompt / Tool Description / Tool Schema
  - System Prompt 设计模式：角色+规则+边界 / 条件路由 / Few-shot 示范
  - 工具描述五要素与工具重叠消歧策略
  - Prompt Injection 四层攻防体系
  - Prompt 版本化与 A/B 测试

- **[17. Agent 记忆与评估：Memory 架构 + 质量保证体系](./17_Memory_and_Evaluation.md)**
  - 记忆三层架构：工作记忆 / 短期记忆 / 长期记忆
  - 滑动窗口与摘要压缩的 Token 控制策略
  - 长期记忆持久化：结构化存储 + 向量化检索
  - 评估金字塔：组件测试 → 集成测试 → 端到端评估 → 线上抽检
  - 🎨 CSS 动画：记忆三层架构的数据流转

- **[18. Agent 控制面：权限管道、Hook 扩展与错误恢复](./18_Control_Plane.md)**
  - 权限管道四步：deny → mode → allow → ask
  - 三权限模式：default / plan / auto
  - Bash 命令的特殊安全检查
  - Hook 系统三事件模型：SessionStart / PreToolUse / PostToolUse
  - 统一返回协议（0=继续, 1=阻止, 2=注入）
  - 错误恢复状态机：running → retrying → recovering → failed

- **[19. 上下文工程：技能加载、压缩策略与 Prompt Pipeline](./19_Context_Engineering.md)**
  - 技能系统两层设计：轻量目录 + 按需深加载
  - SkillManifest / SkillDocument / SkillRegistry 数据结构
  - 压缩策略三层模型：大结果落盘 → 旧结果微压缩 → 历史摘要
  - Prompt Pipeline：System Prompt 的动态拼装流水线
  - Skill vs Memory vs CLAUDE.md 的边界区分

### 特别篇

- **[特别篇. Harness：智能体的"操作系统"](./Special_Agent_Harness.md)**
  - Agent = Model + Harness 的核心定义
  - 文件系统、Bash/代码执行、沙箱、Memory、Hooks 六大组成模块
  - ReAct 循环 + Ralph Loop 拦截 + 自验证的完整执行范式
  - Context Rot（上下文腐烂）的成因与 Harness 的应对策略
  - 🎨 CSS 动画：Harness 六大模块的动态交互

## 🔧 技术栈版本锁定（2026 年 3 月）

| 工具 / 框架 | 版本 | 用途 |
|------------|------|------|
| Python | 3.12+ | 运行时（PydanticAI 要求 3.10+，推荐 3.12） |
| PydanticAI | 1.70+ | 主力 Agent 框架 |
| Pydantic | 2.12+ | 数据验证与结构化输出 |
| LangGraph | 1.1+ | 多 Agent 编排（进阶） |
| MCP Python SDK | 1.26+ | 标准化工具集成 |
| uv | 0.11+ | 包管理 + 虚拟环境 |
| ChromaDB | 1.0+ | 向量数据库（RAG） |
| FastAPI | 0.135+ | Agent 服务化部署 |
| Logfire | latest | Agent 可观测性 |

## 🌟 系列特色

- **渐进式学习路径**：先手写 Agent 理解原理，再用框架提效，最后三个项目练手
- **PydanticAI 主导**：Model Agnostic、类型安全、Pythonic，不绑定任何 LLM 厂商
- **三大实战项目**：客服系统、数据分析、开发 Copilot，覆盖最常见的 Agent 应用场景
- **Mermaid 图解 + CSS 动画组件**：ReAct 循环、多 Agent 通信、图状态流转、记忆架构全部可视化
- **生产导向**：每篇文章都包含 Trade-offs 讨论和常见坑点，不只教怎么做，也教怎么避坑
- **版本锁定**：所有依赖版本精确到 2026 年 3 月最新稳定版

---

> 系列共 20 篇，特别篇 + 19 篇正文。

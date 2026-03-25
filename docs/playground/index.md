---
layout: doc
title: 编程游戏 - 码界觉醒
description: 一款 RPG 编程闯关游戏，通过编写 Python 代码控制角色，沿着前端转 AI 学习路径逐步通关
---

<style>
/* ===== Hero Section ===== */
.game-hero {
  text-align: center;
  padding: 48px 24px 40px;
  border-radius: 16px;
  background: linear-gradient(135deg,
    var(--vp-c-bg-soft) 0%,
    color-mix(in srgb, var(--vp-c-brand-1) 8%, var(--vp-c-bg-soft)) 100%);
  border: 1px solid var(--vp-c-divider);
  margin-bottom: 32px;
}

.game-hero-icon {
  font-size: 56px;
  margin-bottom: 12px;
  display: block;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.15));
}

.game-hero h1 {
  font-size: 36px !important;
  font-weight: 800 !important;
  letter-spacing: -0.5px;
  margin: 0 0 8px !important;
  padding: 0 !important;
  border: none !important;
  background: linear-gradient(135deg, var(--vp-c-brand-1), var(--vp-c-brand-2, var(--vp-c-brand-1)));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.game-hero .tagline {
  font-size: 18px;
  color: var(--vp-c-text-2);
  margin: 0 0 28px;
  line-height: 1.6;
}

.game-hero-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 32px;
  border-radius: 24px;
  background: var(--vp-c-brand-1);
  color: #fff !important;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none !important;
  transition: all 0.25s ease;
  box-shadow: 0 4px 16px color-mix(in srgb, var(--vp-c-brand-1) 35%, transparent);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px color-mix(in srgb, var(--vp-c-brand-1) 45%, transparent);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 24px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1) !important;
  font-size: 15px;
  font-weight: 500;
  text-decoration: none !important;
  transition: all 0.25s ease;
  border: 1px solid var(--vp-c-divider);
}

.btn-secondary:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1) !important;
}

/* ===== Stats Bar ===== */
.game-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  text-align: center;
  padding: 20px 12px;
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  transition: all 0.25s ease;
}

.stat-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
}

.stat-number {
  font-size: 28px;
  font-weight: 800;
  color: var(--vp-c-brand-1);
  display: block;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--vp-c-text-2);
  margin-top: 4px;
  display: block;
}

/* ===== Section Titles ===== */
.section-title {
  font-size: 22px !important;
  font-weight: 700 !important;
  margin: 40px 0 20px !important;
  padding-bottom: 12px !important;
  border-bottom: 2px solid var(--vp-c-divider) !important;
}

/* ===== Level Cards ===== */
.level-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.level-card {
  padding: 20px;
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  transition: all 0.25s ease;
}

.level-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.level-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.level-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.level-info h4 {
  margin: 0 !important;
  padding: 0 !important;
  font-size: 16px !important;
  font-weight: 700;
  color: var(--vp-c-text-1);
}

.level-info .level-tag {
  font-size: 12px;
  color: var(--vp-c-brand-1);
  font-weight: 600;
}

.level-desc {
  font-size: 14px;
  color: var(--vp-c-text-2);
  line-height: 1.6;
  margin: 0;
}

.level-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.skill-tag {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--vp-c-brand-1) 10%, var(--vp-c-bg));
  color: var(--vp-c-brand-1);
  font-weight: 500;
}

/* ===== Feature List ===== */
.feature-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.feature-item {
  padding: 24px 20px;
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  text-align: center;
  transition: all 0.25s ease;
}

.feature-item:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 32px;
  margin-bottom: 12px;
  display: block;
}

.feature-item h4 {
  margin: 0 0 8px !important;
  padding: 0 !important;
  font-size: 15px !important;
  font-weight: 700;
}

.feature-item p {
  font-size: 13px;
  color: var(--vp-c-text-2);
  line-height: 1.5;
  margin: 0;
}

/* ===== Path Section ===== */
.learning-path {
  display: flex;
  flex-direction: column;
  gap: 0;
  margin-bottom: 32px;
  position: relative;
}

.path-item {
  display: flex;
  gap: 16px;
  padding: 20px 0;
  position: relative;
}

.path-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 19px;
  top: 56px;
  bottom: 0;
  width: 2px;
  background: var(--vp-c-divider);
}

.path-dot {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--vp-c-brand-1) 12%, var(--vp-c-bg));
  border: 2px solid var(--vp-c-brand-1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  z-index: 1;
}

.path-content h4 {
  margin: 0 0 4px !important;
  padding: 0 !important;
  font-size: 16px !important;
  font-weight: 700;
  color: var(--vp-c-text-1);
}

.path-content p {
  margin: 0;
  font-size: 14px;
  color: var(--vp-c-text-2);
  line-height: 1.5;
}

/* ===== CTA Bottom ===== */
.game-cta {
  text-align: center;
  padding: 40px 24px;
  border-radius: 16px;
  background: linear-gradient(135deg,
    var(--vp-c-bg-soft) 0%,
    color-mix(in srgb, var(--vp-c-brand-1) 8%, var(--vp-c-bg-soft)) 100%);
  border: 1px solid var(--vp-c-divider);
  margin-top: 24px;
}

.game-cta h3 {
  font-size: 24px !important;
  font-weight: 800 !important;
  margin: 0 0 8px !important;
  padding: 0 !important;
  border: none !important;
}

.game-cta p {
  color: var(--vp-c-text-2);
  margin: 0 0 24px;
  font-size: 15px;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .game-stats { grid-template-columns: repeat(2, 1fr); }
  .level-grid { grid-template-columns: 1fr; }
  .feature-list { grid-template-columns: 1fr; }
  .game-hero h1 { font-size: 28px !important; }
}

/* Hide default page title */
.VPDoc h1.title { display: none !important; }
</style>

<div class="game-hero">
  <span class="game-hero-icon">⚔️</span>
  <h1>码界觉醒</h1>
  <p class="tagline">用代码征服世界 —— 一款 RPG 编程闯关游戏<br/>通过编写 Python 代码控制角色，沿着「前端 → AI」学习路径逐步通关</p>
  <div class="game-hero-actions">
    <a class="btn-primary" href="https://aigame.lzylu.xyz/" target="_blank" rel="noopener">
      🎮 开始冒险
    </a>
    <a class="btn-secondary" href="#game-intro">
      📖 了解更多
    </a>
  </div>
</div>

<div class="game-stats">
  <div class="stat-card">
    <span class="stat-number">94+</span>
    <span class="stat-label">编程关卡</span>
  </div>
  <div class="stat-card">
    <span class="stat-number">15+</span>
    <span class="stat-label">成就勋章</span>
  </div>
  <div class="stat-card">
    <span class="stat-number">6</span>
    <span class="stat-label">技能领域</span>
  </div>
  <div class="stat-card">
    <span class="stat-number">∞</span>
    <span class="stat-label">进化上限</span>
  </div>
</div>

<h2 class="section-title" id="game-intro">🎯 游戏亮点</h2>

<div class="feature-list">
  <div class="feature-item">
    <span class="feature-icon">📖</span>
    <h4>RPG 沉浸式剧情</h4>
    <p>每一关都有独特的剧情设定，将编程知识融入冒险故事，告别枯燥的代码练习</p>
  </div>
  <div class="feature-item">
    <span class="feature-icon">✍️</span>
    <h4>实时代码编辑</h4>
    <p>内置代码编辑器，即时反馈运行结果，边写代码边闯关，学以致用</p>
  </div>
  <div class="feature-item">
    <span class="feature-icon">🏆</span>
    <h4>成就激励系统</h4>
    <p>经验值、等级、勋章，通过游戏化机制激发持续学习的动力</p>
  </div>
  <div class="feature-item">
    <span class="feature-icon">🗺️</span>
    <h4>学习路径可视化</h4>
    <p>从 Python 基础到 AI 开发，清晰的技能树展示你的成长轨迹</p>
  </div>
  <div class="feature-item">
    <span class="feature-icon">🧩</span>
    <h4>填空式挑战</h4>
    <p>精心设计的代码填空挑战，引导思考而非死记硬背，真正理解编程逻辑</p>
  </div>
  <div class="feature-item">
    <span class="feature-icon">💡</span>
    <h4>智能提示系统</h4>
    <p>遇到困难？每关都有渐进式提示，帮你突破思维瓶颈而不直接给出答案</p>
  </div>
</div>

<h2 class="section-title">🗺️ 冒险地图预览</h2>

<div class="level-grid">
  <div class="level-card">
    <div class="level-header">
      <span class="level-icon">🏕️</span>
      <div class="level-info">
        <span class="level-tag">第一章 · Python 山谷</span>
        <h4>变量之泉</h4>
      </div>
    </div>
    <p class="level-desc">一只代码史莱姆守卫着变量之泉！它用温度谜题阻挡你的去路。用正确的 Python 变量和计算击败它吧！</p>
    <div class="level-skills">
      <span class="skill-tag">变量赋值</span>
      <span class="skill-tag">f-string</span>
      <span class="skill-tag">类型转换</span>
    </div>
  </div>
  <div class="level-card">
    <div class="level-header">
      <span class="level-icon">🌀</span>
      <div class="level-info">
        <span class="level-tag">第一章 · Python 山谷</span>
        <h4>列表迷宫</h4>
      </div>
    </div>
    <p class="level-desc">语法骷髅在列表迷宫中游荡！它们用列表谜题困住了宝物。掌握索引与切片，击败骷髅夺回宝藏！</p>
    <div class="level-skills">
      <span class="skill-tag">list</span>
      <span class="skill-tag">索引</span>
      <span class="skill-tag">切片</span>
    </div>
  </div>
  <div class="level-card">
    <div class="level-header">
      <span class="level-icon">🔀</span>
      <div class="level-info">
        <span class="level-tag">第二章 · 进阶峡谷</span>
        <h4>条件分岔路</h4>
      </div>
    </div>
    <p class="level-desc">分岔路口的史莱姆王挡住了去路！它会根据条件选择不同的攻击方式。你必须用 if/elif/else 逻辑应对！</p>
    <div class="level-skills">
      <span class="skill-tag">if/elif/else</span>
      <span class="skill-tag">布尔逻辑</span>
    </div>
  </div>
  <div class="level-card">
    <div class="level-header">
      <span class="level-icon">🌊</span>
      <div class="level-info">
        <span class="level-tag">第二章 · 进阶峡谷</span>
        <h4>循环旋涡</h4>
      </div>
    </div>
    <p class="level-desc">语法骷髅军团在旋涡中循环出现！使用 for 和 while 循环击退每一波敌人！</p>
    <div class="level-skills">
      <span class="skill-tag">for 循环</span>
      <span class="skill-tag">while 循环</span>
      <span class="skill-tag">range</span>
    </div>
  </div>
</div>

<h2 class="section-title">📈 学习路径</h2>

<div class="learning-path">
  <div class="path-item">
    <div class="path-dot">🐍</div>
    <div class="path-content">
      <h4>Python 山谷 · 新手村</h4>
      <p>基础语法、变量、数据类型、字符串操作 —— 每个编程冒险者的起点</p>
    </div>
  </div>
  <div class="path-item">
    <div class="path-dot">⚡</div>
    <div class="path-content">
      <h4>进阶峡谷</h4>
      <p>条件判断、循环控制、函数定义、异常处理 —— 掌握编程的核心武器</p>
    </div>
  </div>
  <div class="path-item">
    <div class="path-dot">🏗️</div>
    <div class="path-content">
      <h4>工程要塞</h4>
      <p>面向对象、模块系统、文件操作、数据库 —— 构建真实项目的基石</p>
    </div>
  </div>
  <div class="path-item">
    <div class="path-dot">🌐</div>
    <div class="path-content">
      <h4>Web 前沿</h4>
      <p>Web 框架、API 设计、前后端交互 —— 打通全栈开发技能</p>
    </div>
  </div>
  <div class="path-item">
    <div class="path-dot">🤖</div>
    <div class="path-content">
      <h4>AI 圣殿</h4>
      <p>机器学习、NLP、Agent 开发 —— 最终的 Boss 战在这里等你</p>
    </div>
  </div>
</div>

<div class="game-cta">
  <h3>准备好了吗？</h3>
  <p>94+ 关卡等你征服，从 Python 新手到 AI 开发者的进化之路现在开始</p>
  <a class="btn-primary" href="https://aigame.lzylu.xyz/" target="_blank" rel="noopener">
    ⚔️ 立即开启冒险
  </a>
</div>

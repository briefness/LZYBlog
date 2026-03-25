---
layout: doc
title: 编程游戏
description: 通过游戏化的方式学习编程技术，边玩边学，寓教于乐
---

<style>
.game-hub-hero {
  text-align: center;
  padding: 48px 24px 36px;
  border-radius: 16px;
  background: linear-gradient(135deg,
    var(--vp-c-bg-soft) 0%,
    color-mix(in srgb, var(--vp-c-brand-1) 8%, var(--vp-c-bg-soft)) 100%);
  border: 1px solid var(--vp-c-divider);
  margin-bottom: 36px;
}

.game-hub-hero h1 {
  font-size: 36px !important;
  font-weight: 800 !important;
  margin: 0 0 8px !important;
  padding: 0 !important;
  border: none !important;
  background: linear-gradient(135deg, var(--vp-c-brand-1), var(--vp-c-brand-2, var(--vp-c-brand-1)));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.game-hub-hero p {
  font-size: 16px;
  color: var(--vp-c-text-2);
  margin: 0;
  line-height: 1.6;
}

/* ===== Game Cards ===== */
.game-card-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.game-card {
  display: flex;
  gap: 24px;
  padding: 28px;
  border-radius: 16px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  transition: all 0.3s ease;
  text-decoration: none !important;
  color: inherit !important;
}

.game-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.game-card-icon {
  font-size: 52px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 16px;
  background: color-mix(in srgb, var(--vp-c-brand-1) 10%, var(--vp-c-bg));
  border: 1px solid color-mix(in srgb, var(--vp-c-brand-1) 20%, transparent);
}

.game-card-body {
  flex: 1;
  min-width: 0;
}

.game-card-body h3 {
  margin: 0 0 6px !important;
  padding: 0 !important;
  border: none !important;
  font-size: 20px !important;
  font-weight: 700;
}

.game-card-desc {
  font-size: 14px;
  color: var(--vp-c-text-2);
  line-height: 1.6;
  margin: 0 0 12px;
}

.game-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.game-tag {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--vp-c-brand-1) 10%, var(--vp-c-bg));
  color: var(--vp-c-brand-1);
  font-weight: 500;
}

.game-card-meta {
  display: flex;
  gap: 16px;
  margin-top: 10px;
  font-size: 13px;
  color: var(--vp-c-text-3);
}

.game-card-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

@media (max-width: 640px) {
  .game-card { flex-direction: column; gap: 16px; }
  .game-hub-hero h1 { font-size: 28px !important; }
}

/* Hide default page title */
.VPDoc h1.title { display: none !important; }
</style>

<div class="game-hub-hero">
  <h1>🎮 编程游戏</h1>
  <p>把枯燥的编程学习变成冒险闯关，用游戏化的方式掌握真正的技术能力</p>
</div>

<div class="game-card-list">
  <a class="game-card" href="/playground/code-quest">
    <div class="game-card-icon">⚔️</div>
    <div class="game-card-body">
      <h3>码界觉醒</h3>
      <p class="game-card-desc">用代码征服世界 —— 一款 RPG 编程闯关游戏。通过编写 Python 代码控制角色，沿着「前端 → AI」学习路径，在剧情驱动的冒险中逐步通关。每一关都有独特的故事和编程挑战。</p>
      <div class="game-card-tags">
        <span class="game-tag">Python</span>
        <span class="game-tag">AI 开发</span>
        <span class="game-tag">RPG 剧情</span>
        <span class="game-tag">代码填空</span>
      </div>
      <div class="game-card-meta">
        <span>📚 94+ 关卡</span>
        <span>🏆 15+ 成就</span>
        <span>🗺️ 6 大章节</span>
      </div>
    </div>
  </a>
</div>

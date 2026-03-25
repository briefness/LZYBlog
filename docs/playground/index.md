---
layout: page
title: 编程游戏 - 码界觉醒
description: 一款 RPG 编程闯关游戏，通过编写 Python 代码控制角色，沿着前端转 AI 学习路径逐步通关
---

<style>
.VPDoc .container { max-width: 100% !important; }
.VPDoc .content { padding: 0 !important; max-width: 100% !important; }
.VPDoc .content-container { max-width: 100% !important; }
.VPContent .VPDoc { padding: 0 !important; }
/* 隐藏侧边栏和页脚，让游戏全屏展示 */
.VPDoc .aside { display: none !important; }
.VPDocFooter { display: none !important; }
.VPDoc { width: 100% !important; }

.game-wrapper {
  width: 100%;
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
}

.game-header {
  padding: 16px 24px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-shrink: 0;
}

.game-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.game-header h2 {
  margin: 0 !important;
  padding: 0 !important;
  font-size: 20px !important;
  font-weight: 700;
  background: linear-gradient(90deg, #e2e8f0, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  border: none !important;
  line-height: 1.4 !important;
}

.game-header p {
  margin: 0;
  font-size: 13px;
  color: #94a3b8;
}

.game-header-actions a {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  background: rgba(167, 139, 250, 0.15);
  color: #a78bfa;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
  border: 1px solid rgba(167, 139, 250, 0.2);
}

.game-header-actions a:hover {
  background: rgba(167, 139, 250, 0.25);
  border-color: rgba(167, 139, 250, 0.4);
}

.game-frame {
  flex: 1;
  border: none;
  width: 100%;
  display: block;
}
</style>

<div class="game-wrapper">
  <div class="game-header">
    <div class="game-header-left">
      <div>
        <h2>⚔️ 码界觉醒 - 用代码征服世界</h2>
        <p>RPG 编程闯关游戏 · 通过编写 Python 代码控制角色 · 沿着前端转 AI 学习路径逐步通关</p>
      </div>
    </div>
    <div class="game-header-actions">
      <a href="https://aigame.lzylu.xyz/" target="_blank" rel="noopener">
        ↗ 新窗口打开
      </a>
    </div>
  </div>
  <iframe 
    class="game-frame" 
    src="https://aigame.lzylu.xyz/" 
    title="码界觉醒 - RPG 编程闯关游戏"
    allow="clipboard-read; clipboard-write"
    loading="lazy"
  ></iframe>
</div>

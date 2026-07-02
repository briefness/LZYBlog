<script setup>
import { ref, onMounted, computed } from 'vue'

const repos = ref([])
const loading = ref(true)
const error = ref(null)
const username = 'briefness'

// 白名单：仅展示这些仓库
const allowedRepos = [
  'fabric-region',
  'ant-design-l',
  'InstantVideo',
  'B2B2C',
  'OmniPost',
  'PoseAI',
  'ffmpeg-performance',
  'web-to-ai',
  'HarmonyDemo',
  'BaseCut',
  'Google-Timer',
  'SecPilot',
  'kling-ad-automation',
]

// GitHub 语言品牌色
const langColors = {
  JavaScript: '#f1e05a',
  TypeScript: '#3178c6',
  Python: '#3572A5',
  Vue: '#41b883',
  Dart: '#00B4AB',
  HTML: '#e34c26',
  CSS: '#563d7c',
  Java: '#b07219',
  Kotlin: '#A97BFF',
  Swift: '#F05138',
  Go: '#00ADD8',
  Rust: '#dea584',
  Shell: '#89e051',
  C: '#555555',
  'C++': '#f34b7d',
  'C#': '#178600',
  Ruby: '#701516',
  PHP: '#4F5D95',
  Jupyter: '#DA5B0B',
  'Jupyter Notebook': '#DA5B0B',
  Markdown: '#083fa1',
}

async function fetchRepos() {
  try {
    loading.value = true
    error.value = null
    const res = await fetch(
      `https://api.github.com/users/${username}/repos?per_page=100&sort=updated`
    )
    if (!res.ok) {
      throw new Error(`GitHub API 请求失败: ${res.status}`)
    }
    const data = await res.json()
    repos.value = data
      .filter(repo => allowedRepos.includes(repo.name))
      .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return '今天'
  if (diffDays === 1) return '昨天'
  if (diffDays < 30) return `${diffDays} 天前`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} 个月前`
  return `${Math.floor(diffDays / 365)} 年前`
}

function getLangColor(lang) {
  return langColors[lang] || '#8b949e'
}

const stats = computed(() => {
  const total = repos.value.length
  const totalStars = repos.value.reduce((sum, r) => sum + r.stargazers_count, 0)
  const totalForks = repos.value.reduce((sum, r) => sum + r.forks_count, 0)
  return { total, totalStars, totalForks }
})

// 语言分布统计
const langStats = computed(() => {
  const map = {}
  repos.value.forEach(r => {
    if (r.language) {
      map[r.language] = (map[r.language] || 0) + 1
    }
  })
  const total = Object.values(map).reduce((a, b) => a + b, 0)
  return Object.entries(map)
    .sort((a, b) => b[1] - a[1])
    .map(([lang, count]) => ({
      lang,
      count,
      percent: Math.round((count / total) * 100),
      color: getLangColor(lang),
    }))
})

onMounted(fetchRepos)
</script>

<template>
  <div class="github-projects">
    <!-- Hero Section -->
    <div class="gp-hero">
      <div class="gp-hero-bg"></div>
      <div class="gp-hero-content">
        <a :href="`https://github.com/${username}`" target="_blank" rel="noopener" class="gp-avatar-link">
          <div class="gp-avatar-ring">
            <img
              :src="`https://avatars.githubusercontent.com/${username}`"
              :alt="username"
              class="gp-avatar"
            />
          </div>
        </a>
        <div class="gp-hero-info">
          <h1 class="gp-title">
            <a :href="`https://github.com/${username}`" target="_blank" rel="noopener">
              @{{ username }}
            </a>
          </h1>
          <p class="gp-tagline">探索 · 创造 · 开源</p>
          <div v-if="!loading && !error" class="gp-stats-row">
            <div class="gp-stat-pill">
              <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
                <path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"/>
              </svg>
              <strong>{{ stats.total }}</strong> 仓库
            </div>
            <div class="gp-stat-pill">
              <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
                <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"/>
              </svg>
              <strong>{{ stats.totalStars }}</strong> Stars
            </div>
            <div class="gp-stat-pill">
              <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
                <path d="M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"/>
              </svg>
              <strong>{{ stats.totalForks }}</strong> Forks
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Language Bar -->
    <div v-if="!loading && !error && langStats.length" class="gp-lang-section">
      <div class="gp-lang-bar">
        <div
          v-for="ls in langStats"
          :key="ls.lang"
          class="gp-lang-bar-seg"
          :style="{ width: ls.percent + '%', backgroundColor: ls.color }"
          :title="`${ls.lang} ${ls.percent}%`"
        ></div>
      </div>
      <div class="gp-lang-legend">
        <span v-for="ls in langStats" :key="ls.lang" class="gp-lang-tag">
          <span class="gp-lang-dot" :style="{ backgroundColor: ls.color }"></span>
          {{ ls.lang }} <span class="gp-lang-pct">{{ ls.percent }}%</span>
        </span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="gp-loading">
      <div class="gp-loading-dots">
        <span></span><span></span><span></span>
      </div>
      <p>正在加载项目数据…</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="gp-error">
      <div class="gp-error-icon">!</div>
      <p>{{ error }}</p>
      <button @click="fetchRepos" class="gp-retry-btn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <path d="M1 4v6h6M23 20v-6h-6"/>
          <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
        </svg>
        重试
      </button>
    </div>

    <!-- Repo Cards -->
    <div v-else class="gp-grid">
      <a
        v-for="(repo, index) in repos"
        :key="repo.id"
        :href="repo.html_url"
        target="_blank"
        rel="noopener"
        class="gp-card"
        :style="{ '--delay': index * 60 + 'ms' }"
      >
        <!-- 卡片顶部装饰条 -->
        <div class="gp-card-accent" :style="{ background: `linear-gradient(135deg, ${getLangColor(repo.language)} 0%, ${getLangColor(repo.language)}88 100%)` }"></div>

        <div class="gp-card-body">
          <div class="gp-card-header">
            <div class="gp-card-icon-wrap" :style="{ '--accent': getLangColor(repo.language) }">
              <svg viewBox="0 0 16 16" fill="currentColor" width="18" height="18">
                <path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"/>
              </svg>
            </div>
            <div class="gp-card-title-group">
              <span class="gp-card-name">{{ repo.name }}</span>
              <span v-if="repo.language" class="gp-card-lang" :style="{ color: getLangColor(repo.language) }">
                {{ repo.language }}
              </span>
            </div>
          </div>

          <p class="gp-card-desc">{{ repo.description || '暂无描述' }}</p>

          <div class="gp-card-footer">
            <div class="gp-card-metrics">
              <span v-if="repo.stargazers_count > 0" class="gp-metric">
                <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
                  <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"/>
                </svg>
                {{ repo.stargazers_count }}
              </span>
              <span v-if="repo.forks_count > 0" class="gp-metric">
                <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
                  <path d="M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"/>
                </svg>
                {{ repo.forks_count }}
              </span>
            </div>
            <span class="gp-card-time">{{ formatDate(repo.updated_at) }}</span>
          </div>
        </div>
      </a>
    </div>
  </div>
</template>

<style scoped>
.github-projects {
  max-width: 1152px;
  margin: 0 auto;
  padding: 0 24px 48px;
}

/* ========== Hero ========== */
.gp-hero {
  position: relative;
  margin: -32px -24px 0;
  padding: 56px 32px 40px;
  overflow: hidden;
}

.gp-hero-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 20% 0%, rgba(88, 166, 255, 0.12) 0%, transparent 70%),
    radial-gradient(ellipse 60% 50% at 80% 20%, rgba(136, 87, 229, 0.10) 0%, transparent 70%),
    radial-gradient(ellipse 40% 40% at 50% 100%, rgba(63, 185, 80, 0.06) 0%, transparent 70%);
  z-index: 0;
}

.dark .gp-hero-bg {
  background:
    radial-gradient(ellipse 80% 60% at 20% 0%, rgba(88, 166, 255, 0.08) 0%, transparent 70%),
    radial-gradient(ellipse 60% 50% at 80% 20%, rgba(136, 87, 229, 0.07) 0%, transparent 70%),
    radial-gradient(ellipse 40% 40% at 50% 100%, rgba(63, 185, 80, 0.04) 0%, transparent 70%);
}

.gp-hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 28px;
}

/* Avatar */
.gp-avatar-link {
  flex-shrink: 0;
  text-decoration: none;
}

.gp-avatar-ring {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  padding: 3px;
  background: conic-gradient(from 0deg, #58a6ff, #8957e5, #3fb950, #f78166, #58a6ff);
  transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  animation: gp-ring-rotate 8s linear infinite;
}

@keyframes gp-ring-rotate {
  to { filter: hue-rotate(360deg); }
}

.gp-avatar-ring:hover {
  transform: scale(1.08) rotate(5deg);
}

.gp-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: block;
  object-fit: cover;
  border: 3px solid var(--vp-c-bg);
}

/* Hero text */
.gp-hero-info {
  flex: 1;
  min-width: 0;
}

.gp-title {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
  line-height: 1.2;
}

.gp-title a {
  color: var(--vp-c-text-1);
  text-decoration: none;
  background: linear-gradient(135deg, var(--vp-c-text-1), var(--vp-c-brand-1));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gp-tagline {
  margin: 6px 0 0;
  font-size: 15px;
  color: var(--vp-c-text-2);
  letter-spacing: 2px;
}

/* Stat pills */
.gp-stats-row {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.gp-stat-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  color: var(--vp-c-text-2);
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  transition: border-color 0.2s, background 0.2s;
}

.gp-stat-pill strong {
  color: var(--vp-c-text-1);
  font-weight: 700;
}

.gp-stat-pill svg {
  opacity: 0.6;
}

/* ========== Language Bar ========== */
.gp-lang-section {
  margin: 32px 0;
}

.gp-lang-bar {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  gap: 2px;
}

.gp-lang-bar-seg {
  border-radius: 4px;
  transition: opacity 0.2s;
  min-width: 3px;
}

.gp-lang-bar-seg:hover {
  opacity: 0.75;
}

.gp-lang-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
}

.gp-lang-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--vp-c-text-2);
}

.gp-lang-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.gp-lang-pct {
  color: var(--vp-c-text-3);
  font-variant-numeric: tabular-nums;
}

/* ========== Loading ========== */
.gp-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 20px;
  color: var(--vp-c-text-2);
}

.gp-loading-dots {
  display: flex;
  gap: 6px;
}

.gp-loading-dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--vp-c-brand-1);
  animation: gp-bounce 1.2s ease-in-out infinite;
}

.gp-loading-dots span:nth-child(2) { animation-delay: 0.15s; }
.gp-loading-dots span:nth-child(3) { animation-delay: 0.3s; }

@keyframes gp-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* ========== Error ========== */
.gp-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 16px;
}

.gp-error-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(248, 81, 73, 0.1);
  color: #f85149;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
}

.gp-error p {
  color: var(--vp-c-text-2);
  font-size: 14px;
}

.gp-retry-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  border-radius: 8px;
  border: 1px solid var(--vp-c-brand-1);
  background: transparent;
  color: var(--vp-c-brand-1);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.gp-retry-btn:hover {
  background: var(--vp-c-brand-1);
  color: #fff;
}

/* ========== Card Grid ========== */
.gp-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

/* ========== Card ========== */
.gp-card {
  position: relative;
  display: flex;
  flex-direction: column;
  border-radius: 14px;
  text-decoration: none;
  overflow: hidden;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease, border-color 0.3s ease;
  animation: gp-card-in 0.4s ease both;
  animation-delay: var(--delay);
}

@keyframes gp-card-in {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.gp-card:hover {
  transform: translateY(-6px);
  box-shadow:
    0 20px 40px -12px rgba(0, 0, 0, 0.08),
    0 0 0 1px var(--vp-c-brand-1);
  border-color: var(--vp-c-brand-1);
}

.dark .gp-card:hover {
  box-shadow:
    0 20px 40px -12px rgba(0, 0, 0, 0.35),
    0 0 0 1px var(--vp-c-brand-1);
}

/* Top accent bar */
.gp-card-accent {
  height: 3px;
  flex-shrink: 0;
}

.gp-card-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 20px;
}

/* Card header */
.gp-card-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.gp-card-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  color: var(--accent);
  transition: transform 0.2s, background 0.2s;
}

.gp-card:hover .gp-card-icon-wrap {
  background: color-mix(in srgb, var(--accent) 20%, transparent);
  transform: scale(1.1);
}

.gp-card-title-group {
  min-width: 0;
  flex: 1;
}

.gp-card-name {
  display: block;
  font-size: 16px;
  font-weight: 650;
  color: var(--vp-c-text-1);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
  transition: color 0.2s;
}

.gp-card:hover .gp-card-name {
  color: var(--vp-c-brand-1);
}

.gp-card-lang {
  font-size: 12px;
  font-weight: 500;
  opacity: 0.8;
}

/* Card description */
.gp-card-desc {
  flex: 1;
  margin: 0 0 16px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--vp-c-text-2);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Card footer */
.gp-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 14px;
  border-top: 1px solid var(--vp-c-divider);
}

.gp-card-metrics {
  display: flex;
  align-items: center;
  gap: 12px;
}

.gp-metric {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--vp-c-text-3);
  font-variant-numeric: tabular-nums;
}

.gp-metric svg {
  opacity: 0.6;
}

.gp-card-time {
  font-size: 12px;
  color: var(--vp-c-text-3);
}

/* ========== Responsive ========== */
@media (max-width: 640px) {
  .github-projects {
    padding: 0 16px 32px;
  }

  .gp-hero {
    margin: -24px -16px 0;
    padding: 40px 20px 32px;
  }

  .gp-hero-content {
    flex-direction: column;
    text-align: center;
  }

  .gp-avatar-ring {
    width: 72px;
    height: 72px;
  }

  .gp-title {
    font-size: 22px;
  }

  .gp-stats-row {
    justify-content: center;
  }

  .gp-grid {
    grid-template-columns: 1fr;
  }
}
</style>

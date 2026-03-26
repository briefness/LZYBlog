
import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

function getSidebarItems(dirName: string, title: string) {
  const dirPath = path.resolve(__dirname, '../posts', dirName)
  const indexPath = path.join(dirPath, 'index.md')
  const items: { text: string, link: string }[] = []

  // Strategy 1: Parse index.md for order and titles
  if (fs.existsSync(indexPath)) {
    const content = fs.readFileSync(indexPath, 'utf-8')
    // Match [Title](link)
    // Exclude links starting with http or # or mailto
    const regex = /\[([^\]]+)\]\((?!http|#|mailto)([^)]+)\)/g
    let match
    while ((match = regex.exec(content)) !== null) {
      const [_, text, link] = match
      
      // Clean up link
      let cleanLink = link.replace(/^\.\//, '') // Remove ./
      if (cleanLink.endsWith('.md')) {
        cleanLink = cleanLink.slice(0, -3)
      }
      
      // Handle subdirectories if needed (e.g. Articles/xx)
      // Usually links in index.md are relative to index.md
      
      items.push({
        text: text.trim(), // Clean text
        link: `/posts/${dirName}/${cleanLink}`
      })
    }
  } 
  
  // Strategy 2: Fallback to scanning directory if no items found in index.md (or index.md missing)
  if (items.length === 0 && fs.existsSync(dirPath)) {
    const files = fs.readdirSync(dirPath)
    files.sort().forEach(file => {
      // Skip index.md itself, skip folders (unless we want to recurse, but keep simple for now)
      if (file.endsWith('.md') && file !== 'index.md') {
         items.push({
           text: file.replace('.md', ''),
           link: `/posts/${dirName}/${file.replace('.md', '')}`
         })
      }
    })
  }

  return [
    {
      text: title,
      items: [
        { text: '目录', link: `/posts/${dirName}/index` },
        ...items
      ]
    }
  ]
}

// https://vitepress.dev/reference/site-config
export default withMermaid(
  defineConfig({
    title: "阿乐的博客",
    description: "技术探索",
    head: [['link', { rel: 'icon', href: '/logo.png' }]],
    themeConfig: {
      logo: '/logo.png',
      // https://vitepress.dev/reference/default-theme-config
      nav: [
        { text: '首页', link: '/' },
        {
          text: 'AI & 智能体',
          items: [
            { text: 'AI 认知', link: '/posts/AI/index' },
            { text: 'Agent 实战', link: '/posts/Agent/index' },
            { text: 'Coze', link: '/posts/coze/index' },
            { text: 'OpenClaw', link: '/posts/OpenClaw/index' }
          ]
        },
        {
          text: '移动 & 跨端',
          items: [
            { text: 'HarmonyOS', link: '/posts/harmonyos/index' },
            { text: 'Flutter', link: '/posts/Flutter/index' },
            { text: 'BaseCut', link: '/posts/BaseCut/index' }
          ]
        },
        {
          text: '后端技术',
          items: [
            { text: 'Python 全栈', link: '/posts/Python/index' }
          ]
        },
        {
          text: '前端技术',
          items: [
            { text: 'Vue3', link: '/posts/Vue3/index' },
            { text: 'React', link: '/posts/React/index' },
            { text: '前端性能', link: '/posts/Performance/index' },
            { text: 'NodeJS', link: '/posts/NodeJS/index' }
          ]
        },
        { text: '🎮 编程游戏', items: [
            { text: '码界觉醒', link: '/playground/code-quest' }
          ]
        }
      ],

      sidebar: {
        '/posts/AI/': getSidebarItems('AI', 'AI 认知'),
        '/posts/Agent/': getSidebarItems('Agent', 'Agent 实战'),
        '/posts/coze/': getSidebarItems('coze', 'Coze'),
        '/posts/OpenClaw/': getSidebarItems('OpenClaw', 'OpenClaw 原理拆解'),
        '/posts/Python/': getSidebarItems('Python', 'Python 全栈'),
        '/posts/harmonyos/': getSidebarItems('harmonyos', 'HarmonyOS'),
        '/posts/Flutter/': getSidebarItems('Flutter', 'Flutter'),
        '/posts/BaseCut/': getSidebarItems('BaseCut', 'BaseCut'),
        '/posts/Vue3/': getSidebarItems('Vue3', 'Vue3'),
        '/posts/React/': getSidebarItems('React', 'React'),
        '/posts/Performance/': getSidebarItems('Performance', '前端性能'),
        '/posts/NodeJS/': getSidebarItems('NodeJS', 'NodeJS'),
        '/posts/miniprogram/': getSidebarItems('miniprogram', '微信小程序')
      }
    },
    ignoreDeadLinks: [
      // Manim 动画是 .py 文件，VitePress 无法解析，忽略检查
      /\/animations\/.+\.py$/,
    ],
    mermaid: {
      // 可选配置
    }
  })
)

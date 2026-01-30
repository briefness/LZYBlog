import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

// https://vitepress.dev/reference/site-config
export default withMermaid(
  defineConfig({
    title: "阿乐的博客",
    description: "技术探索",
    themeConfig: {
      // https://vitepress.dev/reference/default-theme-config
      nav: [
        { text: '首页', link: '/' },
        { text: 'AI 认知', link: '/posts/AI/index' },
        { text: 'Coze', link: '/posts/coze/index' },
        { text: 'HarmonyOS', link: '/posts/harmonyos/index' },
        { text: 'BaseCut', link: '/posts/BaseCut/index' }
      ],

      sidebar: [
        {
          text: '技术笔记',
          items: [
            { text: 'AI 认知', link: '/posts/AI/index' },
            { text: 'Coze', link: '/posts/coze/index' },
            { text: 'HarmonyOS', link: '/posts/harmonyos/index' },
            { text: 'BaseCut', link: '/posts/BaseCut/index' }
          ]
        }
      ],


    },
    // Mermaid 配置
    mermaid: {
      // 可选配置
    }
  })
)

import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

// https://vitepress.dev/reference/site-config
export default withMermaid(
  defineConfig({
    title: "LZY Blog",
    description: "Tech Notes & Life",
    themeConfig: {
      // https://vitepress.dev/reference/default-theme-config
      nav: [
        { text: '首页', link: '/' },
        { text: 'Coze', link: '/posts/coze/index' },
        { text: 'HarmonyOS', link: '/posts/harmonyos/index' },
        { text: 'BaseCut', link: '/posts/BaseCut/index' }
      ],

      sidebar: [
        {
          text: '技术笔记',
          items: [
            { text: 'Coze', link: '/posts/coze/index' },
            { text: 'HarmonyOS', link: '/posts/harmonyos/index' },
            { text: 'BaseCut', link: '/posts/BaseCut/index' }
          ]
        }
      ],

      socialLinks: [
        { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
      ]
    },
    // Mermaid 配置
    mermaid: {
      // 可选配置
    }
  })
)

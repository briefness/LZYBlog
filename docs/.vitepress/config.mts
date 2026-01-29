import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "LZY Blog",
  description: "Tech Notes & Life",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Tech Notes', link: '/posts/tech-notes' }
    ],

    sidebar: [
      {
        text: 'Tech Notes',
        items: [
          { text: 'Tech Notes', link: '/posts/tech-notes' },
          { text: 'FFmpeg Basics', link: '/posts/ffmpeg/basics' },
          { text: 'Vue', link: '/posts/vue/index' },
          { text: 'Electron', link: '/posts/electron/index' },
          { text: 'Coze', link: '/posts/coze/index' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ]
  }
})

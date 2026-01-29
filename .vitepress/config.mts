import { defineConfig } from 'vitepress'


// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "LZY Blog",
  description: "Vue 3, Electron, FFmpeg Technical Notes",
  
  vite: {
    plugins: []
  },

  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'HarmonyOS', link: '/posts/harmonyos/' },
      { text: 'Coze AI', link: '/posts/coze/' },
      { text: 'Tech Notes', link: '/posts/tech-notes' },
      { text: 'Life', link: '/posts/life' }
    ],

    sidebar: {
      '/posts/harmonyos/': [
        {
          text: 'HarmonyOS Development',
          items: [
            { text: 'Overview', link: '/posts/harmonyos/' },
            { text: '1. Environment & Hello World', link: '/posts/harmonyos/Articles/HelloHarmony' },
            { text: '2. Basic UI & Layout', link: '/posts/harmonyos/Articles/BasicUI' },
            { text: '3. Todo List & State', link: '/posts/harmonyos/Articles/TodoList' },
            { text: '4. Navigation & Routing', link: '/posts/harmonyos/Articles/Navigation' },
            { text: '5. Animations', link: '/posts/harmonyos/Articles/Animations' },
            { text: '6. Custom Drawing (Canvas)', link: '/posts/harmonyos/Articles/Drawing' },
            { text: '7. Components & Architecture', link: '/posts/harmonyos/Articles/Components' },
            { text: '8. Network (RCP)', link: '/posts/harmonyos/Articles/Network' },
            { text: '9. Local Database (RDB)', link: '/posts/harmonyos/Articles/Persistence' },
            { text: '10. Advanced State (V2)', link: '/posts/harmonyos/Articles/AdvancedState' },
            { text: '11. Media (Audio/Video)', link: '/posts/harmonyos/Articles/Media' },
            { text: '12. Notifications', link: '/posts/harmonyos/Articles/Notifications' },
            { text: '13. Web Components', link: '/posts/harmonyos/Articles/Web' },
            { text: '14. Concurrency', link: '/posts/harmonyos/Articles/Concurrency' },
            { text: '15. Hardware & Privacy', link: '/posts/harmonyos/Articles/Hardware' },
            { text: '16. Service Widgets', link: '/posts/harmonyos/Articles/ServiceWidgets' },
            { text: '17. Performance Tuning', link: '/posts/harmonyos/Articles/Performance' },
            { text: '18. Publishing', link: '/posts/harmonyos/Articles/Publishing' }
          ]
        }
      ],
      '/posts/coze/': [
        {
          text: 'Coze AI Agent',
          items: [
            { text: '1. Introduction', link: '/posts/coze/01_Coze_Introduction' },
            { text: '2. Prompt Engineering', link: '/posts/coze/02_Prompt_Engineering' },
            { text: '3. Knowledge Base & RAG', link: '/posts/coze/03_Knowledge_Base_RAG' },
            { text: '4. Workflows Logic', link: '/posts/coze/04_Workflows_Logic' },
            { text: '5. Plugins & Tools', link: '/posts/coze/05_Plugins_Tools' },
            { text: '6. Database & Memory', link: '/posts/coze/06_Database_Memory' },
            { text: '7. Advanced Logic (Code)', link: '/posts/coze/07_Advanced_Logic_Code' },
            { text: '8. Multi-Agent & Triggers', link: '/posts/coze/08_Multi_Agent_Triggers' },
            { text: '9. Expert Best Practices', link: '/posts/coze/09_Expert_Best_Practices' },
            { text: '10. Publishing & Integration', link: '/posts/coze/10_Publishing_Integration' }
          ]
        }
      ],
      '/posts/tech-notes': [
        {
          text: 'Tech Notes',
          items: [
            { text: 'Introduction', link: '/posts/tech-notes' },
            { text: 'Vue 3', link: '/posts/vue/' },
            { text: 'Electron', link: '/posts/electron/' },
            { text: 'FFmpeg', link: '/posts/ffmpeg/' }
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ],

    search: {
      provider: 'local'
    }
  }
})

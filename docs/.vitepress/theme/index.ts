import { h } from 'vue'
import Theme from 'vitepress/theme'
import { useData } from 'vitepress'
import './style.css'
import CustomHome from './CustomHome.vue'

export default {
  extends: Theme,
  Layout: () => {
    const { frontmatter } = useData()
    if (frontmatter.value.layout === 'bento') {
      return h(CustomHome)
    }
    return h(Theme.Layout, null, {
      // https://vitepress.dev/guide/extending-default-theme#layout-slots
    })
  },
  enhanceApp({ app }) {
    app.component('CustomHome', CustomHome)
  }
}

# Vue 3 深度精通 (七) —— 工程化基石与最佳实践

完善的工程化体系是优秀项目的基础。Vite + TypeScript + ESLint + Prettier 构成了现代前端开发的黄金组合。

## Vite 进阶配置与插件开发

Vite 性能优异，以下介绍如何编写简单的插件。

### 插件原理

Vite 插件扩展了 Rollup 接口。最常用的是 `transform`钩子，在代码被请求时转换代码。

```javascript
// vite-plugin-my-transform.js
export default function myPlugin() {
  return {
    name: 'transform-file',
    transform(code, id) {
      if (id.endsWith('.vue')) {
        return code.replace(/console\.log/g, 'void 0') // 删除 console.log
      }
    }
  }
}
```

### 环境变量

Vite 使用 `import.meta.env` 暴露环境变量。

1.  `.env`：所有环境
2.  `.env.development`：开发环境
3.  `.env.production`：生产环境

```javascript
console.log(import.meta.env.VITE_API_URL)
console.log(import.meta.env.MODE) // 'development' or 'production'
```

**类型提示**：在 `vite-env.d.ts` 中扩展 `ImportMetaEnv` 接口，获得智能提示。

## TypeScript 高级类型与 Volar

### `defineProps` 与 `withDefaults`

在 TypeScript 中，`defineProps` 的泛型写法比运行时声明更强大。

```typescript
interface Props {
  msg?: string
  labels?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  msg: 'hello',
  labels: () => ['one', 'two']
})
```

### Volar (Vue - Official)

Volar 是 Vue 3 开发的必备插件。它不仅提供高亮和补全，还能进行模板类型检查。
如果遇到类型报错，尝试重启 `Vue Language Server`。

## 代码规范与 Git Hooks

### ESLint + Prettier (Modern Way)

现在推荐使用 ESLint 的 **Flat Config** 格式（ESLint 9+）。若希望简化配置，可直接使用社区预设：

```bash
npm install -D @antfu/eslint-config
```

在 `eslint.config.mjs` 中：

```javascript
import antfu from '@antfu/eslint-config'

export default antfu({
  vue: true,
  typescript: true,
})
```

这会自动配置好 Vue、TS、Prettier 的所有最佳实践，无需手动解决冲突。

### Husky + Commitlint

在 `git commit` 时自动检查代码风格和提交信息格式。

1.  安装 `husky`: `npx husky-init && npm install`
2.  添加 hook: `npx husky add .husky/pre-commit "npm run lint"`
3.  安装 `commitlint`: `npm install --save-dev @commitlint/{config-conventional,cli}`
4.  配置 `commitlint.config.js`:
    ```javascript
    module.exports = { extends: ['@commitlint/config-conventional'] }
    ```

这样，只有符合 `feat: add new feature` 格式的提交才能通过。

### 这就是全部了吗？

工程化涵盖范畴广泛，单元测试（**Vitest**）和 E2E 测试（**Playwright**）将在第 11 篇《全栈生态》中详细探讨。

## 结语

工程化配置是一次性投入，长期受益。下一篇将解锁 Vue 3 的**隐藏技能与黑科技**，包括 `defineModel`, JSX, 以及自定义指令的高阶用法。

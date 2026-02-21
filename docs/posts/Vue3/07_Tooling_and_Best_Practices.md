# Vue 3 深度精通 (七) —— 工程化基石与最佳实践

完善的工程化体系是优秀项目的基础。Vite + TypeScript + ESLint + Prettier 构成了现代前端开发的黄金组合。但真正的工程化远不止于此——自动导入、Monorepo 管理、Git 卡点，每一项配置都是一次性投入、长期受益。

## Vite 进阶配置与插件开发

### 插件原理

Vite 插件扩展了 Rollup 接口。最常用的是 `transform` 钩子，在代码被请求时转换代码：

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

另一个实用钩子是 `configureServer`，可以在开发服务器上添加自定义中间件：

```javascript
export default function apiMockPlugin() {
  return {
    name: 'api-mock',
    configureServer(server) {
      server.middlewares.use('/api/user', (req, res) => {
        res.end(JSON.stringify({ name: 'Lucas', role: 'admin' }))
      })
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

**类型提示**：在 `env.d.ts` 中扩展 `ImportMetaEnv` 接口，IDE 会自动补全所有自定义环境变量：

```typescript
/// <reference types="vite/client" />
interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_ENABLE_MOCK: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

## 自动导入：消灭样板代码

每个 `.vue` 文件顶部都要写 `import { ref, computed, watch } from 'vue'`，重复且繁琐。通过 unplugin 系列工具可以彻底消除这些 import 语句。

### unplugin-auto-import

自动导入 Vue、Vue Router、Pinia 等库的 API：

```javascript
// vite.config.ts
import AutoImport from 'unplugin-auto-import/vite'

export default defineConfig({
  plugins: [
    AutoImport({
      imports: ['vue', 'vue-router', 'pinia'],
      dts: 'src/auto-imports.d.ts', // 生成类型声明
    }),
  ],
})
```

配置之后，`ref`、`computed`、`useRouter`、`storeToRefs` 全部不需要手动 import。Vite 编译时会自动注入。

### unplugin-vue-components

自动导入组件，无需手动 `import MyButton from '@/components/MyButton.vue'`：

```javascript
import Components from 'unplugin-vue-components/vite'
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    Components({
      dirs: ['src/components'],           // 自动扫描目录
      resolvers: [AntDesignVueResolver()], // UI 库按需引入
      dts: 'src/components.d.ts',
    }),
  ],
})
```

效果：在模板中直接用 `<MyButton />`，Vite 会自动从 `src/components/MyButton.vue` 引入。对于 Ant Design Vue、Element Plus 等 UI 库，配合 resolver 还能实现按需引入，不打包未使用的组件。

## TypeScript 高级类型与 Volar

### `defineProps` 与 `withDefaults`

在 TypeScript 中，`defineProps` 的泛型写法比运行时声明更强大：

```typescript
interface Props {
  msg?: string
  labels?: string[]
  config?: { theme: 'light' | 'dark'; locale: string }
}

const props = withDefaults(defineProps<Props>(), {
  msg: 'hello',
  labels: () => ['one', 'two'],
  config: () => ({ theme: 'light', locale: 'zh-CN' }),
})
```

**陷阱**：引用类型的默认值必须用工厂函数 `() => []` 包裹，不能直接写 `['one', 'two']`。否则多个组件实例会共享同一个数组引用，导致数据污染。

### Volar (Vue - Official)

Volar 是 Vue 3 开发的必备插件。它不仅提供高亮和补全，还能进行模板类型检查——能在编译前就发现模板中的类型错误。

如果遇到类型报错但代码确认无误，尝试重启 `Vue Language Server`（Cmd+Shift+P → Restart Vue Language Server）。

## Monorepo 工程实践

当项目包含多个子包（组件库、工具函数、文档站点等）时，Monorepo 是主流的组织方式。

### pnpm workspaces

```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

```
my-project/
├── apps/
│   ├── web/          # 主应用
│   └── docs/         # 文档站点
├── packages/
│   ├── ui/           # 组件库
│   ├── utils/        # 工具函数
│   └── eslint-config/ # 共享 ESLint 配置
├── pnpm-workspace.yaml
└── package.json
```

子包之间通过 `workspace:*` 协议引用：

```json
{
  "dependencies": {
    "@my-project/ui": "workspace:*",
    "@my-project/utils": "workspace:*"
  }
}
```

### Turborepo 加速构建

当 Monorepo 中的包越来越多时，`turbo` 可以并行执行任务并缓存构建结果：

```json
// turbo.json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "lint": {},
    "test": {}
  }
}
```

`turbo run build` 会分析依赖图，按正确顺序并行构建。如果某个包的源码没变，直接复用缓存，跳过构建。

## 代码规范与 Git Hooks

### ESLint + Prettier (Modern Way)

推荐使用 ESLint 的 **Flat Config** 格式（ESLint 9+）。若希望简化配置，直接使用社区预设：

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

这会自动配置好 Vue、TS、Prettier 的所有规则，无需手动解决冲突。

### Husky + lint-staged

在 `git commit` 时自动检查代码风格和提交信息格式：

```bash
# 初始化 husky
npx husky-init && npm install

# 安装 lint-staged
npm install -D lint-staged
```

在 `package.json` 中配置 `lint-staged`：

```json
{
  "lint-staged": {
    "*.{ts,vue}": ["eslint --fix"],
    "*.{css,scss}": ["prettier --write"]
  }
}
```

### Commitlint

安装提交信息格式检查：

```bash
npm install --save-dev @commitlint/{config-conventional,cli}
```

配置 `commitlint.config.js`：

```javascript
export default { extends: ['@commitlint/config-conventional'] }
```

在 `.husky/commit-msg` 中添加：

```bash
npx --no -- commitlint --edit ${1}
```

只有符合 `feat: add new feature` 格式的提交才能通过。

## 结语

工程化配置是一次性投入，长期受益。自动导入减少了重复 import，Monorepo 统一了多包管理，Git Hooks 守住了代码质量底线。下一篇将解锁 Vue 3 的**隐藏技能与黑科技**，包括 `defineModel`, JSX, 以及自定义指令的高阶用法。

# 16. 服务端动作 (Server Actions)：告别 useEffect

在 React 的历史上，表单提交和数据更新一直很痛苦。
需要：
1.  创建一个 API 路由 (`/api/update-user`)。
2.  在前端组件里写 `onSubmit`。
3.  阻止默认行为 `e.preventDefault()`。
4.  使用 `fetch('/api/...')` 发送请求。
5.  处理 loading 状态。
6.  处理 error 状态。
7.  手动刷新数据 `router.refresh()` 或更新本地 State。

React 团队问了一个问题：**“如果能像调用本地函数一样调用服务器函数，会怎么样？”**

这两就是 **Server Actions**。

## 心理模型：RPC (远程过程调用)

可以把 Server Action 想象成一个**“虫洞”函数**。虽然是在客户端组件里点击了按钮，但这个函数体 **100% 在服务器上运行**。

不需要手动写 `fetch`，React 编译器会自动把这个函数转换成一个 POST 请求。

### 例子：更新用户名

```javascript
// actions.ts (服务端代码)
'use server'; // 👈 标记为 Server Action

export async function updateUsername(formData) {
  const newName = formData.get('username');
  
  // 1. 直接操作数据库
  await db.user.update({ where: { id: 1 }, data: { name: newName } });
  
  // 2. 告诉 React：数据变了，请刷新缓存
  revalidatePath('/profile');
}
```

```javascript
// Profile.tsx (客户端组件)
import { updateUsername } from './actions';

export default function Profile() {
  return (
    // ✨ 像原生 HTML 一样直接传入函数！
    <form action={updateUsername}>
      <input name="username" />
      <button type="submit">Update</button>
    </form>
  );
}
```

## 为什么这很革命？

1.  **没有 useEffect**：不再需要写复杂的 Effect 来管理“提交后刷新数据”。Server Action 内置了 `revalidatePath`，并在 Action 完成后自动重新渲染页面。
2.  **渐进增强**：如果用户禁用了 JavaScript，上面的 `<form>` **依然能工作**！因为它就是一个标准的 HTML Form POST。
3.  **类型安全**：因为 `updateUsername` 就是一个普通导入的函数，TypeScript 可以自动推断参数和返回值类型。前后端类型完全打通。

## useFormStatus 与 useOptimistic

React 还提供了专门配合 Action 的 Hook：

*   `useFormStatus`：允许在不想把 State 传得到处都是的情况下，直接在子组件里读取当前 Form 是否正在提交（Pending 状态）。
*   `useOptimistic`：允许在服务器还没返回结果之前，先在界面上“假装”成功了（乐观更新），让体验极其丝滑。

## 总结

1.  **Server Actions 让全栈开发变得像写单体应用一样简单**。没有 API 路由，没有 fetch，只有函数调用。
2.  **它是基于 Web 标准的扩展**。利用 `<form action>` 的原生能力，实现了无 JS 也能运行的鲁棒性。
3.  **告别胶水代码**。大部分用于“同步服务器状态”的 `useEffect` 和 `useState` 都可以被删除了。

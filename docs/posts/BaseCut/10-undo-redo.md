# 撤销/重做系统：从命令模式到实战

> BaseCut 技术博客第十篇。这篇讲撤销/重做系统的设计与实现——让用户可以放心地"后悔"。

## 需求分析

撤销/重做和普通操作不同：

| 对比项 | 普通操作 | 可撤销操作 |
|--------|---------|-----------|
| 数据流 | 单向 | 双向（可逆） |
| 状态追踪 | 无 | 记录历史 |
| 用户心理 | 谨慎操作 | 放心尝试 |
| 实现复杂度 | 低 | 中高 |

撤销/重做需要支持：
- 所有编辑操作可逆（片段、特效、动画、项目设置）
- 连续操作合并（如拖拽位置不产生 100 条历史）
- 批量操作原子化（如分割片段 = 删除 1 + 添加 2）
- 快捷键 `Ctrl+Z` / `Ctrl+Shift+Z`

---

## 架构选择

### 方案对比

| 方案 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| **状态快照** | 每次操作保存完整状态 | 实现简单 | 内存消耗大，难合并 |
| **命令模式** ✅ | 只保存操作的增量 | 内存高效，易扩展 | 实现复杂度稍高 |

我们选择**命令模式**——这也是剪映、Premiere、After Effects 等专业工具的选择。

### 整体流程

```
用户操作 → Store 公共方法 → HistoryStore → HistoryManager → Command
     ↓           ↓               ↓              ↓            ↓
  点击按钮    addClip()      execute()      压栈/合并    execute()/undo()
```

---

## 核心模块设计

### 1. 命令接口

```typescript
// src/engine/HistoryTypes.ts
interface HistoryCommand {
  id: string                    // 唯一标识
  type: string                  // 命令类型（如 'ADD_CLIP'）
  description: string           // 描述（用于 UI 显示）
  timestamp: number             // 时间戳
  
  execute(): void               // 执行
  undo(): void                  // 撤销
  
  canMergeWith?(other): boolean // 可选：判断是否可合并
  mergeWith?(other): Command    // 可选：合并命令
}
```

### 2. 历史管理器

```typescript
// src/engine/HistoryManager.ts
class HistoryManager {
  private undoStack: HistoryCommand[] = []
  private redoStack: HistoryCommand[] = []
  private config = { maxStackSize: 100, mergeWindowMs: 500 }
  
  execute(command: HistoryCommand): void {
    // 尝试与栈顶命令合并
    const lastCmd = this.undoStack[this.undoStack.length - 1]
    const canMerge = this.shouldMerge(lastCmd, command)
    
    if (canMerge) {
      const merged = lastCmd.mergeWith!(command)
      this.undoStack[this.undoStack.length - 1] = merged
      merged.execute()
    } else {
      command.execute()
      this.undoStack.push(command)
    }
    
    // 新命令执行后清空重做栈
    this.redoStack = []
    
    // 限制栈深度
    if (this.undoStack.length > this.config.maxStackSize) {
      this.undoStack.shift()
    }
  }
  
  undo(): boolean {
    const cmd = this.undoStack.pop()
    if (!cmd) return false
    
    cmd.undo()
    this.redoStack.push(cmd)
    return true
  }
  
  redo(): boolean {
    const cmd = this.redoStack.pop()
    if (!cmd) return false
    
    cmd.execute()
    this.undoStack.push(cmd)
    return true
  }
}
```

### 3. 双栈结构图解

```
[执行 A] → undoStack: [A]       redoStack: []
[执行 B] → undoStack: [A, B]    redoStack: []
[撤销]   → undoStack: [A]       redoStack: [B]
[撤销]   → undoStack: []        redoStack: [B, A]
[重做]   → undoStack: [A]       redoStack: [B]
[执行 C] → undoStack: [A, C]    redoStack: []  ← 分支清空！
```

---

## 命令实现

### 片段命令

```typescript
// src/engine/commands/TimelineCommands.ts

// 添加片段
class AddClipCommand implements HistoryCommand {
  private createdClip: Clip | null = null
  
  constructor(
    private getStore: () => TimelineStore,
    private trackId: string,
    private clipData: Omit<Clip, 'id'>
  ) {}
  
  execute(): void {
    const store = this.getStore()
    if (this.createdClip) {
      // 重做：恢复完整数据
      store._addClipDirect(this.trackId, this.createdClip)
    } else {
      // 首次执行：保存创建结果
      const clip = store._addClipDirect(this.trackId, this.clipData)
      this.createdClip = { ...clip }
    }
  }
  
  undo(): void {
    if (this.createdClip) {
      this.getStore()._removeClipDirect(this.createdClip.id)
    }
  }
}

// 更新片段（支持合并）
class UpdateClipCommand implements HistoryCommand {
  private oldValues: Partial<Clip> | null = null
  
  constructor(
    private getStore: () => TimelineStore,
    private clipId: string,
    private updates: Partial<Clip>
  ) {}
  
  execute(): void {
    const store = this.getStore()
    const clip = store.getClipById(this.clipId)
    
    // 首次执行时保存旧值
    if (clip && !this.oldValues) {
      this.oldValues = {}
      for (const key of Object.keys(this.updates)) {
        this.oldValues[key] = clip[key]
      }
    }
    
    store._updateClipDirect(this.clipId, this.updates)
  }
  
  undo(): void {
    if (this.oldValues) {
      this.getStore()._updateClipDirect(this.clipId, this.oldValues)
    }
  }
  
  // 连续更新同一片段时合并
  canMergeWith(other: HistoryCommand): boolean {
    return other instanceof UpdateClipCommand && other.clipId === this.clipId
  }
  
  mergeWith(other: HistoryCommand): HistoryCommand {
    const otherCmd = other as UpdateClipCommand
    const merged = new UpdateClipCommand(
      this.getStore,
      this.clipId,
      { ...this.updates, ...otherCmd.updates }
    )
    merged.oldValues = this.oldValues  // 保留最初的旧值
    return merged
  }
}
```

### 分割片段命令（复杂操作）

```typescript
class SplitClipCommand implements HistoryCommand {
  private originalClip: Clip | null = null
  private splitClipIds: [string, string] | null = null
  
  constructor(
    private getStore: () => TimelineStore,
    private clipId: string,
    private splitTime: number
  ) {}
  
  execute(): void {
    const store = this.getStore()
    
    // 保存原始片段
    if (!this.originalClip) {
      const clip = store.getClipById(this.clipId)
      if (clip) this.originalClip = { ...clip }
    }
    
    // 执行分割
    const result = store._splitClipDirect(this.clipId, this.splitTime)
    if (result) {
      this.splitClipIds = [result[0].id, result[1].id]
    }
  }
  
  undo(): void {
    const store = this.getStore()
    
    // 删除分割后的两个片段
    if (this.splitClipIds) {
      store._removeClipDirect(this.splitClipIds[0])
      store._removeClipDirect(this.splitClipIds[1])
    }
    
    // 恢复原始片段
    if (this.originalClip) {
      store._addClipDirect(this.originalClip.trackId, this.originalClip)
    }
  }
}
```

---

## Store 集成

### 方法分离策略

每个 Store 分离**公共方法**和**直接方法**：

```typescript
// src/stores/timeline.ts
export const useTimelineStore = defineStore('timeline', () => {
  
  // 直接方法（供命令内部调用，不记录历史）
  function _addClipDirect(trackId: string, clip: ClipData): Clip {
    // 直接修改状态
    const newClip = { ...clip, id: crypto.randomUUID() }
    tracks.value.find(t => t.id === trackId)?.clips.push(newClip)
    return newClip
  }
  
  // 公共方法（用户调用，记录历史）
  function addClip(trackId: string, clip: ClipData): Clip {
    const command = new AddClipCommand(getThisStore, trackId, clip)
    useHistoryStore().execute(command)
    return /* 返回新创建的片段 */
  }
  
  return {
    addClip,           // 公开：用户调用
    _addClipDirect,    // 公开：命令调用
  }
})
```

### 已集成的 Store

| Store | 包装的方法 |
|-------|-----------|
| timeline.ts | addClip, removeClip, updateClip, moveClip, splitClip, addTrack, removeTrack |
| effects.ts | addEffect, removeEffect, updateEffect, toggleEffect, reorderEffects |
| animation.ts | addKeyframe, removeKeyframe, updateKeyframe |
| project.ts | setCanvasSize, setFrameRate, rename |

---

## Pinia History Store

```typescript
// src/stores/history.ts
export const useHistoryStore = defineStore('history', () => {
  const manager = new HistoryManager()
  
  // 响应式状态
  const canUndo = ref(false)
  const canRedo = ref(false)
  const undoDescription = ref('')
  const redoDescription = ref('')
  
  function execute(command: HistoryCommand) {
    manager.execute(command)
    syncState()
  }
  
  function undo() {
    if (manager.undo()) syncState()
  }
  
  function redo() {
    if (manager.redo()) syncState()
  }
  
  function syncState() {
    canUndo.value = manager.canUndo
    canRedo.value = manager.canRedo
    undoDescription.value = manager.undoDescription
    redoDescription.value = manager.redoDescription
  }
  
  return { canUndo, canRedo, undoDescription, redoDescription, execute, undo, redo }
})
```

---

## 快捷键集成

```typescript
// src/stores/history.ts
function initKeyboardShortcuts() {
  window.addEventListener('keydown', handleKeydown)
}

function handleKeydown(e: KeyboardEvent) {
  const isMac = navigator.platform.includes('Mac')
  const modKey = isMac ? e.metaKey : e.ctrlKey
  
  if (!modKey) return
  
  if (e.key === 'z' && !e.shiftKey) {
    e.preventDefault()
    undo()
  } else if ((e.key === 'z' && e.shiftKey) || e.key === 'y') {
    e.preventDefault()
    redo()
  }
}

// App.vue
onMounted(() => {
  historyStore.initKeyboardShortcuts()
})
```

---

## 命令合并策略

### 为什么需要合并？

拖拽片段位置时，每帧都可能触发 `updateClip`，如果不合并：

```
拖拽 1 秒 @ 60fps = 60 条历史记录 😱
```

### 合并窗口

```typescript
// 500ms 内的同类型命令可合并
private shouldMerge(lastCmd: HistoryCommand, newCmd: HistoryCommand): boolean {
  if (!lastCmd?.canMergeWith?.(newCmd)) return false
  
  const timeDelta = newCmd.timestamp - lastCmd.timestamp
  return timeDelta < this.config.mergeWindowMs
}
```

### 合并后的历史

```
拖拽开始 → 创建 UpdateClipCommand { oldX: 0 }
拖拽中   → 合并 { oldX: 0, newX: 50 }
拖拽中   → 合并 { oldX: 0, newX: 100 }
拖拽结束 → 最终只有 1 条记录 { oldX: 0, newX: 100 } ✅
```

---

## 性能优化

### 1. 惰性获取 Store

避免循环依赖，命令中通过函数获取 Store：

```typescript
class AddClipCommand {
  constructor(
    private getStore: () => TimelineStore,  // 惰性获取
    ...
  ) {}
  
  execute(): void {
    const store = this.getStore()  // 调用时才获取
    ...
  }
}
```

### 2. 栈深度限制

```typescript
execute(command: HistoryCommand): void {
  ...
  // 限制最大 100 步历史
  if (this.undoStack.length > 100) {
    this.undoStack.shift()  // 移除最旧的
  }
}
```

### 3. 深拷贝数据

```typescript
// ❌ 错误：引用会被后续修改
this.oldClip = clip

// ✅ 正确：必须深拷贝
this.oldClip = { 
  ...clip, 
  effects: clip.effects.map(e => ({ ...e }))
}
```

---

## 最终效果

| 功能 | 快捷键 |
|------|-------|
| 撤销 | `Ctrl+Z` / `Cmd+Z` |
| 重做 | `Ctrl+Shift+Z` / `Cmd+Shift+Z` / `Ctrl+Y` |

支持的操作类型：

- ✅ 片段操作（添加、删除、更新、移动、分割）
- ✅ 轨道操作（添加、删除、静音、锁定）
- ✅ 特效操作（添加、删除、更新、切换、排序）
- ✅ 动画操作（添加、删除、更新关键帧）
- ✅ 项目设置（画布尺寸、帧率、名称）

---

**系列目录**

- [x] 技术选型与项目结构
- [x] 时间轴数据模型
- [x] WebGL 渲染与滤镜
- [x] 转场动画实现
- [x] WebCodecs 视频导出
- [x] LeaferJS 贴纸系统
- [x] 视频特效系统
- [x] 关键帧动画系统
- [x] 性能优化专题
- [x] 撤销/重做系统（本文）

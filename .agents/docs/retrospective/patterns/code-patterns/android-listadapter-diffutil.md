---
id: "android-listadapter-diffutil"
source: "chaos/tests/AndroidStudioProjects/MyApplication"
maturity: "L1"
---

# Android ListAdapter + DiffUtil 高效列表刷新范式

## 模式概述

使用 `ListAdapter` 配合 `DiffUtil.ItemCallback` 管理 RecyclerView 数据，通过 `submitList()` 提交新列表。DiffUtil 在后台线程计算新旧列表差异，只对发生变化的 item 调用绑定，避免 `notifyDataSetChanged()` 的全量刷新，显著降低列表滚动卡顿与不必要的视图重建开销。

## 问题现象

使用传统 `RecyclerView.Adapter` + 手动 `notifyDataSetChanged()` 时，常见问题：

1. **全量刷新**：哪怕只有一条数据变化，也触发全部 item 重绑，屏幕闪烁、滚动跳动
2. **无动画**：增删改无平滑动画，体验生硬
3. **主线程卡顿**：列表较大时 notify 全量刷新引起掉帧
4. **无差异识别**：数据无唯一身份，无法判断「同一项内容变了」还是「换了新项」
5. **样板代码多**：手动维护 `getItemCount` / `getItemId` / 列表拷贝逻辑

## 解决方案

使用 `ListAdapter`，其内部持有 DiffUtil 与异步差异计算，只需实现 `DiffUtil.ItemCallback` 的两个回调，并在数据更新时调用 `submitList()`。

### 完整的 Adapter 实现

```kotlin
class TransformViewHolder(private val binding: ItemTransformBinding) :
    RecyclerView.ViewHolder(binding.root) {
    val textView: TextView = binding.textView
}

class TransformAdapter :
    ListAdapter<String, TransformViewHolder>(object : DiffUtil.ItemCallback<String>() {
        override fun areItemsTheSame(oldItem: String, newItem: String): Boolean =
            oldItem == newItem

        override fun areContentsTheSame(oldItem: String, newItem: String): Boolean =
            oldItem == newItem
    }) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TransformViewHolder {
        val binding = ItemTransformBinding.inflate(LayoutInflater.from(parent.context))
        return TransformViewHolder(binding)
    }

    override fun onBindViewHolder(holder: TransformViewHolder, position: Int) {
        holder.textView.text = getItem(position)
    }
}
```

> **说明**：当 item 本身是 String（或 `equals`/`hashCode` 已正确实现的数据类）时，`areItemsTheSame` 与 `areContentsTheSame` 可以都写 `oldItem == newItem`。当数据是对象时，`areItemsTheSame` 应基于唯一 id（如 `old.id == new.id`），`areContentsTheSame` 才比较内容字段，从而让「同一项内容变化」能被正确识别并触发局部更新。

## 使用方式

在 Fragment / Activity 中装配，并通过数据流驱动 `submitList`：

```kotlin
// 装配
val adapter = TransformAdapter()
binding.recyclerView.adapter = adapter

// 数据驱动刷新：ViewModel 暴露 LiveData/StateFlow，
// 每次数据变化 submitList 即触发差异计算
viewModel.texts.observe(viewLifecycleOwner) { list ->
    adapter.submitList(list)
}
```

```kotlin
// ViewModel 侧：直接替换列表引用即可
class TransformViewModel : ViewModel() {
    private val _texts = MutableLiveData<List<String>>()
    val texts: LiveData<List<String>> = _texts

    fun update(seed: Int) {
        _texts.value = generateItems(seed)  // 生成新列表实例
    }
}
```

## 模式优势

| 优势 | 说明 |
|------|------|
| **最小刷新** | DiffUtil 只重绑变化的 item，减少开销 |
| **内建动画** | 增删改自动附带位移/淡入淡出动画 |
| **后台计算** | 差异在后台线程计算，主线程仅应用 dispatch 结果 |
| **状态保留** | 无关 item 不重建，滚动位置与已加载图片等不被破坏 |
| **职责单一** | 无需手动维护 itemCount / id / 列表副本 |

## 变体与扩展

### 变体 A：AsyncListDiffer（复用已有 Adapter）

若不希望继承 ListAdapter，可在自定义 Adapter 内持有 `AsyncListDiffer`，效果一致：

```kotlin
class MyAdapter : RecyclerView.Adapter<MyViewHolder>() {
    private val differ = AsyncListDiffer(this, object : DiffUtil.ItemCallback<String>() { ... })
    fun submitList(list: List<String>) = differ.submitList(list)
    override fun getItemCount() = differ.currentList.size
    override fun getItem(position: Int) = differ.currentList[position]
}
```

### 变体 B：对象数据 + 唯一 id

数据为对象时，按 id 判同、按内容判变：

```kotlin
class Item(val id: Long, val title: String, val count: Int)

ListAdapter<Item, VH>(object : DiffUtil.ItemCallback<Item>() {
    override fun areItemsTheSame(a: Item, b: Item) = a.id == b.id
    override fun areContentsTheSame(a: Item, b: Item) = a == b
})
```

### 变体 C：结合 Paging / Flow

在分页场景用 `PagingDataAdapter` 或在协程中把 `Flow` 结果 `submitList`，享受同样的差异刷新能力。

## 触发场景

**适用于**：

- 数据频繁增删改的列表（聊天、动态、订阅流）
- 列表项数量较大、全量刷新代价高的场景
- 需要平滑增删动画的界面
- 数据来源为响应式流（LiveData / Flow / StateFlow）的应用

**不适用于**：

- 列表极小（个位数 item）且更新极低频，DiffUtil 收益可忽略时
- 每次都是完全替换且无局部变化、且不需要动画的场景
- item 无法提供稳定身份标识的场景（此时 diff 无意义）

## 反模式

```kotlin
// ❌ 反模式 1：沿用 notifyDataSetChanged 全量刷新
class OldAdapter : RecyclerView.Adapter<OldViewHolder>() {
    var items: List<String> = emptyList()
        set(value) {
            field = value
            notifyDataSetChanged()   // 全部重绑：闪烁、无动画、掉帧
        }
}
```

```kotlin
// ❌ 反模式 2：areItemsTheSame 用内容而非 id，导致整列误判为「新项」
class BadAdapter :
    ListAdapter<Item, VH>(object : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(a: Item, b: Item) = a == b   // 内容一变就当新项，全量重建
        override fun areContentsTheSame(a: Item, b: Item) = false // 恒为 false，无局部优化
    })
```

```kotlin
// ❌ 反模式 3：submitList 传入同一个可变 List 实例，diff 永远检测不到变化
val sharedList = mutableListOf("a", "b", "c")
adapter.submitList(sharedList)
sharedList.add("d")          // 仍在原对象上改，submitList 再次收到相同引用
adapter.submitList(sharedList) // DiffUtil 认为无变化，界面不更新
```

```kotlin
// ❌ 反模式 4：在 onBindViewHolder 中访问可变集合，而非通过 getItem 读取
```

## 检验标准

1. 单条数据变化时，仅该 item 的 `onBindViewHolder` 被调用（可打点验证），而非全部
2. 增删 item 出现平滑动画，无整列表闪烁
3. 列表较大时滚动流畅，无因刷新导致的掉帧
4. `areItemsTheSame` 按稳定 id 判同；`areContentsTheSame` 正确区分内容变化
5. 每次数据更新都通过 `submitList` 提交新的列表实例，不原地修改传入列表

## 跨领域迁移示例

该模式本质是「**最小差异更新（diff-based reconciliation）**」，可迁移到：

- **Jetpack Compose**：`LazyColumn` + `LazyListState` 天然按 key 复用，配合 immutable 数据列表达到同样的最小重组效果
- **React / Vue**：Virtual DOM 的 key-based reconciliation 与 `areItemsTheSame` 思路一致——用稳定 key 判定「同项」、按内容做局部 patch
- **iOS（UITableView / UICollectionView）**：`performBatchUpdates` + `diff` 或 Combine 差异更新，避免 `reloadData` 全量刷新

## 版本与成熟度

- **maturity**: `L1`（实验性，单案例）
- **来源案例**：`chaos/tests/AndroidStudioProjects/MyApplication` 中 `TransformFragment.kt` 的 `TransformAdapter`
- **验证范围**：仅覆盖 String 类型 item 的单一案例，`areItemsTheSame` 基于内容相等；对象模型 + 唯一 id 的变体尚未在源项目落地
- **风险提示**：`submitList` 必须传入新实例；大数据量差异计算虽在后台线程，但过大的首次 diff 仍可能造成短暂卡顿，超大列表建议结合 Paging

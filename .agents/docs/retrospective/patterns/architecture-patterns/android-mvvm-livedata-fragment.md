---
id: "android-mvvm-livedata-fragment"
source: "chaos/tests/AndroidStudioProjects/MyApplication"
maturity: "L1"
---

> **来源**：从 chaos/tests/AndroidStudioProjects/MyApplication 项目的 ViewModel/LiveData/Fragment 实现中提炼（2026 年复盘）。

# Android MVVM + LiveData 标准分层

## 模式概述

采用 **MVVM + LiveData 标准分层**：`ViewModel` 持有 `LiveData` 数据，`Fragment` 通过 `ViewModelProvider` 获取 `ViewModel`，并用 `observe(viewLifecycleOwner)` 订阅数据驱动 UI，实现视图与数据解耦。数据变更由 LiveData 自动通知观察者，Fragment 无需手动管理数据源，ViewModel 与生命周期绑定、配置变更后数据不丢失。

核心分层：

- **View（Fragment）**：只负责渲染与事件转发，不直接管理数据源。
- **ViewModel**：持有并暴露 `LiveData`，管理业务状态，不持有 View/Context。
- **LiveData**：生命周期感知的可观察数据容器，驱动 UI 自动刷新。

## 问题现象

不使用 MVVM + LiveData 时，常见问题：

1. **Fragment 直接管理数据源**：网络/数据库调用、状态维护全写在 Fragment 里，代码膨胀、难复用、难测试。
2. **配置变更丢状态**：旋转屏幕、切后台重建时，Activity/Fragment 销毁重建，数据重新加载。
3. **内存泄漏**：观察者未绑定生命周期，或持有 View 引用，导致 Fragment 销毁后仍被持有。
4. **线程切换混乱**：后台线程更新 UI，手动 `runOnUiThread` 到处穿插。
5. **视图与数据强耦合**：改数据模型需同步改 UI 逻辑，分层不清。

## 解决方案

采用 ViewModel 持有 LiveData、Fragment 观察驱动 UI 的 MVVM 分层。

### ViewModel（持有 LiveData）

ViewModel 暴露不可变的 `LiveData` 对外，内部用 `MutableLiveData` 维护可变状态。ViewModel 不持有 View、Context、Activity：

```kotlin
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class TransformViewModel : ViewModel() {

    // 私有可变 LiveData，对外只暴露不可变 LiveData
    private val _texts = MutableLiveData<List<String>>().apply {
        value = (1..16).mapIndexed { _, i ->
            "This is item # $i"
        }
    }

    val texts: LiveData<List<String>> = _texts
}
```

要点：

- 用 `_texts`（私有 Mutable）+ `texts`（公开只读 LiveData）的惯例，外部无法篡改数据源。
- ViewModel 由 `ViewModelStore` 管理，配置变更（旋转/重建）后同一 ViewModel 实例被复用，数据不丢失。
- ViewModel 生命周期长于对应 View，因此绝不能在其中持有 View/Context/Activity 引用。

### Fragment（观察驱动 UI）

Fragment 通过 `ViewModelProvider(this)` 获取 ViewModel，用 `observe(viewLifecycleOwner)` 订阅 LiveData 更新 RecyclerView：

```kotlin
class TransformFragment : Fragment() {

    private var _binding: FragmentTransformBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // 通过 ViewModelProvider 获取 ViewModel（生命周期绑定，配置变更复用）
        val transformViewModel = ViewModelProvider(this).get(TransformViewModel::class.java)
        _binding = FragmentTransformBinding.inflate(inflater, container, false)
        val root: View = binding.root

        val recyclerView = binding.recyclerviewTransform
        val adapter = TransformAdapter()
        recyclerView.adapter = adapter

        // 用 viewLifecycleOwner 观察，确保在 Fragment 视图销毁时自动取消订阅
        transformViewModel.texts.observe(viewLifecycleOwner) {
            adapter.submitList(it)
        }
        return root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null   // 清空 binding，防止视图销毁后仍持有 View
    }
}
```

要点：

- **必须用 `viewLifecycleOwner` 而非 `this`** 观察：Fragment 的视图在 `onDestroyView` 后销毁，但 Fragment 实例可能存活；用 `viewLifecycleOwner` 保证视图销毁时自动解绑，避免泄漏。
- `_binding` 在 `onDestroyView` 置空，避免 View Binding 持有已销毁视图。
- Fragment 不管理数据源，只把 `submitList(it)` 交给适配器，UI 完全由数据驱动。

## 分层结构说明

| 层 | 职责 | 生命周期 | 关键约束 |
|----|------|---------|---------|
| **Fragment（View）** | 渲染、收集事件、观察 LiveData 刷新 UI | 跟随 Fragment 生命周期 | 不直接访问网络/数据库；不持有全局数据 |
| **ViewModel** | 持有 LiveData、维护业务状态、响应 UI 事件 | 跟随 ViewModelStore（配置变更存活） | 不持有 View/Context/Activity；不含 Android framework 依赖（便于测试） |
| **LiveData** | 生命周期感知的可观察数据容器 | 由 ViewModel 持有 | 主线程派发；`postValue` 用于跨线程 |

数据流：`ViewModel 持有 LiveData` → `Fragment.observe(viewLifecycleOwner)` → 数据变更自动回调 → `adapter.submitList / UI 更新`。UI 事件（如点击）→ Fragment 调用 ViewModel 方法 → ViewModel 更新 LiveData → 反向驱动 UI，形成单向数据流。

## 使用方式

1. **定义 ViewModel**：继承 `ViewModel`，内部用 `MutableLiveData` 维护状态，对外暴露只读 `LiveData`。
2. **获取 ViewModel**：Fragment 中 `ViewModelProvider(this).get(MyViewModel::class.java)`（也可用 `by viewModels()` 委托）。
3. **订阅数据**：`viewModel.xxx.observe(viewLifecycleOwner) { ... }`，在回调中更新 UI。
4. **发起请求**：Fragment 事件（按钮点击等）→ 调用 ViewModel 方法 → ViewModel 更新 LiveData → UI 自动刷新。
5. **释放引用**：Fragment `onDestroyView` 清空 view binding；ViewModel 通过 `onCleared()` 释放资源。

## 适用场景

### 适用于

- ✅ 页面状态需要跨配置变更（旋转/重建）保持的常规页面
- ✅ 数据驱动 UI 的列表页 / 详情页（LiveData + RecyclerView/ListAdapter）
- ✅ 需要 UI 与业务逻辑解耦、便于单元测试的项目
- ✅ 与 Navigation / ViewBinding / RecyclerView 等 Jetpack 组件协同的现代架构

### 不适用于

- ❌ 超简单一次性页面（仅展示静态内容，引入 ViewModel 反而增加样板代码）
- ❌ 对数据量/流式场景要求极高的场景（应改用 Flow/StateFlow 与协程，而非 LiveData）
- ❌ 需要纯 Kotlin 跨平台共享逻辑的模块（应使用不依赖 Android 的层，如 Domain/Data 层）
- ❌ 依赖复杂事件流组合（RxJava / Flow 的 flatMap、debounce 等）的交互密集型页面

## 反模式

| 反模式 | 表现 | 后果 |
|--------|------|------|
| **在 ViewModel 持有 Context / View / Activity** | ViewModel 里保存 `activity`、`fragment`、`view` 引用用于更新 UI | 配置变更后 Activity/Fragment 被回收，ViewModel 却仍持有其强引用，导致内存泄漏（内存溢出） |
| **在 Fragment 直接管理数据源** | Fragment 里直接发起网络请求、读写数据库、维护状态 | 代码膨胀、UI 与业务强耦合、无法复用与测试、配置变更需重新加载 |
| **用 setValue 而非 postValue 跨线程更新** | 在后台线程调用 `mutableLiveData.setValue(...)` | 抛 `IllegalStateException: Cannot invoke setValue on a background thread`；跨线程必须用 `postValue` |
| **observe 未绑定 lifecycle** | 用 `observe(owner)` 时传 `this`（Fragment 而非 viewLifecycleOwner），或用 `observeForever` 后不手动移除 | 视图销毁后观察者仍活跃，收到回调操作已销毁的 View，导致泄漏或崩溃 |
| **ViewModel 里塞网络/数据库 IO 与大量业务** | ViewModel 直接调网络、写库、含复杂业务逻辑，未拆出 Data/Repository 层 | 职责混杂、难以测试、ViewModel 体积过大、配置变更时 IO 重复执行 |

## 检验标准

- [ ] 所有 ViewModel 继承 `ViewModel`，对外暴露只读 `LiveData`，内部用 `MutableLiveData` 维护状态
- [ ] ViewModel 中无 `Activity`/`Fragment`/`View`/`Context` 字段与引用（可通过 lint `ViewModelInjection` / 代码审查确认）
- [ ] Fragment 通过 `ViewModelProvider` / `by viewModels()` 获取 ViewModel，不在 Fragment 中直接管理网络/数据库
- [ ] 所有 `observe` 均绑定 `viewLifecycleOwner`（而非 `this`），无 `observeForever` 遗留
- [ ] 所有 UI 更新均由 LiveData 回调驱动，无 Fragment 中手工线程切换 `runOnUiThread` 散落
- [ ] 跨线程更新 LiveData 全部使用 `postValue`，主线程使用 `setValue`
- [ ] Fragment 的 view binding 在 `onDestroyView` 中置空，无视图引用泄漏

## 迁移示例

**迁移前（Fragment 直接管理数据源）**：

```kotlin
// 旧写法：Fragment 里直接初始化数据、管理状态，配置变更后数据丢失
class TransformFragment : Fragment() {
    private var texts: List<String> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        texts = (1..16).mapIndexed { _, i -> "This is item # $i" }  // 数据在 Fragment 内，旋转即丢
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // 手动把数据塞给 adapter，状态一变就漏同步
        binding.recyclerView.adapter = TransformAdapter(texts)
    }
}
```

**迁移后（MVVM + LiveData）**：

```kotlin
// ViewModel：持有数据，配置变更存活
class TransformViewModel : ViewModel() {
    private val _texts = MutableLiveData<List<String>>().apply {
        value = (1..16).mapIndexed { _, i -> "This is item # $i" }
    }
    val texts: LiveData<List<String>> = _texts
}
```

```kotlin
// Fragment：只观察，不管理数据源
class TransformFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val viewModel = ViewModelProvider(this).get(TransformViewModel::class.java)
        val adapter = TransformAdapter()
        binding.recyclerView.adapter = adapter
        viewModel.texts.observe(viewLifecycleOwner) { adapter.submitList(it) }
    }
}
```

迁移要点：把 Fragment 中的数据源与状态上移到 ViewModel（改为 Mutable/LiveData），Fragment 改为通过 `ViewModelProvider` 获取并用 `observe(viewLifecycleOwner)` 订阅刷新，删除 Fragment 内手工管理数据与线程切换的代码。

## 版本与成熟度

- **成熟度**：L1（单项目验证）。源自 `chaos/tests/AndroidStudioProjects/MyApplication` 单一示例工程，分层结构可复用但尚未跨多项目验证推广。
- **适用版本**：AndroidX 架构组件（`androidx.lifecycle:lifecycle-livedata-ktx` / `lifecycle-viewmodel-ktx`）。若项目已采用 Kotlin 协程，可考虑以 `StateFlow` 替代 `LiveData` 以获得更统一的响应式栈。

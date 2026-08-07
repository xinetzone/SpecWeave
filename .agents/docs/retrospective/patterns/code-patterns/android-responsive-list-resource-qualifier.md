---
id: "android-responsive-list-resource-qualifier"
source: "chaos/tests/AndroidStudioProjects/MyApplication"
maturity: "L1"
---

# Android 资源限定符驱动的响应式列表切换模式

## 模式概述

同一份 RecyclerView 列表，在不同屏幕尺寸下自动切换布局形态——小屏使用 LinearLayoutManager（单列列表），大屏使用 GridLayoutManager（多列网格）。切换完全由 Android 资源限定符（resource qualifier，如 `layout-w600dp`）驱动，业务代码无需任何屏幕判断，做到「一个 Activity/Fragment、多套布局资源、零代码分支」。

## 问题现象

需要让一个列表同时适配手机与平板/大屏时，常见的笨拙做法：

1. **代码里写屏幕判断**：`resources.configuration.screenWidthDp > 600` 后手动 `setLayoutManager`，逻辑散落在 Activity/Fragment，难以维护与测试
2. **只做一套布局**：大屏下一行撑满、元素被拉伸，视觉密度差，空间利用率低
3. **用尺寸资源但仅改 margin**：仅调整间距与字号，无法改变列表的「骨架形态」（单列 vs 多列）
4. **复制粘贴整套页面**：为平板单独建 Activity/Fragment，代码重复、后续改动需同步两处

## 解决方案

利用 Android 资源系统「按配置选择资源目录」的能力：默认目录提供小屏布局，`layout-w600dp`（宽度 ≥ 600dp 的屏幕）提供大屏布局。两份布局内容相同，仅 RecyclerView 的 `layoutManager` 属性不同，其余靠资源系统自动匹配。

### 默认布局 `res/layout/fragment_transform.xml`（手机 / 窄屏）

```xml
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:layoutManager="LinearLayoutManager"
        app:reverseLayout="false"
        app:stackFromEnd="false" />

</FrameLayout>
```

### 大屏布局 `res/layout-w600dp/fragment_transform.xml`（平板 / 宽屏）

```xml
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:layoutManager="GridLayoutManager"
        app:spanCount="4" />

</FrameLayout>
```

> **要点**：两份布局的 View id 必须完全一致（此处均为 `@+id/recyclerView`），这样 Fragment 中的 `binding.recyclerView` 绑定代码无需任何改动。`app:layoutManager` 与 `app:spanCount` 会在 inflate 时被 RecyclerView 自动解析，等价于代码 `rv.layoutManager = LinearLayoutManager(context)` / `GridLayoutManager(context, 4)`。

### Fragment 侧代码（完全无屏幕判断）

```kotlin
class TransformFragment : Fragment() {
    // RecyclerView 的 layoutManager 由资源限定符自动决定，
    // 这里只需要设置 adapter，其余交给系统。
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.recyclerView.adapter = TransformAdapter()
    }
}
```

## 使用方式

1. 先写好默认布局（单列 LinearLayoutManager）并验证小屏表现
2. 复制为 `layout-w600dp/` 目录下的同名布局，改为 GridLayoutManager + 合适的 `spanCount`
3. 确保两份布局的 view id 一致，Fragment 绑定代码零改动
4. 在真实设备 / Android Studio 的 Device Preview 中分别用手机与平板配置预览验证
5. 如需更细粒度，可叠加 `-sw600dp`（最短边限定）、`-land`（横屏）等限定符组合出更多档位

## 模式优势

| 优势 | 说明 |
|------|------|
| **零代码分支** | 屏幕判断完全下沉到资源系统，业务代码干净 |
| **单一数据源** | 一套 Fragment / Adapter / ViewModel，仅布局资源多份 |
| **低耦合** | 改布局形态不动逻辑，改逻辑不动布局 |
| **天然可预览** | AS 布局编辑器直接按限定符切换预览 |
| **复用系统机制** | 无需引入额外库，纯 Android 原生能力 |

## 变体与扩展

### 变体 A：多档位组合

不只两档，用多个限定符目录划分更多断点（如 `layout` / `layout-w600dp` / `layout-w840dp`），每档 spanCount 递增。

### 变体 B：仅调整 spanCount（不改布局文件）

若只希望动态改列数而无需不同布局，可在代码里按宽度设置 `GridLayoutManager` 的 spanCount，但这就回到了代码判断，仅在列数高度依赖业务数据时采用。

### 变体 C：配合 `-land` / `-sw` 限定符

横竖屏分别提供不同形态（如横屏网格、竖屏列表），仍是无代码判断。

## 触发场景

**适用于**：

- 手机 + 平板双端复用的列表页
- 折叠屏/大屏 Android 设备适配
- 信息密度要求随可用宽度变化的展示型列表（图库、商品、卡片流）
- 需要响应式但希望把「形态决策」交给资源系统的场景

**不适用于**：

- 列数必须由运行时数据动态决定的场景（如按返回值确定网格列数）
- 布局差异巨大、远超「同结构不同形态」的页面（此时应拆独立 Fragment 或模块）
- 仅依赖横竖屏而跟宽度无关的简单差异（可直接用 `layout-land` 更直观）

## 反模式

```xml
<!-- ❌ 反模式 1：在代码里写屏幕判断替代资源限定符 -->
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android">
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</FrameLayout>
```

```kotlin
// ❌ 反模式 1（续）：业务代码里塞入屏幕分支，违背本模式初衷
val isWide = resources.configuration.screenWidthDp >= 600
binding.recyclerView.layoutManager = if (isWide) {
    GridLayoutManager(requireContext(), 4)
} else {
    LinearLayoutManager(requireContext())
}
```

```xml
<!-- ❌ 反模式 2：两份布局 view id 不一致，导致 Fragment 绑定失效/空指针 -->
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/recyclerViewWide"   <!-- 大屏用了不同 id -->
    ... />
```

```xml
<!-- ❌ 反模式 3：只改大屏资源，却忘了小屏基线，窄屏回归为无定义 layoutManager -->
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/recyclerView"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    <!-- 默认布局没有 app:layoutManager，运行时报错 -->
    />
```

## 检验标准

1. 手机配置（窄屏）下列表为单列；平板/宽屏（≥600dp）配置下为多列网格
2. 两种配置下 Fragment 均正常渲染，无 `IllegalStateException: RecyclerView has no LayoutManager` 报错
3. 两份布局 view id 完全一致，Fragment/Adapter 代码在两种配置间零改动
4. 旋转/折叠屏切换后布局形态自动跟随，无需重建逻辑手动干预
5. 在 AS Layout Preview 中切换 device 即可预览两套形态，无需运行设备

## 跨领域迁移示例

该模式本质是「**按运行环境选择资源/配置，业务逻辑与形态决策解耦**」，可迁移到：

- **Web 前端（CSS Media Query）**：同一组件用 `@media (min-width: 600px)` 从单列切换为多列 Grid，组件 JS 无需判断视口宽度，与 Android 资源限定符完全同构
- **Flutter（LayoutBuilder + MediaQuery）**：用 `LayoutBuilder` 按 `constraints.maxWidth` 选择 `ListView` 或 `GridView`，把决策收敛到一处
- **后端响应式渲染**：服务端按客户端设备宽度返回不同布局模板，客户端零分支

## 版本与成熟度

- **maturity**: `L1`（实验性，单案例）
- **来源案例**：`chaos/tests/AndroidStudioProjects/MyApplication` 中 TransformFragment 的两套 `fragment_transform.xml` 资源
- **验证范围**：仅覆盖单项目内两档宽度切换的单一案例，spanCount 取值、多断点组合、真机平板表现尚未在多个生产项目验证
- **风险提示**：资源限定符在 inflate 时确定，若后续需求要求运行时动态改列数，需回退到代码判断或改用 `GridLayoutManager` 的 spanCount 动态更新

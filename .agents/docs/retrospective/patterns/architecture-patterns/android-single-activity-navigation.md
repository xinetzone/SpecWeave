---
id: "android-single-activity-navigation"
source: "chaos/tests/AndroidStudioProjects/MyApplication"
maturity: "L1"
---

> **来源**：从 chaos/tests/AndroidStudioProjects/MyApplication 项目的 Activity/Fragment/Navigation 实现中提炼（2026 年复盘）。

# Android 单一 Activity + Navigation 组件多页面架构

## 模式概述

在 Android 应用中，将所有页面组织为 **单一 Activity 承载 + 多 Fragment 页面 + Navigation 组件（Navigation Graph）驱动导航** 的架构。所有页面以 `Fragment` 承载，导航关系统一由 `res/navigation/` 下的 Navigation Graph（XML）定义，`Activity` 仅负责承载 `NavHostFragment` 并挂载导航控制器，不直接管理页面切换逻辑。

该模式把"页面是什么"（Fragment）与"页面如何切换"（NavGraph）解耦，使导航关系可视化、可审计、可配置，且天然适配 Jetpack 生态（返回栈、DeepLink、Safe Args）。

## 问题现象

采用传统多 Activity 或 Activity 内手写 Fragment 事务的组织方式时，常见问题：

1. **页面切换逻辑散落**：`FragmentManager` 事务（`add`/`replace`/`addToBackStack`）散落在各 Activity/Fragment 中，导航关系不可见，难以审计。
2. **返回行为混乱**：手写返回栈时容易漏掉 `addToBackStack`，导致系统返回键行为不符合预期。
3. **目标页标识无统一约束**：用字符串 tag 或常量表示 Fragment，易拼写错误、难做编译期检查。
4. **顶部栏/抽屉/底部导航集成困难**：多页面切换时菜单高亮、标题联动、返回箭头需在每处重复实现。
5. **生命周期与页面解耦差**：页面与 Activity 强耦合，重组、DeepLink、单页模式切换困难。

## 解决方案

采用「单一 Activity + Navigation 组件」架构，三要素：

1. **Navigation Graph（XML）**：集中声明所有目的地（destination）与导航关系。
2. **NavHostFragment 容器**：唯一承载页面的 `FragmentContainerView`。
3. **MainActivity**：只负责获取 `NavController`，并用 `AppBarConfiguration` + `setupActionBarWithNavController` 集成顶部栏/抽屉/底部导航的返回导航。

### 导航图 XML

`res/navigation/mobile_navigation.xml` 定义多个 `<fragment>` 目的地，`app:startDestination` 指定起始页，每个 `fragment` 通过 `android:name` 绑定具体 Fragment 类：

```xml
<?xml version="1.0" encoding="utf-8"?>
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/mobile_navigation"
    app:startDestination="@+id/nav_transform">

    <fragment
        android:id="@+id/nav_transform"
        android:name="com.example.myapplication.ui.transform.TransformFragment"
        android:label="@string/menu_transform"
        tools:layout="@layout/fragment_transform" />

    <fragment
        android:id="@+id/nav_reflow"
        android:name="com.example.myapplication.ui.reflow.ReflowFragment"
        android:label="@string/menu_reflow"
        tools:layout="@layout/fragment_reflow" />

    <fragment
        android:id="@+id/nav_slideshow"
        android:name="com.example.myapplication.ui.slideshow.SlideshowFragment"
        android:label="@string/menu_slideshow"
        tools:layout="@layout/fragment_slideshow" />

    <fragment
        android:id="@+id/nav_settings"
        android:name="com.example.myapplication.ui.settings.SettingsFragment"
        android:label="@string/menu_settings"
        tools:layout="@layout/fragment_settings" />
</navigation>
```

### 承载容器（content_main.xml）

`FragmentContainerView` 承载 `NavHostFragment`，通过 `app:navGraph` 挂载导航图，`app:defaultNavHost="true"` 让系统返回键自动并入 NavController 返回栈：

```xml
<androidx.fragment.app.FragmentContainerView
    android:id="@+id/nav_host_fragment_content_main"
    android:name="androidx.navigation.fragment.NavHostFragment"
    android:layout_width="match_parent"
    android:layout_height="0dp"
    app:defaultNavHost="true"
    app:navGraph="@navigation/mobile_navigation" />
```

### MainActivity 关键代码

`MainActivity` 通过 `NavHostFragment.navController` 获取控制器，用 `AppBarConfiguration` + `setupActionBarWithNavController` 集成顶部栏返回导航，并用 `setupWithNavController` 联动抽屉/底部导航：

```kotlin
class MainActivity : AppCompatActivity() {

    private lateinit var appBarConfiguration: AppBarConfiguration

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        setSupportActionBar(findViewById(R.id.toolbar))

        val navHostFragment =
            (supportFragmentManager.findFragmentById(R.id.nav_host_fragment_content_main)
                    as NavHostFragment?)!!
        val navController = navHostFragment.navController

        // 顶部目的地集合（这些页面不显示返回箭头，属于根级目的地）
        appBarConfiguration = AppBarConfiguration(
            setOf(R.id.nav_transform, R.id.nav_reflow, R.id.nav_slideshow, R.id.nav_settings),
            findViewById(R.id.drawer_layout)
        )
        setupActionBarWithNavController(navController, appBarConfiguration)

        // 抽屉或底部导航与 NavController 联动
        findViewById<NavigationView>(R.id.nav_view)?.setupWithNavController(navController)
    }

    override fun onSupportNavigateUp(): Boolean {
        val navController = findNavController(R.id.nav_host_fragment_content_main)
        return navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
    }
}
```

## 目录组织结构

```
app/src/main/
├── java/com/example/myapplication/
│   ├── MainActivity.kt              # 唯一 Activity，仅承载 NavHostFragment 与导航控制器
│   └── ui/                          # 按页面(Feature)分包
│       ├── transform/TransformFragment.kt
│       ├── reflow/ReflowFragment.kt
│       ├── slideshow/SlideshowFragment.kt
│       └── settings/SettingsFragment.kt
└── res/
    ├── navigation/mobile_navigation.xml   # 导航图：统一声明所有目的地与导航关系
    ├── layout/
    │   ├── activity_main.xml              # 外壳（Toolbar/抽屉/底部导航 + NavHostFragment）
    │   ├── content_main.xml               # FragmentContainerView 承载 NavHostFragment
    │   └── fragment_*.xml                 # 各页面布局
    └── menu/
        ├── navigation_drawer.xml          # 抽屉菜单（id 与导航图目的地 id 保持一致）
        └── bottom_navigation.xml          # 底部导航菜单
```

组织结构要点：

- **按 Feature（页面功能）分包**：`ui/<feature>/` 下放对应 Fragment，职责内聚，与导航图目的地一一对应。
- **导航关系集中声明**：所有目的地集中在 `res/navigation/` 单文件，而非散落在代码里。
- **菜单 id 与目的地 id 对齐**：`navigation_drawer.xml` / `bottom_navigation.xml` 中菜单项的 `id` 必须与导航图 fragment 的 `android:id` 一致，才能被 `setupWithNavController` 正确联动。

## 使用方式

1. **创建导航图**：在 `res/navigation/` 新建 XML，声明 `app:startDestination` 与若干 `<fragment>` 目的地，`android:name` 指向具体 Fragment 类。
2. **挂载 NavHostFragment**：在外壳布局中放 `FragmentContainerView`（`android:name="androidx.navigation.fragment.NavHostFragment"`），`app:navGraph` 指向导航图，`app:defaultNavHost="true"`。
3. **Activity 集成**：在 `MainActivity` 中通过 `supportFragmentManager.findFragmentById(R.id.nav_host...)` 拿到 `NavHostFragment`，再取 `.navController`。
4. **顶部栏返回集成**：构造 `AppBarConfiguration(topLevelDestinations, drawerLayout)`，调用 `setupActionBarWithNavController`。
5. **菜单联动**：抽屉/底部导航 `setupWithNavController(navController)`，菜单项 id 与导航图目的地 id 一致。
6. **页面跳转**：Fragment 内通过 `findNavController().navigate(R.id.xxx)` 跳转，或使用 Safe Args 传递参数。

## 适用场景

### 适用于

- ✅ 中大型 App 需要清晰、可维护的导航关系
- ✅ 依赖抽屉导航 / 底部导航 / 顶部栏的页面组织
- ✅ 需要返回栈、DeepLink、统一返回行为的应用
- ✅ 希望页面与 Activity 解耦、便于单页重构的架构

### 不适用于

- ❌ 页面间完全独立、无共享外壳的超轻量工具型 App（单 Activity 直接布局即可）
- ❌ 需要多个独立任务栈 / 多窗口的复杂桌面级场景（可能需多 Activity）
- ❌ 已有大量历史 Activity 且无重构预算的存量项目（渐进迁移而非一次性推翻）

## 反模式

| 反模式 | 表现 | 后果 |
|--------|------|------|
| **滥用 Fragment 嵌套（Fragment 里套 Fragment）** | 在 Fragment 的布局中再放一个 `FragmentContainerView` 手工管理子 Fragment 事务 | 生命周期、返回栈、事件分发异常复杂，状态丢失难排查，导航图无法表达嵌套关系 |
| **startDestination 缺失或错误** | 导航图未声明 `app:startDestination`，或指向了一个并不存在的目的地 id | 启动即抛 `IllegalArgumentException`（找不到 start destination），或跳转到错误初始页 |
| **导航图 id 与菜单 id 不一致** | 抽屉/底部导航菜单项 id 与导航图 fragment 的 `android:id` 不匹配 | `setupWithNavController` 无法联动，菜单点击无响应或高亮错乱，返回行为异常 |
| **在 Activity 里手写 Fragment 事务绕过 NavGraph** | 用 `supportFragmentManager` + `replace()` 直接切页，导航图形同虚设 | 双轨导航，返回栈与导航图状态不一致，DeepLink/状态恢复失效 |
| **忘记 defaultNavHost="true"** | `FragmentContainerView` 未设置 `app:defaultNavHost="true"` | 系统返回键不交给 NavController，返回行为退回 Activity 默认，破坏返回栈 |

## 检验标准

- [ ] 项目中页面切换全部通过 `NavController.navigate(...)` 完成，无手写 `FragmentManager` 事务切换页面
- [ ] `res/navigation/` 下导航图声明了有效 `app:startDestination`，且所有 `<fragment>` 的 `android:name` 能解析到真实 Fragment 类
- [ ] 导航图各目的地 `android:id` 与对应菜单（抽屉/底部/溢出）项 `id` 一一对应
- [ ] `MainActivity` 中 `setupActionBarWithNavController` + `AppBarConfiguration` 配置正确，返回箭头/标题随页面联动
- [ ] 系统返回键行为符合预期（返回栈顺序正确、根级目的地直接退出）
- [ ] 无「Fragment 里套 Fragment」的手工嵌套管理代码

## 迁移示例

**迁移前（多 Activity / 手写 Fragment 事务）**：

```kotlin
// 旧的跳转方式：手写 FragmentManager 事务，导航关系散落
supportFragmentManager.beginTransaction()
    .replace(R.id.container, TransformFragment())
    .addToBackStack(null)   // 易漏写，返回行为不稳定
    .commit()
```

**迁移后（Navigation 组件）**：

```xml
<!-- 导航图声明目的地与导航关系 -->
<navigation app:startDestination="@+id/nav_transform">
    <fragment
        android:id="@+id/nav_transform"
        android:name="com.example.myapplication.ui.transform.TransformFragment" />
    <fragment
        android:id="@+id/nav_settings"
        android:name="com.example.myapplication.ui.settings.SettingsFragment" />
</navigation>
```

```kotlin
// 页面内跳转：统一走 NavController，返回栈/状态由框架管理
findNavController().navigate(R.id.nav_settings)
```

迁移要点：先把所有 `replace()` 事务改写为导航图目的地 + `navigate()`，再合并多 Activity 到单一 Activity + `NavHostFragment`，最后接入 `AppBarConfiguration` 统一顶部栏返回。

## 版本与成熟度

- **成熟度**：L1（单项目验证）。源自 `chaos/tests/AndroidStudioProjects/MyApplication` 单一示例工程，结构可复用但尚未跨多项目验证推广。
- **适用版本**：AndroidX Navigation 组件（`androidx.navigation:navigation-fragment-ktx` / `navigation-ui-ktx`），当前采用 Navigation 2.x 语义。

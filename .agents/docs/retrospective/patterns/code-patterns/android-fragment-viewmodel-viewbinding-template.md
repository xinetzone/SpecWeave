---
id: "android-fragment-viewmodel-viewbinding-template"
source: "code: chaos/tests/AndroidStudioProjects/MyApplication (SettingsFragment / SettingsViewModel 模式)"
---
# Fragment + ViewModel + ViewBinding 三件套骨架模板

## 模式概述

创建一个标准 Android Fragment 页面时，使用「布局 XML + ViewModel + Fragment」三件套的可复用骨架。团队成员可直接复制该模板实例化新页面，保证 ViewBinding 生命周期正确、数据订阅安全，避免手写时常见的空指针与内存泄漏问题。

三件套分工：

1. **布局 XML**（`fragment_xxx.xml`）—— 定义页面静态结构
2. **ViewModel**（`XxxViewModel.kt`）—— 持有并暴露页面数据（`LiveData`）
3. **Fragment**（`XxxFragment.kt`）—— 绑定布局、获取 ViewModel、订阅数据并随生命周期安全销毁

## 组件三件套完整骨架代码

以下以一个示例页面「设置页」为例，实际使用请按「命名约定」替换 `xxx` / `Xxx`。

### 1. 布局 XML — `fragment_xxx.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:id="@+id/text_xxx"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

### 2. ViewModel — `XxxViewModel.kt`

```kotlin
package com.example.app.ui.xxx

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class XxxViewModel : ViewModel() {

    // 对外只读暴露 LiveData
    val text: LiveData<String> = _text

    // 内部可变的 MutableLiveData，通过 apply { value = ... } 初始化默认值
    private val _text = MutableLiveData<String>().apply {
        value = "默认文本"
    }

    fun updateText(newText: String) {
        _text.value = newText
    }
}
```

### 3. Fragment — `XxxFragment.kt`

```kotlin
package com.example.app.ui.xxx

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.example.app.databinding.FragmentXxxBinding

class XxxFragment : Fragment() {

    // 可空缓存持有 binding，onDestroyView 时必须置空，避免内存泄漏
    private var _binding: FragmentXxxBinding? = null

    // 非空绑定属性，供业务代码安全访问
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // 通过 ViewModelProvider(this) 获取与 Fragment 生命周期绑定的 ViewModel
        val xxxViewModel = ViewModelProvider(this).get(XxxViewModel::class.java)

        _binding = FragmentXxxBinding.inflate(inflater, container, false)
        val root: View = binding.root

        val textView: TextView = binding.textXxx
        // 用 viewLifecycleOwner 订阅，确保生命周期安全
        xxxViewModel.text.observe(viewLifecycleOwner) { textView.text = it }

        return root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // 关键：销毁视图时释放 binding，防止泄漏
    }
}
```

## 使用方式（实例化步骤）

复制模板后按以下顺序实例化一个新页面：

1. **复制三个文件**：把 `fragment_xxx.xml`、`XxxViewModel.kt`、`XxxFragment.kt` 复制到目标包目录（如 `ui/<页面名>/`）。
2. **替换类名**：将所有 `Xxx` 替换为目标页面名，例如 `Settings`。
3. **替换资源名**：将布局文件名、`text_xxx` 等 id 改为目标页面对应命名。
4. **调整布局**：把默认 TextView 替换为页面实际内容。
5. **注册到 Navigation 图**：在 `res/navigation/*.xml` 中新增 `<fragment android:id="@+id/xxxFragment" android:name=".ui.xxx.XxxFragment" .../>` 节点，并配置 `label` 与目标 id。

## 命名约定

| 元素 | 规则 | 示例 |
|------|------|------|
| Fragment 类 | `Xxx` + `Fragment` | `SettingsFragment` |
| ViewModel 类 | `Xxx` + `ViewModel` | `SettingsViewModel` |
| 布局文件 | `fragment_` + 小写下划线 `xxx` | `fragment_settings.xml` |
| Binding 类 | 布局文件名转 PascalCase + `Binding`（由 ViewBinding 自动生成） | `FragmentSettingsBinding` |
| id 命名 | 小写字母 + `_` 前缀（`xxx_`） | `text_settings` |

> 说明：Binding 类名由 Android 插件根据布局文件名自动生成，例如 `fragment_settings.xml` → `FragmentSettingsBinding`，因此只需保证布局文件命名规范即可。

## 正反例

### 正例

```kotlin
// ✅ 正确：onDestroyView 中置空 _binding，并使用 viewLifecycleOwner 订阅
class SettingsFragment : Fragment() {
    private var _binding: FragmentSettingsBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(inflater, container, savedInstanceState): View {
        val settingsViewModel = ViewModelProvider(this).get(SettingsViewModel::class.java)
        _binding = FragmentSettingsBinding.inflate(inflater, container, false)
        val root: View = binding.root
        val textView: TextView = binding.textSettings
        settingsViewModel.text.observe(viewLifecycleOwner) { textView.text = it }
        return root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // ✅ 释放引用
    }
}
```

### 反例

```kotlin
// ❌ 错误：忘记在 onDestroyView 置空 _binding，导致 View 引用无法释放
class SettingsFragment : Fragment() {
    private var _binding: FragmentSettingsBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(...): View {
        _binding = FragmentSettingsBinding.inflate(...)
        return binding.root
    }
    // ❌ 缺少 onDestroyView() { _binding = null }，视图销毁后仍持有引用
}

// ❌ 错误：用 this（Fragment 生命周期）而非 viewLifecycleOwner 订阅，
//    视图销毁后回调仍可能触发，引发空指针或泄漏
settingsViewModel.text.observe(this) { textView.text = it }
```

## 版本与成熟度

- **成熟度**：`L1`（已在一处 Android 项目 `chaos/tests/AndroidStudioProjects/MyApplication` 中验证使用，可复用作骨架模板）
- **依赖**：`androidx.fragment`、`androidx.lifecycle`（`lifecycle-livedata` / `lifecycle-viewmodel`）、ViewBinding（`buildFeatures { viewBinding = true }`）

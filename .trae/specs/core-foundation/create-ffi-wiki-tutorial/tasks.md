# Tasks

## 任务总览

本 spec 共 8 个文档创建任务，按章节顺序编排。全部任务已完成。

- [x] Task 1: 创建 `00-overview.md` 教程总览与导航索引
- [x] Task 2: 创建 `01-what-is-ffi.md` FFI 定义与核心概念
- [x] Task 3: 创建 `02-working-principles.md` FFI 工作原理
- [x] Task 4: 创建 `03-language-implementations.md` 不同编程语言中的 FFI 实现
- [x] Task 5: 创建 `04-use-cases.md` 实际应用案例与代码示例
- [x] Task 6: 创建 `05-advantages-limitations.md` 优势与局限性
- [x] Task 7: 创建 `06-comparison.md` 相关概念对比
- [x] Task 8: 创建 `07-resources.md` 术语表与参考资料
- [x] Task 9: 统一质量验证（文件大小、链接、frontmatter、导航）

---

## 任务详细分解

### Task 1: 创建 `00-overview.md` 教程总览与导航索引
- [x] Step 1.1: 在 `docs/knowledge/learning/ffi-wiki/` 目录下创建 `00-overview.md`
- [x] Step 1.2: 编写 YAML frontmatter
- [x] Step 1.3: 编写教程引言，简述 FFI 在跨语言技术栈中的定位与学习价值
- [x] Step 1.4: 绘制 Mermaid 概念层次图，展示 FFI 与 ABI/API/IDL/RPC/IPC 的关系
- [x] Step 1.5: 编写 8 章导航表（章节号 + 标题 + 简要内容描述 + 文件链接）
- [x] Step 1.6: 编写目标读者说明
- [x] Step 1.7: 编写阅读路径建议，并链接延伸阅读
- **验证**: 通过（77 行 < 300；frontmatter 完整；含 Mermaid 图；导航链接相对路径）

### Task 2: 创建 `01-what-is-ffi.md` FFI 定义与核心概念
- [x] Step 2.1: 创建文件并编写 frontmatter
- [x] Step 2.2: 编写 FFI 标准定义段落（Wikipedia 风格）
- [x] Step 2.3: 编写 ≥5 个核心概念详解
- [x] Step 2.4: 绘制 Mermaid 时间线图
- [x] Step 2.5: 编写 "FFI 与 ABI/API 的关系" 辨析段落
- [x] Step 2.6: 编写 "FFI 解决的核心问题" 段落
- [x] Step 2.7: 添加底部双向导航
- **验证**: 通过（251 行 < 300；含时间线图；含 ABI/API 辨析；Wikipedia 风格）

### Task 3: 创建 `02-working-principles.md` FFI 工作原理
- [x] Step 3.1: 创建文件并编写 frontmatter
- [x] Step 3.2: 编写 "调用约定" 段落，配 Mermaid 时序图
- [x] Step 3.3: 编写 "名称修饰" 段落
- [x] Step 3.4: 编写 "数据封送" 段落，覆盖 4 种类型，每项配代码示例
- [x] Step 3.5: 编写 "内存管理" 段落
- [x] Step 3.6: 编写 "绑定生成" 段落
- [x] Step 3.7: 添加底部双向导航
- **验证**: 通过（228 行 < 300；含调用约定时序图；4 种封送各有代码示例；含绑定对比）

### Task 4: 创建 `03-language-implementations.md` 不同编程语言中的 FFI 实现
- [x] Step 4.1: 创建文件并编写 frontmatter
- [x] Step 4.2: 编写 Python 小节（ctypes + cffi）
- [x] Step 4.3: 编写 Java 小节（JNI + JNA）
- [x] Step 4.4: 编写 Go 小节（cgo）
- [x] Step 4.5: 编写 Rust 小节（extern "C" + unsafe + bindgen）
- [x] Step 4.6: 编写 Node.js 小节（ffi-napi + bun:ffi）
- [x] Step 4.7: 编写 C# 小节（P/Invoke）
- [x] Step 4.8: 编写 6 种方案对比总结表
- [x] Step 4.9: 添加底部双向导航
- **验证**: 通过（209 行 < 300；覆盖 6 种语言；含对比总结表）

### Task 5: 创建 `04-use-cases.md` 实际应用案例与代码示例
- [x] Step 5.1: 创建文件并编写 frontmatter
- [x] Step 5.2: 编写案例 1：Python 调用 C 实现矩阵运算加速
- [x] Step 5.3: 编写案例 2：Rust 集成 C 图形库（raylib）
- [x] Step 5.4: 编写案例 3：Go 通过 cgo 调用 C 压缩库（zlib）
- [x] Step 5.5: 编写最佳实践清单（5 条）
- [x] Step 5.6: 交叉引用 idl-wiki
- [x] Step 5.7: 添加底部双向导航
- **验证**: 通过（232 行 < 300；含 3 个完整案例；含 5 条最佳实践）

### Task 6: 创建 `05-advantages-limitations.md` 优势与局限性
- [x] Step 6.1: 创建文件并编写 frontmatter
- [x] Step 6.2: 编写 "优势" 段落
- [x] Step 6.3: 编写 "局限性" 段落
- [x] Step 6.4: 编写 "性能开销分析" 段落，配 Mermaid 图
- [x] Step 6.5: 编写 "安全性考量" 段落
- [x] Step 6.6: 添加底部双向导航
- **验证**: 通过（145 行 < 300；含性能开销分析；含安全性考量；客观中立）

### Task 7: 创建 `06-comparison.md` 相关概念对比
- [x] Step 7.1: 创建文件并编写 frontmatter
- [x] Step 7.2: 编写多维度对比表格
- [x] Step 7.3: 绘制 Mermaid 关系图
- [x] Step 7.4: 编写选型决策树（Mermaid flowchart）
- [x] Step 7.5: 编写 "常见混淆点澄清" 段落
- [x] Step 7.6: 交叉引用
- [x] Step 7.7: 添加底部双向导航
- **验证**: 通过（101 行 < 300；含多维度对比表格；含关系图 + 决策树；含交叉引用）

### Task 8: 创建 `07-resources.md` 术语表与参考资料
- [x] Step 8.1: 创建文件并编写 frontmatter
- [x] Step 8.2: 编写术语表（21 条）
- [x] Step 8.3: 编写权威参考资料链接清单
- [x] Step 8.4: 编写按难度分级的扩展阅读建议
- [x] Step 8.5: 编写 "项目内相关 wiki 交叉引用" 段落
- [x] Step 8.6: 添加底部双向导航
- **验证**: 通过（78 行 < 300；术语表 21 条；含权威资料链接；含项目内交叉引用）

### Task 9: 统一质量验证
- [x] Step 9.1: 所有文件 < 300 行（最大 251 行，最小 77 行）
- [x] Step 9.2: 链接检查全部通过（40 个本地引用均有效）
- [x] Step 9.3: 所有文件 frontmatter 包含 `source: "spec:create-ffi-wiki-tutorial"` 与 `category: "learning"`
- [x] Step 9.4: 01-06 文件底部三向导航链接完整且正确
- [x] Step 9.5: 内容覆盖度达标（6 种语言、3 个案例、5 条最佳实践、21 条术语）
- [x] Step 9.6: 修复 3 处 idl-wiki 交叉引用断链（章节编号偏移）

---

# Task Dependencies

所有任务已完成。执行顺序：阶段一 Task 1 → 阶段二 Task 2-8 并行 → 阶段三 Task 9 质量验证与修复。
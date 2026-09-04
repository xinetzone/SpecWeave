# Checklist: FFI（外部函数接口）Wiki 教程

## 目录与结构
- [x] `docs/knowledge/learning/ffi-wiki/` 目录存在
- [x] `00-overview.md` 存在且 < 300 行
- [x] `01-what-is-ffi.md` 存在且 < 300 行
- [x] `02-working-principles.md` 存在且 < 300 行
- [x] `03-language-implementations.md` 存在且 < 300 行
- [x] `04-use-cases.md` 存在且 < 300 行
- [x] `05-advantages-limitations.md` 存在且 < 300 行
- [x] `06-comparison.md` 存在且 < 300 行
- [x] `07-resources.md` 存在且 < 300 行

## 00-overview.md 内容验证
- [x] 包含教程简介与 FFI 在跨语言技术栈中的定位说明
- [x] 包含 Mermaid 概念层次图（展示 FFI 与 ABI/API/IDL/RPC/IPC 的关系）
- [x] 包含 8 章完整导航表（章节号 + 标题 + 简要描述 + 文件链接）
- [x] 包含目标读者说明
- [x] 包含阅读路径建议（线性阅读 vs 按需查阅）
- [x] 包含与 `interface-api-abi-protocol-wiki` 和 `idl-wiki` 的关联指引

## 01-what-is-ffi.md 内容验证
- [x] 包含 Wikipedia 风格的标准定义（客观中立，先简洁定义再展开）
- [x] 包含 ≥5 个核心概念详解（跨语言调用/调用约定/数据封送/内存边界/符号解析）
- [x] 包含 Mermaid 发展时间线图（早期→标准化→现代三阶段）
- [x] 包含 FFI 与 ABI/API 的关系辨析段落
- [x] 包含 FFI 解决的核心问题说明（打破语言孤岛/复用 C 库/性能优化）
- [x] 底部导航：无上一章 / 返回目录 / 下一章 `02-working-principles.md`

## 02-working-principles.md 内容验证
- [x] 包含调用约定详解（cdecl/stdcall/fastcall/system V AMD64）
- [x] 包含 Mermaid 时序图展示跨语言调用栈帧变化
- [x] 包含名称修饰说明（C++ name mangling + `extern "C"` 解决方案 + 代码示例）
- [x] 包含数据封送 4 种类型：基本类型映射（含对应表）、结构体对齐（含规则说明）、字符串传递、回调函数指针
- [x] 每项数据封送配代码示例
- [x] 包含内存管理段落（所有权边界/分配释放策略/常见陷阱）
- [x] 包含绑定生成段落（手动绑定 vs 自动绑定工具对比）
- [x] 底部导航：上一章/返回目录/下一章正确

## 03-language-implementations.md 内容验证
- [x] 覆盖 Python（ctypes + cffi）两种方案，含实现机制 + API + 代码示例 + 场景
- [x] 覆盖 Java（JNI + JNA）两种方案，含实现机制 + API + 代码示例 + 场景
- [x] 覆盖 Go（cgo）方案，含实现原理 + 核心语法 + 代码示例 + 注意事项
- [x] 覆盖 Rust（extern "C" + unsafe + bindgen）方案，含实现机制 + 语法 + 代码示例 + 安全性说明
- [x] 覆盖 Node.js（ffi-napi + bun:ffi）两种方案，含实现机制 + API + 代码示例 + 场景
- [x] 覆盖 C#（P/Invoke）方案，含实现原理 + 核心语法 + 代码示例 + 场景
- [x] 包含 6 种方案对比总结表
- [x] 底部导航：上一章/返回目录/下一章正确

## 04-use-cases.md 内容验证
- [x] 包含案例 1：Python 调用 C 实现矩阵运算加速（C 源码 + Python ctypes 调用 + 性能对比）
- [x] 包含案例 2：Rust 集成 C 图形库（C 头文件 + Rust 绑定 + 调用示例）
- [x] 包含案例 3：Go 通过 cgo 调用 C 压缩库（C 调用 + Go 封装 + 使用示例）
- [x] 包含 ≥5 条最佳实践（错误处理/内存安全/线程安全/版本兼容/绑定测试）
- [x] 包含与 `idl-wiki` 的交叉引用（FFI 手动绑定 vs IDL 代码生成选择）
- [x] 底部导航：上一章/返回目录/下一章正确

## 05-advantages-limitations.md 内容验证
- [x] 包含优势分析（性能/生态/整合/零依赖）
- [x] 包含局限性分析（类型安全/内存安全/调试/平台/构建）
- [x] 包含性能开销分析（调用开销分解 + 基准数据 + Mermaid 图）
- [x] 包含安全性考量（常见漏洞 + 防护建议）
- [x] 内容客观中立，不偏袒任何技术方案
- [x] 底部导航：上一章/返回目录/下一章正确

## 06-comparison.md 内容验证
- [x] 包含 FFI vs ABI/API/RPC/IPC/IDL 多维度对比表格
- [x] 包含 Mermaid 关系图（展示各概念在跨语言技术栈中的层次关系）
- [x] 包含选型决策树（Mermaid flowchart）
- [x] 包含常见混淆点澄清（FFI vs ABI、FFI vs IDL、FFI vs RPC）
- [x] 包含与 `interface-api-abi-protocol-wiki` 和 `idl-wiki` 的交叉引用
- [x] 底部导航：上一章/返回目录/下一章正确

## 07-resources.md 内容验证
- [x] 包含 ≥15 条术语表
- [x] 包含权威参考资料链接（语言官方文档 + Wikipedia + 论文/书籍）
- [x] 包含按难度分级的扩展阅读建议（入门/进阶/高级）
- [x] 包含与项目内相关 wiki 的交叉引用
- [x] 底部导航：上一章/返回目录/无下一章，提示 "教程已完成"

## 元数据与导航
- [x] 所有 8 个文件 frontmatter 包含 `source: "spec:create-ffi-wiki-tutorial"`
- [x] 所有 8 个文件 frontmatter 包含 `category: "learning"`
- [x] 所有 8 个文件 frontmatter 包含 `x-toml-ref` 字段
- [x] 分章文档（01-06）包含完整的三向导航链接
- [x] 所有导航链接使用相对路径

## 链接有效性
- [x] 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/ffi-wiki/` 全部通过
- [x] 无 `file:///` 绝对路径断链
- [x] 所有交叉引用链接指向正确文件

## 代码质量
- [x] 所有代码示例标注语言类型
- [x] 代码示例具有说明性或可运行性
- [x] 代码示例覆盖 C/Python/Go/Rust 等主流语言
- [x] 无遗留的占位符或 TODO 标记
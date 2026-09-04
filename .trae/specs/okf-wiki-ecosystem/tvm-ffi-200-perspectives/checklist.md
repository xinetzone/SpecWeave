# TVM FFI 200 视角深度解读 - 验证清单

## R阶段（事实采集）验证

- [ ] Checkpoint 1: facts.md 存在且包含编号事实 F-001 起
- [ ] Checkpoint 2: 每个事实包含源码文件路径和行号引用
- [ ] Checkpoint 3: 事实中无"用于"/"目的是"/"设计为"等推断性表述（G1质量门）
- [ ] Checkpoint 4: 核心模块全覆盖（any/c_api/function/object/container/tensor/error/dtype/enum/cast）
- [ ] Checkpoint 5: TVM 中 FFI 交互关键文件已采集（_ffi_api.py, module.cc, runtime 等）

## I阶段（洞察与知识地图）验证

- [ ] Checkpoint 6: 至少 5 个洞察四元组（陈述+证据+反常识+行动）（G2质量门）
- [ ] Checkpoint 7: 200 个视角全部有编号、标题、分类映射
- [ ] Checkpoint 8: 每个视角至少关联一个 F-xxx 事实编号
- [ ] Checkpoint 9: 15 个分类的文档数量之和等于 200
- [ ] Checkpoint 10: 视角之间无标题重复或内容过度重叠

## 基础设施验证

- [ ] Checkpoint 11: `d:\AI\projects\docs` 目录存在
- [ ] Checkpoint 12: 15 个分类子目录全部创建（01-architecture 至 15-npu-accelerator）
- [ ] Checkpoint 13: 每个分类目录下存在 concepts/ 和 references/ 子目录
- [ ] Checkpoint 14: references/ 信源文件先于 concepts/ 创建（G3信源先行）
- [ ] Checkpoint 15: 每个 references/ 文件包含源码路径和关键 API 清单

## 文档数量与分类验证

- [ ] Checkpoint 16: 分类01（架构与设计哲学）恰好 15 份概念文档
- [ ] Checkpoint 17: 分类02（核心类型系统）恰好 20 份概念文档
- [ ] Checkpoint 18: 分类03（函数与调用系统）恰好 15 份概念文档
- [ ] Checkpoint 19: 分类04（容器系统）恰好 15 份概念文档
- [ ] Checkpoint 20: 分类05（Tensor与DLPack）恰好 10 份概念文档
- [ ] Checkpoint 21: 分类06（错误处理系统）恰好 10 份概念文档
- [ ] Checkpoint 22: 分类07（反射系统）恰好 15 份概念文档
- [ ] Checkpoint 23: 分类08（C++实现细节）恰好 15 份概念文档
- [ ] Checkpoint 24: 分类09（Python绑定）恰好 15 份概念文档
- [ ] Checkpoint 25: 分类10（Rust绑定）恰好 10 份概念文档
- [ ] Checkpoint 26: 分类11（C ABI与平台）恰好 10 份概念文档
- [ ] Checkpoint 27: 分类12（构建与打包）恰好 10 份概念文档
- [ ] Checkpoint 28: 分类13（测试策略）恰好 10 份概念文档
- [ ] Checkpoint 29: 分类14（TVM编译器集成）恰好 15 份概念文档
- [ ] Checkpoint 30: 分类15（NPU与加速器建议）恰好 15 份概念文档
- [ ] Checkpoint 31: 概念文档总数恰好 200 份

## Frontmatter 规范性验证

- [ ] Checkpoint 32: 每份概念文档包含 YAML frontmatter（--- 包裹）
- [ ] Checkpoint 33: frontmatter 包含 type 字段（值为 Concept）
- [ ] Checkpoint 34: frontmatter 包含 title 字段
- [ ] Checkpoint 35: frontmatter 包含 description 字段（30-80字）
- [ ] Checkpoint 36: frontmatter 包含 tags 字段（数组）
- [ ] Checkpoint 37: frontmatter 包含 generated 字段（by + at）
- [ ] Checkpoint 38: frontmatter 包含 verified 字段（by: "process:seven-concepts-v" + at）
- [ ] Checkpoint 39: frontmatter 包含 status 字段（draft/stable）
- [ ] Checkpoint 40: frontmatter 包含 sources 字段（id + resource + title）
- [ ] Checkpoint 41: sources 指向的 references/ 文件确实存在

## API 真实性验证（G4质量门核心）

- [ ] Checkpoint 42: 分类01 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 43: 分类02 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 44: 分类03 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 45: 分类04 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 46: 分类05 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 47: 分类06 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 48: 分类07 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 49: 分类08 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 50: 分类09 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 51: 分类10 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 52: 分类11 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 53: 分类12 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 54: 分类13 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 55: 分类14 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 56: 分类15 文档引用的类名/函数名经 Grep 验证存在于源码
- [ ] Checkpoint 57: 代码块标注了正确的语言（cpp/python/rust/c）
- [ ] Checkpoint 58: 代码示例中的 API 调用与 facts.md 事实一致

## 链接完整性验证

- [ ] Checkpoint 59: 文档间交叉链接无断裂（目标文件存在）
- [ ] Checkpoint 60: 交叉链接使用 `/` 开头的 bundle-relative 路径
- [ ] Checkpoint 61: sources 字段中的 resource 路径有效
- [ ] Checkpoint 62: 无 `file:///` 绝对路径链接
- [ ] Checkpoint 63: 无 `../` 相对路径链接

## NPU 建议验证

- [ ] Checkpoint 64: 分类05（Tensor与DLPack）全部 10 份文档包含"NPU建议"章节
- [ ] Checkpoint 65: 分类15（NPU与加速器）全部 15 份文档包含"NPU建议"章节
- [ ] Checkpoint 66: tasks.md 中标注 ✓ 的其他文档均包含"NPU建议"章节
- [ ] Checkpoint 67: NPU 建议具体可操作，非泛泛而谈
- [ ] Checkpoint 68: NPU 建议结合 TVM FFI 机制给出实现路径
- [ ] Checkpoint 69: NPU 建议引用了相关 API 或代码模式

## 内容质量验证

- [ ] Checkpoint 70: 每份文档开头有 1-2 段概述
- [ ] Checkpoint 71: 每份文档包含源码引用（文件路径+行号）
- [ ] Checkpoint 72: 每份文档有"## 相关概念"章节
- [ ] Checkpoint 73: 文档使用 `##` 二级标题分节，不使用 `#`（留给文件标题）
- [ ] Checkpoint 74: 正文使用规范现代汉语
- [ ] Checkpoint 75: 英文技术术语首次出现时括号注释
- [ ] Checkpoint 76: 每份文档长度 800-3000 字
- [ ] Checkpoint 77: 无虚构 API、不存在的文件路径或编造的设计决策

## 索引验证

- [ ] Checkpoint 78: 总索引 index.md 存在且包含 okf_version frontmatter
- [ ] Checkpoint 79: 总索引链接全部 15 个分类
- [ ] Checkpoint 80: 总索引列出全部 200 份文档
- [ ] Checkpoint 81: 每个分类目录有 index.md（无 frontmatter）
- [ ] Checkpoint 82: 每个分类 index 列出其下全部概念文档
- [ ] Checkpoint 83: 每个分类有 log.md 变更日志
- [ ] Checkpoint 84: 所有 index.md 在内容文档定稿后生成（Index最后写原则）

## 文件名规范验证

- [ ] Checkpoint 85: 文件名使用 kebab-case 纯英文
- [ ] Checkpoint 86: 文件名包含视角编号前缀（如 001-overview-architecture.md）
- [ ] Checkpoint 87: 无中文文件名
- [ ] Checkpoint 88: 无空格或特殊字符文件名

## V阶段最终验证

- [ ] Checkpoint 89: V阶段验证报告已生成
- [ ] Checkpoint 90: 所有发现的问题已修复
- [ ] Checkpoint 91: 0 个虚构 API
- [ ] Checkpoint 92: 0 个断裂链接
- [ ] Checkpoint 93: frontmatter 100% 完整

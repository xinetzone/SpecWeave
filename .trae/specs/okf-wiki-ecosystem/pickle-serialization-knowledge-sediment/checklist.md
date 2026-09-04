# Checklist

> **方法论编排 G1-G4 质量门检查清单**

## G1：事实阶段质量门（R 阶段产出检查）

- [x] 事实清单纯客观描述，无因果推断词（"因为/导致/所以"）
- [x] 三份源材料的关键事实均已提取（修复事实、诊断方法、检查流程）
- [x] 事实清单覆盖：IdentityTransform 类、环境变量、诊断日志、11 测试、5 决策、6 种模式、3 种修复方案、5 步流程

## G2：洞察阶段质量门（I 阶段产出检查）

- [x] 洞察四元组完整：现象描述 + 根因分析 + 影响评估 + 改进建议
- [x] 根因触及本质（pickle 要求模块级 qualname，而非表面现象"lambda 不能 pickle"）
- [x] 与已有沉淀的差异化定位清晰（源码层正本清源 vs 运行时兼容层）
- [x] 互补关系明确（可改源码用源码层修复，不可改源码用运行时兼容层）

## G3：萃取阶段质量门（E 阶段产出检查）

### pickle-serialization-source-fix.md

- [x] frontmatter 完整（id/title/type/date/maturity/source/related_patterns/tags）
- [x] 包含触发场景（识别信号 + 适用条件 + 不适用条件）
- [x] 包含三种修复方案及适用条件（命名类 / 命名函数 / functools.partial）
- [x] 包含 pickle 四条黄金法则（模块级别 / 无 lambda / 无状态 / 可导入）
- [x] 包含反模式（至少 3 条，含"在 __call__ 加日志"）
- [x] 包含与 `python-314-multiprocessing-fork-compat.md` 的互补关系声明
- [x] 包含迁移验证方法
- [x] 包含相关案例（引用 task-summary-20260723.md）

### dataloader-pickle-diagnosis-sop.md

- [x] frontmatter 完整（id/title/category/tags/date/status/summary）
- [x] 包含 5 步诊断流程（复现 → 定位 → 识别 → 修复 → 验证）
- [x] 包含 6 种不可序列化模式对照表（lambda/闭包/局部类/文件句柄/网络连接/CUDA 张量）
- [x] 包含 3 种修复方案模板及适用场景
- [x] 包含跨启动模式验证矩阵（fork/forkserver/spawn）
- [x] 包含常见错误信息对照表
- [x] 包含环境变量速查（XMN_MP_START_METHOD / XMN_DEBUG_PICKLE）
- [x] 包含代码审查附加检查项

## G4：行动项原子化质量门（索引同步与收尾检查）

- [x] code-patterns/README.md 模式清单新增条目，一句话摘要准确
- [x] best-practices/README.md 文档索引新增条目，适用场景标签准确
- [x] best-practices/README.md 快速导航新增「序列化诊断」场景分组
- [x] 新模式与 `python-314-multiprocessing-fork-compat.md` 的 related_patterns 双向声明
- [x] 新实践与 `python-version-upgrade-compatibility-check.md` 的关联已建立

## 链接与溯源校验

- [x] 新文档内引用使用相对路径，无 `file:///` 绝对路径
- [x] frontmatter 的 source 字段标注来源（task-summary-20260723.md / DEBUG_PICKLE.md / PICKLE_CHECKLIST.md）
- [x] 跨目录引用使用多级相对路径
- [x] 同目录互引使用文件名相对路径
- [x] 无断链（引用的目标文件均存在）

## 内容质量校验

- [x] 新文档不与已有文档内容重复（聚焦源码层修复，非运行时兼容层）
- [x] 源材料的精华已整合（DEBUG_PICKLE.md 的 6 种模式 + PICKLE_CHECKLIST.md 的 5 步流程）
- [x] 案例引用真实（基于 task-summary-20260723.md 的实际修复）
- [x] 代码示例可运行（IdentityTransform 类、pickle.dumps 诊断函数）
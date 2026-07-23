# Spec Templates 索引

本目录存放可复用的 Spec 模板。每个模板针对一类特定的任务类型，提供预定义的 PRD 结构、任务拆分和验证清单。

## 可用模板

| 模板 | 适用场景 | 来源 |
|------|---------|------|
| [cpp-dependency-slimming](cpp-dependency-slimming/) | C++ 项目依赖替换/瘦身（用新库替换旧依赖、移除boost/glog等） | 萃取自 Caffe→tvm-ffi 瘦身实战 |

## 使用方法

1. 复制模板目录到目标项目的 `.trae/specs/[你的spec名称]/` 下
2. 按照模板中的 `README.md` 指引填写占位符
3. 完成前置预检章节（Step 0/0.5/1）后再开始执行
4. 执行过程中逐项勾选 checklist.md 中的验证项

## 添加新模板

当你完成一个有代表性的项目后，可以将其 spec 萃取为模板：

1. 将实际项目的 spec.md/tasks.md/checklist.md 复制为模板
2. 将项目特定内容替换为 `[占位符]`
3. 添加 README.md 说明使用方法、适用场景、核心原则
4. 在本索引中添加条目

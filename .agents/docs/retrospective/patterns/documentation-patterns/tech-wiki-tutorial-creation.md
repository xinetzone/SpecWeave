---
id: pattern-tech-wiki-tutorial-creation
title: 技术Wiki教程创建模式
date: 2026-07-28
source: retro-tvm-ffi-wiki-20260728
maturity: draft
validation_count: 1
reuse_count: 0
tags: [wiki, 技术文档, 教程模式, 开源翻译, 知识沉淀]
pattern_type: methodology
category: documentation
---

# 技术Wiki教程创建模式

## 触发场景
当需要为一个第三方开源库/框架创建系统性中文教程Wiki时，特别是：
- 源码位于vendor子模块（只读约束）
- 库本身缺乏中文文档
- 需要面向项目内部开发者提供学习材料
- 教程需要可验证的代码示例

## 核心步骤

### 步骤1：源码结构分析（前置）
1. 阅读源码根目录README和目录结构
2. 识别核心头文件/模块入口
3. 理解include/src/python的分层关系
4. 列出examples目录下的示例文件
5. **产出**：项目结构图和核心模块清单

### 步骤2：章节结构设计
遵循"认知路径优先"原则，按8+4结构组织：
```
第一部分：入门认知（2章）
├── 00-overview.md       总览：是什么/解决什么/核心特性/学习路线
└── 01-structure.md      项目结构：目录树+各模块职责

第二部分：核心概念（5章）
├── 02-type-system.md    类型系统：Any/DataType/类型映射表
├── 03-object-system.md  对象系统：Object/ObjectRef/继承机制
├── 04-function.md       函数注册：PackedFunc/Registry/跨语言调用
├── 05-containers.md     容器类型：Array/Map/String/Tensor等
└── 06-reflection.md     反射机制：dataclass/序列化

第三部分：进阶机制（1章）
└── 07-module-system.md  模块系统：动态加载/inline编译

第四部分：实战指南（4章）
├── 08-cpp-guide.md      C++开发指南
├── 09-python-guide.md   Python开发指南
├── 10-build.md          构建打包
├── 11-examples.md       实战案例

第五部分：参考资料（2章）
├── 12-faq.md            FAQ常见问题
└── 13-source-analysis.md 源码解析
```

### 步骤3：内容编写规范
1. **双语术语**：首次出现时给出"英文术语（中文解释）"，后续统一使用英文术语
2. **类型表格**：复杂类型系统使用"类型编码→C类型→Python类型→用途"四列表格
3. **代码块标注语言**：C++用```cpp，Python用```python
4. **跨章节引用**：使用相对路径Markdown链接
5. **每章开头有摘要**：告诉读者本章讲什么、学完能做什么

### 步骤4：可运行Demo脚本
1. 创建`examples_demo.py`（或对应语言），整合所有核心API演示
2. 脚本结构：环境检查→基础API→容器→Tensor互操作→高级特性→inline编译
3. 每个模块用清晰分隔符（=====）和标题
4. 可选依赖用try/except优雅降级，给出安装指引
5. 发布前通过语法检查

### 步骤5：Wiki索引发布
1. 在对应分类目录下创建README.md作为分类索引
2. 更新知识库README.md的快速导航表
3. 添加最近更新条目
4. 运行docgen更新全局导航
5. 更新统计数字（总条目数、分类数）

## 反模式

| 反模式 | 后果 | 正确做法 |
|--------|------|---------|
| 想到哪写到哪，无章节规划 | 读者认知跳跃，教程难读 | 先设计章节结构再写内容 |
| 只翻译不验证代码 | 示例代码可能无法运行 | 配套可运行demo脚本验证 |
| 术语只有中文无英文 | 读者查源码时对不上 | 双语术语对照 |
| 在vendor目录直接修改 | 无法提交，submodule冲突 | 在knowledge区独立创建Wiki |
| 纯文字描述类型系统 | 读者理解困难 | 使用类型映射表格 |
| 忘记发布到索引 | 文档成为孤岛，难以发现 | 更新README和导航表 |

## 迁移验证
- ✅ TVM FFI Wiki教程：14章+examples_demo.py，已发布到knowledge/tech/
- 🔄 可迁移到：其他vendor库（pytorch、onnxruntime等）的中文教程创建

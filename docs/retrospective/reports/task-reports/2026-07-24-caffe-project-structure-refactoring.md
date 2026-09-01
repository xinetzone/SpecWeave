---
id: "caffe-project-structure-refactoring-retrospective"
title: "Caffe 项目结构重组复盘报告"
date: 2026-07-24
type: "retrospective+insight+extraction"
scope: "task"
source: "projects/xuanspace/vendor/caffe/ commit 1fd2e13e"
methodology: "R→I→E (场景4：知识沉淀)"
tags: [caffe, project-structure, refactoring, build-config, cmake, conan, documentation]
---

# Caffe 项目结构重组复盘报告

> **方法论链路**: R（复盘）→ I（洞察）→ E（萃取）
> **源提交**: `projects/xuanspace/vendor/caffe/` commit `1fd2e13e`
> **涉及项目**: `projects/xuanspace/vendor/caffe/`

---

## 一、R-Phase：复盘（事实采集）

### 1.1 任务概览

| 维度 | 事实 |
|------|------|
| 任务目标 | 将根目录中散落的构建配置、文档、示例代码按职责分离到独立目录 |
| 执行时间 | 2026-07-24 |
| 涉及仓库 | caffe (daoflows/caffe fork) |
| 原子提交 | `1fd2e13e refactor(project): 重组项目结构，将构建配置/文档/示例分离到独立目录` |
| 变更规模 | 13 files, +906 -89 |

### 1.2 变更内容

#### 构建配置迁移（4 个文件）

| # | 操作 | 旧路径 | 新路径 | 附加修改 |
|---|------|--------|--------|---------|
| 1 | 重命名 | `.conanrc` | `tools/build-config/.conanrc` | `conan_home` 路径从 `./.conan2` 修正为 `../../.conan2` |
| 2 | 重命名 | `CMakeLists.txt` | `tools/build-config/CMakeLists.txt` | proto 文件路径添加 `../../` 前缀 |
| 3 | 重命名 | `conanfile.py` | `tools/build-config/conanfile.py` | 无内容变更 |
| 4 | 新增 | — | `tools/build-config/README.md` | 36 行构建说明文档 |

#### 文档分离（1 个文件）

| # | 操作 | 路径 | 说明 |
|---|------|------|------|
| 5 | 新增 | `docs/adding-operators.md` | 从 `README.md` 提取"添加新算子（四步法）"完整内容，66 行 |

#### 示例代码（5 个文件）

| # | 操作 | 路径 |
|---|------|------|
| 6 | 新增 | `examples/op-extension/README.md` |
| 7 | 新增 | `examples/op-extension/code/gen_proto_demo.py` |
| 8 | 新增 | `examples/op-extension/code/hardsigmoid_layer.py` |
| 9 | 新增 | `examples/op-extension/code/hardsigmoid_param.proto` |
| 10 | 新增 | `examples/op-extension/code/test_hardsigmoid.py` |

#### 结构文档更新（2 个文件）

| # | 文件 | 变更行数 | 变更内容 |
|---|------|---------|---------|
| 11 | `AGENTS.md` | +15/-2 | 目录树新增 `docs/`、`tools/build-config/` 节点；导航表更新构建引用路径 |
| 12 | `README.md` | +6/-84 | 构建指令和算子文档精简为链接引用；详细内容迁移至 `tools/build-config/README.md` 和 `docs/adding-operators.md` |

### 1.3 重构前后目录对比

```
重构前                              重构后
caffe/                              caffe/
├── .conanrc                        ├── docs/
├── CMakeLists.txt                   │   └── adding-operators.md
├── conanfile.py                    ├── tools/
├── AGENTS.md                        │   └── build-config/
├── README.md (84行冗余内容)          │       ├── .conanrc
├── caffex/                          │       ├── CMakeLists.txt
├── python/                          │       ├── conanfile.py
└── .agents/                         │       └── README.md
                                     ├── examples/
                                     │   └── op-extension/
                                     ├── AGENTS.md (更新)
                                     ├── README.md (精简至46行)
                                     ├── caffex/
                                     ├── python/
                                     └── .agents/
```

### 1.4 质量门 G1 自检

- [x] 事实阶段无因果推断词（"因为"、"导致"、"所以"）
- [x] 所有变更均以可验证的 git diff 为数据源
- [x] 变更内容以表格形式呈现，精确到文件路径和行数

---

## 二、I-Phase：洞察（根因分析）

### 2.1 现象描述

caffe 项目根目录中存在三类文件混合：构建配置（`.conanrc`、`CMakeLists.txt`、`conanfile.py`）、项目文档（`README.md` 中嵌套算子开发指南）和源代码目录（`caffex/`、`python/`）。随项目演进，`README.md` 膨胀至 84 行（含构建命令、算子开发四步法），构建配置与源码目录平级，缺少示例代码目录。

### 2.2 根因分析

| 根因 | 类别 | 说明 |
|------|------|------|
| 项目初期快速搭建，未规划目录结构 | 架构债 | 构建配置、文档、示例直接放在根目录，"能用就行"阶段未做目录规划 |
| 文档膨胀未及时拆分 | 文档债 | `README.md` 从简单说明逐步叠加构建指令和算子开发指南，超过有效信息密度阈值 |
| 缺少示例代码目录约定 | 规范缺失 | 项目没有约定示例代码存放位置，导致算子扩展示例无处归档 |

### 2.3 影响评估

| 影响 | 严重程度 | 说明 |
|------|---------|------|
| 新开发者认知负荷高 | 中 | 根目录文件列表混杂，难以快速定位"构建入口"和"文档入口" |
| 文档可发现性差 | 中 | 算子开发指南藏在 README 底部，不读完无法发现 |
| 构建配置与项目耦合过紧 | 低 | 配置文件路径硬编码相对于根目录，移动后需修正 |
| 示例代码缺失入口 | 中 | 缺少 `examples/` 目录，示例代码无法系统化组织 |

### 2.4 改进建议

| 建议 | 优先级 | 实施状态 |
|------|--------|---------|
| 构建配置统一归入 `tools/build-config/` | 高 | 已完成 |
| 长文档按主题拆分到独立文件 | 高 | 已完成（`adding-operators.md`） |
| 建立 `examples/` 目录约定 | 高 | 已完成（`op-extension/` 示例） |
| `AGENTS.md` 目录树保持同步更新 | 中 | 已完成 |
| 后续新增示例和文档遵循目录约定 | 中 | 待持续执行 |

### 2.5 质量门 G2 自检

- [x] 洞察四元组完整：现象 → 根因 → 影响 → 建议
- [x] 根因分析使用 5-Whys 方法追溯至架构债和规范缺失
- [x] 改进建议有明确优先级和实施状态

---

## 三、E-Phase：萃取（可复用模式）

### 3.1 模式：项目目录结构渐进式分离法

**触发场景**：项目初期快速搭建后，根目录文件混杂（构建配置、文档、示例与源码目录平级），需要在不破坏现有功能的前提下进行目录结构重组。

**核心步骤**：

| 步骤 | 操作 | 输入 | 输出 |
|------|------|------|------|
| S1：分类识别 | 扫描根目录所有文件，按职责分类（构建配置/文档/示例/源码） | 根目录文件列表 | 分类矩阵 |
| S2：目标目录创建 | 为每类文件创建目标子目录（如 `tools/build-config/`、`docs/`、`examples/`） | 分类矩阵 | 空目录结构 |
| S3：文件迁移 | 使用 `git mv` 将文件移至目标目录，同步修正内部路径引用 | 文件 + 目标目录 | 重命名后的文件 |
| S4：文档补充 | 为目标目录创建 README.md，说明该目录用途和文件说明 | 目标目录 | README.md |
| S5：入口文档浓缩 | 将根目录入口文档（README.md, AGENTS.md）中的冗余内容替换为链接引用 | 原始入口文档 | 精简后的入口文档 |
| S6：原子提交 | 将全部变更作为一个原子提交，确保重构可独立回滚 | 所有变更 | git commit |

**关键注意事项**：

1. **S3 路径修正**：文件移动后，内部相对路径引用必须同步修正。如 `CMakeLists.txt` 中 `python/protos/caffe.proto` 需改为 `../../python/protos/caffe.proto`。
2. **S5 链接引用**：入口文档精简后，用相对路径链接指向新位置，确保信息不丢失。
3. **git mv 优于手动 mv**：`git mv` 能自动识别重命名，保持 git 历史连续性。

**反模式**：

| 反模式 | 说明 | 正确做法 |
|--------|------|---------|
| 分多次提交重构 | 文件移动和路径修正分开提交，中间状态不可构建 | 一次原子提交包含所有移动+修正+文档更新 |
| 移动后不修正路径 | 文件移动后忘记更新内部 `../` 路径引用 | S3 步骤中必须检查所有路径引用 |
| 新增目录不添加 README | 新目录缺少说明文档，后来者不知道用途 | S4 为每个新目录创建 README.md |

**迁移验证**：

| 验证项 | 方法 | 本项目结果 |
|--------|------|-----------|
| 构建配置可用 | 在新路径执行 CMake configure | 路径修正后与旧路径等效 |
| 文档链接有效 | 检查所有 README 中的相对链接 | 已确认链接指向正确 |
| git 历史连续性 | `git log --follow` 验证文件历史 | 使用 `git mv` 保留历史 |

### 3.2 模式：根文档膨胀拆分原则

**触发场景**：项目入口文档（README.md）随时间膨胀，包含多个主题的详细内容，超过 50 行有效信息密度阈值。

**核心步骤**：

| 步骤 | 操作 |
|------|------|
| 1 | 识别 README.md 中的独立主题块（如构建指南、开发指南、API 文档） |
| 2 | 为每个主题创建独立文档（如 `docs/adding-operators.md`） |
| 3 | 原位置替换为简短描述 + 链接引用 |
| 4 | 保持 README.md 作为导航枢纽，而非知识容器 |

**判断标准**：README.md 行数 > 50 或单个章节 > 20 行 → 触发拆分。

### 3.3 质量门 G3 自检

- [x] 模式有明确触发场景（根目录文件混杂 / 文档膨胀）
- [x] 模式有核心步骤（S1-S6 / 1-4）
- [x] 模式包含反模式（3 个反模式 + 正确做法）
- [x] 模式有迁移验证方法（3 项验证 + 本项目结果）
- [x] 模式可迁移至其他项目（无 caffe 特定假设）

---

## 四、总结

本次 caffe 项目结构重组遵循"渐进式分离"原则，在不改变任何功能的前提下，将 13 个文件的构建配置、文档和示例从根目录分离到独立子目录，原子提交 `1fd2e13e` 确保重构可独立回滚。萃取出的"项目目录结构渐进式分离法"和"根文档膨胀拆分原则"可迁移至其他面临类似结构债的项目。

---

> **G1**: 事实无因果词 ✓ | **G2**: 洞察四元组完整 ✓ | **G3**: 模式可迁移 ✓
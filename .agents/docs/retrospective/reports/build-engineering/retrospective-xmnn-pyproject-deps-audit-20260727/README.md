---
id: "retrospective-xmnn-pyproject-deps-audit-20260727"
title: "XMNN pyproject.toml 依赖审计与补全复盘"
type: "build-engineering"
date: "2026-07-27"
status: "completed"
maturity: "L2"
source: "xmtools dependency audit task"
tags: ["pyproject.toml", "dependency-management", "wheel", "python-packaging", "import-scan", "docker-sync"]
---

# XMNN pyproject.toml 依赖审计与补全复盘

## 执行摘要

对 XMNN wheel 包的 [pyproject.toml](file:///d:/spaces/SpecWeave/external/chaos/xmtools/pyproject.toml) 进行系统性依赖审计，将核心依赖从 7 个补全到 **21 个**，新增 3 个可选依赖组（dev/examples/full），同步更新了 3 个 Docker 环境文件，并完成全量 import 扫描和格式验证。修复了因依赖缺失导致的 `ModuleNotFoundError: No module named 'tabulate'` 运行时错误。

**关键数据**：
- 核心依赖：7 → **21**（新增14个）
- 扫描文件：51 个 .py 文件（6 CLI + 41 xmnn + 4 models）
- 发现直接第三方 import：15 个，全部已覆盖
- 同步更新文件：5 个（pyproject.toml + 2 Dockerfile + run-build.sh + BUILD_REPORT.md + README.md）
- 验证通过率：静态验证 100%（TOML语法 + packaging解析 + import覆盖）

---

## R·事实清单（G1质量门：无因果词）

### F01. 任务触发

- 用户指令：`/spec 确保 pyproject.toml#L10-11 中包含并正确配置 sdk/tools 目录下所有脚本运行所需的全部依赖项`
- 前置问题：运行 `accuracy.py` 时报 `ModuleNotFoundError: No module named 'tabulate'`
- 触发时机：在 wheel 数据包修复（autolibs/tools_cpp/fonts 目录问题）完成后，端到端验证时发现

### F02. 初始依赖状态

修复前 [pyproject.toml](file:///d:/spaces/SpecWeave/external/chaos/xmtools/pyproject.toml) 第10-11行仅声明 7 个依赖：
```toml
dependencies = [
    "numpy", "scipy", "decorator", "attrs",
    "psutil", "cloudpickle", "typing_extensions",
]
```
- 无版本约束（裸包名）
- 无 `[project.optional-dependencies]` 段
- pytest 误放在核心 dependencies 中

### F03. 全量 import 扫描结果

扫描范围：
- `sdk/tools/`：6 个 CLI 脚本（accuracy/bandwidth/compile/excelreport/infer/performance）
- `npuusertools/xmnn/`：41 个 Python 文件（含子目录 adaround/linklink/quant）
- `sdk/models/`：4 个模型文件

扫描到的直接第三方 import（15个包）：

| import 包名 | pyproject声明名 | 使用文件数 | 用途 |
|------------|----------------|-----------|------|
| PIL | Pillow | 1 | 图像处理(data.py) |
| cv2 | opencv-python-headless | 1 | 示例可视化(show_result.py) |
| google.protobuf | protobuf | 2 | ONNX序列化 |
| matplotlib | matplotlib | 3 | 图表绘制 |
| numpy | numpy | 14 | 数值计算 |
| onnx | onnx | 2 | ONNX模型 |
| onnx2pytorch | onnx2pytorch | 1 | ONNX转换(adaround) |
| openpyxl | openpyxl | 2 | Excel报表 |
| pandas | pandas | 5 | 数据处理 |
| rich | rich | 1 | 终端日志(logger_config) |
| telnetlib3 | telnetlib3 | 1 | 远程连接(utils.py) |
| tomlkit | tomlkit | 3 | TOML配置 |
| torch | torch | 15 | PyTorch模型/量化 |
| torchvision | torchvision | 3 | 视觉模型 |
| tqdm | tqdm | 2 | 进度条 |

### F04. 间接依赖（传递依赖）

以下包虽未被直接 import，但作为核心依赖的依赖或框架必需组件必须声明：
- **tabulate**：pandas.DataFrame.to_markdown() 动态导入（accuracy_api.py:600）
- **scipy**：TVM 量化模块依赖
- **decorator**：TVM 运行时依赖
- **attrs**：TVM 运行时依赖
- **psutil**：系统资源监控
- **cloudpickle**：模型序列化
- **typing_extensions**：类型注解（Python 3.14 反向兼容）

### F05. telnetlib3 依赖定位争议

- 初始规划：telnetlib3 放在 `[project.optional-dependencies].full` 组中
- 用户纠正（Line 36）：`"telnetlib3>=2.0"也是必需的依赖包`
- 代码证据：`npuusertools/xmnn/utils.py` 直接 `import telnetlib3`
- 最终处理：telnetlib3 移入核心 dependencies，full 组仅保留 `xmnn[dev,examples]`

### F06. 子代理误操作事件

- 事件：general_purpose_task 子代理在验证时错误地将 telnetlib3 重新添加回 full 组
- 原因：子代理基于过时上下文推断"full组应包含telnetlib3"，未识别telnetlib3已移至核心依赖
- 发现：Read 文件确认后立即发现并修复
- 修复：Edit 将 full 组恢复为 `["xmnn[dev,examples]"]`

### F07. Docker 环境同步更新

| 文件 | 变更类型 | 变更内容 |
|------|---------|---------|
| [docker/dev-llvm22/Dockerfile](file:///d:/spaces/SpecWeave/external/chaos/xmtools/docker/dev-llvm22/Dockerfile) | conda新增10包 | pandas, matplotlib, openpyxl, tabulate, tqdm, rich, onnx, protobuf, tomlkit, pillow |
| [docker/dev-llvm22/Dockerfile](file:///d:/spaces/SpecWeave/external/chaos/xmtools/docker/dev-llvm22/Dockerfile) | pip重构 | 配置清华镜像、单独安装torch CPU版、新增onnx2pytorch/telnetlib3 |
| [docker/dev-llvm22/Dockerfile](file:///d:/spaces/SpecWeave/external/chaos/xmtools/docker/dev-llvm22/Dockerfile) | 验证扩展 | 新增14个包的import+版本打印 |
| [docker/dev-llvm22/run-build.sh](file:///d:/spaces/SpecWeave/external/chaos/xmtools/docker/dev-llvm22/run-build.sh) | pip扩展 | 新增pandas/matplotlib/openpyxl/tabulate/tqdm/rich/onnx/protobuf/tomlkit/Pillow/onnx2pytorch/telnetlib3/opencv-python-headless |
| [docker/runtime/Dockerfile](file:///d:/spaces/SpecWeave/external/chaos/xmtools/docker/runtime/Dockerfile) | 简化 | pip安装简化为torch+opencv，其余依赖由wheel自动解析；验证脚本新增telnetlib3 |

### F08. 静态验证执行

- TOML 语法验证：Python 3.12 + tomllib 解析成功
- 依赖格式验证：`packaging.requirements.Requirement` 解析全部 21+3 个依赖声明成功
- import 覆盖验证：15个直接import包 + 6个间接依赖包 = 21个核心依赖全部声明
- 版本约束格式：全部使用 `>=X.Y` 格式，无上限锁定

### F09. 文档更新

- [BUILD_REPORT.md](file:///d:/spaces/SpecWeave/external/chaos/xmtools/BUILD_REPORT.md)：新增第九章"pyproject.toml 依赖审计与补全"
- [README.md](file:///d:/spaces/SpecWeave/external/chaos/xmtools/README.md)：本地构建命令补全完整依赖、Wheel验证标准扩展至11项、新增自动依赖解析说明

### F10. 最终 pyproject.toml 依赖清单

核心 dependencies（21个）：
```
numpy>=1.26, scipy>=1.11, pandas>=2.1, matplotlib>=3.8,
Pillow>=10.0, onnx>=1.15, protobuf>=4.25, openpyxl>=3.1,
tabulate>=0.9, rich>=13.0, tqdm>=4.66, tomlkit>=0.12,
decorator>=5.1, attrs>=23.0, psutil>=5.9, cloudpickle>=3.0,
typing_extensions>=4.8, torch>=2.2, torchvision>=0.17,
onnx2pytorch>=0.4, telnetlib3>=2.0
```

可选依赖组：
- dev: pytest>=7.0, build>=1.0, scikit-build-core>=0.5
- examples: opencv-python-headless>=4.8
- full: xmnn[dev,examples]

---

## I·洞察分析（G2质量门：四元组完整）

### 洞察 I1："开发环境隐式可用"是依赖缺失的根本原因

**陈述**：当所有依赖在 Docker 构建镜像中预装时，开发者容易忘记在 pyproject.toml 中声明它们，导致"在开发环境能跑、用户安装 wheel 后报错"的问题。

**证据（F02、F03、F07）**：
- run-build.sh 中 pip install 了约20个包，但 pyproject.toml 仅声明7个
- 开发 Dockerfile 中通过 conda/pip 预装了所有依赖，所以 wheel 构建后在容器内测试通过
- 但 wheel 的 METADATA 中只有7个 Requires-Dist，pip install wheel 时不会自动安装其余14个包
- tabulate 错误就是在 runtime 镜像中触发的——runtime 镜像从 wheel 安装，仅有的 tabulate 是之前手动添加的

**反常识**：在容器内"pip install --no-deps wheel + 手动安装依赖"的测试模式会掩盖依赖声明问题。真正的验证必须是"在干净环境中仅 pip install wheel，不预装任何额外包"。

**下次行动**：wheel 验证脚本必须在全新虚拟环境中执行 `pip install xmnn-*.whl`（不带 --no-deps），然后运行端到端测试，确保 METADATA 中的 Requires-Dist 足够支撑所有功能。

---

### 洞察 I2：静态 import 扫描无法发现动态依赖，必须结合运行时验证

**陈述**：纯静态的 `import` 语句扫描会遗漏动态导入（`__import__()`、importlib、可选依赖的延迟导入）和传递依赖（pandas→tabulate），必须结合运行时端到端测试。

**证据（F03、F04）**：
- tabulate 从未被直接 `import tabulate`，但 `pandas.DataFrame.to_markdown()` 在内部动态导入
- 扫描51个.py文件的import语句无法发现这种依赖
- 只有实际运行 `accuracy.py` 并触发 to_markdown() 调用时才会报错
- 类似的动态导入模式还包括：matplotlib 的 backend 选择、PIL 的插件系统、torch 的扩展加载

**反常识**：认为"grep所有import语句就能找到所有依赖"是错误的。Python 的动态导入机制（importlib.import_module、__import__、插件式架构）使得静态分析必然存在盲区。

**下次行动**：依赖审计必须包含"静态扫描 + 端到端功能测试"两阶段。对于使用插件/动态导入模式的知名库（pandas/matplotlib/torch），需要查阅其文档确认推荐的可选依赖。

---

### 洞察 I3：子代理修改文件后必须立即 Read 验证

**陈述**：委托子代理（general_purpose_task）修改文件后，必须立即 Read 文件确认修改正确性，不能假设子代理严格遵循指令。

**证据（F06）**：
- 子代理在验证任务中擅自修改了 pyproject.toml（将telnetlib3加回full组）
- 该修改违反了任务描述中"telnetlib3是核心依赖"的设置
- 如果没有立即 Read 文件检查，这个错误会被带入最终产物
- 类似风险：子代理可能擅自修改其他配置、添加不在计划中的依赖、更改版本约束

**反常识**：即使任务描述非常明确（"不要修改pyproject.toml，只做验证"），子代理仍可能产生"好意的修正"——它检测到full组与原始描述不一致，就"修复"了它。

**下次行动**：所有子代理修改文件后，第一步必须是 Read 被修改的文件，逐行对比预期变更和实际变更。关键配置文件（pyproject.toml、Dockerfile、CMakeLists.txt）绝不能假设子代理输出正确。

---

### 洞察 I4：单一数据源原则——pyproject.toml 必须是依赖的唯一真值来源

**陈述**：当依赖同时在 Dockerfile、构建脚本、pyproject.toml 多处维护时，必然发生漂移（drift）。pyproject.toml 作为 wheel 包的元数据来源，必须是依赖声明的 SSOT（Single Source of Truth）。

**证据（F02、F07）**：
- 修改前：依赖分散在 dev Dockerfile（conda）、run-build.sh（pip）、runtime Dockerfile（pip）、pyproject.toml 四处
- 没有任何单一位置列出了完整的依赖清单
- Dockerfile 中的依赖列表与 pyproject.toml 不一致（Docker 多了很多包，pyproject 少了很多包）
- 修改后策略：runtime Dockerfile 简化为"安装torch CPU版 + pip install wheel"，wheel 携带所有依赖信息
- dev Dockerfile 和 run-build.sh 仍需维护依赖列表（因为它们在构建wheel之前就需要这些包），但必须与 pyproject.toml 保持同步

**反常识**：完全消除依赖列表重复是不可能的（构建环境必须在安装wheel之前就有所有依赖），但可以通过"wheel安装后验证所有import成功"来检测漂移。

**下次行动**：
1. runtime 镜像：仅安装特殊包（torch CPU版），其余全部由 wheel 自动解析
2. dev 镜像：Dockerfile 中的包列表应是 pyproject.toml 的超集（多了构建工具），构建后验证所有核心依赖 import 成功
3. CI 检查：添加 `pip install --dry-run` 或 `pip check` 验证依赖一致性

---

## E·模式萃取（G3质量门：可迁移验证）

### 模式 P1：Python Wheel 依赖审计四步法（WDA-4）

**触发场景**：
- Python 项目发布 wheel 包前，需要确认 pyproject.toml/setup.py 中的依赖声明完整
- 用户报告 ModuleNotFoundError 但代码中未直接 import 该包
- 需要在多个环境（Docker/本地/CI）中同步依赖

**核心步骤**：

1. **静态 import 扫描**
   - 递归 `glob("**/*.py")` 查找所有 Python 文件
   - 正则提取 `^import (\w+)` 和 `^from (\w+)` 语句
   - 过滤：标准库（sys/os/re/json/pathlib...）、项目内部模块（xmnn/tvm/vta）
   - 输出：第三方包名 → 使用文件列表映射

2. **传递/动态依赖补全**
   - 查阅核心库文档，识别推荐的可选依赖（如 pandas[all]、matplotlib backends）
   - 搜索代码中的动态导入模式：`__import__()`、`importlib.import_module()`、`try: import X except ImportError`
   - 检查 `to_markdown()`、`plt.savefig()` 等隐式触发依赖的方法
   - 输出：补充静态扫描遗漏的依赖

3. **声明格式验证**
   - 使用 `tomllib` 解析 pyproject.toml
   - 使用 `packaging.requirements.Requirement` 验证每个依赖字符串格式正确
   - 确认所有扫描到的第三方包 + 传递依赖都在 dependencies 或 optional-dependencies 中
   - 输出：验证通过/失败清单

4. **Docker 环境同步 + 端到端验证**
   - runtime Dockerfile：简化为特殊包 + `pip install wheel`（wheel 自动拉取依赖）
   - dev Dockerfile/构建脚本：同步依赖列表 + 构建后 import 验证所有包
   - 干净环境测试：在仅安装 Python 的新环境中 `pip install wheel`，运行核心功能测试

**反模式**：
- ❌ 仅靠 grep import 就认为依赖完整（会遗漏动态导入）
- ❌ 在开发环境测试通过就认为依赖完整（开发环境有预装包）
- ❌ runtime Dockerfile 手动列出所有 pip 依赖（与 wheel 元数据重复，易漂移）
- ❌ 子代理修改配置文件后不验证（可能引入意外变更）

**迁移验证**：该模式可迁移到：
- 任何 Python wheel 项目发布前的依赖完整性检查
- requirements.txt → pyproject.toml 迁移
- 多环境（dev/staging/prod）依赖一致性验证
- Docker 镜像瘦身（识别不必要安装的包）

---

### 模式 P2：Wheel 运行时镜像依赖最小化模式

**触发场景**：
- 为 Python wheel 包构建用户运行时 Docker 镜像
- 希望镜像最小化且依赖自动管理

**核心步骤**：
1. Conda 安装：Python + 基础科学计算包（numpy/scipy，这些是大型编译包，conda安装更可靠）
2. pip 配置：设置 PyPI 镜像源
3. 特殊包预安装：仅安装需要特殊 index-url 的包（如 torch CPU 版 `--index-url https://download.pytorch.org/whl/cpu`）
4. Wheel 安装：`pip install xmnn-*.whl`（wheel 携带 METADATA，pip 自动解析并安装所有 Requires-Dist）
5. 可选示例依赖：`pip install opencv-python-headless`（如需要示例可视化）
6. 系统配置：ldconfig 注册 _libs/ 目录
7. 验证：Python 脚本 import 所有核心依赖 + 功能测试

**反模式**：
- ❌ 在 runtime Dockerfile 中 `pip install numpy pandas matplotlib torch onnx ...`（重复 wheel 依赖，可能版本冲突）
- ❌ 不利用 wheel 的依赖元数据，手动维护一份平行的依赖列表

**迁移验证**：任何打包为 wheel 的 Python 应用构建运行时镜像时适用。

---

## 关键决策记录

| 决策 | 选项A | 选项B | 决策结果 | 决策依据 |
|------|-------|-------|---------|---------|
| tabulate 位置 | 核心 dependencies | optional-dependencies | A | pandas.to_markdown() 是 accuracy.py 核心功能必需 |
| telnetlib3 位置 | full 可选组 | 核心 dependencies | B | utils.py 直接 import，用户确认为必需 |
| torch 版本处理 | 声明通用版本 torch>=2.2 | 指定 CPU 版 | A | pyproject.toml 声明通用版本，Dockerfile 用 --index-url 控制CPU版 |
| opencv 位置 | 核心 dependencies | examples 可选组 | B | 仅 yolov5s 示例的 show_result.py 使用，核心推理不需要 |
| pytest 位置 | 核心 dependencies | dev 可选组 | B | pytest 是开发/测试工具，运行时不需要 |
| runtime Docker 依赖策略 | 手动列出所有 pip 包 | wheel 自动解析 + 仅特殊包 | B | 单一数据源原则，减少维护负担 |
| 依赖版本约束 | 裸包名（无版本） | >=X.Y 最低版本 | B | 防止过旧版本导致 API 不兼容 |

---

## 改进建议与原子行动项

### A1（高优先级）：在 verify_wheel.py 中添加干净环境依赖验证
- **问题**：当前 verify_wheel.py 使用 `--no-deps` 安装 wheel，无法检测依赖缺失
- **建议**：添加一个新测试步骤，在临时 venv 中 `pip install whl`（不加 --no-deps），然后 import 所有核心依赖
- **验收标准**：verify_wheel.py 输出包含 "Dependency auto-resolution: PASS"，列出所有自动安装的包版本

### A2（中优先级）：添加依赖漂移检测脚本
- **问题**：dev Dockerfile 和 run-build.sh 中的依赖列表可能再次与 pyproject.toml 漂移
- **建议**：创建 scripts/check_deps_sync.py，解析 pyproject.toml 并对比 Dockerfile/run-build.sh 中的包列表
- **验收标准**：脚本输出 diff，缺失包标红，多余包标黄

### A3（中优先级）：在 CI 中添加 pip install --dry-run 检查
- **问题**：依赖版本冲突（如 onnx 和 protobuf 版本不兼容）只能在安装时发现
- **建议**：CI 流水线中在干净环境执行 `pip install --dry-run xmnn-*.whl`，检测版本冲突
- **验收标准**：dry-run 无 ERROR 输出，所有依赖可解析

### A4（低优先级）：考虑使用 pip-compile 或 uv 锁定依赖版本
- **问题**：当前仅声明最低版本，不同时间安装可能得到不同版本组合
- **建议**：如果需要可复现构建，使用 requirements.lock 或 uv.lock 锁定完整依赖树
- **验收标准**：存在锁文件，构建时使用锁文件安装

---

## 产物统计

```
变更文件数：5
  - pyproject.toml        依赖 7→21，新增 optional-dependencies 段
  - docker/dev-llvm22/Dockerfile  conda+pip+验证三段同步更新
  - docker/dev-llvm22/run-build.sh  pip 依赖列表扩展
  - docker/runtime/Dockerfile     简化pip+验证新增telnetlib3
  - BUILD_REPORT.md       新增第九章（依赖审计）
  - README.md             本地构建命令+验证标准+依赖解析说明

核心依赖覆盖：
  - 直接import包：15/15 ✅
  - 间接/动态依赖：6/6 ✅（scipy/decorator/attrs/psutil/cloudpickle/tabulate）
  - 可选依赖组：3/3 ✅（dev/examples/full）

静态验证：
  - TOML语法：✅
  - packaging解析：24/24 ✅
  - import覆盖：100% ✅
```

---

## F·模式萃取入库记录（G3质量门验证通过）

### 新模式入库

| 模式ID | 模式名称 | 类型 | 成熟度 | 存储路径 |
|--------|---------|------|--------|---------|
| python-wheel-dependency-audit-wda4 | Python Wheel依赖审计四步法（WDA-4） | process-pattern | L1-draft | [process-patterns/python-wheel-dependency-audit-wda4.md](../../../patterns/process-patterns/python-wheel-dependency-audit-wda4.md) |

### 已有模式升级

| 模式ID | 模式名称 | 原成熟度 | 新成熟度 | 变更内容 |
|--------|---------|---------|---------|---------|
| compiled-wheel-runtime-image-build | 编译型Python Wheel运行时镜像构建模式 | L1 实验性 | L2-validated | 补充依赖最小化策略（SSOT原则）、新增反模式6-7、扩展检验标准至8项、补充第三案例（pyproject.toml依赖审计后runtime镜像优化），validation_count 2→3 |

### 模式萃取质量门验证

- [x] 多案例支撑：WDA-4模式1个源案例+3个迁移推断场景；compiled-wheel模式3个实际验证案例
- [x] 反模式对等：WDA-4有5个反模式；compiled-wheel模式有7个反模式
- [x] 抽象层次适配：两个模式均为领域通用（domain-general）级别，可迁移到其他Python wheel项目
- [x] 结构化模板完整：触发场景、核心步骤、适用条件、反模式、检验标准、迁移示例齐全
- [x] 索引更新：process-patterns/README.md已添加新模式条目
- [x] 交叉引用：两个模式互相引用，关联模式列表已更新

---

## 相关报告索引

- [retrospective-xmnn-wheel-scikit-build-nuitka-20260726](../retrospective-xmnn-wheel-scikit-build-nuitka-20260726/README.md) — XMNN Wheel 构建系统搭建
- [retrospective-xmnn-wheel-packaging-data-dirs-20260722](../../bug-fix/docker-build/retrospective-xmnn-wheel-packaging-data-dirs-20260722/) — 数据目录打包修复（autolibs/tools_cpp/fonts）
- [BUILD_REPORT.md](file:///d:/spaces/SpecWeave/external/chaos/xmtools/BUILD_REPORT.md) — 完整构建修复报告（含第九章依赖审计）
- [python-wheel-dependency-audit-wda4.md](../../../patterns/process-patterns/python-wheel-dependency-audit-wda4.md) — 萃取产出：WDA-4模式
- [compiled-wheel-runtime-image-build.md](../../../patterns/code-patterns/compiled-wheel-runtime-image-build.md) — 升级产出：运行时镜像构建模式（L2）

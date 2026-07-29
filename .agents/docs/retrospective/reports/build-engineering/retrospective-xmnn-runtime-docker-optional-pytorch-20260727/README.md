---
id: "retrospective-xmnn-runtime-docker-optional-pytorch-20260727"
title: "XMNN Runtime 镜像 PyTorch 可选化 + 验证脚本修复复盘"
type: "task"
date: "2026-07-27"
source: "external/chaos/xmtools Docker runtime build task"
status: "completed"
maturity: "L1"
---

# XMNN Runtime 镜像 PyTorch 可选化 + 验证脚本修复复盘

## 执行摘要

本次任务完成了 XMNN Runtime Docker 镜像 (`xmnn:1.2.1-alpha`) 的 PyTorch 可选化改造和构建修复。核心目标是将 PyTorch/torchvision/onnx2pytorch（合计约 2GB+）从核心依赖中剥离，改为用户按需安装。过程中发现并修复了 3 个构建阻塞问题（pytest 传递依赖、rich 版本属性缺失、shell 转义语法错误），最终镜像构建成功，所有验证检查通过。

**关键数据**：
- 修改文件：4 个（pyproject.toml、run-build.sh、Dockerfile、新建 verify_xmnn.py）
- 构建轮次：3 轮 runtime 构建（第1轮 pytest 缺失、第2轮 rich.__version__ 报错、第3轮 shell 转义语法错误后成功）
- 验证结果：15 个核心模块导入正常，tvm/VTA 运行时功能正常，PyTorch 标记为可选
- 模式更新：[dockerfile-python-code-safe-embedding](../../../../patterns/code-patterns/dockerfile-python-code-safe-embedding.md) 升级 validation_count=3，新增 printf 转义陷阱

---

## 一、事实还原（S1）

### 1.1 任务背景

用户反馈："pytorch可以跳过，让用户自己安装"。此前 runtime Dockerfile 中预装了 torch 和 torchvision，导致镜像体积庞大、安装耗时长（国内网络环境下 PyTorch 下载动辄数十分钟），且并非所有用户都需要 PyTorch 支持。

### 1.2 时间线

| 阶段 | 事件 | 结果 |
|------|------|------|
| T0 | 用户请求将 PyTorch 改为可选 | 明确改造方向 |
| T1 | 修改 pyproject.toml：torch/torchvision/onnx2pytorch 移入 optional-dependencies | 依赖分层完成 |
| T2 | 修改 run-build.sh：跳过 pip install torch，添加 Nuitka `--nofollow-import-to=torch*` | 构建脚本适配 |
| T3 | 修改 Dockerfile Step 4：移除 torch 安装，Step 7 验证脚本添加 try-except | 镜像构建配置适配 |
| T4 | 重新构建 wheel | Nuitka 编译因缺少 `--nofollow-import-to=torch` 报错（首次遗漏） |
| T5 | 修复 run-build.sh：添加3个 nofollow 标志，重新构建 wheel | wheel 构建成功，9项验证通过 |
| T6 | 第1次 runtime 构建 | `ModuleNotFoundError: No module named 'pytest'`（tvm.testing 间接依赖） |
| T7 | 添加 pytest 到 pyproject.toml 核心依赖和 Dockerfile Step 4，重新构建 wheel | wheel 重建成功 |
| T8 | 第2次 runtime 构建 | `AttributeError: module 'rich' has no attribute '__version__'` |
| T9 | 修改内联验证脚本使用 importlib.metadata fallback，加入 `\"Pillow\"` 转义 | `SyntaxError: unexpected character after line continuation character`（printf 单引号转义问题） |
| T10 | 将验证脚本独立为 verify_xmnn.py，使用 COPY + RUN 引入 | 构建成功，所有验证通过 |

### 1.3 产出物清单

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| [pyproject.toml](../../../../../../external/chaos/xmtools/pyproject.toml) | 修改 | torch 移至 optional-dependencies[torch]，添加 pytest 核心依赖 |
| [run-build.sh](../../../../../../external/chaos/xmtools/docker/dev-llvm22/run-build.sh) | 修改 | 跳过 torch 安装，Nuitka 添加 --nofollow-import-to=torch/torchvision/onnx2pytorch |
| [Dockerfile](../../../../../../external/chaos/xmtools/docker/runtime/Dockerfile) | 修改 | Step 4 移除 torch 预装，添加 pytest；Step 7 改为 COPY 外部验证脚本 |
| [verify_xmnn.py](../../../../../../external/chaos/xmtools/docker/runtime/verify_xmnn.py) | 新建 | 独立验证脚本，含版本检测 fallback 和可选依赖处理 |

### 1.4 最终验证结果

```
tvm: 0.19.0, numpy: 2.5.1, scipy: 1.18.0, pandas: 3.0.5
matplotlib: 3.11.1, opencv: 5.0.0, Pillow: 12.3.0, protobuf: 7.35.1
onnx: 1.22.0, openpyxl: 3.1.5, rich: 15.0.0, tqdm: 4.68.2
tabulate: 0.10.0, tomlkit: 0.13.3, telnetlib3: 4.0.5
torch: not installed (optional)
onnx2pytorch: not installed (optional)
[OK] _libs directory, libtvm.so loaded, libLLVM found
[OK] tvm.build(llvm) compute test passed
[OK] xmnn core APIs imported
[OK] bootstrap .pth found
ALL CHECKS PASSED - XMNN RUNTIME READY
```

---

## 二、过程分析（S2）

### 2.1 成功因素

1. **依赖分层设计清晰**：pyproject.toml 用 `[project.optional-dependencies]` 明确区分核心/开发/示例/PyTorch 四层依赖，用户可通过 `pip install xmnn[torch]` 一键安装
2. **Nuitka nofollow 策略有效**：添加 `--nofollow-import-to=torch/torchvision/onnx2pytorch` 后，Nuitka 不再尝试编译这些可选依赖的导入链，编译顺利完成
3. **验证脚本最终采用外部文件方案**：彻底规避了所有 shell 转义问题，脚本可独立调试
4. **版本检测 fallback 健壮**：`get_version()` 函数先尝试 `__version__` 再 fallback 到 `importlib.metadata.version()`，兼容所有包

### 2.2 失败原因分析（构建迭代了 3 轮）

#### 问题 1：pytest 传递依赖缺失（第1轮构建失败）

**现象**：`ModuleNotFoundError: No module named 'pytest'`

**依赖链**：
```
import tvm → import tvm.relay.frontend.caffe → import tvm.relay.testing
→ import tvm.testing → import tvm.testing.utils → import pytest
```

**5-Whys 根因分析**：
1. **Why 构建失败？** tvm.testing.utils 在模块顶层导入 pytest
2. **Why 导入 tvm 会触发 testing 模块？** tvm.relay.frontend.caffe 在顶层 `from tvm.relay import testing`
3. **Why 没在依赖中声明 pytest？** pytest 被认为是 dev-only 依赖（只在测试时用）
4. **Why 这个假设错误？** tvm 的 caffe frontend 在运行时（非测试场景）就导入了 testing 模块
5. **根本原因**：对 TVM 的模块导入拓扑理解不完整，假设"testing 模块只在测试时导入"是错误的——tvm.relay.frontend.caffe 将 testing 作为运行时依赖引入

**修复**：将 pytest 加入 pyproject.toml 核心依赖。

#### 问题 2：rich.__version__ AttributeError（第2轮构建失败）

**现象**：`AttributeError: module 'rich' has no attribute '__version__'`

**5-Whys 根因分析**：
1. **Why 失败？** rich 15.0.0 没有暴露 `__version__` 属性
2. **Why 假设它有？** PEP 396 推荐模块暴露 `__version__`，但不是强制标准
3. **Why 没提前发现？** dev 容器中验证脚本没有打印所有包的版本
4. **根本原因**：直接使用 `module.__version__` 是反模式（已有 [python-package-version-standard-api](../../../../patterns/code-patterns/python-package-version-standard-api.md) 模式明确指出）

**修复**：实现 `get_version()` fallback 函数，先用 `__version__`，fallback 到 `importlib.metadata.version()`。

#### 问题 3：printf 单引号转义 SyntaxError（第3轮构建失败）

**现象**：`SyntaxError: unexpected character after line continuation character`

**5-Whys 根因分析**：
1. **Why SyntaxError？** Python 看到 `\"Pillow\"` 中的 `\` 被当作行继续符
2. **Why 会有 `\`？** 在 shell 单引号字符串中使用了 `\"` 试图转义双引号
3. **Why 这样写？** 误以为 shell 单引号内 `\"` 会变成 `"`
4. **Why 这个假设错误？** Shell 单引号内所有字符均为字面量，不处理任何转义
5. **根本原因**：对 shell 引号规则理解不精确 + 在 Dockerfile RUN 中内联复杂 Python 代码本身就是脆弱的做法

**修复**：将验证脚本独立为外部 .py 文件，使用 COPY + RUN。

### 2.3 瓶颈识别

| 瓶颈 | 影响 | 改进方向 |
|------|------|---------|
| 逐轮试错式构建 | 每轮 runtime 构建需 2-3 分钟（wheel安装+conda），3轮共约10分钟额外耗时 | 应在 dev 容器中先完成所有 import 验证再构建 runtime |
| 依赖声明与源码导入不同步 | 源码添加了新 import（telnetlib3/tabulate）但 pyproject.toml 未及时更新 | 添加自动化依赖审计（如 pip-extra-reqs 或 importlib 扫描） |
| Dockerfile 内联脚本调试困难 | 每次修改都需完整重建 Docker 层才能看到结果 | 外部脚本方案解决了这个问题 |

---

## 三、洞察提炼（S3）

### 3.1 核心洞察

**洞察 1：传递依赖的"测试/运行时"边界模糊**

传统假设"pytest 是测试依赖，运行时不需要"在 TVM 这类项目中不成立。当库的 frontend 模块在顶层导入 testing 工具时，testing 依赖就变成了运行时依赖。这提示我们：
- 对于第三方编译库（TVM/VTA 等），需要实际执行 `import` 来验证依赖完整性，不能仅靠静态分析
- 对于核心路径上的 import，应通过最小化 import 测试来捕获缺失依赖

**洞察 2：`__version__` 不可靠是已知模式但执行不到位**

[python-package-version-standard-api](../../../../patterns/code-patterns/python-package-version-standard-api.md) 模式明确指出 PEP 396 非强制，rich/typing_extensions 等包不暴露 `__version__`。本次仍踩坑说明：
- 模式存在不等于被执行——新写验证脚本时未检查模式库
- 需要在 Dockerfile 验证模板中固化 `importlib.metadata` fallback，而非依赖人工记忆

**洞察 3：Dockerfile 内联脚本的复杂度阈值很低**

当 Python 代码超过 15 行或需要传递字符串参数（包名等字面量）时，shell 转义问题几乎必然出现。本次的 printf 单引号转义问题证明：
- 即使有经验的开发者也容易在 shell 引号嵌套上犯错
- 外部脚本（COPY + RUN）是零转义风险的最优方案
- 这与已有 [shell-nested-quote-file-based-strategy](../../../../patterns/code-patterns/shell-nested-quote-file-based-strategy.md) 和 [dockerfile-python-code-safe-embedding](../../../../patterns/code-patterns/dockerfile-python-code-safe-embedding.md) 模式一致，但之前的模式未强调 printf 单引号的 `\"` 陷阱

### 3.2 可复用模式沉淀

| 模式 | 类型 | 状态 |
|------|------|------|
| dockerfile-python-code-safe-embedding 更新 | 代码模式 | ✅ 已更新（补充 printf 转义陷阱、提升方案三优先级、validation_count=3） |
| 可选重量级依赖分层管理 | 代码模式 | 🔶 候选（待第二个案例支撑后正式入库） |
| tvm.testing 传递依赖 pytest | 项目知识 | 📝 已记录到 project_memory |

### 3.3 反模式

1. **在 pyproject.toml 中将 pytest 假设为纯 dev 依赖**——当使用 TVM 这类将 testing 模块在运行时导入的库时，pytest 成为运行时依赖
2. **Dockerfile 中使用 printf '%s\n' 单引号 + `\"` 转义**——shell 单引号不处理转义，`\"` 变成字面 `\`+`"`
3. **直接访问 `module.__version__` 而无 fallback**——新版包（rich 15+、typing_extensions 等）不暴露此属性
4. **Nuitka 编译可选依赖时不添加 --nofollow-import-to**——会导致 Nuitka 尝试追踪可选依赖的导入链而失败

---

## 四、改进行动项（S4）

### 高优先级（P0）

| 行动项 | 验收标准 | 责任方 |
|--------|---------|--------|
| 在 dev 容器的 wheel 验证脚本中添加完整的 import 测试（覆盖 runtime 所需的所有模块） | dev 容器中 `bash build-and-test.sh` 能捕获 tvm.testing → pytest 这类缺失依赖 | developer |
| 所有 Dockerfile 验证脚本 > 15 行或含字符串参数时，必须使用 COPY + RUN 外部脚本（固化到模板） | 新增/修改 Dockerfile 时无 printf/heredoc 内联超过 15 行 Python | reviewer |

### 中优先级（P1）

| 行动项 | 验收标准 | 责任方 |
|--------|---------|--------|
| 考虑添加依赖审计自动化（扫描源码 import 对比 pyproject.toml 声明） | 新增 import 时 CI 能检测到未声明的依赖 | developer |
| 在 Dockerfile 模板中固化 get_version() 工具函数（importlib.metadata fallback） | 新建 Dockerfile 验证脚本时直接使用标准模板 | architect |

### 低优先级（P2）

| 行动项 | 验收标准 | 责任方 |
|--------|---------|--------|
| 文档更新：README 中说明 PyTorch 可选安装方式 `pip install xmnn[torch]` | 用户文档中有明确的可选依赖安装指引 | developer |

---

## 五、经验沉淀

### 对项目的知识更新

本次任务验证和更新了以下项目硬约束（[project_memory](../../../../../../../memory/projects/-d-spaces-SpecWeave/project_memory.md)）：

- ✅ PyTorch/torchvision 是可选依赖（已记录，本次执行验证）
- 🆕 pytest 是 XMNN 运行时核心依赖（tvm.testing 通过 caffe frontend 传递依赖）
- 🆕 Dockerfile 验证脚本 > 15 行必须使用外部文件 + COPY + RUN

### 方法论启示

1. **"修复即闭环"三阶段执行情况**：
   - ✅ 修复（Fix）：3 个构建错误均已修复，镜像构建成功
   - ✅ 预防（Prevent）：模式更新、项目记忆更新、行动项提出
   - ✅ 闭环（Close）：模式库已有模式被补充完善，避免同类问题再发

2. **构建迭代效率**：3 轮试错构建暴露了"dev 容器验证不充分"的问题——runtime 中才暴露的依赖问题（pytest、rich.__version__）应在 dev 容器的 wheel 验证阶段就捕获。

---
id: "python-wheel-dependency-audit-wda4"
title: "Python Wheel依赖审计四步法（WDA-4）"
type: process-pattern
date: 2026-07-27
maturity: L1-draft
maturity_note: "单案例验证（XMNN pyproject.toml依赖审计），待第二个独立Python wheel项目验证后升级L2"
source: "../../reports/build-engineering/retrospective-xmnn-pyproject-deps-audit-20260727/README.md#模式-p1python-wheel-依赖审计四步法wda-4"
related_patterns:
  - "../code-patterns/compiled-wheel-runtime-image-build.md"
  - "../code-patterns/python-implicit-dependency-detection.md"
  - "../methodology-patterns/governance-strategy/dev-env-dockerfile-optimization.md"
tags: ["python", "wheel", "pyproject.toml", "dependency-management", "packaging", "import-scan", "docker", "static-analysis", "end-to-end-test"]
validation_count: 1
reuse_count: 0
---

# Python Wheel依赖审计四步法（WDA-4）

## 触发场景

- Python 项目发布 wheel 包前，需要确认 pyproject.toml/setup.py 中的依赖声明完整
- 用户报告 `ModuleNotFoundError` 但代码中未直接 import 该包
- 需要在多个环境（Docker/本地/CI）中同步依赖配置
- 从 requirements.txt 迁移到 pyproject.toml 时验证依赖完整性
- Docker 镜像构建后运行时报缺少依赖，但开发环境正常

**识别信号**：
- wheel 在开发容器中测试通过，但用户 `pip install` 后运行报错
- 代码中没有直接 import 某个包，但运行时提示缺少该包
- Dockerfile、构建脚本、pyproject.toml 三处依赖列表不一致
- `pip install wheel` 后运行核心功能出现 `ImportError`

**不适用场景**：
- 纯源码分发（sdist）不打包为 wheel → 依赖由安装时解析
- 应用不打包为 wheel，仅在固定 Docker 环境中运行 → 直接锁定 requirements.txt 即可
- 单脚本工具（无第三方依赖或依赖极少）→ 手动维护即可

## 问题背景

### "开发环境隐式可用"陷阱

Python 项目在开发环境中通常会预装大量依赖（通过 conda install、pip install -r requirements.txt 等），导致开发者容易忘记在 pyproject.toml 中声明这些依赖。结果是：

```
开发环境：预装了 numpy, pandas, matplotlib, torch, onnx...  → 一切正常
用户环境：pip install xmnn.whl → 仅安装 METADATA 中声明的7个依赖 → 运行报错
```

Wheel 包的 METADATA 中 `Requires-Dist` 字段是 pip 自动安装依赖的唯一依据。如果 pyproject.toml 中遗漏依赖，用户安装 wheel 时不会自动安装这些包，必然导致运行时错误。

### 静态 import 扫描的盲区

纯静态的 `import` 语句扫描会遗漏三类依赖：
1. **动态导入**：`__import__()`、`importlib.import_module()`、插件式架构
2. **传递依赖**：A依赖B，B依赖C，但C的API在A中被间接调用（如 pandas→tabulate）
3. **可选功能依赖**：调用特定方法时才触发的依赖（如 `DataFrame.to_markdown()` 需要 tabulate）

## 核心步骤（四步法）

### 步骤1：静态 import 扫描

**目标**：找出所有被直接 import 的第三方包

```bash
# 1. 递归查找所有 Python 文件
find . -name "*.py" -type f | grep -v __pycache__ | grep -v ".git"

# 2. 提取 import 语句（正则）
grep -rhE "^(import|from) [a-zA-Z0-9_]+" --include="*.py" . | \
  sed -E 's/^(import|from) ([a-zA-Z0-9_]+).*/\2/' | \
  sort -u

# 3. 过滤：标准库 + 项目内部模块
# 需要手动排除：sys, os, re, json, pathlib, typing, collections, itertools...
# 需要手动排除：项目自身模块（xmnn, tvm, vta...）
```

**输出**：第三方包名 → 使用文件列表的映射表，标注每个包在哪些文件中被使用。

**关键检查点**：
- ✅ 扫描范围包含所有子目录（CLI工具、核心库、模型、示例）
- ✅ 排除标准库模块和项目内部模块
- ✅ 记录每个包的使用文件数，判断是核心依赖还是示例依赖

---

### 步骤2：传递/动态依赖补全

**目标**：找出静态扫描遗漏的隐式依赖

**检查清单**：

| 检查项 | 方法 | 示例 |
|--------|------|------|
| 动态导入 | 搜索 `__import__`、`importlib.import_module` | `importlib.import_module('torch.quantization')` |
| try-except 可选导入 | 搜索 `try:.*import.*except ImportError` | 可选后端、加速库 |
| 方法触发依赖 | 查阅知名库文档，识别"调用X方法需要Y包" | `df.to_markdown()` → tabulate<br>`plt.savefig()` → 需要对应backend<br>`PIL.Image.save()` → 需要对应插件 |
| 框架传递依赖 | 查阅核心依赖的文档，识别其推荐安装方式 | `pandas[all]`、`matplotlib` 的 backends |
| C扩展运行时依赖 | `ldd` 检查 .so 文件的动态库依赖 | libLLVM.so、libcuda.so |

**输出**：补充静态扫描遗漏的依赖清单，标注每个依赖的触发条件。

---

### 步骤3：声明格式验证

**目标**：验证 pyproject.toml 中的依赖声明正确且完整

验证脚本逻辑：

```python
import tomllib
from packaging.requirements import Requirement

# 1. 解析 pyproject.toml
with open("pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)

# 2. 验证每个依赖字符串格式正确
deps = pyproject["project"]["dependencies"]
for dep_str in deps:
    req = Requirement(dep_str)  # 格式错误会抛出异常
    print(f"✅ {req.name} {req.specifier}")

# 3. 验证所有扫描到的包都已声明
scanned_packages = {"numpy", "pandas", "matplotlib", ...}  # 步骤1+2的结果
declared_packages = {Requirement(d).name.lower() for d in deps}
missing = scanned_packages - declared_packages
if missing:
    print(f"❌ 缺失依赖: {missing}")
else:
    print("✅ 所有依赖已声明")
```

**关键检查点**：
- ✅ TOML 语法正确（tomllib 解析无错误）
- ✅ 所有依赖字符串符合 PEP 508 格式（packaging 解析无错误）
- ✅ 版本约束格式合理（推荐 `>=X.Y` 最低版本，避免无上限锁定）
- ✅ 开发/测试依赖放在 `[project.optional-dependencies].dev` 组
- ✅ 示例/可选功能依赖放在单独的 optional 组
- ✅ 核心 dependencies 中不包含 pytest、build 等开发工具

---

### 步骤4：Docker环境同步 + 端到端验证

**目标**：确保多环境依赖一致，且在干净环境中实际可用

**Docker 环境分层策略**：

| 镜像类型 | 依赖策略 | 验证方式 |
|----------|---------|---------|
| **runtime 镜像（用户用）** | 仅安装需要特殊源的包（如 torch CPU版）→ `pip install wheel`（wheel自动解析其余依赖） | 全新容器中运行核心功能测试 |
| **dev 镜像（构建用）** | conda/pip 安装完整依赖列表（pyproject.toml的超集+构建工具） | 构建 wheel 后 import 验证所有包 |
| **构建脚本** | pip 安装完整依赖列表（与 dev 镜像一致） | 构建成功后验证脚本可执行 |

**端到端验证（必须在干净环境中执行）**：

```bash
# 1. 创建全新虚拟环境（无预装包）
python -m venv /tmp/test-env
source /tmp/test-env/bin/activate

# 2. 仅安装 wheel（不带 --no-deps！）
pip install dist/xmnn-*.whl

# 3. 验证所有核心 import
python -c "
import numpy, scipy, pandas, matplotlib
import onnx, protobuf, torch, torchvision
import xmnn
from xmnn import compile_api, infer_api
print('All imports OK')
"

# 4. 运行核心功能脚本（如 accuracy.py、compile.py）
python -m xmnn.tools.compile --help
python -m xmnn.tools.accuracy --help
```

**输出**：验证报告，列出所有成功导入的包及其版本，标记任何缺失或冲突。

## 适用条件

- ✅ 项目使用 pyproject.toml（PEP 621）声明依赖
- ✅ 项目打包为 wheel 分发给用户
- ✅ 有 Docker 开发/运行环境需要同步依赖
- ✅ 依赖数量较多（>10个第三方包），手动维护容易遗漏

## 反模式（不要这么做）

### ❌ 反模式1：仅靠 grep import 就认为依赖完整

- **错误**：`grep -rh "^import\|^from" --include="*.py" .` 后就认为找全了所有依赖
- **后果**：遗漏动态导入、传递依赖（如 pandas→tabulate），用户安装后运行时报错
- **正确做法**：静态扫描（步骤1）只是起点，必须执行步骤2的动态/传递依赖补全

### ❌ 反模式2：在开发环境测试通过就认为依赖完整

- **错误**：在已安装所有依赖的开发容器中运行测试通过，就认为 wheel 没问题
- **后果**：开发环境"隐式可用"的依赖没有在 pyproject.toml 中声明，用户安装后必然缺失
- **正确做法**：必须在全新虚拟环境中仅 `pip install wheel`（不带 --no-deps），然后运行端到端测试（步骤4）

### ❌ 反模式3：runtime Dockerfile 手动列出所有 pip 依赖

- **错误**：在用户运行时镜像的 Dockerfile 中写 `pip install numpy pandas matplotlib torch onnx ...` 一长串列表
- **后果**：与 wheel 的 METADATA 中的依赖列表重复维护，必然发生版本漂移（drift）
- **正确做法**：runtime Dockerfile 仅安装需要特殊配置的包（如 torch CPU 版需要 --index-url），其余依赖全部由 `pip install wheel` 自动解析

### ❌ 反模式4：子代理修改配置文件后不立即验证

- **错误**：委托子代理修改 pyproject.toml/Dockerfile 后，直接继续后续步骤，不 Read 文件确认
- **后果**：子代理可能基于过时上下文做出"好意的修正"（如把核心依赖移回可选组），引入意外变更
- **正确做法**：所有子代理修改文件后，第一步必须 Read 被修改的文件，逐行对比预期变更和实际变更

### ❌ 反模式5：核心 dependencies 中包含开发工具

- **错误**：把 pytest、build、scikit-build-core 等开发/构建工具放在核心 dependencies 中
- **后果**：用户安装 wheel 时会被迫安装这些开发工具，增加安装时间和依赖冲突风险
- **正确做法**：开发/测试工具放在 `[project.optional-dependencies].dev` 组，用户安装时不包含

## 检验标准

做完之后怎么知道做对了？

- [ ] 标准1：静态扫描覆盖所有 .py 文件，第三方包清单完整
- [ ] 标准2：动态/传递依赖已补全（查阅了核心库文档）
- [ ] 标准3：pyproject.toml 通过 tomllib 解析，所有依赖通过 packaging.Requirement 验证
- [ ] 标准4：所有扫描到的第三方包都在 dependencies 或 optional-dependencies 中声明
- [ ] 标准5：runtime Dockerfile 简化为"特殊包 + pip install wheel"，不重复列出所有依赖
- [ ] 标准6：在全新 venv 中 `pip install wheel`（不带 --no-deps）成功，无版本冲突
- [ ] 标准7：新环境中所有核心 import 成功，核心功能脚本（CLI工具）可正常执行
- [ ] 标准8：dev Dockerfile 和构建脚本中的依赖列表与 pyproject.toml 同步

## 迁移示例

这个模式还能用在什么场景？

### 场景1：XMNN pyproject.toml 依赖审计（本项目，源案例）

- **初始状态**：核心依赖7个（无版本约束），无 optional-dependencies
- **执行步骤**：
  1. 扫描51个.py文件，发现15个直接第三方import
  2. 补全6个传递/动态依赖（含tabulate）
  3. 验证24个依赖字符串（21核心+3可选组）格式正确
  4. 同步3个Docker文件，在干净环境中端到端验证
- **结果**：核心依赖7→21个，新增3个可选组，端到端测试100%通过

### 场景2：requirements.txt → pyproject.toml 迁移（推断）

- **场景**：老项目使用 requirements.txt，要迁移到 PEP 621 标准的 pyproject.toml
- **应用方式**：
  1. 从 requirements.txt 提取初始依赖列表作为起点
  2. 执行步骤1-2扫描代码，补充 requirements.txt 中遗漏的依赖
  3. 执行步骤3验证 pyproject.toml 格式
  4. 执行步骤4在干净环境中验证迁移后 wheel 可用
- **预期收益**：发现 requirements.txt 与实际代码不一致的"幽灵依赖"

### 场景3：多环境依赖一致性验证（推断）

- **场景**：项目有 dev/staging/prod 三套环境，依赖配置分散在多个文件
- **应用方式**：
  1. 以 pyproject.toml 作为单一数据源（SSOT）
  2. 对比其他环境配置文件（Dockerfile、requirements.txt、CI脚本）
  3. 标记差异：缺失的包、版本不一致、多余的包
  4. 同步更新所有配置，确保一致性
- **预期收益**：消除"在我机器上能跑"问题，减少环境相关bug

### 场景4：Docker 镜像瘦身（跨领域推断）

- **场景**：Docker 镜像体积过大，需要识别不必要安装的包
- **应用方式**：
  1. 执行步骤1-2扫描代码中实际使用的包
  2. 对比 Dockerfile 中安装的包列表
  3. 识别代码中未使用的包（可能是历史遗留）
  4. 移除未使用的包，重新构建镜像并验证
- **预期收益**：减小镜像体积，加快部署速度，减少攻击面

## 待验证问题（升级 L2 需确认）

1. **自动化脚本可行性**：能否编写一个完全自动化的脚本执行步骤1-3，仅需人工确认步骤2的动态依赖？
2. **pip-compile/uv 集成**：使用 uv.lock 或 requirements.lock 锁定完整依赖树时，本模式如何调整？
3. **monorepo 场景**：在多包 monorepo 中，如何处理包间依赖和第三方依赖的边界？
4. **C扩展系统依赖**：除了 Python 包依赖，如何系统化审计 .so 文件依赖的系统库（libxxx.so）？

## 与相关模式的关系

- **[compiled-wheel-runtime-image-build.md](../code-patterns/compiled-wheel-runtime-image-build.md)**：本模式步骤4的 runtime 镜像策略使用该模式
- **[python-implicit-dependency-detection.md](../code-patterns/python-implicit-dependency-detection.md)**：本模式步骤2的动态依赖检测参考该模式
- **[dev-env-dockerfile-optimization.md](../methodology-patterns/governance-strategy/dev-env-dockerfile-optimization.md)**：本模式步骤4的 dev 镜像优化参考该模式
- **[docker-build-network-resilience.md](docker-build-network-resilience.md)**：本模式步骤4的网络依赖安装使用该模式的容错策略

## Changelog

- **2026-07-27** (v1.0.0): 初始版本，从 XMNN pyproject.toml 依赖审计复盘萃取，单案例验证，标记 L1-draft

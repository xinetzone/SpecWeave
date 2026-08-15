# onnx-dev 变体 - 纯 ONNX 生态镜像 AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本目录是 devcontainer-base 变体系列的一个变体，
>         规则继承自 ../AGENTS.md（变体系列入口），后者继承自 ../../AGENTS.md（项目入口）
> 步骤 3：按上下文路由表加载变体特有规范（.agents/rules/dockerfile.md）
> 步骤 3.5：自检 — 确认已理解父级规则与本变体特有约束（尤其 PyTorch 一等排除约束）
> 步骤 4：在规范指导下执行任务
> ```

本文件是 onnx-dev 变体（纯 ONNX 生态镜像，不含 PyTorch）的 AI 协作者入口。
进入本目录的任务优先读取本文件；本文件未覆盖的规则回退到父级 [../AGENTS.md](../AGENTS.md)。

## 变体概述

| 属性 | 值 |
|------|-----|
| 变体名称 | `onnx-dev` |
| 镜像标签 | `devcontainer-base:onnx-dev-<TAG>`（默认 latest） |
| 基础镜像 | `devcontainer-base:conda-llvm-${BASE_TAG}` |
| 依赖链 | base → conda-llvm → **onnx-dev** |
| 核心定位 | 纯 ONNX 工具链运行时（模型定义/推理/精简/优化/算子编写） |
| Python 环境 | conda **main 环境**（`/opt/conda/envs/main`，Python 3.14.6 cp314t free-threading，GIL 禁用） |
| 安装包 | onnx、onnxruntime、onnx-simplifier、onnxscript（全部经 pip 装入 main 环境） |
| 显式排除 | torch、torchvision（**一等排除约束**，见下文）；onnxoptimizer（free-threading 不兼容，见设计决策） |

## 三条不可违反的约束（改动本变体前必读）

### 1. PyTorch 一等排除约束

- **禁止安装** `torch`、`torchvision` 及任何强依赖 torch 的包
- **双重负向验证防线**（两处强制，不可删除）：
  1. Dockerfile Stage 2 安装后：`find_spec('torch') is None` 断言
  2. Dockerfile Stage 4 验证 8/10：torch AND torchvision 同时缺席断言
- 测试脚本 T8/T9 为运行期第三道防线
- 检测用 `importlib.util.find_spec`（不实际 import，无副作用）
- **无 `TORCH_INDEX_URL` 构建参数**（区别于 onnx-pytorch 变体）

### 2. main 环境安装约束

- 所有 pip 包安装至 conda **main 环境**（非 base 环境 `/opt/conda`）
- `ENV PATH=/opt/conda/envs/main/bin:...` 置于最前（默认 `python` 即 main 环境）
- 验证命令一律使用绝对路径 `/opt/conda/envs/main/bin/python`

### 3. free-threading 防线

- 安装后必须断言：python 构建串含 `cp314t` 且 `sys._is_gil_enabled() is False`
- 任何 pip 依赖破坏 free-threading 状态都会使构建立即失败（by design）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则）
  └─ apps/AGENTS.md（应用区入口）
       └─ devcontainer-base/AGENTS.md（项目路由入口）
            └─ variants/AGENTS.md（变体系列入口）
                 └─ onnx-dev/AGENTS.md ← 本文件（变体级入口）
                      ├─ .agents/rules/dockerfile.md  ← 本变体特有 Dockerfile 规范
                      ├─ Dockerfile                   ← 4 追加阶段构建定义
                      ├─ .env.example                ← 构建参数模板（无 TORCH_INDEX_URL）
                      └─ README.md                   ← 人类可读文档
```

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| 修改本变体 Dockerfile | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | 基础信息、PATH 优先级、PyTorch 一等排除约束、free-threading 防线、4 阶段结构、构建参数 |
| 新增/修改 pip 包 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) + 本文件三条约束 | 新包必须兼容 cp314t free-threading 且不传递依赖 torch |
| 变体共享约定（FROM/SHELL/缓存挂载/验证检查点） | [../.agents/rules/variant-conventions.md](../.agents/rules/variant-conventions.md) | 所有变体必须遵循的 Dockerfile 共享约定 |
| 构建/测试本变体 | [../scripts/build-onnx-dev.sh](../scripts/build-onnx-dev.sh) + [../scripts/test-onnx-dev.sh](../scripts/test-onnx-dev.sh) | 一键构建（依赖链自动补齐）+ 23 项单元测试 |
| 注册信息/构建编排 | [../build.sh](../build.sh) + [../.agents/rules/build-orchestration.md](../.agents/rules/build-orchestration.md) | VARIANTS 数组条目、拓扑排序、逐条验证 |
| 测试规范（L1-L6 六层策略） | [../.agents/rules/testing.md](../.agents/rules/testing.md) | 测试脚本编写规范 |
| 参考姊妹变体（含 PyTorch 版本） | [../onnx-pytorch/README.md](../onnx-pytorch/README.md) | 对比参考：base 环境架构 + torch 安装 |
| 父级回退（变体系列通用规则） | [../AGENTS.md](../AGENTS.md) | 本文件未覆盖时回退 |

## 构建与验证速查

```bash
# 一键构建（WSL2/Linux，自动补齐 conda-llvm 依赖并运行测试）
bash variants/scripts/build-onnx-dev.sh

# 仅构建（经统一构建脚本，国内镜像源）
bash variants/build.sh --variant onnx-dev --cn

# 仅测试已有镜像（23 项，含 torch 缺席负向验证 T8/T9）
bash variants/scripts/test-onnx-dev.sh --tag latest

# 快速验证镜像内 ONNX 生态 + torch 缺席 + GIL 状态
docker run --rm devcontainer-base:onnx-dev-latest \
  /opt/conda/envs/main/bin/python -c "import onnx,onnxruntime,sys;import importlib.util as u;print(onnx.__version__,onnxruntime.__version__,'torch_absent' if u.find_spec('torch') is None else 'TORCH_PRESENT!','gil_disabled' if not sys._is_gil_enabled() else 'GIL_ENABLED!')"
```

## 已知设计决策记录

| 决策 | 理由 |
|------|------|
| onnxoptimizer 被排除（构建期 + 测试期 T4 双负向防线） | 其 sdist 声明 `py_limited_api='cp312'`，与 free-threading 构建（`Py_GIL_DISABLED`）根本不兼容（CPython #111506），无 cp314t wheel，源码构建必失败；onnxsim 0.5+ 已内置图优化基本覆盖其用途 |
| 基于 conda-llvm 而非 onnx-pytorch 裁剪 | 裁剪已构建镜像不可行（层不可变）；从依赖链上游分叉是唯一干净路径 |
| torch 缺席用 `find_spec` 而非 `import` | 不实际导入：更快、无副作用、不触发 torch 初始化报错歧义 |
| Stage 4 计时器数据在 `rm -rf /tmp/*` 前捕获 | 计时器文件位于 /tmp，清理后再读取会因空值导致算术展开语法错误（已修复并预防） |
| conda 中间变体引用已移除 | conda 变体已下线，conda-llvm 直接基于 devcontainer-base:latest |

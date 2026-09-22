---
id: "native-dev-offline-delivery"
title: "两个过程：有网构建 → 无网离线开发"
source: "README.md#两个过程镜像构建有网离线开发无网"
---
# 两个过程：有网构建 → 无网离线开发

本栈的开发流程显式拆为两个过程——**过程一必须有网、过程二完全不需要网**。
拆分的理由：镜像构建期的 apt / mamba / pip 三段绕不开网络，而日常的
`build-tvm` / `wheel` / 调试没有任何联网必要；分开建模后，无网机器只要携带
**一个镜像归档 + 源码目录**，就能完成全部编译与打包。

## 过程一：镜像环境构建（有网侧，一次性）

目标是产出**离线自足镜像**：把 numpy/scipy 等 `pyproject.toml` 声明的全部运行时依赖、Nuitka 打包栈、
系统 gcc/g++、LLVM/Clang 22、cmake/ninja/ccache、patchelf 等编译期依赖全部
烤进镜像，并由**构建期离线完备性守卫**（`smoke/_toolchain_guards.py` §7）逐项
实测断言。守卫在构建期 fail-fast，把缺口暴露在有网侧，而不是搬到无网机器后才炸。

```bash
invoke native.build        # 构建镜像；Layer 5 自动跑「离线完备性守卫」
invoke native.save         # 导出归档：tar.gz + manifest/SHA256
#   产物落在镜像缓存目录（默认 ./.image-cache/），形如
#   native-dev-<tag>-<时间戳>.tar.gz + 同名 .manifest.json（含 SHA256 与 latest 软链）
```

携带到无网机器的是两样东西：① `.image-cache/` 里的镜像归档（tar.gz + manifest）；
② 源码目录（`npu_tvm` 含 `3rdparty` 子模块、`npuusertools`、`models`）——源码
不在镜像内，由使用者自备（路径见 [05 参数表](05-params-and-relations.md) `NPU_TVM_PATH` 等）。

## 过程二：启动开发环境并开发（无网侧）

```bash
invoke native.load --path /path/to/native-dev-*.tar.gz   # manifest 完整性校验后导入
invoke native.up --offline                             # 不构建、不起任何对外网络请求

# —— 以下开发活动全部离线可用（脚本内已无联网点）——
invoke native.build-tvm      # invoke config + cmake + ninja + gcc，全本地
invoke native.wheel          # Nuitka 本地编译 + python -m build --no-isolation
podman-compose -p native-dev exec native \
    bash /opt/native-builder/scripts/verify-wheel.sh   # 10 项隔离验证，亦无联网点
```

无网侧**不补装任何依赖**：缺任何一项都说明过程一的镜像不自足，正确处置是回有网侧
重跑 `invoke native.build && invoke native.save` 后重新携带归档——这正是把守卫放在
构建期的意义（两个过程之间只有单向传递，过程二没有回补手段）。

## 离线开关语义

等价开关：**`NATIVE_OFFLINE=1`**（写 `.env` 或 shell export 均可，经 WSL 桥接透传
进容器）。`invoke native.up --offline` 与 `NATIVE_OFFLINE=1` 效果相同；`.env` 里开了
想临时关掉用 `invoke native.up --no-offline`。注意 `--offline` 是**全链路**语义，
不只是跳过构建。

**`--skip-build` ≠ `--offline`**：`--skip-build` 只声明「这一次 `up` 不构建」，
**不注入** `NATIVE_OFFLINE`（只影响 `up` 一步，`build` / `wheel` / `build-tvm` 行为
不变）。在无网机器上 `invoke native.up --skip-build && invoke native.wheel` 能起栈成功，
但容器内打包仍会尝试联网兜底而失败。**无网环境请一律用 `--offline`**；
`--skip-build` 只用于有网环境下省一次构建。

| 环节 | 离线下的行为 |
|---|---|
| `native.up` | 强制跳过构建（`skip_build=True`）；`--no-build` 现已**恒真**（C16，在线同理），离线禁网不再依赖该分叉；镜像不存在时 fail-fast Exit(1) |
| `native.build` | 镜像构建在任何情况下都需要网络，离线判定为真时**立即 Exit(1)** 并给出离线三选一指引，不进入构建流程 |
| `native.wheel` | 容器内不再 pip 兜底 numpy/scipy（缺失即 Exit 2）；Nuitka 去掉 `--assume-yes-for-downloads`；缺系统 gcc 也 Exit 2 |
| `build-wheel.sh` pip 镜像 | 离线不再改写 pip config（`PIP_MIRROR` 在无网侧无意义） |

设计原则是**硬失败 + 可执行中文指引**，不做静默降级——离线环境里"悄悄联网然后
超时"比直接报错难排查得多。

# 创建 Windows 下 Python 3.14.6t(free-threading) Conda 环境 — 任务清单

## Task 1: 创建 py314t free-threading 环境
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 使用 conda-forge 频道创建环境 `py314t`，安装 `python-freethreading=3.14.*`(优先 3.14.6)
  - 候选命令：`conda create -n py314t conda-forge::'python-freethreading=3.14.*' -y`
  - 若默认频道不含 conda-forge，添加 `-c conda-forge`；若网络受阻，配置镜像(BFSU/TUNA)兜底
  - 记录实际安装的 Python 版本与构建号
- **Test Requirements**:
  - `rule` TR-1.1: 环境 `py314t` 出现在 `conda env list` 中
  - `rule` TR-1.2: `conda list -n py314t` 显示 python 主版本为 3.14
  - `rule` TR-1.3: free-threading: `conda list -n py314t python_abi` 的 build 为 `*_cp314t`

## Task 2: 写入并验证 free-threading 持久化约束
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 `$CONDA_PREFIX\conda-meta\pinned`(即 env 下 `conda-meta/pinned`)写入 `python_abi 3.14 *_cp314t`
  - 该文件在创建后通常已生成；若不存在则创建；若存在则合并(避免重复行)
- **Test Requirements**:
  - `rule` TR-2.1: env 的 `conda-meta/pinned` 包含一行 `python_abi 3.14 *_cp314t`
  - `rule` TR-2.2: 无重复行

## Task 3: 运行 GIL 禁用与 SOABI 校验
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 运行 `...\envs\py314t\python.exe -c "import sysconfig; import sys; print(sys.version); print(sys._is_gil_enabled())"`，
    GIL 必须为 `False`
  - 打印 SOABI，必须含 `cp314t`/`cpython-314t`
  - 打印解释器可执行名(python3.14t 或 python)，记录到说明
- **Test Requirements**:
  - `rule` TR-3.1: `sys._is_gil_enabled()` 输出 `False`
  - `rule` TR-3.2: SOABI 包含 `t`(cp314t/cpython-314t)

## Task 4: 编写激活与使用说明
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 在 spec 目录或项目约定的合适位置记录：激活命令、GIL 校验命令、退出命令、常见问题
  - 说明 conda-forge 频道来源与 python_abi 约束的作用
- **Test Requirements**:
  - `rule` TR-4.1: 说明文档存在且命令可复制执行
  - `rubric` TR-4.2: 说明对新手清晰度；scale 1-3；threshold >= 3

## 注意事项（执行环境风险）
- 本终端为沙箱，`conda` 命令曾命中受限缓存路径(`AppData\Local\conda-anaconda-tos\...`)失败。
  若 create 仍受限，尝试：改用 conda-forge 镜像缓存目录(设置 `CONDA_PKGS_DIRS` 到非受限路径)、
  或请求在沙箱外执行该命令。
- free-threading 检测以 `_is_gil_enabled()` 的值(False)为准，不能只看属性是否存在。

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]
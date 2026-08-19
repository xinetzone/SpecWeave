# 创建 Windows 下 Python 3.14.6t(free-threading) Conda 环境 — 检查清单

## 环境创建
- [x] `py314t` 环境成功创建并出现在 `conda env list`
- [x] Python 主版本为 3.14(优先 3.14.6，回退则记录实际版本)  → **实测 3.14.6 free-threading build**
- [x] 来源为 conda-forge 频道(`python-freethreading`)

## free-threading 持久化
- [x] `conda-meta/pinned` 包含 `python_abi 3.14 *_cp314t`(无重复行)
- [x] `conda list python_abi` 的 build 为 `*_cp314t`  → **`3.14 / 8_cp314t`**

## GIL 与 SOABI 校验
- [x] `python -c "import sys; print(sys._is_gil_enabled())"` 输出 `False`  → **`False`**
- [x] SOABI 包含 `t`(cp314t/cpython-314t)  → **`cp314t-win_amd64`**

## 资源与使用说明
- [x] 可用 `conda activate py314t` 激活（需先设 `CONDA_ENVS_DIRS`，见 USAGE.md）
- [x] 使用说明文档存在，激活/GIL校验/退出命令完整可复制（USAGE.md）
- [x] 未破坏任何现有环境；未改动 CPython 源码工作树
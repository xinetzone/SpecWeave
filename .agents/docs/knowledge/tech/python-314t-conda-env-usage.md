# py314t — Python 3.14.6t（free-threading / no-GIL）环境使用说明

## 环境速览

| 项 | 值 |
|---|---|
| 环境名 | `py314t` |
| Python 版本 | **3.14.6 free-threading build**（conda-forge，Win-64） |
| GIL 状态 | **禁用**（`sys._is_gil_enabled() == False`） |
| SOABI | `cp314t-win_amd64` |
| 来源包 | `python-freethreading`（conda-forge） |
| `python_abi` | `3.14 / 8_cp314t`（已持久化到 `conda-meta/pinned`） |
| 环境前缀 | `D:\spaces\SpecWeave\.temp\conda-envs\py314t` |

可执行文件：`python.exe`（即 `python3.14t.exe`）、`pythonw3.14t.exe`。

## 激活环境（二选一）

### 方式 A（推荐）：设置 envs 目录后激活
因为创建时沙箱不允许写入默认 envs 目录，本环境位于工作区 `.temp\conda-envs`。
先在当前终端设置 `CONDA_ENVS_DIRS`，再激活：

```powershell
$env:CONDA_ENVS_DIRS = "D:\spaces\SpecWeave\.temp\conda-envs"
conda activate py314t
```

> 注意：`CONDA_ENVS_DIRS` 是本终端会话级变量。若打开新终端需重新设置，或用方式 B 直接引用。

### 方式 B：直接使用环境前缀（无需激活）
```powershell
conda run -p "D:\spaces\SpecWeave\.temp\conda-envs\py314t" python -c "import sys; print(sys.version)"
# 或直接调用解释器
"D:\spaces\SpecWeave\.temp\conda-envs\py314t\python.exe" --version
```

## 校验 free-threading（no-GIL）已生效

```powershell
python -c "import sys, sysconfig; print(sys.version); print('GIL_enabled =', sys._is_gil_enabled()); print('SOABI =', sysconfig.get_config_var('SOABI'))"
```

期望输出：
- `3.14.6 free-threading build ...`
- `GIL_enabled = False`
- `SOABI = cp314t-win_amd64`

> 判断依据：必须看 `_is_gil_enabled()` 的**值**为 `False`。`sys._is_gil_enabled` 属性在全部 3.14 中均存在，不能只看属性是否存在（否则 GIL 版本也会误判为 free-threading）。

## 退出激活

```powershell
conda deactivate
```

## 保持 free-threading 的约束

`conda-meta\pinned` 已写入 `python_abi 3.14 *_cp314t`，用于防止后续安装其他包时，
解释器被非 free-threading 版本静默替换。

## 常见问题

- **`conda activate py314t` 找不到环境？** → 先按「方式 A」设置 `CONDA_ENVS_DIRS`，或改用「方式 B」直接引用前缀。
- **想把环境移到标准位置？** → 在非沙箱终端（有 `D:\Users\xinzo\anaconda3\envs` 写权限）运行。

  第一步先导出（注意：文件名必须是支持的模式，如 `environment.yml`；且需先设 `CONDA_ENVS_DIRS` 才能找到本环境）：
  ```powershell
  $env:CONDA_ENVS_DIRS = "D:\spaces\SpecWeave\.temp\conda-envs"
  conda env export -n py314t -f "D:\spaces\SpecWeave\.temp\environment.yml"
  ```

  第二步在非沙箱终端按导出的 spec 重建到标准位置（会包含 `python=3.14.6=*_cp314t` 与 `python_abi=*_cp314t`，保持 free-threading）：
  ```powershell
  conda env create -n py314t -f "D:\spaces\SpecWeave\.temp\environment.yml"
  ```
  （`.temp\environment.yml` 已替你生成；包已缓存在 `.temp\conda-pkgs`，重建较快。
  重建后建议再写一次 `conda-meta\pinned` 的 `python_abi 3.14 *_cp314t` 约束。）
  > 为什么不能叫 `py314t.yml`：`conda env export -f` 依据文件名自动识别格式，仅识别 `environment.*` 等约定名称；自定义文件名需加 `--format=environment-yaml`。
- **test/debug CPython 源码**：`d:\spaces\SpecWeave\external\libs\python\cpython` 当前为 `main`（3.16.0a0）。
  本环境为 3.14.6t，用于 free-threading 相关调试；与源码版本强绑定时需另行切换 checkout（按 specs 决策，本次不切换）。
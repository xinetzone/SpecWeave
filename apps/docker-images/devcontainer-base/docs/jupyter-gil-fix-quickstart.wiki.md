# Jupyter GIL 问题修复 — 新开发者快速上手指南（团队 Wiki 版）

> **一句话**：镜像里的 Python 是 free-threading（无 GIL）构建，但 Jupyter kernel 偶尔会"悄悄"把 GIL 打开，导致多线程不并行、代码变慢。用 `fix-jupyter-gil.sh` 三步诊断→修复→验证即可解决。
>
> **适用对象**：刚接触 `devcontainer-base` 镜像的新开发者。
>
> 📌 本版为团队 Wiki 粘贴版：所有仓库内链接已转换为 GitHub 绝对 URL。仓库内版本见 [jupyter-gil-fix-quickstart.md](https://github.com/xinetzone/SpecWeave/blob/main/apps/docker-images/devcontainer-base/docs/jupyter-gil-fix-quickstart.md)（相对路径，适合仓库内浏览）。

---

## 1. 什么时候需要用它（症状识别）

你不需要理解 PEP 703 也能判断该不该跑脚本。遇到以下任一情况就用：

| 症状 | 示例 |
|------|------|
| Jupyter 里跑多线程代码**不加速**反而变慢 | `ThreadPoolExecutor` 8 线程 vs 单线程耗时几乎一样 |
| 想确认 kernel 是否真的在并行 | 想打印 `sys._is_gil_enabled()` 但不确定怎么验证 |
| 刚升级/重建镜像，想排查 Jupyter 环境 | 新镜像里 Jupyter 行为异常 |
| bash 下正常、Jupyter 内异常 | 同一个命令在终端跑很快，在 notebook 里跑变慢 |

**不用它的情况**：你的容器不是 free-threading 构建（脚本会检测并自动跳过）；你只用 SSH 不用 Jupyter。

## 2. 前置条件

- 已启动 `devcontainer-base` 或任一变体镜像容器（`conda-llvm` / `onnx-dev` 等）
- 容器内能执行 bash 命令（`docker exec` / SSH / VSCode Remote 均可）
- 脚本在镜像内可用（若未内置，用只读挂载方式带入，见下）

```bash
# 若脚本未内置在镜像里，用挂载方式带入（Windows WSL 示例）
podman run --rm -v /path/to/fix-jupyter-gil.sh:/tmp/gil.sh:ro \
    --entrypoint bash devcontainer-base:latest -c 'bash /tmp/gil.sh --all'
```

脚本源码：[variants/scripts/fix-jupyter-gil.sh](https://github.com/xinetzone/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/scripts/fix-jupyter-gil.sh)

## 3. 三步上手

脚本有 4 种运行模式，新手只需记住最常用的 **`--all`**：

```bash
# ① 快速诊断（只读，不改任何东西）—— 推荐先跑这个
bash fix-jupyter-gil.sh

# ② 完整修复（诊断 + 修复配置 + 验证）—— 遇到问题直接跑这个
bash fix-jupyter-gil.sh --all

# ③ 只修配置，不验证（高级）
bash fix-jupyter-gil.sh --fix

# ④ 只验证 kernel GIL 状态（高级）
bash fix-jupyter-gil.sh --verify
```

**新手标准流程**：
1. 先跑 `bash fix-jupyter-gil.sh` 看 GIL-03 是否显示 `[FAIL]`
2. 若 FAIL，跑 `bash fix-jupyter-gil.sh --all`，等它自动注入配置并验证
3. 看到 `[RESULT] PASS` 即完成；看到 `[RESULT] FAIL` 跳到第 5 节

### 实战案例：一次真实的报错排查（8 线程不加速）

> 以 `conda-llvm` 镜像为例，演示从"发现变慢"到"确认并行"的完整闭环。照着做即可。

**① 复现症状（notebook 中执行）**

```python
import time
from concurrent.futures import ThreadPoolExecutor

def work(_):
    time.sleep(1)
    return _

t0 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    list(ex.map(work, range(8)))
print(f"8线程耗时: {time.time()-t0:.2f}s")

import sys
print("kernel GIL:", sys._is_gil_enabled())
```

期望：8 个 1 秒任务并行约 **1s**；实际约 **8s** 且打印 `kernel GIL: True` → 确认 GIL 被启用、多线程已退化为串行。

**② 跑诊断脚本（容器 bash 中）**

```bash
bash fix-jupyter-gil.sh
```

关键输出（GIL-03 暴露根因）：

```
=== [GIL-03] 配置检查（只读，--fix 可注入） ===
  [FAIL] /etc/supervisor/conf.d/jupyter.conf 缺少 PYTHON_GIL，Jupyter kernel 内 GIL 会被 _brotli 拉起
  [HINT] 运行 bash fix-jupyter-gil.sh --fix 注入
```

**③ 一键修复 + 验证**

```bash
bash fix-jupyter-gil.sh --all
```

期望先看到 `[FIXED] 已注入 PYTHON_GIL="0" 到 environment= 行`，随后 GIL-04 输出：

```
  [kernel] E2E_OK GIL_ENABLED= False
  [RESULT] PASS（kernel 内 GIL 保持禁用）
```

**④ 重启 Jupyter 服务（关键一步，别漏）**

```bash
supervisorctl restart jupyter
```

> 为什么必须重启：`--all` 的 E2E 验证用的是**新起的临时 kernel**，所以能通过；但你正在用的 notebook kernel 是**旧进程**，不会继承新注入的 `PYTHON_GIL=0`，不重启就会回到原状。

**⑤ 回到 notebook 复测**

```python
import sys
print(sys._is_gil_enabled())   # 现在输出 False

# 重跑 ① 的多线程测试 → 8线程耗时 ≈ 1s，真正并行
```

**⑥ 收尾自测（可选）**

```bash
python examples/free_threading_demo.py   # 输出串行/多线程/多进程耗时对比，确认多线程显著优于串行
```

## 4. 输出怎么看（5 个环节）

脚本按 GIL-01 ~ GIL-05 分步执行，重点看 3 处：

| 环节 | 看什么 | 期望结果 |
|------|--------|---------|
| GIL-01 环境检测 | 是否 `free-threading` + `bash GIL 状态` | `禁用（nogil 生效）` |
| GIL-03 配置检查 | `jupyter.conf` 是否含 `PYTHON_GIL` | `[OK] ... 已含 PYTHON_GIL`（修复后） |
| GIL-04 kernel 验证 | kernel 内 `_is_gil_enabled()` | `[RESULT] PASS` |

> GIL-02 是"肇事模块复现"（复现 `_brotli` 拉起 GIL 的过程），了解即可；GIL-05 是重建/清理指引，改镜像时才需要。

## 5. 结果异常时的处置

| 现象 | 原因 | 处置 |
|------|------|------|
| `[FAIL]` jupyter.conf 缺 `PYTHON_GIL` | 镜像版本旧，未含修复 | 跑 `--fix` 注入；**重启 Jupyter** 生效 |
| `[RESULT] FAIL`（修复后 kernel 仍 GIL 启用） | 注入后没重启 Jupyter 服务 | `supervisorctl restart jupyter` 后重跑 `--verify` |
| GIL-01 显示"非 free-threading" | 用的不是 main 环境 Python | 检查 `MAIN_PY` 路径是否正确（默认 `/opt/conda/envs/main/bin/python`） |
| 其他 C 扩展也拉起 GIL（不止 brotli） | 该扩展未声明 free-threading 支持 | 见下"问题升级路径" |

## 6. 三个易踩的坑（务必看）

1. **改了 jupyter.conf 必须重启 Jupyter**：配置注入后不重启不生效。`--fix` 只会改文件，`--all` 才会连带验证。
2. **`-e PYTHON_GIL=1` 不能切回兼容模式**：supervisord 的 `environment=` 优先级**高于** docker run 环境变量。想给 Jupyter 开 GIL 兼容模式，必须改 `/etc/supervisor/conf.d/jupyter.conf` 并重启，而不是 `docker run -e`。
3. **GIL 是"一次性保险丝"**：`PYTHON_GIL=0` 只在进程启动时生效；运行中 import 到不兼容的 C 扩展仍会打开 GIL 且无法在当前进程内关闭。所以修好后若又变慢，先重启 Jupyter（kernel 重启即可恢复）。

## 7. 问题升级路径（脚本解决不了时）

1. **定位肇事模块**：用更强大的诊断工具
   ```bash
   python scripts/check_gil_state.py --audit numpy,brotli
   ```
   它会用"金丝雀子进程"逐个 import 并报告哪个模块拉起了 GIL。工具源码：[scripts/check_gil_state.py](https://github.com/xinetzone/SpecWeave/blob/main/apps/docker-images/devcontainer-base/scripts/check_gil_state.py)
2. **重建镜像**（源配置已被改坏/想根治）：见脚本 GIL-05 的重建指引，`base` 重建后所有变体自动继承修复。
3. **查文档**：
   - 根因与修复细节：[故障排查报告](https://github.com/xinetzone/SpecWeave/blob/main/.agents/docs/retrospective/reports/build-engineering/troubleshooting-devcontainer-jupyter-gil-20260819.md)
   - CI 守卫规范：[variants-ci.md 第9章](https://github.com/xinetzone/SpecWeave/blob/main/apps/docker-images/devcontainer-base/.agents/workflows/variants-ci.md)
   - free-threading C 扩展编译指南：[PY314T-C-EXTENSION-GUIDE.md](https://github.com/xinetzone/SpecWeave/blob/main/apps/docker-images/devcontainer-base/docs/PY314T-C-EXTENSION-GUIDE.md)
   - 自测多线程并行：[examples/free_threading_demo.py](https://github.com/xinetzone/SpecWeave/blob/main/apps/docker-images/devcontainer-base/examples/free_threading_demo.py)

---

## 附：新手最常用命令速查

```bash
# 诊断 + 修复 + 验证 一键完成
bash fix-jupyter-gil.sh --all

# 修复后手动重启 Jupyter（如需）
supervisorctl restart jupyter

# 手动验证 kernel GIL 状态（在 notebook 里执行）
import sys; print(sys._is_gil_enabled())   # 期望 False

# 多线程自测（确认真正并行）
python examples/free_threading_demo.py
```

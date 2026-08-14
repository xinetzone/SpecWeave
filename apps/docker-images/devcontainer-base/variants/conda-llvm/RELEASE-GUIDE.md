# DevContainer Base - Conda-LLVM 镜像发布操作指南 (Release Guide)

> 面向维护者的**端到端发布操作手册**。从环境准备、依赖校验、构建、验证到发布/回滚，
> 每一步都有可复现的命令与验收标准。
> 前置阅读：[发布清单 RELEASE.md](./RELEASE.md)（版本矩阵）+ [依赖说明 DEPENDENCIES.md](./DEPENDENCIES.md)（依赖结构）。

> **架构说明**：本变体直接基于 `devcontainer-base:${BASE_TAG}`（conda 中间变体已下线），工具链安装于 conda main 环境（Python 3.14.6 cp314t free-threading）。

## 1. 发布前置条件

| 条件 | 验收标准 |
|------|---------|
| 构建环境 | Linux / WSL2 + Docker BuildKit，且已登录 docker CLI |
| 依赖镜像存在 | `devcontainer-base:<TAG>`（如 `latest` 或 `1.0`） |
| 目标标签 | 确定发布标签（如 `2.0`） |
| 版本决策 | 确认 `LLVM_VERSION`（默认 22.1.8）在 conda-forge 全部可用（llvmdev/clangdev/clang/lld） |
| 测试脚本适配 | 确认 `test-conda-llvm.sh` 已适配 main 环境路径（T14/T19，见第 4 节注意事项） |

```bash
# 校验依赖镜像（以 latest 为例）
docker images --format '{{.Repository}}:{{.Tag}}' | grep -E 'devcontainer-base:(latest|<TAG>)$'
```

## 2. 依赖链构建（自底向上）

`build.sh` 通过拓扑排序自动处理依赖顺序；conda-llvm 无中间变体依赖，仅需基础镜像：

```bash
cd /path/to/devcontainer-base

# ① 基础镜像（V2 内置默认镜像源）
bash scripts/build.sh --tag latest --cn

# ② conda-llvm 变体（会自动先校验 ① 存在）
bash variants/scripts/build-conda-llvm.sh --tag 2.0
```

> 国内网络环境统一加 `--cn`（apt=aliyun, conda=tuna, pip=aliyun，为 `build.sh --cn` 的实际传参）。

## 3. 构建（conda-llvm）

```bash
# 推荐：一键脚本（构建 + 自动验证 + 计时汇总）
bash variants/scripts/build-conda-llvm.sh --tag 2.0

# 等价手动构建
docker build -f variants/conda-llvm/Dockerfile \
  --build-arg APT_MIRROR=aliyun \
  --build-arg CONDA_MIRROR=bfsu \
  --build-arg PIP_MIRROR=aliyun \
  --build-arg BASE_TAG=latest \
  -t devcontainer-base:conda-llvm-2.0 \
  .
```

**验收**：构建日志末尾出现 `[TIMER] Stage 4/4 ...` 与 **BUILD TIMING SUMMARY** 汇总表，退出码为 0；Stage 2 的 free-threading GUARD 检查通过（`[OK] python is free-threading (cp314t) build` + `[OK] GIL is disabled`）。

## 4. 验证（发布门禁）

运行 21 项测试套件，**全部 PASS 才可发布**：

```bash
bash variants/scripts/test-conda-llvm.sh --tag 2.0
# 期望输出: All 21 tests passed! (0 FAILED)
```

> ⚠️ **测试脚本适配检查（发布前必做）**：截至 main 环境迁移，测试脚本中以下用例仍检查旧 base 环境路径，与新架构镜像不一致，需先适配：
> - **T14**：`/opt/conda/bin/jupyter` → 应为 `/opt/conda/envs/main/bin/jupyter`
> - **T19**：`which python` 期望 `/opt/conda/bin/python` → 应为 `/opt/conda/envs/main/bin/python`
>
> 适配完成前，测试结果中的 T14/T19 FAIL 不代表镜像缺陷；可用下方冒烟验证替代判定。

快速冒烟验证（新架构路径）：

```bash
# 版本
docker run --rm devcontainer-base:conda-llvm-2.0 llvm-config --version   # 22.1.8
docker run --rm devcontainer-base:conda-llvm-2.0 clang --version | head -1
# free-threading Python（main 环境）
docker run --rm devcontainer-base:conda-llvm-2.0 \
  bash -c 'python --version && python -c "import sys; print(sys._is_gil_enabled())"'
# 期望: Python 3.14.6 / False
# C++ 编译
docker run --rm devcontainer-base:conda-llvm-2.0 bash -c \
  'echo "int main(){return 0;}" > /tmp/a.cpp && clang++ /tmp/a.cpp -o /tmp/a && /tmp/a && echo COMPILE_OK'
```

## 5. 元数据核验

发布前核验 build-info（含 main 环境字段）：

```bash
docker run --rm devcontainer-base:conda-llvm-2.0 \
  cat /etc/devcontainer-variant-conda-llvm-build-info | grep -E 'BUILD_DATE|BASE_IMAGE|VERSION|CONDA_VERSION|INSTALL_ENV|PYTHON_BUILD|PACKAGES'
```

| 字段 | 期望 |
|------|------|
| `BASE_IMAGE` | `devcontainer-base:<TAG>`（标签完整） |
| `LLVM_VERSION_ACTUAL` / `CLANG_VERSION_ACTUAL` | `22.1.8` |
| `INSTALL_ENV` | `main (default user env)` |
| `PYTHON_BUILD` | `free-threading nogil active` |
| `PACKAGES_INSTALLED` | 含 `llvmdev,clangdev,clang,lld,cmake,ninja,make,libgcc,libstdcxx-ng` |
| `PACKAGES_EXCLUDED` | 含 `lldb(...)` |

## 6. 标签与发布（Registry）

```bash
# 打发布标签（滚动标签 + 精确标签）
docker tag devcontainer-base:conda-llvm-2.0 devcontainer-base:conda-llvm-latest

# 若推送到 registry
# docker tag devcontainer-base:conda-llvm-2.0 <registry>/devcontainer-base:conda-llvm-2.0
# docker push <registry>/devcontainer-base:conda-llvm-2.0
# docker push <registry>/devcontainer-base:conda-llvm-latest
```

**发布清单更新**：将实际构建日期、镜像大小、验证结果回填到 [RELEASE.md](./RELEASE.md) 的「发布元数据」与「验证结果」章节（新增对应新架构的发布记录，勿覆盖 1.0 历史记录）。

## 7. 发布后验证（冒烟）

```bash
# DinD 开发模式
docker run -d --name smoke --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
  -e USER_PASSWORD=devpass -e JUPYTER_TOKEN=mysecret \
  devcontainer-base:conda-llvm-2.0
docker exec smoke bash -c 'docker --version && ssh -V 2>&1 && /opt/conda/envs/main/bin/jupyter --version | head -1'
docker rm -f smoke
```

## 8. 回滚

| 场景 | 操作 |
|------|------|
| 功能回滚 | 重新 `docker tag` 上一稳定标签，或从 registry 拉取旧版本 |
| 镜像重建 | 清缓存重建 `build-conda-llvm.sh --tag 2.0 --no-cache` |
| 元数据错误 | 修正 Dockerfile 后按「依赖链构建」自底向上重建 |

## 9. 发布检查清单

- [ ] 依赖镜像（base）已构建且版本匹配
- [ ] conda-llvm 构建成功（退出码 0，计时汇总完整，free-threading GUARD 通过）
- [ ] 测试脚本已适配 main 环境路径（T14/T19），21 项测试全部 PASS（或冒烟验证替代通过）
- [ ] build-info 元数据完整（`BASE_IMAGE` 含完整标签、`INSTALL_ENV=main`、`PYTHON_BUILD=free-threading nogil active`）
- [ ] 滚动标签 + 精确标签已打
- [ ] 发布清单 [RELEASE.md](./RELEASE.md) 元数据已回填（新增记录，保留 1.0 历史）
- [ ] 发布后冒烟验证通过

## 10. 相关文档

- [发布清单](./RELEASE.md)
- [依赖说明](./DEPENDENCIES.md)
- [变体 README](./README.md)
- [构建编排规范](../.agents/rules/build-orchestration.md)
- [测试规范](../.agents/rules/testing.md)
- [变体约定](../.agents/rules/variant-conventions.md)

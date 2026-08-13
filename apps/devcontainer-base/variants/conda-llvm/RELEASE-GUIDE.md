# DevContainer Base - Conda-LLVM 镜像发布操作指南 (Release Guide)

> 面向维护者的**端到端发布操作手册**。从环境准备、依赖校验、构建、验证到发布/回滚，
> 每一步都有可复现的命令与验收标准。
> 前置阅读：[发布清单 RELEASE.md](./RELEASE.md)（版本矩阵）+ [依赖说明 DEPENDENCIES.md](./DEPENDENCIES.md)（依赖结构）。

## 1. 发布前置条件

| 条件 | 验收标准 |
|------|---------|
| 构建环境 | Linux / WSL2 + Docker BuildKit，且已登录 docker CLI |
| 依赖镜像存在 | `devcontainer-base:1.0`、`devcontainer-base:conda-1.0` |
| 目标标签 | 确定发布标签（本示例为 `1.0`） |
| 版本决策 | 确认 `LLVM_VERSION`（默认 22.1.8）在 conda-forge 全部可用 |

```bash
# 校验依赖镜像
docker images --format '{{.Repository}}:{{.Tag}}' | grep -E 'devcontainer-base:(1.0|conda-1.0)$'
```

## 2. 依赖链构建（自底向上）

`build.sh` 通过 `topological_sort()` 自动处理依赖顺序，亦可手动分步构建以隔离故障：

```bash
cd /path/to/devcontainer-base

# ① 基础镜像
bash scripts/build.sh --tag 1.0 --cn

# ② conda 变体
bash variants/build.sh --variant conda --tag 1.0 --cn

# ③ conda-llvm 变体（会自动先校验 ① ② 存在）
bash variants/scripts/build-conda-llvm.sh --tag 1.0
```

> 国内网络环境统一加 `--cn`（apt=aliyun, conda=tuna, pip=aliyun）。

## 3. 构建（conda-llvm）

```bash
# 推荐：一键脚本（构建 + 自动验证 + 计时汇总）
bash variants/scripts/build-conda-llvm.sh --tag 1.0

# 等价手动构建
docker build -f variants/conda-llvm/Dockerfile \
  --build-arg APT_MIRROR=aliyun \
  --build-arg CONDA_MIRROR=tuna \
  --build-arg PIP_MIRROR=aliyun \
  --build-arg BASE_TAG=1.0 \
  -t devcontainer-base:conda-llvm-1.0 \
  variants/
```

**验收**：构建日志末尾出现 `[TIMER] Build duration: Ns` 与阶段计时汇总表，退出码为 0。

## 4. 验证（发布门禁）

运行 21 项测试套件，**全部 PASS 才可发布**：

```bash
bash variants/scripts/test-conda-llvm.sh --tag 1.0
# 期望输出: All 21 tests passed! (0 FAILED)
```

快速冒烟验证：

```bash
# 版本
docker run --rm devcontainer-base:conda-llvm-1.0 llvm-config --version   # 22.1.8
docker run --rm devcontainer-base:conda-llvm-1.0 clang --version | head -1
# C++ 编译
docker run --rm devcontainer-base:conda-llvm-1.0 bash -c \
  'echo "int main(){return 0;}" > /tmp/a.cpp && clang++ /tmp/a.cpp -o /tmp/a && /tmp/a && echo COMPILE_OK'
```

## 5. 元数据核验

发布前核验 build-info，确认 `BASE_IMAGE` 标签完整（含 BASE_TAG 修复）：

```bash
docker run --rm devcontainer-base:conda-llvm-1.0 \
  cat /etc/devcontainer-variant-conda-llvm-build-info | grep -E 'BUILD_DATE|BASE_IMAGE|VERSION|CONDA_VERSION'
```

| 字段 | 期望 |
|------|------|
| `BASE_IMAGE` | `devcontainer-base:conda-1.0`（标签完整） |
| `LLVM_VERSION_ACTUAL` / `CLANG_VERSION_ACTUAL` | `22.1.8` |
| `CMAKE_VERSION_ACTUAL` / `NINJA_VERSION_ACTUAL` | `4.4.2` / `1.13.2` |
| `PACKAGES_INSTALLED` | 含 `llvmdev,clangdev,clang,lld,lldb,cmake,ninja,make` |

## 6. 标签与发布（Registry）

```bash
# 打发布标签（滚动标签 + 精确标签）
docker tag devcontainer-base:conda-llvm-1.0 devcontainer-base:conda-llvm-latest

# 若推送到 registry
# docker tag devcontainer-base:conda-llvm-1.0 <registry>/devcontainer-base:conda-llvm-1.0
# docker push <registry>/devcontainer-base:conda-llvm-1.0
# docker push <registry>/devcontainer-base:conda-llvm-latest
```

**发布清单更新**：将实际构建日期、镜像大小、验证结果回填到 [RELEASE.md](./RELEASE.md) 的「发布元数据」与「验证结果」章节。

## 7. 发布后验证（冒烟）

```bash
# DinD 开发模式
docker run -d --name smoke --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
  -e USER_PASSWORD=devpass -e JUPYTER_TOKEN=mysecret \
  devcontainer-base:conda-llvm-1.0
docker exec smoke bash -c 'docker --version && ssh -V 2>&1 && /opt/venv/bin/jupyter --version | head -1'
docker rm -f smoke
```

## 8. 回滚

| 场景 | 操作 |
|------|------|
| 功能回滚 | 重新 `docker tag` 上一稳定标签，或从 registry 拉取旧版本 |
| 镜像重建 | 清缓存重建 `build-conda-llvm.sh --tag 1.0 --no-cache` |
| 元数据错误 | 修正 Dockerfile 后按「依赖链构建」自底向上重建 |

## 9. 发布检查清单

- [ ] 依赖镜像（base / conda）已构建且版本匹配
- [ ] conda-llvm 构建成功（退出码 0，计时汇总完整）
- [ ] 21 项测试全部 PASS
- [ ] build-info 元数据完整（`BASE_IMAGE` 含完整标签）
- [ ] 滚动标签 + 精确标签已打
- [ ] 发布清单 [RELEASE.md](./RELEASE.md) 元数据已回填
- [ ] 发布后冒烟验证通过

## 10. 相关文档

- [发布清单](./RELEASE.md)
- [依赖说明](./DEPENDENCIES.md)
- [变体 README](./README.md)
- [构建编排规范](../.agents/rules/build-orchestration.md)
- [测试规范](../.agents/rules/testing.md)
- [变体约定](../.agents/rules/variant-conventions.md)

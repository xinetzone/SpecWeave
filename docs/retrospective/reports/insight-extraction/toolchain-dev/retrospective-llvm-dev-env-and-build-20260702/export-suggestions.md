---
id: "retrospective-llvm-dev-env-and-build-20260702-export"
title: "导出清单"
source: "session: llvm-dev-env-and-build-20260702"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/toolchain-dev/retrospective-llvm-dev-env-and-build-20260702/export-suggestions.toml"
---
# 导出清单

## 一、本次已交付的资产

### 1.1 环境资产

| 资产 | 位置 | 说明 |
|------|------|------|
| llvm-dev 镜像 | `localhost/llvm-dev:latest` | 基于 localhost/nuitka-gcc-llvm:latest 构建的开发环境镜像 |
| llvm-dev 容器 | 容器名：`llvm-dev` | 正在运行的容器，2222 端口暴露 SSH |
| 开发环境目录 | `server/dev-env/llvm-dev/` | 镜像构建与启动脚本目录 |
| Dockerfile | `server/dev-env/llvm-dev/docker/Dockerfile` | 带阿里云源加速的镜像定义 |
| entrypoint.sh | `server/dev-env/llvm-dev/docker/entrypoint.sh` | 更新后的入口脚本 |
| run.py | `server/dev-env/llvm-dev/bin/run.py` | 一键构建与启动脚本 |
| 文档 | `server/dev-env/llvm-dev/docs/` | README.md 与 REMOTE_DEBUG_GUIDE.md |

### 1.2 编译产物

| 产物 | 位置 | 说明 |
|------|------|------|
| libtvm.so | `server/libs/npu_tvm/build/libtvm.so` | 编译完成的 TVM 核心库 |
| libtvm_runtime.so | `server/libs/npu_tvm/build/libtvm_runtime.so` | TVM 运行时库 |
| VTA 仿真库 | `server/libs/npu_tvm/vta/vta_hw/lib/` | VTA 仿真相关库 |
| clang 构建日志 | `.temp/logs/clang.log` | 已归档的 Clang 编译失败日志 |
| gcc 构建日志 | `.temp/logs/gcc.log` | 已归档的 GCC 编译成功日志 |

### 1.3 复盘知识资产

| 资产 | 位置 | 说明 |
|------|------|------|
| 复盘报告目录 | `client/sdk/AI/docs/retrospective/reports/insight-extraction/toolchain-dev/retrospective-llvm-dev-env-and-build-20260702/` | 本次复盘的完整报告 |
| README.md | 同上 | 项目概览与导航 |
| execution-retrospective.md | 同上 | 执行过程复盘 |
| insight-extraction.md | 同上 | 洞察萃取 |
| export-suggestions.md | 同上 | 本文档 |

## 二、后续建议的行动

### 2.1 立即执行（高优先级）

- [x] 清理或归档 clang.log 和 gcc.log，避免仓库膨胀 → 已移动到 `.temp/logs/`
- [x] 在项目的构建说明中，明确推荐用 `CC=/opt/conda/bin/gcc CXX=/opt/conda/bin/g++` 构建 → 已更新 [README.md](../../../../../) 和 [entrypoint.sh](../../../../../../external/multica-ai/multica/docker/entrypoint.sh)
- [x] 配置新的远程 SSH 配置，把 `llvm-dev` 添加到 `~/.ssh/config` → 已创建配置，内容如下：
  ```
  Host llvm-dev
      HostName 127.0.0.1
      Port 2222
      User dev
      StrictHostKeyChecking accept-new
      ServerAliveInterval 30
      ServerAliveCountMax 6
  ```

### 2.2 短期执行（中优先级）

- [x] 正式确认编译器优先级策略：默认使用 GCC 构建，Clang 仅用于兼容性检查或代码质量验证；原因是 `vta/vta_hw` 中的 VLA 初始化写法可被 GCC 接受但会被 Clang 22 拒绝
- [x] 在 Dockerfile 里预配置默认编译器（`CC/CXX`）→ 已更新 `Dockerfile`
- [x] 把本次的“重构三步法”加入到团队工程文档 → 已更新 [development-standards.md](../../../../../development-standards.md)

### 2.3 长期规划（低优先级）

- [x] 评估是否需要修复 VTA 源码，让其符合 C++ 标准（避免对编译器的依赖）→ 已评估：当前不需要立即修改挂载源码；现阶段以 GCC 作为稳定构建路径，若未来必须恢复 Clang 全量构建，再单独推进源码标准化修复
- [x] 把本项目的 Docker 构建最佳实践（阿里云源、基础镜像复用、默认编译器统一）提取为通用模板 → 已新增 `server/dev-env/README.md`
- [x] 建立定期清理旧镜像的机制 → 已新增 `cleanup_images.py`，默认 dry-run，`--apply` 才会真实删除

## 三、可复用的知识片段

### 3.1 快速切换编译器构建

```bash
# 在 llvm-dev 容器内
cd /workspace/libs/npu_tvm

# 用 GCC 构建（推荐）
CC=/opt/conda/bin/gcc CXX=/opt/conda/bin/g++ inv rebuild

# 或者用 Clang 构建（用于代码质量检查，但会失败在 VTA 部分）
CC=/opt/conda/bin/clang CXX=/opt/conda/bin/clang++ inv rebuild
```

### 3.2 解决 SSH host key 变化问题

```bash
# 宿主机上清除旧的 host key
ssh-keygen -f "~/.ssh/known_hosts" -R "[127.0.0.1]:2222"

# 然后重新连接
ssh -p 2222 dev@127.0.0.1
```

### 3.3 镜像/环境命名原则

1. 用功能命名，不用版本号命名
2. 版本信息放在基础镜像标签或注释里
3. 保持名称稳定，便于长期使用

## 四、归档与备份建议

### 4.1 备份什么

- [ ] 保留本次的两个构建日志（clang.log 和 gcc.log）至少一段时间
- [ ] 考虑把 llvm-dev 镜像导出为 tar 备份：`docker save localhost/llvm-dev:latest | gzip > llvm-dev-20260702.tar.gz`

### 4.2 清理什么

- [ ] 旧的 llvm21-dev 镜像（如果确认不再需要）
- [ ] 旧的构建产物（如果 build 目录过大，可以考虑定期清理）

## 五、与其他资产的关联

- 本次任务的记忆项目：见 memory 目录下的相关总结
- 相关知识库条目：可考虑把“编译器兼容性问题处理”加入到知识库

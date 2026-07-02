---
id: "retrospective-llvm-dev-mount-permission-fix-20260702-export"
title: "导出清单"
source: ".trae/specs/document-mount-permission-retrospective/spec.md"
---
# 导出清单

## 一、本次已交付的资产

### 1.1 权限治理实现

| 资产 | 位置 | 说明 |
|------|------|------|
| 运行期权限模型 | `server/dev-env/llvm-dev/docker/entrypoint.sh` | 负责宿主机 UID/GID 映射、镜像内目录初始化、非 root 会话入口，不触碰绑定挂载目录 |
| 验证链脚本 | `server/dev-env/llvm-dev/bin/run.py` | 负责宿主机零漂移比对、容器视图核对、非 root 读写探针 |
| 环境使用手册 | `server/dev-env/llvm-dev/docs/README.md` | 说明零漂移策略、工具边界、修复命令与示例 |

### 1.2 历史污染修复工具

| 资产 | 位置 | 说明 |
|------|------|------|
| 主入口 | `server/dev-env/llvm-dev/bin/fix_mount_permissions.py` | 通用挂载子目录权限修复工具，支持 `--dry-run`、`--uid`、`--gid`、`--confirm-non-build` |
| 兼容入口 | `server/dev-env/llvm-dev/bin/fix_build_permissions.py` | 历史命令兼容包装器，内部转发到主入口 |
| 安全边界 | `server/dev-env/llvm-dev/docs/README.md` | 记录默认只放行 `build` / `build_*`，非 `build` 目录必须显式确认 |

### 1.3 复盘知识资产

| 资产 | 位置 | 说明 |
|------|------|------|
| 复盘目录 | `client/sdk/AI/docs/retrospective/reports/insight-extraction/retrospective-llvm-dev-mount-permission-fix-20260702/` | 本次任务四件套归档位置 |
| `README.md` | 同上 | 复盘概览、导航与关联资源 |
| `execution-retrospective.md` | 同上 | 事实链、决策点、问题与修复过程 |
| `insight-extraction.md` | 同上 | 方法论、工程边界、安全护栏与验证模型 |
| `export-suggestions.md` | 同上 | 本文档 |

## 二、推荐复用途径

### 2.1 日常开发默认路径

- 启动或回归验证 `llvm-dev` 环境时，继续使用 `python3 bin/run.py`
- 把 `run.py` 输出视为权限治理回归测试，不要把它当成“自动修权限”脚本
- 文档与口头说明统一使用 `fix_mount_permissions.py` 作为主入口名

### 2.2 遇到历史污染时的标准处理

优先执行 dry-run：

```bash
cd /media/pc/data/ai/notebook/server/dev-env/llvm-dev
python3 bin/fix_mount_permissions.py --dry-run \
  /media/pc/data/ai/notebook/server/libs/npu_tvm/build
```

确认计划无误后再实际修复：

```bash
cd /media/pc/data/ai/notebook/server/dev-env/llvm-dev
python3 bin/fix_mount_permissions.py \
  /media/pc/data/ai/notebook/server/libs/npu_tvm/build
```

如果目标不是 `build` 类目录，必须逐路径确认：

```bash
cd /media/pc/data/ai/notebook/server/dev-env/llvm-dev
python3 bin/fix_mount_permissions.py --dry-run \
  --confirm-non-build /media/pc/data/ai/notebook/server/libs/npu_tvm/3rdparty \
  /media/pc/data/ai/notebook/server/libs/npu_tvm/3rdparty
```

### 2.3 历史命令兼容说明

- 老文档、老习惯仍可短期使用 `python3 bin/fix_build_permissions.py ...`
- 新增说明、培训、脚本引用统一改用 `fix_mount_permissions.py`
- 后续若要收敛兼容入口，应先完成全仓搜索与文档替换，再考虑移除

## 三、自动策略与人工修复的边界卡片

### 3.1 自动策略负责什么

- 创建/调整容器内开发用户，使 UID/GID 与宿主机映射一致
- 初始化镜像内自建目录，例如 `/workspace`、`/workspace/libs`、`/workspace/.container-runtime`
- 验证宿主机权限零漂移、容器视图一致性与非 root 业务可用性

### 3.2 自动策略不做什么

- 不对 `/workspace/libs/npu_tvm`、`/workspace/libs/npuusertools` 及其既有文件执行 `chmod` / `chown`
- 不在启动期隐式修复任何历史遗留的异常属主目录
- 不把高风险宿主机改写操作隐藏在入口脚本中

### 3.3 人工修复工具负责什么

- 修复显式指定挂载子目录及其子项的属主/属组
- 对默认安全目标直接支持，对高风险目标要求逐路径确认
- 提供 `--dry-run` 计划预览与权限不足提示

## 四、后续建议

### 4.1 立即执行

- [x] 在复盘体系中沉淀本次四件套与索引入口
- [x] 统一 README 对外口径，主入口名称使用 `fix_mount_permissions.py`
- [x] 保留 `fix_build_permissions.py` 兼容层，降低迁移摩擦

### 4.2 短期跟进

- [ ] 对仓库内仍引用 `fix_build_permissions.py` 的脚本或文档做一次全量排查，评估是否需要统一替换为主入口名
- [ ] 视需要把“三联证据法”抽成其他挂载式环境可直接复用的验证模板
- [ ] 若后续出现更多历史污染场景，优先补充示例与风险提示，而不是放宽默认权限护栏

### 4.3 长期维护

- [ ] 将“零漂移优先于启动期自动修权限”纳入挂载式开发环境通用规范
- [ ] 在后续环境演进中继续坚持“默认保守、显式确认、兼容迁移”的工具设计原则
- [ ] 若未来要移除兼容入口，提前准备替换清单、迁移公告和使用统计

## 五、可复制的最小操作协议

1. 先运行 `python3 bin/run.py`，确认当前流程没有制造新的权限漂移
2. 若仍有历史脏目录阻塞构建，先执行 `fix_mount_permissions.py --dry-run`
3. 对非 `build` 目录必须补上 `--confirm-non-build PATH`
4. 只有在修复计划与目标路径完全确认后，才执行真实修复
5. 所有新增文档、说明、答复统一使用主入口名称，兼容入口只作过渡说明

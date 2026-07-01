# 本地目录权限修复报告

## 1. 任务范围

- 目标目录：`/media/pc/data/ai/notebook/client/sdk/AI`
- 本次仅实施可直接落地的本地权限修复，不修改 `tasks.md`、`checklist.md`
- 修复目标：
  - 为目录递归补齐 `setgid`
  - 为目录递归补齐默认 ACL
  - 移除目录 `other` 访问权限
  - 保留现有用户/组可用性，不修改属主属组

## 2. 新增交付物

- `apply-local-folder-permission-fix.sh`
- `audit-log-lib.sh`
- `collect-cross-system-permission-evidence.sh`
- `validate-access-matrix.sh`
- `verify-cross-system-permission-fix.sh`
- `report.md`
- 运行证据目录：`evidence/`

## 3. 修复前基线

### 3.1 文件系统与根目录状态

- 文件系统：`xfs`
- 修复前根目录权限：`775`
- 修复前根目录属主属组：`ai:ai`
- 修复前根目录 ACL：

```text
user::rwx
group::rwx
other::r-x
```

### 3.2 修复前统计

来源：`evidence/20260701-101123-apply/pre_counts.txt`

| 指标 | 数值 |
|---|---:|
| 目录总数 | 380 |
| 未设置 setgid 的目录数 | 380 |
| 仍开放 other 访问的目录数 | 380 |
| 缺少默认 ACL 的目录数 | 380 |

结论：修复前目标树内全部目录都未设置 `setgid`、未配置默认 ACL，且目录对 `other` 仍保留访问能力。

## 4. 已实施项

### 4.1 本地权限修复

已执行脚本：`apply-local-folder-permission-fix.sh`

实际实施动作：

```bash
find "$TARGET_DIR" -type d -exec chmod g+s,o-rwx {} +
find "$TARGET_DIR" -type d -exec setfacl -m d:u::rwx,d:g::rwx,d:o::---,d:m::rwx {} +
```

说明：

- `chmod g+s` 为所有目录补齐 `setgid`，保证后续新建子目录/文件优先继承父目录组
- `chmod o-rwx` 移除所有目录的 `other` 访问权限，避免未授权旁路访问
- `setfacl -m d:u::rwx,d:g::rwx,d:o::---,d:m::rwx` 为所有目录补齐默认 ACL，保证后续新建内容继续继承 owner/group 协作权限
- 未修改任何目录的属主和属组
- 修复前后属主属组分布直方图一致，均为 `ai:ai -> 380`

### 4.2 证据采集与校验

已执行脚本：

- `collect-cross-system-permission-evidence.sh`
- `verify-cross-system-permission-fix.sh`

关键证据目录：

- apply：`evidence/20260701-101123-apply`
- collect：`evidence/20260701-101220-collect-post-fix`
- verify：`evidence/20260701-101223-verify`

## 5. 验证结果

### 5.1 修复后权限状态

来源：

- `evidence/20260701-101123-apply/post_counts.txt`
- `evidence/20260701-101123-apply/post_root_stat.txt`
- `evidence/20260701-101123-apply/post_root_acl.txt`

修复后根目录状态：

```text
mode=drwxrws--- perm=2770 owner=ai group=ai path=/media/pc/data/ai/notebook/client/sdk/AI
```

修复后根目录 ACL：

```text
user::rwx
group::rwx
other::---
default:user::rwx
default:group::rwx
default:mask::rwx
default:other::---
```

修复后统计：

| 指标 | 数值 |
|---|---:|
| 目录总数 | 380 |
| 未设置 setgid 的目录数 | 0 |
| 仍开放 other 访问的目录数 | 0 |
| 缺少默认 ACL 的目录数 | 0 |

### 5.2 采集结果

来源：`evidence/20260701-101220-collect-post-fix/summary.txt`

| 指标 | 数值 |
|---|---:|
| 目录总数 | 382 |
| 未设置 setgid 的目录数 | 0 |
| 仍开放 other 访问的目录数 | 0 |
| 缺少默认 ACL 的目录数 | 0 |

说明：采集阶段目录数变为 `382`，是因为运行脚本后在目标目录下新增了 `evidence/` 及其子目录；新增目录同样继承了修复后的权限策略。

### 5.3 校验结果

来源：`evidence/20260701-101223-verify/verify_summary.txt`

| 校验项 | 结果 |
|---|---|
| 目录未设置 setgid 数量为 0 | PASS |
| 目录 `other` 访问数量为 0 | PASS |
| 缺少默认 ACL 的目录数量为 0 | PASS |
| 根目录权限为 `2770` | PASS |
| 根目录存在 `setgid` | PASS |
| 根目录默认 ACL `default:user::rwx` | PASS |
| 根目录默认 ACL `default:group::rwx` | PASS |
| 根目录默认 ACL `default:other::---` | PASS |
| 属主属组分布未变化 | PASS |
| 综合校验结果 | PASS |

说明：校验阶段目录数为 `383`，相比采集阶段再次增加 1 个目录，来源于新增的 verify 证据目录本身；该目录同样符合修复后的权限策略。

### 5.4 访问矩阵与 JSONL 审计

<!-- ACCESS_MATRIX_RESULTS:BEGIN -->
- 待执行：运行 `validate-access-matrix.sh` 后，此处会回填本地合法访问、SSH 未授权失败、静态 `other` 拦截的验证结果。
- 审计日志文件：`evidence/access-audit.jsonl`
<!-- ACCESS_MATRIX_RESULTS:END -->

## 6. 已完成与未完成边界

### 6.1 本次已完成

- 已完成目标目录的本地目录权限收敛
- 已完成目录 `setgid` 补齐
- 已完成目录默认 ACL 补齐
- 已完成目录 `other` 访问移除
- 已完成修复前/后证据采集
- 已完成本地校验并输出 PASS 结果

### 6.2 本次未直接实施

以下内容属于跨系统治理或更高权限运维范畴，本次未直接在本地落地：

- 共享服务配置检查与调整，例如 Samba、NFS、9p、FUSE 或其他网盘/同步代理
- 挂载参数检查，例如 ACL 挂载选项、UID/GID 映射、权限掩码、缓存与身份映射参数
- 来源系统身份认证链路梳理与验证
- 跨系统账户到本地 UID/GID 或组的映射策略确认
- 至少两类来源环境的真实跨系统访问验证

## 7. 管理员待执行项

建议管理员继续执行以下事项，以完成“跨系统文件夹权限修复”的全链路闭环：

1. 核查目标目录的实际共享出口与挂载方式，明确是否经过 Samba、NFS、宿主机共享、同步盘或容器卷映射
2. 核查共享服务与挂载参数是否保留 ACL、`setgid` 和组继承行为，避免远端访问侧绕过本地目录策略
3. 明确各来源系统用户身份到本地 `UID/GID/组` 的映射规则，输出“来源系统 -> 身份 -> 本地主体 -> 可访问资源”的映射表
4. 为合法用户、受限用户、管理员、未授权访问者分别执行真实访问验证，至少覆盖两类来源环境
5. 配置并验证审计日志，至少记录身份、来源、目标路径、动作、结果、失败原因、时间戳
6. 对需要跨组协作的目录补充命名 ACL 规则；若存在非 `ai:ai` 协作组，应按业务最小权限原则精细化授权
7. 评估文件级权限是否也需要同步收敛；本次修复聚焦目录权限与目录默认 ACL，未批量改写既有普通文件权限位

## 8. 结论

- 本地可直接实施的目录权限修复已完成
- 目标目录已从“全部目录缺少 `setgid` / 默认 ACL，且 `other` 可访问”的状态，收敛到“全部目录具备 `setgid`、默认 ACL 且 `other` 无访问”
- 属主属组可用性保持不变，根目录最终状态为 `ai:ai`、权限 `2770`
- 本地校验结果为 `PASS`
- 已补充 JSONL 审计日志与访问矩阵脚本，跨系统认证映射与更丰富来源环境验证仍需管理员继续完成

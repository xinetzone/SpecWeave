# openkylin-dev-container - Independent Review

审查对象：`.trae/specs/infra-env/openkylin-dev-container/`（spec.md + tasks.md + evidence/）与实现产物 `apps/dev-tools/openkylin-wsl-devkit/openkylin-dev-container/`、文档 `docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md`。

审查方式：全新上下文只读独立核验（重跑命令、重读日志，不依赖实施者记忆），对照 spec.md AC-1~AC-6 与 tasks.md TR-1.1~TR-5.2 逐项复核。

## Checkpoints

- [x] CP-R1: 工程文件清单齐备，无第三方运行时依赖
  - **Type**: `rule`
  - **Covers**: AC-1 / TR-1.1
  - **Evidence**: 独立 `Get-ChildItem` 实测 13 个文件（Containerfile、entrypoint.sh、healthcheck.sh、conf×5、scripts×4、README.md）；提交 `6449ae135` 清单一致；build/smoke 为 bash+pwsh 双环境、无 pip 依赖声明。

- [x] CP-R2: 基底与软件源约束
  - **Type**: `rule`
  - **Covers**: AC-2 / TR-2.1 / TR-2.2
  - **Evidence**: Containerfile 首行 `FROM localhost/openkylin:3.0`（用户裁定基底，spec Constraints 同步）；grep `add-apt-repository|sources.list` 无命中（无第三方 apt 源）；容器契约 G3 三必需参数（`--device /dev/fuse` + `--security-opt label=disable` + `--cgroupns=host`）出现于 build/smoke 脚本，全仓库无 `--privileged`。

- [x] CP-R3: 构建成功且镜像存在
  - **Type**: `rule`
  - **Covers**: AC-3 / TR-3.1
  - **Evidence**: 独立重跑 `podman image exists localhost/openkylin-dev:3.0` 退出码 0；构建日志 `evidence/build-20261009.log` 终态成功（6 次迭代：PEP 668 → 中断 → UID 冲突 → subuid → OCI 格式 → 成功）。

- [x] CP-R4: 冒烟探针与启动健康
  - **Type**: `rule`
  - **Covers**: AC-4 / TR-4.1 / TR-4.2
  - **Evidence**: 重读 `evidence/smoke-20261009.log`：P1-P8 全 PASS（sshd -t / jupyter / supervisord / zh_CN.UTF-8 / Asia/Shanghai / devuser uid=1000 / subuid / podman 就绪）；P8b live rootless 按 spec Assumptions 记录 `ENV-LIMIT`（rootless 外层宿主嵌套 userns EPERM，镜像就绪已验）；全量启动 HEALTHCHECK healthy（sshd + jupyter）。见发现 F-1。

- [x] CP-R5: 脚本静态校验与无拉取冒烟
  - **Type**: `rule`
  - **Covers**: AC-5 / TR-5.2（bash -n）
  - **Evidence**: 独立重跑 `bash -n build.sh`、`bash -n smoke.sh` 均退出码 0；smoke 脚本含 `--pull=never`，日志无任何 registry 拉取记录。

- [x] CP-U1: 文档五要素质量
  - **Type**: `rubric`
  - **Covers**: AC-6 / TR-5.1
  - **Scale**: 1-5
  - **Anchors**: 1 = 零散说明不可复现；3 = 覆盖用途/构建/运行/验证/边界五要素且可复现；5 = 五要素齐备 + 冒烟示例 + 故障排查表 + 已知边界 + 与 okw/模式文档互链
  - **Pass Threshold**: >= 4
  - **Evidence**: 得分 **5**。`05-openkylin-dev-container.md` 含用途定位、双环境构建、运行（G3 三必需 + 命令示例 + 安全边界）、冒烟探针清单、已知边界（ENV-LIMIT / amd64 / 不做什么）、构建期故障排查表（PEP 668 / UID 冲突 / subuid / OCI / locale），互链 `03-podman-rootless.md` 与模式文档 `wsl-rootfs-oci-image-export`；okw README 镜像章节可复现构建。

- [x] CP-R6: docs 指南与 toctree 接入
  - **Type**: `rule`
  - **Covers**: TR-5.2
  - **Evidence**: `Test-Path 05-openkylin-dev-container.md` = True；index.md「按任务阅读」新增行 + toctree 含 `05-openkylin-dev-container`。

## Review History

### Review R1
- **Result**: `pass`
- **Evidence**: 全部 6 个检查点通过（5 rule + 1 rubric 得 5）；每条 AC/TR 有独立重跑证据；可行动发现 0 条，建议性发现 3 条（见下，不阻塞验收）。
- **Findings**:
  - **F-1**（advisory，低）：AC-4 字面「Rootless 为 true」在 rootless 外层宿主（Windows Podman Machine）路径未完全达成，实测降级为 `ENV-LIMIT`；spec Assumptions 与 tasks.md TR-4.2 已授权该降级。建议后续在 rootful 外层宿主（openKylin WSL 发行版内 podman）补 live rootless 全量验证，以完全满足字面 AC；无需改 spec（假设条款即治理依据）。
  - **F-2**（advisory，低）：WSL 发行版内真实构建未执行（spec 开放问题 OQ-2）。当前覆盖：Windows Podman Machine 真实验证 + `bash -n`/dry-run 静态覆盖。建议 Task 6 之后在 openKylin WSL 内补跑 `build.sh` 留存证据。
  - **F-3**（advisory，低）：Jupyter 默认无 token、SSH 密码认证，仅限本地开发；已文档化于指南「安全边界」与 README。禁止对外暴露 22/8888 端口；如需公网使用应先加固（密钥认证 + token/密码）。
- **Recommended Issues**: 无（全部 advisory，不产生 pending issue）。

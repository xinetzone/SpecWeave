---
title: "xmnn 容器 unhealthy 误报诊断与修复复盘"
date: 2026-08-12
session: sc-20260812-xmnn-container-health
scenario: problem-solving
chain: F→V→C→R→I→E
source: "conversation sc-20260812-xmnn-container-health"
category: task-reports
---

# xmnn 容器 unhealthy 误报诊断与修复复盘

## R：复盘事实清单（G1门检查）

### 现象事实
- F-001: 4 个运行中容器全部显示 `unhealthy`：chaos-jupyter、xmnn-whl-builder-jupyter、xmnn-runtime-jupyter、chaos-ai-portable
- F-002: 健康日志统一输出 `sshd port 22: FAILED (process not running)`
- F-003: 健康日志统一输出 `docker port /var/run/docker.sock: FAILED (socket not found)`
- F-004: 健康日志统一输出 `jupyter port 8888: OK (HTTP 200)`
- F-005: chaos-jupyter 健康日志 `FailingStreak: 58`（连续失败 58 次）
- F-006: 探针脚本 healthcheck.sh 逻辑：`ENABLE_SSH`/`ENABLE_DOCKER`/`ENABLE_JUPYTER` 默认 `yes`，任一 FAIL 即判 UNHEALTHY
- F-007: 容器 env 含 `ENABLE_SSH=yes`、`ENABLE_DOCKER=yes`

### 部署形态
- F-008: 3 个容器（chaos-jupyter / xmnn-whl-builder-jupyter / xmnn-runtime-jupyter）为 Jupyter-only 部署，端口映射 `127.0.0.1:88xx→8888`，无 22 端口映射、无 docker.sock 挂载
- F-009: chaos-ai-portable 为完整开发容器，由 WSL 侧 `/root/chaos-ai-build/docker-compose.yml`（项目 `chaos-ai-build`）管理，supervisord 托管 sshd / dockerd / jupyter 三服务
- F-010: D 盘 `docker-compose.yml` 与 WSL `/root/chaos-ai-build/docker-compose.yml` 是两份不同配置，后者保留 legacy 服务

### 修复执行
- F-011: 创建 fix-container-health.sh 修复脚本，对 3 个 Jupyter 容器 `--recreate` 注入 `-e ENABLE_SSH=no -e ENABLE_DOCKER=no`
- F-012: 修复脚本最初修补的是 D 盘 docker-compose.yml，但 chaos-ai-portable 实际由 WSL `/root/chaos-ai-build/docker-compose.yml` 管理，需修补实际管理文件
- F-013: `/root/chaos-ai-build/docker-compose.yml` 注入 `ENABLE_SSH=no`/`ENABLE_DOCKER=no` 到 dev-portable environment 后 `docker compose up -d dev-portable` 重建
- F-014: chaos-ai-portable 重建后 `supervisorctl status` 确认 sshd / dockerd / jupyter 均 RUNNING

### 修复结果
- F-015: 4 个容器全部转为 `healthy`
- F-016: supervisorctl 确认 sshd (PID 164) / dockerd (PID 165) / jupyter (PID 167) 真实运行，无 FAILED/FATAL

---

## I：核心洞察（G2门检查）

### 洞察1：健康检查状态 ≠ 服务健康状态——探针-部署模式错配
- **陈述**：容器标红 `unhealthy` 但核心服务完全可用（Jupyter HTTP 200）。`unhealthy` 源于健康探针把「sshd 运行 + docker.sock 存在 + Jupyter HTTP」三件事强绑定为一个布尔结果，而 Jupyter-only 容器本就不该运行 sshd、本就没有 docker.sock。
- **证据**：F-002/F-003/F-004（探针明细）、F-008（Jupyter-only 部署形态）、F-015/F-016（修复后 healthy 且服务真实运行）
- **反常识**：挑战了「unhealthy = 服务故障」的默认假设——容器监控标签反映的是探针判定，而非服务真实可用性；探针假设与部署形态错配时，监控会系统性误报。
- **行动**：探针应支持按部署模式启用/禁用对应 `ENABLE_*` 检测项，而非默认全开。

### 洞察2：有开关 ≠ 会用开关——默认值在专用模式下成为默认坑
- **陈述**：探针已暴露 `ENABLE_*` 开关（F-006），但容器启动时未显式关闭无关项（F-007），导致默认 `yes` 在专用部署形态下成为系统性误报源。
- **证据**：F-006/F-007（默认全开但容器不运行对应服务）、F-011（显式注入开关后消除误报）
- **反常识**：挑战了「默认全开更安全」的假设——在 Jupyter-only 部署中，默认全开反而制造误报；默认值应随部署模式裁剪，而非运行时依赖人工关闭。
- **行动**：为专用部署形态固化默认关闭策略（启动脚本/compose 模板层），一处修复多处生效。

### 洞察3：问题覆盖面越广，越指向配置/模板而非单点故障
- **陈述**：4 个不同镜像、不同管理方式的容器（3 个 ad-hoc + 1 个 compose）出现完全一致的误报（F-002/F-003 跨容器一致），指向共享的「探针默认配置」这一系统级根因，而非各容器独立的运行时故障。
- **证据**：F-001/F-002/F-003（跨 4 容器一致的探针输出）、F-016（supervisorctl 证实服务真实可用，排除运行时故障）
- **反常识**：挑战了「每个容器单独排查」的思路——同类现象在异构容器上一致复现，应优先检查共享配置层（探针脚本/默认值/管理模板），而非逐个容器调试。
- **行动**：诊断时先判断「单点 vs 系统性」——跨容器一致的症状优先检查共享配置层。

---

## V：对抗审查（F 后强制）

### 魔鬼代言人视角
1. **攻击**：会不会 sshd 本该运行但崩了？Jupyter 容器没启动 sshd 是不是异常？
   - **采纳修正**：通过 docker ps 确认无 22 端口映射、启动命令为 `exec /opt/…jupyter`（F-008），不启动 sshd 是预期行为而非崩溃；排除该假设。
2. **攻击**：chaos-ai-portable 是完整开发容器，关闭 sshd/dockerd 探针会不会掩盖真实故障？
   - **采纳修正**：修复后用 `supervisorctl status` 实证 sshd/dockerd/jupyter 均 RUNNING（F-016），确认关闭探针不掩盖真实问题；并在复盘中显式记录该风险与验证方式。

### 新人视角
1. **攻击**：看到 `unhealthy` 会以为是服务故障，会不会误导排查？
   - **采纳修正**：在报告与修复脚本注释中明确「unhealthy 是探针-模式错配误报」，并在验证环节展示探针明细（Jupyter OK）而非仅看状态标签。

### 老板视角
1. **攻击**：4 个容器标红影响 CI/监控排障判断，ROI 如何？
   - **采纳修正**：修复为最小改动（仅注入探针开关，不引入 sshd/docker 依赖），消除误报同时保留服务可用性；记录修复脚本供复用。

### 未来视角（6个月后）
1. **攻击**：若后续给 Jupyter 容器加回 sshd/docker 能力，这些 `no` 开关会导致探针漏检真实故障？
   - **采纳修正**：在报告行动项中记录「探针开关应与部署形态联动」——若部署形态升级，需同步开启对应探针，避免漏检。

---

## E：模式萃取（G3门检查）

### 模式：探针-部署模式对齐（Healthcheck-Mode Alignment）

**模式名称**：健康探针与部署形态对齐模式

**触发场景**：
- Docker 容器配置了健康探针（HEALTHCHECK）
- 同一探针脚本用于多种部署形态（如 Jupyter-only / ssh+docker 完整开发 / 生产服务）
- 出现探针强检「本部署形态不需要的服务」导致的系统性 unhealthy 误报

**核心步骤**：
1. **识别部署形态**：明确容器提供哪些服务（Jupyter-only / ssh+docker / full）
2. **探针按形态裁剪**：用 `ENABLE_*` 开关按部署形态启用/禁用对应检测项，不默认全开
3. **模板层固化**：在启动脚本 / compose 模板中固化对应形态的开关配置，而非运行时依赖人工注入
4. **实证验证**：修复后不仅看状态标签，还要 `supervisorctl status` / 探针明细实证服务真实可用，排除掩盖真实故障
5. **覆盖所有管理方**：容器若由 compose 管理，需确认实际管理文件（可能存在于 WSL 侧而非源码目录），修补实际文件而非副本

**反模式**：
1. ❌ **反模式1：探针默认全开**：不按部署形态裁剪 `ENABLE_*`，导致专用容器（Jupyter-only）系统性误报（F-002/F-003）
2. ❌ **反模式2：为满足探针强加无关服务**：为让 `unhealthy` 变绿而给 Jupyter 容器硬加 sshd/docker，违背「运行时精简」设计
3. ❌ **反模式3：只看 unhealthy 标签**：不查探针明细（Jupyter OK）就重启/重建，可能掩盖真实故障或引入无关变更
4. ❌ **反模式4：修补错误的配置文件**：compose 管理的容器修补源码目录副本而非实际管理文件（F-010/F-012），导致修复不生效

**检验标准**：
- 所有容器健康状态与其实际部署形态一致（Jupyter-only 容器不再因 sshd/docker 缺失标红）
- 关闭的探针对应服务经实证确认不运行或正常运行（无掩盖真实故障）
- 探针开关配置固化在模板层，新起容器默认正确
- 修复覆盖实际管理文件，`docker compose config --quiet` 校验 YAML 有效

**迁移示例**：
```bash
# Jupyter-only 容器启动时显式关闭无关探针
docker run -d \
  --name chaos-jupyter \
  -p 127.0.0.1:8899:8888 \
  -e ENABLE_SSH=no \
  -e ENABLE_DOCKER=no \
  -e ENABLE_JUPYTER=yes \
  -e JUPYTER_PORT=8888 \
  xmnn-runtime:latest \
  bash -c "exec /opt/venv/bin/jupyter lab --no-browser --ip=0.0.0.0 --port=8888 --ServerApp.allow_root=True --ServerApp.token=xmnn"
```

---

## C：原子行动项（G4门检查）

- **A-001**：4 个容器健康状态修复（已完成）
  - 验收标准：`docker ps` 4 个容器均显示 `healthy`
  - 状态：已完成 ✅

- **A-002**：chaos-ai-portable 服务实证（已完成）
  - 验收标准：`docker exec chaos-ai-portable supervisorctl status` 显示 sshd/dockerd/jupyter 均 RUNNING，无 FAILED
  - 状态：已完成 ✅

- **A-003**：修复脚本入库供复用（完成）
  - 验收标准：fix-container-health.sh 保留于 `scripts/`，支持 `--recreate` / `--restart-only` 两模式
  - 状态：已完成 ✅

- **A-004**：报告归档至 task-reports 分类（本报告）
  - 验收标准：frontmatter 完整、source 溯源、链接有效
  - 状态：本次完成

- **A-005**：向工具链反馈探针设计（建议，待执行）
  - 验收标准：评估 healthcheck.sh 是否应依据部署形态默认裁剪 `ENABLE_*`，或文档化默认全开的前提
  - 优先级：P1

---

## 执行日志（CMD-LOG）

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20260812-xmnn-container-health | msg=识别为「问题解决」场景
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20260812-xmnn-container-health | msg=选择 F→V→C→R→I→E 诊断链路
[CMD-LOG] | level=INFO | cmd=export-report | step=S0 | event=CMD_START | session=exprt-20260812-xmnn-container-health | msg=导出复盘报告
```

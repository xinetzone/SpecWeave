# apps/containers 组级治理变更日志

> 组级资产（AGENTS.md / .agents/ / docs/ / README.md）的变更记录。
> 成员内变更见各成员 `.agents/CHANGELOG.md`（jupyter-podman-rootless / client）。

## 2026-09-15

- **init** | 组级治理层首次建立：新增 `AGENTS.md`（组级路由入口 + G1-G4 跨成员契约）、
  `README.md`（人类入口）、`.agents/`（README + rules/shared-package.md + 6 占位目录）、
  `docs/`（README 索引 + 00-overview + 01-getting-started）。
  - 背景：2026-09-15 OKF 重构后本组演化为 builder + client + shared 三成员结构
    （新增 jpman-common 共享包、overlay_core 声明式栈内核、base-rootless 单一事实源），
    组层治理资产缺位、client/.agents 预留的 L1 回退层悬空。
  - 组级唯一规则主题 `shared-package.md`：承载 G1（连接层唯一事实源/零栈知识/单向依赖）
    与 G2（shared 先安装）权威定义，并修正 `ContainerConfig` 归属误引
    （实为 client/tasks/utils.py:197，非 shared/containers.py）。
  - 同步修复：client/.agents/README.md 父级继承表 L1 行（"当前不存在"→实际入口）；
    apps/AGENTS.md 嵌套路由树补组层节点、应用路由表补 containers/shared 条目。

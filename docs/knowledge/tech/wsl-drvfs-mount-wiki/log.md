# WSL DrvFs 挂载教程 - 变更日志

## 2026-10-13：初始版本（v1.0）

基于微软官方归档博文 *File System Improvements to the Windows Subsystem for Linux*（2017，Sven Groot，Windows Insider build 16176）的一次系统化学习，采用七概念方法论场景 4（知识沉淀）链路 **R→I→E→V→C**（depth=standard），session=`sc-20261013-wsl-drvfs-mount-wiki`。

内容敏感度预检：**公开内容**（微软官方公开归档页，无访问控制）→ 产出物入根 `docs/knowledge/tech/`。

### R 阶段（事实采集，G1）

- 从主信源 S-001 正文五节采集 31 条事实，从同页评论区 S-003 交叉登记 6 条现场记录（F-001～F-031）。
- V 阶段补充信源 S-005a/b/c 后，追加 5 条现代演进事实（F-032～F-036），合计 **36 条**。
- 置信度分级：A=官方正文权威陈述；B=背景链接或评论区交叉核对采纳；C=评论区单源（仅现象登记，不进命令范式）。
- G1 自检：条数 36 ≥ 20；逐条复核无「因为/导致/所以/由于/从而」因果词；每条有信源与置信度；历史事实与现代事实分节登记。**G1 通过**。
- 产出：[references/01-fact-ledger.md](references/01-fact-ledger.md)。

### I 阶段（洞察，G2）

提炼 4 条四元组洞察（现象/证据/反常识/行动），均在概念文档中落地：

1. **drvfs 的「设备」是 Windows 路径名，不是 Linux 块设备。** 证据：同一 `mount -t drvfs` 的源可为 `D:`、`\\server\share`、`C:\mountpoint`（F-008/F-013/F-020），而自动挂载只覆盖有盘符卷（F-004/F-019）。反常识：Linux 传统 mount 的源是 `/dev/sdX` 或特定远程 FS 类型，drvfs 实为「借 Windows 存储栈访问」的适配层。行动：找不到存储时先问「它在 Windows 侧叫什么」。落地：00/01/02/03。
2. **权限位与大小写在 drvfs 上是「显示语义」，以实际打开结果为准。** 证据：网络 FS 恒报 0777（F-024）、只能尝试打开判断（F-025）、FAT/网络 FS 不区分大小写且不支持符号链接（F-023/F-026）。反常识：SSH、`find -perm`、`test -x` 等把权限位当真值的工具链会基于失真元数据决策。行动：安全敏感工作负载放 ext4；访问性用 open 验证。落地：04，并在 05 给出现代 `metadata` 补救选项（F-033）。
3. **网络共享的认证边界在 Windows 侧，drvfs 只复用会话、不发起认证。** 证据：WSL 无凭据参数（F-015），凭据三途径在 Windows 侧（F-016），可经 interop 调 `net.exe use`（F-017）；评论区「无报错但目录不存在」症状（F-018）。反常识：Linux 用户预期 `mount.cifs` 的 `username=`/`password=`，drvfs 刻意不提供。行动：先 Windows 侧认证、再 WSL 挂载、以实际访问验收。落地：02。
4. **能力可用性曾与 Windows build 强绑定，命令报错先查 build 而非发行版包。** 证据：功能随 build 16176 引入（F-002），15063 用户报 `unknown filesystem type 'drvfs'`、16299 可用（F-027）。反常识：Linux 世界能力随软件包升级获得，WSL 1 时代该能力随 Windows 内核提供，`apt-get update` 无效。行动：先 `ver`/`winver` 确认版本；现代 Windows 10/11 已为既有能力。落地：01 排错表、05 第一节。

**G2 通过**（四元组完整，4 ≥ 3）。

### E 阶段（萃取/文档生成，G3）

- [references/00-sources.md](references/00-sources.md)：信源登记 S-001～S-005c（归档博文、背景链接、评论区、release notes、现代文档组三篇）。
- [concepts/00-overview.md](concepts/00-overview.md)：定位、时代边界、能力矩阵、三个心智模型、适用/不适用。
- [concepts/01-drvfs-manual-mount.md](concepts/01-drvfs-manual-mount.md)：三步命令、`mkdir` 独立步骤（F-011）、历史报错表。
- [concepts/02-network-mount.md](concepts/02-network-mount.md)：两条挂载路径、引号规则、凭据边界、无报错失败排查。
- [concepts/03-ntfs-folder-volumes.md](concepts/03-ntfs-folder-volumes.md)：无盘符卷、挂载点硬约束、与 bind mount 分工表。
- [concepts/04-filesystem-semantics.md](concepts/04-filesystem-semantics.md)：语义支持矩阵、0777 对工具链的影响、性能注意。
- [concepts/05-version-and-modern-wsl.md](concepts/05-version-and-modern-wsl.md)：build 门槛、fstab 自动化历史与现代答案、DrvFs 选项、`wsl --mount` 与限制、性能布局、未竟诉求去向。
- 各级 `index.md`（根 + concepts + references）与本文件，均含 `{toctree}` 块。
- G3 自检：模式含触发场景+命令步骤+反模式（C 级污染命令、把 0777 当真实权限、在挂载命令里找凭据参数、用 apt 修内核能力）+跨场景迁移（本机多盘、企业 SMB、NAS、无盘符卷、现代 WSL 2 物理盘）。**G3 通过**。

### V 阶段（对抗审查，V 门）

- 四视角（魔鬼代言人/新人/老板/未来维护者）共 8 条意见（V1～V8），采纳 5 条实质修正：
  - V1（P0）：补现代信源 S-005a/b/c 与 05 节，全篇时代定位；
  - V2（P1）：0777 结论补现代 `metadata` 补救路径；
  - V3（P1）：C 级评论区用法隔离，fstab 给出 `mountFsTab` 现代答案；
  - V4（P1）：02 增补凭据失败症状与三步排查；
  - V5（P2）：取消 examples 层，首页保留「三条结论」保证可执行性；
  - V6（P1）：活文档标注抓取日期与 stale_after；V7/V8 记录不采纳理由。
- 详见 [references/02-adversarial-review.md](references/02-adversarial-review.md)。**V 门通过**。

### C 阶段（原子交付）

- 在 `docs/knowledge/tech/index.md` 的 toctree 注册 `wsl-drvfs-mount-wiki/index`。
- 预提交验证：Markdown 相对路径链接检查；frontmatter 完整性核对。
- 提交方式：遵循 Conventional Commits，中文主体，等待用户明确指令后执行（不自动提交）。

---

**状态**：draft
**规范**：OKF v0.2
**下次检查**：2027-10-13（stale_after），优先复评 S-005a/b/c 活文档组

# offline-delivery 独立应用抽取 - Independent Review

> 本文件在实施队列清空后创建（TRAE-spec-mode Review 阶段产物；本仓库以 `review.md` 为标准命名，`checklist.md` 为已废止历史命名）。
> 检查点由**全新上下文的只读独立审查**（Review R1）逐条取证，不采信实施者自验结论；R1 的 1 项 actionable 发现由 Task 11 修复后经 R2 复核。

- [x] CP-R1: 新应用完全自包含（无 client/shared 依赖，Containerfile 仅用产品目录内资产）
  - **Type**: `rule`
  - **Covers**: AC-1, TR-3.1
  - **Evidence**: R1 取证：`grep -rn "jpman_client|jpman_common|overlays/_shared|invoke |client/|shared/"` 命中 24 处，逐条判定**全部**为文档/规则/测试中的排除项表述与 `release/artifacts/.gitignore` 注释，无一为真实依赖；`grep bin/` 零命中；`Containerfile.xmnn-runtime` 4 处 `COPY`（`scripts/…`、`wheels/xmnn-*.whl`、`scripts/`、`smoke/`）源路径全在产品目录内

- [x] CP-R2: 交付骨架纯移动（客户可见契约逐字一致，仅 README 两处表述更新）
  - **Type**: `rule`
  - **Covers**: AC-2, TR-2.1, TR-2.2, TR-2.3
  - **Evidence**: R1 取证：六文件 `git hash-object` 与 `rev-parse HEAD:…` 比对**全部 SAME**；`README.md` diff 仅 2 hunk（4±），均为「开发仓库便捷壳」表述；`xmnnctl` CR=0/LF=454、`xmnnctl.ps1` CR=0/LF=498；骨架 `grep '\.\./'` 无命中；`compose.yaml` 含 `pull_policy: never`、无 `extends`/`build:`；override 三必需齐备且无 `privileged`

- [x] CP-R3: CLI 与现版语义等价（暂存选择序、双 tag、CRLF 守卫、归档原子性、`release.json` 字段与 torch 双键回退）
  - **Type**: `rule`
  - **Covers**: AC-3, TR-4.1, TR-4.2, TR-4.3, TR-5.2
  - **Evidence**: R1 取证：`./bin/relpack version` → `产品=xmnn-runtime|形态=cpu|镜像=localhost/xmnn-runtime:cpu|版本=1.2.1.dev0`；`--help` 覆盖 5 命令；探针 `badproduct`/`badflavor`/`unknowncmd` 均非零退出、`help` 零退出；源码核对：双 tag、`podman save | gzip -1` + `gzip -t` + 原子 `mv`、CRLF 守卫跳过 `artifacts/` 与 `.ps1/.psm1/.bat/.cmd`、`release.json` 字段与旧 `ReleaseManifest` 逐字同（仅 `pack_tool` 变更）、torch 新键优先旧键回退；Task 11 后文档字段名同步为 `archive.file`

- [x] CP-R4: client 侧零残留且内核无死代码
  - **Type**: `rule`
  - **Covers**: AC-4, TR-6.1, TR-6.2, TR-6.3, TR-6.4
  - **Evidence**: R1 取证：`grep -rn "xmnnrt|xmnn-runtime|relpack" apps/containers/client` 仅命中 `.agents/CHANGELOG.md` 与 `AGENTS.md` 的**变更日志小节**（历史条目 + 本次迁出记录）；`invoke --list` = 根7/container7/env3/quant6/xmnn10/monetize8，**无 `xmnnrt.*`**；`flavor_tag|image_flavor|image_tag_alias|torch_default` 于 `src/` 零命中，`warn_torch_flavor_mismatch` 仍有调用方；`pytest tests -q --ignore=tests/test_ast_inject.py` → **182 passed / 2 skipped / exit 0**，且 `git status tests/test_ast_inject.py` 为空（8 例失败为未触碰文件的存量差异）

- [x] CP-R5: 仓库治理资产同步（成员登记、路由表、`.gitattributes`、看板入册）
  - **Type**: `rule`
  - **Covers**: AC-5, TR-1.1, TR-1.2, TR-1.3, TR-7.1, TR-7.2, TR-7.3, TR-9.1, TR-9.2
  - **Evidence**: R1 取证：7 个路由/文档文件均登记 `offline-delivery`（`apps/containers/AGENTS.md` 四成员表 + 路由表、`apps/containers/README.md`、组级 `docs`×3、`apps/AGENTS.md`、`apps/README.md`）；`.gitattributes` 含 `**/relpack`/`**/relpack.ps1 eol=lf` 且注释改指新应用并注明便捷壳已删；`apps/containers/.agents/README.md`「四成员路由表」、`shared-package.md`「离线交付成员为脚本型成员」；`check-links.py --path apps/containers` → **exit 0**（12 条既有目录链接警告，无断链）；R1 后 F6 修复使看板 `infra-env/README.md` 第 17 行由「? 待启动」变为「✓ 完成」

- [x] CP-R6: 真机端到端可用（`pack` 产物自洽、`smoke` 经交付骨架四步通过、仓库外交付零依赖）
  - **Type**: `rule`
  - **Covers**: AC-6, TR-8.1, TR-8.2, TR-8.3, TR-10.1, TR-10.2
  - **Evidence**: R1 取证：`sha256sum`/`stat -c %s` → `c4907c7d…`/`4088086206`，与 `release.json` 逐字一致，`pack_tool=offline-delivery.relpack`；**独立重跑** `./bin/relpack smoke` 共 3 次，末次 `[ OK ] smoke 通过：…10 项守卫…全部成功`、`SUMMARY: 10 passed, 0 failed`、权威退出码 **0**，随后 `podman ps -a` 无 xmnn-runtime 容器、2225/8893 释放；`run_smoke_step` 定义于 `bin/lib/pipeline.sh`（`shift` 后 `cd "$RELEASE_DIR"`）、三处调用点 `run_smoke_step up ./xmnnctl up` 自洽（Task 10 修复确已落地）。仓库外交付（`D:\tmp-delivery-check` 硬链接）`init → load → ps → up → smoke → down` 六步 exit 0 为实施者证据，R1 以静态旁证交叉核对（骨架零 `../`、零仓库引用），未独立重跑

- [x] CP-R7: 静态质量与回归无回退（新应用 pytest、`bash -n`、pwsh7 合规、client 全量回归）
  - **Type**: `rule`
  - **Covers**: AC-7, TR-5.1, TR-5.3, TR-4.4, TR-10.3
  - **Evidence**: R1 取证：新应用 `pytest tests -q` → **56 passed**（含 Task 10 新增 3 例，行为用例在 WSL 内真实执行非 skip）；`bash -n` ×4 全 exit 0；`Parser::ParseFile` → PARSE OK；`check-pwsh7-compliance.py` → 2 合规 0 豁免；Task 11 后复跑仍 56 passed

- [x] CP-U1: 可扩展性——新增第二个交付产品所需改动面
  - **Type**: `rubric`
  - **Covers**: AC-8, TR-4.5
  - **Scale**: 1-5
  - **Anchors**: 1 = 需改 CLI 逻辑与多处硬编码；3 = 需改 CLI 若干处 + 新增文件；5 = 仅新增 `products/<名>/`（含 `product.env`）并在文档登记，CLI 代码零改动
  - **Pass Threshold**: >= 4
  - **Evidence**: R1 评分 **4/5**（≥4 通过）：产品差异已收敛到 `product.env` 九键（镜像名 / Containerfile / wheel glob / prefix / dist / 基镜像 / torch 缺省 / 骨架目录），`docs/01-quickstart.md` §4 给出可执行的新增产品步骤；扣分项为 CLI 仍内嵌骨架控制脚本名（`./xmnnctl`）与骨架端口键（`XMNN_SSH_PORT`/`XMNN_JUPYTER_PORT`），故未达「CLI 代码零改动」的 5 分锚点

- [x] CP-U2: 文档可执行——第三人可照文档从零跑通 stage → build → pack → smoke
  - **Type**: `rubric`
  - **Covers**: AC-9, TR-8.4
  - **Scale**: 1-5
  - **Anchors**: 1 = 只有文件清单；3 = 有命令但缺前置条件/失败处置；5 = 前置条件、逐命令预期输出、常见失败与处置齐备且与 CLI `--help` 一致
  - **Pass Threshold**: >= 4
  - **Evidence**: R1 评分 **4/5**（≥4 通过）：`README.md` + `docs/{README,00-overview,01-quickstart}.md` 含前置条件表、逐命令示例与预期输出、失败处置表与 Windows 等价命令，且与 `--help` 文案一致；扣分项为 `release.json` 字段名笔误与命令表参数栏错列——二者均已由 Task 11 修复（F2/F3）

## Review History

### Review R1
- **Result**: `fail`
- **Evidence**: 7 个 `rule` 检查点（CP-R1..CP-R7）全部独立取证通过；2 个 `rubric` 检查点 CP-U1=4、CP-U2=4（均达阈值）。存在 1 项 actionable 发现：
  - **F2（actionable，低严重度）**：`docs/01-quickstart.md` 把 `release.json` 的归档字段写作 `archive.name`，实际为 `archive.file`（复现：对照 `products/xmnn-runtime/release/artifacts/release.json`）；同一笔误亦见于 `.agents/rules/delivery-pipeline.md` §3
- **Findings（advisory，已记录/部分已修）**：
  - F1 `tasks.md` Task 3 证据表述过度（声称「逐一同哈希」但 5/6 因注释改写而不同）→ 已更正 Task 3 Completion Evidence
  - F3 `README.md` 命令表 `smoke` 参数栏与实现不符 → Task 11 修复
  - F4 `release/artifacts/.gitignore` 注释仍写 `invoke xmnnrt.pack`（受「骨架纯移动」约束，本次不改）→ 作为后续提案
  - F5 CLI 内嵌 `xmnnctl` 与骨架端口键（影响 CP-U1 五档锚点）→ 记为后续可选项
  - F6 看板状态「? 待启动」与完成事实不符 → Task 11 修复（`status: completed` + docgen 刷新）
  - F7 组级 `docs/01-getting-started.md` frontmatter `source` 陈旧 → Task 11 修复
  - F8 本次变更集整体未提交（工作区状态，符合「不自动 git commit」约定）
  - F9 新 CLI 未复刻旧脚本的 `XDG_RUNTIME_DIR` 兜底（Windows 经 `wsl.exe` 非登录 shell 调用时可能缺该变量）→ Task 11 修复

### Review R2（发现项修复复核）
- **Result**: `pass`
- **Evidence**:
  - F2 修复复核：`grep` 确认 `docs/01-quickstart.md` 字段名与 `release.json` 逐字一致（`wheel(file/version/size_bytes)`、`image(ref/id/torch_cpu/abi)`、`archive(file/size_bytes/sha256)`），`.agents/rules/delivery-pipeline.md` §3 改为 `archive.file`（主智能体直接核实）
  - F3 修复复核：`README.md` 命令表 `pack`/`smoke` 行参数为 `--version V`（主智能体 grep 核实）
  - F9 修复复核：`bin/lib/common.sh` 含 `ensure_xdg_runtime_dir`（仅未设/空时导出 `/run/user/<uid>`，不覆盖既有值）
  - F6/F7 修复复核：`spec.md` `status: "completed"`；看板行 `| 17 | [extract-offline-delivery-app](…) | ✓ 完成 | ✓✗✗ |`；`apps/containers/docs/01-getting-started.md` frontmatter `source` 已述四成员现状（主智能体直接读取核实）
  - 回归（Task 11 修复者原始输出）：应用内 `pytest tests -q` → **56 passed**；`check-links --path apps/containers` exit 0；`bash -n` → BASH_OK；`relpack version` 输出与基线一致
  - 复核结论：R1 的唯一 actionable 发现已闭环，全部检查点保持 `pass`，无新增可行动发现

### Review R3（验收声明与实测范围的最终校准）
- **Result**: `pass`
- **Evidence**: 独立审查指出两处措辞需放宽并已在本文档如实标注——① AC-4 的「仅命中 `.agents/CHANGELOG.md`」实际还应包含 `client/AGENTS.md` 的变更日志小节（仍属历史/记录性内容，无活跃配置残留）；② TR-8.3 的仓库外交付六步为实施者证据 + 静态旁证，未作第二轮独立重跑。两项均为证据口径问题，不改变任何检查点结论
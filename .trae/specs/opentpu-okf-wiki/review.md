# openTPU OKF Wiki 教程束 — Task 14 C 阶段独立评审记录

- 时间：2026-10-13 18:40 (+08:00)
- 评审方式：general_purpose_task 拉起 **fresh-context 独立子代理**（非 R/E/V 作者上下文），全程只读（未修改文件、未 commit、未联网），自行对拍源码、复跑门禁与独立链接枚举。
- 对象：`projects/awesome-okf-xs/doc/bundles/jishu/iot/opentpu/` 全 29 个 md。
- 基线：`external/dao/openTPU`，评审代理亲自复核 `git rev-parse HEAD = ffe997e9a8b8607b07b3d1bb3c1132db0faf044e`、`git status --porcelain` 空。

## 评审结论：PASS-WITH-NITS → 修复后 PASS

P0=0、P1=0、P2=1、P3=5。P2/P3 全部为审计簿记与措辞层问题，**所有被引事实与 572 条链接本身有效**；6 条问题已在本轮全部修复并复核。

## 发现清单与处置

| 级别 | 位置 | 问题 | 处置 |
|------|------|------|------|
| P2-1 | references/verification.md §1 | 链接总数沿用 G4 修复前快照（565/116/67），修复后独立枚举实测 572（blob 356、其他 GitHub 26、/-根 124、相对族 66=plain 63+合法跨束 3） | ✅ 已回填修复后计数，注明 C 阶段复扫 |
| P3-1 | log.md E 阶段段 | 「共 25 个 md」与分项和（17+3+4+4+1=29）矛盾 | ✅ 25→29 |
| P3-2 | concepts/14 L56 | kind 枚举只写 fpga/asic；target.py L44 `KINDS=("fpga","asic","sim")`（4 个现网 TOML 未用 sim） | ✅ 补全枚举并加 pinned 链接与使用现状说明 |
| P3-3 | examples/01 L86 | 「generic tech 的 20 个 .sv」易被读作 generic 目录有 20 个（实际 tech/generic 仅 2，20 是 RTL_SOURCES 跨目录总数） | ✅ 改为「RTL_SOURCES 列出的 20 个（分布在 vpu/mem/top/mxu/dma/seq，tech/generic 仅 2 个）」 |
| P3-4 | concepts/13 L78 | `LINE=64` 被说成「64 字节线」；64 是 fp32 字数（间距 256 字节），「64-byte lines」指 beat 不共享 | ✅ 改为「64 fp32 字（256 字节）段落，互不共享 64 字节 beat」，与 example 02 口径统一 |
| P3-5 | concepts/13 L37 | 「八个基础设施文件」只列 7 个名字（第八个是 `__init__.py`） | ✅ 显式补上 `__init__.py` |

P3-2/3/4/5 的源码事实均由主会话二次独立复核（target.py L44、offload.py L88、rtl/tech/generic 目录计数、opentpu/llm 15 文件清单）后才落改。

## 评审代理实测证据（摘录）

- 行级对拍 50 项（concepts 13-16、examples 00-02、references 关键数字为主，覆盖 CLI 11、邮箱协议常量、README 性能/PPA/tok/s 全部精确数字、两 ASIC target 面积功耗表、TOML 键值、tests/RTL 计数、validate 判据、WAITW/checks 常量等）：**全部命中**。
- 链接机械枚举（剔除围栏）：`TOTAL 572；blob 356 全 40 位且等于 PIN；forbidden 0；broken 0`。
- 编号机械核对：F-001~F-123 无缺号（A-J 十组）、C01-C32、I-1~I-5、R3-01~20 齐。
- 门禁（cwd=projects/awesome-okf-xs）：`check-bundles-index.py` rc=0（9 域/61 组/628 束五面一致）；`check-toctrees.py doc/bundles/jishu/iot/opentpu` rc=0。
- 口径：全束性能/PPA/命中率数字均带「作者报告」限定，未发现冒充实测表述；未运行仿真/位流的 blocked 声明与实际一致。
- 残余观察（不影响 pass）：offload.md §10、WAIT_TO bit8 编码等少量行级锚点未逐行追踪，所关联叙述与已核验上下文一致、无反证。

## 收口判定

6 条问题修复后，束满足 source-code-to-okf-wiki v1.5.0 的 C 门标准（零虚构、计数一致、链接全通、frontmatter 完整、口径标签到位）。**C 评审 PASS，束可交付；不 commit**（awesome-okf-xs 为 git submodule，提交需用户显式指令）。

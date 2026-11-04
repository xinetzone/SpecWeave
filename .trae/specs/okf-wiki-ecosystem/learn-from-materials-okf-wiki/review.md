---
status: "reviewed"
---

# learn-from-materials OKF Wiki 审查记录

## G1 事实门

- [x] 事实与作者观点分层：41 条事实中，作者一手操作（F-023/025/026/027）单独标注为「单源/一手实测」，不与其他事实混列。
- [x] 数字、命令、版本和许可证均有来源：仓库元数据（GitHub API）、版本 1.1.0（官方 badge）、支持格式与宿主清单（README EN/CN 双份）、CLI 链（README 命令行工具节）均可溯源。
- [x] 口径差异未被掩盖：F-033（文章宿主「豆包工作」vs 官方宿主清单）双源并列登记，不判定源文有误。

## G2 核验门

- [x] P0 核验 10 项：9 项 ✅ 通过 + 1 项 ⚠️ 口径差异（双源并列）+ 0 项 ❌。
- [x] star/fork 标注为「核验时点快照，非稳定值」，不写入结论性表述。
- [x] showcase 16 张截图明确标注为设计展示、非浏览器验收报告。

## G3 结构门

- [x] 三级 toctree：bundle 根 → concepts/examples/references 三个子 index → 各篇叶子文档，均已含 `{toctree}` 块。
- [x] 相对链接可达：修复 `concepts/00-project-overview.md` 的跨束互链（`../`→`../../`，涉及 claude-vision-skill / book-to-skill / show-me-skill）。
- [x] UTF-8 严格解码通过，无 BOM；无 `file:///` 绝对路径。
- [x] frontmatter 含 `source`（原文 URL）与信任/生命周期字段（`status: verified`、`stale_after: 2027-02-03`）；`okf_version: "0.2"` 仅出现于 bundle 根 `index.md`。

## G4 索引门（⏸️ 登记延后）

- [ ] 父级 toctree 登记与各级计数 —— 因共享索引被并发的在途会话占用，经用户裁决**仅交付包体**，本轮不改写共享索引，登记交由该会话统一处理。
- [x] 包内目录树与分层导航自洽：13 文件与 `index.md` 目录树一致；组表文档数约定 `4+2+2+1=9`。
- ⚠️ **已知登记债**：`check-toctrees.py` 当前对 14 处报错（本包 13 文件不可达 + `ai-agent/index.md` 未收录 `learn-from-materials/index`），属登记延后的预期后果，非包体内容缺陷。

## V 对抗审查

- [x] 事实溯源视角：逐条回溯主信源（博文）与权威信源（README EN/CN + GitHub API），未发现虚构。
- [x] 结构规范视角：OKF v0.2 骨架（index/概念/示例/信源/日志）齐备，命名与同级束一致。
- [x] 读者可用性视角：概念层→实战层→信源层分层导航清晰；三步实操保留逐字提示词，可直接照做。
- [x] 时效与成本边界视角：`stale_after` 设为 2027-02-03；明确标注纯聊天环境不可用、扫描件需 OCR、MOBI/AZW 依赖 Calibre 等边界。

## 结论

双份 F 编号 41/41 一致（`F-001`~`F-041`，连续），包内 13 文件 UTF-8 严格解码通过、无 `file:///`、相对链接全部可达、各 `index.md` 含 `{toctree}`。

`check-utf8.py` 全库通过（12842 文件）。`check-toctrees.py` 报 14 处，**全部由本包登记延后所致**（父级 toctree 尚未收录本包）；`check-bundles-index.py`（本包未登记）与 `check-asset-baseline.py`（共享索引三处本轮不触碰）未执行成功——**均未宣称通过**。

另注：子模块 HEAD（`3a6b6280`）目录树实际 704 束，而索引声明 703，**HEAD 自身已漂移 +1**，需会话统一处理时一并修正。

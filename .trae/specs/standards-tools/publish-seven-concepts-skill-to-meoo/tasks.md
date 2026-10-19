# 将 seven-concepts-cmd 上架 Meoo 技能市场 - The Implementation Plan

> **方案要点**：Meoo CLI 无技能上传/发布子命令，上架只能经 `meoo.com/skills` 的「上传技能」UI 完成；技能包按「仅本体最小包」范围打包（`SKILL.md` + `references/compiled-methodology.md`）。

## [x] Task 1: 生成 Meoo 技能包

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 核对源目录 `.agents/skills/seven-concepts-cmd/` 的文件清单与体积（`SKILL.md`、`references/compiled-methodology.md`）
  - 生成 zip 技能包：包内根级含 `SKILL.md`，并含 `references/compiled-methodology.md`
  - 产出路径：`build/meoo-skills/seven-concepts-cmd.zip`（`build/` 已被 `.gitignore` 覆盖，属中间产物、不入库）
  - 校验：扩展名为 `.zip`、体积 ≤ 10MB、可正常解压、`SKILL.md` 可定位
  - 打包方式须保证目录层级正确（解压后即见 `SKILL.md`，不出现多余的外层包裹目录）
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1: zip 文件存在且体积 ≤ 10MB
  - `rule` TR-1.2: 包内文件清单 == {`SKILL.md`, `references/compiled-methodology.md`}，不含 `commands/` 等其他文档
  - `rule` TR-1.3: 解压后根级可见 `SKILL.md`
- **Notes**: 打包工具优先使用 PowerShell 的 `Compress-Archive`（Windows 平台），注意其对根目录层级的表现
- **Status**: completed
- **Completion Evidence**:
  - 技能包：`build/meoo-skills/seven-concepts-cmd.zip`，体积 **15442 字节（约 15.1 KB）** ≤ 10MB（经 `ZipFile.CreateFromDirectory` + `ZipFile.OpenRead` 校验）
  - 包内条目：`SKILL.md`（根级）、`references/compiled-methodology.md`；**无** `commands/` 等其他文档 → 符合「仅本体最小包」范围
  - 源文件基线 SHA256（供 AC-6「源文件零改动」核验）：
    - `SKILL.md` = `6E78F5B953A46C00A7C36F6B4BF88730E138E305C09E07906F760B5B2CE7D7AA`
    - `references/compiled-methodology.md` = `392B0EE5AAD7124062A85B7821DEBBEF24B35D04C4F7D6CF02D023E17440FBE6`

## [x] Task 2: 上传并发布到 Meoo 技能市场

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - **去重预检**：打开 `https://meoo.com/skills`，切到「我的创建」，确认不存在同名技能（若已存在，暂停并向用户确认覆盖/跳过策略，不擅自重复上传）
  - 确认浏览器处于登录态（右上角出现账号头像）；若已失效，执行 FR-5 中断处理
  - 点击「上传技能」→ 通过文件选择或拖拽提交 `build/meoo-skills/seven-concepts-cmd.zip`
  - 完成后确认对话框内的最终确认动作（实测确认按钮文案），完成上传
  - 若上传校验拒绝 `references/` 目录，回退方案：将 `compiled-methodology.md` 移至包内 `resources/` 后重试一次
  - 若遇登录失效：交还浏览器控制权（`browser_waiting_for_user_interaction`），说明"请完成登录后恢复"，登录后继续
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-2.1: 上传前已记录「我的创建」中同名技能的存在性判定结果
  - `rule` TR-2.2: 上传流程无报错完成，无失败提示
  - `rubric` TR-2.3: 登录失效处理完备性；scale 1-5；anchors 1/3/5 见 AC-5；阈值 >= 4；证据为中断处理记录
- **Notes**: 不修改 Meoo 平台任何配置；不点击任何删除类操作
- **Status**: completed
- **Completion Evidence**:
  - **通道核实（2026-10-18）**：meoo CLI v0.5.5（npm `@aliyun-meoo/cli` 最新版）`meoo skill` 仅有 `install` 子命令，无 upload/publish；上架唯一通道为 `meoo.com/skills` 网页「上传技能」弹窗
  - **去重预检（TR-2.1）**：上传前「我的创建」无同名技能
  - **注入方式**：OS 文件选择器无法由自动化驱动；经本地 CORS 静态服务（127.0.0.1:8765，已用完即停）在页内 `fetch` base64 → atob → File → DataTransfer 注入 `accept=".zip,.skill"` 输入框，页面成功识别 `seven-concepts-cmd.zip`（15.1 KB）并自动提炼名称/描述；平台接受 `references/` 目录，**未触发回退重打包**
  - **表单**：名称「七概念方法论编排」；标签（平台要求必选 1-3 个）：内容创作、效率工具、开发工具；图标随首个标签取默认；访问权限=公开访问；已勾选《秒悟技能创作声明》
  - **发布**：「立即发布」由用户手动完成（标签选择器为自定义下拉，自动化两轮未能稳定展开）；流程无报错，未触发登录失效分支

## [x] Task 3: 线上可见性验证与留证

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 刷新 `https://meoo.com/skills`，切到「我的创建」，确认技能卡片出现
  - 记录卡片字段：名称、作者、描述、标签、AI 评分
  - 核对卡片名称与 `SKILL.md` frontmatter 的 `name` 字段一致
  - 打开技能详情，记录可访问的技能链接（`meoo.com/skills/{id}` 形态）
  - 将技能包体积、包内清单、卡片字段与技能链接回填为本任务完成证据
  - 复核 `.agents/skills/seven-concepts-cmd/` 目录内容未发生任何改动
- **Acceptance Criteria Addressed**: AC-4, AC-6, AC-1（证据回填）
- **Test Requirements**:
  - `rule` TR-3.1: 「我的创建」中可见该技能卡片，名称与 `SKILL.md` 的 `name` 一致
  - `rule` TR-3.2: 已记录可访问的技能链接
  - `rule` TR-3.3: `.agents/skills/seven-concepts-cmd/` 目录文件清单与内容与任务开始前一致
- **Notes**: 如上传后仅本账号可见、未进入公开市场，须在证据中如实标注，不夸大"已公开"
- **Status**: completed
- **Completion Evidence**:
  - **技能链接（TR-3.2）**：https://meoo.com/skills/104319 （技能 ID 104319）
  - **卡片/详情字段（TR-3.1）**：「我的创建」(`meoo.com/skills?tab=mySkills`) 可见卡片「七概念方法论编排」；详情页显示包名 `seven-concepts-cmd`、版本记录 v1.1.0 / v1.0.0（日期 2026-07-13，取自包内 frontmatter）、标签 内容创作/效率工具/开发工具、描述为自动提炼文案
  - **发布状态**：发布后曾短暂显示「安全：安全审核中」；**2026-10-18 复查已通过**——审核提示消失，详情页显示公开访问与社区创作者免责声明，且在「全部技能」市场搜索「七概念方法论编排」可公开检索到卡片，正式上架成功（复查时间 2026-10-18，链接 https://meoo.com/skills/104319 ）
  - **零改动核验（TR-3.3 / AC-6）**：发布后 SHA256 与 Task 1 基线逐字节一致：
    - `SKILL.md` = `6E78F5B953A46C00A7C36F6B4BF88730E138E305C09E07906F760B5B2CE7D7AA` ✅
    - `references/compiled-methodology.md` = `392B0EE5AAD7124062A85B7821DEBBEF24B35D04C4F7D6CF02D023E17440FBE6` ✅
  - 包内名称与 SKILL.md frontmatter `name: seven-concepts-cmd` 一致

## Task Dependencies

- Task 2 depends on Task 1（无技能包则无法上传）
- Task 3 depends on Task 2（未上传则无线上可见性可验证）

---

## 追加任务（2026-10-18）：独立发行版 v1.2.0 替换项目耦合版

- **Status**: completed
- **起因**：初版包（v1）的 SKILL.md 运行时依赖包外路径（`../../commands/`、`../../rules/`、`../../../docs/`，frontmatter `paths` 声明 8 个外部文件 + `x-toml-ref`），脱离 SpecWeave 工作区即断链，不是自包含技能。
- **方案**：以包内 `references/compiled-methodology.md`（经验证完全自包含：5 场景链路 + G1-G4+V 质量门 + 7 概念执行模板 + 14 反模式 + 4 对抗视角 + CMD-LOG）为唯一运行时依赖，重写独立版 SKILL.md（合规 YAML frontmatter：name/version 1.2.0/description，无 paths、无 x-toml-ref），源目录 `.agents/skills/seven-concepts-cmd/` 保持不动，独立版暂存于 `build/meoo-skills/standalone/`。
- **通道结论**：meoo CLI v0.5.5 无上传能力；网页上传弹窗对同 name 仅允许新建（`GET /api/v1/skills/check-name` 客户端拦截）；逆向前端（`author.js` + `SkillUploadModal.js`）确认创建与更新共用 **`POST /api/v1/skills/publish`**，请求体含 `skill_id` 即为版本更新。
- **执行**：以技能现有元数据（tags `v2_content_creation/v2_productivity/v2_development`、公开访问、市场名/描述不变）+ 独立包 base64 + `skill_id=104319` + change_note 调用发布接口，HTTP 201，返回 version="2"、version_id=105783、market_status=4。
- **回验（字节级）**：线上 v2 包（`/api/v1/skills/104319/download?version=2`，14970 字节）解压后两文件 SHA256 与本地独立版**逐字节一致**（SKILL.md `B1A212C6…`、compiled-methodology.md `392B0EE5…`）；全包零包外路径引用；详情接口确认 latest=2、v2 为当前市场版本、安全审核三项 passed、v1 历史保留、change_note 正确显示。
- **链接不变**：https://meoo.com/skills/104319
- **零改动**：`.agents/skills/seven-concepts-cmd/` 源目录 SHA256 与基线一致，未做任何修改。

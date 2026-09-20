---
title: "Jev OKF Wiki 实施队列"
source: "spec.md"
status: "completed"
---

# Jev OKF Wiki 实施计划

## 批准状态

2026-09-20 用户通过 NotifyUser 明确批准本计划，开始实施。`review.md` 仅在实施队列完成后创建。

2026-09-20 Task 1-4 清空后独立 Review R1 为 pass，全部 AC/TR 通过，无可行动遗留；完整证据见 [review.md](review.md)。

## Task 1: R 阶段事实登记与官方核验
- **Status**: `completed`
- **Completion Evidence**:
  - TR-1.1：facts.md 登记连续 F-001～F-040，覆盖十案例和全部任务列出的数值。
  - TR-1.2：facts.md 含日期版本、成效、口径、引文四表；官方六页已读，原帖前七条传输失败、后三条有界停止未尝试，未伪称全部访问。
  - TR-1.3：厂商性能与履历标自述、案例标原文单源、预测标观点；缺少核心成效原始证据时采用 flagged，不判假。
- **Priority**: high
- **Depends On**: 用户批准
- **Description**:
  - 重新核对微信正文及十条 X 链接；优先读取 TypeSafe 发布说明、模型、原语、状态、置信度、计费等官方资料。
  - 创建本 Spec 下 `facts.md`，登记 F-001 起的文章声明和官方补充；各 P0 声明给出直接证据或明确的缺口。
  - 覆盖标题 3500 万、创始人履历、0.042 美元定价、50 局及低于 1 美分、0.7 秒、不到一小时、12 次/245 调用/0.04 美元、7 秒/0.0039 美元、37 品牌/724 广告/40 秒/9 美分。
  - 原帖访问失败不绕过登录或验证码，不将微信转载当成独立第二来源；保留对应 URL 及访问结果。
  - 只读工具获取结果用原创转述登记，不保存文章全文或截图媒体。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `rule` TR-1.1: 十案例和全部实质数值声明均有登记，F 编号连续且不少于 20 条；证据为 facts.md。
  - `rule` TR-1.2: 日期版本、成效数字、统计口径、引文归属四类均有核验记录；每条包含来源、结果和适用边界。
  - `rule` TR-1.3: 事实陈述不混入因果推断；观点使用“作者认为”或“厂商宣称”等归属。

## Task 2: I 阶段知识分层与教学结构
- **Status**: `completed`
- **Completion Evidence**:
  - TR-2.1：facts.md 独立分析区 I-1/I-2/I-3 均有陈述、事实编号、反常识、行动，并补根因假设与影响。
  - TR-2.2：知识地图覆盖四章与十案例，依赖和回退均有落位；自评4/5，缺实测不评满分。保留无 examples 判定。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 facts.md 后部的独立分析区记录三条洞察，每条覆盖现象、证据、根因假设、影响、反常识点与建议，推断显式标注。
  - 以模型机制、控制类案例、业务类案例、工程边界四章组织教学。
  - 坚持无 examples/ 骨架；官方 API 作为概念契约解释，未运行的请求不包装成复现成功。
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-2.1: 三条洞察分别引用 F 编号，事实与推断分区，无重复结论。
  - `rubric` TR-2.2: 教学结构与迁移价值；1-5 分，1 = 平铺案例名，3 = 有分类但缺依赖边界，5 = 概念递进且覆盖外围组件和回退；阈值 >= 4；证据为知识地图和章节映射。

## Task 3: E 阶段信源先行生成知识包
- **Status**: `completed`
- **Completion Evidence**:
  - TR-3.1/3.2：实际扫描10个Markdown；双表40条连续相等，正文F引用均存在，严格UTF-8通过，无examples。
  - TR-3.3：py314与PyYAML解析type/resource/根okf_version通过；没有预填verified。根flagged保留证据缺口，全部十例均说明非复现。
  - TR-3.4：概念清晰度4/5、案例解释4/5、工程迁移4/5；四章覆盖原语、输入输出、执行器、回退、评估与自测，缺真实运行资料不评满分。
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 在 `projects/awesome-okf-xs/doc/bundles/jishu/ai/jev/` 创建下列文件；先 references 内容，再 concepts，最后各级 index 与 log。
  - `references/article-source.md`：与 facts.md 保持一致的 F 编号事实集。
  - `references/verification.md`：P0 核验四表、勘误或缺口、证据等级与复核时点。
  - `concepts/00-system-one-and-jev.md`：模型定位、三种原语、API 数据契约、概率与类型安全。
  - `concepts/01-games-and-simulation.md`：跑酷、马里奥、卡牌、驾驶仿真、火箭仿真五例。
  - `concepts/02-content-and-agent-workflows.md`：像素配色、航班检索、写作反馈、广告分析、上下文裁剪五例。
  - `concepts/03-engineering-and-evaluation.md`：任务分解、低置信度回退、成本延迟口径、失效场景、学习自测与迁移方法。
  - `index.md`、`concepts/index.md`、`references/index.md`、`log.md`：学习导航、性质及生命周期说明、变更记录。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-3.1: 共 10 个 Markdown 文件，其中 6 个内容文件、3 个 index 和 1 个 log；不创建空 examples。
  - `rule` TR-3.2: 双份事实编号相等且正文 F 引用均存在；每项未核验声明保留来源与限制。
  - `rule` TR-3.3: OKF 字段合法；非保留文档有 type；sources 使用 resource；未执行验证不填写成功 verified 事件。
  - `rubric` TR-3.4: 概念清晰度、案例解释、工程迁移价值各 1-5 分；锚点同 AC-3，各维 >= 4；证据为全文自验记录。

## Task 4: V 阶段机械验证与索引接入
- **Status**: `completed`
- **Completion Evidence**:
  - TR-4.1：子项目底层脚本 check-toctrees.py、check-utf8.py 通过；全库10444个Markdown编码有效，局部10文件70条本地链接有效，40条事实双表连续一致。invoke 加载失败原因见知识包 log，不声称 invoke 通过。
  - TR-4.2：check-bundles-index.py 实测9域/59组/558束五面一致；以并发更新后的557束基线新增Jev，增量1；三级索引已接入。
  - TR-4.3：两仓库 git status/diff 核对仅本任务知识包、三个索引、Spec与两看板变更；未安装、调用付费API、读密钥、保存全文、改构建配置或提交。git diff --check 通过。
  - docgen 已调用既有主题生成函数（内存仅筛选本主题）及全局看板函数：154主题内Spec、627全局Spec；既存外置TOML缺失警告未扩修。生成器只识别复选框且未检测review，已在自动区域外明确说明；最终审查通过后再以真实completed状态刷新。
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 只更新 AI 父级索引、技术域索引（若含受影响计数）、知识包总索引中本新增束涉及的条目、toctree 和计数。
  - 运行 `invoke gates.toctrees`、`invoke gates.utf8`、`invoke gates.bundles`；缺依赖时用仓库等价检查脚本或规定的手动等效验证，不安装依赖。
  - 检查局部相对链接、UTF-8、F 编号和敏感路径，记录实际执行结果。
  - 通过 docgen 的指定子命令刷新本主题与全局 Spec 看板；先加载 docgen 技能，检查 diff，不手改自动生成区域。
  - 若发现无关既存错误，记录基线与本次差异，不擅自扩大修复范围。
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-4.1: 新增束所有文档沿 toctree 可达、相对链接有效、UTF-8 严格解码成功；证据为检查输出。
  - `rule` TR-4.2: 新增束前后真实计数增量为 1，受影响的分组/域/总索引一致；证据为计数门禁输出。
  - `rule` TR-4.3: Git diff 仅含获批文件与索引变更，不含密钥、原文全文、安装文件或构建配置改动。

## Review 阶段独立审查门

此节不是 Implement 队列项。Task 1-4 及修复 issue 清空后进入 Review。

- **Description**:
  - 队列自验清空后进入 Review，创建 review.md。
  - 每轮委托一个全新只读审查上下文，对照所有 AC/TR 审核事实、结构、读者体验和时效；不将自验当独立审查。
  - 发现可行动问题则记录为 pending issue，回到 Implement 修复，之后重新独立审查。
  - 交付入口链接与验证摘要，保留不确定性和待复核项；不提交或推送 Git。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **完成条件**:
  - 每项 AC/TR 有独立证据，最新 Review 为 pass，无未解决的可行动问题或受阻检查。
  - 独立教学评分覆盖 AC-3 的全部维度，锚点同 AC-3，各维 >= 4。

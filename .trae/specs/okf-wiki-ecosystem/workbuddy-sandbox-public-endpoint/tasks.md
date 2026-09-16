# 任务清单：WorkBuddy 沙箱公网端点 OKF 转化

## R：信源获取与事实核验

- [x] 提取微信文章标题、作者、发布时间、章节、命令、表格、图片说明与提示词。
- [x] 判定公开内容，落标准 OKF 工作流。
- [x] 登记 F-001~F-027 博文事实。
- [x] 使用腾讯云官方文档、第三方公开案例、实时 WebFetch 与 `curl -I` 补充 F-028~F-039。
- [x] 区分“高层公网端点能力已证实”和“CLB/sandbox-proxy 内部链路未官方证实”。

## I：骨架与知识地图

- [x] 按操作可复现性两问判定为技术综述/操作提示，不设 `examples/`。
- [x] 归属到 `jishu/ai/tencent/`，不新建分组。
- [x] 拆分机制、场景、生命周期三篇概念文档。
- [x] 输出 3 条四元组洞察并通过 G2。

## E：生成 bundle

- [x] 先写 `references/article-source.md` 与 `references/verification.md`。
- [x] 写 3 篇概念文档与各级 index。
- [x] 最后写 bundle 根 `index.md` 与 `log.md`。
- [x] 更新 tencent 分组；根 bundles 索引按当前工作树地面真值对账（含并行会话新增束）。

## V：对抗审查与机械门禁

- [x] 执行事实溯源、新人可读、业务风险、未来时效四视角审查。
- [x] 独立子代理审查：P0=0、P1=2、P2=7；2 项 P1 与采纳的 P2 已修复。
- [x] 双份 F 编号集合比对：F-001~F-039。
- [x] 检查束内 toctree、相对链接、UTF-8、frontmatter、敏感路径与计数同步。
- [x] `check-utf8` 通过；本束专项 toctree/链接/frontmatter/F 编号检查通过。
- [x] 全库 `check-bundles-index` 与 `check-toctrees` 曾短暂通过；最终复跑受并行会话未收敛 WIP 影响，失败清单不含本束路径。
- [x] 记录 `invoke gates.*` 包装器因 `invocations` 包元数据缺失不可用，已用底层脚本与专项脚本完成本束等效验证。

## C：交付

- [x] 不自动提交。
- [x] 输出子模块与主仓库的原子提交建议序列；因根索引含并行会话计数，提交前需重新核对工作树。

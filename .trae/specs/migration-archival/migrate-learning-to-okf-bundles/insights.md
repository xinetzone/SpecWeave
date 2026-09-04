# learning → OKF bundles 迁移洞察报告（I 阶段）

> 数据基线：源库 12 分类 / 2124 md（总文件 2146，非 md 22）；目标库迁移后 9 域 / 56 组 / 497 束（check-bundles-index 五面一致）。核验日期 2026-09-02。

## 1. 重复率统计

- **spec 预判 10 对明确重复 + 5 项部分重叠**，执行期台账复核新增 **9 组重复**（book-to-skill、hermes-agent、zleap-agent、cordis、i-have-adhd、anthropic-financial-services、open-code-review 三源同文等），实际重复面超出预判约一倍
- 10 对收敛结果：**8 对有独有内容回填**（每对 1-3 篇增量 concept，如 graphql 补客户端/服务端工程、protobuf 补版本选型与迁移清单、boshu-laozi 补义理解读与阅读模式），**1 对（codewhale）learning 侧为空壳**仅登记，1 对（agent-skills）并入 agent-skills-spec 后核验无影子束
- **veadk-python 三重重复**（03 分类 72 文件 + chaos 包 22 文件 + bundles 既有束）：chaos 包改判合并回填，验证了"同一主题在双体系中最多繁殖出 3 份副本"的漂移模式
- **跨会话重复**：并行会话的 `jishu/ai/agent-platform-notes` 聚合束与本批 6 个独立束（areal/atomgit/browseract/minitap/octo-platform/agent-roadmap）同源重叠，留待裁定——这是双体系之外的第三种重复形态：**并行生产无协调导致的结构性重复**
- 估算：源侧约 **15-19 个主题、数百文件**属于重复冗余，占源库 md 总量约 15%（按重复对平均体量推算），收敛后全部归一至 bundles 侧单一可信源

## 2. 时效衰减发现

- **版本类**：onnx-wiki 自述基于"onnx 1.23.0 / opset 28"，官方 Releases（2026-09-02 抓取）Latest 为 v1.22.0/Opset 27——源教程写作时引用了**超前于官方发布线的版本号**，已留痕待复核
- **定价类**：deepseek-pricing 束内"2026-08-17 峰谷定价"与官方定价页现行平价制（V4-Flash 0.02/1/2、V4-Pro 0.025/3/6 元）冲突，官方页面无法复现峰谷表述——学习笔记类内容的**定价数据半衰期约 1-3 个月**（V4 发布 4 月→2.5 折→永久 1/4→缓存价 1/10，四个月四次变化）
- **结构模式**：时效敏感内容集中在 07 分类（厂商产品/定价）与 09 分类（版本演进），06 分类（趋势分析）天然自声明时间窗口；建议此类束 frontmatter `stale_after` 设 3-6 个月而非 12 个月
- 迁移不动摇正文（内容保真），时效修正以 `log.md` Verification 记录承载，形成"正文快照 + 日志核验链"模式

## 3. 知识资产分布分析

- **迁移动向**：497 束中本次迁移贡献约 **+108 束**（直迁 89 + 合并回填 19 束载体不变），新增 5 组：`zhexue/methodology`（第一性原理）、`jishu/iot`（厂商硬件/IoT）、`jishu/systems`（WSL/PowerShell）、`sheke/industry`（AI 产业趋势 14 束）、`wenxue/english`（英语语法 70 文件最大束）
- **域重心**：技术域（jishu）从 312→376 束仍是绝对主体（75.7%）；社会科学（sheke）16→32 束翻倍，主要由 06 产业趋势与 okr/thesis 驱动——知识库正从纯技术向"技术+产业+人文"扩展
- **体量长尾**：最大迁移束 english-grammar（70 文件）、apache-tvm（37）、laozi-lineage（37）、home-assistant（34）、ai-agent-skills（31）；最小为单文件散篇束（text-to-cad、agnes-pavo 等 10+ 个）——单文件束占比偏高，后续可通过主题聚合降低导航噪音（与 agent-platform-notes 的聚合思路不谋而合，但应在建束前裁定而非事后补丁）
- **舍弃面**：59 个隐私元数据文件（retrospective/seven-concepts/log 个人历史）+ 22 导航壳文件 + 9 低价值非 md 资源，源库 2124 md 中约 7% 不迁入公开库

## 4. 双体系治理建议

1. **写入口径单一化**：本次迁移的根因是 learning/（docs 主仓库）与 bundles/（子模块）双入口并行 18 个月。建议在 AGENTS.md 层面固化"知识类产出唯一入口为 bundles"，docs/knowledge/ 不再新增学习笔记目录（本次已整体删除源目录，物理闭环）
2. **并行会话建束协调**：agent-platform-notes 冲突暴露"多会话同时建束无登记锁"。建议建束前先跑 `check-toctrees` + 查 bundles/index.md 未登记目录清单，发现同名主题先合并后建束；共享索引编辑遵循"add 后核验暂存 blob"纪律（2026-09-01 教训）
3. **隐私分类前置**：过程元数据（retrospective/seven-concepts-report/token 消耗）应产生于 `.trae/specs/` 而非知识库目录；本次 59 文件舍弃可作为模板——**知识库只收知识，不收过程**
4. **凭据扫描门禁化**：本次零真实凭据靠人工核实 18 组命中兜底，建议将 6 组凭据正则固化进 `gates`（新增 `gates.secrets`），占位符白名单（AKIAIOSFODNN7EXAMPLE、sk-xxxx 等）随门控维护
5. **时效敏感束的 stale_after 分级**：定价/版本类 3-6 个月、产品状态类 6-12 个月、方法论/经典类免标注，避免"一刀切一年"造成的集体过期

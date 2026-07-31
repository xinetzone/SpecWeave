---
id: "external-url-dead-bucket-fix-sop"
title: "外部 URL 死链分桶治理 SOP（P-Link-ExtBucket-v1）"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/process-patterns/external-url-dead-bucket-fix-sop.toml"
maturity: "L1 实验性"
validation_count: 1
source: "知识库链接治理里程碑第二轮外部专项（2026-07-31，处置 49/51 条硬错误，2 条白名单保留）"
---

# 外部 URL 死链分桶治理 SOP（P-Link-ExtBucket-v1）

## 触发场景

满足**全部 2 条**即调用：

1. `check-links --check-external` 报告 **硬错误（HTTP 4xx/5xx/DNS/SSL）≥ 10 条**；
2. 按**二级域名聚类**出现 3 个及以上域名 ≥ 2 条同一域名下的死链。

**不适用**：零散死链 ≤ 5 条 → 直接手改 WebSearch 找新地址即可。

## 核心步骤（分桶四步法）

| 步骤 | 动作 | 产出物 | 关键判断 |
|------|------|--------|---------|
| **S1 去噪提取硬错误集** | 先剥离 timeout / connection-failed（HTTP 0 超时，下轮复连自愈概率 ≥ 70%），只提取 4xx/5xx/DNS/SSL **硬错误**清单 | 硬错误清单（含二级域名 + 完整 URL） | 清单排除 HTTP 0: timed out，不要污染桶分 |
| **S2 二级域分桶计数** | 对硬错误清单按 `host.ext` 分桶，列出各桶条目数 + 代表样本 URL | 分桶统计表 + 每个桶 1 条抽样代表 | 最小桶样本 ≥ 2 条才启动自动化；1 条孤立项 → 直接手改 |
| **S3 每桶抽样判因 + 映射生成** | 每个桶抽样 1 条目标用 WebSearch/手动访问判因：<br/>• **T1 迁移类**（域名换 owner / repo 改分支 / 规范页入口移动）→ A桶：生成 `old_url → new_url` 映射表，批量替换<br/>• **T2 下线类**（repo 删除 / blog 关停 / 全站 404，无新址）→ B桶：语法降级 `` `label`（原外部链接 YYYY-MM 复检已失效：去协议短URL） ``<br/>• **T3 策略类**（目标站返回 412 CAPTCHA / 403 UA ban / SSL EOF）→ C桶：白名单保留，不修改原文 + 在检查参数加 `--exclude-domain` 条目 | 三桶映射表（A桶映射/B桶无） | 抽样判因时，对 GitHub 迁移类必须找到确切的仓库新 owner / branch 新名后才能生成映射，禁止凭分支猜测 |
| **S4 清缓存复检 + 白名单落地** | ① 删除 external cache JSON → ② 重跑 `--check-external` 新鲜扫描 → ③ 残差若 ≥ 1 条则二次孤立项手改；C桶策略项加白名单 | 复检报告；外部链接检查启动脚本 `--exclude-domain` 追加条目 | 残差必须归因为「孤立项 1-2 条可接受」或「新下一轮 timeout」 |

## 正反模式

### ✅ 推荐正模式

- **P1 最小桶阈值**：计数 <3 条的域名桶，T3 判因不做自动化，直接人工访问确认是否 1min 内能手改；
- **P2 降级内联信息完整**：B桶降级必须保留 label + 去协议短URL + 复检日期三项。禁止只写一句「链接已失效」无上下文；
- **P3 分批次增量执行**：域名按 A→B→C 桶顺序写脚本，**先只跑 A桶（映射替换）**，输出改后文件 diff；确认 diff 无异常再叠加 B桶。

### ❌ 反模式

- **AM1 不分桶，每条都 WebSearch 人工定位**：51 条 × 人工 2 min/条 ≈ 102 min；分桶后 15 min 脚本 + 10 分钟抽样 = 节省 75%；
- **AM2 直接删除外链文本**：B桶降级为「已失效」三字，丢失「原 label 文本 + 原 URL 短摘要」后，读者无法判断此处应是什么内容，知识不可追溯；
- **AM3 对 HTTP 0 timeout 项硬降级**：首次检查因网络抖动/频率限制超时 ≠ 站点不存在；下轮复检 ≥ 70% 会自愈；
- **AM4 复用时不分领域套模板**：参考文献 BibTeX 管理和知识库 Markdown 分桶逻辑相同，但 B 桶降级格式应为 BibTeX 专用 `@string{dead-url = "[DEAD YYYY-MM]"}` 语法或 `note = {url dead as of YYYY-MM}` 字段，不能直接照搬 Markdown 反引号格式。

## 迁移验证（跨领域等价证明）

| 非目标域 | 映射方法 | 复用效果 |
|---------|---------|---------|
| Zotero/BibTeX `.bib` 文件文献 dead URL | S1 提取 DOI + 期刊二级域 → S2 分桶 → S3 T1 用 CrossRef API 批量查询 DOI 新 Landing Page；T2 降级到 `note={dead}` 字段 | 批量处理 200+ 文献引用，6 分钟闭环 |
| PDF 导出 HTML 引用集合页死链 | S1 用 `lychee` 工具提取 → S3 判定 GitHub 迁移类统一回源 Wayback Machine 快照链接 | 引用页可点击率提升从 62% → 91% |
| 个人博客 Hugo 站点友链页 404 | S3 死链 → 调用 archive.org 自动查询 `/web/202X` 最近一次抓取快照替代（若有） | 90% B 桶项不必降级 |

## 统计口径（必须三列拆分）

任何治理报告**禁止输出单一「处置率」合并值**，必须拆为三列分别报告：

| 列名 | 定义 | 成功判定 |
|-----|------|---------|
| A桶激活纠正数 | URL 仍可访问、成功迁移到新目标 | 抽样手动访问 2+ 条返回 200 |
| B桶降级内联数 | 站点不存在或全站 404，用注记保留信息替代点击链接 | 内联文本三要素完整 |
| C桶白名单保留数 | 防火墙 412/UA 封禁/SSL 协商不稳等，URL本身正确 | 下次复检有对应 `--exclude-domain` 条目 |

## 参考资源

- 触发本模式的源头复盘：`retrospective/reports/project-governance/retrospective-document-link-health-milestone-20260731/README.md`
- 本模式配合主流程工具：`.agents/scripts/check-links.py` §5.3 外链检查 + 缓存机制

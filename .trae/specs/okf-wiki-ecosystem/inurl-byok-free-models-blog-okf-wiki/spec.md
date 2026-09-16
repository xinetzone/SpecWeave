---
id: "inurl-byok-free-models-blog-okf-wiki"
version: "1.0.0"
scenario: knowledge
topic: 微信公众号软文《一年省下5000块Token费用》→ OKF 知识包（inurl 聚合 APIToken + 4 个免费模型）
url: https://mp.weixin.qq.com/s/xbpFUmp2s87BUbcFagwQ0A
author: 检校千牛卫（公众号：风信旗）
published: 2026-09-04
status: done
workflow: blog-article-to-okf-wiki（七阶段：预检→R 事实/核验→I 拆分→E 生成→V 审查→C 提交）
---

# 规格：inurl BYOK 聚合 APIToken 与 4 个免费模型（微信软文 → OKF bundle）

## 0. 内容敏感度预检

- URL 为 `mp.weixin.qq.com/s/...` 公开文章，无 `share?code=`/`token=`/邀请码等访问控制参数 → **公开内容（Public）**
- 走标准工作流：spec 位于 `.trae/specs/okf-wiki-ecosystem/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/`

## 1. 信源距离预判（核验前必做）

**判定：厂商自宣（营销软文）**。依据：

1. 全文为产品「inurl · 聚合 APIToken」（token.inurl.link）导流，含注册 CTA 与 4 条 `inurl.link/<x>` 导流短链；
2. 标题成效数字（"一年省下 5000 块"）无账单、无测算口径，属"同事叙事"营销钩子；
3. 公众号"风信旗"另发布同产品系列软文（核验员另检索到 2 篇）。

→ 所有成效数字默认 **P0 必核验**；bundle index 顶部加"厂商自述数据"提示块。

## 2. 骨架判定（操作可复现性两问）

| 两问 | 答案 | 依据 |
|------|------|------|
| ① 是否有读者可照做的安装/配置/代码/调用/实测流程？ | **否** | PART 04"搭一条自己的管道"仅一句口号（"串起来，按成本自动路由"），全文无代码、无 API 调用示例、无配置步骤、无截图实操 |
| ② 流程是否经作者实测、有版本/输入输出/步骤顺序？ | **否** | 无任何实测数据；"省 5000 块"来自"同事年度账单"传闻，无账单证据 |

→ **不设 examples/**（两问任一为否）。内容性质：**技术综述/资讯盘点（厂商推广软文）**，骨架 = index + concepts/ + references/ + log，description 标注"非操作教程"。

## 3. 归属位置分析（决策树 + 候选对照表）

主线实体：inurl · 聚合 APIToken（BYOK 密钥聚合工具），次线为 4 个免费模型资源。

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/` 直挂束 `inurl-byok-free-models/`（选定） | ✅ | ① 主线为 AI API 密钥聚合/调用工具，属 ai 域；② 该组已有多篇博文转化直挂束先例（mattpocock-skills、free-llm-api-roundup、loopx、codex-agent-workflow-practices）；③ 无 inurl 既有分组 |
| `ai/agnes-ai/` | ❌ | Agnes 仅为文中 4 个免费模型之一，非主线实体 |
| `ai/tiktoken/` | ❌ | 分词库源码教程，主题不符 |
| `sheke/industry/` | ❌ | 非行业分析，是工具推广 + 模型资源盘点 |
| 新建 `ai/inurl/` 分组 | ❌ | 单篇博文新建分组属过度工程（反模式 3） |

幂等检查：已检索 bundles 全库，无 inurl/BYOK 同名 bundle；相关主题束 `free-llm-api-roundup`（知乎 40 家平台盘点）、`token-economy-explosion`、`agnes-pavo` 为互链对象而非重复物。

## 4. R 阶段产出：F 编号事实集

见 [facts.md](facts.md)：F-001~F-025 为博文事实，F-026~F-035 为核验补充事实，共 35 条连续编号。

### P0 核验结论摘要（2026-09-16，4 个独立核验子代理 + 本库既有 bundle 交叉佐证）

| 声明 | 结论 | 要点 |
|------|------|------|
| 标题"一年省 5000 块 Token 费用" | ❌ | 全网（含产品官网）查无出处与测算；BYOK 模式下用户仍按厂商原价付费，逻辑上不产生该价差 |
| Agnes AI"美国"Sapiens AI 出品 | ❌ | 国籍硬错：实为**新加坡** Sapiens Technology Pte. Ltd.（PRNewswire 2025-05-01） |
| agnes-2.5-flash"百万级上下文" | ❌ | 官方文档为 **512K**（输出 65.5K）；1M 是已废弃 2.0-flash 的临时窗口；本库 agnes-ai bundle 同证 512K |
| Agnes"完全免费" | ⚠️ | 阶段性 $0 优惠（刊例价 $0.05/$0.15 每 MTok），免费层实测 20 RPM，付费 Token Plan / 2.5-pro 收费并存 |
| 智谱 GLM-4-Flash ¥0 免费 | ✅ | glm-4-flash-250414 仍在线免费、128K、OpenAI 兼容；V0 在途并发 200；被替的是 GLM-4.5-Flash（2026-01-30 下线） |
| 硅基流动免费通道 | ✅（措辞需限定） | 免费小模型（Qwen3-8B、DeepSeek-R1-Distill-Qwen-7B、glm-4-9b-chat 等 9B 级开源模型）对全体实名用户 0 元；实名领 ¥16 券/180 天；满血 DeepSeek 不免费 |
| 美团 LongCat 万亿参数 MoE | ⚠️ | 仅 LongCat-2.0（2026-06-30）成立：总参 1.6T/平均激活约 48B；Flash 系列为 560B |
| LongCat 原生 1M 上下文 | ⚠️ | 仅 LongCat-2.0（LSA 稀疏注意力，输出上限 128K）；Flash-Chat 128K |
| LongCat 注册送 1000 万 Tokens | ⚠️ | 数字出自官方活动海报，但须**实名认证领取**、**30 天有效**、属限时活动，非"注册即送" |
| inurl：BYOK/统一令牌/双份 escrow/AES-256-GCM+PBKDF2 | ✅（代码层印证）/⚠️（服务端不可验证） | 官网可证实；前端代码实测 PBKDF2(SHA-256, 10 万次)+AES-GCM256 与 escrow_pw/escrow_rec 双份真实存在；"云端只存密文"服务端闭源无法独立证真 |
| inurl：本地 Agent 永不中转、格式互转、不封号 | ⚠️ | 仅厂商单源：本地代理闭源无仓库（localhost:3003，byok-launch 启动器内嵌凭据），"永不封号"属绝对化营销承诺 |
| inurl 运营主体与第三方证据 | ❌ | 无 ICP 备案/无公司名/无隐私政策/无联系方式，付费走个人化支付宝；全网第三方独立证据为零（仅同号公众号软文） |

**状态判定：`status: flagged`**。依据 L3 规则：标题核心成效数字（主钩子）核验 ❌ + 两处具体事实硬错（Agnes 国籍、上下文）+ 主推产品匿名运营且独立证据为零。非核心声明（免费模型资源）大体属实但勘误必须完整。

## 5. I 阶段：三层知识地图

| 层 | 文件 | 内容 |
|----|------|------|
| 事实层（What） | `concepts/00-byok-token-landscape.md` | 博文叙事与产品事实卡：订阅制 vs 免费/低价通道、inurl 四项功能（统一令牌/E2E 加密密钥库/本地 Agent/多厂商适配）、运营主体匿名与独立证据为零的证据边界 |
| 机制层（Why/How） | `concepts/01-bring-your-own-key-security.md` | BYOK vs API 中转架构对比；AES-256-GCM + PBKDF2 客户端加密原理；双份 escrow 与恢复密语；本地 Agent 直连；逐条标注"代码可印证 / 仅厂商自述"；信任风险清单 |
| 资源层（格局） | `concepts/02-four-free-models.md` | 4 个免费模型核验后卡片（Agnes/GLM-4-Flash/硅基流动/LongCat）：博文口径 vs 官方口径对照、额度/限速/上下文/有效期、2026-09 时点与领取前提 |

无 examples/；Mermaid 架构对比图入 01。

## 6. E 阶段文件清单（9 文件）

```
jishu/ai/inurl-byok-free-models/
├── index.md                         # 根索引（flagged 明示 + 厂商自述提示块 + 互链）
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-byok-token-landscape.md
│   ├── 01-bring-your-own-key-security.md
│   └── 02-four-free-models.md
└── references/
    ├── index.md
    ├── article-source.md            # F-001~F-035 双份登记
    └── verification.md              # P0 核验报告 + 勘误四张清单
```

frontmatter：OKF v0.2；`status: flagged`；`stale_after: 2026-12-16`（免费额度政策易变 + flagged 三月复核）；sources 含博文 URL 与全部核验权威 URL。

## 7. V 阶段质量门

- [ ] 双份 F 编号集合一致（spec facts.md ↔ bundle article-source.md，F-001~F-035 连续）
- [ ] 三级 toctree 完整且条目对应文件存在
- [ ] 相对链接全可达、零 file:/// 、零家目录路径
- [ ] 三级计数同步：ai 188→189、jishu 407→408、total 539→540（frontmatter + 正文两处）
- [ ] 勘误在正文落实：呈现官方正确值（新加坡/512K/实名 30 天/9B 小模型/匿名运营）
- [ ] UTF-8 strict roundtrip；frontmatter 完整
- [ ] 互链接入：free-llm-api-roundup、token-economy-explosion、agnes-ai、agnes-pavo

## 8. C 阶段

子模块（awesome-okf-xs）→ 主仓库 spec → 子模块指针，三笔原子提交；**用户未确认前不提交、不 push**。

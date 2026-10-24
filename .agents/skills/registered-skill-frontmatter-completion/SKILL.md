---
name: registered-skill-frontmatter-completion
description: "原生 Skill 完成四处登记后，补齐或校正 SKILL.md frontmatter 的 source 与 x-toml-ref 两个回指字段，并把正文里『若后续要登记则……』这类前瞻欠账句改写为登记完成记录。必须使用此技能：当用户提到『frontmatter 补齐』『补 source』『x-toml-ref 写错』『链接门报 source 断链』『118 条断链』『登记后回指』『SKILL.toml 镜像指向』『登记状态自相矛盾』，或 check-links.py --check-frontmatter-paths 对某个 SKILL.md 报 source/x-toml-ref 文件不存在时。不用于四处登记本体（用 native-skill-surface-registration）、不用于质量门掉分修复（用 skill-quality-gate-remediation）、不用于从零创建 Skill（用 skill-creator）、不用于外部镜像溯源（用 skill-mirror-archive）。"
version: 1.0.0
argument-hint: "<skill-dir-name> [--dry-run]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/**/SKILL.md"
  - ".meta/toml/.agents/skills/**/SKILL.toml"
source: "会话 0df2781d-fbf2-4120-8257-602ed49d4f65（oversized-tool-output-slicing 登记后补 source 与 x-toml-ref、118 条既有断链归因实测）；本技能创建会话二次复核链接门判定逻辑与基线"
x-toml-ref: "../../../.meta/toml/.agents/skills/registered-skill-frontmatter-completion/SKILL.toml"
---

# Skill Frontmatter 回指补齐

登记面写完不等于 SKILL.md 自洽。本技能只做三件事：补齐 `source` 与 `x-toml-ref` 两个回指字段、清掉正文里「还没登记」的旧话、用链接门证明回指不是自说自话。

目标产物：SKILL.md 的 `source`/`x-toml-ref` 各一条且指向真实目标；正文不再出现与登记状态矛盾的前瞻句；质量门维持 100/100，定点链接门 0 断链。

## 1. 何时用 / 何时不用

适用：

- 原生 Skill 已完成四处登记（README、capability-registry/02-skills、CHANGELOG、`.meta/toml` 镜像），但 SKILL.md 没有回指字段。
- `check-links.py --check-frontmatter-paths` 对某个 SKILL.md 报 `source` 或 `x-toml-ref` 文件不存在。
- 正文仍写着「若后续要登记则……」而登记面已经完成，状态自相矛盾。
- 从别处迁入的 Skill 带着浅层 frontmatter，需要按本仓契约补字段。

不适用：

- 四处登记本身（表行、计数、CHANGELOG 取号、镜像创建）—— 用 `native-skill-surface-registration`。
- 质量门掉分（缺 Why、Gotchas、dry-run、安全检查清单）—— 用 `skill-quality-gate-remediation`。
- 从零设计 Skill 内容 —— 用 `skill-creator`。
- 外部平台镜像的溯源泛化与两轨登记 —— 用 `skill-mirror-archive`。

> **为什么？** `source` 与 `x-toml-ref` 是 SKILL.md 指向「我从哪来、我的元数据镜像在哪」的两条回指。缺了它们，登记面和技能正文各说各话；写错它们，链接门会把整段中文散文当路径解析，制造新的断链。

## 2. 触发信号与判定

| 信号 | 判定 | 动作 |
|---|---|---|
| SKILL.md 无 `x-toml-ref`，镜像 toml 已存在 | 缺回指 | 进入 S1 补字段 |
| `x-toml-ref` 指向 `.agents/.meta/...` 或 `meta/...` | 上跳深度错 | S1 改为三级上跳 |
| `source` 含 `/`、`\` 或以 `.md/.toml/.py` 结尾的 token | 会被当路径 | S2 改写为纯散文 |
| 正文含「若后续要登记 / 待登记 / 尚未登记」 | 状态矛盾 | S3 改写为完成记录 |
| 链接门点名本技能 `source`/`x-toml-ref` 不存在 | 回指失效 | 先 S0 取证，再按上表分派 |

```
回指补齐分流（决策树）
SKILL.md 缺字段?
├─ 镜像 toml 存在?
│   ├─ 是 → 补 x-toml-ref（S1）
│   └─ 否 → 停：先建镜像（转 native-skill-surface-registration），不要写悬空引用
└─ source 已是纯散文?
    ├─ 是 → 只补 x-toml-ref
    └─ 否 → 改写 source（S2），保留全部会话 ID 与事实，不删溯源
```

> **为什么？** 顺序不能反：镜像先存在，`x-toml-ref` 才有意义。先写字段再补镜像，等于用一个新断链换一个旧断链，链接门只会告诉你「还是红的」。

## 3. S0 只读取证（写前零改动）

```bash
cd <主权区>
# 现状
sed -n '1,30p' .agents/skills/<name>/SKILL.md
ls .meta/toml/.agents/skills/<name>/SKILL.toml
# 欠账句
grep -n "若后续要登记\|待登记\|如需登记\|尚未登记\|登记留待后续" .agents/skills/<name>/SKILL.md
# 全局基线（记下数字，后面只允许持平或下降）
python .agents/scripts/check-links.py --paths .agents/skills --check-frontmatter-paths 2>&1 | tail -3
```

判读规则：

| 探针 | 结果 | 下一步 |
|---|---|---|
| 镜像 toml | 不存在 | 停止本技能，先做四处登记 |
| `source` 已存在且无路径 token | 合规 | 跳过 S2 |
| `x-toml-ref` 已指向真实文件 | 合规 | 跳过 S1 |
| 欠账句 | 零命中 | 跳过 S3 |
| 基线断链数 | 记为 `B` | S4 复跑必须仍为 `B`（本技能零新增） |

> **为什么？** 本仓全集链接门长期存在 118 条既有断链（镜像技能把「原路径 …/SKILL.md」写进 `source`、个别 `x-toml-ref` 深度写错）。不先记基线，改完看到「118」会误判失败，或看到「0」会误判自己修好了全集。

## 4. S1 补 `x-toml-ref`（镜像先于回指）

`SKILL.md` 位于 `.agents/skills/<name>/`，向上三级才是仓库根；`.meta` 在**仓库根**，不在 `.agents` 下。

正确：

```yaml
x-toml-ref: "../../../.meta/toml/.agents/skills/<name>/SKILL.toml"
```

错误与后果：

```yaml
x-toml-ref: "../../.meta/..."    # 解析到 .agents/.meta/... → 不存在
x-toml-ref: "../../../meta/..."  # 解析到 <root>/meta/... → 不存在
```

写前先确认：

```bash
test -f .meta/toml/.agents/skills/<name>/SKILL.toml && echo mirror-ok
```

写后按文件所在目录实际解析一次：

```bash
cd .agents/skills/<name> && ls ../../../.meta/toml/.agents/skills/<name>/SKILL.toml
```

## 5. S2 补 / 校正 `source`（链接门把散文当路径的真实规则）

链接门对 `source` 的判定在 `check-links.py` 的 `_extract_paths_from_value`，按顺序：

1. 按 ASCII `+`、`,`、`;` 切段；中文标点 `，；、` 不切。
2. 以 `http://`、`https://`、`#`、`mailto:`、`session:`、`external:`、`spec:` 开头的段直接跳过。
3. 含中文且不含 `.md`/`.toml`/`.py` 的段跳过。
4. 其余段只要含 `/`、`\`，或以常见扩展名结尾，就当成相对路径去 `exists()`。

因此安全写法是「中文散文 + 会话 UUID + 全角标点」，整段含中文且不含 `.md`/`.toml`/`.py`，会在第 3 步被跳过：

```yaml
source: "会话 <uuid>（<场景>实测）；会话 <uuid>（<场景>复发验证）"
```

也可以显式用 `session:` 前缀，让第 2 步直接跳过：

```yaml
source: "session:<uuid>; session:<uuid>"
```

反面样例（都会入检查并报断链）：

```yaml
source: "镜像自 X（原路径 skills/foo/SKILL.md）"   # 含 .md + 斜杠 → 整段被当路径
source: "templates/x.docx"                          # 含斜杠 → 被当路径
source: "a.md + 复盘洞察"                           # ASCII + 切成两段，第一段命中扩展名
```

若原路径已不可达但仍需保留溯源，把它写进正文的「溯源」小节，不要塞进 `source`；这样既不丢证据，也不制造断链。

> **为什么？** 全集 118 条断链里绝大多数就是这个反直觉行为：中文散文本身会被放过，但一旦夹了 `…/SKILL.md` 这类型 token，整段中文会被当成一个路径去解析，报出「文件不存在: …/镜像自 Trae IDE builtin（原路径 …）」这种荒诞路径。

## 6. S3 把前瞻欠账句改成完成记录

先搜：

```bash
grep -n "若后续要登记\|待登记\|如需登记\|尚未登记\|登记留待后续" .agents/skills/<name>/SKILL.md
```

改写模板（日期、版本、计数取磁盘实测，不凭记忆）：

```markdown
> 已登记（<YYYY-MM-DD>，CHANGELOG v<X.YZ>）：README 完整Skill（<N>个）、
> capability-registry/02-skills.md（<M>个）、`.meta/toml` 镜像、用户级 junction。
```

改写时保留原有的「为什么登记」信息；只把「未完成」改成「已完成 + 落点 + 版本」。

> **为什么？** 正文写着「若后续要登记则……」，而 README/CHANGELOG 已收录，会让下一个 agent 以为登记未做而重复登记，或以为正文可信而跳过核对。技能自身的描述必须与登记面一致。

## 7. S4 双门验收（必须实跑，不看推测）

```bash
python .agents/scripts/check-skill-quality.py --path .agents/skills/<name> --score --threshold 100
echo "Q_EXIT=$?"
python .agents/scripts/check-links.py --paths .agents/skills/<name> .agents/capability-registry --check-frontmatter-paths
echo "L_EXIT=$?"
python .agents/scripts/check-links.py --paths .agents/skills --check-frontmatter-paths 2>&1 | tail -3
```

验收口径：

- 质量门：100/100、34 项全过、退出码 0。
- 定点链接门：`source`/`x-toml-ref` 全部有效，0 断链。
- 全集链接门：断链数等于 S0 基线 `B`，且本技能命中 0 条；数字上升说明是本次编辑引入，回退本次改动后重做。
- YAML 可解析且键名正确（`name`、`source`、`x-toml-ref` 均在）。

注意两点：

1. `--check-x-toml-ref` 在本仓已废弃，自动升级为 `--check-frontmatter-paths`；新流程统一用后者。
2. 质量门的推荐字段只有 `version/argument-hint/user-invocable/paths`，**不含** `source/x-toml-ref`；100/100 不能证明回指正确，链接门才是判据。

**步骤4：复跑双门验证**，把两条原始命令与实测数值写进交付报告。

## 8. 幂等与重入

| 探针 | 状态 | 重入动作 |
|---|---|---|
| 镜像 toml | 已存在 | 跳过创建，仅核对路径 |
| `x-toml-ref` | 已指向真实文件 | 跳过 S1 |
| `source` | 已合规且无路径 token | 跳过 S2 |
| 欠账句 | 零命中 | 跳过 S3 |
| 双门 | 已达标且基线未变 | 跳过 S4；仅当再次编辑后才复跑 |

已存在的正确字段不重写：重复改写会丢失既有会话 ID 或改变溯源措辞，属于无收益风险。

## 9. 交付报告

| 项目 | 内容 |
|---|---|
| 字段变更 | `source` 与 `x-toml-ref` 的 before → after |
| 欠账句 | 命中条数、改写后的完成记录 |
| 质量门 | 分数、通过项数、退出码、原始命令 |
| 定点链接门 | 引用数、断链数、退出码 |
| 全集基线 | S0 基线 `B` → S4 复测值，是否持平 |
| 未做项 | 明确列出的跳过面或阻塞原因 |

## 10. 安全检查清单（逐项确认）

- [ ] 已确认镜像 toml 存在后才写 `x-toml-ref`
- [ ] 已确认 `x-toml-ref` 从 SKILL.md 目录解析到真实文件
- [ ] 已确认 `source` 不含 `/`、`\`、`.md/.toml/.py` token
- [ ] 已保留原有会话 ID 与溯源事实，未借改写删证据
- [ ] 已用磁盘实测值填写日期、CHANGELOG 版本与分类计数
- [ ] 已实跑质量门并确认 100/100、34 项全过、退出码 0
- [ ] 已实跑定点链接门并确认 0 断链
- [ ] 已记录全集基线并确认本次零新增断链
- [ ] 已回读实际文件验证 frontmatter 可解析、键名完整
- [ ] 未改动其他技能正文，未顺手“修复”既有 118 条断链

## 11. Gotchas（陷阱与反直觉行为）

1. `source` 自己就是被检查的路径字段；中文散文只有在不含 `.md/.toml/.py` 时才被整体跳过。
2. 切分只认 ASCII `+ , ;`；中文标点不切。一个英文逗号后面接路径，就能把一条正常散文变成断链。
3. `.meta` 在仓库根，不在 `.agents` 下；从 SKILL.md 上跳必须是三级 `../../../`。
4. `--check-x-toml-ref` 是废弃别名，传它会自动升级；文档和脚本里统一写 `--check-frontmatter-paths`。
5. `add-agents-frontmatter.py` 会把 Skill 格式判为专用 schema 直接跳过，不能指望批量脚本补这两个字段。
6. 全集链接门有 118 条既有断链；只报本技能命中数 + 基线差值，不要宣称「全库 0 断链」。
7. 质量门 100/100 不代表回指正确：推荐字段里没有 `source/x-toml-ref`，必须另跑链接门。
8. 先写 `x-toml-ref` 再补镜像，会得到一条新的悬空引用；顺序必须是镜像先行。
9. `session:` 前缀会被链接门跳过，但 `会话：<uuid>` 里的全角冒号不触发前缀规则；两种写法都安全，别混用半角冒号加空格。
10. 欠账句改写要保留「为什么登记」的上下文；只改状态、删掉理由，会让下一位读者失去判断依据。

## 12. 相关资产

- 链接门实现：`.agents/scripts/check-links.py`（`_extract_paths_from_value`、`--check-frontmatter-paths`）
- 质量门实现：`.agents/scripts/check-skill-quality.py` 与 `.agents/scripts/lib/check_skill_quality/constants.py`
- 批量补全工具：`.agents/scripts/add-agents-frontmatter.py`（会跳过 Skill 格式）
- 上游登记：`native-skill-surface-registration`；掉分修复：`skill-quality-gate-remediation`；镜像溯源：`skill-mirror-archive`
- 真实案例：`.agents/skills/oversized-tool-output-slicing/SKILL.md`（`source` 纯散文 + 三级 `x-toml-ref`，定点链接门 0 断链）

## 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-10-24 | 初始版本：S0 基线取证、镜像先行补 `x-toml-ref`、按链接门算法改写 `source`、欠账句改完成记录、双门与基线差值验收 |

---
name: skill-registry-count-drift-audit
version: 1.0.0
description: "审计 Skill 登记面的分类计数漂移：把 .agents/skills/README.md 与 .agents/capability-registry/02-skills.md 每个分类标题声明的（N个）与该节实际表格数据行逐一比对，先自证计数器再下结论，区分表头漂移、多子表求和与跨面缺行三类，缺行只报告不擅改。当用户提到「登记面计数漂移」「表头数字和行数不一致」「README 与 registry 数量对不上」「命令集门面 11/10」「审计分类计数」「count drift」「核对（N个）」时必须使用此技能；不用于执行四处登记（用 native-skill-surface-registration），不用于判断推荐动作（用 skill-recommendation-disk-triage）。"
argument-hint: "[readme-path] [registry-path]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/README.md"
  - ".agents/capability-registry/02-skills.md"
source: "会话 0df2781d-fbf2-4120-8257-602ed49d4f65 的三版计数器失败—纠偏—收敛实测（工作流门面 6/50、内置镜像 21/8 两次误报；registry 命令集门面 11/10 缺行取证）"
x-toml-ref: "../../../.meta/toml/.agents/skills/skill-registry-count-drift-audit/SKILL.toml"
---

# 登记面分类计数漂移审计

登记面的分类标题写着「（N个）」，表体却可能少一行或多一行。本技能用一套**先自证、再判案**的只读流程，把「表头漂移」「多子表求和」「某登记面缺行」三类现象分开，输出可逐字复跑的证据报告。

目标产物：

1. 每个分类一行的「声明 / 实际 / 首表 / 子表数」表；
2. 同名分类的跨面名称差表，以及每个差集项的磁盘存在性；
3. 明确的退出码与「是否修改过任何文件」声明。

默认审计面：`.agents/skills/README.md`、`.agents/capability-registry/02-skills.md`。

## 1. 适用边界

适用：

- 怀疑分类表头数字与表体行数不一致，需要给出可复跑的判定。
- 两个登记面同一分类数量对不上，需要定位是「表头写错」还是「某面缺行」。
- 登记新 Skill 前后做一次基线核对，避免基于错误基数继续加减。

不适用：

- 执行四处登记、补表行、建 toml 镜像 —— 用 `native-skill-surface-registration`。
- 判断一条自动推荐该 create 还是 update —— 用 `skill-recommendation-disk-triage`。
- 质量门掉分修复 —— 用 `skill-quality-gate-remediation`。

> **为什么？** 计数审计与登记是两种权限：审计只需要读，登记会改受版本控制的共享文件。把两者混在一个流程里，容易在「还没证明表头是错的」时就把表头改掉，制造新的污染。

## 2. 输入与输出

| 输入 | 默认值 | 说明 |
|---|---|---|
| README 路径 | `.agents/skills/README.md` | 可换成任意同格式登记面 |
| registry 路径 | `.agents/capability-registry/02-skills.md` | 与 README 分类名可部分重叠 |
| 技能根目录 | 不传则跳过磁盘校验 | 传 `.agents/skills` 时对差集项检查 `<name>/SKILL.md` |
| `--section-scope` | `level` | `level`=下一条同级或更高级标题；`any`=下一条任意标题 |
| `--json` | 关闭 | 输出机器可读 JSON，便于二次比对 |
| `--strict` | 关闭 | 把「仅跨面缺行」也提升为退出码 1 |

输出结构固定如下，禁止只给一句「有漂移」：

```text
分类计数
  [OK|DRIFT] <分类名>  声明=N 实际=M 首表=F 子表=K

跨面名称差
  <分类名>: README 有而 registry 无 = [name(disk:yes/no), ...]
  <分类名>: registry 有而 README 无 = [...]

结论: X 处表头漂移, Y 处跨面缺行; 本次未修改任何文件
```

> **为什么？** 只报总数无法区分「计数器错了」和「登记面错了」。把首表行数与子表数一并暴露，人才能一眼看出多子表分类是否被首表误导。

## 3. 三步审计法

### 3.1 第一步：解析分类标题（允许标题内含空格）

```text
^(#{3,4})\s+(.+?)\s*[（(](\d+)\s*个[^）)]*[）)]\s*$
```

- 匹配 3–4 级标题；同时接受全角「（）」与半角「()」。
- 标题用非贪婪 `(.+?)` 且允许空格，`内置镜像 Skill`、`TeleAgent 平台镜像 Skill` 才不会漏。
- 先扫描并跳过 ``` / ~~~ 代码围栏，围栏内的伪标题不参与。

> **为什么？** 实测第一版正则只允许无空格标题，8 个分类只匹配到 4 个；漏掉的 4 个分类没有截断上一节，行数被累加，直接产出「工作流门面 6/50」这类假警报。若照假警报改表头，会把本来正确的数字改错。

### 3.2 第二步：以标题为界，统计区间内全部表格

1. 区间终点取「下一条同级或更高级标题」（`--section-scope level`，默认）。这样 `####` 子标题下的子表仍属于当前分类；若某面用 `####` 表示并列分类，改用 `--section-scope any`。
2. 表格判定：一行以 `|` 开头，且下一行是分隔行（形如 `|---|:---|`）。
3. 表头行与分隔行都不计入数据行；从分隔行之后连续统计 `|` 开头的行，遇到非 `|` 行即结束该表。
4. 区间内可能有多张表（如 `内置镜像 Skill` 的 work/global/design/code 四张）。**全部分表求和**后再与表头比对，同时记录首表行数与子表数。

> **为什么？** 只数首表会把「内置镜像 Skill 21 个」误判成 21/8；只数到下一个匹配的分类标题会把中间分类的行全部吞进来，产生 6/50。两个错误方向相反，但都会让人去改一个本来正确的表头。计数的第一职责是**不制造假阳性**，其次才是发现真问题。

### 3.3 第三步：三类判定与跨面名称差

| 判定 | 条件 | 动作 |
|---|---|---|
| 表头漂移 | 声明 ≠ 区间内全部数据行之和 | 先确认本文计数器已通过自检，再考虑修正表头 |
| 多子表求和 | 子表数 > 1 且 声明 = 各子表之和 | 判为一致；首表不等不算漂移 |
| 跨面缺行 | 同名分类两面的名称集合有差集 | 对差集项 `ls <技能根>/<name>/SKILL.md` 验盘，只报告，不擅改 |

跨面名称比对前要做归一化：去掉 Markdown 链接外壳、反引号、以及行首装饰符（例如 README 里的 `⭐ role-model-methodology` 要与 registry 的 `role-model-methodology` 视为同一项）。

> **为什么？** 表头漂移与缺行是两种病：前者改数字，后者补行。实测 registry「命令集门面」声明 11、实际 10，差集恰好是 `token-optimize-cmd`，且该技能磁盘存在、README 已登记 —— 真因是 registry 缺行，不是表头写错。若按「表头减一」修，会把正确的索引口径改坏，还会掩盖缺行。

## 4. 运行捆绑脚本

脚本零依赖，Node 14+ 即可；默认只读，不写任何文件。

```bash
# 0) 先自证计数器：夹具正向 + 负向断言，必须全 PASS
node .agents/skills/skill-registry-count-drift-audit/scripts/audit_surface_counts.js --self-test

# 1) 对两个登记面实跑（默认路径）
node .agents/skills/skill-registry-count-drift-audit/scripts/audit_surface_counts.js \
  --readme .agents/skills/README.md \
  --registry .agents/capability-registry/02-skills.md \
  --skills-root .agents/skills

# 2) 机器可读结果
node .agents/skills/skill-registry-count-drift-audit/scripts/audit_surface_counts.js \
  --readme .agents/skills/README.md \
  --registry .agents/capability-registry/02-skills.md \
  --skills-root .agents/skills --json
```

退出码：

| 码 | 含义 |
|---|---|
| 0 | 无发现 |
| 1 | 存在表头漂移（或 `--strict` 下的跨面缺行） |
| 2 | 仅存在跨面缺行 |
| 3 | 参数或文件读取错误 |

> **为什么？** 三版手写计数器各自踩一个坑，第四次还会再踩。把解析、分表、跨面差固化成一个带自检的脚本，后续每次审计都是同一把尺子；自检夹具则保证「尺子本身」没有随环境漂移。

## 5. 报告模板

```markdown
## 登记面计数审计

| 登记面 | 分类 | 声明 | 实际 | 首表 | 子表数 | 判定 |
|---|---|---|---|---|---|---|
| README | 完整Skill | 18 | 18 | 18 | 1 | OK |
| registry | 命令集门面 | 11 | 10 | 10 | 1 | DRIFT |

### 跨面名称差
- 完整Skill: README 有而 registry 无 = [trae-computer-use-ptc(disk:yes), meoo-cli(disk:yes)]
- 命令集门面: README 有而 registry 无 = [token-optimize-cmd(disk:yes)]

### 结论
- 表头漂移：1 处（registry/命令集门面）
- 跨面缺行：若干（见上）
- 本次是否修改文件：否
```

报告必须写出实际命令与退出码；缺行项必须带 `disk:yes/no`，否则无法区分「登记漏了」与「索引指向了已删除资产」。

## 6. 修复边界

- **默认只读**。审计结束停在报告，不自动改表头、不自动补行。
- **表头漂移**：只有在计数器通过自检、且该分类的「首表/子表数」解释得通时，才把声明改为实际值；改完立即复跑，确认变为 OK。
- **跨面缺行**：属于登记动作，转 `native-skill-surface-registration`；若缺行资产属于他人或来源不明，只报告，等用户确认。
- **禁止批量对齐**：不要用「把两面表头改成一样」的方式消除差异 —— README 与 registry 的分类基数本来就独立，差异可能反映真实的登记进度。
- **写前预检**：任何修改前重新读取目标文件；共享工作区可能有并发提交或 rebase，旧快照里的行号与计数会失效。

> **为什么？** 审计的价值在于把「哪个数字错了」证明到可以逐字复跑。先改后证，等于用一次新的猜测覆盖旧记录；而并发写入会让基于旧快照的修改直接冲突或丢失。

## 7. Gotchas（陷阱与反直觉行为）

1. 标题正则漏掉空格是最常见的假阳性来源：`TeleAgent 平台镜像 Skill`、`内置镜像 Skill` 都会被无空格正则跳过。
2. 区间不能延伸到「下一个匹配的分类标题」，否则中间未匹配分类的表格会被吞入上一节（实测 6/50）。
3. 只统计首表会把多子表分类误判为漂移（实测 21/8，真实为 8+6+4+3=21）。
4. 数据行计数必须剔除表头行与 `|---|` 分隔行；把分隔行算进去会恒定多 1。
5. 行首 `⭐` 等装饰符会让同名项在跨面差里变成两条假差集，比对前要归一化。
6. README 与 registry 的计数基数独立，同名分类数量不同不必然是错误；先看名称差与磁盘状态，再判性质。
7. 代码围栏里的示例标题是陷阱；解析器必须先做围栏屏蔽。
8. 同名分类在两面可能用不同标题文案（例如带来源说明后缀）；按去掉「（N个…）」后的标题精确比对，不做模糊匹配。
9. 共享工作区可能正在 rebase 或有并发提交：写入前必须重新读取文件，不能复用几分钟前的行号。
10. 退出码 2 表示「只有跨面缺行」；不要把它当成审计失败，它表达的是「需要登记动作」。

## 8. 安全检查清单（逐项确认）

- [ ] 已确认本次为只读审计，未修改任何登记面文件
- [ ] 已运行 `--self-test` 且全部断言 PASS，计数器本身已验证
- [ ] 已确认分类标题匹配数等于文件中带「（N个）」的 3–4 级标题数
- [ ] 已确认每个分类记录了首表行数与子表数，多子表分类未被首表误导
- [ ] 已对跨面差集逐项执行磁盘校验并标注 `disk:yes/no`
- [ ] 已确认报告含实际命令、退出码与「是否修改文件」声明
- [ ] 若发现缺行，已明确转入登记流程或仅报告，未擅改他人资产
- [ ] 若执行了任何修复，已复跑脚本并确认对应分类转为 OK

## 9. 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-10-24 | 初始版本：标题正则、区间与多子表计数、三类判定、自检脚本、跨面差与磁盘校验 |

## 参考

- 三版计数器的逐次输出与误报证据：[references/evidence-case.md](references/evidence-case.md)
- 审计脚本：[scripts/audit_surface_counts.js](scripts/audit_surface_counts.js)
- 登记动作：`native-skill-surface-registration`；推荐分诊：`skill-recommendation-disk-triage`

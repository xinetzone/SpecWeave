# 案例：ci-gate-effectiveness-audit 迁移与质量门分差

本案例来自会话 `511919f2-09d9-46aa-b6bb-a423d6f9e91d`，记录一次「只迁入内容 + 验收、正文不动」的真实迁移。它补齐了 `user-skill-sovereign-migration` 的两条边界：质量门 <100 时不能靠改正文凑分；质量门必须在源与目标两侧用同一命令对照。

## 1. 背景

`ci-gate-effectiveness-audit` 先在用户级目录 `~/.qoder/skills/ci-gate-effectiveness-audit` 创建并可工作，包含 3 个文件：`SKILL.md`、`references/verified-case-act-001.md`、`scripts/scan_gate_suppressions.py`。用户随后只说「迁移到 .agents/skills」。

批准范围由两个选择确定：

- 本次迁移的执行范围：只迁入内容 + 验收。
- 源目录收尾：保留源实体，暂不建联接。

## 2. 预检事实

| 检查项 | 结果 |
|---|---|
| 源路径形态 | 实体目录，`LinkType` 空、`Target` 空，非联接 |
| 源资源 | 3 个文件，无 `__pycache__` 残留 |
| 目标路径 | `.agents/skills/ci-gate-effectiveness-audit` 不存在，首次迁移 |
| 仓库根 | `D:/spaces/SpecWeave`，非 submodule |
| 登记面 | README、CHANGELOG、02-skills 均无同名条目，TOML 镜像不存在 |
| 并发脏文件 | README、CHANGELOG、02-skills 已被另一轮迁移修改；本轮不 stage、不 stash、不清理 |

## 3. frontmatter 的条件字段

本轮只新增两个字段：

```diff
 disable-model-invocation: false
+paths:
+  - ".agents/skills/ci-gate-effectiveness-audit/**"
+title: "CI 门禁有效性审计 Skill"
```

`source` 与 `x-toml-ref` 刻意未写。原因不是遗漏，而是链接门契约：

- `check-links.py --check-frontmatter-paths` 的默认字段是 `source`、`x-toml-ref`（`check-links.py:477`）。
- `.meta/toml` 镜像尚未创建；此时写入 `x-toml-ref` 必然报「文件不存在」。
- 本轮登记延后，因此两个回指字段一并延后。

结论：`x-toml-ref` 是条件字段。照模板无条件写入，会在内容尚未验收前先制造一条链接门断链。

## 4. 保真与链接门实测

| 检查 | 实测 |
|---|---|
| 正文 | 去掉 frontmatter 后逐字一致 |
| 资源 | `verified-case-act-001.md`、`scan_gate_suppressions.py` 的 SHA256 与源全等 |
| 绝对路径 | 扫描无命中 |
| 引用资源 | `references/`、`scripts/` 两个引用均存在 |
| 链接门 | `check-links.py --path <DST> --check-frontmatter-paths`：本地引用全存在、frontmatter 字段全有效、0 断链 0 警告，退出码 0 |

## 5. 质量门两侧分差

同一命令在源与目标各跑一次：

| 位置 | 分数 | 警告数 |
|---|---|---|
| 源（用户级） | 65 | 7 |
| 目标（主权区） | 70 | 6 |
| 分差 | +5 | −1 |

+5 恰好是新增 `paths` 消掉的那一条。残余 6 项警告为：

- `description.mandatory_phrase`
- `description.trigger_context`
- `why.explanations`
- `safety.idempotent`
- `safety.checklist`
- `open_standard.body.gotchas`

这 6 项在源侧逐条存在，因此定性为「既有内容特征、非迁入漂移」，而不是「迁移导致掉分」。

## 6. 停止点：范围排除正文时的 <100

迁移前规程只写「质量门未达 100 分时转 `skill-quality-gate-remediation`」。但本轮批准范围明示「只迁入内容 + 验收」「正文不动」，而修复技能会改正文。照规程转修复即越权。

实际动作：

1. 不改正文凑分。
2. 把 70 < 100、6 项残余警告、源/目标分差写入交付报告。
3. 明确标注「修复待下一轮单独授权」。
4. 不在本轮做四处登记与 Junction，避免把登记建立在未达标内容上。

用户随后单独说「开启下一轮，修掉剩余的质量警告」，修复才进入下一轮。

## 7. 可复用结论

1. **质量门要看分差，不只看目标分数**：目标 70 分可能是源侧 65 分的既有特征，+5 来自新增 `paths`；只看 70 会误判为迁移失败。
2. **<100 的处置取决于批准范围**：允许改正文才转修复；排除正文时停止修复、如实上报，把修复留给下一轮。
3. **`x-toml-ref` 是条件字段**：镜像未建时省略；登记延后时 `source`/`x-toml-ref` 一并延后，避免自造链接门断链。
4. **保真与质量门是两道独立结论**：正文逐字一致、哈希全等、链接门 0 断链，不等于质量门达标；两者要分别报告。

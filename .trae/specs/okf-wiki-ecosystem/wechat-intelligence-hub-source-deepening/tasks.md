# 任务清单（Spec Mode · tasks.md）

> 对应 [spec.md](spec.md) 的 Requirements；状态为 2026-11-06 V 阶段终检结果。

## 实施清单

- [x] 1. 启动协议回读根 `AGENTS.md`、`context-routing.md`、`projects/AGENTS.md`、`awesome-okf-xs/AGENTS.md`、`external/AGENTS.md`、内容敏感度预检规范（三锚点确认）
- [x] 2. 解析 `/七概念` 别名 → `seven-concepts.md` + `seven-concepts-cmd`；加载 `source-code-to-okf-wiki` v1.5.0 与 `source-code-to-okf-adversarial-update` 模式
- [x] 3. 内容敏感度预检：源码为公开开源代码 → **Public**，走标准 Spec Mode
- [x] 4. G0 信源稳定性：锁定 commit `fb6a42c`，记录 remote URL / SHA / 提交时间 / 工作区 clean；`check-source-path-stability.py` 定向扫描 rc=0
- [x] 5. R 阶段事实采集：`git ls-tree` HEAD 口径规模 + `ast` 解析 38 个 `.py`；产出 F-058~F-101
- [x] 6. **AST 脚本修正**：仅处理 `ast.Assign` 导致带注解常量（`TOOL_SPECS: dict[...] = {...}`）被漏掉、字段数误返回 0 → 补 `ast.AnnAssign` 后恢复 266
- [x] 7. I 阶段对抗性对账：首轮 8 项 ⚠️ 逐项给源码证据与判定；产出漂移分类 D1~D5 与首轮可信度评估
- [x] 8. E 阶段信源先行落盘：`references/source-code-map.md` → `references/source-code-verification.md` → `concepts/06~09` → 三级 `index.md` → 根 `index.md` → `log.md`
- [x] 9. 定向修订（不重写首轮结论）：根 `index.md` 六处区块、`concepts/02` 修订框、`references/verification.md` 追加「源码轮追记」节
- [x] 10. 计数断言双口径复核：R 用 AST/grep，V 用正则/awk；发现并修正 `style-previews` 文件数 9→**10**
- [x] 11. Grep 级 API 真实性验证：全部类名/函数名/常量名在上游源码验证存在；无写入型函数反向验证
- [x] 12. V 阶段机械门禁：`check-utf8.py` / `check-toctrees.py` / `check-bundles-index.py` / `check-asset-baseline.py` / `check-source-path-stability.py` 全 rc=0
- [x] 13. F 编号双份登记核验：spec `facts.md` ↔ bundle `source-code-map.md` 集合相等（44 条，F-058~F-101），与首轮 57 条零重叠
- [x] 14. 链接与 frontmatter 核验：71 条相对链接 0 断链、0 绝对路径、必填字段齐备、`okf_version` 仅在根 `index.md`

## 门禁结果

| 门禁 | 结果 | 说明 |
|------|------|------|
| `check-utf8.py` | ✅ rc=0 | 12983 个文件均为有效 UTF-8 |
| `check-toctrees.py` | ✅ rc=0 | 全部 index.md 引用有效、内容文档可达（首轮记录的并行 WIP 红灯已由并行会话自行修复） |
| `check-bundles-index.py` | ✅ rc=0 | 9 域 / 64 组 / 719 束，五面一致 |
| `check-asset-baseline.py` | ✅ rc=0 | 基线口径一致，规模数字无矛盾，行尾归一自证成立（首轮 +79248 残差已收敛） |
| `check-source-path-stability.py` | ✅ rc=0 | `scanned_files=18`、`blocking_count=0` |
| F 编号双份登记 | ✅ | 各 44 条，F-058~F-101 连续无跳号、集合相等、双向差集为空 |
| 相对链接 / frontmatter | ✅ | 71 条相对链接断链 0；必填 frontmatter 缺失 0；`okf_version` 仅根 `index.md` |
| 计数断言双口径 | ✅ | 唯一修正项 `style-previews` 9→10，其余全量复核一致 |

## 复跑命令

```bash
cd projects/awesome-okf-xs
python scripts/check-utf8.py
python scripts/check-toctrees.py
python scripts/check-bundles-index.py
python scripts/check-asset-baseline.py
cd ../..
python .agents/scripts/check-source-path-stability.py \
  --path "projects/awesome-okf-xs/doc/bundles/jishu/ai/products/wechat-intelligence-hub" --json
```

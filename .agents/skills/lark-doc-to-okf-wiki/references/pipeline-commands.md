# 采集命令手册（lark-cli）

> 所有命令均为只读（Risk: read）。执行前确认 `lark-cli --version` 可用；不可用时先按插件说明安装。

## 0. 预检与幂等

```bash
lark-cli --version
lark-cli docs +fetch --help
lark-cli whiteboard +export --help
```

幂等约定：

- 采集产物落在临时目录（如 `playground/_tmp/<topic>/`），重复执行覆盖同名文件即可，不影响知识包。
- 知识包目录内只放最终产物，不重复写入原始 JSON。
- 同一 token 重复导出结果一致；若不一致，先核对 `revision_id` 是否变化。

## 1. 正文与评论

```bash
lark-cli docs +fetch \
  --doc "<doc-url-or-token>" \
  --doc-format markdown > raw.md
```

返回体（JSON）关键字段：

| 字段 | 用途 |
|---|---|
| `data.document.content` | 正文（markdown 或 DocxXML 片段） |
| `data.document.document_id` | 写进知识包 frontmatter |
| `data.document.revision_id` | 版本锚定，改版后据此复核 |
| `data.reference_map.comments` | 评论 sidecar（引用、回复、图片 token） |

常用变体：

| 目的 | 命令 |
|---|---|
| 只看标题结构 | `--scope outline --max-depth 2` |
| 取某标题下全文 | `--scope section --start-block-id <id>` |
| 关键词定位 | `--scope keyword --keyword "foo\|bar"` |
| 保留块 ID 与样式 | `--doc-format xml --detail with-ids` |

注意：`--detail with-ids` 只在 `--doc-format xml` 下生效；与 markdown 同传会收到告警并忽略该参数。

## 2. 画板导出

```bash
# 结构化节点：文本、坐标、类型、层级
lark-cli whiteboard +export \
  --whiteboard-token <token> \
  --output-type raw > wb01.json

# 预览图：核对版式、颜色、箭头
lark-cli whiteboard +export \
  --whiteboard-token <token> \
  --output-type preview --output ./wb01.jpg --overwrite
```

输出类型对照：

| 类型 | 适用 | 失败表现 |
|---|---|---|
| `raw` | 所有画板（推荐默认） | 无 |
| `preview` | 所有画板，用于版式判读 | 扩展名不匹配时报 `failed_precondition` |
| `source` | 仅含 Mermaid/PlantUML 代码块的画板 | 纯原生画板返回 `no code blocks found` |
| `svg` | 需要矢量重绘时 | 视画板内容而定 |

批量导出（PowerShell）：

```powershell
$map = @{ "wb01"="<token1>"; "wb02"="<token2>" }
foreach ($k in $map.Keys) {
  lark-cli whiteboard +export --whiteboard-token $map[$k] --output-type raw > "$k.json"
  lark-cli whiteboard +export --whiteboard-token $map[$k] --output-type preview --output "$k.jpg" --overwrite
}
```

## 3. 采集完成的自检

- [ ] `raw.md` 非空，且能看到 `revision_id`
- [ ] 正文中 `whiteboard` 块数量 = 已导出画板数
- [ ] 每块画板的 `raw` JSON 可解析（`ok: true`）
- [ ] 每块画板都有对应 `.jpg` 预览，且文件大小 > 0
- [ ] 评论 sidecar 已保留（若原文有评论）

## 4. 临时目录与清理

- 原始 JSON、TSV 抽取件、预览图都放临时目录；只把最终预览图复制进知识包 `assets/`。
- 临时目录按仓库约定不纳入版本控制；交付完成后可保留供复核，也可清理。

---
id: "flat-nested-hybrid-scan"
source: "docgen.py _dash_scan_themes() 扁平主题目录扫描bug修复"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/flat-nested-hybrid-scan.toml"
---
# 扁平+嵌套混合目录扫描模式

## 问题

目录扫描器假设"两层结构"（父目录 → 子目录 → 目标文件），但实际数据存在两种合法结构：
- **嵌套结构**：`theme/spec/tasks.md`（子目录中包含目标文件）
- **扁平结构**：`theme/tasks.md`（目标文件直接在父目录下）

仅扫描嵌套结构会导致扁平结构的条目被静默忽略——输出 0/0 但不报错，难以发现。

典型症状：
- 看板/索引中某些条目显示 0/0 完成，但实际 tasks.md 中所有任务已勾选
- 新增扁平结构条目后，扫描器无任何报错但统计数量不变
- 调试时发现 `spec_dirs` 列表为空，但 `theme_dir` 下确实存在 `tasks.md`

## 解决方案

先执行嵌套扫描，结果为空时回退到扁平结构检查——将父目录自身作为条目加入：

```python
spec_dirs = [
    d for d in theme_dir.iterdir()
    if d.is_dir() and d.name not in EXCLUDED_DIRS and (d / "tasks.md").exists()
]
if not spec_dirs and (theme_dir / "tasks.md").exists():
    spec_dirs = [theme_dir]  # 扁平结构：theme 自身即 spec
```

## 代码

### ❌ 反模式：仅扫描嵌套结构

```python
for theme_dir in ordered:
    spec_dirs = sorted([
        d for d in theme_dir.iterdir()
        if d.is_dir() and d.name not in EXCLUDED_DIRS and (d / "tasks.md").exists()
    ])
    # Bug: 扁平结构（theme_dir 自身含 tasks.md）被忽略
    specs = [_dash_scan_spec(d) for d in spec_dirs]
    themes.append(ThemeStatus(name=theme_dir.name, specs=specs))
```

### ✅ 推荐模式：嵌套优先，扁平回退

```python
for theme_dir in ordered:
    spec_dirs = sorted([
        d for d in theme_dir.iterdir()
        if d.is_dir() and d.name not in EXCLUDED_DIRS and (d / "tasks.md").exists()
    ])
    if not spec_dirs and (theme_dir / "tasks.md").exists():
        spec_dirs = [theme_dir]  # 扁平结构：theme 自身即 spec
    specs = [_dash_scan_spec(d) for d in spec_dirs]
    themes.append(ThemeStatus(name=theme_dir.name, specs=specs))
```

## 适用场景

- 目录扫描器/索引生成器（文档索引、Spec 看板、应用清单）
- 文件系统遍历工具需要同时支持 `parent/child/file` 和 `parent/file` 两种结构
- 从旧版扁平结构迁移到新版嵌套结构期间的过渡期

## 设计原则

1. **嵌套优先**：先尝试嵌套结构（更丰富的子目录信息），退化时回退到扁平结构
2. **避免静默失败**：回退逻辑必须显式（`if not spec_dirs`），不能依赖隐式行为
3. **防御性条件**：`(theme_dir / "tasks.md").exists()` 确保退化只在目标文件确实存在时触发

## 成熟度

L2 已验证 — 修复后 docgen.py 看板从 226 个 Spec 正确识别到 276 个，jupyter-ssh-base 等 50+ 个扁平 Spec 从 0/0 变为 1/1 完成。

## 交叉引用

- 来源：jupyter-ssh-base 项目完工复盘 [retrospective-jupyter-ssh-base-20260724](../../reports/project-reports/retrospective-jupyter-ssh-base-20260724/README.md#L66-L74)
- 修复提交：`daa80b1e fix(docgen): 修复扁平主题目录扫描bug`
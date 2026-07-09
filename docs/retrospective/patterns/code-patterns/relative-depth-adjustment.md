---
id: "relative-depth-adjustment"
source: "../../reports/project-governance/documentation-governance/retrospective-link-fix-depth-adjustment-20260626/insight-extraction.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/relative-depth-adjustment.toml"
---
# 相对路径深度自动校正算法（relative-depth-adjustment）

## 模式类型
代码模式

## 成熟度
L2 已验证（14个真实断链+7个测试用例验证通过）

## 适用场景
- Markdown/HTML 文件间的相对链接维护
- 目录重构/原子化拆分后的批量链接修复
- 文档系统中文件移动后的引用更新

## 问题背景
目录原子化（单文件 → 目录+多文件）是文档项目高频操作，会导致大量相对路径 `../` 层数错误。手动逐个计算层级效率低且易出错。

## 核心假设
断链路径中，非 `../` 部分（文件名和中间目录名）通常保持不变，只是相对根的位置发生了变化。

## 算法伪代码

```python
def try_adjust_relative_depth(broken_url, source_file, max_adjust=3):
    """
    尝试调整相对路径中 ../ 的数量来寻找有效目标
    
    策略：
    1. 统计现有 ../ 数量 N
    2. 提取剩余路径段 R（去除 ../ 后的部分）
    3. 优先尝试增加深度 N+1, N+2, ..., N+max_adjust
    4. 再尝试减少深度 N-1, N-2, ..., 0
    5. 对每个候选，同时检查：
       - 候选路径本身是否存在（文件引用）
       - 候选路径 + "/README.md" 是否存在（目录引用）
    6. 返回第一个有效目标，或 None
    """
    parts = broken_url.split('/')
    dotdot_count = sum(1 for p in parts if p == '..')
    remaining = [p for p in parts if p != '..']
    base_dir = source_file.parent
    
    # 优先尝试增加深度（原子化/拆分场景）
    for delta in range(1, max_adjust + 1):
        candidate = build_path(base_dir, dotdot_count + delta, remaining)
        if is_valid(candidate):
            return candidate
        if is_valid(candidate / "README.md"):
            return candidate / "README.md"
    
    # 再尝试减少深度（合并/上移场景）
    for delta in range(1, min(dotdot_count, max_adjust) + 1):
        candidate = build_path(base_dir, dotdot_count - delta, remaining)
        if is_valid(candidate):
            return candidate
        if is_valid(candidate / "README.md"):
            return candidate / "README.md"
    
    return None
```

## 关键设计决策

1. **增加深度优先**：原子化拆分是文档项目高频操作，文件通常向更深处移动
2. **目录引用处理**：自动尝试 `README.md`，Markdown 中目录链接默认指向其下的 README
3. **调整幅度限制**：默认 ±3 级，足够覆盖大多数重构场景，避免过深搜索导致误匹配
4. **存在性校验**：只有目标真实存在才返回，确保零误报

## 成功案例

| 场景 | 断链数 | 修复成功率 | 误报率 |
|------|--------|-----------|--------|
| 本次断链修复 | 14 | 100%（10/10适用场景） | 0% |

> **关联模块**：
> - `fix-priority-chain.md` — 修复优先级链（本算法为第一优先级策略）
> - `dry-run-first.md` — dry-run 安全修改模式
> - `context-aware-path-resolution.md` — 上下文感知路径解析

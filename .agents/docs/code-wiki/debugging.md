---
source:
  - ../../../apps/AGENTS.md
  - ../../../.gitmodules
  - ../../scripts/lib/project.py
  - ../../scripts/lib/stage_guardrails/runtime.py
  - ../../scripts/sg_dashboard/parser.py
  - ../../../docs/tasks.py
status: stable
updated_at: 2026-08-23
---

# 调试指南

## 先判断是哪一层出问题

在 `SpecWeave` 中，问题通常来自 4 个层面：

| 层面 | 典型症状 | 先看哪里 |
|---|---|---|
| 路由层 | 智能体读错规范、走错区域 | [AGENTS.md](../../../AGENTS.md#L3-L32) |
| 工作树层 | 路由表里有目录，但当前 checkout 没有 | [apps/AGENTS.md](../../../apps/AGENTS.md#L37-L61) 与当前文件树 |
| 脚本层 | 检查器/生成器运行失败 | `.agents/scripts/` |
| 文档层 | Sphinx 构建失败、链接断裂 | `docs/` 与 `.agents/docs/` |

## 常见问题 1：规范文件和当前工作树不一致

### 现象

- `apps/AGENTS.md` 提到了很多应用，但当前工作树里找不到对应目录。
- Code Wiki、README 或导航表指向一个当前不存在的路径。

### 排查方法

1. 先看规范声明是否存在，例如 [apps/AGENTS.md](../../../apps/AGENTS.md#L37-L61)。
2. 再看当前工作树是否真的存在该目录。
3. 最后用 [`.gitmodules`](../../../.gitmodules#L1-L35) 判断它是否应该来自 submodule。

### 处理原则

- 把“规范蓝图”和“当前 checkout 实况”分开记录。
- 不要因为路由表里出现某个路径，就默认当前工作树一定存在。

## 常见问题 2：脚本找不到项目根目录

### 现象

- 从非仓库根目录运行脚本时出现路径错误。
- 某些脚本对 `AGENTS.md` 或 `.agents/` 定位失败。

### 关键实现

[resolve_project_root()](../../scripts/lib/project.py#L18-L53) 的逻辑是：

- 优先向上查找 `AGENTS.md`
- 找不到时回退到 `README.md`

### 建议

- 优先在仓库根目录执行主仓脚本。
- 如果编写新脚本，优先复用 `lib.project`，不要手写 `parent.parent.parent`。

## 常见问题 3：阶段守卫拦截了操作

### 现象

- 某个动作被提示“不允许在当前阶段执行”。
- 日志里出现拦截、绕过或边界拒绝信息。

### 关键入口

- [GuardrailRuntime](../../scripts/lib/stage_guardrails/runtime.py#L83-L207)
- [BoundaryChecker](../../scripts/lib/stage_guardrails/boundary.py#L450-L549)
- [StageStateManager](../../scripts/lib/stage_guardrails/state/manager.py#L21-L115)

### 排查顺序

1. 当前是否已经进入某个阶段。
2. 当前角色是否合法。
3. 当前操作是否属于只读豁免。
4. 是否触发了 baby-code 探针豁免逻辑。

### 推荐做法

- 先看 `current_stage`、`current_role`。
- 再检查 `BoundaryChecker.check()` 返回的 `violation_type` 与 `deny_reason`。

## 常见问题 4：SG Dashboard 没有读到日志

### 现象

- 仪表盘为空。
- 明明有日志文件，但统计结果为 0。

### 关键实现

[parse_log_file()](../../scripts/sg_dashboard/parser.py#L39-L77) 只会处理包含以下前缀的行：

- `[SG-LOG]`
- `[PDR-LOG]`

### 排查方法

1. 确认日志文件编码是 UTF-8。
2. 确认日志行真的包含上面的结构化前缀。
3. 确认日志目录路径正确，且文件后缀在 `*.log` 或 `*.txt` 范围内。

## 常见问题 5：文档站构建失败

### 现象

- `invoke html` 失败。
- `sphinx-build` 未找到。
- `linkcheck` 或 `doctest` 阶段报错。

### 关键依据

[docs/tasks.py](../../../docs/tasks.py#L26-L51) 通过 `subprocess.run()` 调用 `sphinx-build -M`，如果系统中没有 `sphinx-build`，会直接抛出友好的 `Exit` 错误。

### 排查方法

1. 确认已安装 `docs/requirements.txt`。
2. 确认 `sphinx-build` 在 PATH 中，或通过 `SPHINXBUILD` 显式指定。
3. 如果只有外链检查失败，可先单跑 `invoke linkcheck` 缩小范围。

## 常见问题 6：导航或链接批量更新后出现断链

### 建议工具链

先后运行：

```powershell
python .agents\scripts\build-ref-index.py --stats
python .agents\scripts\check-links.py
python .agents\scripts\docgen.py nav
```

如果是文件移动后的修链场景，再用 `link_fixer.fix_broken_links()` 或相应包装脚本。

## 调试策略建议

### 先确认事实，再修问题

这个仓库里很多错误并不是代码逻辑 bug，而是“路由声明、工作树状态、submodule 初始化、文档主容器”之间的认知偏差。优先确认：

1. 我看到的是规范蓝图还是当前工作树？
2. 这个路径来自主仓还是 submodule？
3. 这一步属于文档问题、脚本问题还是路由问题？

### 缩小范围优先

不要一开始就跑全量 CI。更高效的顺序通常是：

1. 复现最小命令
2. 确认输入路径
3. 单跑对应脚本
4. 最后再跑全量检查

## 最小排障命令集

```powershell
python .agents\scripts\repo-check.py all
python .agents\scripts\check-links.py
python .agents\scripts\docgen.py nav
cd docs; invoke html
```

如果是 submodule 相关问题，再补：

```bash
git submodule status
git submodule update --init --recursive
```

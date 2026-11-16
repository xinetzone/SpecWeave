---
name: stale-path-remediation
version: 1.0.0
description: "当用户提到『路径失效』『硬编码目录不存在』『迁移后 No such file or directory』『脚本计数为 0／扫描 0 个文件』『frontmatter source 断链』，或需要处置仓库重构、目录迁移、submodule 搬迁后残留的失效引用时，必须使用此技能。五步闭环：S1 定位失效路径（grep 全部消费方：脚本/CI/钩子/文档/frontmatter）→ S2 证明目标消失（Test-Path/Glob 零命中 + git log 取证，不靠报错猜测）→ S3 找权威继任者（迁移落点与规范工具，守住 submodule 只读边界）→ S4 自定位最小修复（Path(__file__) 回溯、委托 shim、退役守卫 exit 2 三处方，不重写领域逻辑、不写机器绝对路径）→ S5 实跑取证（真实执行＋临时夹具＋测试回归，区分契约退出码与崩溃，夹具无残留）。封装 check_mermaid.py 委托化、count_wikis.py 退役守卫、frontmatter source 断链修复三个同会话实战案例。"
argument-hint: "<失效路径或报错现象> [载体：脚本/文档/frontmatter/CI]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/stale-path-remediation/**"
  - "check_mermaid.py"
  - "count_wikis.py"
  - "docs/tech/references/trae-project-adaptation-guide.md"
title: "迁移失效路径处置 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/stale-path-remediation/SKILL.toml"
---

# 迁移失效路径处置 Skill

> 把「这个路径怎么没了」从一次凭感觉的点修复，变成一条可复跑、可取证的五步闭环：**定位 → 证伪 → 继任 → 最小修复 → 实跑取证**。

本 Skill 处置的对象是**迁移后失效的路径引用**：仓库重构、目录迁移、`.agents/docs/` 废止、submodule 搬迁之后，脚本、文档与元数据里残留的、指向已消失目标的路径。目标是让失效点要么重新指向权威继任者，要么以显式诊断退役，而不是裸崩溃或静默返回零。

## 1. 何时使用

### 触发场景

当用户提到以下任一信号时触发：

- 「路径失效了」「硬编码的目录不存在」「迁移后报 No such file or directory / FileNotFoundError」；
- 「脚本跑出来计数是 0」「扫描了 0 个文件」但目录里明明有内容；
- 「frontmatter 的 source 断链」「x-toml-ref 指向不存在的文件」「Markdown 链接层级不对」；
- 仓库重构、整体迁移（如 2026-08-31 `.agents/docs/` → 根 `docs/`）、submodule 搬迁后的残留引用排查与修复；
- 接手老脚本时发现机器绝对路径（如 `d:\AI\...`）、写死的文件清单。

### 不适用与边界路由

| 场景 | 归属技能 | 分界 |
|---|---|---|
| 文件读完后、写入前被并发会话改写，Edit 报 0 occurrences | stale-read-edit-reconciliation | 那个文件还在，是内容漂移；本技能处理目标已消失 |
| 许可证/版本号/分类等跨文件声明不一致 | declared-consistency-fix | 声明漂移走 git 考古定真源；本技能只处理路径类失效 |
| 日常 Markdown 断链检测 | link-check-cmd | 它是检测器；本技能是路径类检出结果的修复规程 |
| S5 临时夹具的建测清安全 | windows-temp-fixture-teardown-safety | 夹具生命周期纪律以该技能为准 |
| 退出码 1 是契约检出还是崩溃 | bundled-script-exit-code-ambiguity | S5 取证时按该技能的三断言判别 |
| 失效点本身是 Skill 登记面 | native-skill-surface-registration | 登记面写入走四面登记流程 |

## 2. 失效路径的四种形态

先判型，再选 S4 的修复处方。判型靠 S1/S2 的取证事实，不靠报错文案。

| 形态 | 典型特征 | 实测样例 | 首选处方 |
|---|---|---|---|
| F1 机器绝对路径 | 盘符 + 作者本机目录，换机器即失效 | `count_wikis.py` 第 3 行 `d:\AI\docs\knowledge\learning` | P1 自定位回溯 + P3 退役守卫 |
| F2 相对路径层级错误 | 文件迁移后深度变化，`../` 少一级或多一级 | frontmatter source `../../.trae/...` 应为 `../../../.trae/...` | 按文件实际深度重算层级 |
| F3 写死的已删除清单 | 脚本内硬编码一组文件/目录，目标整体迁移或废止 | `check_mermaid.py` 149 行硬编码已删除的 wsl-wiki 四文件 | P2 委托 shim |
| F4 元数据断链 | frontmatter `source`/`x-toml-ref`、TOML 镜像指向空目标 | 同源 TOML 缺 `standards-tools/` 路径段 | 主文件与镜像同源修正 |

## 3. 五步法 S1–S5

### S1 定位失效路径：枚举全部消费方

拿到失效信号后，先用失效路径的关键段做全仓 grep，把所有消费方一次枚举干净：脚本、CI workflow、钩子、文档、frontmatter、测试、TOML 镜像。只修第一个命中点就收工，必然留下同类断链。

- Windows 环境用 Grep 工具或 `Select-String`；Glob 不支持花括号 `{a,b}` 语法，会返回假的 No file found，拆成简单 pattern 分别验。
- 对脚本类载体同时查调用面：谁在 CI/钩子里调用它（grep 脚本名），避免改了入口没改调用参数。

### S2 证明目标消失：零命中 + git 考古

对每个被指向的目标，用两条独立证据证明它确实消失，而不是「我没找到」：

1. `Test-Path <目标>`（PowerShell）或 Glob/LS 零命中，记录命令与输出；
2. `git log --oneline -- <目标路径>` 找到删除/迁移提交，区分三种结局：**搬走了**（有 rename/move 提交）、**删除了**（有 delete 提交）、**本仓从未存在**（机器路径或外部依赖）。

> **为什么 S2 不能只看报错？** 报错只证明「这次访问失败」，不证明目标的命运。权限不足、cwd 不对、单文件参数被扫描器跳过都会产出与「路径消失」相同的报错，但修复方向完全不同。零命中是空间证据，git log 是时间证据，两者交叉才能把 F1~F4 判型坐实。

### S3 找权威继任者：迁移落点与规范工具

目标搬走了就找落点，能力废止了就找规范继任者：

- 按 S2 的迁移提交顺藤摸瓜，确认内容的新位置（如旧 `docs/knowledge/learning` 的 0x 分类已整体迁入 submodule `projects/awesome-okf-xs/doc/bundles/`）；
- 若继任能力位于 submodule（实测继任工具为该子模块 `doc/_ext/okf_inventory_builder.py`），记住 submodule 是只读边界：只能委托调用或在主仓建 shim，禁止就地修改；
- 找不到继任者时，不臆造新工具，转 P3 退役守卫并在诊断信息里写明退役事实。

### S4 自定位最小修复：三处方选型

修复只允许落在「定位方式、转发方式、退役方式」三层，不重写继任者的领域逻辑。

> **为什么强调最小修复？** 失效脚本的价值是它的调用入口与 CLI 契约，不是它体内的领域实现。重写逻辑会制造第二份真相，继任者以后演进时两份必然漂移；最小修复让真相始终只有继任者一份，旧入口只负责把请求准确送过去。

### S5 实跑取证：真实执行 + 夹具 + 回归

修复完成后按三层证据验收，全部记录命令与输出：

1. **真实执行**：跑真实命令验证行为，`py_compile` 只证明语法不证明行为；
2. **临时夹具**：在 `.temp/` 下建最小夹具验证正常路径（如统计夹具 4/4 正确），夹具按单进程建测清管理，收尾无残留；
3. **测试回归**：复跑该脚本关联的既有测试与链接门，确认无断链、无回归；历史基线项（如 `mermaid-baseline.json` 里的存量 `<br/>` 错误）先与基线比对再归因，不算本次回归。

## 4. 三处方：最小修复模式

### P1 自定位回溯

把 cwd 依赖与机器绝对路径替换为脚本自定位：

```python
REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_BASE = REPO_ROOT / "docs" / "knowledge"
```

适用 F1 与任何「在作者机器上能跑、换机器就失效」的脚本。`__file__` 不依赖调用方 cwd，克隆到任意目录都成立。

> **为什么禁止机器绝对路径？** 它把脚本的正确性绑定在单台机器的目录结构上，而仓库的本质是可克隆的——任何不可克隆的路径假设都是定时炸弹，且不会产生错误码，只会在别人的环境里静默失效。

### P2 委托 shim

保留旧入口的 CLI 表面（参数透传、`--help`、版本校验），把领域行为整体委托给 S3 确认的权威工具：

```python
# 旧脚本瘦身为转发层：解析参数 → 版本校验 → subprocess 转发权威工具
import subprocess, sys
sys.exit(subprocess.call([sys.executable, str(REPO_ROOT / ".agents/scripts/repo-check.py"), "mermaid", *sys.argv[1:]]))
```

适用 F3。实测中 149 行硬编码脚本瘦身为 44 行 shim 后，`--help` 正常、参数透传、72 条既有测试全过。

### P3 退役守卫

能力确已废止且无继任者时，保留入口但加显式守卫，禁止静默零结果：

```python
def main(base: Path) -> int:
    if not base.exists():
        print(f"[退役] 统计目标已迁移至 <继任位置>，本入口不再产出计数", file=sys.stderr)
        return 2  # 区别于正常 0 与检出 1
```

适用 F1 中目标整体废止的情形。退出码要与正常完成（0）、契约检出（1）区分开，退役诊断写明继任位置，让后来者知道该去哪里。

## 5. 三个实战案例（2026-11-16 同会话）

### 案例一：frontmatter source 断链（F2 + F4）

- 现象：[trae-project-adaptation-guide.md](../../../docs/tech/references/trae-project-adaptation-guide.md) 的 `source` 指向 `.trae/specs/` 但链接门报断链。
- 取证：文件位于 `docs/tech/references/`（仓根下三层），原 `../../.trae/` 只回退两层；同源 TOML 镜像还缺 `standards-tools/` 路径段。
- 修复：主文件改 `../../../.trae/specs/standards-tools/...`；TOML 镜像补齐同源段。
- 取证闭环：`check-links.py` 实扫 references 目录 22 文件全部通过、退出码 0。

### 案例二：check_mermaid.py 委托化（F3 → P2）

- 现象：仓根 [check_mermaid.py](../../../check_mermaid.py) 硬编码四个已随 `.agents/docs/` 废止而删除的 wsl-wiki 文件。
- 取证：grep 确认无 CI/钩子引用其他参数契约；权威继任者是 `.agents/scripts/repo-check.py mermaid`。
- 修复：149 行硬编码改为 44 行委托 shim，保留 python310 版本校验与参数透传。
- 取证闭环：`--help` 正常；目录级实扫正确透传退出码 1（14 个 `<br/>` 错误属 `mermaid-baseline.json` 历史基线，3 个既有文件）；`test_checks_mermaid.py` 72 passed。

### 案例三：count_wikis.py 退役守卫（F1 → P1 + P3）

- 现象：[count_wikis.py](../../../count_wikis.py) 第 3 行写死 `d:\AI\docs\knowledge\learning`。
- 取证：`Test-Path` 为 False；旧 0x 分类结构全仓绝迹，内容迁入只读 submodule，权威工具是子模块内的 `okf_inventory_builder.py`（不可改）；无 CI/钩子引用。
- 修复：`REPO_ROOT = Path(__file__).resolve().parent` 自定位 + `main(base)` 守卫（目标不存在 → stderr 退役诊断、退出码 2）；原统计逻辑原样保留，目标存在时仍可工作。
- 取证闭环：实跑退出码 2 且诊断正确；`py_compile` 退出码 0；`.temp/cw-verify` 临时夹具统计 4/4 正确；夹具与 pyc 当场清理无残留。

## 6. 反模式

1. **裸崩溃**：让 `FileNotFoundError` traceback 直接冒到用户面前，没有诊断、没有继任指引。
2. **静默零计数（假绿）**：目标缺失时返回 0 或空集且退出码 0，把「失效」伪装成「没有数据」——比崩溃更危险，因为下游会当真。
3. **重写权威工具逻辑**：把继任者的领域算法复制回旧脚本，制造双份真相与必然漂移。
4. **机器绝对路径**：任何盘符开头、只在作者机器成立的路径。
5. **只修首个命中**：不枚举全部消费方，留下 CI、文档、镜像里的同类断链。
6. **越界改 submodule**：在只读子模块里就地修继任工具，主仓无法追踪该改动。
7. **单文件参数假绿**：扫描器收到单个文件路径时输出「扫描文件: 0」且退出码 0，须改用目录级实扫验证。

## 7. 安全检查清单（逐项确认）

写盘与收尾前逐项核对：

- [ ] 已枚举全部消费方（脚本/CI/钩子/文档/frontmatter/测试/TOML 镜像），grep 零遗漏后才动手
- [ ] 已验证失效目标 Test-Path/Glob 零命中，并保存 git log 取证命令与输出
- [ ] 已确认继任者身份（迁移落点或权威工具），submodule 只读边界未被突破
- [ ] 修复处方与 diff 范围已预览，写盘前获得用户确认（预检门）
- [ ] 已检查修复中无机器绝对路径、无 cwd 依赖，路径全部自定位或按实际深度相对引用
- [ ] 已执行真实命令取证（非仅语法编译），契约退出码与未捕获崩溃已区分
- [ ] 临时夹具按单进程建测清管理，收尾验证无残留（夹具目录与 `__pycache__` 已删除）
- [ ] 已复跑关联测试与链接门，结果无断链、无回归，历史基线项已单独标注归因
- [ ] 同源元数据（frontmatter source、TOML 镜像）已更新并与主文件口径一致

## 8. 陷阱与反直觉（Gotchas）

1. **单文件 `--path` 是假绿高发区**：实测 `check_mermaid.py --path <单文件>` 返回「扫描文件: 0」且退出码 0，不代表图表合规；验证扫描类脚本一律用目录级实扫。
2. **Glob 花括号是语法幻觉**：Glob 工具不支持 `{a,b}`，返回 No file found 不代表文件不存在；拆成多个简单 pattern 或改用 LS。
3. **退出码 1 有两种身份**：Python 未捕获异常固定退出 1，恰好也是校验脚本最常用的契约检出码；判别方法见 bundled-script-exit-code-ambiguity，不能只看退出码。
4. **相对路径层级随文件深度变化**：`docs/tech/references/` 下的文件回仓根需要 `../../../`，少一级就是断链；修正后必须实跑链接门，不能肉眼推定。
5. **历史基线不是本次回归**：实扫出现的 14 个 `<br/>` 错误登记在 `mermaid-baseline.json`，先比对基线清单再归因，禁止把存量债务记到自己的修复头上。
6. **并发会话会移动 HEAD 与登记面**：编辑登记文件前重读磁盘现盘，CHANGELOG 取号必须实跑 `grep -m1 '^- \*\*v'`，不能凭记忆编号。
7. **只读继任者只能委托**：submodule 里的权威工具再合适也不能就地改，主仓侧建 shim 转发是唯一合规路径。
8. **py_compile 通过 ≠ 行为正确**：它只覆盖语法层；退役守卫的 exit 2、夹具统计 4/4 这类行为契约只能靠真实执行证明。

## 9. 与邻近技能的边界

- 对 **stale-read-edit-reconciliation**：它管「文件还在但内容被并发改写」，本技能管「目标已经消失」；信号是 Test-Path 零命中时归本技能。
- 对 **declared-consistency-fix**：它管许可证/版本号/分类等声明口径漂移，本技能只管路径引用失效；若一次修复中两者同时出现，路径部分按本技能、声明部分按它，分两个原子提交。
- 对 **link-check-cmd**：它是日常断链检测器，本技能是路径类检出后的修复规程；检测归它，修复归本技能。
- 对 **native-skill-surface-registration**：若失效路径位于 Skill 四个登记面，登记面的写入格式、计数与预览门以该技能为准。

## 10. Changelog

- **v1.0.0** (2026-11-16): 初始版本。萃取自同会话三个实战案例（frontmatter source 断链修复、check_mermaid.py 委托 shim、count_wikis.py 退役守卫），沉淀 F1~F4 四形态判型、S1~S5 五步法与 P1~P3 三处方。

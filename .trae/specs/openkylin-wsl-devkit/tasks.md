# openKylin WSL 开发工具包（openkylin-wsl-devkit）- 实施计划

> 任务为依赖有序的垂直切片；每个 Task 至少含一条 TR。代码根：`apps/dev-tools/openkylin-wsl-devkit/`；spec 根：`.trae/specs/openkylin-wsl-devkit/`。

## Task 1: 包骨架、pyproject 与 CLI 框架
- **Status**: `completed`
- **Completion Evidence**:
  - TR-1.1：`tests/test_distro.py` 12 用例全过（wsl_exe PATH 查找/WINDIR 回退/未找到、run_wsl 成功注入 WSL_UTF8/distro_missing/failed/command_missing/timeout 五态归一）。`tests/test_cli.py` 版本与 help 快照（--version/无命令/未知命令/全子命令 --help/exec REMAINDER 语义）全过。
  - TR-1.2：`python -m build --wheel` 产出 `openkylin_wsl_devkit-0.1.0-py3-none-any.whl`（wheel 内含 okw 六模块 + entry_points.txt 注册 `okw`）；`okw --version` 输出 `okw 0.1.0`。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 按仓库约定建 scikit-build-core 纯 Python 包：`pyproject.toml`（`requires=["scikit-build-core>=0.9"]`、build-backend、`[tool.scikit-build]` 的 `wheel.packages=["src/okw"]`、`wheel.cmake=false`（纯 Python 免 CMake）、`build-dir="build/{wheel_tag}"`、`minimum-version="0.9"`）；`[project.scripts] okw = "okw.cli:main"`；包目录 `src/okw/`（`__init__.py` 含 `__version__`、`__main__.py`）、tests/、README.md。
  - `cli.py`：argparse 根解析器与全部子命令注册（list/status/import/export/unregister/exec/verify/scaffold/ref）。
  - `distro.py` 基础：`wsl_exe()` 全路径解析（PATH 优先，回退 `$env:WINDIR\System32\wsl.exe`）；`run_wsl(args)` 统一调用封装（注入 `WSL_UTF8=1`，非零退出码归一为受控 `CmdResult`，区分 command_missing/distro_missing/failed/timeout/ok）。
- **Acceptance Criteria Addressed**: AC-1, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-1.1: mock subprocess 表驱动：命令数组正确、WSL_UTF8 注入、PATH 裁剪回退、四类结果区分；pytest 全通过。
  - `rule` TR-1.2: `python -m build` 产出 wheel 且 `okw` console 脚本注册正确；`python -m okw --version` 输出版本；未知子命令退出码 2 中文提示。

## Task 2: 发行版管理（list/status/import/export/unregister/exec）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-2.1：`parse_list_output` 三形态（表头表格/无表头短形态/旧列表形态）快照解析正确，格式漂移 fail-fast；`okw list` 真实运行输出本机 2 个发行版并标注默认星标。
  - TR-2.2：import 命令构造断言（`--import <name> <location> <image> --version 2`）；真实 gzip 头 `1F 8B` 校验通过、非 gzip 拒绝；unregister 无 `--yes` 拒绝且零 wsl 调用；exec 参数透传（剥离 `--` 分隔符）。
  - TR-2.3：verify 默认星标保护快照对比（调用前后 `wsl --list --quiet` 首行一致）。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `distro.py` 完整实现：`list_distros()`（wsl -l -v 解析、格式漂移 fail-fast）、`status(name)`、`import_distro(image, name, location, version=2)`（gzip 头字节校验 + 知识库 §4 排障提示）、`export_distro(name, output)`、`unregister_distro(name)`（需 `--yes`）、`exec_distro(name, cmd)`（参数透传 + 发行版预检）。
  - `cli.py` 装配六个子命令；import 失败时输出排障三问中文提示（位置漂移→查内存→`wsl --shutdown` 重试→解压纯 tar）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-2.1: 构造的 `wsl -l -v` 快照（多发行版/默认星标/WSL2+WSL1 混合）解析断言正确；不存在的发行版中文错误退出码 1。
  - `rule` TR-2.2: import 命令数组断言；真实 gzip 头通过、非 gzip 拒绝；unregister 无 `--yes` 拒绝。
  - `rule` TR-2.3: 本工具所有命令执行前后默认发行版快照对比不变。

## Task 3: 五步环境验收 verify
- **Status**: `completed`
- **Completion Evidence**:
  - TR-3.1：`tests/test_verify.py` 7 用例全过（全 PASS 五步/missing systemd 不中断/user UID 不匹配/包数异常/distro 不在列单 FAIL/默认星标变化 FAIL/format_report 渲染）。
  - TR-3.2：真实冒烟（只读）：`okw verify openKylin-3.0` 输出"发行版不存在"（本机当前无该发行版，AC-10 约定 blocked 收口，不伪造）；`okw verify podman-machine-default` 输出合法 PASS/FAIL 清单（WSL2 在列 PASS、os-release 非 openkylin FAIL、命令超时受控归一），无未捕获异常。
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `verify.py`：五步验收（① wsl -l -v 在列且 WSL2 + 默认星标对比；② /etc/os-release ID/VERSION；③ 默认用户/UID（openkylin/1000 对照）；④ /etc/wsl.conf 的 [boot] systemd=true 与 [user] default=；⑤ dpkg-query -W | wc -l 包数对照 405）；单项失败不中断，PASS/FAIL 清单输出，全 PASS 退出 0。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-3.1: mock 五命令输出表驱动：正常/缺失 systemd 配置/包数异常/发行版不存在 四场景的 PASS/FAIL 清单与退出码断言。
  - `rule` TR-3.2: 真实发行版冒烟（只读）输出合法；发行版不存在时登记 blocked 不伪造。

## Task 4: 开发脚手架（scaffold deb + scaffold dput）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-4.1：`tests/test_scaffold.py` 12 用例全过；六系列参数化（yangtze/1.0、nile/2.0、huanghe/3.0）生成五文件（control/changelog/rules/compat/format）断言正确；未知系列/空项目受控错误。
  - TR-4.2：dput 配置字段断言（[okbs] fqdn=upload.build.openkylin.top:2121 / method=sftp / incoming=%(okbs)s / login）；默认不写文件（打印片段）、--output 写入正确；真实执行 `okw scaffold deb/dput` 均成功。
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - `scaffold.py`：`scaffold_deb(project, series, version, target_dir)`（control/changelog/rules/compat=12/source/format=3.0 (quilt)，系列代号映射 1.0=yangtze/2.0=nile/3.0=huanghe）；`scaffold_dput(openkylin_id, output)`（OKBS 配置片段，默认打印、--output 写文件）。
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 临时目录生成 deb 骨架逐项断言；三代号参数化表驱动。
  - `rule` TR-4.2: dput 配置片段字段断言；输出路径默认与指定均正确。

## Task 5: 知识库参考 ref
- **Status**: `completed`
- **Completion Evidence**:
  - TR-5.1：`tests/test_ref.py` 7 用例全过（四主题内容字段断言、list_topics 覆盖、未知主题 None、相对路径存在性——8 条路径全部真实存在于仓库）。
  - TR-5.2：`okw ref` 无参数列出全部主题；`okw ref series` 真实输出版本代号速查；未知主题退出码 2。
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - `ref.py`：四主题速查（series 版本代号/wsl-troubleshoot 排障三问+稀疏 VHD+弱口令/okbs 五步流程+paramiko 前置/verify 五步口径），每条附知识库相对路径。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-5.1: 四主题输出内容与知识库事实一致；相对路径在仓库内真实存在。
  - `rule` TR-5.2: `okw ref` 无参数列出全部主题；未知主题中文提示退出码 2。

## Task 6: CLI 装配收尾与错误处理统一
- **Status**: `completed`
- **Completion Evidence**:
  - TR-6.1：`tests/test_cli.py` 34 用例全过（全子命令 --help/未知命令 2/版本/list/status/import 成功与坏魔数与失败排障提示/unregister 二次确认/exec 透传/verify 通过与失败退出码/scaffold deb 与 dput/ref）。
  - TR-6.2：`okw --version` 输出与 `__version__` 一致（okw 0.1.0）。
- **Priority**: medium
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 统一 CLI 行为：全部子命令 --help 完整；未知子命令/参数中文提示退出码 2；WslError/ScaffoldError 归一为中文可操作提示；`--version` 输出版本；console 脚本 `okw` 与 `python -m okw` 等价。
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-6.1: 全子命令 `--help` 快照测试；未知命令退出码 2 与中文提示断言。
  - `rule` TR-6.2: `okw --version` 与 `__version__` 一致。

## Task 7: 测试完备、覆盖率与静态卫生
- **Status**: `completed`
- **Completion Evidence**:
  - TR-7.1：`pytest` 96 用例全过（原 82 + 守护测试 14 参数化）；整体覆盖率 92%（distro 97% / verify 95% / scaffold 100% / ref 100% / cli 86%），关键模块（distro/verify/scaffold）均 ≥90%。
  - TR-7.2：`python -m build --wheel` 成功产出 wheel；`git status --porcelain --untracked-files=all` 仅应用目录与 spec 目录新文件（工具零运行时写入）。
  - 治理闭环（用户 2026-09-30 指令）：全仓扫描确认本应用无 `from __future__ import annotations` 真实 AST 节点；新增 `tests/test_no_future_annotations.py` AST 守护测试（14 参数化用例），负向验证真实拦截（临时加入该导入 → 1 failed）；全局红线已固化至 `.agents/rules/ai-coding-guidelines.md`（技术红线章节）与根 `AGENTS.md`（开发规范 Python 红线条款）。
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 完整测试套件：`tests/conftest.py`（假 wsl fixture：mock `_run_subprocess` 返回 CompletedProcess 形状 / mock `run_wsl` 按子串分支）、test_distro/test_verify/test_scaffold/test_ref/test_cli + test_no_future_annotations（AST 守护）。
  - `pytest --cov` 配置：整体 ≥80%、关键模块 ≥90%。
  - 仓库卫生：工具零运行时写文件（除 scaffold 显式目标外无写入路径）；wheel 构建成功。
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-7.1: 全测试通过；覆盖率整体 ≥80%、distro/verify/scaffold ≥90%。
  - `rule` TR-7.2: wheel 构建成功、包可导入、`okw` script 注册；`git status --porcelain` 无应用目录与 spec 目录外新增。

## Task 8: 真实冒烟、README 与 apps 区域登记
- **Status**: `completed`
- **Completion Evidence**:
  - TR-8.1：`apps/dev-tools/openkylin-wsl-devkit/README.md` 完整（定位/安装/全子命令用法/知识库映射/安全边界/已知边界）；`okw --help` 与 README 命令逐项核对一致；apps 登记完成：`apps/AGENTS.md` 应用路由表 + 边界声明各加一行（dev-tools 分组）、`apps/README.md` dev-tools 清单补 openkylin-wsl-devkit（计数 5→6）；不新建独立 AGENTS.md（遵循根规范）。
  - TR-8.2 自评 **3/5**（AC-10 维度）：真实冒烟 `okw list` 全 PASS（本机 2 发行版 + 默认星标）；`okw verify podman-machine-default` 输出合法 PASS/FAIL 清单（WSL2 在列 PASS，非 openkylin 项 FAIL 属正确行为）；`okw verify openKylin-3.0` 报告"发行版不存在"——知识库 S32 记录的 openKylin-3.0 发行版当前不在本机 WSL 在列（已被移除/未注册），按 spec AC-10 约定以 AC-2~AC-9 完整 mock 证据收口，未伪造真实 verify 全 PASS；评分依据：真实环境不可用（发行版缺失）非工具缺陷，AC-2~AC-9 证据完整（96 测试、wheel 构建、真实 list 冒烟）。
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 真实冒烟：本机发行版上执行 `okw list` 与 `okw verify <name>`（只读），记录输出；发行版缺失登记 blocked 不伪造。
  - README.md 完整化；apps/AGENTS.md 应用路由表与边界声明各加一行（dev-tools 分组）；apps/README.md dev-tools 清单补登记（计数 5→6）。
- **Acceptance Criteria Addressed**: AC-10, AC-9（收尾）
- **Test Requirements**:
  - `rule` TR-8.1: README 中命令与实际 CLI help 一致（人工核对）；路由表条目相对路径有效。
  - `rubric` TR-8.2: 真实发行版冒烟评分（AC-10 同维）；scale 1-5；threshold >= 3；evidence = list/verify 真实输出记录。

# Tasks：jupyter-podman-rootless 嵌入 containers 上游工具

> 前置约束：三个上游 commit 已核实固定（podman-compose `e3df1047` / podman-py `5dd81b49` / toolbox `81401f64`，以现 `external/dao/action/Containers/` untracked 快照为 pin 依据）。Task 1 在 `vendor/` 注册后，构建/文档统一以 `vendor/<name>` 为唯一使用入口；`external/` 快照不删除、不纳入版本控制。所有代码/规则改动遵循应用 `.agents/rules/` 与父级 SpecWeave/vendor 规范；里程碑完成后按原子提交规则入库。

## [x] Task 1: 在 vendor/ 注册三个 containers 上游仓库为 git submodule（third_party）
- Priority: high | Depends On: None
- Description:
  - 核对现快照 HEAD 与 spec 固定 commit 一致（`git -C external/dao/action/Containers/<name> rev-parse HEAD`），作为 pin 依据。
  - 逐个注册：在 SpecWeave 根 `git submodule add git@github.com:containers/<name>.git vendor/<name>`；随后 `git -C vendor/<name> checkout <固定commit>` 完成 pin（若 add 因目录已存在失败，采用"临时移出→add 克隆→checkout pin commit→与快照内容一致性核对"方案；注册成功后可 `git submodule absorbgitdirs` 规范 .git 存放）。
  - 更新 `vendor/AGENTS.md`：子模块路由表与边界声明新增 podman-compose / podman-py / toolbox 三个 `third_party` 条目（说明：containers 官方容器编排工具链，只读依赖）。
  - 运行 `python .agents/scripts/check-vendor.py` 再生成 `vendor/README.md` / `vendor/VERSION.md`；确认三子模块已登记、无孤儿目录。
  - 验证：`git submodule status` 三行均以 40 位 commit 开头且等于固定值；`git status --short` 无泄漏；`external/dao/action/Containers/` 下历史 untracked 快照无任何条目进入版本控制。
- Acceptance：ADDED「在 vendor/ 注册 containers 上游三仓库为 git submodule（third_party）」两 Scenario。
- 里程碑：原子提交 1（仅仓库层 vendor 注册与登记，不含应用改动）。

## [x] Task 2: 构建上下文 stage 机制 + 忽略规则
- Priority: high | Depends On: Task 1
- Description:
  - 新增 python helper（放 `src/jpman_builder/tasks/utils.py` 或独立 `stage_upstream.py`）：从 SpecWeave root（向上探测最近的 `.git`/`.gitmodules`）解析三个 `vendor/<name>` submodule 路径 → 复制到 `<project_root>/upstream/<name>`（跳过 `.git`；先全量复制，按需再精简）；submodule 目录缺失/为空（未初始化）时抛友好错误并给出 `git submodule update --init vendor/<name>`。
  - 在 `bin/jpman` 增加 bash 等价 stage 逻辑并接入 build/rebuild/rebuild-all 前置步骤；`src/jpman_builder/tasks/build.py` 的 CLI 与 podman-compose 后端路径同样接入（幂等，重复执行不报错）。
  - `.gitignore`（应用）：追加 `upstream/`。
  - `.containerignore`：确保 `upstream/` 不被排除；为 `*.md` 黑名单增加 `!upstream/podman-compose/README.md`、`!upstream/podman-py/README.md` 反白（setuptools readme 依赖）；确认 `upstream/*/.git` 等被过滤。
  - 验证：手动执行一次 stage，比对三个 `upstream/<name>` 目录内容与 `vendor/<name>` 一致且不含 `.git`；context 中 README.md 存在。
- Acceptance：ADDED「构建链路自动 stage 上游源树」两 Scenario（缺失报错可在未 init 状态演练验证）。
- 里程碑：原子提交 2（stage 机制，可与 Task 3 拆开提交，便于独立回滚）。

## [x] Task 3: Containerfile 嵌入三个工具
- Priority: high | Depends On: Task 2
- Description:
  - 新增 `toolbox-builder` Go 阶段（`FROM golang:<pin> AS toolbox-builder`，建议 pin 与 vendor/toolbox 的 go.mod 匹配的稳定版）：`COPY upstream/toolbox/src ./` → `ARG GO_PROXY`（默认 `https://proxy.golang.org,direct`）→ `go build -o /out/toolbox .`；若上游要求（go-build-wrapper/meson 元数据）则退化为在 builder 内按官方方式产出二进制。
  - conda-builder 阶段：`COPY upstream/podman-py ./podman-py`、`COPY upstream/podman-compose ./podman-compose`；在 main 环境创建后 `pip install --no-cache-dir ./podman-py ./podman-compose`（如遇 cp314t 无 wheel 的运行时依赖 sdist 编译失败 → 降级：先 `mamba install -n main -c conda-forge` 安装其运行时依赖，再 `pip install --no-deps ./...`）；安装后 `rm -rf` 源树目录并清理 pip 缓存。
  - final 阶段：`COPY --from=toolbox-builder /out/toolbox /usr/local/bin/toolbox`；`chmod 755`，确认 devuser PATH 含 `/usr/local/bin`。
  - Layer 6 VALIDATE 清单 15→18 项：新增 `podman-compose --version`、`python -c "import podman"`、`toolbox --help` 三检查（含版本回显日志）。
  - 遵循 containerfile.md 规范：分段 `RUN &&`、每段 `[INFO]/[OK]` 日志与 `[TIMER]`、构建参数经 ARG、体积清理（toolbox builder 工具链不进 final）。
  - 验证：`bash -n`/语法自检；真实 `podman build` 通过（若本机 WSL/Podman 可用）并打印体积变化；不可构建时交由 Task 5 用户侧验证。
- Acceptance：ADDED「镜像内嵌 podman-compose 与 podman-py」「镜像内嵌 toolbox 二进制」两 Scenario（容器内验证）。
- 里程碑：原子提交 3（镜像变更；确保 stage 逻辑已先合入，层缓存策略不受影响）。

## [x] Task 4: 规则与文档同步
- Priority: medium | Depends On: Task 3
- Description:
  - `.agents/rules/containerfile.md`：层架构新增 toolbox-builder 阶段说明、python 工具安装位置（conda-builder 内本地源，来源 vendor/）、VALIDATE 15→18 项、层变化频率标注。
  - `.agents/rules/build-test.md`：前置条件加 `git submodule update --init vendor/<name>` 检查；验证流程加三个内嵌工具检查项。
  - `.agents/CHANGELOG.md`：追加 feat 条目（记录 commit、日期、镜像内嵌三工具 + stage 机制 + vendor 注册）。
  - 人类文档：新增 `docs/17-upstream-tools.md`（三上游来源 vendor/ third_party、固定 commit、升级流程、容器内用法、与宿主侧 pip 的关系）；更新 `docs/README.md`（索引与文档数）、`docs/04-image-architecture.md`（层架构图/说明）、`docs/08-directory-structure.md`（`upstream/` 临时目录与 vendor/ 来源说明）；`AGENTS.md`、`.agents/README.md` 描述性文字同步（如有工具清单表述）。
  - 验证：`python <SpecWeave>/.agents/scripts/check-links.py --path docs` 断链检查通过；术语自查无"podman-compose 仅宿主机"等过期表述。
- Acceptance：ADDED「规则与文档同步」Scenario。
- 里程碑：原子提交 4（文档）。

## [x] Task 5: 端到端验证与收尾
- Priority: medium | Depends On: Task 4
- Description:
  - 若 WSL/Podman 可用：真实构建（可走 `.image-cache/` 缓存或 TUNA 镜像源）并执行 7 步验证 + 三个内嵌工具容器内验证；记录镜像体积增量与耗时。
  - `toolbox create/enter` DinP 冒烟：作为 runtime-conditional 验证记录结果（WSL2 用户命名空间限制下失败不阻塞验收）。
  - 汇总核验 checklist.md 全部勾选项；有失败项则回写本文件新增修复任务再验证。
- Acceptance：checklist.md 全部通过。
- 里程碑：如有文档/代码修正随修复原子提交。

## Task Dependencies
- Task 2 依赖 Task 1（vendor/ 子模块存在才能 stage）
- Task 3 依赖 Task 2（Containerfile COPY 依赖 stage 产物进 context）
- Task 4 依赖 Task 3（文档须描述真实实现的层架构/命令）
- Task 5 依赖 Task 4（全量收尾验证）
- Task 1 可独立先行；Task 2 内 python helper 与 bash（jpman）实现彼此独立，可在同一任务内并行；Task 4 中各文档可并行起草。

## 并行性提示
- Task 2 的 python helper 与 bash（jpman）实现各自独立可并行；Task 4 各文档并行起草后统一核链接。

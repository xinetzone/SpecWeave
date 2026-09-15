# client overlay 新栈交付检查清单（Delivery Checklist）

> 配合 [../SKILL.md](../SKILL.md) 使用。每建一个新叠加栈逐项打勾；
> 复杂/高影响栈（形态 B、跨外部仓库、重型构建）必须走 Spec Mode，
> 本清单即其 AC 的最小集来源。

## 0. 立项

- [ ] 决策树确认不能用根 `invoke run` / 扩现有栈解决
- [ ] 形态判定（A 运行时依赖 / B 工具链挂载）与参考实现选定
- [ ] 命名冻结：`<STACK>` / `<NS>` / 镜像 / 服务 / env 前缀 / 端口（与在运行栈错开）

## 1. 静态门禁（本机/WSL，秒级，必须全过）

- [ ] 新增/修改 Python：`python -m py_compile ...` 退出 0
- [ ] 新增/修改 shell：`bash -n <f>` 全过（PowerShell 调 wsl 用全路径，避免 `$var` 被吞）
- [ ] 功能性文件禁项 grep 0 命中（README 事实表述除外）：
      `external/chaos/ai`、`--mount=type=bind`、`CHAOS_ROOT`、`/builder/`、
      `import podman`、`--privileged`、`SHELL [`、`HEALTHCHECK`
- [ ] 模板占位符清零：grep `__STACK__|__NS__|__NSU__|__SVC__|__ENV_PREFIX__|__IMAGE__|__SSH_PORT__|__JUPYTER_PORT__|__CONTAINERFILE__` 仅剩注释说明（如技能模板自身），成品无残留
- [ ] **测试黄金表已扩且全绿**：client 目录 `pytest tests/test_overlay_core.py tests/test_tasks_surface.py tests/test_compose_merge.py`（新栈进入任务集/签名/docstring 断言与 GOLDEN 表）
- [ ] `podman-compose -f <abs>/compose.yaml config` 退出 0，断言：
      1 服务、extends 可解析、image+build、端口、bind 数（长语法+create_host_path）、
      named volume（如有）、三必需/凭证四变量/bridge 来自 rootless-base 基段（栈文件未重复）、
      无 privileged/healthcheck/command
- [ ] `invoke --list`（PYTHONPATH=src 或已 pip install -e .）含全部 `<ns>.*` 任务
      （六任务经 `for _t in <ns>.TASKS.items()` 注册；长任务单独 add_task）
- [ ] Windows 原生 `invoke <ns>.ps` 实测：WSL 桥接成功 Exit 0，或不可桥接时 Exit 1 + 双路径中文指引；bridge_env_keys 与 .env 对齐
- [ ] 键集合三方 diff 为空：compose `${VAR}` ≡ overlay .env.example ≡ root .env.example 段；桥接键 ≡ StackSpec.bridge_env_keys
- [ ] 新增/修改 md 相对链接全部可达，无 file:/// 绝对链接

## 2. 真实镜像构建（WSL2 machine，禁止以静态检查替代）

- [ ] 基底镜像存在（`podman image exists localhost/jupyter-podman-rootless:latest`）
- [ ] `podman build` 或 `invoke <ns>.build` 退出 0（记录镜像源与关键版本）
- [ ] 镜像 inspect：Entrypoint=[tini -- entrypoint.sh]、Cmd 空、无 Healthcheck
- [ ] 构建期守卫 root + devuser 双身份 PASS
- [ ] 镜像内无错误版本 `*.pyc`/`__pycache__`/`*.bak_*`（.dockerignore `**/` 模式 + 末层清理）
- [ ] 镜像不含构建中间产物与宿主源码（构建上下文=栈目录）

## 3. E2E（栈运行态）

- [ ] `up -d` 容器 Up；SSH 端口 banner、Jupyter /lab 返回 200/302
- [ ] bind 挂载点在容器内可见；形态 B：关键文件/源码 import 路径前缀断言通过
- [ ] 内核（如有）：argv/解释器/环境正确，root 与 devuser 双可见
- [ ] 全部冒烟脚本 PASS（固定输入断言，非“导入成功即通过”）
- [ ] 形态 B 长任务（编译/打包等）真实跑通一次，产物落宿主可见 bind 目录
- [ ] 外部只读源码树前后 hash/状态快照一致，无临时注入残留
- [ ] `down` 后项目容器/网络清零，bind 保留，volume 语义正确（默认保留 / --volumes 删）
- [ ] 第二轮 up→smoke→down 幂等

## 4. 接线登记（7 点，见 SKILL.md §9）

- [ ] tasks/__init__.py：import 新栈模块、Collection + for 循环注册 TASKS、长任务单独 add_task、configure 段、docstring
- [ ] root client .env.example 新段（与 overlay .env.example、bridge_env_keys 双向对齐）
- [ ] client tests 两张黄金表（test_tasks_surface.py / test_compose_merge.py）
- [ ] 文档锚点：client README.md 小节、docs/1x 新栈文档 + docs/README 索引、overlay README
- [ ] client AGENTS.md（6 处）+ .agents/README.md（4 处）+ apps/AGENTS.md（路由表+边界表）
- [ ] .agents/rules/<ns>-overlay.md + P0 C# 约束（含 extends 基段/内核零栈知识红线）
- [ ] pyproject 不改（[compose] extra 与 jpman-common 依赖已存在）

## 5. 收口

- [ ] 改动全部落在白名单；既有 overlay（onnx/xmnn/monetize）与三栈 SPEC/TASKS 零回归
- [ ] 复杂栈完成 fresh-context 独立 Review（rule+rubric），actionable 清零
- [ ] 产物版本/镜像 ID/关键命令输出归档到 spec 或任务证据
- [ ] 未授权不执行 git commit（用户明示后按 atomic-commit-cmd 提交）

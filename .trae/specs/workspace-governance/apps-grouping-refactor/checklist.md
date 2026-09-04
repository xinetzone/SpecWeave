# Checklist

## 目录分组

- [x] `apps/` 一级目录 = {AGENTS.md, README.md, .agents/, shared/, tests/, docker-images/, ai-agents/, dev-tools/, samples/}
- [x] `docker-images/` 含 7 个应用：devcontainer-base, docker-ssh-dind, jupyter-ssh-base, pytorch-base, caffe-ffi-jupyter, caffe-ffi-cross, xmnn-runtime
- [x] `ai-agents/` 含 3 个应用：ai-code-assistant, eve-minimal-agent, zhujian-wudao
- [x] `dev-tools/` 含 2 个应用：camera-power-controller, prompt_extraction
- [x] `samples/` 含 3 个应用：cow-demo, short-video-site, zleap-workspace-first-prototype
- [x] 所有应用目录名保持不变（未重命名）
- [x] 所有移动均通过 git 追踪（507 个 rename，历史可追溯）

## 引用更新

- [x] `apps/AGENTS.md` 路由表/边界声明/嵌套树/流程图路径已更新为分组路径
- [x] `apps/README.md` 应用清单已按分组组织，链接可解析
- [x] `apps/.agents/README.md` 目录结构示意已更新
- [x] 各应用内部 AGENTS.md 中 `apps/<app>/` 路由层级示意已更新
- [x] 根 `.agents/`（context-routing、code-wiki、docker-cache、checklists、capability-registry 等）旧路径引用已更新
- [x] 应用内部 docs/scripts 中的 `apps/<app>/` 与 `/SpecWeave/apps/...` 绝对路径已更新
- [x] 补充：`.github/workflows/` 3 个 CI 文件路径过滤器与 working-directory 已更新；zhujian-wudao 3 个 x-toml-ref 相对深度已校正
- [x] `.trae/specs/` 历史快照未被追改

## 功能等价性

- [x] prompt_extraction pytest 测试通过（301 passed，`python -m pytest apps/dev-tools/prompt_extraction/tests`）
- [x] Dockerfile 跨应用依赖（BASE_IMAGE 镜像标签引用）不受目录移动影响
- [x] 活跃文档中无 `apps/<app>/` 旧路径残留（apps/、根 .agents/、.github/ 均清理，仅剩历史 spec/.meta/子模块与 d:/AI 外部路径）
- [x] git 状态干净：0 未跟踪、无丢失文件，所有移动被追踪（507 rename / 80 M / 5 A / 2 D 均为良性）

## 方法论质量门

- [x] G1：事实采集（I 前）无因果推断，基于实际目录/引用扫描
- [x] G2：洞察完整（现象+根因+影响+建议）
- [x] G3（可跳过）：本场景不涉及模式入库，E 阶段非必需
- [x] G4：任务原子化——目录移动与引用更新职责分离
- [x] V：重构等价性验证已执行（功能不变 + 依赖完整 + 无断链）

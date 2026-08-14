# Tasks

> 方法论：场景3 重构优化（I→F→A→V→C）。任务按「目录移动（原子单元）→ 引用更新 → 验证」拆分，每个分组一次 `git mv` 保持历史可追溯。

## 分组目录移动（A 阶段）

- [x] Task 1: 创建 4 个分组目录并移动 `docker-images/` 组（7 个应用）
  - [x] `git mv` 移动 devcontainer-base、docker-ssh-dind、jupyter-ssh-base、pytorch-base、caffe-ffi-jupyter、caffe-ffi-cross、xmnn-runtime → `apps/docker-images/`
  - [x] 验证 `apps/docker-images/` 下 7 个应用齐全，apps/ 根下不再残留

- [x] Task 2: 移动 `ai-agents/` 组（3 个应用）
  - [x] `git mv` 移动 ai-code-assistant、eve-minimal-agent、zhujian-wudao → `apps/ai-agents/`
  - [x] 验证 `apps/ai-agents/` 下 3 个应用齐全

- [x] Task 3: 移动 `dev-tools/` 组（2 个应用）
  - [x] `git mv` 移动 camera-power-controller、prompt_extraction → `apps/dev-tools/`
  - [x] 验证 `apps/dev-tools/` 下 2 个应用齐全

- [x] Task 4: 移动 `samples/` 组（3 个应用）
  - [x] `git mv` 移动 cow-demo、short-video-site、zleap-workspace-first-prototype → `apps/samples/`
  - [x] 验证 `apps/samples/` 下 3 个应用齐全

## 活跃引用更新（依赖正确性）

- [x] Task 5: 更新 `apps/` 根级索引文件
  - [x] `apps/AGENTS.md`：应用路由表、边界声明、嵌套优先级树、流程图中所有 `apps/<app>/` → `apps/<group>/<app>/`
  - [x] `apps/README.md`：应用清单按分组小节组织，链接更新为分组路径
  - [x] `apps/.agents/README.md`：目录结构示意更新为分组结构

- [x] Task 6: 更新各应用内部 AGENTS.md 与文档/脚本中的路径引用
  - [x] 应用内部 AGENTS.md（devcontainer-base/docker-ssh-dind 等路由层级示意）
  - [x] 应用内部 docs 与 scripts 中的 `apps/<app>/` 与 `/SpecWeave/apps/...` 引用（如 caffe-ffi-jupyter/WSL-DEPLOY-GUIDE.md、scripts/*.sh、zleap docs/*.md、devcontainer-base/variants/scripts/*.sh）
  - [x] 补充修复：zhujian-wudao/.agents 3 个 x-toml-ref 相对深度（+1 层 `../`），apps/.agents/README.md 残留行

- [x] Task 7: 更新根 `.agents/` 下的活跃引用
  - [x] `.agents/context-routing.md`（apps/prompt_extraction 等）
  - [x] `.agents/docs/code-wiki/*.md`（prompt_extraction 大量引用）
  - [x] `.agents/docs/tools/docker-cache.md`（devcontainer-base 引用）
  - [x] `.agents/checklists/conda-build-best-practices.md`（caffe-ffi-jupyter 引用）
  - [x] `.agents/capability-registry/*.md`、`.agents/docs/reuse-and-generalization.md` 等其余引用
  - [x] 补充修复：`.github/workflows/` 3 个 CI 文件（devcontainer-variants.yml / onnx-quantize-ci.yml / jupyter-ssh-base-ci.yml）路径过滤器与 working-directory

## 全量验证（V 阶段等价性验证 + G 质量门）

- [x] Task 8: 全量验证重构正确性
  - [x] 路径一致性检查：apps/ 下一级目录 = {AGENTS.md, README.md, .agents/, shared/, tests/, docker-images/, ai-agents/, dev-tools/, samples/}；4 组共 15 个应用无遗漏（spec 中"17"为高估，实际 15，全部就位）
  - [x] 链接检查：活跃文档中无 `apps/<app>/` 旧路径残留（apps/、根 .agents/、.github/ 均已清理，仅剩历史 spec/.meta/子模块与 d:/AI 外部路径）
  - [x] 功能等价验证：prompt_extraction pytest 301 passed；Dockerfile 跨应用依赖（BASE_IMAGE=jupyter-ssh-base:1.3 等镜像标签）不受目录移动影响；zhujian-wudao x-toml-ref 相对路径已校正
  - [x] git 状态检查：git add -A 后 507 个 rename（R100=461 + R89-99=46）、0 未跟踪、无丢失文件（2 个 D 为历史迁移遗留与 .gitkeep 配对歧义，均无实际丢失）

# Task Dependencies

- [Task 5] 依赖 [Task 1][Task 2][Task 3][Task 4]（索引更新需在目录移动完成后）
- [Task 6] 依赖 [Task 1]-[Task 4]（应用内引用随目录移动）
- [Task 7] 依赖 [Task 1]-[Task 4]
- [Task 8] 依赖 [Task 5][Task 6][Task 7]（验证在全部引用更新完成后执行）
- [Task 1]-[Task 4] 相互独立，可并行执行

# Tasks

- [x] Task 1: 单源版本化：将 xs-cli 版本改为从 `xs/__init__.py` 动态读取
  - [x] 1.1 修改 `tools/xs/pyproject.toml`：移除 `[project] version`，改为 `dynamic = ["version"]`，新增 `[tool.setuptools.dynamic] version = {attr = "xs.__version__"}`
  - [x] 1.2 更新 `xs version bump`（`version_cmd.py`），在更新 pyproject 版本时同步写入 `xs/__init__.py` 的 `__version__`
  - [x] 1.3 验证 `python -m build` 生成的 wheel 版本号等于 `xs.__version__`（另修复 discovery.py 读取 dynamic version，使 `proj.version` 正确解析）

- [x] Task 2: 补齐 xs-cli 打包元数据
  - [x] 2.1 将 `license = {text = "MIT"}` 改为 SPDX 形式 `license = "MIT"`
  - [x] 2.2 增加 `readme = "README.md"`、`keywords`、`classifiers`、`project.urls`（Homepage/Repository/Issues，指向 github.com/xinetzone/xuanspace）
  - [x] 2.3 移除 `[tool.pdm.build]` 段，统一 setuptools 构建
  - [x] 2.4 新建 `tools/xs/README.md`（含安装、使用、开发说明）

- [x] Task 3: 新增 GitHub Actions 发布工作流
  - [x] 3.1 编写 `.github/workflows/release.yml`：`on: push: tags: ["xs-cli-v*"]`，构建 sdist+wheel，`twine upload` 到 PyPI
  - [x] 3.2 使用 `PYPI_TOKEN` secret 上传 PyPI；预留 `PYPI_TEST_TOKEN` 的 TestPyPI dry-run 步骤

- [ ] Task 4: 本地构建、校验与安装验证
  - [ ] 4.1 在 `tools/xs/` 运行 `python -m build` 生成 sdist + wheel
  - [ ] 4.2 运行 `twine check dist/*` 校验元数据
  - [ ] 4.3 在干净 venv 中 `pip install dist/xs_cli*.whl` 并运行 `xs --version`、`xs --help` 验证 CLI 可用

- [ ] Task 5: TestPyPI dry-run 发布验证
  - [ ] 5.1 上传到 TestPyPI 并确认安装成功（可选，需凭据）

# Task Dependencies
- [Task 2] 依赖 [Task 1]（版本单源化先行，避免元数据与版本冲突）
- [Task 4] 依赖 [Task 1]、[Task 2]
- [Task 3] 可与 [Task 1]、[Task 2] 并行
- [Task 5] 依赖 [Task 4]
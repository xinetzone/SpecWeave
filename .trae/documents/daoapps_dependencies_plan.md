# 道用依赖配置迁移计划

## 调研结论

- 道用当前以 requirements.txt 管理 7 项站点依赖和 pytest。
- 玄境使用 pyproject.toml，按 docs、test、dev 等用途分组，同时提供 extras 和 dependency-groups。
- 道用的本地命令、GitHub Actions、RTD 和两项契约测试直接依赖 requirements.txt。
- 道用子项目工作树在调研时无变更；玄境仅作为只读参考。

## 推荐方案

采用玄境的依赖分组方式，不复制其发行包、monorepo 和原生构建配置。
道用仍是纯文档站，以 pyproject.toml 的标准 dependency-groups 为唯一依赖事实来源：

- docs：保留现有 7 项站点依赖及全部版本下限，包括中文搜索必需的 jieba。
- test：保留 pytest>=8.0。
- dev：通过 include-group 组合 docs 和 test，不重复依赖条目。

不新增可安装发行包、src/ 空包、构建后端、PDM workspace 或锁文件。
不照搬玄境 requires-python>=3.14.6；本次保持道用两条发布通道现有 Python 3.14 设置。

## 修改范围

仅在批准后进入 daoapps.github.io 子项目开发流程：

1. 新建 pyproject.toml，迁入依赖分组；移除 requirements.txt。
2. 修改 tests/test_site_contract.py：从 TOML 读取中文分词依赖，核验分组与发布入口；先运行新测试取得失败证据。
3. 修改 .github/workflows/pages.yml：使用 pip>=25.1 的 --group 安装依赖；gates 安装 docs+test，build 仅安装 docs；缓存依赖路径和 doctree 哈希改为 pyproject.toml。
4. 修改 .readthedocs.yml：在 build.jobs.pre_install 中升级 pip 并安装 docs 组，移除旧 requirements 安装项；保持源目录、语言守卫、警告即失败及 htmlzip 不变。
5. 同步 README.md、AGENTS.md 和 tests/visual_equivalence.py 的安装说明，消除旧入口引用。

本地统一入口示例：

```bash
python -m pip install "pip>=25.1"
python -m pip install --group dev
```

## 方法论与边界

- seven-concepts-cmd：轻量重构链路，事实对照、连接设计、影响面拆解、等价验证；Git 提交需另行明确授权。
- dao-san-triads：只读诊断阶段借用“先设计连接”原则，检查依赖声明如何供给三个执行入口；这是现代工程类比，不是经典文本推导。
- dao-san-triads 自身要求子模块零写入。本计划批准后，实际迁移转入道用子项目开发流程，不以该技能授权写入。
- 不修改玄境、站点内容、样式、主仓 gitlink；不提交或推送。

## 验证

1. 解析 pyproject.toml，机械核对原依赖及版本下限无丢失、dev 引用不重复。
2. 在隔离环境中实际安装 docs 和 test 分组，验证 pip --group 可用。
3. 运行全量 pytest tests -q。
4. 运行 Sphinx HTML 和 singlehtml 的 -W --keep-going 构建，检查退出码。
5. 检查工作流 YAML 和 RTD 安装入口；有 actionlint 时运行校验。
6. 扫描旧 requirements.txt 引用并检查 git diff --check。

## 风险

- pip 旧版不支持 --group：本地说明、CI 和 RTD 显式升级到 pip>=25.1。
- RTD 分组安装需要自定义 pre_install：本地验证同一安装命令，但平台真实构建仍须部署后验证，不声称已验证远端。
- 依赖解析可能选取更新版本：保留原下限；若出现 sphinx-design 版本变化，补跑既有视觉等价工具，失败则暂停并报告。
- 用户若希望完全采用玄境的可安装包和 extras，而非非发行式分组，需要调整方案后再次确认。

## 执行结果

- 用户已批准；依赖分组、CI、RTD、本地说明和契约测试均已迁移。
- 8 项原依赖及下限全部保留；requirements.txt 已移除。
- 新迁移测试在旧配置下取得 4 项预期失败；迁移后全量测试 52 passed。
- 同步移除修改文件中既有 future annotations，并添加 AST 守护测试。
- pip --group dev 在已有 py314 环境中离线 dry-run 成功；独立环境联网安装多次无输出并超时，未完成干净环境安装验收。
- HTML -W 构建存在 57 条警告；以 HEAD 的 git archive 同环境对照，基线也是 57 条，归一化后逐条差集为 0。
- singlehtml -W 构建存在 9 条未入目录树警告，涉及同一批既有 design 文档；未修改或抑制这些警告。
- 工作流和 RTD YAML 已解析验证；本机未发现 actionlint，未执行其专用校验。
- sphinx-design 仍为现有 0.7.0，未升级依赖、样式或 DOM；未触发视觉等价比对。
- 玄境工作树无变更；未提交、推送或更改主仓 gitlink。
- RTD 平台真实构建与干净 Linux 环境安装仍需后续验收，本次不声称通过。

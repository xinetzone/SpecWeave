# podman-compose 事实

F-001: 项目是Compose Spec的实现，使用Podman作为后端，聚焦于rootless和daemon-less进程模型。
F-002: 项目直接执行podman命令，无需运行守护进程。
F-003: 运行依赖：podman、Python 3.9或更新版本、PyYAML、python-dotenv；可选依赖podman dnsname插件（使用CNI网络时需要）。
F-004: 项目主体是单个Python文件脚本podman_compose.py，可直接放入PATH执行。
F-005: pyproject.toml中项目名称为podman-compose，Python入口点为podman-compose = "podman_compose:main"。
F-006: 项目license为GPL-2.0-only，作者为Muayyad Alsadi。
F-007: 版本1.x分支要求Podman版本>=3.4，0.1.x旧分支兼容Podman 3.1.0之前版本。
F-008: 项目提供bash补全脚本，位于completion/bash/podman-compose。
F-009: tests/目录下包含integration/集成测试目录，按功能划分子目录（abort、additional_contexts、build、compose_up_behavior、deps、env_file_tests等）。
F-010: examples/目录下提供多个示例compose文件（awx3、azure-vote、busybox、echo、hello-app、hello-python、nvidia-smi、wordpress等）。
F-011: docs/目录下包含版本变更日志（Changelog-1.1.0.md到Changelog-1.6.0.md）、Extensions.md、Mappings.md。
F-012: 项目使用towncrier生成变更日志，newsfragments/目录下存放变更片段（.bugfix、.feature、.change、.misc类型）。
F-013: 提供Dockerfile用于生成二进制文件，scripts/目录下包含download_and_build_podman-compose.sh、make_release.sh等脚本。
F-014: 支持通过pip安装（pip3 install podman-compose），也可通过apt、dnf、brew等包管理器安装。
F-015: 项目使用setuptools作为构建后端，配置了ruff（lint/format）、mypy（类型检查）工具。

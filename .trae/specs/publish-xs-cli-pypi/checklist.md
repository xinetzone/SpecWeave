# Checklist

- [ ] xs-cli 版本号为单源：pyproject 使用 `dynamic = ["version"]` 引用 `xs/__init__.py` 的 `__version__`
- [ ] `xs version bump` 同步更新 pyproject 与 `__init__.py` 的版本号
- [ ] xs-cli pyproject 元数据完整：SPDX license、readme、keywords、classifiers、project.urls
- [ ] `[tool.pdm.build]` 已移除，构建统一使用 setuptools backend
- [ ] `tools/xs/README.md` 存在且被 `readme` 字段正确引用
- [ ] `.github/workflows/release.yml` 存在，tag 触发构建并 twine 上传 PyPI
- [ ] `python -m build` 成功生成 sdist + wheel
- [ ] `twine check dist/*` 通过
- [ ] 干净 venv `pip install dist/*.whl` 后可运行 `xs --version`
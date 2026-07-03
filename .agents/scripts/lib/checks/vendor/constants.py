"""vendor 检查常量和模板定义模块。

必需文件配置、元数据字段要求、README/VERSION模板字符串。
"""

from __future__ import annotations

REQUIRED_ROOT_FILES = ["README.md", "VERSION.md"]
REQUIRED_LIB_FIELDS = ["名称", "版本", "来源", "引入日期", "用途", "许可证"]

VENDOR_README_TPL = """+++
# 此文件由 check-vendor 自动生成，请根据实际情况完善
+++

# Vendor 依赖总览

本目录存放项目引入的第三方依赖库。
- **git 子模块**：通过 `.gitmodules` 管理，会提交 gitlink 至版本控制
- **手动管理依赖**：通过 `.gitignore` 忽略（vendor/* 排除白名单），不提交源码

## 依赖清单

| 库名称 | 版本 | 引入日期 | 用途 |
|---|---|---|---|
{libs_table}

## 使用说明

1. 新增 git 子模块：`git submodule add <url> vendor/<name>`
2. 新增手动管理依赖：运行 `python .agents/scripts/repo-check.py vendor --fix` 创建标准模板
3. 手动管理依赖的每个子目录必须包含 `README.md` 元数据文件
4. 所有依赖版本需同步更新至 `VERSION.md`
5. 定期运行 `python .agents/scripts/repo-check.py vendor --scan-refs` 检查未使用依赖

## 管理规范

详见 [临时依赖管理流程](../.agents/protocols/dependency-management.md)
"""

VENDOR_VERSION_TPL = """+++
# 此文件由 check-vendor 自动生成，请根据实际情况完善
+++

# Vendor 依赖版本清单

| 库名称 | 版本号 | 来源地址 | 引入日期 | 许可证 | 类型 | 备注 |
|---|---|---|---|---|---|---|
{libs_table}

## 更新记录

- {date} | 初始化版本清单
"""

VENDOR_LIB_README_TPL = """+++
# 此文件由 check-vendor 自动生成，请根据实际情况完善
+++

# {lib_name}

## 基本信息

- **名称**：{lib_name}
- **版本**：请填写版本号
- **来源**：请填写 GitHub URL 或下载链接
- **引入日期**：{date}
- **用途**：请填写引入此库的原因和在项目中的作用
- **许可证**：请填写许可证类型（如 MIT、Apache-2.0 等）

## 修改记录

如对上游源码有修改，请在此记录：

| 修改日期 | 修改内容 | 修改原因 |
|---|---|---|
| 无 | - | - |

## 注意事项

- 请定期检查上游更新
- 如不再使用，请从 vendor/ 目录移除并更新 VERSION.md
"""

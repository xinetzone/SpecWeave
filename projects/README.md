# Projects — 第一方子项目目录

本目录存放 SpecWeave 的**第一方自有子项目**（git submodules），与 `vendor/`（第三方依赖子模块）形成明确区分。

## 目录约定

| 目录 | 用途 | 示例 |
|------|------|------|
| `projects/` | 第一方自有项目（本团队/个人开发维护） | xuanspace |
| `vendor/` | 第三方依赖（外部团队/开源项目，可能包含 patch） | flexloop, ark-cli |
| `external/` | 不被 git 跟踪的外部参考库与调试实验区 | chaos/caffe, ffi/tvm（本地克隆） |
| `apps/` | SpecWeave 主仓库内的应用 | ai-code-assistant, zhujian-wudao |

## 子模块管理

```bash
# 添加第一方子模块
git submodule add https://github.com/xinetzone/<repo>.git projects/<name>

# 更新子模块到最新版本
git submodule update --remote projects/<name>

# 初始化（clone 后）
git submodule update --init --recursive
```

## 现有子项目

| 项目 | 描述 | 仓库 |
|------|------|------|
| [xuanspace](xuanspace/) | Xuanspace（玄境）Python monorepo 项目管理工具 | https://github.com/xinetzone/xuanspace |

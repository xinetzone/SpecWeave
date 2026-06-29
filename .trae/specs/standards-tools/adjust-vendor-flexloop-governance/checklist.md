# flexloop 子模块治理模式调整 — Verification Checklist

## 配置层验证

- [x] `.gitmodules` 中 vendor/flexloop 条目包含 `branch = main` 配置
- [x] `git config -f .gitmodules submodule.vendor/flexloop.branch` 返回 `main`（通过 repo-check 分支跟踪检查间接验证）
- [x] 分支跟踪配置验证通过（repo-check 报告 "已配置 branch 跟踪"）

## 文档层验证

- [x] VENDOR-INTEGRATION.md 将 flexloop 标注为「自有协作子模块」
- [x] 三区域边界模型已更新
- [x] 「协作四原则」已定义
- [x] 禁止行为清单已更新
- [x] 子模块开发工作流章节完整
- [x] 条件导入章节包含 Python 代码示例
- [x] 沙箱运行规范章节包含使用示例
- [x] 版本控制策略更新为「跟踪 main 分支」
- [x] dependency-management.md 区分两种子模块模式
- [x] vendor/README.md 和 vendor/VERSION.md 已更新类型标注（owned_collab, main）
- [x] 所有修改的 Markdown 文件 Mermaid 图通过 check-mermaid.py 检查（0 错误 0 警告）

## 工具层验证

- [x] vendor.py 引入子模块类型概念（third_party / owned_collab）
- [x] 裸 `import vendor.xxx` 在 owned_collab 模式下报告为警告
- [x] try/except ImportError 包裹的条件导入不被标记为违规
- [x] 反向依赖检测使用 pathlib.resolve 精确判断
- [x] 分支跟踪检查通过 path 字段精确定位配置段
- [x] 子模块清洁检查区分本地提交（允许）和未提交修改（错误）
- [x] vendor_sandbox.py 模块创建，包含 run_flexloop_script()、FLEXLOOP_AVAILABLE、conditional_import()
- [x] FLEXLOOP_AVAILABLE 正确检测子模块初始化状态
- [x] conditional_import() 对不存在的模块返回 None
- [x] 所有现有 pytest 测试通过（34 passed）
- [x] check-vendor.py 包装器已更新为设置 PYTHONIOENCODING=utf-8（与 check-mermaid.py 一致）

## 功能层验证

- [x] repo-check.py vendor 非 deep 模式 exit code 0
- [x] flexloop 被正确识别为 owned_collab 类型
- [x] vendor_sandbox.py 路径计算正确（PROJECT_ROOT = D:\spaces\SpecWeave）
- [x] 条件导入优雅降级（nonexistent module 返回 None）

## 治理层验证

- [x] 两个项目独立性确认：flexloop 内 Python 代码无 sys.path 插入上级目录或超出边界的相对导入
- [x] 单向依赖确认：SpecWeave→flexloop 方向（通过条件导入和沙箱）
- [x] 测试隔离确认：pytest 已排除 vendor/ 目录
- [x] 元数据一致性：VERSION.md 中 flexloop 标注为 owned_collab 类型

## 已知预存问题（非本次引入）

- flexloop 子模块内 README.md 存在 CRLF 行尾符差异（Windows git autocrlf），导致 git status 显示 M 状态
- flexloop 内部文档（docs/topics/*.md）有 7 处 Markdown 链接指向其自身项目结构路径（apps/chaos/...），这些是 flexloop 仓库的历史文档链接，非 Python 代码依赖

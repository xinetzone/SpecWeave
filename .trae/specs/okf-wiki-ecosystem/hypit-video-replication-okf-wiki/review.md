---
status: "reviewed"
---

# Hypit OKF Wiki 审查记录

## G1 事实门

- [x] 事实与作者观点分层。
- [x] 数字、命令、版本和许可证均有来源。

## G3 模式门

- [x] 已提炼“语义锚定优于固定时间码”的可迁移模式。
- [x] 已记录反模式：把示例成本当普遍成本、把第三方模型能力归给 Hypit、跳过版权与服务凭证检查。

## V 对抗审查

- [x] 事实溯源视角
- [x] 结构规范视角
- [x] 读者可用性视角
- [x] 时效与成本边界视角

## 结论

双份 F 编号 24/24 一致，新增文档 UTF-8 通过。`check-toctrees.py` 仍被仓库既有缺失项 `jishu/tencent/tencent-buddy-family/index.md` 拦截；`check-bundles-index.py` 已因本次计数修正后待重跑确认。`invoke gates.*` 因环境缺少 `invocations` 包元数据未执行成功，未宣称 gates 通过。

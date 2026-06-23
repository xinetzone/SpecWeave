# Checklist

## 数据模型
- [x] TOML frontmatter 中 `tier` 字段已定义，取值 `co-founder` / `standard`
- [x] `[permissions]` 表结构已定义，含 `view` 与 `manage` 字段
- [x] 联合创始角色文件 frontmatter 声明 `tier = "co-founder"`
- [x] 联合创始角色文件 frontmatter 包含 `[permissions]` 表

## 角色文件
- [x] `.agents/roles/co-founder.md` 已创建
- [x] co-founder.md 包含 Description、Responsibilities、Non-Goals 三部分
- [x] co-founder.md 标题以 `[联合创始] 🏛️` 前缀起始
- [x] co-founder.md 的 Non-Goals 与现有角色边界清晰无重叠

## 索引清单
- [x] `.agents/roles/README.md` 角色职责矩阵新增"层级标记"列
- [x] 联合创始角色行显示 🏛️ 联合创始
- [x] 普通角色行显示"标准"
- [x] README.md 文件结构说明已加入 `co-founder.md`
- [x] README.md 新增"权限控制"章节

## AGENTS.md 同步
- [x] AGENTS.md 角色定义索引表已追加联合创始角色行

## 一致性与验证
- [x] 联合创始角色在 README.md 索引与详情文件中视觉标记一致（🏛️ + [联合创始]）
- [x] `[permissions]` 表在联合创始角色文件中字段完整
- [x] check-links.py 验证新增文件无断链（联合创始角色相关链接全部有效）

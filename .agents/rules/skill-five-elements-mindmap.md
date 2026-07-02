---
id: "skill-five-elements-mindmap"
title: "Skill 质量五要素模型 · 思维导图"
source: ".agents/rules/skill-development.md#3"
x-toml-ref: "../../.meta/toml/.agents/rules/skill-five-elements-mindmap.toml"
---
# Skill 质量五要素模型 · 思维导图

> 源文档：[skill-development.md](./skill-development.md) §3 质量五要素模型

```mermaid
mindmap
  root((<b>高质量 Skill</b><br/>五要素模型))
    1️⃣ Trigger-Ready<br/>Description<br/>触发就绪描述
      完整触发词列表
        同义词
        口语化表达
        相关操作词
        英文术语
      强制措辞
        "必须使用此技能"
        "Use this skill when..."
      说明核心优势
        比手动操作好在哪
        双方案各自亮点
      反模式
        只写"XX操作工具"
        过于简短导致undertrigger
      正例参考
        forum-posting v1.1.1
          发帖/编辑/回复/清理草稿
          + forum-bot脚本/操作forum.trae.cn
          + "必须使用此技能"
    2️⃣ Decision<br/>Tree<br/>方案决策树
      多方案必备
        不止简单罗列
        编码选型逻辑
      选择条件
        运行环境
          IDE内 → MCP
          命令行/CI → 脚本
        安全需求
          需要dry-run → 脚本
          即时交互 → MCP
        登录状态
          未登录 → 先脚本login持久化
      默认推荐方案
        标注⭐首选
      Why解释
        降低Agent决策负担
        避免方案选错
    3️⃣ Progressive<br/>Disclosure<br/>渐进式披露
      长度控制
        ≤500行正文
        skill-creator推荐值
      内联内容
        操作步骤
        核心参数
        工具函数
        检查清单
      引用内容
        完整参数表 → 知识库
        故障排查树 → 知识库
        长期方案配置 → 知识库
      按需加载
        scripts/ → 脚本
        references/ → 参考
        assets/ → 资源
    4️⃣ Why-<br/>Explanation<br/>设计意图解释
      格式规范
        "> **为什么？**"
        引用块格式
      解释内容
        规则背后的意图
        不仅是"不能做"
        还要说"为什么不能"
      覆盖范围
        关键决策点
        非显而易见的规则
        安全相关约束
      反模式
        纯MUST规则列表
        无解释的禁止项
      实战价值
        边界情况正确判断
        避免同类错误重复
    5️⃣ Safety<br/>Checklist<br/>安全检查清单
      写操作必备
        发帖/编辑/删除/发布
      dry-run/预览机制
        脚本：--dry-run标志
        MCP：先展示diff
      幂等性检查
        避免重复添加
        prepend前缀匹配
        内容存在则跳过
      结果验证
        操作后刷新确认
        snapshot比对
      不可撤销警告
        发布即对外可见
        编辑有历史记录
      实操检查项forum-posting
        知识库已读
        登录状态确认
        dry-run已执行
        幂等性已检查
        用户明确确认
        间隔≥3秒
        按钮区分create类
        input/change事件已触发
        结果已验证
        草稿已清理
```

## 使用说明

- 本思维导图是 [skill-development.md](./skill-development.md) §3 五要素模型的可视化展开
- 创建/优化 Skill 时，对照五个分支逐项检查即可完成质量自检
- 最右侧叶子节点是具体的检查点和正/反例，可直接作为 review 清单使用
- 与 [skill-development.md §8 验证清单](./skill-development.md#8-验证清单) 配合使用：验证清单是9项快速过检，本思维导图是深度参考

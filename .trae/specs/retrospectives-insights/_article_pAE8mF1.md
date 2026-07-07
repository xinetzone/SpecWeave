winkrun winkrun

在小说阅读器读本章

去阅读

大家必装的skill升级了，这次有点不一样。

Superpowers 是一套技能和指令组合，遵循完整的软件开发方法论，适用于 Claude Code、Codex 等各种编码 Agent。6.0 版本经过 Fable 5 优化，运行速度大幅提升 50%，Token 消耗减少 60%，同时保持同样高质量的输出。

![](https://mmbiz.qpic.cn/mmbiz_jpg/rY5icXvTTrJ9tHicoPXLbkHoWZibtzWNtL6nlwzgje4m6J13orFtFoictfbAtcYV6oVQlcVxffUz4tibbBrkNBfTicUC4a7w4teyCs44d3e7roia24/640?wx_fmt=jpeg)

## 怎么做到的？

官方团队写了一篇博客详细解释优化过程。核心思路是：让 Fable 5 自动分析 Superpowers 的构建循环，然后自己跑实验优化自己。

第一晚，Fable 分析了数千次 Subagent Driven Development 会话，发现代码审查子 Agent 在执行审查时跑了大量 git 命令。简单地将审查指令改为一个预生成审查包的 shell 脚本，就减少了约 10% 的 Token 消耗和运行时间。

第二晚，团队让 Fable 继续优化，目标是再省 15%。Fable 独立得出结论：将代码审查和规范合规审查合并为一个 Agent。测试结果：又省了 15%。

![Fable 自动研究循环结果截图](https://mmbiz.qpic.cn/sz_mmbiz_png/rY5icXvTTrJ9qVMicfqP6icBdHmDFnmcicxiaX4LA9OVIsbFXjibHFibnB6CicicJDt6bD6waV7iaIiahXo3SwZox3stb9BCIxBJkicW4qautSygGibaC0Ow/640?wx_fmt=png&from=appmsg)

第三晚，团队更激进了：让 Fable 跑一个完整的自动研究循环，执行至少 25 个实验。Fable 构建了自动研究框架，花了一整夜，耗资约 165 美元（未补贴价格）。结果：

- 简洁审查合同：审查输出减少 41%，结论不变
- 叙述配方：输出减少 54%，零方差
- 条件实现者分层：每轮节省约 0.5-1 美元
- 限制控制器思考反而适得其反——思考时间增加，但回合效率更高

最终，在 Claude Code 上，运行时间降低 50%，Token 消耗降低 60%。在 Codex 上，一开始测出来没变化——后来发现是基准测试环境没隔离，修正后结果一致。

![Codex 测试结果截图](https://mmbiz.qpic.cn/mmbiz_png/rY5icXvTTrJ9n4lNuyCebib078y8YYicS7gZ0aicFYEicJUB7UeiaZgKNzhjUgeAdEgyOiaYX7sDPGmIWW6kBv5bBYdPkI4N3K2EX3ax5hSfTGw2vQ/640?wx_fmt=png&from=appmsg)

## 这件事有意思在哪？

不是数字本身。而是优化过程：让 Agent 自己优化自己的流程，结果比人类手动调整好得多。Fable 在几小时内完成了人类可能花几周才能完成的实验循环，而且它自己发现了合并审查 Agent 这个人类也想到但还没来得及验证的方案。

当然，有网友指出，Superpowers 的流程更适合项目或模块 0 到 1 的阶段，对于其他用途，这个流程可能太重了。这确实是个合理的判断——它做了大量前期规划、TDD、双重审查，自然会慢一些。但如果你需要高质量的、可自主运行的代码生成，Superpowers 6.0 可能是目前最省 Token 的选择。

## 怎么用？

Superpowers 6.0 已发布，支持 Claude Code、Codex、Cursor、Antigravity、Kimi Code、OpenCode、Pi 等多种编码 Agent。安装方式因平台而异，GitHub 仓库有详细说明：https://github.com/obra/superpowers

官方博客：https://blog.fsck.com/2026/06/15/Superpowers-6/

关注公众号回复“进群”入群讨论

微信扫一扫  
使用小程序

： ， ， ， ， ， ， ， ， ， ， ， ， 。 视频 小程序 赞 ，轻点两下取消赞 在看 ，轻点两下取消在看 分享 留言 收藏 听过
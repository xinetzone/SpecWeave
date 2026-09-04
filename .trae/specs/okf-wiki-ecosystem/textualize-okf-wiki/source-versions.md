# Textualize 信源版本登记（G0）

- 盘点日期：2026-09-01
- 信源根目录：`external/dao/action/Textualize/`（工作区持久目录，非临时段）
- 冻结策略：任务期间禁止 `git pull` / 切换分支；按盘点时 commit hash 视为固定快照
- 全部仓库位于 main 分支（浮动分支风险已用 hash 记录对冲）

| 仓库 | 分支 | commit hash | 远程 URL | 深度分层 |
|------|------|-------------|----------|---------|
| rich | main | 9d8f9a372cc5916fd4781fec207ced7ddac2f08f | git@github.com:Textualize/rich.git | deep |
| textual | main | 06dbeef4bb70fb718236aa418ed658ef4667a126 | git@github.com:Textualize/textual.git | deep |
| frogmouth | main | 15c3e85a6e84b2e4a6845723acf12beb54c81eb2 | git@github.com:Textualize/frogmouth.git | medium |
| toolong | main | 5aa22ee878026f46d4d265905c4e1df4d37842ae | git@github.com:Textualize/toolong.git | medium |
| trogon | main | eaa9e68c403cae6aff0a80957d8876b284fd76b0 | git@github.com:Textualize/trogon.git | medium |
| rich-cli | main | 46f4d2469097be395558768714a5f07ebccf1412 | git@github.com:Textualize/rich-cli.git | medium |
| textual-dev | main | e563f96f32d582b7cf22622a401f537c40349adc | git@github.com:Textualize/textual-dev.git | medium |
| textual-serve | main | fa5cf5f5b4273c97ed286a55747106701ddc9917 | git@github.com:Textualize/textual-serve.git | medium |
| textual-web | main | 7d6741c9f7869881722d7d8dcf70a286cc270db9 | git@github.com:Textualize/textual-web.git | medium |
| textual-demo | main | babcbd1b742ba893e834fafb6f82930ae18cad65 | git@github.com:Textualize/textual-demo.git | light |
| textual-key-recorder | main | 8c3176ca020b261f041a4d9d7dc927a279cc69c1 | git@github.com:Textualize/textual-key-recorder.git | light |
| .github | main | 37d03f2bc007387c8efa3c12bd273ea8fb1c763e | git@github.com:Textualize/.github.git | light |

## G0 判定记录

- 信源分类：全部为工作区持久目录克隆（非 temporary/env-bound），但处于 main 浮动分支
- 处置：不升级 vendor 子模块（用户指定信源目录），以 commit hash + 盘点日期固定快照语义
- 路径引用规范：facts 与文档中信源路径一律写 `external/dao/action/Textualize/<repo>/...` 相对形式，禁止 file:/// 绝对路径

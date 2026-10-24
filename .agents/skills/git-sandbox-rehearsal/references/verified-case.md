# 取证、实测与未验证项

本文件区分四类信息：来源会话里读到的工具输出、仓库中可复核的历史事实、本次落盘前的真实沙箱实测、以及无法确认的推断。

## 1. 来源会话

会话 `758291eb-74a7-4b27-b7eb-956977dcbdea`（标题「创建原子提交技能」）在本机留下了多仓预演的过程证据：

| 证据 | 内容 |
|---|---|
| 沙箱位置 | `RH=D:/<repo>/.git/atomic-split-rehearsal-20261024-114136`，预演结束后 `REHEARSAL_REMOVED=yes` |
| git 目录解析 | `GITDIR=.../nested/.git`，子模块场景下 `--absolute-git-dir` 可用 |
| 父仓子模块 | `GITLINK_IN_TREE` 与 `NESTED_HEAD` 相等，`GITLINK_MATCH=yes` |
| 推送前后计数 | 首次 `no-upstream`，推送后 `0<TAB>0` |
| 远端提交 | `ls-remote` 等于本地 HEAD |
| 远端领先 | 另一个克隆推一条后计数为 `0<TAB>1` |
| 收尾 | 沙箱删除，真实仓库未提交、未推送 |

该会话的压缩转储只保留工具输出，不保留命令参数，因此「是否用过 `-c protocol.file.allow=always`、`ls-tree` 前是否 fetch」不能从转储直接确认。

## 2. 交叉证据

同项目技能 `atomic-commit-mixed-file-split` 的取证文件记录了来源会话 `c9d91a62-53d0-4853-8e7d-1f4b25892d0d` 中的两类真实失败：

| 现象 | 原因 | 处置 |
|---|---|---|
| `cd: projects/<x>: No such file or directory` | Bash 调用之间工作目录被重置 | 全部改为 `git -C <绝对路径>` |
| `cp: cannot stat '/tmp/<file>'` | Git Bash 的 `/tmp` 与 Windows Python 临时目录不是同一命名空间 | 临时产物改放 `--absolute-git-dir` 下 |

上述两条是 SKILL.md 第 12、13 节的直接来源；对应证据见 `atomic-commit-mixed-file-split/references/verified-case.md` 与 `references/split-runbook.md` 第 1 节。

该技能的实测记录还提供了分层推送的参考数值：首次 `no-upstream`、推送后 `0 0`、另一克隆推送后 `0 1`、`ls-tree` gitlink 与嵌套 HEAD 一致。

## 3. 本次落盘前的沙箱实测

目的：确认推荐数据中两个未经会话转储证实的说法，并验证 SKILL.md 的命令能跑通。

环境：Windows 10，Git 2.56.0.windows.2，Python 未参与本次实测；宿主机全局配置 `protocol.file.allow=always`、`core.autocrlf=true`。

| 用例 | 命令要点 | 实测结果 |
|---|---|---|
| 默认策略 + 普通路径 | `git -C parent -c protocol.file.allow=user submodule add <abs-path> libs/nested` | `fatal: transport 'file' not allowed`，EXIT=128，工作树 0 行改动 |
| 默认策略 + `file://` | 同上，URL 换成 `file:///D:/.../remote.git` | 同样被拒，EXIT=128 |
| `always` + 普通路径 | `git -C parent -c protocol.file.allow=always submodule add ...` | 成功，gitlink 等于嵌套 HEAD |
| 宿主机全局配置 | `git config --global --get protocol.file.allow` | `always`，说明不显式测试会被全局配置掩盖 |
| 领先计数 | `rev-list --left-right --count HEAD...origin/main` | `1<TAB>0` |
| 未 fetch 的陈旧计数 | 第二个克隆推送后、未 fetch | `0<TAB>0` |
| fetch 后的落后计数 | 同上，fetch 后 | `0<TAB>1` |
| 落后推送 | `push origin HEAD:main` | EXIT=1，`non-fast-forward` |
| 远端提交断言 | `ls-remote origin refs/heads/main` | 等于本地 HEAD |
| 父仓远端 gitlink | `ls-tree origin/main libs/nested` | 等于嵌套 HEAD |
| 只 `git add` 子模块 | 子模块副本未更新时 `git add libs/nested` | `nothing to commit`，EXIT=1 |
| 先更新副本再 add | `fetch` + `checkout <sha>` + `add` | 提交成功，`ls-tree` 与嵌套 HEAD 一致 |
| 清理与残留 | 前缀校验 `rm -rf` 后检查 | 沙箱不存在，`.git` 下无 `git-sandbox-*` |

沙箱位于 `D:/<repo>/.git/git-sandbox-20261024-121617`，验证结束后已删除。本次没有向真实仓库写入文件、修改配置或推送。

## 4. 与推荐数据的差异

| 推荐说法 | 实测修正 |
|---|---|
| 「本地子模块必须 `protocol.file.allow=always`」 | 方向正确，但条件是默认策略 `user`。若宿主机全局已设为 `always`，不加参数也能成功；为避免「换台机器就失败」，仍应在命令上显式携带。 |
| 「`ls-tree origin/main` 需先 fetch」 | 成立，但无法从来源转储确认当时是否如此操作。本次用第二个克隆构造远端推进，验证了「未 fetch 的 rev-list 读数为 `0 0`」这一同源机制。 |
| 「按被测流程执行并用 rev-list/ls-remote/ls-tree 断言」 | 成立。补充一个来源未记录的坑：父仓 gitlink 不会因 `git add` 自动前移，必须先把子模块副本 fetch + checkout 到目标 SHA。 |

## 5. 未验证或不可复核项

1. 来源会话的具体命令参数未保留在转储中，本技能的命令序列是按同一目标重建并实测的等价流程，不是对历史命令的逐字转录。
2. 未在 Linux/macOS 上实测；`--absolute-git-dir`、本地裸远端与 `rev-list` 语义跨平台一致，但 `/tmp` 命名空间问题只适用于 Windows。
3. 未验证真实网络远端（HTTPS/SSH）下的行为。本技能明确不覆盖联网推送与凭据场景。
4. 未对真实仓库做任何写入，因此没有「真实多仓推送」的现场样本；来源会话的推送证据来自其工具输出，不能在本机用相同 SHA 复现。
5. 共享工作树是活跃环境：本次实测期间真实仓库 HEAD 由其他会话推进，工作树条目数也发生变化。该变化未被归因于本次预演，因为预演全程只对真实仓库执行了 `rev-parse` 与 `status` 读取；这也验证了「不要用全局 HEAD 快照判定污染」的规则。

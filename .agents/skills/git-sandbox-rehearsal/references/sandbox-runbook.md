# 沙箱执行手册与实测记录

本文件给出可直接复制的命令序列，并记录 2026-10-24 在 Windows + Git 2.56 上的实测。占位符按第 1 节替换；SHA 与计数是当次运行的产物，重跑会变化，断言的是关系而不是具体值。

## 1. 一次性变量

```bash
export GIT_TERMINAL_PROMPT=0
REAL="<真实仓库绝对路径>"                 # 只用于解析 git 目录
GITDIR="$(git -C "$REAL" rev-parse --absolute-git-dir)"
ROOT="$GITDIR/git-sandbox-$(date +%Y%m%d-%H%M%S)"
NESTED="$ROOT/nested"
BARE="$ROOT/remote.git"
PARENT="$ROOT/parent"
PARENT_BARE="$ROOT/parent-remote.git"
SECOND="$ROOT/second"
```

## 2. 建仓与基线

```bash
test -e "$ROOT" && { echo "SANDBOX_EXISTS"; exit 2; }
mkdir -p "$NESTED" "$PARENT"

git -C "$NESTED" init -q -b main
git -C "$NESTED" config user.email sandbox@example.invalid
git -C "$NESTED" config user.name "Sandbox Bot"
git -C "$NESTED" config core.autocrlf false
printf 'v1\n' > "$NESTED/data.txt"
git -C "$NESTED" add data.txt
git -C "$NESTED" commit -q -m baseline
N0="$(git -C "$NESTED" rev-parse HEAD)"

git init -q --bare "$BARE"
git -C "$NESTED" remote add origin "$BARE"
git -C "$NESTED" push -q -u origin main

test "$(git -C "$NESTED" rev-parse --is-inside-work-tree)" = true
test "$(git -C "$NESTED" rev-list --count HEAD)" = 1
test "$(git -C "$NESTED" ls-remote origin refs/heads/main | cut -f1)" = "$N0"
```

## 3. 父仓子模块

```bash
git -C "$PARENT" init -q -b main
git -C "$PARENT" config user.email sandbox@example.invalid
git -C "$PARENT" config user.name "Sandbox Bot"
git -C "$PARENT" config core.autocrlf false

git -C "$PARENT" -c protocol.file.allow=always \
  submodule add "$BARE" libs/nested

git -C "$PARENT" add .gitmodules libs/nested
git -C "$PARENT" commit -q -m "baseline with submodule"

P0="$(git -C "$PARENT" rev-parse HEAD)"
GITLINK="$(git -C "$PARENT" ls-tree HEAD libs/nested | awk '{print $3}')"
test "$GITLINK" = "$N0"
git -C "$PARENT" config -f .gitmodules --get submodule.libs/nested.url   # 必须等于 $BARE
```

不带 `-c protocol.file.allow=always` 时，默认策略下会失败：

```text
fatal: transport 'file' not allowed
fatal: clone of '<path>' into submodule path '<path>' failed
EXIT=128
```

## 4. 远端门禁与前移 gitlink

```bash
git init -q --bare "$PARENT_BARE"
git -C "$PARENT" remote add origin "$PARENT_BARE"
git -C "$PARENT" push -q -u origin main

# 嵌套仓产生一个待推送提交
printf 'v2\n' > "$NESTED/data.txt"
git -C "$NESTED" add data.txt
git -C "$NESTED" commit -q -m "nested advance"
N1="$(git -C "$NESTED" rev-parse HEAD)"

git -C "$NESTED" fetch -q origin
git -C "$NESTED" rev-list --left-right --count HEAD...origin/main   # 期望 1<TAB>0
git -C "$NESTED" push -q origin HEAD:main
test "$(git -C "$NESTED" ls-remote origin refs/heads/main | cut -f1)" = "$N1"

# 关键：先让子模块副本指向新提交，再暂存
git -C "$PARENT/libs/nested" fetch -q origin
git -C "$PARENT/libs/nested" checkout -q "$N1"
test "$(git -C "$PARENT/libs/nested" rev-parse HEAD)" = "$N1"
git -C "$PARENT" add libs/nested
git -C "$PARENT" commit -q -m "advance gitlink"
git -C "$PARENT" push -q origin HEAD:main

git -C "$PARENT" fetch -q origin
test "$(git -C "$PARENT" ls-tree origin/main libs/nested | awk '{print $3}')" = "$N1"
```

只执行 `git -C "$PARENT" add libs/nested` 而不先更新子模块副本时，实测输出：

```text
On branch main
nothing to commit, working tree clean
EXIT=1
```

## 5. 远端领先与推送门

```bash
git clone -q "$BARE" "$SECOND"
git -C "$SECOND" config user.email sandbox@example.invalid
git -C "$SECOND" config user.name "Sandbox Bot"
printf 'v3\n' > "$SECOND/data.txt"
git -C "$SECOND" add data.txt
git -C "$SECOND" commit -q -m "from second clone"
git -C "$SECOND" push -q origin main

# 不 fetch：仍读到旧引用
git -C "$NESTED" rev-list --left-right --count HEAD...origin/main   # 实测 0<TAB>0（假安全）

git -C "$NESTED" fetch -q origin
git -C "$NESTED" rev-list --left-right --count HEAD...origin/main   # 实测 0<TAB>1

git -C "$NESTED" push -q origin HEAD:main
# 实测 EXIT=1，输出包含 non-fast-forward 与 rejected
```

## 6. 清理

```bash
case "$ROOT" in
  "$GITDIR"/git-sandbox-*) rm -rf "$ROOT" ;;
  *) echo "REFUSE: $ROOT"; exit 2 ;;
esac
test -e "$ROOT" && echo "STILL_EXISTS" || echo "REMOVED"
ls -d "$GITDIR"/git-sandbox-* 2>/dev/null || echo "NO_SANDBOX_LEFT"
```

## 7. 本次实测记录

环境：Windows 10，Git 2.56.0.windows.2，全局 `protocol.file.allow=always`，全局 `core.autocrlf=true`。

| 检查 | 实测输出 |
|---|---|
| 沙箱位置 | `D:/<repo>/.git/git-sandbox-20261024-121617` |
| 嵌套仓基线 | `rev-list --count HEAD` = `1` |
| 子模块本地传输（默认策略） | 普通路径与 `file://` 均 `fatal: transport 'file' not allowed`，EXIT=128 |
| 子模块本地传输（`always`） | 克隆成功，gitlink 等于嵌套 HEAD |
| 领先计数 | `1<TAB>0` |
| 远端领先（未 fetch） | `0<TAB>0` |
| 远端领先（fetch 后） | `0<TAB>1` |
| 落后推送 | EXIT=1，`non-fast-forward` |
| 远端提交 | `ls-remote` 等于本地 HEAD |
| 父仓 gitlink | `ls-tree origin/main libs/nested` 等于嵌套 HEAD |
| 子模块副本未更新 | `git add` 后 `nothing to commit` |
| 收尾 | 沙箱删除后路径不存在 |

## 8. 失败重试的边界

- 子模块添加成功后再执行一次，报 `'libs/nested' already exists in the index` 并退出 128。不要用 `--force` 覆盖，换一个新时间戳的沙箱重来。
- 子模块添加在传输阶段失败时，`git status` 通常仍为空（本次实测 0 行），可以直接重试同一条命令。
- 预演中途发现断言设计错误时，保留输出、清理沙箱、修正断言后重建；不要在旧沙箱上继续叠加步骤，否则失败现场会被污染。

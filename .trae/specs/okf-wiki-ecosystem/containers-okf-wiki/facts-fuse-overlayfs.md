---
source: external/dao/action/Containers/fuse-overlayfs
---

# fuse-overlayfs 可验证事实

## 项目元信息

F-001: 项目名称为 `fuse-overlayfs`，版本为 `2.0.0`，使用 Rust 2024 edition，最低 Rust 版本为 `1.85.0`。

F-002: 项目许可证为 `GPL-2.0-or-later`，描述为 "Overlay Filesystem in Userspace"，仓库地址为 https://github.com/containers/fuse-overlayfs。

F-003: 项目依赖包括 fuser 0.17.0（启用 abi-7-40 特性）、rustix 1.1（启用 process 特性）、libc 0.2.183、signal-hook 0.3.18、parking_lot 0.12.5、log 0.4.29、env_logger 0.11.9、thiserror 2.0.18、rustc-hash 2.1.1。

F-004: 项目要求系统安装 libfuse >= v3.2.1；在用户命名空间中使用时要求 Linux Kernel >= v4.18.0。

## 项目结构

F-005: src/ 目录包含以下模块文件：config.rs、copyup.rs、datasource.rs、direct.rs、error.rs、layer.rs、main.rs、mapping.rs、node.rs、overlay.rs、whiteout.rs、xattr.rs，以及 sys/ 子目录。

F-006: src/sys/ 子目录包含以下模块：dir.rs、fs.rs、handle.rs、io.rs、mod.rs、openat2.rs、process.rs、statx.rs、xattr.rs。

F-007: main.rs 中声明了 11 个 mod：config、copyup、datasource、direct、error、layer、mapping、node、overlay、sys、whiteout、xattr（共12个，包含sys子模块）。

F-008: 开发规则要求：禁止在 src/sys/ 之外使用 unsafe 代码；禁止使用 unwrap()、expect()、panic!()，所有错误必须通过 reply.error(errno) 报告给内核。

## 配置模块 (config.rs)

F-009: 定义了 `pub struct OverlayConfig`，包含以下字段：lowerdir、upperdir、workdir、mountpoint、redirect_dir、context、plugins（Option<String>）；uid_str、gid_str（Option<String>）；uid_mappings、gid_mappings（Vec<IdMapping>）；timeout（f64，默认值 1_000_000_000.0）；xattr_permissions（i32，默认 0）；nfs_filehandles（i32，默认 0）；threaded、fsync、fast_ino_check、writeback、disable_xattrs（bool，fsync 和 writeback 默认 true）；squash_to_uid、squash_to_gid（Option<u32>）；debug、foreground、squash_to_root、ino_t_32、static_nlink、volatile_mode、noacl（bool）；fuse_options（Vec<String>）；euid（u32，默认调用 crate::sys::process::geteuid()）。

F-010: 定义了常量 `FUSE_PASSTHROUGH_OPTS: &[&str]`，包含 19 个 FUSE 透传选项：allow_root、default_permissions、allow_other、suid、nosuid、dev、nodev、exec、noexec、atime、noatime、diratime、nodiratime、splice_write、splice_read、splice_move、kernel_cache、max_write、ro、rw。

F-011: 提供了 `pub fn parse_args(args: &[String]) -> Result<OverlayConfig, String>` 函数解析命令行参数；提供了 `pub fn parse_lowerdir(lowerdir: &str) -> Vec<String>` 函数解析 lowerdir 路径（支持冒号分隔、反斜杠转义、插件语法 //plugin//path）；提供了 `pub fn parse_plugin_path(path: &str) -> Option<(&str, &str)>` 函数解析插件路径。

## 节点与 inode 管理 (node.rs)

F-012: 定义了 `pub enum DirState`，包含两个变体：`NotADir`（非目录）和 `Dir { children: FxHashMap<Vec<u8>, NodeId>, whiteouts: FxHashSet<Vec<u8>>, loaded: bool }`（目录，包含子节点映射、白名单集合、加载标记）。

F-013: 定义了三个全局静态原子变量用于 SIGUSR1 统计报告：`pub static STAT_NODES: AtomicU64`、`pub static STAT_INODES: AtomicU64`、`pub static STAT_PASSTHROUGH: AtomicBool`。

F-014: 定义了 `pub struct NodeId(pub u64)`（节点 ID 不透明句柄，非零）、`pub struct InodeKey { pub ino: u64, pub dev: u64 }`（底层文件系统 inode+dev 键）。

F-015: 定义了 `pub struct NodeArena`（节点竞技场），内部使用 FxHashMap<NodeId, OvlNode> 存储节点，next_id 从 1 开始；提供 new()、insert()、get()、get_mut()、remove()、contains_key() 方法，插入和删除时更新 STAT_NODES 计数。

F-016: 定义了 `pub struct OvlIno`，包含：nodes（FxHashSet<NodeId>，硬链接节点集合）、lookups（AtomicI64，FUSE lookup 计数）、mode（u32，文件模式）、fuse_ino（u64，分配给内核的 FUSE inode 号）。

F-017: 定义了 `pub struct OvlNode`，包含字段：parent（Option<NodeId>）、dir_state（DirState）、layer_idx（usize，所在层索引）、last_layer_idx（usize，最后存在的层索引）、tmp_ino（u64，底层 inode）、tmp_dev（u64，底层 dev）、name（Vec<u8>，文件名）、hidden_path（Option<String>，隐藏节点临时名）、hidden_dirfd（i32，隐藏节点目录 fd，默认 -1）、name_hash（u64，FNV-1a 哈希）、n_links（usize）、mode（u32），以及三个 bool 标志：do_unlink、do_rmdir、hidden。

F-018: OvlNode 提供了 new()、is_dir()、is_loaded()、mark_loaded()、mark_unloaded()、get_child()、children()、children_mut()、insert_child()、remove_child()、is_whiteout()、insert_whiteout() 方法；impl Drop for OvlNode 在 drop 时清理 hidden_path 指向的临时文件（unlinkat 或 unlinkat AT_REMOVEDIR）。

F-019: 定义了 `pub struct InodeTable`，包含：table（FxHashMap<InodeKey, Box<OvlIno>>）、fuse_map（FxHashMap<u64, InodeKey>，反向映射）、same_device（bool）、next_fallback（u64，冲突回退计数器，初始值 0x8000_0000_0000_0000）。

F-020: 提供了 `pub fn compute_fuse_ino(ino: u64, dev: u64, same_device: bool) -> u64` 函数：同设备时直接使用 ino（ino<=1 时加 2），跨设备时使用哈希算法；结果不为 0 或 1。

F-021: 提供了 `pub fn compute_path(arena: &NodeArena, id: NodeId) -> Vec<u8>` 函数：通过父指针链计算路径，根节点返回 b"."，子节点按 parent/name 拼接。

F-022: 使用 FNV-1a 哈希算法计算文件名哈希，FNV_OFFSET_BASIS 为 0xcbf29ce484222325，FNV_PRIME 为 0x100000001b3。

## 层管理 (layer.rs)

F-023: 定义了 `pub struct OvlLayer`，包含：ds（Box<dyn DataSource>，数据源）、low（bool，是否为只读下层）。

F-024: OvlLayer 提供 from_datasource() 构造函数，以及 root_fd()、st_dev()、stat_override_mode() 方法委托给 ds。

F-025: 提供了 `pub fn init_layers(lowerdir: &str, upperdir: Option<&str>, nfs_filehandles_config: i32, xattr_permissions: i32) -> Result<Vec<OvlLayer>, String>` 函数初始化层：上层（若存在）在索引 0，然后是各下层；使用 direct::new() 创建 DirectAccess 数据源；xattr_permissions=1 设置 Privileged 模式，=2 设置 Containers 模式；xino=on 要求所有层支持 NFS 文件句柄。

F-026: 提供了 `pub fn all_same_device(layers: &[OvlLayer]) -> bool` 函数，检查所有层是否在同一设备上（通过 st_dev() 比较）。

## Copy-up 逻辑 (copyup.rs)

F-027: 提供了 `fn copy_xattr(sfd: RawFd, dfd: RawFd) -> FsResult<()>` 函数复制扩展属性，跳过以 "trusted.overlay."、"user.overlay."、"overlay." 开头的内部 xattr。

F-028: 提供了 `fn copy_data(sfd: RawFd, dfd: RawFd, size: i64) -> FsResult<()>` 函数，数据复制优先级：FICLONE（reflink）→ sendfile → read/write 回退（1MB 缓冲区）。

F-029: 提供了 `pub fn create_node_directory(...)` 递归创建上层目录，在 workdir 创建临时目录后 rename 到上层，支持 RENAME_EXCHANGE 处理已存在目录。

F-030: 提供了 `pub fn copyup(...) -> FsResult<()>` 函数实现文件 copy-up：目录调用 create_node_directory；符号链接 readlinkat 后 symlinkat；特殊文件（chr/blk/fifo/sock）mknodat；普通文件 open→copy_data→futimens→copy_xattr→fchmod→rename；copy-up 完成后设置 node.layer_idx = 0。

## 直接文件系统访问 (direct.rs)

F-031: 定义了 `pub struct DirectAccess`，包含：resolved_path（String）、fd（Option<OwnedFd>，层根目录 fd）、dev（libc::dev_t）、stat_override（StatOverrideMode）、nfs_fh（i32，-1=error/0=no/1=yes）、fh_size（u32）。

F-032: 定义了 `struct DirectDirIterator` 包装 sys::dir::DirStream，实现 DirIterator trait。

F-033: impl DataSource for DirectAccess：所有文件打开通过 openat2::safe_openat（RESOLVE_IN_ROOT 防止符号链接逃逸）；stat 优先使用 statx，回退到 fstatat；xattr 操作通过 /proc/self/fd/<fd>/<basename> 路径；NFS 文件句柄通过 name_to_handle_at 获取后 FNV-1a 哈希。

F-034: 提供了 `pub fn new() -> DirectAccess` 构造未初始化实例，需调用 load_data_source() 初始化；提供 set_stat_override() 方法覆盖检测到的 stat 覆盖模式。

## 核心文件系统实现 (overlay.rs)

F-035: 定义了 `pub struct OverlayFs`，包含：config（OverlayConfig）、inner（RwLock<OverlayInner>）、open_files（RwLock<FxHashMap<u64, Arc<OwnedFd>>>>）、next_fh（AtomicU64，从 1 开始）、open_dirs（RwLock<FxHashMap<u64, Arc<DirHandle>>>>）、next_dh（AtomicU64，从 1 开始）、inode_backings（RwLock<FxHashMap<u64, (Arc<BackingId>, usize)>>，passthrough 引用计数）、fh_to_ino（RwLock<FxHashMap<u64, u64>>）、passthrough_enabled（AtomicBool）、notifier（Arc<OnceLock<fuser::Notifier>>）。

F-036: 定义了 `struct OverlayInner`，包含：layers（Vec<OvlLayer>）、inodes（InodeTable）、nodes（NodeArena）、root_id（NodeId）、workdir_fd（RawFd）、ino_passthrough（bool）、overflow（OverflowIds）、wd_counter（u64，从 1 开始）、can_mknod（bool，由 FUSE_OVERLAYFS_DISABLE_OVL_WHITEOUT 环境变量控制）。

F-037: OverlayFs::new() 初始化时：all_same_device() 判断 ino_passthrough；创建根节点（空名称，layer_idx=0，is_dir=true）；创建 NodeArena 和 InodeTable；next_fh/next_dh 从 1 开始。

F-038: impl Filesystem for OverlayFs 在 init() 中协商 FUSE 能力：FUSE_DONT_MASK、FUSE_SPLICE_READ/WRITE/MOVE、FUSE_PARALLEL_DIROPS、FUSE_HANDLE_KILLPRIV、FUSE_CACHE_SYMLINKS、FUSE_DO_READDIRPLUS、FUSE_READDIRPLUS_AUTO；根据条件启用 FUSE_PASSTHROUGH（与 writeback_cache 互斥）、FUSE_WRITEBACK_CACHE、FUSE_POSIX_ACL；passthrough 在设置 FUSE_OVERLAYFS_NO_PASSTHROUGH 或 fsync=0（volatile）时禁用。

F-039: 白名单（whiteout）检测有三种形式：.wh.<name> 文件、.wh. 前缀条目本身、char device (0,0)；目录不透明标记为 "trusted.overlay.opaque" xattr。

## 主入口 (main.rs)

F-040: main() 函数流程：parse_args() 解析配置 → 初始化日志（支持 FUSE_OVERLAYFS_DEBUG_LOG 环境变量输出到文件）→ 验证 lowerdir 和 mountpoint 必须存在 → redirect_dir 只支持 "off" → set_limits() 将 RLIMIT_NOFILE 提升到硬限制 → check_writeable_proc() 检查 /proc 是否可写 → open_trusted 打开 workdir → init_layers() 初始化层 → 配置 fuser MountOption 和 SessionACL（euid=0 默认加 default_permissions/allow_other/suid/noatime，否则加 default_permissions/noatime）→ 线程数默认可用并行度，Android 强制单线程 → 创建 OverlayFs → Session::new() 挂载 → 设置 notifier → 非前台模式 daemonize() → 注册 SIGUSR1 处理器（输出 STAT_NODES/STAT_INODES/STAT_PASSTHROUGH 统计）→ session.spawn() 运行事件循环。

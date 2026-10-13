```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-drvfs-manual-mount
02-network-mount
03-ntfs-folder-volumes
04-filesystem-semantics
05-version-and-modern-wsl
```

# 概念文档索引

| 编号 | 文档 | 说明 |
|------|------|------|
| 00 | [DrvFs 手动挂载能力概览与时代定位](00-overview.md) | 能力边界矩阵、三个核心心智模型、2017 博文与现代 WSL 的关系 |
| 01 | [DrvFs 手动挂载驱动器（U盘、移动盘、光驱）](01-drvfs-manual-mount.md) | `mkdir` + `mount -t drvfs` + `umount` 三步与历史报错排查 |
| 02 | [挂载 UNC 网络位置与凭据边界](02-network-mount.md) | 单引号/双反斜杠规则、凭据在 Windows 侧、`net.exe use` 与无报错失败排查 |
| 03 | [挂载无盘符卷：空 NTFS 文件夹挂载点](03-ntfs-folder-volumes.md) | 卷挂载点约束、drvfs 与 bind mount 的分工 |
| 04 | [不同底层文件系统的 DrvFs 语义差异](04-filesystem-semantics.md) | 权限位 0777、实际打开验证、大小写与链接支持矩阵、性能注意 |
| 05 | [版本边界与现代 WSL 演进](05-version-and-modern-wsl.md) | build 门槛、wsl.conf 自动挂载与 metadata 选项、`wsl --mount`、性能布局建议 |

# toolbox 事实

F-001: 项目现称Toolbx（曾用名Toolbox、Fedora Toolbox），是Linux上用于软件开发和主机故障排查的交互式命令行环境工具，构建在Podman和OCI标准容器技术之上。
F-002: Toolbx环境无缝访问用户主目录、Wayland/X11套接字、网络（含Avahi和CA证书）、可移动设备、systemd journal、SSH agent、D-Bus、ulimits、/dev和udev数据库，主机文件系统在/run/host访问。
F-003: 特别适用于OSTree-based操作系统（Fedora CoreOS、Silverblue），这类系统不鼓励在主机安装软件，Toolbx提供完全可变的容器环境。
F-004: 在Fedora上基于fedora-toolbox OCI镜像创建容器，不要求必须使用OSTree系统，在Fedora Workstation/Server上同样可用。
F-005: 项目使用Go语言编写，Go模块路径为github.com/containers/toolbox，Go版本要求1.22.0。
F-006: 主要Go依赖：github.com/spf13/cobra（CLI框架）、github.com/spf13/viper（配置）、github.com/sirupsen/logrus（日志）、github.com/godbus/dbus/v5（D-Bus）、github.com/NVIDIA相关库（GPU支持）。
F-007: src/cmd/目录下包含14个Go源文件：completion.go、create.go、enter.go、help.go、initContainer.go、list.go、rm.go、rmi.go、root.go、rootDefault.go、rootMigrationPath.go、root_test.go、run.go、utils.go。
F-008: 主要命令包括：create（创建容器）、enter（进入容器）、list（列出容器/镜像）、rm（删除容器）、rmi（删除镜像）、run（在容器中运行命令）、completion（Shell补全）。
F-009: 使用Meson构建系统（根目录meson.build、src/meson.build），包含meson_go_fmt.py辅助脚本和go-build-wrapper包装脚本。
F-010: doc/目录下包含多个man手册源文件：toolbox.1.md、toolbox-help.1.md、toolbox-list.1.md、toolbox-rm.1.md、toolbox-rmi.1.md、toolbox-run.1.md、toolbox.conf.5.md。
F-011: profile.d/目录下包含toolbox.sh脚本，用于Shell环境集成。
F-012: src/pkg/目录下包含term（终端处理）和utils（工具函数，含arch.go架构检测、rhel.go RHEL检测）两个子包。
F-013: data/gfx/目录下包含README.gif和powerup.gif演示图片。
F-014: 二进制名称仍为toolbox，Git仓库名称也仍为toolbox，名称迁移工作进行中。
F-015: test/system/目录包含系统测试，项目在Zuul CI上运行测试。

# qm 事实

F-001: 项目全称Quality Management，是用于运行功能安全质量管理软件的容器化环境，用于汽车ASIL（Automotive Safety Integrity Level）场景研究。
F-002: QM环境使用cgroups、namespaces、安全隔离等容器技术，防止QM内进程干扰系统上其他进程。
F-003: QM运行自己版本的systemd和Podman，不仅隔离应用和容器，也隔离systemd和Podman命令本身。
F-004: 软件安装在/usr/lib/qm/rootfs目录下，自动与主机隔离，内部可进一步使用Podman运行嵌套容器。
F-005: 项目包含独立的SELinux策略，QM进程运行在qm_t域，容器与qm_t进程及其他容器互相隔离。
F-006: 项目集成BlueChi（systemd服务控制器），QM内bluechi-agent基于主机/etc/bluechi/agent.conf配置，节点名前添加"qm."前缀。
F-007: OOM分数调整配置：QM容器默认oom_score_adj=500，QM内嵌套容器默认oom_score_adj=750，ASIL应用可设置为-1到-1000（-1000免疫OOM killer）。
F-008: 安装后执行/usr/share/qm/setup脚本，安装selinux-policy-targeted、podman、systemd、bluechi包，启用并启动qm.service（Quadlet）。
F-009: tools/qmctl/目录下包含qmctl工具：qmctl.py（Python实现）、qmctl（Shell包装脚本）、qmctl.1（man手册）。
F-010: 项目根目录tools/下包含多个Shell工具脚本：comment-tz-local、qm-is-ostree、qm-rootfs（输出rootfs位置）、qm-storage-settings（配置存储）、version-update。
F-011: subsystems/目录包含多个子系统模块：kvm、ros2、sound、video、text2speech、wayland、qm-oci-hooks，每个子系统有独立Makefile。
F-012: kvm子系统包含ContainerFile、build_kvm_container.sh构建脚本、kvm.container Quadlet文件。
F-013: wayland子系统包含weston.ini配置、wayland-session二进制、多个Quadlet文件（qm-dbus-broker.container、wayland-compositor.container）和Containerfile。
F-014: qm.container默认DropCapability包含sys_boot，默认不包含SYS_RESOURCE能力（自定义OOM分数时需手动添加）。
F-015: qm.8.md是man手册源文件，说明安装、进入QM环境（podman exec -ti qm sh）、安装额外包（dnf --installroot=/usr/lib/qm/rootfs）等操作方法。

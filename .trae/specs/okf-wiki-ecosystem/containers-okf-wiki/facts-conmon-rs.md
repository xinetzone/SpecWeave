# conmon-rs 事实

F-001: 项目定位为pod级别的OCI容器运行时监视器（OCI container runtime monitor），使用Rust语言编写。
F-002: 项目目标包含成为完整pod（容器组）的监视器，而非每个容器创建一个conmon实例。
F-003: 项目架构包含两个主要组件：Rust服务器端（conmon-rs/server）和Golang客户端（pkg/client）。
F-004: Rust服务器二进制入口文件位于conmon-rs/server/src/main.rs，二进制名称为conmonrs。
F-005: 项目使用Cap'n Proto作为RPC通信协议，客户端与服务器通过UNIX domain socket通信。
F-006: Cargo workspace包含3个成员：conmon-rs/common、conmon-rs/client、conmon-rs/server。
F-007: 所有Rust crate版本号为1.0.1，license为Apache-2.0，edition为2024。
F-008: conmon-common crate依赖capnp 0.27.0，build脚本使用capnpc生成代码。
F-009: conmonrs-cli crate（客户端CLI）依赖tokio、capnp-rpc、futures、serde等库。
F-010: conmonrs crate（服务器）依赖axum、clap、nix、libc、tracing、opentelemetry（可选feature）等库。
F-011: Go模块路径为github.com/containers/conmon-rs，Go版本为1.26.3。
F-012: Go客户端依赖capnproto.org/go/capnp/v3、github.com/opencontainers/runc、go.podman.io/common等库。
F-013: 服务器端支持journald日志、CRI日志格式、JSON日志三种容器日志后端（container_log/目录下）。
F-014: release profile配置为lto=true、opt-level="z"、codegen-units=1、panic="abort"、strip=true以优化二进制体积。
F-015: 项目提供静态链接二进制文件，可通过scripts/get脚本从Google Cloud Storage下载，支持cosign签名验证。

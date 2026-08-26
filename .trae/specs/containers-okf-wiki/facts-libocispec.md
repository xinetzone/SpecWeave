# libocispec 事实

F-001: 项目是用于解析OCI runtime和OCI image规范文件的库，支持C语言和Rust语言绑定。
F-002: 解析器直接从源仓库中的JSON schema生成。
F-003: C语言版本依赖json-c库（版本>=0.14），使用autotools构建系统（autogen.sh、configure、make）。
F-004: C API头文件命名格式为runtime_spec_schema_config_schema.h，提供_parse_file和_generate_json函数。
F-005: Rust crate名称为libocispec，版本为0.1.0，edition为2018。
F-006: Rust crate依赖chrono、serde、serde_json、serde_derive、serde-value、url库。
F-007: src/目录下包含lib.rs、serialize.rs、image/mod.rs、runtime/mod.rs、ocispec/子目录。
F-008: src/ocispec/目录下包含C语言实现文件：json_common.c、json_common.h、validate.c，以及Python代码生成脚本（generate.py、headers.py、helpers.py、json_api.py、sources.py）。
F-009: Rust crate导出三个公共模块：serialize、image、runtime。
F-010: runtime::Spec结构体提供load()和save()方法，通过serialize模块进行JSON反序列化和序列化。
F-011: image::ImageSpec结构体同样提供load()和save()方法。
F-012: src/runtime/test/目录下包含测试用配置文件config.test.json。
F-013: tests/目录下包含15个C语言测试文件（test-1.c到test-15.c）。
F-014: Rust crate默认feature启用"serde"和"deps-serde"，deps-serde启用chrono和url的serde feature。
F-015: 项目提供make generate-rust目标用于重新生成Rust类型绑定。

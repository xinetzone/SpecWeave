# protobuf 仓库结构与构建系统事实清单（R阶段）

采集范围：protobuf 主仓（d:\spaces\SpecWeave\external\libs\protocolbuffers\protobuf，只读）的仓库顶层结构、各语言运行时目录、版本常量（protobuf_version.bzl / version.json / CMakeLists.txt）、CMake 构建系统（CMakeLists.txt 与 cmake/ 模块及全部 option）、Bazel 构建系统（MODULE.bazel / WORKSPACE / 顶层 BUILD.bazel / bazel/ 规则 / build_defs/ / toolchain/ / .bazelrc）、editions/ 目录、docs/ 文档、examples/ 示例、editors/ 编辑器支持、ci/ 与 compatibility/ 目录。每条事实仅记录代码/配置中客观存在的内容，事实编号 F-REPO-NNN，末尾标注源码文件路径（相对仓库根）。

## 一、仓库顶层结构

F-REPO-001: 仓库根下含 32 个目录：.bazelci、.bcr、.github、bazel、benchmarks、build_defs、ci、cmake、compatibility、conformance、csharp、docs、editions、editors、examples、go、hpb、hpb_generator、java、lua、objectivec、patches、php、pkg、python、ruby、rust、src、third_party、toolchain、upb、upb_generator。 —— 仓库根

F-REPO-002: 仓库根下顶层文件含：BUILD.bazel、CMakeLists.txt、MODULE.bazel、WORKSPACE、WORKSPACE.bzlmod、protobuf_version.bzl、protobuf_deps.bzl、protobuf_release.bzl、protobuf.bzl、version.json、README.md、SECURITY.md、LICENSE、CONTRIBUTING.md、CONTRIBUTORS.txt、CODE_OF_CONDUCT.md、Protobuf.podspec、maven_install.json、maven_dev_install.json、global.json、.bazelrc、bazel9.bazelrc、.bazeliskrc、.bazelignore、.readthedocs.yml、appveyor.yml、appveyor.bat、generate_descriptor_proto.sh、regenerate_stale_files.sh、google3_export_generated_files.sh、fix_permissions.sh、Disable_bundle_install.patch、PrivacyInfo.xcprivacy、.clang-format、.gitmodules。 —— 仓库根

F-REPO-003: src/ 下含 google/、solaris/ 子目录与 BUILD.bazel、file_lists.cmake、libprotobuf-lite.map、libprotobuf.map、libprotoc.map、README.md；src/solaris/ 下仅含 libstdc++.la。 —— src/

F-REPO-004: src/google/protobuf/ 下含 bridge、compiler、io、json、stubs、test_protos、testdata、testing、util 九个子目录，该目录内共 330 个条目。 —— src/google/protobuf/

F-REPO-005: python/ 下含 dist、docs、google、protobuf_distutils 子目录与 C 扩展源文件（protobuf.c/h、descriptor.c/h、descriptor_pool.c/h、descriptor_containers.c/h、message.c/h、map.c/h、repeated.c/h、unknown_fields.c/h、convert.c/h、buffer_convert.c/h、extension_dict.c/h）、python_api.h、BUILD.bazel、build_targets.bzl、internal.bzl、py_extension.bzl、minimal_test.py、python_version_test.py、requirements.txt、MANIFEST.in、version_script.lds、README.md、.repo-metadata.json。 —— python/

F-REPO-006: java/ 下含 bom、core、internal、kotlin、kotlin-lite、lite、osgi、protoc、test、util 子目录与 BUILD.bazel、pom.xml、linkage_monitor.sh、lite.md、README.md。 —— java/

F-REPO-007: java/core、java/lite、java/kotlin、java/util 四个子目录均含 src/ 子目录、BUILD.bazel、generate-sources-build.xml、pom_template.xml；java/lite 另含 lite.awk、process-lite-sources-build.xml、proguard.pgcfg、generate-test-sources-build.xml；java/kotlin 另含 pom.xml 与 generate-test-sources-build.xml；java/util 含 generate-sources-build.xml。 —— java/core/、java/lite/、java/kotlin/、java/util/

F-REPO-008: java/protoc/ 下仅含 pom.xml 与 README.md 两个文件。 —— java/protoc/

F-REPO-009: csharp/ 下含 compatibility_tests、google、keys、protos、src 子目录与 BUILD.bazel、buildall.bat、buildall.sh、build_packages.bat、build_release.sh、build_tools.sh、generate_protos.sh、Google.Protobuf.Tools.nuspec、Google.Protobuf.Tools.targets、install_dotnet_sdk.ps1、NuGet.Config、CHANGES.txt、README.md、.editorconfig。 —— csharp/

F-REPO-010: objectivec/ 下含 DevTools、Tests 子目录、三个 Xcode 工程（ProtocolBuffers_iOS.xcodeproj、ProtocolBuffers_OSX.xcodeproj、ProtocolBuffers_tvOS.xcodeproj）与 BUILD.bazel、defs.bzl、generate_well_known_types.sh，及 GPB 前缀运行时源文件（GPBMessage、GPBDescriptor、GPBCodedInputStream、GPBCodedOutputStream、GPBArray、GPBDictionary、GPBExtensionRegistry、GPBExtensionInternals、GPBRootObject、GPBUtilities、GPBWellKnownTypes、GPBWireFormat、GPBUnknownField、GPBUnknownFields 各 .h/.m）与 .pbobjc 文件（GPBAny、GPBApi、GPBDuration、GPBEmpty、GPBFieldMask、GPBSourceContext、GPBStruct、GPBTimestamp、GPBType、GPBWrappers 各 .pbobjc.h/.m）。 —— objectivec/

F-REPO-011: php/ 下含 ext、src、tests 子目录与 BUILD.bazel、composer.json、composer.json.dist、internal_generated_files.bzl、generate_descriptor_protos.sh、generate_test_protos.sh、update_reserved_words.sh、release.sh、REFCOUNTING.md、README.md。 —— php/

F-REPO-012: ruby/ 下含 ext、lib、src、tests 子目录与 BUILD.bazel、defs.bzl、Gemfile、Gemfile.lock、google-protobuf.gemspec、generate_stubs.rb、Rakefile、pom.xml、README.md、.yardopts。 —— ruby/

F-REPO-013: rust/ 下含 bazel、cpp_kernel、protobuf_macros、release_crates、test、upb、upb_kernel 子目录与 BUILD、defs.bzl、dist.bzl、rules.bzl 及 Rust 源文件（protobuf.rs、protobuf_lite.rs、proxied.rs、repeated.rs、map.rs、singular.rs、primitive.rs、string.rs、enum.rs、extension.rs、codegen_traits.rs、cord.rs、prelude.rs、shared.rs、internal.rs、gtest_matchers.rs、gtest_matchers_impl.rs）。 —— rust/

F-REPO-014: rust/release_crates/ 下含 google_protobuf、google_protobuf_codegen、protobuf、protobuf_codegen、protobuf_example、protobuf_macros、protobuf_tests、protobuf_well_known_types 八个 crate 目录与 BUILD、cargo_test.sh、Cargo.toml、README.md、substitute_rust_release_version.bzl；google_protobuf crate 目录内含 BUILD.bazel、build.rs、Cargo-template.toml、README.md。 —— rust/release_crates/

F-REPO-015: rust/test/ 下含 cpp、encode_raw_string_as_crate_name、more_test_protos、p、q、rust_proto_library_unit_test、shared、treeshaking、upb 九个子目录。 —— rust/test/

F-REPO-016: lua/ 下含 BUILD.bazel、lua_proto_library.bzl、upb.c、upb.h、upb.lua、upbc.cc、def.c、msg.c、main.c、test_upb.lua、test.proto、README.md。 —— lua/

F-REPO-017: hpb/ 下含 backend（含 cpp、upb 子目录）、bazel、internal 子目录与 BUILD、arena.h、hpb.h、multibackend.h、options.h、ptr.h、repeated_field.h、requires.h、extension.cc/h、status.cc/h、status_test.cc；hpb/bazel/ 下含 hpb_proto_library.bzl 与 BUILD；hpb/internal/ 下含 internal.h、message_lock.cc/h、message_lock_test.cc、template_help.h、template_help_test.cc、os_macros_restore.inc、os_macros_undef.inc。 —— hpb/

F-REPO-018: hpb_generator/ 下含 tests 子目录与 BUILD、protoc-gen-hpb.cc、generator.cc/h、gen_accessors.cc/h、gen_enums.cc/h、gen_extensions.cc/h、gen_messages.cc/h、gen_repeated_fields.cc/h、gen_utils.cc/h、keywords.cc/h、names.cc/h、context.h、README.md；hpb_generator/tests/ 下含 basic_test_editions.proto、test_model.proto、test_extension.proto 等测试 proto 与 extension_test.cc、metadata_test.cc、multibackend_test.cc、repeated_test.cc、test_generated.cc、test_hpb_bzl_alias.cc 等测试源文件。 —— hpb_generator/

F-REPO-019: upb/ 下含 base、bazel、cmake、conformance、hash、json、lex、mem、message、mini_descriptor、mini_table、port、reflection、test、text、util、wire 十七个子目录与 BUILD、generated_code_support.h、README.md。 —— upb/

F-REPO-020: upb_generator/ 下含 c、cmake、common、minitable、reflection、stage0 子目录与 bootstrap_compiler.bzl、BUILD、common.cc/h、file_layout.cc/h、plugin.cc/h、plugin_bootstrap.h。 —— upb_generator/

F-REPO-021: go/ 下含 google/protobuf 子目录与 BUILD.bazel。 —— go/

F-REPO-022: conformance/ 下含 ruby、test_protos 子目录与 BUILD、conformance.proto、defs.bzl、bazel_conformance_test_runner.sh、conformance_test_runner.cc、conformance_test.cc/h、conformance_test_main.cc、各语言测试实现（conformance_cpp.cc、conformance_objc.m、conformance_php.php、conformance_python.py、conformance_rust.rs、ConformanceJava.java、ConformanceJavaLite.java）、binary_json_conformance_suite.cc/h、binary_wireformat.cc/h、text_format_conformance_suite.cc/h、testee.cc/h、test_manager.cc/h、failure_list_trie_node.cc/h、fork_pipe_runner.cc/h、failure_list_*.txt（cpp、csharp、csharp_performance、dart_upb、java、java_lite、jruby、jruby_ffi、objc、objc_performance、php、php_c、python、python-post26、python_cpp、python_upb、ruby、rust_cc、rust_upb）、text_format_failure_list_*.txt（cpp、dart_upb、java、java_lite、php、python、rust_cc、rust_upb）、update_failure_list.py、autoload.php、README.md。 —— conformance/

F-REPO-023: benchmarks/ 下含 BUILD、build_defs.bzl、benchmark.cc、compare.py、descriptor.proto、descriptor_sv.proto、empty.proto、gen_protobuf_binary_cc.py、gen_synthetic_protos.py、gen_upb_binary_c.py。 —— benchmarks/

F-REPO-024: third_party/ 下含 utf8_range 子目录与 BUILD.bazel、jsoncpp.BUILD、zlib.BUILD。 —— third_party/

F-REPO-025: patches/ 下含 protobuf_v25 子目录。 —— patches/

F-REPO-026: toolchain/ 下含 BUILD.bazel、cc_toolchain_config.bzl、platforms.bzl、toolchains.bazelrc。 —— toolchain/

F-REPO-027: pkg/ 下含 test 子目录与 BUILD.bazel、build_systems.bzl、cc_dist_library.bzl、README.md；pkg/test/ 下含 BUILD.bazel、file_lists.cmake.golden、gen_file_lists_golden_test.sh、test_lib.cc、test_lib.h。 —— pkg/

## 二、版本常量

F-REPO-028: protobuf_version.bzl 定义 7 个版本常量：PROTOC_VERSION = "37.0"、PROTOBUF_JAVA_VERSION = "4.37.0"、PROTOBUF_PYTHON_VERSION = "7.37.0"、PROTOBUF_PHP_VERSION = "5.37.0"、PROTOBUF_RUBY_VERSION = "4.37.0"、PROTOBUF_RUST_VERSION = "0.37.0"、PROTOBUF_LEGACY_RUST_VERSION = "4.37.0"。 —— protobuf_version.bzl

F-REPO-029: version.json 的 main 段含 protoc_version = "37-dev"、lts = false、date = "2026-07-09"；languages 段含 cpp = "7.37-dev"、csharp = "3.37-dev"、java = "4.37-dev"、javascript = "3.37-dev"、objectivec = "5.37-dev"、php = "5.37-dev"、python = "7.37-dev"、ruby = "4.37-dev"、rust = "0.37-dev"、legacy_rust = "4.37-dev"。 —— version.json

F-REPO-030: CMakeLists.txt 含 set(protobuf_VERSION_STRING "7.37.0")，并以 protobuf_VERSION_REGEX 正则解析出 protobuf_VERSION_MAJOR/MINOR/PATCH/PRERELEASE 四个变量。 —— CMakeLists.txt

F-REPO-031: MODULE.bazel 的 module 声明为：name = "protobuf"、version = "37.0-dev"（注释标注 "Automatically updated on release"）、bazel_compatibility = [">=8.0.0"]、compatibility_level = 1、repo_name = "com_google_protobuf"。 —— MODULE.bazel

## 三、CMake 构建系统

F-REPO-032: CMakeLists.txt 首部含 cmake_minimum_required(VERSION 3.16...3.26) 与 project(protobuf C CXX)。 —— CMakeLists.txt

F-REPO-033: CMakeLists.txt 定义 17 个 option：protobuf_INSTALL（默认 ON）、protobuf_BUILD_TESTS（OFF）、protobuf_BUILD_CONFORMANCE（OFF）、protobuf_BUILD_EXAMPLES（OFF）、protobuf_BUILD_PROTOBUF_BINARIES（ON）、protobuf_BUILD_PROTOC_BINARIES（ON）、protobuf_BUILD_LIBPROTOBUF（ON）、protobuf_BUILD_LIBPROTOC（OFF）、protobuf_BUILD_LIBUPB（ON）、protobuf_DISABLE_RTTI（OFF）、protobuf_TEST_XML_OUTDIR（""）、protobuf_ALLOW_CCACHE（OFF）、protobuf_FORCE_FETCH_DEPENDENCIES（OFF）、protobuf_LOCAL_DEPENDENCIES_ONLY（OFF）、protobuf_USE_UNITY_BUILD（OFF）、protobuf_BUILD_SHARED_LIBS（${protobuf_BUILD_SHARED_LIBS_DEFAULT}）、protobuf_WITH_ZLIB（${protobuf_WITH_ZLIB_DEFAULT}）。 —— CMakeLists.txt

F-REPO-034: CMakeLists.txt 按行号顺序 include 的仓库内 cmake 模块：protobuf-options.cmake（L72）、gtest.cmake（L311）、abseil-cpp.cmake（L314）、utf8_range.cmake（L317）、libprotobuf-lite.cmake（L318）、libprotobuf.cmake（L323）、libprotoc.cmake（L329）、libupb.cmake（L335）、upb_generators.cmake（L339）、protoc.cmake（L342）、tests.cmake（L376）、conformance.cmake（L380）、install.cmake（L384）、examples.cmake（L388）；另 include CMakeDependentOption（L54）、CheckLinkerFlag（L181）、CheckCXXSourceCompiles（L184、L224）。 —— CMakeLists.txt

F-REPO-035: cmake/ 目录含 20 个 .cmake 文件：abseil-cpp.cmake、conformance.cmake、dependencies.cmake、examples.cmake、gtest.cmake、install.cmake、libprotobuf-lite.cmake、libprotobuf.cmake、libprotoc.cmake、libupb.cmake、protobuf-configure-target.cmake、protobuf-generate.cmake、protobuf-options.cmake、protobuf-lite.pc.cmake、protobuf.pc.cmake、protoc.cmake、tests.cmake、upb_generators.cmake、upb.pc.cmake、utf8_range.cmake。 —— cmake/

F-REPO-036: cmake/ 目录另含 4 个 .in 模板：protobuf-config.cmake.in、protobuf-config-version.cmake.in、protobuf-module.cmake.in、version.rc.in，及 BUILD.bazel、dependencies_generator.py、README.md 与 4 个安装清单 golden 文件：installed_bin_golden.txt、installed_include_golden.txt、installed_lib_shared_golden.txt、installed_lib_static_golden.txt。 —— cmake/

## 四、Bazel 构建系统

F-REPO-037: WORKSPACE 首行 workspace(name = "com_google_protobuf")；文件内加载 //:protobuf_deps.bzl 并调用 protobuf_deps()，通过 http_archive 定义 platforms 0.0.10、googletest 1.15.0、rules_ruby 0.17.3（附 Disable_bundle_install.patch）、lua 5.2.4、google_benchmark、googleapis、com_google_absl_py 2.1.0、rules_fuzzing 0.5.3、com_google_protobuf_v25、rules_testing 0.9.0 等仓库，并执行 maven_install（name="maven" 与 name="protobuf_maven_dev"）。 —— WORKSPACE

F-REPO-038: WORKSPACE.bzlmod 文件内仅含注释，文字为"This is a WORKSPACE file used by bzlmod in combination with MODULE.bazel. It's used for a gradual migration and it should be empty. Don't remove this file. If the file doesn't exist, bzlmod falls back to WORKSPACE file."。 —— WORKSPACE.bzlmod

F-REPO-039: MODULE.bazel 的非 dev 依赖 bazel_dep 列表：apple_support 2.3.0（repo_name build_bazel_apple_support）、rules_proto 7.1.0、abseil-cpp 20250512.1、rules_cc 0.2.18、zlib 1.3.1.bcr.5、bazel_skylib 1.9.0、jsoncpp 1.9.6.bcr.2、rules_java 8.6.1、rules_jvm_external 6.7、rules_kotlin 2.3.20、rules_license 1.0.0、rules_pkg 1.0.1、rules_python 2.3.0、rules_rust 0.69.0、rules_shell 0.6.1、platforms 0.0.11、re2 2024-07-02.bcr.1。 —— MODULE.bazel

F-REPO-040: MODULE.bazel 的 dev_dependency：rules_ruby 0.20.1（附 single_version_override 与 Disable_bundle_install.patch）、rules_fuzzing 0.5.3（archive_override）、googletest 1.17.0.bcr.2、rules_testing 0.9.0、abseil-py 2.1.0（repo_name com_google_absl_py）、lua 5.4.6、googleapis 0.0.0-20240819-fe8ba054a、google_benchmark 1.9.2、com_google_protobuf_v25 25.0（archive_override，strip_prefix = "protobuf-25.0"，含 patches/protobuf_v25/ 下 0001 至 0008 共 8 个 patch）、jq.bzl 0.6.1。 —— MODULE.bazel

F-REPO-041: MODULE.bazel 通过 use_extension("//bazel/private/oss/toolchains/prebuilt:protoc_extension.bzl", "protoc") 定义 prebuilt_protoc，use_repo 声明 9 个平台仓库：prebuilt_protoc.linux_aarch_64、linux_ppcle_64、linux_s390_64、linux_x86_32、linux_x86_64、osx_aarch_64、osx_x86_64、win32、win64；其后 register_toolchains("//bazel/private/oss/toolchains/prebuilt:all") 与 register_toolchains("//bazel/private/oss/toolchains:all")。 —— MODULE.bazel

F-REPO-042: MODULE.bazel 定义 SUPPORTED_PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]；system_python extension 调用 system_python.find(name = "system_python", minimum = "3.9")。 —— MODULE.bazel

F-REPO-043: MODULE.bazel 的 rust extension 声明 rust.toolchain(edition = "2024", versions = ["1.85.0"])；crate extension 声明 crate.spec：googletest 0.14.2、linkme 0.3.35、paste 1.0.15、quote 1.0.38、syn（version ">=2, <3"，features 含 "full"）。 —— MODULE.bazel

F-REPO-044: MODULE.bazel 定义 PROTOBUF_MAVEN_ARTIFACTS 列表：com.google.code.findbugs:jsr305:3.0.2、com.google.code.gson:gson:2.8.9、com.google.errorprone:error_prone_annotations:2.5.1、com.google.j2objc:j2objc-annotations:2.8、com.google.guava:guava:32.0.1-jre；protobuf_deps.bzl 中亦定义同名同值的 PROTOBUF_MAVEN_ARTIFACTS 常量。 —— MODULE.bazel、protobuf_deps.bzl

F-REPO-045: MODULE.bazel 末尾定义 11 个 flag_alias：experimental_proto_descriptor_sets_include_source_info、experimental_protoc_opts、protocopt、proto_compiler、proto_toolchain_for_cc、proto_toolchain_for_java、proto_toolchain_for_javalite、strict_proto_deps、strict_public_imports、cc_proto_library_header_suffixes、cc_proto_library_source_suffixes（各自指向 @//bazel/flags 下的 starlark_flag）。 —— MODULE.bazel

F-REPO-046: MODULE.bazel 与 WORKSPACE 均注册 10 个 //toolchain: 下的交叉编译 toolchain：osx-x86_64-toolchain、osx-aarch_64-toolchain、linux-aarch_64-toolchain、linux-ppcle_64-toolchain、linux-s390_64-toolchain、linux-x86_32-toolchain、linux-x86_64-toolchain、win32-toolchain、win64-toolchain、k8-toolchain。 —— MODULE.bazel、WORKSPACE

F-REPO-047: 顶层 BUILD.bazel load 了 //bazel:cc_proto_library.bzl、//bazel:java_lite_proto_library.bzl、//bazel:java_proto_library.bzl、//bazel:proto_library.bzl、//bazel/toolchains:proto_lang_toolchain.bzl、//build_defs:cpp_opts.bzl（COPTS、LINK_OPTS）与 //:protobuf.bzl（internal_objc_proto_library、internal_php_proto_library、internal_py_proto_library）；文件内含 licenses(["notice"])、license target（package_name = "protobuf"）与 exports_files(["LICENSE", "PrivacyInfo.xcprivacy", "MODULE.bazel"])。 —— BUILD.bazel

F-REPO-048: 顶层 BUILD.bazel 通过 alias 定义 10 个 Well-Known Types target 的四组别名（共 40 个）：any、api、duration、empty、field_mask、source_context、struct、timestamp、type、wrappers 各自的 _proto、_cc_proto、_upb_proto、_upb_reflection_proto 变体，actual 均指向 //src/google/protobuf: 下同名 target，visibility 为 //visibility:public。 —— BUILD.bazel

F-REPO-049: 顶层 BUILD.bazel 另定义 target：descriptor_proto、compiler_plugin_proto、cpp_features_proto、cpp_file_options_proto、cpp_file_options_cc_proto、json_options_proto、json_enumvalue_options_proto、json_enumvalue_options_cc_proto、java_features_proto、go_features_proto、c_sharp_features_proto、generated_protos_proto、test_messages_proto2_cc_proto、test_messages_proto3_cc_proto、test_messages_proto2_java_proto、test_messages_proto3_java_proto、test_messages_proto2_objc_proto、test_messages_proto3_objc_proto、test_messages_proto3_php_proto。 —— BUILD.bazel

F-REPO-050: bazel/ 目录下含 8 个 .bzl 规则文件：proto_library.bzl、cc_proto_library.bzl、py_proto_library.bzl、java_proto_library.bzl、java_lite_proto_library.bzl、upb_c_proto_library.bzl、upb_proto_reflection_library.bzl、proto_descriptor_set.bzl，及 BUILD 与 common、flags、private、tests、toolchains 五个子目录。 —— bazel/

F-REPO-051: build_defs/ 目录含 9 个文件：arch_tests.bzl、BUILD.bazel、cc_proto_blacklist_test.bzl、compiler_config_setting.bzl、cpp_opts.bzl、internal_shell.bzl、java_opts.bzl、kotlin_opts.bzl、platforms.bzl。 —— build_defs/

F-REPO-052: protobuf_deps.bzl 定义 protobuf_deps() 函数，内含 if not native.existing_rule(...) 守卫的 http_archive 定义：bazel_features 1.33.0、bazel_skylib 1.9.0、abseil-cpp（commit 76bb24329e8bf5f39704eb10d21b9a80befa7c81，注释标注 "Abseil LTS 20250512.1"）等；文件头部 docstring 给出第三方消费者 WORKSPACE 加载片段。 —— protobuf_deps.bzl

F-REPO-053: .bazelrc 含 build --@com_google_protobuf//bazel/toolchains:prefer_prebuilt_protoc=false、build --@rules_rust//rust/settings:experimental_use_cc_common_link=True、build --features=layering_check、12 条 build --incompatible_* 标志（incompatible_check_sharding_support、incompatible_config_setting_private_default_visibility、incompatible_default_to_explicit_init_py、incompatible_disable_native_android_rules、incompatible_disable_starlark_host_transitions、incompatible_disable_target_provider_fields、incompatible_disallow_empty_glob、incompatible_dont_use_javasourceinfoprovider、incompatible_enable_android_toolchain_resolution、incompatible_enable_apple_toolchain_resolution、incompatible_exclusive_test_sandboxed、incompatible_top_level_aspects_require_providers、incompatible_use_cc_configure_from_rules_cc）、try-import-if-bazel-version >=9.0.0 %workspace%/bazel9.bazelrc，及 build:dbg/opt/asan/msan/tsan/ubsan、build:clang/linux/macos/windows/clang-cl/msvc-cl 配置段。 —— .bazelrc

## 五、editions/ 目录

F-REPO-054: editions/ 下含 codegen_tests、golden、input 三个子目录与 BUILD、defaults.bzl、defaults_test.cc、4 个 defaults_test_embedded*.h.template 模板（defaults_test_embedded.h.template、_base64、_decimal_array、_hex_array）、edition_defaults_test_utils.cc/h、edition_defaults_test_utils_test.cc、generated_files_test.cc、generated_reflection_test.cc、internal_defaults_escape.cc。 —— editions/

F-REPO-055: editions/codegen_tests/ 下含 BUILD 与 56 个 proto 文件，按文件名前缀分组：edition2023_* 30 个（如 edition2023_ctype.proto、edition2023_java_multiple_files.proto、edition2023_naming_style_*.proto 系列 9 个、edition2023_go_api_*.proto 系列 5 个）、edition2024_* 6 个（edition2024_default_symbol_visibility.proto 及其 5 个变体）、proto2_* 13 个（proto2_enum.proto、proto2_group.proto、proto2_optional.proto、proto2_packed.proto、proto2_required.proto、proto2_utf8_*.proto 3 个等）、proto3_* 7 个（proto3_enum.proto、proto3_implicit.proto、proto3_optional.proto、proto3_packed.proto、proto3_unpacked.proto、proto3_utf8_strict.proto、proto3_import.proto）。 —— editions/codegen_tests/

## 六、docs/ 目录

F-REPO-056: docs/ 顶层含 7 个 .md 文件：cmake_protobuf_generate.md、cpp_build_systems.md、field_presence.md、implementing_proto3_presence.md、jvm_aot.md、options.md、third_party.md，及 csharp、design、upb 三个子目录。 —— docs/

F-REPO-057: docs/upb/ 含 6 个文件：arena_fusion.md、design.md、render.py、style-guide.md、vs-cpp-protos.md、wrapping-upb.md。 —— docs/upb/

F-REPO-058: docs/design/ 含 editions、prototiller 两个子目录；design/editions/ 含 22 个 .md（含 README.md，如 what-are-protobuf-editions.md、edition-zero-features.md、edition-lifetimes.md、editions-feature-visibility.md、protobuf-editions-design-features.md、stricter-schemas-with-editions.md 等）与 images/ 子目录（3 个 .png）；design/prototiller/ 含 4 个 .md（README.md、editions-tooling.md、prototiller-reqs-for-edition-zero.md、prototiller-reqs-for-editions.md）。 —— docs/design/

F-REPO-059: docs/csharp/ 含 proto2.md 一个文件。 —— docs/csharp/

## 七、examples/ 目录

F-REPO-060: examples/ 下含 addressbook.proto、add_person.cc、add_person.py、add_person.rb、add_person.dart、AddPerson.java、list_people.cc、list_people.py、list_people.rb、list_people.dart、ListPeople.java 及构建文件 BUILD.bazel、CMakeLists.txt、Makefile、MODULE.bazel、WORKSPACE、WORKSPACE.bzlmod、pubspec.yaml、.bazelrc、.gitignore、README.md，另含 go、examples_with_hyphen 两个子目录。 —— examples/

## 八、编辑器支持、CI 与兼容性

F-REPO-061: editors/ 下含 proto.vim、protobuf-mode.el、README.txt 三个文件。 —— editors/

F-REPO-062: ci/ 下含 clang_wrapper、clang_wrapper++、push_auto_update.sh、python_compatibility.sh、README.md 五个文件。 —— ci/

F-REPO-063: compatibility/ 下含 smoke、v3.25.0 两个子目录与 BUILD.bazel。 —— compatibility/

F-REPO-064: compatibility/smoke/ 下含 9 个版本目录：v3.0.0、v3.8.0、v3.11.0、v3.19.0、v3.20.0、v21.12、v25.8、v26.0、v32.1，及 add_gencode.sh、refresh_gencode.sh、BUILD.bazel、CHECKED_IN_GENCODE_BUILD.bazel.template、proto3_gencode_test.proto、stale_gencode_smoke_test.bzl、StaleGencodeSmokeTest.java、README.md。 —— compatibility/smoke/

F-REPO-065: compatibility/v3.25.0/ 下含 patches 子目录、generic_test_protos-speed.srcjar、java_test_protos-speed.srcjar、lite_test_protos-speed.srcjar、README.md。 —— compatibility/v3.25.0/

F-REPO-066: MODULE.bazel 的 ruby extension 声明 ruby.toolchain(name = "ruby", version = "system") 与 ruby.bundle_fetch(name = "protobuf_bundle", gemfile = "//ruby:Gemfile", gemfile_lock = "//ruby:Gemfile.lock")，gem_checksums 含 bigdecimal-3.1.9、ffi-1.17.1、ffi-compiler-1.3.2、power_assert-2.0.5、rake-13.2.1、rake-compiler-1.1.9、rake-compiler-dock-1.2.1、test-unit-3.6.7 及对应 -java 变体的 sha256 值。 —— MODULE.bazel

F-REPO-067: MODULE.bazel 声明 python_headers extension（use_extension("//python/dist:python_downloads.bzl", "python_headers")），含 python_headers.source_archive(version = "3.10.0") 与两个 nuget_package(cpu = "i686"/"x86-64", version = "3.10.0") 调用，use_repo 声明 nuget_python_i686_3.10.0、nuget_python_x86-64_3.10.0、python-3.10.0。 —— MODULE.bazel

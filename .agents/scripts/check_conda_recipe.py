#!/usr/bin/env python3
"""
Conda Recipe 配置自动化检查脚本
基于 .agents/checklists/conda-build-best-practices.md 最佳实践清单

扫描 conda.recipe/ 目录下的 meta.yaml 和 build.sh，检查关键配置项是否遗漏。

Usage:
    python check_conda_recipe.py [path/to/conda.recipe]
    python check_conda_recipe.py projects/xuanspace/libs/caffe-ffi/conda.recipe
"""

import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

# ── Colors ──
class C:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'

@dataclass
class CheckResult:
    category: str
    name: str
    status: str  # 'PASS', 'WARN', 'FAIL'
    message: str
    detail: Optional[str] = None

@dataclass
class RecipeChecker:
    recipe_dir: Path
    meta_yaml: str = ""
    build_sh: str = ""
    results: List[CheckResult] = field(default_factory=list)

    def __post_init__(self):
        meta_path = self.recipe_dir / "meta.yaml"
        build_path = self.recipe_dir / "build.sh"
        if meta_path.exists():
            self.meta_yaml = meta_path.read_text(encoding='utf-8', errors='replace')
        if build_path.exists():
            self.build_sh = build_path.read_text(encoding='utf-8', errors='replace')

    def add(self, category: str, name: str, status: str, message: str, detail: str = None):
        self.results.append(CheckResult(category, name, status, message, detail))

    def check_meta_present(self, text: str = None):
        if not (self.recipe_dir / "meta.yaml").exists():
            self.add("meta.yaml", "文件存在", "FAIL", "meta.yaml 不存在")
            return False
        return True

    def check_build_present(self, text: str = None):
        if not (self.recipe_dir / "build.sh").exists():
            self.add("build.sh", "文件存在", "FAIL", "build.sh 不存在")
            return False
        return True

    # ── meta.yaml checks ──
    def check_build_number(self):
        m = re.search(r'number:\s*(\d+)', self.meta_yaml)
        if m:
            num = int(m.group(1))
            self.add("meta.yaml", "build:number", "PASS", f"build number = {num}")
        else:
            self.add("meta.yaml", "build:number", "FAIL", "未找到 build:number")

    def check_detect_prefix(self):
        if re.search(r'detect_binary_files_with_prefix\s*:\s*false', self.meta_yaml, re.I):
            self.add("meta.yaml", "detect_binary_files_with_prefix", "PASS",
                     "已设置 detect_binary_files_with_prefix: false（避免 RPATH 绝对路径 placeholder 错误）")
        elif re.search(r'detect_binary_files_with_prefix\s*:\s*true', self.meta_yaml, re.I):
            self.add("meta.yaml", "detect_binary_files_with_prefix", "FAIL",
                     "detect_binary_files_with_prefix 为 true，RPATH 相对路径时必须为 false")
        else:
            self.add("meta.yaml", "detect_binary_files_with_prefix", "WARN",
                     "未显式设置 detect_binary_files_with_prefix，建议设为 false 当使用 $ORIGIN 相对 RPATH 时")

    def check_missing_dso_whitelist(self):
        if re.search(r'missing_dso_whitelist', self.meta_yaml):
            # Extract all "- "pattern"" entries after missing_dso_whitelist until next top-level key
            entries = []
            in_block = False
            for line in self.meta_yaml.split('\n'):
                if re.match(r'^\s*missing_dso_whitelist\s*:', line):
                    in_block = True
                    continue
                if in_block:
                    # Match list item: whitespace + - + "pattern"
                    m = re.match(r'^\s+-\s+"([^"]+)"', line)
                    if m:
                        entries.append(m.group(1))
                    elif re.match(r'^\S', line) and not line.strip().startswith('#'):
                        # Hit a non-indented line (next top-level key)
                        break
            if entries:
                self.add("meta.yaml", "missing_dso_whitelist", "PASS",
                         f"已配置 DSO 白名单 ({len(entries)} 项): {', '.join(entries)}")
            else:
                self.add("meta.yaml", "missing_dso_whitelist", "WARN", "missing_dso_whitelist 存在但格式可能不正确或为空")
        else:
            self.add("meta.yaml", "missing_dso_whitelist", "WARN",
                     "未配置 missing_dso_whitelist，包内自带的共享库可能导致 DSO 检查误报")

    def check_python_version_constraint(self):
        if re.search(r'skip\s*:.*py<\d+', self.meta_yaml):
            m = re.search(r'skip\s*:.*py<(\d+)', self.meta_yaml)
            ver = m.group(1) if m else "?"
            self.add("meta.yaml", "Python 版本约束", "PASS", f"已设置 Python 版本约束 (py<{ver})")
        else:
            self.add("meta.yaml", "Python 版本约束", "WARN", "未设置 Python 版本约束 (skip: true # [py<X])")

    def check_host_deps(self):
        """检查关键host依赖：patchelf, cmake, scikit-build-core, 数值库开发包"""
        required_host = ['patchelf', 'cmake', 'scikit-build-core']
        found = []
        missing = []
        for dep in required_host:
            if re.search(rf'-\s+{re.escape(dep)}', self.meta_yaml):
                found.append(dep)
            else:
                missing.append(dep)

        # 检查 BLAS 库：openblas 需要同时有运行时和开发包
        has_libopenblas = bool(re.search(r'-\s+libopenblas\b', self.meta_yaml))
        has_openblas_dev = bool(re.search(r'-\s+openblas\b(?!\s*#.*runtime)', self.meta_yaml))

        if missing:
            self.add("meta.yaml", "host 构建工具依赖", "FAIL",
                     f"缺少关键 host 依赖: {', '.join(missing)}",
                     f"已找到: {', '.join(found)}")
        else:
            self.add("meta.yaml", "host 构建工具依赖", "PASS",
                     f"关键构建工具依赖齐全: {', '.join(found)}")

        if has_libopenblas and has_openblas_dev:
            self.add("meta.yaml", "BLAS/OpenBLAS 依赖", "PASS",
                     "OpenBLAS 配置正确：host 含 libopenblas(运行时) + openblas(开发包)")
        elif has_libopenblas and not has_openblas_dev:
            self.add("meta.yaml", "BLAS/OpenBLAS 依赖", "FAIL",
                     "只有 libopenblas(运行时)，缺少 openblas 开发包（头文件和 libopenblas.so 符号链接）")
        elif has_openblas_dev and not has_libopenblas:
            self.add("meta.yaml", "BLAS/OpenBLAS 依赖", "WARN",
                     "有 openblas 开发包但 run 段缺少 libopenblas 运行时")
        else:
            self.add("meta.yaml", "BLAS/OpenBLAS 依赖", "WARN",
                     "未检测到 OpenBLAS 依赖，如不需要 BLAS 加速可忽略")

    def check_run_deps(self):
        """检查run依赖是否有运行时库"""
        run_libs = []
        for lib in ['libopenblas', 'libprotobuf', 'numpy']:
            if re.search(rf'-\s+{re.escape(lib)}\b', self.meta_yaml):
                run_libs.append(lib)

        # 检查 run 段是否有 python 版本约束
        has_python = bool(re.search(r'requirements:.*run:.*-\s+python[><=]', self.meta_yaml, re.DOTALL))
        if has_python:
            self.add("meta.yaml", "run Python 版本", "PASS", "run 段已约束 Python 版本")
        else:
            self.add("meta.yaml", "run Python 版本", "WARN", "run 段未显式约束 Python 版本")

        if run_libs:
            self.add("meta.yaml", "run 运行时依赖", "PASS",
                     f"运行时库依赖: {', '.join(run_libs)}")
        else:
            self.add("meta.yaml", "run 运行时依赖", "WARN", "未检测到运行时库依赖（纯 Python 包可忽略）")

    def check_test_section(self):
        has_test = bool(re.search(r'^test\s*:', self.meta_yaml, re.MULTILINE))
        has_imports = bool(re.search(r'imports\s*:', self.meta_yaml))
        has_commands = bool(re.search(r'commands\s*:', self.meta_yaml))

        if not has_test:
            self.add("meta.yaml", "test 段配置", "FAIL", "未配置 test 段")
            return

        checks = []
        status = "PASS"
        if has_imports:
            # Check if internal deps are also tested
            imports_block = re.search(r'imports\s*:\s*\n((?:\s+-\s+\S+\s*\n?)+)', self.meta_yaml)
            if imports_block:
                imports = re.findall(r'-\s+(\S+)', imports_block.group(1))
                checks.append(f"imports: {', '.join(imports)}")
                if len(imports) < 2 and 'tvm_ffi' not in ' '.join(imports):
                    self.add("meta.yaml", "test/imports", "WARN",
                             f"建议同时测试内部依赖包（如 tvm_ffi），当前仅测试: {', '.join(imports)}")
        else:
            checks.append("无 imports 测试")
            status = "WARN"

        if has_commands:
            checks.append("commands: 有功能测试")
        else:
            checks.append("无 commands 功能测试")
            if status == "PASS":
                status = "WARN"

        self.add("meta.yaml", "test 段配置", status, '; '.join(checks))

    # ── build.sh checks ──
    def check_shell_options(self):
        if re.search(r'set\s+-[a-zA-Z]*e[a-zA-Z]*\s+-o\s+pipefail', self.build_sh) or \
           re.search(r'set\s+-eux\s+-o\s+pipefail', self.build_sh):
            self.add("build.sh", "set -eux -o pipefail", "PASS",
                     "已启用严格错误检查 (set -eux -o pipefail)")
        elif re.search(r'set\s+-e\b', self.build_sh):
            self.add("build.sh", "set -eux -o pipefail", "WARN",
                     "有 set -e 但缺少 -u/-x/-o pipefail，建议启用严格模式")
        else:
            self.add("build.sh", "set -eux -o pipefail", "FAIL",
                     "未启用 set -e 错误检查，可能导致静默失败")

    def check_patchelf_presence(self):
        if re.search(r'patchelf', self.build_sh):
            self.add("build.sh", "patchelf 使用", "PASS", "build.sh 中使用了 patchelf 修复 RPATH")
        else:
            self.add("build.sh", "patchelf 使用", "FAIL",
                     "未使用 patchelf 设置 RPATH，共享库依赖可能解析失败")

    def check_rpath_origin(self):
        """检查 RPATH 是否全是 $ORIGIN 相对路径，无绝对路径"""
        # Find patchelf --set-rpath lines
        rpath_lines = re.findall(r'patchelf\s+--set-rpath\s+"([^"]+)"', self.build_sh)
        # Also find CMAKE_INSTALL_RPATH
        cmake_rpath = re.findall(r'-DCMAKE_INSTALL_RPATH=(\S+)', self.build_sh)

        all_rpaths = rpath_lines + cmake_rpath
        absolute_paths = []
        origin_paths = []
        for rp in all_rpaths:
            if re.search(r'(?<!\$)/opt/|(?<!\$)/usr/|\$\{PREFIX\}/lib', rp):
                absolute_paths.append(rp)
            if r'\$ORIGIN' in rp or '$ORIGIN' in rp:
                origin_paths.append(rp)

        if absolute_paths:
            self.add("build.sh", "RPATH 相对路径", "FAIL",
                     f"RPATH 中发现绝对路径（会导致 prefix replacement 错误）: {absolute_paths}",
                     "请将 ${PREFIX}/lib 替换为 $ORIGIN/../../.. 相对路径")
        elif origin_paths:
            self.add("build.sh", "RPATH 相对路径", "PASS",
                     f"RPATH 使用 $ORIGIN 相对路径（避免 placeholder 错误）")
        else:
            self.add("build.sh", "RPATH 相对路径", "WARN",
                     "未检测到显式 RPATH 设置（纯 Python 包可忽略）")

    def check_rpath_depth_main(self):
        """检查主SO的RPATH是否有 $ORIGIN/../../.. (上溯3级到PREFIX/lib)"""
        # Check both patchelf --set-rpath lines AND CMAKE_INSTALL_RPATH
        patchelf_rpaths = re.findall(r'patchelf\s+--set-rpath\s+"([^"]+)"', self.build_sh)
        cmake_rpaths = re.findall(r'-DCMAKE_INSTALL_RPATH=(\S+)', self.build_sh)
        # Also check RPATH variables assigned before patchelf calls (e.g. NEW_RPATH, _MAIN_RPATH)
        var_rpaths = re.findall(r'(?:NEW_RPATH|_MAIN_RPATH|RPATH)\s*=\s*"([^"]+)"', self.build_sh)
        var_rpaths += re.findall(r'(?:NEW_RPATH|_MAIN_RPATH|RPATH)\s*=\s*"\\([^"]+)"', self.build_sh)
        all_rpaths = patchelf_rpaths + cmake_rpaths + var_rpaths

        has_main_depth = any(
            (r'\$ORIGIN/../../..' in rp or '$ORIGIN/../../..' in rp or
             r'\$ORIGIN/../../../' in rp or '$ORIGIN/../../../' in rp)
            for rp in all_rpaths
        )
        if has_main_depth:
            self.add("build.sh", "主SO RPATH 上溯级数", "PASS",
                     "主SO RPATH 包含 $ORIGIN/../../..（上溯3级到 PREFIX/lib）")
        else:
            self.add("build.sh", "主SO RPATH 上溯级数", "WARN",
                     "主SO RPATH 未检测到 $ORIGIN/../../..，系统库（protobuf/openblas）可能找不到",
                     f"检测到的RPATH: {all_rpaths if all_rpaths else 'none'}")

    def check_dep_so_rpath(self):
        """检查是否为依赖SO（如libtvm_ffi.so）也设置了RPATH"""
        # Check patchelf calls directly AND variable assignments for RPATH strings
        patchelf_calls = re.findall(r'patchelf\s+--set-rpath[^"]*"([^"]+)"', self.build_sh)
        var_rpaths = re.findall(r'(?:_TVM_RPATH|_DEP_RPATH|NEW_RPATH)\s*=\s*"\\([^"]+)"', self.build_sh)
        var_rpaths += re.findall(r'(?:_TVM_RPATH|_DEP_RPATH|NEW_RPATH)\s*=\s*"([^"]+)"', self.build_sh)
        all_rpaths = patchelf_calls + var_rpaths

        if len(all_rpaths) >= 2:
            # Check if one of them has 4-level depth for dep SO in lib/ subdir
            has_dep_depth = any(
                (r'\$ORIGIN/../../../../' in rp or '$ORIGIN/../../../../' in rp)
                for rp in all_rpaths
            )
            if has_dep_depth:
                self.add("build.sh", "依赖SO RPATH 同步修复", "PASS",
                         "已为依赖SO（如libtvm_ffi.so）独立设置RPATH（上溯4级）")
            else:
                self.add("build.sh", "依赖SO RPATH 同步修复", "WARN",
                         "有多个patchelf调用但依赖SO的RPATH上溯级数可能不正确（子目录需上溯4级）",
                         f"检测到的RPATH: {all_rpaths}")
        elif len(all_rpaths) == 1:
            self.add("build.sh", "依赖SO RPATH 同步修复", "WARN",
                     "只检测到1个RPATH设置，如果包内有多个SO（含依赖包的SO），需为每个SO独立设置RPATH")

    def check_editable_cleanup(self):
        """检查三重防护editable清理逻辑"""
        # Check for clean_editable helper or inline patterns
        has_helper = bool(re.search(r'clean_editable_files?\s*\(\)', self.build_sh))
        has_generic_pattern = bool(re.search(r'_editable_\*', self.build_sh))
        has_specific_pattern = bool(re.search(r'_editable_skbc_', self.build_sh))
        # Check for source-path .pth cleanup (grep for xuanspace|SpecWeave|_skbuild in .pth context)
        has_pth_find = bool(re.search(r'find.*\.pth', self.build_sh))
        has_pth_grep = bool(re.search(r'grep.*xuanspace|grep.*SpecWeave|grep.*_skbuild', self.build_sh))
        has_pth_cleanup = has_pth_find and has_pth_grep

        issues = []
        checks = []
        if has_helper:
            checks.append("clean_editable_files() 辅助函数")
        if has_generic_pattern:
            checks.append("通用 _editable_* 模式")
        elif has_specific_pattern:
            issues.append("editable 清理模式过于具体 (_editable_skbc_*)，建议改用 _editable_*")
        if has_pth_cleanup:
            checks.append("源码路径 .pth 文件清理")
        else:
            issues.append("未清理指向源码路径(xuanspace/SpecWeave/_skbuild)的 .pth 文件")

        if has_helper or has_generic_pattern:
            status = "PASS" if not issues else "WARN"
            self.add("build.sh", "Editable 清理 (build.sh内)", status,
                     '; '.join(checks + issues) if checks + issues else "已配置 editable 清理")
        elif has_specific_pattern:
            self.add("build.sh", "Editable 清理 (build.sh内)", "WARN",
                     "editable 清理模式过于具体 (_editable_skbc_*)，可能遗漏其他变体，建议改用 _editable_*")
        else:
            self.add("build.sh", "Editable 清理 (build.sh内)", "FAIL",
                     "未检测到 editable finder 文件清理逻辑，可能导致包从源码目录加载而非 site-packages")

    def check_pip_local_install(self):
        """检查是否优先pip install本地依赖（而非add_subdirectory编译源码）"""
        has_pip_install_local = bool(re.search(r'pip\s+install.*--no-deps.*--no-build-isolation', self.build_sh))
        has_cmake_args_save = bool(re.search(r'_OLD_CMAKE_ARGS.*CMAKE_ARGS', self.build_sh)) or \
                               bool(re.search(r'save.*CMAKE_ARGS|CMAKE_ARGS.*save', self.build_sh, re.I))
        has_cmake_args_restore = has_cmake_args_save  # Simplified

        if has_pip_install_local:
            checks = ["pip install 本地依赖"]
            if has_cmake_args_save:
                checks.append("CMAKE_ARGS 保存/恢复")
            else:
                checks.append("⚠️ 未保存/恢复 CMAKE_ARGS")
            self.add("build.sh", "pip install 本地依赖集成", "PASS" if has_cmake_args_save else "WARN",
                     '; '.join(checks))
        elif re.search(r'add_subdirectory.*tvm.ffi|add_subdirectory.*vendor', self.build_sh, re.I):
            self.add("build.sh", "pip install 本地依赖集成", "WARN",
                     "使用 add_subdirectory 编译依赖源码，建议改用 pip install 本地源码确保 ABI 版本一致")
        else:
            self.add("build.sh", "pip install 本地依赖集成", "WARN",
                     "未检测到本地依赖 pip install 逻辑（纯 Python 包或无本地依赖可忽略）")

    def check_skbuild_cmake_args_separator(self):
        """检查SKBUILD_CMAKE_ARGS是否用空格分隔（非分号）"""
        skbuild = re.search(r'SKBUILD_CMAKE_ARGS\s*=\s*"([^"]+)"', self.build_sh, re.DOTALL)
        if skbuild:
            args_str = skbuild.group(1)
            # Check for semicolons in CMake args (common mistake)
            if ';' in args_str and '-D' in args_str:
                # Allow semicolons only in $ORIGIN paths... actually ; in RPATH: is different
                # CMake args separated by ; is bad; they should be space-separated
                if re.search(r'-D\w+=[^;]*;[^-]', args_str):
                    self.add("build.sh", "SKBUILD_CMAKE_ARGS 分隔符", "FAIL",
                             "SKBUILD_CMAKE_ARGS 使用分号分隔参数，CMake 会将分号解析为列表分隔符导致参数错误",
                             "请使用空格分隔，行尾用反斜杠续行")
                else:
                    self.add("build.sh", "SKBUILD_CMAKE_ARGS 分隔符", "PASS", "SKBUILD_CMAKE_ARGS 使用空格分隔")
            else:
                self.add("build.sh", "SKBUILD_CMAKE_ARGS 分隔符", "PASS", "SKBUILD_CMAKE_ARGS 使用空格分隔")

    def check_cmake_args_isolation(self):
        """检查pip install前是否清空/隔离CMAKE_ARGS"""
        if re.search(r'export\s+CMAKE_ARGS\s*=\s*""', self.build_sh) or \
           re.search(r'unset\s+CMAKE_ARGS', self.build_sh) or \
           re.search(r'_OLD_CMAKE_ARGS.*CMAKE_ARGS.*export\s+CMAKE_ARGS\s*=', self.build_sh, re.DOTALL):
            self.add("build.sh", "CMAKE_ARGS 隔离", "PASS",
                     "pip install 前已隔离 CMAKE_ARGS（避免 conda 的 CMAKE_INTERRUPT_ARGS 干扰 wheel 构建）")
        else:
            self.add("build.sh", "CMAKE_ARGS 隔离", "WARN",
                     "未检测到 CMAKE_ARGS 隔离，conda 的 CMAKE_ARGS（含 CMAKE_INSTALL_PREFIX）可能干扰 scikit-build-core wheel 构建")

    def check_ldd_verification(self):
        """检查构建后是否运行ldd验证依赖"""
        has_ldd = bool(re.search(r'\bldd\b', self.build_sh))
        has_not_found_check = bool(re.search(r'ldd.*not found', self.build_sh))
        if has_ldd and has_not_found_check:
            self.add("build.sh", "ldd 依赖验证", "PASS",
                     "构建后运行 ldd 检查并验证无 'not found' 依赖")
        elif has_ldd:
            self.add("build.sh", "ldd 依赖验证", "WARN", "运行了 ldd 但未检查 'not found' 依赖")
        else:
            self.add("build.sh", "ldd 依赖验证", "WARN", "构建后未运行 ldd 验证共享库依赖解析")

    def check_nm_symbol(self):
        """检查是否用nm验证关键ABI符号"""
        if re.search(r'\bnm\b.*-D', self.build_sh):
            self.add("build.sh", "nm 符号验证", "PASS", "使用 nm -D 验证 ABI 符号导出（T 类型）")
        else:
            self.add("build.sh", "nm 符号验证", "WARN", "建议使用 nm -D 验证关键 ABI 符号是否为全局导出（T 类型）")

    def check_crlf_fix(self):
        """检查是否处理CRLF换行符"""
        if re.search(r'dos2unix|sed.*s/\\r\$//', self.build_sh):
            self.add("build.sh", "CRLF 修复", "PASS", "已处理 Windows/Docker 挂载的 CRLF 换行符问题")
        else:
            self.add("build.sh", "CRLF 修复", "WARN", "未检测到 CRLF 修复，Windows/Docker 挂载目录可能导致脚本执行错误")

    def check_intree_cleanup(self):
        """检查是否清理in-tree构建残留"""
        has_build_clean = bool(re.search(r'rm\s+.*build.*_skbuild|rm\s+-rf.*\bbuild\b', self.build_sh))
        if has_build_clean:
            self.add("build.sh", "In-tree 构建残留清理", "PASS",
                     "构建前已清理 build/, _skbuild/, dist/, *.egg-info 等残留目录")
        else:
            self.add("build.sh", "In-tree 构建残留清理", "WARN",
                     "未检测到 in-tree 构建残留清理，旧构建产物可能导致增量编译问题")

    def check_setuptools_scm(self):
        """检查是否处理setuptools-scm版本伪装"""
        if re.search(r'SETUPTOOLS_SCM_PRETEND_VERSION', self.build_sh):
            self.add("build.sh", "setuptools-scm 版本伪装", "PASS",
                     "已设置 SETUPTOOLS_SCM_PRETEND_VERSION（Docker 中 git submodule describe 可能失败）")
        else:
            self.add("build.sh", "setuptools-scm 版本伪装", "WARN",
                     "未设置 SETUPTOOLS_SCM_PRETEND_VERSION，git submodule 在 Docker 中可能无法正确获取版本")

    def check_backtrace_off(self):
        """检查是否关闭libbacktrace避免pytest崩溃"""
        if re.search(r'TVM_FFI_USE_LIBBACKTRACE\s*=\s*OFF', self.build_sh) and \
           re.search(r'TVM_FFI_BACKTRACE_ON_SEGFAULT\s*=\s*OFF', self.build_sh):
            self.add("build.sh", "libbacktrace 关闭", "PASS",
                     "已关闭 TVM_FFI_USE_LIBBACKTRACE（避免 pytest 环境下 backtrace_symbols() 崩溃）")
        elif re.search(r'BACKTRACE', self.build_sh):
            self.add("build.sh", "libbacktrace 关闭", "WARN",
                     "检测到 backtrace 相关配置但可能未完全关闭两个选项")
        # Not adding FAIL since this is project-specific

    def run_all_checks(self):
        meta_exists = self.check_meta_present()
        build_exists = self.check_build_present()

        if meta_exists:
            self.check_build_number()
            self.check_detect_prefix()
            self.check_missing_dso_whitelist()
            self.check_python_version_constraint()
            self.check_host_deps()
            self.check_run_deps()
            self.check_test_section()

        if build_exists:
            self.check_shell_options()
            self.check_patchelf_presence()
            self.check_rpath_origin()
            self.check_rpath_depth_main()
            self.check_dep_so_rpath()
            self.check_editable_cleanup()
            self.check_pip_local_install()
            self.check_skbuild_cmake_args_separator()
            self.check_cmake_args_isolation()
            self.check_ldd_verification()
            self.check_nm_symbol()
            self.check_crlf_fix()
            self.check_intree_cleanup()
            self.check_setuptools_scm()
            self.check_backtrace_off()

        return self.results

    def print_report(self):
        print(f"\n{C.BOLD}{'='*70}{C.NC}")
        print(f"{C.BOLD}  Conda Recipe 配置检查报告{C.NC}")
        print(f"{C.BOLD}{'='*70}{C.NC}")
        print(f"  Recipe 目录: {C.CYAN}{self.recipe_dir}{C.NC}")

        if not (self.recipe_dir / "meta.yaml").exists():
            print(f"\n  {C.RED}FAIL{C.NC}: meta.yaml 不存在")
        if not (self.recipe_dir / "build.sh").exists():
            print(f"  {C.RED}FAIL{C.NC}: build.sh 不存在（纯 Python 包可忽略）")

        # Group by category
        categories = {}
        for r in self.results:
            categories.setdefault(r.category, []).append(r)

        n_pass = n_warn = n_fail = 0
        for cat in ['meta.yaml', 'build.sh']:
            if cat not in categories:
                continue
            print(f"\n{C.BOLD}── {cat} ──{C.NC}")
            for r in categories[cat]:
                if r.status == 'PASS':
                    icon = f"{C.GREEN}  ✓ PASS{C.NC}"
                    n_pass += 1
                elif r.status == 'WARN':
                    icon = f"{C.YELLOW}  ⚠ WARN{C.NC}"
                    n_warn += 1
                else:
                    icon = f"{C.RED}  ✗ FAIL{C.NC}"
                    n_fail += 1
                print(f"{icon} {r.name}")
                print(f"         {r.message}")
                if r.detail:
                    print(f"         {C.CYAN}→ {r.detail}{C.NC}")

        # Summary
        print(f"\n{C.BOLD}{'='*70}{C.NC}")
        total = n_pass + n_warn + n_fail
        print(f"  总计: {total} 项检查")
        print(f"  {C.GREEN}PASS: {n_pass}{C.NC}  ", end='')
        print(f"{C.YELLOW}WARN: {n_warn}{C.NC}  ", end='')
        print(f"{C.RED}FAIL: {n_fail}{C.NC}")

        if n_fail > 0:
            print(f"\n  {C.RED}存在 {n_fail} 个必须修复的问题{C.NC}")
            return 1
        elif n_warn > 0:
            print(f"\n  {C.YELLOW}存在 {n_warn} 个建议改进项{C.NC}")
            return 0
        else:
            print(f"\n  {C.GREEN}所有检查通过！{C.NC}")
            return 0


def find_default_recipe():
    """Try to find a conda.recipe directory in common locations"""
    candidates = [
        Path.cwd() / "conda.recipe",
        Path.cwd() / "projects" / "xuanspace" / "libs" / "caffe-ffi" / "conda.recipe",
    ]
    for p in candidates:
        if (p / "meta.yaml").exists():
            return p
    return None


def main():
    if len(sys.argv) > 1:
        recipe_dir = Path(sys.argv[1]).resolve()
    else:
        recipe_dir = find_default_recipe()
        if recipe_dir is None:
            print("Usage: python check_conda_recipe.py [path/to/conda.recipe]")
            print("\nSearched default locations:")
            print(f"  {Path.cwd() / 'conda.recipe'}")
            sys.exit(1)

    if not recipe_dir.exists():
        print(f"Error: Directory not found: {recipe_dir}")
        sys.exit(1)

    checker = RecipeChecker(recipe_dir)
    results = checker.run_all_checks()
    exit_code = checker.print_report()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

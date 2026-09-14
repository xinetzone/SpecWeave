cmake_minimum_required(VERSION 3.18)
project(xmnn LANGUAGES NONE)

find_package(Python3 COMPONENTS Interpreter REQUIRED)

if(Python3_VERSION VERSION_LESS "3.14")
    message(FATAL_ERROR "Python 版本必须 >= 3.14，当前版本: ${Python3_VERSION}")
else()
    message(STATUS "  Python 版本: ${Python3_VERSION} (满足 >=3.14 要求)")
endif()

# 自包含 CACHE 变量：默认值指向 xmnn-dev 叠加层的容器内运行时布局，
# 构建时由 scripts/build-wheel.sh 以 cmake.define.* 覆盖（LLVM_LIB_DIR 取
# `llvm-config --libdir` 实测值，禁止硬编码 conda 快照 SONAME）。
set(NUITKA_OUTPUT_DIR "/opt/xmnn-builder/build/nuitka" CACHE PATH "Nuitka compilation output directory")
set(TVM_BUILD_DIR "/workspace/npu_tvm/build" CACHE PATH "TVM C++ build directory")
set(TVM_ROOT_DIR "/workspace/npu_tvm" CACHE PATH "TVM source root directory")
set(XMN_PYTHON_DIR "/workspace/npuusertools" CACHE PATH "npuusertools source directory")
set(LLVM_LIB_DIR "/opt/conda/envs/main/lib" CACHE PATH "LLVM and dependency libraries directory (inject llvm-config --libdir)")
set(XMN_NUITKA_OUT "${NUITKA_OUTPUT_DIR}/xmnn_out" CACHE PATH "XMNN Nuitka compilation output directory")

foreach(_d NUITKA_OUTPUT_DIR TVM_BUILD_DIR TVM_ROOT_DIR XMN_PYTHON_DIR LLVM_LIB_DIR XMN_NUITKA_OUT)
    if(NOT IS_ABSOLUTE "${${_d}}")
        set(${_d} "${PROJECT_SOURCE_DIR}/${${_d}}")
    endif()
endforeach()

message(STATUS "XMNN Wheel Build Configuration:")
message(STATUS "  PROJECT_SOURCE_DIR = ${PROJECT_SOURCE_DIR}")
message(STATUS "  NUITKA_OUTPUT_DIR  = ${NUITKA_OUTPUT_DIR}")
message(STATUS "  TVM_BUILD_DIR      = ${TVM_BUILD_DIR}")
message(STATUS "  XMN_PYTHON_DIR     = ${XMN_PYTHON_DIR}")
message(STATUS "  XMN_NUITKA_OUT     = ${XMN_NUITKA_OUT}")
message(STATUS "  LLVM_LIB_DIR       = ${LLVM_LIB_DIR}")

set(INSTALL_LIBDIR "_libs")

install(FILES "${PROJECT_SOURCE_DIR}/_xmnn_bootstrap.py" DESTINATION ".")
install(FILES "${PROJECT_SOURCE_DIR}/xmnn_bootstrap.pth" DESTINATION ".")
message(STATUS "  Will install bootstrap module and .pth file")

file(GLOB TVM_NUITKA_SO LIST_DIRECTORIES false "${NUITKA_OUTPUT_DIR}/tvm.cpython-*.so")
if(TVM_NUITKA_SO)
    install(FILES ${TVM_NUITKA_SO} DESTINATION ".")
    foreach(_f ${TVM_NUITKA_SO})
        message(STATUS "  Will install Nuitka tvm module: ${_f}")
    endforeach()
else()
    message(FATAL_ERROR "tvm Nuitka module not found at ${NUITKA_OUTPUT_DIR}")
endif()

set(TVM_LIB "${TVM_BUILD_DIR}/libtvm.so")
if(EXISTS "${TVM_LIB}")
    install(FILES "${TVM_LIB}" DESTINATION "${INSTALL_LIBDIR}")
    message(STATUS "  Will install TVM native lib: ${TVM_LIB}")
else()
    message(FATAL_ERROR "libtvm.so not found at ${TVM_LIB}（先运行 scripts/build-tvm.sh 或 inv xmnn.build-tvm）")
endif()

# ------------------------------------------------------------------------------
# LLVM 依赖库收集（SONAME 漂移防护 + 单副本）：
# 移植源按 2026-08 conda 快照硬编码 7 个文件名（libxml2.so.16 /
# libicuuc.so.78 等），conda 重新求解可能升级小版本导致静默缺库（旧实现缺失仅
# WARNING）。这里按 glob 收集，并遵循「wheel 运行时只需要 NEEDED 的 SONAME
# 短名」原则，每个依赖只落一份：
#   - 软链条目（SONAME 短名，如 libz.so.1 → libz.so.1.3.2）：cp -L 去引用
#     真实文件、以短名装入 _libs（wheel ZIP 经 scikit-build 打包会解引用软链，
#     建软链无意义；短名才是动态加载器 NEEDED 解析所用名字）；
#   - 被短链指向的长名真实文件（.so.1.3.2）跳过，避免内容重复（R1 F-2）；
#   - 本身即真实文件且无软链指向（如 conda 直接发布 libLLVM.so.22.1）：原名装。
# 任一模式收集为空即 FATAL_ERROR，并打印 libdir 候选供定位实际 SONAME。
# ------------------------------------------------------------------------------
function(install_llvm_deps GLOB_PATTERN LIB_LABEL)
    file(GLOB _matches LIST_DIRECTORIES false "${LLVM_LIB_DIR}/${GLOB_PATTERN}")
    set(_short_pairs "")
    set(_linked_targets "")
    set(_real_originals "")
    foreach(_m IN LISTS _matches)
        if(EXISTS "${_m}" AND NOT IS_DIRECTORY "${_m}")
            get_filename_component(_m_name "${_m}" NAME)
            get_filename_component(_m_real "${_m}" REALPATH)
            if(IS_SYMLINK "${_m}")
                list(APPEND _short_pairs "${_m_name}=>${_m_real}")
                list(APPEND _linked_targets "${_m_real}")
            else()
                list(APPEND _real_originals "${_m}")
            endif()
        endif()
    endforeach()
    # 注：CMake 4.x 仅识别复数拼写 REMOVE_DUPLICATES（3.x 曾接受单数
    # REMOVE_DUPLICATE，移植源的旧拼写在 cmake 4.4 报「does not recognize」）。
    list(REMOVE_DUPLICATES _short_pairs)
    list(REMOVE_DUPLICATES _linked_targets)
    list(REMOVE_DUPLICATES _real_originals)

    set(_install_pairs "${_short_pairs}")
    foreach(_orig IN LISTS _real_originals)
        if(NOT _orig IN_LIST _linked_targets)
            list(APPEND _install_pairs "${_orig}=>${_orig}")
        endif()
    endforeach()
    list(REMOVE_DUPLICATES _install_pairs)

    if(NOT _install_pairs)
        file(GLOB _all_libs LIST_DIRECTORIES false "${LLVM_LIB_DIR}/lib*.so*")
        message(FATAL_ERROR
            "LLVM dependency '${LIB_LABEL}' (${GLOB_PATTERN}) not found under ${LLVM_LIB_DIR}. "
            "SONAME may have drifted; inspect candidates under that libdir "
            "(available: ${_all_libs}) and update the GLOB_PATTERN / smoke guard.")
    endif()

    foreach(_pair IN LISTS _install_pairs)
        string(REPLACE "=>" ";" _pair_parts "${_pair}")
        list(GET _pair_parts 0 _dest_raw)
        list(GET _pair_parts 1 _src_path)
        # dest 可能是短链短名（libz.so.1）或同名绝对路径，统一取 basename
        get_filename_component(_dest_name "${_dest_raw}" NAME)
        get_filename_component(_src_name "${_src_path}" NAME)
        if(_src_name STREQUAL _dest_name)
            install(FILES "${_src_path}" DESTINATION "${INSTALL_LIBDIR}")
            message(STATUS "  Will install dependency ${LIB_LABEL}: ${_dest_name}")
        else()
            # 去引用真实文件、以 SONAME 短名落盘（单副本）；cp 失败必须硬报错
            # （execute_process 默认不检查返回码，静默缺库不可接受）。
            install(CODE "
                execute_process(COMMAND bash -c \"
                    cp -L '${_src_path}' '\$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/${INSTALL_LIBDIR}/${_dest_name}'
                \" RESULT_VARIABLE _cp_rc)
                if(NOT _cp_rc EQUAL 0)
                    message(FATAL_ERROR \"cp -L ${_src_path} -> ${_dest_name} failed: \${_cp_rc}\")
                endif()
                message(STATUS \"  Installed ${LIB_LABEL} SONAME: ${_dest_name} (from ${_src_name})\")
            ")
        endif()
    endforeach()
endfunction()

install_llvm_deps("libLLVM.so.22*" "LLVM runtime")
install_llvm_deps("libz.so.*" "zlib")
install_llvm_deps("libzstd.so.*" "zstd")
install_llvm_deps("libxml2.so.*" "libxml2")
install_llvm_deps("libiconv.so.*" "iconv")
install_llvm_deps("libicuuc.so.*" "ICU uc")
install_llvm_deps("libicudata.so.*" "ICU data")

file(GLOB _vta_sim_libs "${TVM_BUILD_DIR}/vta/vta_hw/lib/libvta_fsim*.so")
foreach(_vlib ${_vta_sim_libs})
    if(EXISTS "${_vlib}")
        install(FILES "${_vlib}" DESTINATION "${INSTALL_LIBDIR}")
        get_filename_component(_vlib_name "${_vlib}" NAME)
        message(STATUS "  Will install VTA sim lib: ${_vlib_name}")
    endif()
endforeach()

set(VTA_NUITKA_OUT "${NUITKA_OUTPUT_DIR}/vta_out")
file(GLOB VTA_NUITKA_SO LIST_DIRECTORIES false "${VTA_NUITKA_OUT}/vta.cpython-*.so")
if(VTA_NUITKA_SO)
    install(FILES ${VTA_NUITKA_SO} DESTINATION ".")
    foreach(_f ${VTA_NUITKA_SO})
        message(STATUS "  Will install Nuitka vta module: ${_f}")
    endforeach()
else()
    message(FATAL_ERROR "vta Nuitka module not found at ${VTA_NUITKA_OUT}")
endif()

file(GLOB XMN_NUITKA_SO LIST_DIRECTORIES false "${XMN_NUITKA_OUT}/xmnn.cpython-*.so")
if(XMN_NUITKA_SO)
    install(FILES ${XMN_NUITKA_SO} DESTINATION ".")
    foreach(_f ${XMN_NUITKA_SO})
        message(STATUS "  Will install Nuitka xmnn module: ${_f}")
    endforeach()
else()
    message(FATAL_ERROR "xmnn Nuitka module not found at ${XMN_NUITKA_OUT}")
endif()

set(XMN_PKG_DIR "${XMN_PYTHON_DIR}/xmnn")

foreach(_dname tools_cpp fonts)
    set(_src "${XMN_PKG_DIR}/${_dname}")
    if(EXISTS "${_src}")
        install(DIRECTORY "${_src}/" DESTINATION "xmnn/${_dname}" USE_SOURCE_PERMISSIONS)
        message(STATUS "  Will install xmnn/${_dname} -> xmnn/${_dname}/ (USE_SOURCE_PERMISSIONS)")
    else()
        message(FATAL_ERROR "xmnn/${_dname} not found at ${_src}")
    endif()
endforeach()

# install(DIRECTORY) 会跳过 0 字节空文件（源 autolibs/ 下 .log 均为空），wheel
# 打包时也会过滤空文件，导致 xmnn/autolibs 在 wheel 中缺失。这里用 cp 复制整个
# autolibs 目录，并额外写入一个非空占位文件，确保目录结构完整进入 wheel。
set(AUTOLIBS_SRC "${XMN_PKG_DIR}/autolibs")
if(EXISTS "${AUTOLIBS_SRC}")
    install(CODE "
        execute_process(COMMAND bash -c \"
            set -e
            SRC='${AUTOLIBS_SRC}'
            DST='\$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/xmnn/autolibs'
            if [ -d \\\"\\$DST\\\" ]; then rm -rf \\\"\\$DST\\\" ; fi
            mkdir -p \\\"\\$DST\\\"
            cp -a \\\"\\$SRC/.\\\" \\\"\\$DST/\\\"
            # 写入非空占位文件，确保目录在 wheel 中非空保留（wheel 会过滤空文件）
            printf 'XMNN autolibs placeholder\\n' > \\\"\\$DST/.xmnn_autolibs_keep\\\"
            echo '  installed xmnn/autolibs (cp -a + placeholder)'
        \")
    ")
    message(STATUS "  Will install xmnn/autolibs via cp -a + placeholder")
else()
    message(FATAL_ERROR "xmnn/autolibs not found at ${AUTOLIBS_SRC}")
endif()

install(DIRECTORY "${TVM_ROOT_DIR}/vta/vta_hw/config"
    DESTINATION "vta_hw"
    FILES_MATCHING
    PATTERN "*.py"
    PATTERN "*.json"
)
message(STATUS "  Will install vta_hw/config directory")

install(DIRECTORY "${TVM_ROOT_DIR}/python/tvm/relay/std"
    DESTINATION "tvm/relay"
    FILES_MATCHING
    PATTERN "*.rly"
)
message(STATUS "  Will install tvm/relay/std data directory")

find_program(PATCHELF_EXECUTABLE patchelf)

if(PATCHELF_EXECUTABLE)
  message(STATUS "  patchelf found: ${PATCHELF_EXECUTABLE}")
  install(CODE "
    execute_process(COMMAND bash -c \"
      set -e
      LIBDIR='\$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/${INSTALL_LIBDIR}'
      echo \\\"  patchelf: Setting RPATH to \\\\\\$ORIGIN for all libs in \\\$LIBDIR\\\"
      for lib in \\\"\\\$LIBDIR\\\"/*.so*; do
        if [ -f \\\"\\\$lib\\\" ]; then
          ${PATCHELF_EXECUTABLE} --set-rpath '\\\$ORIGIN' \\\"\\\$lib\\\"
          echo \\\"    patchelf: \\\$(basename \\\"\\\$lib\\\") -> RPATH=\\\$ORIGIN\\\"
        fi
      done
      echo '  patchelf: RPATH set successfully on all libraries'
    \" RESULT_VARIABLE _patchelf_result)
    if(NOT _patchelf_result EQUAL 0)
      message(WARNING \"patchelf command failed with result: \${_patchelf_result}\")
    endif()
  ")
else()
  message(FATAL_ERROR "patchelf not found! Cannot set self-contained RPATH on _libs libraries")
endif()

install(CODE "
  execute_process(COMMAND bash -c \"
    set -e
    BINDIR='\$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/xmnn/tools_cpp/bin'
    if [ -d \\\"\\$BINDIR\\\" ]; then
      find \\\"\\$BINDIR\\\" -type f -exec chmod +x {} \\\\;
      echo '  chmod +x: all files in xmnn/tools_cpp/bin/ are now executable'
    fi
  \")
")

message(STATUS "XMNN CMake configuration complete.")

# WindowsRuntimeDlls.cmake — Reusable WIN32 IMPORTED DLL resolution & copy utilities
#
# Extract from caffe-ffi build system (2026-08-01).
# Provides generic CMake functions to resolve DLL paths for WIN32 IMPORTED SHARED
# targets and copy runtime dependencies alongside executables.
#
# ## Anti-pattern fixed
# Many CMake package configs (e.g. tvm-ffi, protobuf on conda) only set
# IMPORTED_IMPLIB (.lib) on WIN32 and leave IMPORTED_LOCATION (.dll) unset.
# Using $<TARGET_FILE:dep> in a POST_BUILD command then silently produces an
# empty string, so `copy_if_different` does nothing and the executable crashes
# at startup with 0xC0000135 (DLL_NOT_FOUND) or 0xC0000139 (ENTRY_POINT_NOT_FOUND)
# when a stale DLL is picked up from PATH.
#
# ## Key insight: search-order = priority
# When collecting DLLs from multiple search directories, `copy_if_different`
# executes commands in the order they are added. "Last writer wins" — the last
# copy command for a given DLL name overwrites earlier copies. Therefore,
# highest-priority directories (e.g. active conda env) MUST come LAST in the
# search list so they override stale DLLs from fallback paths.
#
# ## Public functions
#   win32_resolve_imported_dll(<imported_target> <out_var>)
#       Resolve actual .dll path for a WIN32 IMPORTED SHARED target.
#       Returns empty string if resolution fails.
#
#   win32_copy_target_dll(<target> <dependency_target>)
#       Copy a single dependency target's DLL to <target>'s output directory.
#       Handles both IMPORTED (via win32_resolve_imported_dll) and locally-built
#       targets (via $<TARGET_FILE>). Emits WARNING on resolution failure
#       instead of silently skipping.
#
#   win32_copy_dlls_from_dirs(<target> [dirs...])
#       Copy DLLs matching globs from given directories. Last directory in the
#       list has highest priority (last-writer-wins). Provide glob patterns via
#       WIN32_DLL_GLOBS variable before calling, or pass extra args as globs.
#
#   win32_collect_conda_bin_dirs(<out_var>)
#       Collect conda environment Library/bin directories from CONDA_PREFIX,
#       Python3_ROOT_DIR, and PYTHON_ROOT_DIR into <out_var>.
#
# ## Usage example
#   include(WindowsRuntimeDlls)
#   win32_collect_conda_bin_dirs(CONDA_DLL_DIRS)
#   add_executable(my_app main.cpp)
#   target_link_libraries(my_app PRIVATE some_imported::lib)
#   win32_copy_target_dll(my_app some_imported::lib)
#   win32_copy_dlls_from_dirs(my_app
#       "${Protobuf_DIR}/../../../bin" "${Protobuf_DIR}/../../bin"
#       ${CONDA_DLL_DIRS}
#       GLOBS "absl_*.dll" "libprotobuf*.dll" "utf8_range*.dll"
#   )

if(WIN32)

# ── Internal: resolve a WIN32 IMPORTED target's DLL path ──
#
# Strategy (in order, first match wins):
#   1. IMPORTED_LOCATION
#   2. IMPORTED_LOCATION_<CONFIG> (DEBUG/RELEASE/RELWITHDEBINFO/MINSIZEREL)
#   3. Derive from IMPORTED_IMPLIB: replace .lib → .dll in same directory
#   4. Derive from IMPORTED_IMPLIB: check ../bin/<name>.dll (conda layout)
#   5. IMPORTED_IMPLIB_<CONFIG> variants of 3 & 4
function(win32_resolve_imported_dll dep_target out_dll_path_var)
  set(_dll_path "")

  # 1. IMPORTED_LOCATION
  get_target_property(_loc ${dep_target} IMPORTED_LOCATION)
  if(_loc AND EXISTS "${_loc}")
    set(_dll_path "${_loc}")
  endif()

  # 2. IMPORTED_LOCATION_<CONFIG>
  if(NOT _dll_path)
    foreach(_cfg DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
      get_target_property(_loc_cfg ${dep_target} IMPORTED_LOCATION_${_cfg})
      if(_loc_cfg AND EXISTS "${_loc_cfg}")
        set(_dll_path "${_loc_cfg}")
        break()
      endif()
    endforeach()
  endif()

  # 3 & 4. Derive from IMPORTED_IMPLIB
  if(NOT _dll_path)
    get_target_property(_implib ${dep_target} IMPORTED_IMPLIB)
    if(_implib AND EXISTS "${_implib}")
      get_filename_component(_dll_dir "${_implib}" DIRECTORY)
      get_filename_component(_dll_name_we "${_implib}" NAME_WE)
      set(_candidate "${_dll_dir}/${_dll_name_we}.dll")
      if(EXISTS "${_candidate}")
        set(_dll_path "${_candidate}")
      else()
        # conda layout: .lib in lib/, .dll in bin/ (sibling directory)
        get_filename_component(_dll_dir_parent "${_dll_dir}" DIRECTORY)
        set(_candidate2 "${_dll_dir_parent}/bin/${_dll_name_we}.dll")
        if(EXISTS "${_candidate2}")
          set(_dll_path "${_candidate2}")
        endif()
      endif()
    endif()
  endif()

  # 5. IMPORTED_IMPLIB_<CONFIG> variants
  if(NOT _dll_path)
    foreach(_cfg DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
      get_target_property(_implib_cfg ${dep_target} IMPORTED_IMPLIB_${_cfg})
      if(_implib_cfg AND EXISTS "${_implib_cfg}")
        get_filename_component(_dll_dir "${_implib_cfg}" DIRECTORY)
        get_filename_component(_dll_name_we "${_implib_cfg}" NAME_WE)
        set(_candidate "${_dll_dir}/${_dll_name_we}.dll")
        if(EXISTS "${_candidate}")
          set(_dll_path "${_candidate}")
          break()
        endif()
        get_filename_component(_dll_dir_parent "${_dll_dir}" DIRECTORY)
        set(_candidate2 "${_dll_dir_parent}/bin/${_dll_name_we}.dll")
        if(EXISTS "${_candidate2}")
          set(_dll_path "${_candidate2}")
          break()
        endif()
      endif()
    endforeach()
  endif()

  set(${out_dll_path_var} "${_dll_path}" PARENT_SCOPE)
endfunction()

# ── Copy a single DLL file to target output directory ──
function(win32_copy_dll_file target_name dll_path)
  if(NOT TARGET ${target_name})
    message(FATAL_ERROR "win32_copy_dll_file(): target '${target_name}' does not exist")
  endif()
  if(NOT dll_path)
    message(FATAL_ERROR "win32_copy_dll_file(): dll_path is empty for target '${target_name}'")
  endif()
  if(EXISTS "${dll_path}")
    add_custom_command(TARGET ${target_name} POST_BUILD
      COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${dll_path}"
        "$<TARGET_FILE_DIR:${target_name}>"
      COMMENT "Copying ${dll_path} to output directory"
    )
  endif()
endfunction()

# ── Copy a dependency target's DLL (handles IMPORTED vs local) ──
function(win32_copy_target_dll target_name dependency_target)
  if(NOT TARGET ${target_name})
    message(FATAL_ERROR "win32_copy_target_dll(): target '${target_name}' does not exist")
  endif()
  if(NOT TARGET ${dependency_target})
    message(FATAL_ERROR "win32_copy_target_dll(): dependency target '${dependency_target}' does not exist")
  endif()

  get_target_property(_is_imported ${dependency_target} IMPORTED)
  if(_is_imported)
    win32_resolve_imported_dll(${dependency_target} _resolved_dll)
    if(_resolved_dll)
      add_custom_command(TARGET ${target_name} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
          "${_resolved_dll}"
          "$<TARGET_FILE_DIR:${target_name}>"
        COMMENT "Copying ${dependency_target} DLL (${_resolved_dll}) to output directory"
      )
    else()
      message(WARNING
        "win32_copy_target_dll(): could not resolve DLL path for IMPORTED target "
        "'${dependency_target}'. Falling back to TARGET_FILE generator expression, "
        "which may fail on WIN32 if IMPORTED_LOCATION is not set."
      )
      add_custom_command(TARGET ${target_name} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
          "$<TARGET_FILE:${dependency_target}>"
          "$<TARGET_FILE_DIR:${target_name}>"
        COMMENT "Copying ${dependency_target} DLL to output directory (fallback)"
      )
    endif()
  else()
    add_custom_command(TARGET ${target_name} POST_BUILD
      COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "$<TARGET_FILE:${dependency_target}>"
        "$<TARGET_FILE_DIR:${target_name}>"
      COMMENT "Copying ${dependency_target} DLL to output directory"
    )
  endif()
endfunction()

# ── Collect conda Library/bin directories ──
function(win32_collect_conda_bin_dirs out_var)
  set(_dirs "")
  if(DEFINED ENV{CONDA_PREFIX})
    list(APPEND _dirs "$ENV{CONDA_PREFIX}/Library/bin")
  endif()
  if(Python3_ROOT_DIR)
    list(APPEND _dirs "${Python3_ROOT_DIR}/Library/bin")
  endif()
  if(PYTHON_ROOT_DIR)
    list(APPEND _dirs "${PYTHON_ROOT_DIR}/Library/bin")
  endif()
  list(REMOVE_DUPLICATES _dirs)
  set(${out_var} "${_dirs}" PARENT_SCOPE)
endfunction()

# ── Copy DLLs by glob patterns from search directories ──
#
# Usage:
#   win32_copy_dlls_from_dirs(<target> [dir1 dir2 ...] GLOBS "pattern1" "pattern2" ...)
#
# IMPORTANT: Directories are searched in order, and copy_if_different executes in
# order. LAST directory wins for duplicate DLL names. Put highest-priority
# directories LAST in the list.
function(win32_copy_dlls_from_dirs target_name)
  if(NOT TARGET ${target_name})
    message(FATAL_ERROR "win32_copy_dlls_from_dirs(): target '${target_name}' does not exist")
  endif()

  cmake_parse_arguments(_arg "" "" "GLOBS" ${ARGN})
  set(_dirs ${_arg_UNPARSED_ARGUMENTS})
  set(_globs ${_arg_GLOBS})

  if(NOT _globs)
    message(FATAL_ERROR "win32_copy_dlls_from_dirs(): no GLOBS specified")
  endif()

  foreach(_dll_dir ${_dirs})
    foreach(_glob ${_globs})
      file(GLOB _dlls "${_dll_dir}/${_glob}")
      foreach(_dll ${_dlls})
        if(EXISTS "${_dll}")
          add_custom_command(TARGET ${target_name} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
              "${_dll}"
              "$<TARGET_FILE_DIR:${target_name}>"
            COMMENT "Copying ${_dll} to output directory"
          )
        endif()
      endforeach()
    endforeach()
  endforeach()
endfunction()

endif()  # WIN32

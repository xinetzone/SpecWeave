# AutoCopyRuntimeDlls.cmake — One-call WIN32 runtime DLL auto-copy
#
# Built on top of WindowsRuntimeDlls.cmake. Provides a single function that
# recursively traverses a target's link dependencies and automatically copies
# all required third-party DLLs to the executable output directory.
#
# ## Quick start
#   include(WindowsRuntimeDlls)
#   include(AutoCopyRuntimeDlls)
#
#   add_executable(my_app main.cpp)
#   target_link_libraries(my_app PRIVATE ${THIRD_PARTY_LIBS})
#
#   # One call — copies all DLLs automatically:
#   auto_copy_runtime_dlls(my_app)
#
# ## Public functions
#   auto_copy_runtime_dlls(<target>
#       [SEARCH_DIRS dir1 dir2 ...]     # Extra DLL search directories
#       [GLOBS pattern1 pattern2 ...]   # Additional glob patterns for dir search
#       [EXTRA_TARGETS tgt1 tgt2 ...]   # Additional targets to copy (not in link deps)
#       [EXCLUDE_TARGETS tgt1 tgt2 ...] # Targets to skip
#       [QUIET]                         # Suppress info messages
#       [DRY_RUN]                       # Print what would be copied without copying
#   )
#
# ## What it does automatically
#   1. Recursively traverses the target's INTERFACE_LINK_LIBRARIES and
#      LINK_LIBRARIES to discover all dependency targets (IMPORTED or built)
#   2. For each SHARED_LIBRARY IMPORTED target, resolves the DLL via
#      win32_resolve_imported_dll() (handles IMPORTED_LOCATION / IMPORTED_IMPLIB
#      fallback chain)
#   3. For each locally-built SHARED target, uses $<TARGET_FILE> genex
#   4. Optionally glob-copies DLLs from SEARCH_DIRS (e.g. conda Library/bin,
#      Protobuf bin dirs) using "last directory wins" priority ordering
#   5. Skips static libraries, interface libraries, object libraries, and
#      targets already in EXCLUDE_TARGETS
#   6. De-duplicates DLL paths so the same DLL isn't copied multiple times
#
# ## Dependency traversal
# The traversal follows these CMake target properties:
#   - LINK_LIBRARIES (direct private/interface/public link deps)
#   - INTERFACE_LINK_LIBRARIES (transitive interface deps)
#   - Manually-specified EXTRA_TARGETS
# It stops at non-targets (library file paths, plain library names),
# excluded targets, and already-visited targets (cycle protection).
#
# ## Search directory ordering (CRITICAL)
# When using SEARCH_DIRS + GLOBS, directories listed LAST have highest priority.
# Copy commands execute in declaration order; copy_if_different's last write wins.
# Example (correct order for conda environments):
#   auto_copy_runtime_dlls(my_app
#       SEARCH_DIRS
#           "${Protobuf_DIR}/../../../bin"    # lowest priority (fallback)
#           "${Protobuf_DIR}/../../bin"      #
#           $ENV{CONDA_PREFIX}/Library/bin   # highest priority (active env wins)
#       GLOBS "absl_*.dll" "libprotobuf*.dll"
#   )

if(NOT WIN32)
  # On non-WIN32 platforms, provide no-op stubs so including this file is safe
  function(auto_copy_runtime_dlls target_name)
  endfunction()
  return()
endif()

# Ensure base module is available
include(${CMAKE_CURRENT_LIST_DIR}/WindowsRuntimeDlls.cmake)

# ── Internal: recursively collect link dependency targets ──
function(_autodll_collect_deps target_name _out_var _visited_var _exclude_set)
  # Already visited?
  list(FIND ${_visited_var} "${target_name}" _idx)
  if(NOT _idx EQUAL -1)
    return()
  endif()

  # Mark as visited
  list(APPEND ${_visited_var} "${target_name}")
  set(${_visited_var} "${${_visited_var}}" PARENT_SCOPE)

  # Not a CMake target? Skip (plain library name / file path)
  if(NOT TARGET ${target_name})
    return()
  endif()

  # Excluded?
  if(DEFINED ${_exclude_set}_${target_name})
    return()
  endif()

  # Add to result
  list(APPEND ${_out_var} "${target_name}")

  # Recurse into link libraries
  get_target_property(_link_libs ${target_name} LINK_LIBRARIES)
  if(_link_libs)
    foreach(_dep IN LISTS _link_libs)
      if(TARGET ${_dep})
        _autodll_collect_deps(${_dep} ${_out_var} ${_visited_var} ${_exclude_set})
        set(${_out_var} "${${_out_var}}" PARENT_SCOPE)
        set(${_visited_var} "${${_visited_var}}" PARENT_SCOPE)
      endif()
    endforeach()
  endif()

  # Recurse into interface link libraries (transitive)
  get_target_property(_iface_libs ${target_name} INTERFACE_LINK_LIBRARIES)
  if(_iface_libs)
    foreach(_dep IN LISTS _iface_libs)
      if(TARGET ${_dep})
        _autodll_collect_deps(${_dep} ${_out_var} ${_visited_var} ${_exclude_set})
        set(${_out_var} "${${_out_var}}" PARENT_SCOPE)
        set(${_visited_var} "${${_visited_var}}" PARENT_SCOPE)
      endif()
    endforeach()
  endif()

  set(${_out_var} "${${_out_var}}" PARENT_SCOPE)
endfunction()

# ── Internal: check if a target is a shared/DLL library that needs copying ──
function(_autodll_is_shared_dll target_name _out_var)
  set(_is_shared FALSE)

  get_target_property(_type ${target_name} TYPE)
  if(_type STREQUAL "SHARED_LIBRARY")
    set(_is_shared TRUE)
  elseif(_type STREQUAL "MODULE_LIBRARY")
    set(_is_shared TRUE)
  elseif(_type STREQUAL "IMPORTED_LIBRARY")
    # For imported targets, check if it's a shared lib (DLL on WIN32)
    get_target_property(_imported_loc ${target_name} IMPORTED_LOCATION)
    get_target_property(_imported_implib ${target_name} IMPORTED_IMPLIB)
    get_target_property(_imported_soname ${target_name} IMPORTED_SONAME)
    if(_imported_loc OR _imported_implib OR _imported_soname)
      # It points to a file — check extension
      foreach(_prop_val ${_imported_loc} ${_imported_implib} ${_imported_soname})
        if(_prop_val AND (_prop_val MATCHES "\\.(dll|DLL)$" OR _prop_val MATCHES "\\.(lib|LIB)$"))
          set(_is_shared TRUE)
          break()
        endif()
      endforeach()
    else()
      # IMPORTED target with no location/implib — check INTERFACE_LIB_TYPE or assume shared
      get_target_property(_iface_type ${target_name} TYPE)
      # IMPORTED_LIBRARY without explicit type: check if it has DLL-related props
      get_target_property(_dll_check ${target_name} IMPORTED_IMPLIB_${CMAKE_BUILD_TYPE})
      if(_dll_check)
        set(_is_shared TRUE)
      else()
        foreach(_cfg DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
          get_target_property(_icfg ${target_name} IMPORTED_IMPLIB_${_cfg})
          if(_icfg)
            set(_is_shared TRUE)
            break()
          endif()
        endforeach()
      endif()
    endif()
  endif()

  set(${_out_var} ${_is_shared} PARENT_SCOPE)
endfunction()

# ── Main public function: auto-copy all runtime DLLs for a target ──
function(auto_copy_runtime_dlls target_name)
  if(NOT TARGET ${target_name})
    message(FATAL_ERROR "auto_copy_runtime_dlls(): target '${target_name}' does not exist")
  endif()

  # Only meaningful for executables and shared libraries
  get_target_property(_tgt_type ${target_name} TYPE)
  if(NOT (_tgt_type STREQUAL "EXECUTABLE" OR _tgt_type STREQUAL "SHARED_LIBRARY"))
    message(DEBUG "auto_copy_runtime_dlls(): target '${target_name}' is ${_tgt_type}, skipping")
    return()
  endif()

  cmake_parse_arguments(_arg "QUIET;DRY_RUN" "" "SEARCH_DIRS;GLOBS;EXTRA_TARGETS;EXCLUDE_TARGETS" ${ARGN})

  # Build exclude set (for O(1) lookup)
  foreach(_excl IN LISTS _arg_EXCLUDE_TARGETS)
    set(_autodll_exclude_${_excl} TRUE)
  endforeach()

  # Collect all dependency targets recursively
  set(_all_deps "")
  set(_visited "")
  _autodll_collect_deps(${target_name} _all_deps _visited _autodll_exclude)

  # Add extra targets
  foreach(_extra IN LISTS _arg_EXTRA_TARGETS)
    if(TARGET ${_extra})
      list(FIND _visited "${_extra}" _idx)
      if(_idx EQUAL -1)
        list(APPEND _all_deps "${_extra}")
      endif()
    else()
      if(NOT _arg_QUIET)
        message(WARNING "auto_copy_runtime_dlls(): EXTRA_TARGETS entry '${_extra}' is not a target, skipping")
      endif()
    endif()
  endforeach()

  # Remove the target itself from dependency list
  list(REMOVE_ITEM _all_deps "${target_name}")
  list(REMOVE_DUPLICATES _all_deps)

  set(_copied_dlls "")
  set(_skipped_targets "")
  set(_copied_count 0)

  foreach(_dep IN LISTS _all_deps)
    _autodll_is_shared_dll(${_dep} _is_shared)
    if(NOT _is_shared)
      list(APPEND _skipped_targets "${_dep}")
      continue()
    endif()

    get_target_property(_dep_is_imported ${_dep} IMPORTED)

    if(_dep_is_imported)
      win32_resolve_imported_dll(${_dep} _dll_path)
      if(_dll_path AND EXISTS "${_dll_path}")
        list(FIND _copied_dlls "${_dll_path}" _dup_idx)
        if(_dup_idx EQUAL -1)
          if(_arg_DRY_RUN)
            message(STATUS "[auto_copy_dlls DRY_RUN] Would copy IMPORTED target '${_dep}': ${_dll_path}")
          else()
            win32_copy_dll_file(${target_name} "${_dll_path}")
          endif()
          list(APPEND _copied_dlls "${_dll_path}")
          math(EXPR _copied_count "${_copied_count} + 1")
        endif()
      else()
        if(NOT _arg_QUIET)
          message(WARNING
            "auto_copy_runtime_dlls(): could not resolve DLL for IMPORTED target '${_dep}'. "
            "The executable may fail at startup with 0xC0000135."
          )
        endif()
      endif()
    else()
      # Locally-built shared library — use TARGET_FILE genex
      list(FIND _copied_deps_build "${_dep}" _build_idx)
      if(_build_idx EQUAL -1)
        if(_arg_DRY_RUN)
          message(STATUS "[auto_copy_dlls DRY_RUN] Would copy built target '${_dep}' via TARGET_FILE")
        else()
          add_custom_command(TARGET ${target_name} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
              "$<TARGET_FILE:${_dep}>"
              "$<TARGET_FILE_DIR:${target_name}>"
            COMMENT "Copying ${_dep} DLL to output directory"
          )
        endif()
        set(_copied_deps_build "${_copied_deps_build};${_dep}")
        math(EXPR _copied_count "${_copied_count} + 1")
      endif()
    endif()
  endforeach()

  # Glob-copy from search directories (for DLLs not exposed as CMake targets,
  # e.g. transitive abseil DLLs, OpenBLAS runtime DLLs, etc.)
  if(_arg_SEARCH_DIRS AND _arg_GLOBS)
    foreach(_dll_dir IN LISTS _arg_SEARCH_DIRS)
      foreach(_glob IN LISTS _arg_GLOBS)
        file(GLOB _glob_dlls "${_dll_dir}/${_glob}")
        foreach(_dll IN LISTS _glob_dlls)
          if(EXISTS "${_dll}")
            get_filename_component(_dll_name "${_dll}" NAME)
            # Check if already queued by path or by filename
            set(_already_copied FALSE)
            foreach(_existing IN LISTS _copied_dlls)
              get_filename_component(_existing_name "${_existing}" NAME)
              if(_existing_name STREQUAL _dll_name)
                set(_already_copied TRUE)
                break()
              endif()
            endforeach()
            if(NOT _already_copied)
              if(_arg_DRY_RUN)
                message(STATUS "[auto_copy_dlls DRY_RUN] Would copy glob DLL '${_dll}'")
              else()
                add_custom_command(TARGET ${target_name} POST_BUILD
                  COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    "${_dll}"
                    "$<TARGET_FILE_DIR:${target_name}>"
                  COMMENT "Copying ${_dll_name} to output directory"
                )
              endif()
              list(APPEND _copied_dlls "${_dll}")
              math(EXPR _copied_count "${_copied_count} + 1")
            endif()
          endif()
        endforeach()
      endforeach()
    endforeach()
  elseif(_arg_SEARCH_DIRS AND NOT _arg_GLOBS)
    message(WARNING "auto_copy_runtime_dlls(): SEARCH_DIRS provided but no GLOBS specified; directory search will be skipped")
  endif()

  if(NOT _arg_QUIET)
    message(STATUS "auto_copy_runtime_dlls(${target_name}): ${_copied_count} DLL(s) queued for copy")
    if(_arg_DRY_RUN)
      message(STATUS "auto_copy_runtime_dlls(${target_name}): DRY_RUN mode — no files were actually copied")
    endif()
  endif()
endfunction()

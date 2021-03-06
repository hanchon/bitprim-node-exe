#
# Copyright (c) 2017-2018 Bitprim Inc.
#
# This file is part of Bitprim.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

cmake_minimum_required(VERSION 3.4)

# bitprim-node-exe
#==============================================================================
project(bitprim-node-exe
        VERSION 0.10.2
        LANGUAGES CXX C)

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

# Check for baseline language coverage in the compiler for the C++11 standard.
#------------------------------------------------------------------------------
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Process options.
#==============================================================================

# Implement --use-conan
#------------------------------------------------------------------------------
option(USE_CONAN "Use Conan Build Tool." OFF)
option(NO_CONAN_AT_ALL "Conan totally disabled." OFF)

# Implement --with_rpc
#------------------------------------------------------------------------------
option(WITH_RPC "Compile with RPC-ZMQ support." OFF)
if (WITH_RPC)
  add_definitions(-DBITPRIM_WITH_RPC)
endif()

if (NO_CONAN_AT_ALL)
  set(USE_CONAN OFF)
endif()

# Implement --with-litecoin.
#------------------------------------------------------------------------------
# option(WITH_LITECOIN "Compile with Litecoin support." OFF)

set(BITPRIM_BUILD_NUMBER "-" CACHE STRING "Specify the Bitprim Build Number.")

set(CURRENCY "BCH" CACHE STRING "Specify the Cryptocurrency (BCH|BTC|LTC).")

# -DBITPRIM_BUILD_NUMBER=\"-\"

if (${CURRENCY} STREQUAL "BCH")
  add_definitions(-DBITPRIM_CURRENCY_BCH)
  add_definitions(-DBITPRIM_CURRENCY_SYMBOL_STR="BCH")
  add_definitions(-DBITPRIM_CURRENCY_STR="Bitcoin Cash")
elseif (${CURRENCY} STREQUAL "BTC")
  add_definitions(-DBITPRIM_CURRENCY_BTC)
  add_definitions(-DBITPRIM_CURRENCY_SYMBOL_STR="BTC")
  add_definitions(-DBITPRIM_CURRENCY_STR="Bitcoin Legacy")
elseif (${CURRENCY} STREQUAL "LTC")
  add_definitions(-DBITPRIM_CURRENCY_LTC)
  add_definitions(-DBITPRIM_CURRENCY_SYMBOL_STR="LTC")
  add_definitions(-DBITPRIM_CURRENCY_STR="Litecoin")
else()
  message(FATAL_ERROR "Invalid Cryptocurrency: ${CURRENCY}")
endif()

message(STATUS "Bitprim: Cryptocurrency: ${CURRENCY}")

set(MICROARCHITECTURE "x86_64" CACHE STRING "Specify the Cryptocurrency (x86_64|...).")
message( STATUS "Bitprim: Compiling for ${MICROARCHITECTURE}")
add_definitions(-DBITPRIM_MICROARCHITECTURE=${MICROARCHITECTURE})
add_definitions(-DBITPRIM_MICROARCHITECTURE_STR="${MICROARCHITECTURE}")


# Conan infrastructure
#==============================================================================
if (EXISTS ${CMAKE_SOURCE_DIR}/bitprimbuildinfo.cmake)
    include(${CMAKE_SOURCE_DIR}/bitprimbuildinfo.cmake)
else()
    message( STATUS "bitprimbuildinfo doent exists")
endif()

# Check dependencies.
#==============================================================================
#------------------------------------------------------------------------------
if (NOT USE_CONAN)
  if (NOT TARGET bitprim-node)
    find_package(bitprim-node 0.10.2 REQUIRED)
  endif()

  if (WITH_RPC)
    # Require bitprim-rpc of at least version 0.10.2
    #------------------------------------------------------------------------------
    if (NOT TARGET bitprim-rpc)
      find_package(bitprim-rpc 0.10.2 REQUIRED)
    endif()
  endif()

endif()

# if (WITH_LITECOIN)
#   add_definitions(-DLITECOIN)
# endif()

# Set flags.
#==============================================================================
include(CheckCXXCompilerFlag)

# Including common functions
#------------------------------------------------------------------------------
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)
include(BitprimTools)


# Warn on all stuff.
#------------------------------------------------------------------------------
if (NOT MSVC)
  _add_c_compile_flag(-Wall _has_all_warning_flag)
else()
  _add_c_compile_flag(-W4 _has_all_warning_flag)
  add_definitions(-D_SCL_SECURE_NO_WARNINGS)
  add_definitions(-D_CRT_SECURE_NO_WARNINGS)
endif()

# Warn on extra stuff.
#------------------------------------------------------------------------------
if (NOT MSVC)
  _add_c_compile_flag(-Wextra _has_extra_warning_flag)
endif()

# Be really annoying.
#------------------------------------------------------------------------------
_add_c_compile_flag(-Wpedantic _has_pedantic_warning_flag)
if (_has_pedantic_warning_flag)
  _add_c_compile_flag(-pedantic _has_pedantic_flag)
endif()

# Conform to style.
#------------------------------------------------------------------------------
_add_cxx_compile_flag(-Wno-missing-braces _has_no_missing_braces_warning_flag)

# Conflict in stdlib under clang. Enabled in clang only.
#------------------------------------------------------------------------------
_add_cxx_compile_flag(-Wno-mismatched-tags _has_no_mismatched_tags_warning_flag)

# Clean up boost 1.55 headers. Enabled in gcc only.
#------------------------------------------------------------------------------
_add_c_compile_flag(-Wno-deprecated-declarations _has_no_deprecated_declarations_warning_flag)

# Protect stack.
#------------------------------------------------------------------------------
_add_link_flag(-fstack-protector _has_stack_protector_flag)

# Protect stack comprehensively.
#------------------------------------------------------------------------------
_add_link_flag(-fstack-protector-all _has_stack_protector_all_flag)

# Hide internal functions from external libs. Enabled in gcc only.
#------------------------------------------------------------------------------
_add_cxx_compile_flag(-fvisibility-hidden _has_visibility_hidden_flag)

# Hide inlines from external libs. Enabled in gcc only.
#------------------------------------------------------------------------------
_add_cxx_compile_flag(-fvisibility-inlines-hidden _has_visibility_inlines_hidden_flag)

# Target Windows Vista. Enabled in msvc only.
#------------------------------------------------------------------------------
if (MSVC)
  add_definitions(-D_WIN32_WINNT=0x0600)
endif()


# Build
#==============================================================================
add_executable(console.bn
        console/executor.cpp
        console/executor.hpp
        console/main.cpp)

# target_link_libraries(console.bn bitprim-node)

# target_compile_definitions(console.bn PUBLIC -DBITPRIM_BUILD_NUMBER="\\"${BITPRIM_BUILD_NUMBER}\\"")
target_compile_definitions(console.bn PUBLIC -DBITPRIM_BUILD_NUMBER="${BITPRIM_BUILD_NUMBER}")
target_compile_definitions(console.bn PUBLIC -DBCN_STATIC -DBCB_STATIC -DBCD_STATIC -DBCT_STATIC -DBC_STATIC)

if (NOT USE_CONAN)
  target_link_libraries(console.bn PUBLIC bitprim-node)
  if(WITH_RPC)
    target_link_libraries(console.bn PUBLIC bitprim-rpc)
  endif()
endif()

if (NOT NO_CONAN_AT_ALL)
  target_link_libraries(console.bn PUBLIC ${CONAN_LIBS})
endif()

if (USE_CONAN)
  if (MINGW)
    target_link_libraries(console.bn PUBLIC ws2_32 wsock32) #TODO(fernando): manage with Conan
  endif()
endif()

set_target_properties(
        console.bn PROPERTIES
        FOLDER "node"
        OUTPUT_NAME bn)






# Install
#==============================================================================
install(TARGETS console.bn
        RUNTIME DESTINATION bin)

# # Export
# #==============================================================================
# include(CMakePackageConfigHelpers)

# export(EXPORT bitprim-node
#         FILE "${CMAKE_CURRENT_BINARY_DIR}/bitprim-nodeTargets.cmake")
# export(PACKAGE bitprim-node)

# configure_file(bitprim-nodeConfig.cmake.in
#         "${CMAKE_CURRENT_BINARY_DIR}/bitprim-nodeConfig.cmake"
#         @ONLY)

# write_basic_package_version_file(
#         "${CMAKE_CURRENT_BINARY_DIR}/bitprim-nodeConfigVersion.cmake"
#         VERSION ${PROJECT_VERSION}
#         COMPATIBILITY AnyNewerVersion)

# install(
#         FILES
#         "${CMAKE_CURRENT_BINARY_DIR}/bitprim-nodeConfig.cmake"
#         "${CMAKE_CURRENT_BINARY_DIR}/bitprim-nodeConfigVersion.cmake"
#         DESTINATION ${_config_package_location})

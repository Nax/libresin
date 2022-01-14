cmake_minimum_required(VERSION 3.12)
project(libresin)

set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(ResinVersion)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

if (EXISTS "${CMAKE_SOURCE_DIR}/codegen")
  set(GENERATE_CODE ON)
else()
  set(GENERATE_CODE OFF)
endif()
add_subdirectory(src)

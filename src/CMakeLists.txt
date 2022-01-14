if (NOT MSVC)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -fomit-frame-pointer -fstrict-aliasing -fno-exceptions -fno-rtti")
else()
    string(REGEX REPLACE "/GR" "" CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")
    string(REGEX REPLACE "/W[0-4]" "/W3" CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")
    string(REGEX REPLACE "/EH[a-z]+" "" CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /EHs-c- /GR-")
    add_definitions(-D_HAS_EXCEPTIONS=0 -D_CRT_SECURE_NO_WARNINGS=1)
endif()

if (GENERATE_CODE)
  find_package(Python3 REQUIRED)

  set(REGISTRY_COMMIT "92ab62262a8ee313dfd5bbdbed00acbec96fe80c")
  set(REGISTRY_XML_GL "https://raw.githubusercontent.com/KhronosGroup/OpenGL-Registry/${REGISTRY_COMMIT}/xml/gl.xml")
  set(REGISTRY_XML_WGL "https://raw.githubusercontent.com/KhronosGroup/OpenGL-Registry/${REGISTRY_COMMIT}/xml/wgl.xml")

  set(XML_DIR "${CMAKE_BINARY_DIR}/xml/${REGISTRY_COMMIT}")
  set(XML_GL  "${XML_DIR}/gl.xml")
  set(XML_WGL "${XML_DIR}/wgl.xml")

  set(GENERATED_SOURCE_DIR "${CMAKE_BINARY_DIR}/gen/src")
  set(GENERATED_INCLUDE_DIR "${CMAKE_BINARY_DIR}/gen/include")

  make_directory("${XML_DIR}")
  make_directory("${GENERATED_SOURCE_DIR}")
  make_directory("${GENERATED_INCLUDE_DIR}/resin")

  set(CODEGEN_PY  "${CMAKE_SOURCE_DIR}/codegen/codegen.py")
  set(GL_H_IN     "${CMAKE_SOURCE_DIR}/codegen/gl.h.in")
  set(GL_H        "${GENERATED_INCLUDE_DIR}/resin/gl.h")
  set(WGL_H_IN    "${CMAKE_SOURCE_DIR}/codegen/wgl.h.in")
  set(WGL_H       "${GENERATED_INCLUDE_DIR}/resin/wgl.h")

  set(LOADER_GENERIC_C_IN "${CMAKE_SOURCE_DIR}/codegen/loader_generic.c.in")
  set(LOADER_GENERIC_C    "${GENERATED_SOURCE_DIR}/loader_generic.c")

  if (NOT EXISTS "${XML_GL}")
    file(DOWNLOAD "${REGISTRY_XML_GL}" "${XML_GL}" SHOW_PROGRESS)
  endif()

  if (NOT EXISTS "${XML_WGL}")
    file(DOWNLOAD "${REGISTRY_XML_WGL}" "${XML_WGL}" SHOW_PROGRESS)
  endif()

  add_custom_command(
    OUTPUT
      "${GL_H}"
      "${WGL_H}"
      "${LOADER_GENERIC_C}"
    DEPENDS
      "${CODEGEN_PY}"
      "${XML_GL}"
      "${XML_WGL}"
      "${GL_H_IN}"
      "${WGL_H_IN}"
      "${LOADER_GENERIC_C_IN}"
    COMMAND
      "${Python3_EXECUTABLE}" "${CODEGEN_PY}" "${CMAKE_SOURCE_DIR}/codegen" "${XML_DIR}" "${GENERATED_INCLUDE_DIR}/resin" "${GENERATED_SOURCE_DIR}"
    COMMENT
      "Generating code"
    VERBATIM
  )
  set(ROOT "${CMAKE_BINARY_DIR}/gen/")
else()
  set(ROOT "${CMAKE_SOURCE_DIR}")
endif()

if (WIN32)
  set(CMAKE_DEBUG_POSTFIX d)
endif()

make_directory("${CMAKE_BINARY_DIR}/include/resin")
configure_file("${CMAKE_SOURCE_DIR}/src/config.h.in" "${CMAKE_BINARY_DIR}/include/resin/config.h")
set(SOURCES
  "${CMAKE_BINARY_DIR}/include/resin/config.h"
  "${ROOT}/include/resin/gl.h"
  "${ROOT}/src/loader_generic.c"
  support_common.c
)

if (WIN32)
  list(APPEND SOURCES "${CMAKE_SOURCE_DIR}/src/support_win32.c")
endif()

add_library(libresin STATIC ${SOURCES})
if (NOT WIN32)
  set_target_property(libresin OUTPUT_NAME "resin")
endif()
include_directories("${CMAKE_SOURCE_DIR}/include" "${CMAKE_BINARY_DIR}/include" "${CMAKE_BINARY_DIR}/gen/include")

install(TARGETS libresin ARCHIVE DESTINATION lib)
install(
  FILES
    "${CMAKE_BINARY_DIR}/include/resin/config.h"
    "${CMAKE_SOURCE_DIR}/include/resin/common.h"
    "${CMAKE_SOURCE_DIR}/include/resin/resin.h"
    "${ROOT}/include/resin/gl.h"
    "${ROOT}/include/resin/wgl.h"
  DESTINATION
    "include/resin"
)

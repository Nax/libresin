if (GENERATE_CODE)
  find_package(Python3 REQUIRED)

  set(REGISTRY_COMMIT "92ab62262a8ee313dfd5bbdbed00acbec96fe80c")
  set(REGISTRY_XML_GL "https://raw.githubusercontent.com/KhronosGroup/OpenGL-Registry/${REGISTRY_COMMIT}/xml/gl.xml")

  set(XML_DIR "${CMAKE_BINARY_DIR}/xml/${REGISTRY_COMMIT}")
  set(XML_GL "${XML_DIR}/gl.xml")

  set(GENERATED_SOURCE_DIR "${CMAKE_BINARY_DIR}/src")
  set(GENERATED_INCLUDE_DIR "${CMAKE_BINARY_DIR}/include")

  make_directory("${XML_DIR}")
  make_directory("${GENERATED_SOURCE_DIR}")
  make_directory("${GENERATED_INCLUDE_DIR}/resin")

  set(CODEGEN_PY  "${CMAKE_SOURCE_DIR}/codegen/codegen.py")
  set(GL_H_IN     "${CMAKE_SOURCE_DIR}/codegen/gl.h.in")
  set(GL_H        "${GENERATED_INCLUDE_DIR}/resin/gl.h")

  if (NOT EXISTS "${XML_GL}")
    file(DOWNLOAD "${REGISTRY_XML_GL}" "${XML_GL}" SHOW_PROGRESS)
  endif()

  add_custom_command(
    OUTPUT
      "${GL_H}"
    DEPENDS
      "${CODEGEN_PY}"
      "${XML_GL}"
      "${GL_H_IN}"
    COMMAND
      "${Python3_EXECUTABLE}" "${CODEGEN_PY}" "${GL_H_IN}" "${XML_GL}" "${GL_H}"
    COMMENT
      "Generating resin/gl.h"
    VERBATIM
  )
  set(ROOT "${CMAKE_BINARY_DIR}")
else()
  set(ROOT "${CMAKE_SOURCE_DIR}")
endif()

set(SOURCES
  "${ROOT}/include/resin/gl.h"
  resin.c
)

if (WIN32)
  list(APPEND SOURCES "${CMAKE_SOURCE_DIR}/src/loader_win32.c")
endif()

add_library(libresin STATIC ${SOURCES})
if (NOT WIN32)
  set_target_property(libresin OUTPUT_NAME "resin")
endif()
include_directories("${CMAKE_SOURCE_DIR}/include" "${CMAKE_BINARY_DIR}/include")

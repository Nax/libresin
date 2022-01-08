find_package(Python3 REQUIRED)

set(REGISTRY_COMMIT "92ab62262a8ee313dfd5bbdbed00acbec96fe80c")
set(REGISTRY_XML_GL "https://raw.githubusercontent.com/KhronosGroup/OpenGL-Registry/${REGISTRY_COMMIT}/xml/gl.xml")

set(XML_DIR "${CMAKE_BINARY_DIR}/xml/${REGISTRY_COMMIT}")
set(XML_GL "${XML_DIR}/gl.xml")

make_directory("${XML_DIR}")
if (NOT EXISTS "${XML_GL}")
  file(DOWNLOAD "${REGISTRY_XML_GL}" "${XML_GL}" SHOW_PROGRESS)
endif()

#ifndef RESIN_COMMON_H
#define RESIN_COMMON_H 1

#include <stdint.h>

#if defined(WIN32)
# define RESIN_APIENTRY __stdcall
#else
# define RESIN_APIENTRY
#endif

#if !defined(GLAPI)
# if defined(__cplusplus)
#  define GLAPI extern "C"
# else
#  define GLAPI extern
# endif
#endif

typedef unsigned int    GLenum;
typedef unsigned char   GLboolean;
typedef unsigned int    GLbitfield;
typedef void            GLvoid;
typedef int8_t          GLbyte;
typedef uint8_t         GLubyte;
typedef int16_t         GLshort;
typedef uint16_t        GLushort;
typedef int             GLint;
typedef unsigned int    GLuint;
typedef int32_t         GLclampx;
typedef int             GLsizei;
typedef float           GLfloat;
typedef float           GLclampf;
typedef double          GLdouble;
typedef double          GLclampd;
typedef void*           GLeglClientBufferEXT;
typedef void*           GLeglImageOES;
typedef char            GLchar;
typedef char            GLcharARB;

#if defined(__APPLE__)
typedef void*           GLhandleARB;
#else
typedef unsigned int    GLhandleARB;
#endif

typedef uint16_t        GLhalf;
typedef uint16_t        GLhalfARB;
typedef int32_t         GLfixed;
typedef intptr_t        GLintptr;
typedef intptr_t        GLintptrARB;

#if defined(_MSC_VER)
typedef long            GLsizeiptr;
typedef long            GLsizeiptrARB;
#else
typedef ssize_t         GLsizeiptr;
typedef ssize_t         GLsizeiptrARB;
#endif

typedef int64_t         GLint64;
typedef int64_t         GLint64EXT;
typedef uint64_t        GLuint64;
typedef uint64_t        GLuint64EXT;

#endif

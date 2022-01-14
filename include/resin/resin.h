#ifndef RESIN_RESIN_H
#define RESIN_RESIN_H 1

#if defined(__cplusplus)
# define RESIN_API extern "C"
#else
# define RESIN_API
#endif

RESIN_API void  resinReset(void);
RESIN_API void* resinGetProcAddr(const char* name);
RESIN_API int   resinIsExtensionAvailable(const char* name);

#if defined(_WIN32)
RESIN_API int   resinIsExtensionAvailableWGL(const char* name);
#endif

#endif

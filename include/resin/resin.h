#ifndef RESIN_RESIN_H
#define RESIN_RESIN_H

#if defined(__cplusplus)
# define RESIN_API extern "C"
#else
# define RESIN_API
#endif

RESIN_API void* resin_GetProcAddr(const char* name);

#endif

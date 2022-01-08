#include <resin/resin.h>
#define WIN32_LEAN_AND_MEAN 1
#define VC_EXTRALEAN 1
#include <windows.h>

typedef void* (__stdcall *PFNWGLGETPROCADDRPROC)(const char* name);

static HMODULE sLibOpenGL;
static PFNWGLGETPROCADDRPROC sGetProcAddress;

RESIN_API void* resin_GetProcAddr(const char* name)
{
    void* proc;

    if (!sLibOpenGL)
    {
        sLibOpenGL = LoadLibraryA("OPENGL32");
        sGetProcAddress = (PFNWGLGETPROCADDRPROC)GetProcAddress(sLibOpenGL, "wglGetProcAddress");
    }

    proc = sGetProcAddress(name);
    if (proc == (void*)0 || proc == (void*)1 || proc == (void*)2 || proc == (void*)-1)
        proc = GetProcAddress(sLibOpenGL, name);
    return proc;
}

#include <resin/resin.h>
#define WIN32_LEAN_AND_MEAN 1
#define VC_EXTRALEAN 1
#include <windows.h>

typedef void*       (__stdcall *PFNWGLGETPROCADDRPROC)(const char* name);
typedef const char* (__stdcall *PFNWGLGETEXTENSIONSSTRINGARBPROC)(HDC dc);
typedef HDC         (__stdcall *PFNWGLGETCURRENTDCPROC)(void);

static HMODULE sLibOpenGL;

static PFNWGLGETPROCADDRPROC            sWglGetProcAddress;
static PFNWGLGETEXTENSIONSSTRINGARBPROC sWglGetExtensionsStringARB;
static PFNWGLGETCURRENTDCPROC           sWglGetCurrentDC;

RESIN_API int resinCheckExtensionString(const char* list, const char* name);

RESIN_API void* resinGetProcAddr(const char* name)
{
    void* proc;

    if (!sLibOpenGL)
    {
        sLibOpenGL = LoadLibraryA("OPENGL32");
        sWglGetProcAddress = (PFNWGLGETPROCADDRPROC)GetProcAddress(sLibOpenGL, "wglGetProcAddress");
    }

    proc = sWglGetProcAddress(name);
    if (proc == (void*)0 || proc == (void*)1 || proc == (void*)2 || proc == (void*)3 || proc == (void*)-1)
        proc = GetProcAddress(sLibOpenGL, name);
    return proc;
}

RESIN_API int resinIsExtensionAvailableWGL(const char* name)
{
    HDC dc;
    const char* str;

    if (!sWglGetCurrentDC)
    {
        sWglGetCurrentDC = (PFNWGLGETCURRENTDCPROC)resinGetProcAddr("wglGetCurrentDC");
        sWglGetExtensionsStringARB = (PFNWGLGETEXTENSIONSSTRINGARBPROC)resinGetProcAddr("wglGetExtensionsStringARB");
    }
    if (!sWglGetExtensionsStringARB)
        return 0;

    dc = sWglGetCurrentDC();
    str = sWglGetExtensionsStringARB(dc);
    return resinCheckExtensionString(str, name);
}

BOOL APIENTRY resin_impl2_wglMakeAssociatedContextCurrentAMD(HGLRC hglrc);
BOOL APIENTRY resin_impl2_wglMakeContextCurrentARB(HDC hDrawDC, HDC hReadDC, HGLRC hglrc);
BOOL APIENTRY resin_impl2_wglMakeContextCurrentEXT(HDC hDrawDC, HDC hReadDC, HGLRC hglrc);
BOOL APIENTRY resin_impl2_wglMakeCurrent(HDC hDc, HGLRC newContext);

BOOL APIENTRY resin_impl_wglMakeAssociatedContextCurrentAMD(HGLRC hglrc)
{
    resinReset();
    return resin_impl2_wglMakeAssociatedContextCurrentAMD(hglrc);
}

BOOL APIENTRY resin_impl_wglMakeContextCurrentARB(HDC hDrawDC, HDC hReadDC, HGLRC hglrc)
{
    resinReset();
    return resin_impl2_wglMakeContextCurrentARB(hDrawDC, hReadDC, hglrc);
}

BOOL APIENTRY resin_impl_wglMakeContextCurrentEXT(HDC hDrawDC, HDC hReadDC, HGLRC hglrc)
{
    resinReset();
    return resin_impl2_wglMakeContextCurrentEXT(hDrawDC, hReadDC, hglrc);
}

BOOL APIENTRY resin_impl_wglMakeCurrent(HDC hDc, HGLRC newContext)
{
    resinReset();
    return resin_impl2_wglMakeCurrent(hDc, newContext);
}

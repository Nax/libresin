#include <string.h>
#include <resin/resin.h>
#include <resin/gl.h>

RESIN_API int resinCheckExtensionString(const char* list, const char* name)
{
    size_t len;
    char c;

    len = strlen(name);
    for (;;)
    {
        if (*list == 0)
            return 0;
        if (strncmp(list, name, len) == 0)
        {
            list += len;
            c = *list;
            if (c == ' ' || c == 0)
                return 1;
        }
        for (;;)
        {
            c = *list++;
            if (c == ' ' || c == 0)
                break;
        }
    }
}

RESIN_API int resinIsExtensionAvailable(const char* name)
{
    GLint tmp;
    const char* str;

    glGetIntegerv(GL_MAJOR_VERSION, &tmp);
    if (tmp >= 3)
    {
        glGetIntegerv(GL_NUM_EXTENSIONS, &tmp);
        for (GLint i = 0; i < tmp; ++i)
        {
            str = glGetStringi(GL_EXTENSIONS, i);
            if (strcmp(name, str) == 0)
                return 1;
        }
    }
    else
    {
        str = glGetString(GL_EXTENSIONS);
        if (resinCheckExtensionString(str, name))
            return 1;
    }

#if defined(_WIN32)
    return resinIsExtensionAvailableWGL(name);
#else
    return 0;
#endif
}

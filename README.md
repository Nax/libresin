# libresin

A modern OpenGL loader, inspired by [libepoxy](https://github.com/anholt/libepoxy).

## Building

Build it like any cmake project. For example, on Unix-like systems:

    mkdir build
    cd build
    cmake .. -DCMAKE_BUILD_TYPE=Release
    make -j32
    sudo make install

Note that this project uses python during build and fetch some XML files from the internet during the build.  
The source code release files have these steps pre-generated. Prefer to use these unless you want to work on libresin itself.

## License

This project is available under the [MIT license](LICENSE).

## Author

Made by Maxime Bacoux "[Nax](https://github.com/Nax)".  
Strongly influenced by [libepoxy](https://github.com/anholt/libepoxy) from [anholt](https://github.com/anholt).

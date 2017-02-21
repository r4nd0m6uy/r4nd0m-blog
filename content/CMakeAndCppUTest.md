Title: CMake and CppUTest
Date: 2017-02-21 12:00
Category: Programming
Tags: unit test, tutorial, cmake

When implementing a new feature or fixing bugs, I like having a quick
feedback to make sure that my changes didn't break the code. This is why
I usually write unit tests and execute them during the build process. In
this article I want to give some pointers to make my favorite tools work
well together that are the [CppUtest](https://cpputest.github.io/) unit
testing framework and the [cmake](https://cmake.org/) build utility.

I like **cmake** because it creates excellent 
[Makefiles](https://www.gnu.org/software/make/manual/make.html) that is
usually difficult to get right. As a developper, it compiles only files
that changed that is very efficient when your recompiling your tests
very frequently. cmake is supported by many
[build systems]({filename}/YoctoBrAndCo.md) that facilitates the
deployement on embedded targets and can be easily added to your
contineous integration process where you want to compile the unit tests
automatically.

There are many out the but **CppUTest** is a well proven unit test
framework. I like it because it has a mocking framework, a memory leak
detector and doesn't need other external libraries to compile.

# Installing cmake and CppUTest
Those tools should be available in your distribution, you should use
your package manager to install them. As long as it is decent enough, I
don't mind much about cmake version but I like working with the last
development version of CppUTest and maybe want to use different version
when compiling a stable release.

There are different ways to compile CppUTest but as long as we are
talking about cmake, I will use this way. The default installation path
is */usr/local* but as I want to host different version, I define the
prefix to */opt/cpputest-<GIT_VERSION>*:

    :::sh
    git clone https://github.com/cpputest/cpputest.git ; cd cpputest
    mkdir cmake-build ; cd cmake-build
    cmake ../ -DCMAKE_INSTALL_PREFIX:PATH=/opt/cpputest-$(git describe)
    make -j3

Once the compilation is done, you can run *make install* and make an
user friendly symbolic link to the last available version:

    :::sh
    sudo make install
    sudo ln -s /opt/cpputest-$(git describe) /opt/cpputest

To switch from a version to another, I just change the /opt/cpputest
symlink.

# The project structure
My favorite structure is having the sources and tests in separated
folders. I write a root CMakeLists.txt that can include what I want to
compile, it should be easy to build the application without the tests.
Here is a skeleton showing what your project would look like:

    :::txt
    .
    ├── CMakeLists.txt
    ├── README.md
    ├── src
    │   ├── CMakeLists.txt
    │   ├── main.cpp
    │   └── time
    │       ├── Bar.cpp
    │       ├── Bar.hpp
    │       ├── Foo.cpp
    │       ├── Foo.hpp
    │       ├── IFoo.cpp
    │       └── IFoo.hpp
    └── tests
        ├── CMakeLists.txt
        ├── BarTest.cpp
        ├── FooTest.cpp
        ├── main.cpp
        └── mocks
            ├── IFooMock.cpp
            └── IFooMOck.hpp

# CMakefile.txt
Now the intersting part is writing CMakeFiles. Here is what looks like
the root CMakeLists.txt:

    :::cmake
    # (1) CMake definitions, compiler flags and useful variables
    cmake_minimum_required(VERSION 3.7)
    project(cmakeCppUTestDemo)

    add_compile_options(-std=c++11 -Wall -Werror)

    set(APP_NAME fooApp)
    set(APP_LIB_NAME fooAppLib)
    
    # (2) Include application build instructions
    add_subdirectory(src)
    
    # (3) include tests build instructions   
    option(COMPILE_TESTS "Compile the tests" OFF)
    if(COMPILE_TESTS)
      add_subdirectory(tests)
    endif(COMPILE_TESTS)

**(1)**

First the usual cmake options, we need to define a project name and
decide which version of cmake we need. I also add some restrictive
compiliation flags and declare some variables that I can share between
both subprojects, the application and the tests.

**(2)**

Because making sure that the application compiles is an excellent test,
this is done all the time and include the sub cmakefile.

**(3)**

Compiling the unit tests is probably not a required step for everyone,
this is why I want to give explicitely the option to do it by passing
*COMPILE_TESTS=ON* to cmake.

# src/CMakefile.txt
Here is how looks the instruction to build the main application:

    :::cmake
    # (1) Build a library with my application sources
    set(APP_LIB_SOURCE
        IFoo.cpp
        Foo.cpp
        Bar.cpp
    )

    add_library(${APP_LIB_NAME} ${APP_LIB_SOURCE})

    # (2) Add main(..) to the application library to have something we can run
    add_executable(${APP_NAME} main.cpp)
    target_link_libraries(${APP_NAME} ${APP_LIB_NAME})

**(1)**

The trick is to use a separated main function from the application
sources, so it doesn't conflict with the main from the tests. We simply
compile here a static library that can be used when linking with the
tests or the main from the normal program.

**(2)**

As we have all the objects we need, we add the main file where we can
provide an entry point.

# tests/CMakefile.txt
Finally, how to build the unit tests that you wrote using CppUtest:

    :::cmake
    # (1) Look for installed version of CppUTest
    if(DEFINED ENV{CPPUTEST_HOME})
        message(STATUS "Using CppUTest home: $ENV{CPPUTEST_HOME}")
        set(CPPUTEST_INCLUDE_DIRS $ENV{CPPUTEST_HOME}/include)
        set(CPPUTEST_LIBRARIES $ENV{CPPUTEST_HOME}/lib)
        set(CPPUTEST_LDFLAGS CppUTest CppUTestExt)
    else()
        find_package(PkgConfig REQUIRED)
        pkg_search_module(CPPUTEST REQUIRED cpputest>=3.8)
        message(STATUS "Found CppUTest version ${CPPUTEST_VERSION}")
    endif()

    # (2) Our unit tests sources
    set(TEST_APP_NAME ${APP_NAME}_tests)
    set(TEST_SOURCES
        mocks/IFooMock.cpp
        FooTest.cpp
        BarTest.cpp
        main.cpp
    )

    # (3) Take care of include directories
    include_directories(${CPPUTEST_INCLUDE_DIRS} ../src/)
    link_directories(${CPPUTEST_LIBRARIES}
    
    # (4) Build the unit tests objects and link then with the app library
    add_executable(${TEST_APP_NAME} ${TEST_SOURCES})
    target_link_libraries(${TEST_APP_NAME} ${APP_LIB_NAME} ${CPPUTEST_LDFLAGS})

    # (5) Run the test once the build is done
    add_custom_command(TARGET ${TEST_APP_NAME} COMMAND ./${TEST_APP_NAME} POST_BUILD)

**(1)**

If the user has *CPPUTEST_HOME* set in his environment, we use it to
locate CppUTest installation. In case it is not provided, we use
pkgconfig to look for it in the system. The cmake process fails here if
CppUTest is not found or its version is too old.

**(2)**

Then we add all the sources required to compile the unit tests,
including the main function.

**(3)**

We have to define the include directory of our application source so the
compiler can find our headers files. We also have to take care of
CppUTest include directories variables we set previously.

**(4)**

Compile the unit test application by linking it with our library and
CppUTest.

**(5)**

Finally run the tests once it is built! If the unit test fails, the make
command will also fail, that gives us a quick feedback if everything is
fine!

# Compile the whole
To compile the application, proceed the usual cmake way:

    :::sh
    mkdir build ; cd build
    cmake ../
    make -j3

If you want to compile the unit tests, execute cmake with this
parameter:

    :::sh
    cmake -DCOMPILE_TESTS=ON ../

If you haven't installed cpputest or use a too old version, this error
will pop out:

    :::txt
    -- Checking for one of the modules 'cpputest>=3.8'
    CMake Error at /usr/share/cmake-3.7/Modules/FindPkgConfig.cmake:637 (message):
      None of the required 'cpputest>=3.8' found
    Call Stack (most recent call first):
      tests/CMakeLists.txt:8 (pkg_search_module)

You can install cpputest with your package manager or set the
*CPPUTEST_HOME* environment variables pointing to your last version:

    :::sh
    CPPUTEST_HOME=/opt/cpputest/ cmake -DCOMPILE_TESTS=ON ../

Once cmake ran correcly, you just need to run *make* to (re)build the
changes and run the unit tests:

    :::sh
    make -j3
    ...
    [100%] Linking CXX executable fooApp_tests
    ..................................................
    ..
    OK (52 tests, 52 ran, 112 checks, 0 ignored, 0 filtered out, 7 ms)

    [100%] Built target fooApp_tests

# Conclusion
Now you have a template that you can use it for your own project and be
efficient by having a quick feedback if something goes wrong!


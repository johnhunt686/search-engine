# search-engine
For build details and documentation see Build and Run


# Build and Run
## 'the search engine' - John
this must be compiled for the system to be tested on
eventually this will be on our deployed server and dependancies will be easier
there is a windows setup guide below (untested)

### API
the node.js server can be started with
```node server.js```
this will run on localhost:3000 and can be accesed like this
http://localhost:3000/search?q=test&setting1=fast
it will return json in a format that has yet to be determined
idk if you need the dependancies installed or not but you might need gdc and node? :3
this will run the compiled binaries for the c++ 

### Windows Setup Guide for search_engine.cpp (CMake + libpqxx)

##### Devleopment Environment:
- [Visual Studio](https://visualstudio.microsoft.com/)  
  - Select: **Desktop development with C++**
- [CMake](https://cmake.org/download/)
- [Git](https://git-scm.com/) (for vcpkg)

##### Install vcpkg
````powershell
git clone https://github.com/microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat
````

##### Install Dependancies
````.\vcpkg install libpqxx:x64-windows````
##### Configure Project
````cmake -S . -B build `
  -DCMAKE_TOOLCHAIN_FILE=C:/path/to/vcpkg/scripts/buildsystems/vcpkg.cmake````
##### Build & Run
````
cmake --build build
.\build\Debug\MyApp.exe
````



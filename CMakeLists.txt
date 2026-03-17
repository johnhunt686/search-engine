cmake_minimum_required(VERSION 3.14)

project(SearchEngine)

set(CMAKE_CXX_STANDARD 17)

find_package(PkgConfig REQUIRED)
pkg_check_modules(PQXX REQUIRED libpqxx)

add_executable(SearchEngine src/search_engine.cpp)

target_include_directories(SearchEngine PRIVATE ${PQXX_INCLUDE_DIRS})
target_link_libraries(SearchEngine PRIVATE ${PQXX_LIBRARIES})
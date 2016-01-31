cmake_minimum_required(VERSION 3.2)
project(opsisd)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES main.c opsisd.c opsisd.h serial.c serial.h)
add_executable(opsisd ${SOURCE_FILES})
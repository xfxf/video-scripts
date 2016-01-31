cmake_minimum_required(VERSION 3.4)
project(opsis)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")

set(OPSISD_SOURCE_FILES
    opsisd/main.c
    opsisd/opsisd.c
    opsisd/opsisd.h
    opsisd/serial.c
    opsisd/serial.h)

add_executable(opsisd ${OPSISD_SOURCE_FILES})


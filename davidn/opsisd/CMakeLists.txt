cmake_minimum_required(VERSION 3.4)

option(tests "Build all tests." OFF)         # cmake -Dtest=ON

set(PROJECT_NAME opsisd)
project(${PROJECT_NAME})

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")

if (APPLE)
    add_definitions(-DGTEST_USE_OWN_TR1_TUPLE)
    add_definitions(-D__GLIBCXX__)
endif (APPLE)

include_directories(LOCAL include)

set(OPSISD_SOURCE_FILES
        src/opsisd.c include/opsisd.h
        src/array.c include/array.h
        src/buffer.c include/buffer.h
        src/serial.c include/serial.h
        src/network.c include/network.h
        src/selector.c include/selector.h
        src/logging.c include/logging.h
        src/iodev.c include/iodev.h)

add_executable(opsisd src/main.c ${OPSISD_SOURCE_FILES})

####
# test support
####

if (tests)

    # add googletest gtest/gmock to test builds
    add_subdirectory( tests/googletest )
    enable_testing()

    include_directories( ${gtest_SOURCE_DIR}/include )
    include_directories( ${gmock_SOURCE_DIR}/include )

    ####
    # unit tests
    ####

    add_executable(runSerialUnitTests ${OPSISD_SOURCE_FILES}
            tests/serial/test_find_opsis_serial.cc)
    target_link_libraries(runSerialUnitTests gtest gtest_main)
    add_test(opsis_serial_interface runSerialUnitTests)

    add_executable(runMiscUnitTests ${OPSISD_SOURCE_FILES}
            tests/misc/test_logging.cc
            tests/misc/test_array.cc
            tests/misc/test_buffer.cc)

    target_link_libraries(runMiscUnitTests gtest gtest_main)

    add_test(misc_tests runMiscUnitTests)

endif()

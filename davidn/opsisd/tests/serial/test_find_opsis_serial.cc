//
// Created by David Nugent on 1/02/2016.
//


extern "C" {
#include "opsisd.h"
}
#include "gtest/gtest.h"

namespace {

    static const char portlist[] = "ttyACM*|/dev/ttyVIZ*|/dev/tty*";
    static const char host[] = "localhost";

    // struct ctrldev *find_opsis_serial_all(const struct opsisd_opts *opts);
    // void ctrldev_free(struct ctrldev *first_dev);
    // char *find_opsis_serial(const struct opsisd_opts *opts);

    struct opsisd_opts opts = {
        0,                                  // verbose
        0,                                  // daemonize
        115200,                             // baudrate
        portlist,                           // port
        host,                               // listen_addr
        8501,                               // listen_port

    };

    TEST(SerialFunctions, findOpsisSerialAll) {
        struct ctrldev *first_dev = find_opsis_serial_all(&opts);
        // assuming we are running on a unix like system
        EXPECT_NE((struct ctrldev *)0, first_dev);
    };

    TEST(SerialFunctions, findOpsisSerial) {
        char *ctrl_dev = find_opsis_serial(&opts);
        EXPECT_NE((char *)0, ctrl_dev);
    }

} // namespace


int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

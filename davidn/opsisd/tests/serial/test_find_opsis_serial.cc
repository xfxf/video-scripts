//
// Created by David Nugent on 1/02/2016.
//


extern "C" {
#include "opsisd.h"
}

#include "logging.h"
#include "gtest/gtest.h"

namespace {

    static const char portlist[] = "/dev/ttyVIZ*|ttyACM*|/dev/tty*";
    static const char host[] = "localhost";

    struct opsisd_opts opts = {
        V_NONE,                             // verbose
        0,                                  // logflags
        NULL,                               // logfile
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
        for (struct ctrldev *next = first_dev; next != NULL; next = next->next) {
            ASSERT_NE((char *)0, next->devname);
            EXPECT_EQ(0, access(next->devname, R_OK|W_OK));
        }
    };

    TEST(SerialFunctions, findOpsisSerial) {
        char *ctrl_dev = find_opsis_serial(&opts);
        EXPECT_NE((char *)0, ctrl_dev);
        EXPECT_EQ(0, access(ctrl_dev, R_OK|W_OK));
    }

} // namespace

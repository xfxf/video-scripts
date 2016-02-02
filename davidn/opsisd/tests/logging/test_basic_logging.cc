//
// Created by David Nugent on 2/02/2016.
//


extern "C" {
#include "logging.h"
}
#include "gtest/gtest.h"

namespace {

    TEST(LoggingFunctions, createAndRotateLog) {
        log_init(LOG_ECHO|LOG_SYNC, V_DEBUG, "logfile-%Y%M%D_%H%M%S.log");

        log_trace("This should not appear in the log");
        log_debug("This is a debug entry with a %s value %d", "test", 123);
        log_info("This is a message at log level '%s'", "info");
        log_critical("This is a critial message at log level, testing %d", 123);
        log_error("This is an error message!");
        log_fatal("This is a fatal error message...");
        const char *log_name1 = log_name();
        EXPECT_NE((const char *)0, log_name1);
        sleep(1);
        log_rotate();
        const char *log_name2 = log_name();
        EXPECT_NE((const char *)0, log_name2);
        EXPECT_NE(log_name1, log_name2);
        log_warning("Log name first = '%s', second = '%s'", log_name1, log_name2);
    };


} // namespace


int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

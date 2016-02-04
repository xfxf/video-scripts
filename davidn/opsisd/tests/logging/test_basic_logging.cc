//
// Created by David Nugent on 2/02/2016.
//


extern "C" {
#include "logging.h"
}
#include "gtest/gtest.h"

namespace {

    TEST(LoggingFunctions, createAndRotateLog) {
        log_init(LOG_ECHO|LOG_SYNC, V_DEBUG, "logfile-%Y%m%d_%H%M%S.log");

        log_trace("This should not appear in the log");
        log_debug("This is a debug entry with a %s value %d", "test", 123);
        log_info("This is a message at log level '%s'", "info");
        log_critical("This is a critial message at log level, testing %d", 123);
        log_error("This is an error message!");
    //  log_fatal(2, "This is a fatal error message...");
        const char *log_name1 = log_name();
        EXPECT_NE((const char *)0, log_name1);
        log_info("Rotating log! (sleeping for 1 second to ensure different name)");
        sleep(1);
        log_rotate();
        log_info("Log is rotated!");
        const char *log_name2 = log_name();
        EXPECT_NE((const char *)0, log_name2);
        EXPECT_NE(log_name1, log_name2);
        log_warning("Log name first = '%s', second = '%s'", log_name1, log_name2);
        log_info("Ending test");
    };

    TEST(LoggingFunctions, loggingLevels) {
        log_init(LOG_ECHO|LOG_STDERR, V_TRACE, "logfile-%Y%m%d_%H%M%S.log");
        const char *levelnames[] = { "none", "fatal", "critical", "error", "warn", "info", "debug", "trace" };
        for (int v = V_NONE; v++ < V_MAX; ) {
            log_message((enum Verbosity)v, "This is a log message at %s level", levelnames[v]);
        }
    }

} // namespace

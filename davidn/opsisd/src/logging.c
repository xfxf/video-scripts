//
// Created by David Nugent on 2/02/2016.
//

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#include "logging.h"

static struct {
    // configuration data
    int verbosity;          // Logging verbosity
    int flags;              // Logging flags
    char const *logpath;    // Logfile name template
    char const *datefmt;    // Logfile date/time format
    char const *logfmt;     // General format of a log line
    // internal data
    int log_counter;
    char *logname;          // Current logfile name
    FILE *logfp;            // Current logfile FILE*
} logData = {
    V_DEFAULT,
    LOG_ECHO,
    "log_%%Y%%m%%d_%%H%%M%%S.log",
    "%%Y-%%m-%%d %%H:%%M:%%S.%03u %c%02u%02u",
    "%s %s %s\n",
    // internal data
    0,
    0,
    0,
};


static char const *levels[] = {
    "NONE",             // 0 (use default)
    "FATAL",            // 1
    "CRITICAL",         // 2
    "ERROR",            // 3
    "WARNING",          // 4
    "INFO",             // 5
    "DEBUG",            // 6
    "TRACE",            // 7
};


void
log_init(int flags, enum Verbosity verbosity, char const *logpath) {
    logData.flags = flags;
    logData.verbosity = verbosity;
    if (logpath != NULL) {
        char log_path[strlen(logpath)*2 + 1];
        logData.flags |= LOG_FILE;
        for (char *p = log_path; *logpath != '\0'; ++logpath) {
            if (*logpath == '%') // double up the '%'
                *p++ = '%';
            *p++ = *logpath;
            *p = '\0';
        }
        logData.logpath = strdup(log_path);
    } else if (!(logData.flags & LOG_NOECHO))
        logData.flags |= LOG_ECHO;
    if (logData.verbosity == V_NONE)
        logData.verbosity = V_DEFAULT;
}


static size_t
datetime_fmt(char *dest, size_t size, char const *fmtstr) {
    char fmt[256];
    struct timeval tv;
    struct timezone tz;

    if (gettimeofday(&tv, &tz) != 0)
        return (size_t)-1; // should log this but most likely will get recusion hell!
    int sign ='+';
    int hours =0, mins =0;
    struct tm *current_time;
    if (logData.flags & LOG_UTC)
        current_time = gmtime(&tv.tv_sec);
    else {
        current_time = localtime(&tv.tv_sec);
        sign = tz.tz_minuteswest < 0 ? tz.tz_minuteswest = 0 - tz.tz_minuteswest,  '-' : '+';
        hours = tz.tz_minuteswest / 60;
        mins = tz.tz_minuteswest % 60;
    }
    snprintf(fmt, sizeof(fmt), fmtstr, tv.tv_usec / 1000, sign, hours, mins);
    return (size_t)strftime(dest, size, fmt, current_time);
}


static char *
log_newName() {
    char buffer[1024];
    return datetime_fmt(buffer, sizeof(buffer)-1, logData.logpath) == -1 ? NULL : strdup(buffer);
}

const char *
log_name() {
    return logData.logfp && logData.flags & LOG_FILE ? logData.logname : NULL;
}


void
log_rotate() {
    if (logData.logfp != NULL) {
        fclose(logData.logfp);
        logData.logfp = NULL;
    }
    if (logData.flags & LOG_FILE) {
        logData.logname = log_newName();
        logData.logfp = fopen(logData.logname, "a+");
        // emergency mode, just go into echo to stdout or stderr
        if (logData.logfp == NULL && !(logData.flags & LOG_NOECHO))
            logData.flags |= LOG_ECHO;
    }
}

int
log_log(enum Verbosity verbosity, char const *fmt, va_list args) {
    int rc = 0;
    // first make sure we want to output something

    if (verbosity <= logData.verbosity) {
        if (verbosity > V_TRACE) // Prevent potential bounds errors
            verbosity = V_TRACE;
        char logdate[256];
        if (datetime_fmt(logdate, sizeof(logdate) - 1, logData.datefmt) == (size_t) -1) {
            fprintf(stderr, "FATAL: invalid date format '%s'\n", logData.datefmt);
            exit(2);
        }
        if (logData.logfp == NULL && logData.flags & LOG_FILE)
            log_rotate();
        char fmtstr[strlen(logdate) + strlen(fmt) + 128];
        snprintf(fmtstr, sizeof(fmtstr), logData.logfmt, logdate, levels[verbosity], fmt);
        if (rc >= sizeof(fmtstr)) {
            fprintf(stderr, "FATAL: invalid log format '%s'\n", logData.logfmt);
            exit(2);
        }
        if (logData.logfp != NULL) {
            va_list args_2 = {0};
            va_copy(args_2, args);
            rc = vfprintf(logData.logfp, fmtstr, args_2);
            if (logData.flags & LOG_SYNC) {
                fflush(logData.logfp);
                fsync(fileno(logData.logfp));
            }
        }
        if (logData.flags & LOG_ECHO) {
            FILE *out = logData.flags & LOG_STDERR ? stderr : stdout;
            rc = vfprintf(out, fmtstr, args);
            fflush(out);
        }
        va_end(args);
    }
    return rc;
}


int
log_message(enum Verbosity verbose, char const *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    int rc = log_log(verbose, fmt, args);
    va_end(args);
    return rc;
}

void
log_fatal(int ec, char const *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    log_log(V_FATAL, fmt, args);
    va_end(args);
    exit(ec);
}


int
log_critical(char const *fmt, ...)  {
    va_list args;
    va_start(args, fmt);
    int rc = log_log(V_CRITICAL, fmt, args);
    va_end(args);
    return rc;
}


int
log_error(char const *fmt, ...)  {
    va_list args;
    va_start(args, fmt);
    int rc = log_log(V_ERROR, fmt, args);
    va_end(args);
    return rc;
}


int
log_warning(char const *fmt, ...)  {
    va_list args;
    va_start(args, fmt);
    int rc = log_log(V_WARN, fmt, args);
    va_end(args);
    return rc;
}


int
log_info(char const *fmt, ...)  {
    va_list args;
    va_start(args, fmt);
    int rc = log_log(V_INFO, fmt, args);
    va_end(args);
    return rc;
}


int
log_debug(char const *fmt, ...)  {
    va_list args;
    va_start(args, fmt);
    int rc = log_log(V_DEBUG, fmt, args);
    va_end(args);
    return rc;
}


int
log_trace(char const *fmt, ...)  {
    va_list args;
    va_start(args, fmt);
    int rc = log_log(V_TRACE, fmt, args);
    va_end(args);
    return rc;
}

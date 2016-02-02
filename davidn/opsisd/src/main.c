//
// Created by David Nugent on 30/01/2016.
//
// main.c
//
// Startup, argument parsing and handoff to daemon process
// Very little application specific code to see here, move on...

#include <stdio.h>
#include <getopt.h>
#include <stdlib.h>
#include <string.h>

#include "opsisd.h"
#include "serial.h"
#include "logging.h"


// short options
const char shortopts[] = "hvV::Dp:s:l:L:equF";
// long options
const struct option longopts[] = {
//  { char*name, int has_arg, int *flag, int val }
    { "port",       required_argument,  NULL,           'p' },
    { "speed",      required_argument,  NULL,           's' },
    { "listen",     required_argument,  NULL,           'l' },
    { "log",        required_argument,  NULL,           'L' },
    { "echo",       no_argument,        NULL,           'e' },
    { "quiet",      no_argument,        NULL,           'q' },
    { "utc",        no_argument,        NULL,           'u' },
    { "fsync",      no_argument,        NULL,           'F' },
    { "help",       no_argument,        NULL,           'h' },
    { "version",    no_argument,        NULL,           'v' },
    { "verbose",    optional_argument,  NULL,           'V' },
    { "daemon",     no_argument,        NULL,           'D' },
};
// options text (for help)
const char *helpopts[][3] = {
//  { char*default, char*arg_help, char*description }
    { "auto",           "auto|device [device...]",  "set serial port name, may contain wildcards or list" },
    { "115200",         "baudrate",                 "set baud rate" },
    { "localhost:8501", "[ip/hostname]:portnum",    "set listen address"},
    { NULL,             "FILENAME",                 "log to FILENAME (may contain strftime(3) strings)" },
    { NULL,             NULL,                       "echo log to stdout (twice for stderr)" },
    { NULL,             NULL,                       "don't echo log at all" },
    { NULL,             NULL,                       "log dates as UTC"},
    { NULL,             NULL,                       "force sync after each log write"},
    { NULL,             NULL,                       "display this help message" },
    { NULL,             NULL,                       "display version info" },
    { NULL,             "0-7",                      "increase or set verbosity level" },
    { NULL,             NULL,                       "detatch and fork into background" },
};

static int usage(FILE *out, int exitCode);


int
parse_args(int argc, char * const *argv, struct opsisd_opts *opts) {
    int rc =0, r =0;
    int longindex = 0;

    // Defauts
    opts->verbose = 0;
    opts->logflags = 0;
    opts->logfile = NULL;
    opts->daemonize = 0;
    opts->baudrate = speed_to_baud(115200);
    opts->port = "auto";
    opts->listen_addr = "localhost";
    opts->listen_port = 8501;

    while (rc == 0 && (r = getopt_long(argc, argv, shortopts, longopts, &longindex)) != EOF) {
        switch (r) {
            case 'h':
                exit(usage(stdout, 0));
                // notreached
            case 'v':
                printf("%s version %s\n", OPSISD_NAME, OPSISD_VERSION);
                exit(0);
                // notreached
            case 'V':
                if (optarg == NULL)
                    opts->verbose++;
                else {
                    char *endptr = optarg;
                    opts->verbose = (int)strtol(optarg, &endptr, 10) & 7;
                    if (endptr == NULL || *endptr != '\0') {
                        fprintf(stderr, "invalid verbosity (0-7) '%s'\n", optarg);
                        rc = usage(stderr, 2);
                    }
                }
                break;
            case 'D':
                opts->daemonize = 1;
                break;
            case 's': {
                char *endptr = optarg;
                long baudrate = strtol(optarg, &endptr, 10);
                if (endptr != NULL && *endptr == '\0') {
                    opts->baudrate = speed_to_baud(baudrate);
                    if (opts->baudrate != BINVALID)
                        break;
                }
                fprintf(stderr, "invalid speed '%s'\n", optarg);
                rc = usage(stderr, 2);
            }
                break;
            case 'l': {
                char *at = strchr(optarg, ':');
                if (at == NULL)
                    at = optarg + strlen(optarg);
                size_t i = at - optarg;
                char listen_addr[i+1];
                strncpy(listen_addr, optarg, i);
                listen_addr[i] = '\0';
                opts->listen_addr = strdup(listen_addr);
                if (*at != '\0' && *(++at) != '\0') {
                    char *endptr = at;
                    opts->listen_port = (short)strtol(at, &endptr, 10);
                    if (*endptr != '\0') {
                        fprintf(stderr, "invalid port number '%s'", at);
                        rc = usage(stderr, 2);
                    }
                }
            }
                break;
            case 'p': {
                const char *args[OPSIS_MAX_PORTS + 1];
                int count = 0, index = optind - 1;
                for (count =0; index < argc && index < OPSIS_MAX_PORTS; count++) {
                    const char *next = argv[index++];
                    if (next == NULL || *next == '-' || *next == '\0')
                        break;
                    args[count] = next;
                }
                optind = index - 1;
                if (count > 0) {
                    int length =0;
                    for (int i =0; i < count; i++)
                        length += strlen(args[i]) + 1;
                    char *ports = malloc(length);
                    *ports = '\0';
                    for (int i =0; i < count; i++) {
                        strcat(ports, args[i]);
                        strcat(ports, "|");
                    }
                    opts->port = ports;
                    break;
                }
                // fallthru
            }
            case 'L':
                opts->logfile = optarg;
                break;
            case 'e':   // -> echo -> stderr -> off
                if (opts->logflags & LOG_ECHO) {
                    if (!(opts->logflags & LOG_STDERR)) { // echo -> stderr
                        opts->logflags |= LOG_STDERR;
                        break;
                    }
                    // fallthru: stderr -> off
                } else { // quiet -> echo
                    opts->logflags |= LOG_ECHO;
                    opts->logflags &= ~(LOG_NOECHO | LOG_STDERR);
                    break;
                }
                // fallthru
            case 'q':
                opts->logflags &= ~(LOG_ECHO|LOG_STDERR);
                opts->logflags |= LOG_NOECHO;
                break;
            case'u':
                opts->logflags |= LOG_UTC;
                break;
            case 'F':
                opts->logflags |= LOG_SYNC;
                break;
            case ':':
            case '?':
                rc = usage(stderr, 1);
                break;
        }
    }
    return rc;
}

#define HELP_INDENT 50

static int
usage(FILE *out, int ec) {
    fprintf(out, "%s [ options ]\n Options:\n", OPSISD_NAME);
    for(int index =0; index < sizeof(longopts)/sizeof(struct option); index++) {
        int len = 0;
        switch (longopts[index].has_arg) {
            case no_argument:
                len = fprintf(out, "  -%c --%s", longopts[index].val, longopts[index].name);
                break;
            case optional_argument:
                len = fprintf(out, "  -%c --%s [%s]", longopts[index].val, longopts[index].name, helpopts[index][1]);
                break;
            case required_argument:
                len = fprintf(out, "  -%c --%s %s", longopts[index].val, longopts[index].name, helpopts[index][1]);
                break;
        }
        char const *desc = helpopts[index][2] == NULL ? "" : helpopts[index][2];
        fprintf(out, "%*s %s\n", len > HELP_INDENT ? 0 : len - HELP_INDENT, "", desc);
    }
    return ec;
}

int
main(int argc, char * const *argv) {
    struct opsisd opsisd = {};

    int rc = parse_args(argc, argv, &opsisd.opts);
    if (rc == 0) {
        log_init(opsisd.opts.logflags, opsisd.opts.verbose, opsisd.opts.logfile);
        log_debug("      Device : %s", opsisd.opts.port);
        log_debug("    Baudrate : %ld", baud_to_speed(opsisd.opts.baudrate));
        log_debug("Bind Address : %s", opsisd.opts.listen_addr);
        log_debug("   Bind Port : %u", opsisd.opts.listen_port);
        log_debug("   Daemonize : %s", opsisd.opts.daemonize ? "Yes" : "No");
        log_debug("   Verbosity : %d", opsisd.opts.verbose);
    }
    return rc;
}

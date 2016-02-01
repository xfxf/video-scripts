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

// short options
const char shortopts[] = "hvdDp:s:l:";
// long options
const struct option longopts[] = {
//  { char*name, int has_arg, int *flag, int val }
    { "help",       no_argument,        NULL,           'h' },
    { "version",    no_argument,        NULL,           'v' },
    { "verbose",    no_argument,        NULL,           'd' },
    { "daemon",     no_argument,        NULL,           'D' },
    { "port",       required_argument,  NULL,           'p' },
    { "speed",      required_argument,  NULL,           's' },
    { "listen",     required_argument,  NULL,           'l' },
};
// options text (for help)
const char *helpopts[][3] = {
//  { char*default, char*arg_help, char*description }
    { NULL,             NULL,                       "display this help message" },
    { NULL,             NULL,                       "display version info" },
    { NULL,             NULL,                       "increase verbosity level" },
    { NULL,             NULL,                       "detatch and fork into background" },
    { "auto",           "auto|device [device...]",  "set serial port name, may contain wildcards or list" },
    { "115200",         "baudrate",                 "set baud rate" },
    { "localhost:8501", "[ip/hostname]:portnum",    "set listen address"},
};

static int usage(FILE *out, int exitCode);

int
parse_args(int argc, char * const *argv, struct opsisd_opts *opts) {
    int rc =0, r =0;
    int longindex = 0;

    // Defauts
    opts->verbose = 0;
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
            case 'd':
                opts->verbose++;
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
                opts->listen_addr = malloc(i+1);
                strncpy(opts->listen_addr, optarg, i);
                opts->listen_addr[i] = '\0';
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
            case ':':
            case '?':
                rc = usage(stderr, 1);
                break;
        }
    }
    return rc;
}

static int
usage(FILE *out, int ec) {
    fprintf(out, "%s [ options ]\n Options:\n", OPSISD_NAME);
    for(int index =0; index < sizeof(longopts)/sizeof(struct option); index++) {
        switch (longopts[index].has_arg) {
            case no_argument:
                fprintf(out, "  -%c --%s  ;%s\n", longopts[index].val, longopts[index].name,
                        helpopts[index][2]);
                break;
            case optional_argument:
                fprintf(out, "  -%c --%s [%s]  ;%s\n", longopts[index].val, longopts[index].name,
                        helpopts[index][1], helpopts[index][2]);
                break;
            case required_argument:
                fprintf(out, "  -%c --%s %s  ;%s\n", longopts[index].val, longopts[index].name,
                        helpopts[index][1], helpopts[index][2]);
                break;
        }
    }
    return ec;
}

int
main(int argc, char * const *argv) {
    struct opsisd opsisd = {};

    int rc = parse_args(argc, argv, &opsisd.opts);
    if (rc == 0) {
        FILE *log = stdout;
        if (opsisd.opts.verbose >= V_DEBUG) {
            fprintf(log, "      Device : %s\n", opsisd.opts.port);
            fprintf(log, "    Baudrate : %ld\n", baud_to_speed(opsisd.opts.baudrate));
            fprintf(log, "Bind Address : %s\n", opsisd.opts.listen_addr);
            fprintf(log, "   Bind Port : %u\n", opsisd.opts.listen_port);
            fprintf(log, "   Daemonize : %s\n", opsisd.opts.daemonize ? "Yes" : "No");
            fprintf(log, "   Verbosity : %d\n", opsisd.opts.verbose);
        }
    }
    return rc;
}

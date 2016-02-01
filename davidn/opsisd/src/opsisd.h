//
// Created by David Nugent on 31/01/2016.
//
// opsisd.h

#ifndef OPSISD_OPISD_H
#define OPSISD_OPISD_H

#define OPSISD_VERSION "0.1"
#define OPSISD_NAME "opsisd"

#define OPSIS_MAX_PORTS 31

// configuration data
struct opsisd_opts {
    int verbose;
    int daemonize;
    long baudrate;
    char *port;
    char *listen_addr;
    short listen_port;
};

// working data
struct opsisd {
    struct opsisd_opts opts;
};

enum Verbosity {
    V_QUIET,
    V_ERROR,
    V_INFO,
    V_DEBUG,
    V_TRACE
};

char const *find_opsis_serial(const struct opsisd_opts *opts);

#endif //OPSISD_OPISD_H

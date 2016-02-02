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
    int logflags;
    char const *logfile;
    int daemonize;
    long baudrate;
    char const *port;
    char const *listen_addr;
    short listen_port;
};

// working data
struct opsisd {
    struct opsisd_opts opts;
};


// controller serial device llist node
struct ctrldev {
    struct ctrldev *next;
    char *devname;
};

struct ctrldev *find_opsis_serial_all(const struct opsisd_opts *opts);
void ctrldev_free(struct ctrldev *first_dev);
char *find_opsis_serial(const struct opsisd_opts *opts);



#endif //OPSISD_OPISD_H

//
// Created by David Nugent on 31/01/2016.
//

#ifndef OPSISD_SERIAL_H
#define OPSISD_SERIAL_H

#define BINVALID -1L

long speed_to_baud(long speed);
long baud_to_speed(long baud);

#include "iodev.h"

typedef struct serial_cfg_s serial_cfg_t;

struct serial_cfg_s {
    iodev_cfg_t cfg;
    char const *portname;
    long baudrate;
};

extern serial_cfg_t *serial_getcfg(iodev_t *sdev);

#endif

//
// Created by David Nugent on 31/01/2016.
//

#ifndef OPSISD_SERIAL_H
#define OPSISD_SERIAL_H

#include "device.h"

#define BINVALID -1L

long speed_to_baud(long speed);
long baud_to_speed(long baud);

struct serial_config {
    char const *portname;
    long baudrate;
};

struct serial_device {
    struct device dev;

};
#endif

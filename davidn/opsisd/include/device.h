//
// Created by David Nugent on 3/02/2016.
//
// Generic device type

#ifndef OPSISD_DEVICE_H
#define OPSISD_DEVICE_H

// common device interface

#include <stddef.h>

enum devState {
    CLOSED,         // closed/inactive
    OPEN,           // open, inactive, idle
    CONNECTED,      // open, active, connected or listening
    ACTIVE          // open, active, communicating
};

struct dev_config {
    int fd;
    int listener;
};

struct device {

    struct dev_config *cfg;

    char const * (*name)(struct device *dev);
    int (*state)(struct device *dev);
    struct dev_config *(*get_config)(struct device *dev);

    // device control
    int (*open)(struct device *dev, char const *data, int listen);
    void (*close)(struct device *dev);
    int (*configure)(struct device *dev, void *data);

    // I/O
    int (*read)(struct device *dev, void *buf, size_t size);
    int (*write)(struct device *dev, void *buf, size_t size);

};

#endif //OPSISD_DEVICE_H

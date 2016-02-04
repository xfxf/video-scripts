//
// Created by David Nugent on 2/02/2016.
//
// Generic selector type for registering filehandles in a non-blocking select(2)

#ifndef OPSISD_SELECTOR_H
#define OPSISD_SELECTOR_H

#include "array.h"
#include "iodev.h"

typedef struct selector_s selector_t;

struct selector_s {
    int alloc;
    array_t devs;
};

extern selector_t *selector_init(selector_t *selector);
extern void selector_free(selector_t *selector);
extern size_t selector_device_count(selector_t *selector);
extern iodev_t *selector_get_device(selector_t *selector, size_t index);
extern void selector_add_device(selector_t *selector, iodev_t *dev);

#endif //OPSISD_SELECTOR_H

//
// Created by David Nugent on 3/02/2016.
//

#include <stdlib.h>
#include <string.h>

#include "selector.h"

#define SELECTOR_ALLOC 0xa51d15a


selector_t *
selector_init(selector_t *selector) {
    if (selector != NULL)
        memset(selector, '\0', sizeof(selector_t));
    else {
        selector = calloc(1, sizeof(selector_t));
        selector->alloc = SELECTOR_ALLOC;
    }
    array_init(&selector->devs, sizeof(iodev_t *), 8);
    return selector;
}


iodev_t *
selector_get_device(selector_t *selector, size_t index) {
    return *((iodev_t **)array_get(&selector->devs, index));
}


size_t
selector_device_count(selector_t *selector) {
    return array_count(&selector->devs);
}


void
selector_free(selector_t *selector) {
    // Make sure that all devices are in closed state
    for (size_t i =0; i < array_count(&selector->devs); i++) {
        iodev_t *dev = selector_get_device(selector, i);
        if (iodev_getstate(dev) > IODEV_CLOSED)
            iodev_close(dev, IOFLAG_INACTIVE);
    }
    // Free the device array
    array_free(&selector->devs);
    // Free the selector if we originally allocated it
    if (selector->alloc == SELECTOR_ALLOC) {
        selector->alloc = 0;
        free(selector);
    }
}


void
selector_add_device(selector_t *selector, iodev_t *dev) {
    array_append(&selector->devs, &dev);
    dev->selector = selector;
}

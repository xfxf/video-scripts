//
// Created by David Nugent on 3/02/2016.
//
// Generic device type

#ifndef OPSISD_IODEV_H
#define OPSISD_IODEV_H

// common device interface

#include <stddef.h>
#include <stdarg.h>

#include "buffer.h"

enum devState {
    IODEV_NONE,             // default state
    IODEV_INACTIVE,         // closed, do not open
    IODEV_CLOSED,           // closed (queue for open)
    IODEV_PENDING,          // waiting for open to complete
    IODEV_OPEN,             // open, inactive, idle
    IODEV_CONNECTED,        // open, active, connected or listening
    IODEV_ACTIVE            // open, active, communicating
};

enum devFlags {
    IOFLAG_NONE = 0x00,
    IOFLAG_FLUSH = 0x01,
    IOFLAG_INACTIVE = 0x02,
};

typedef struct iodev_cfg_s iodev_cfg_t;

struct iodev_cfg_s {
    const char *name;
    int fd;
    int listener;
} device_cfg;

iodev_cfg_t *alloc_cfg(size_t size, const char *name, int listener);
void free_cfg(iodev_cfg_t *cfg);


typedef struct iodev_s iodev_t;
typedef struct selector_s selector_t;

struct iodev_s {

    iodev_cfg_t *cfg;

    int fd;
    selector_t *selector;

    int state;
    buffer_t rbuf;
    buffer_t tbuf;

    // device control
    int (*open)(iodev_t *dev, char const *data, int listen);
    void (*close)(iodev_t *dev, int flags);
    int (*configure)(iodev_t *dev, void *data);

    // I/O
    int (*read_handler)(iodev_t *dev);
    int (*write_handler)(iodev_t *dev);
    int (*except_handler)(iodev_t *dev);
    int (*read)(iodev_t *dev, void *buf, size_t len);
    int (*write)(iodev_t *dev, void const *buf, size_t len);

    // Errors & notifications
    int (*errfunc)(char const *fmt, va_list args);
    int (*notify)(char const *fmt, va_list args);

};


iodev_cfg_t *iodev_getcfg(iodev_t *iodev);
const char *iodev_name(iodev_t *iodev);
int iodev_getstate(iodev_t *dev);
int iodev_setstate(iodev_t *dev, int state);
int iodev_getfd(iodev_t *dev);
void iodev_seterrfunc(iodev_t *dev, int (*func)(char const *fmt, va_list args));
void iodev_setnotify(iodev_t *dev, int (*func)(char const *fmt, va_list args));

extern iodev_t *iodev_create(iodev_cfg_t *cfg, size_t bufsize);
extern void iodev_free(iodev_t *dev);

extern int iodev_open(iodev_t *dev, char const *data, int listen);
extern void iodev_close(iodev_t *dev, int flags);
extern int iodev_configure(iodev_t *dev, void *data);
extern int iodev_read_handler(iodev_t *dev);
extern int iodev_write_handler(iodev_t *dev);
extern int iodev_except_handler(iodev_t *dev);

extern int iodev_read(iodev_t *dev, void *buf, size_t len);
extern int iodev_write(iodev_t *dev, void const *buf, size_t len);

#endif //OPSISD_IODEV_H

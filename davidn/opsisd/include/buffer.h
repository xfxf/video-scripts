//
// Created by David Nugent on 4/02/2016.
// Simple ring buffer

#ifndef OPSISD_BUFFER_H
#define OPSISD_BUFFER_H

#include <stddef.h>

typedef struct buffer_s buffer_t;

struct buffer_s {
    int alloc;
    size_t
        b_size,         // size of the buffer
        b_lo,           // lo position, data fetched from here
        b_hi;           // hi position, data added at here
    void *data;
};

extern buffer_t *buffer_init(buffer_t *buffer, size_t size);
extern void buffer_free(buffer_t *buffer);

extern void buffer_flush(buffer_t *buffer);
extern size_t buffer_available(buffer_t *buffer);
extern size_t buffer_used(buffer_t *buffer);
extern void buffer_compact(buffer_t *buffer);

size_t buffer_size(buffer_t *buffer);
size_t buffer_inptr(buffer_t *buffer);
size_t buffer_outptr(buffer_t *buffer);

extern size_t buffer_put(buffer_t *buffer, void const *buf, size_t len);
extern size_t buffer_get(buffer_t *buffer, void *buf, size_t len);

#endif //OPSISD_BUFFER_H

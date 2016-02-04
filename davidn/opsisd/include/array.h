//
// Created by David Nugent on 3/02/2016.
// Simple dynamic array

#ifndef OPSISD_ARRAY_H
#define OPSISD_ARRAY_H

#include <stddef.h>
#include <stdarg.h>

typedef struct array_s array_t;

// This is intended to be opaque
struct array_s {
    unsigned int alloced;   // non-zero = heap allocated
    size_t
        e_size,             // size of each element
        e_all,              // number of allocated elements
        e_end,              // index of last+1 element
        e_inc;              // realloc increment size (elements)
    void *data;             // where the data is stored

    int (*errfunc)(array_t *, char const *fmt, va_list args);
};

extern array_t *array_alloc(size_t element_size, size_t initial_count);
extern void array_free(array_t *array);
extern int array_init(array_t *array, size_t element_size, size_t initial_count);

extern void array_seterrfunc(array_t *array, int (*errfunc)(array_t *, char const *fmt, va_list args));

extern void *array_get(array_t *array, size_t index); // effectively array[index]
extern void *array_put(array_t *array, void const *element, size_t index);
extern void *array_new(array_t *array); // create new element in array
extern void *array_new_at(array_t *array, size_t index); // create new element at index
extern void *array_append(array_t *array, void const *element);

// These may affect an index and should not be used when that will surprise
extern void *array_insert(array_t *array, void const *element, size_t at);
extern size_t array_delete(array_t *array, size_t at);
extern size_t array_index(array_t *array, void *ptr);

size_t array_count(array_t const *array);
size_t array_capacity(array_t const *array);
size_t array_element_size(array_t const *array);
size_t array_chunk_size(array_t const *array);

#endif //OPSISD_ARRAY_H

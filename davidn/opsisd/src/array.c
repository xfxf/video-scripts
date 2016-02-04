//
// Created by David Nugent on 3/02/2016.
//

#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <stdio.h>
#include <sys/errno.h>
#include "array.h"


#define ALLOC_MAGIC 0x5a5a5a5a

static int array_error(array_t *array, const char *fmt, ...) __attribute__((format (printf, 2, 3)));

static int
array_error(array_t *array, const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    int len = 0;
    if (array->errfunc != NULL)
        len = array->errfunc(array, fmt, args);
    else {
        len = vfprintf(stderr, fmt, args);
        len += fprintf(stderr, "\n");
    }
    va_end(args);
    return len;
}


array_t *
array_alloc(size_t element_size, size_t initial_count) {
    array_t *array = calloc(1, sizeof(array_t));
    array->alloced = ALLOC_MAGIC;
    array_init(array, element_size, initial_count);
    return array;
}


size_t array_count(array_t const *array) { return array->e_end; }
size_t array_capacity(array_t const *array) { return array->e_all; }
size_t array_element_size(array_t const *array) { return array->e_size; }
size_t array_chunk_size(array_t const *array) { return array->e_inc; }

#define BOUNDS_FAIL 1
#define BOUNDS_OK   0

static int
array_check_bounds(array_t *array, size_t index, size_t within) {
    if (index >= (array->e_end + within)) {
        array_error(array, "array bounds error: %zu (of %zu elements)", index, array->e_end);
        return BOUNDS_FAIL;
    }
    return BOUNDS_OK;
}


void
array_free(array_t *array) {
    if (array != NULL) {
        // deallocate the array data
        if (array->data != NULL) {
            free(array->data);
            array->e_all = array->e_end = 0;
            array->data = (void **)0;
        }
        // deallocate the array struct if we originally allocated it
        if (array->alloced == ALLOC_MAGIC) {
            array->alloced = 0;
            free(array);
        }
    }
}


static int
array_check_alloc(array_t *array, size_t elements) {
    if (elements <= 0)
        elements = 1;
    // Is array large enough to handle <element> elements?
    size_t count = array->e_all;
    while (count <= array->e_end + elements)
        count += array->e_inc; // Add a block and retest
    if (count > array->e_all) {
        void *buf = realloc(array->data, count * array->e_size);
        if (buf == NULL) {
            array_error(array, "array_check_alloc reallocation failure(%d): %s", errno, strerror(errno));
            return -1;
        }
        array->data = buf;
        size_t added = count - array->e_all;
        memset(array->data + array->e_all * array->e_size, '\0', added * array->e_size);
        array->e_all = count;
    }
    return 0;
}


int
array_init(array_t *array, size_t element_size, size_t initial_count) {
    array->e_size = element_size;
    array->e_all = array->e_end = 0;
    array->e_inc = initial_count ? initial_count : 8;
    array->data = NULL;
    return array_check_alloc(array, 0);
}


void
array_seterrfunc(array_t *array, int (*errfunc)(array_t *, char const *fmt, va_list args)) {
    array->errfunc = errfunc;
}


void *
array_get(array_t *array, size_t index) {
    if (array_check_bounds(array, index, 0) == BOUNDS_FAIL)
        return NULL;
    return array->data + index * array->e_size;
}


void *
array_put(array_t *array, void const *element, size_t at) {
    void *ptr = array_get(array, at);
    if (ptr != NULL)
        memmove(ptr, element, array->e_size);
    return ptr;
}


void *
array_new(array_t *array) {
    array_check_alloc(array, 1);
    size_t index = array->e_end++;
    return array_get(array, index);
}


void *
array_new_at(array_t *array, size_t index) {
    if (array_check_bounds(array, index, 1) == BOUNDS_FAIL)
        return NULL;
    // do this first, in case the array needs to move (via realloc)
    array_check_alloc(array, 1);
    void *ptr = array->data + index * array->e_size;
    if (ptr != NULL) {
        size_t to_move = array->e_end - index;
        if (to_move > 0)
            memmove(ptr + array->e_size, ptr, array->e_size * to_move);
        ++array->e_end;
        memset(ptr, '\0', array->e_size);
    }
    return ptr;
}


void *
array_append(array_t *array, void const *element) {
    void *ptr = array_new(array);
    if (ptr != NULL)
        memcpy(ptr, element, array->e_size);
    return ptr;
}


void *
array_insert(array_t *array, void const *element, size_t at) {
    void *ptr = array_new_at(array, at);
    if (ptr != NULL)
        memcpy(ptr, element, array->e_size);
    return ptr;
}


size_t
array_index(array_t *array, void *ptr) {
    if (ptr < array->data || ptr > (array->data + (array->e_size * array->e_end)))
        return (size_t)-1;
    return (ptr - array->data) / array->e_size;
}


size_t
array_delete(array_t *array, size_t at) {
    if (array_check_bounds(array, at, 0) == BOUNDS_OK) {
        if (at < --array->e_end) {
            void *ptr = array_get(array, at);
            size_t to_move = array->e_end - at;
            if (to_move > 0)
                memmove(ptr, ptr + array->e_size, to_move * array->e_size);
        }
        return array->e_end;
    }
    return (size_t)-1;
}

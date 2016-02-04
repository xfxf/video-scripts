//
// Created by David Nugent on 3/02/2016.
//

extern "C" {
#include "array.h"
#include "logging.h"
}

#include "gtest/gtest.h"

namespace {

    struct element {
        size_t number;
    };

    #define I 8
    #define N (I * 5 + 1)

    TEST(ArrayFunctions, arrayCreationAuto) {
        // allocate on stack
        array_t A = {};
        array_init(&A, sizeof(element), I); // init must be called in this case
        EXPECT_EQ(0, array_count(&A));
        // This will generate a bounds error and return NULL
        EXPECT_EQ((void *)0, array_get(&A, 0));
        // Add lots of elements
        for (size_t i=0; i < N; i++) {
            element *e = (element *)array_new(&A);
            e->number = i;
        }
        // Make sure we have as many as expected
        EXPECT_EQ(N, array_count(&A));
        // Free the array
        array_free(&A);
        // A is auto, so still exists
        EXPECT_EQ(0, array_count(&A));
        EXPECT_EQ(A.data, (void*)0);
    };

    TEST(ArrayFunctions, arrayCreateHeap) {
        // allocate on heap
        array_t *A = array_alloc(sizeof(element), I);   // init already done
        EXPECT_EQ(0, array_count(A));
        // This will generate a bounds error and return NULL
        EXPECT_EQ((void *)0, array_get(A, 0));
        // Add lots of elements
        for (size_t i=0; i < N; i++) {
            element *e = (element *)array_new(A);
            e->number = i;
        }
        // Make sure we have as naby as expected
        EXPECT_EQ(N, array_count((array_t const *)A));
        // Free the array
        array_free(A);
        // Cannot query A further due to deallication
    }

    // error message thunk, redirects to logging framework
    extern "C" int
    array_error(array_t *, char const *fmt, va_list args) {
        return log_log(V_ERROR, fmt, args);
    }

    TEST(ArrayFunctions, arrayErrorFunction) {
        array_t A = {};
        // Set the error message handler
        array_seterrfunc(&A, array_error);
        // Now generate an error, same as above
        EXPECT_EQ((void *)0, array_get(&A, 0));
        array_free(&A);
    }

    TEST(ArrayFunctions, arrayNewAndAppend) {
        array_t * A = array_alloc(sizeof(element), I);
        // Build an array of elements
        for (size_t i=0; i < N; i++) {
            element *e = (element *)array_new(A);
            e->number = i;
        }
        EXPECT_EQ(N, array_count(A));
        array_t * B = array_alloc(sizeof(element), I);
        // Build another array of the same elements, but using append
        for (size_t i=0; i < N; i++) {
            element e = {i};
            array_append(B, &e);
        }
        EXPECT_EQ(N, array_count(B));
        // Now, compare the two arrays
        for (size_t i=0; i < N; i++) {
            element *a = (element *)array_get(A, i);
            element *b = (element *)array_get(B, i);
            EXPECT_EQ(a->number, b->number);
        }
        array_free(B);
        array_free(A);
    }

    TEST(ArrayFunctions, arrayInsertNewAt) {
        array_t * A = array_alloc(sizeof(element), I);
        // Build an array of elements, inserting at start
        for (size_t i=0; i < N; i++) {
            element *e = (element *)array_new_at(A, 0);
            e->number = i;
        }
        EXPECT_EQ(N, array_count(A));
        array_t * B = array_alloc(sizeof(element), I);
        // Build another array of the same elements, but using append
        for (size_t i=0; i < N; i++) {
            element e = {i};
            array_insert(B, &e, 0);
        }
        EXPECT_EQ(N, array_count(B));
        // Now, compare the two arrays
        for (size_t i=0; i < N; i++) {
            element *a = (element *)array_get(A, i);
            element *b = (element *)array_get(B, i);
            EXPECT_EQ(a->number, b->number);
        }
        array_free(A);
    }

    TEST(ArrayFunctions, arrayDelete) {
        array_t * A = array_alloc(sizeof(element), I);
        for (size_t i=0; i < N; i++) {
            element e = {i};
            array_append(A, &e);
        }
        size_t capacity = array_capacity(A);
        EXPECT_EQ(N, array_count(A));
        // delete the first element
        size_t rc = array_delete(A, 0);
        // returns remaining records, if any
        EXPECT_EQ(N-1, rc);
        ASSERT_EQ(N-1, array_count(A));
        // delete the last element
        rc = array_delete(A, rc - 1);
        EXPECT_EQ(N-2, rc);
        ASSERT_EQ(N-2, array_count(A));
        // delete a record somewhere in between
        rc = array_delete(A, size_t(rc / 2));
        EXPECT_EQ(N-3, rc);
        ASSERT_EQ(N-3, array_count(A));
        while (rc > 0 && rc != (size_t)-1)
            rc = array_delete(A, 0);
        EXPECT_EQ(0, rc);
        // check that error is generated and we get error result
        rc = array_delete(A, 0);
        EXPECT_EQ((size_t)-1, rc);
        // check that capacity did not change
        EXPECT_EQ(capacity, array_capacity(A));
        array_free(A);
    }

    TEST(ArrayFunctions, arrayIndexAndPut) {
        array_t * A = array_alloc(sizeof(element), I);
        for (size_t i=0; i < N; i++) {
            element e = {i};
            element *ee = (element *)array_append(A, &e);
            size_t index = array_index(A, ee);
            EXPECT_EQ(i, index);
        }
        EXPECT_EQ(N, array_count(A));
        for (size_t i =0; i < N; i++) {
            size_t v = N - i - 1;
            element e = {v};
            element *ee = (element *)array_put(A, &e, i);
            EXPECT_EQ(e.number, ee->number);
        }
        for (size_t i =0; i < N; i++) {
            size_t v = N - i - 1;
            element *e = (element *)array_get(A, v);
            EXPECT_EQ(i, e->number);
        }
        array_free(A);
    }

} // namespace

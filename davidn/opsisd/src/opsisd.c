//
// Created by David Nugent on 31/01/2016.
//


#include <stddef.h>
#include <string.h>
#include <wordexp.h>
#include <stdlib.h>
#include <unistd.h>
#include "opsisd.h"

// device list support

static char const *auto_devices = "/dev/ttyACM*|/dev/ttyVIZ*";

static struct ctrldev *
new_odev(char const *devicename) {
    struct ctrldev *curr_dev = NULL;
    // requires a real, existing and accessible file
    if (access(devicename, R_OK|W_OK) != -1) {
        curr_dev = malloc(sizeof(struct ctrldev));
        if (curr_dev != NULL) {
            curr_dev->devname = strdup(devicename);
            curr_dev->next = NULL;
        }
    }
    return curr_dev;
}

void
ctrldev_free(struct ctrldev *first_dev) {
    if (first_dev) {
        for (struct ctrldev *next = first_dev; next != NULL; ) {
            free(next->devname);
            struct ctrldev *fnext = next;
            next = next->next;
            free(fnext);
        }
    }
}

// This should theoretically test to see if it is an opsis
// probably by figuring out which driver is handling it,
// however we bypass this and always ok the first one...
static int
test_ctrldev(const struct ctrldev *_odev) {
    return 1;
}

char *
find_opsis_serial(const struct opsisd_opts *opts) {
    struct ctrldev *first_dev = find_opsis_serial_all(opts);
    char *result = NULL;
    for (struct ctrldev *next = first_dev; result == NULL && next != NULL; next = next->next) {
        if (test_ctrldev(next)) {
            result = next->devname;
            next->devname = NULL;
        }
    }
    ctrldev_free(first_dev);
    return result;
}


// Attempt to locate

struct ctrldev *
find_opsis_serial_all(const struct opsisd_opts *opts) {
    static struct ctrldev *first_dev = NULL;

    char const *devices = opts->port;
    if (strcmp(devices, "auto") == 0)
        devices = auto_devices;
    size_t len = 0;
    struct ctrldev **next_dev = &first_dev;
    for (const char *p = devices; p != NULL && *p != '\0'; p += len) {
        const char *sep = strchr(p, '|');
        int skip = sep == NULL ? sep = p + strlen(p), 0 : 1;
        len = sep - p;
        if (len < 1)
            break;
        int xtra = *p == '/' || *p == '~' ? 0 : 5;   // need to add device prefix?
        char device[len + xtra + 1];
        if (xtra)
            strcpy(device, "/dev/");
        strncpy(device + xtra, p, len);
        device[len + xtra] = '\0';
        // Check for a glob pattern
        if (strcspn(device, "*?!$[]") != strlen(device) || *device == '~') {
            wordexp_t exprc;
            switch (wordexp(device, &exprc, 0)) {
                case 0:
                    for (size_t i =0; i < exprc.we_wordc; i++) {
                        if ((*next_dev = new_odev(exprc.we_wordv[i])) != NULL)
                            next_dev = &(*next_dev)->next;
                    }
                case WRDE_NOSPACE:
                    wordfree(&exprc);
                default:
                    break;
            }
        } else {
            if ((*next_dev = new_odev(device)) != NULL)
                next_dev = &(*next_dev)->next;
        }
        len += skip;
    }
    return first_dev;
}

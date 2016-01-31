//
// Created by David Nugent on 31/01/2016.
//


#include <stddef.h>
#include <string.h>
#include <wordexp.h>
#include <stdlib.h>
#include "opsisd.h"

static char const *auto_devices = "/dev/ttyACM*";

struct odev {
    struct odev *next;
    char *devname;
};

static struct odev *
new_odev(char const *devicename) {
    struct odev *_odev = malloc(sizeof(struct odev));
    _odev->devname = strdup(devicename);
    _odev->next = NULL;
    return _odev;
}

// This should theoretically test to see if it is an opsis
// probably by figuring out which driver is handling it,
// however we bypass this and always ok the first one...
static int
test_odev(const struct odev *_odev) {
    return 1;
}

// Attempt to locate

char const *
find_opsis_serial(const struct opsisd_opts *opts) {
    char const *result = NULL;
    static struct odev *first_dev = NULL;

    char const *devices = opts->port;
    if (strcmp(devices, "auto"))
        devices = auto_devices;
    size_t len = 0;
    struct odev **next_dev = &first_dev;
    for (const char *p = devices; p != NULL && *p != '\0'; p += len) {
        const char *sep = strchr(p, '|');
        if (sep == NULL)
            sep = p + strlen(p);
        len = sep - p;
        if (len < 1)
            break;
        int xtra = *p == '/' ? 0 : 5;   // need to add device prefix?
        char device[len + xtra + 1];
        if (xtra)
            strcpy(device, "/dev/");
        strncpy(device + xtra, p, len);
        device[len + xtra] = '\0';
        // Check for a glob pattern
        if (strcspn(device, "*?[]") != strlen(device)) {
            wordexp_t exprc;
            switch (wordexp(device, &exprc, 0)) {
                case 0:
                    for (size_t i =0; i < exprc.we_wordc; i++) {
                        *next_dev = new_odev(exprc.we_wordv[i]);
                        next_dev = &(*next_dev)->next;
                    }
                case WRDE_NOSPACE:
                    wordfree(&exprc);
                default:
                    exprc = NULL;
                    break;
            }
        } else {
            *next_dev = new_odev(device);
            next_dev = &(*next_dev)->next;
        }
    }
    if (first_dev) {
        // locate our device and deallocate the rest
        for (struct odev *next = first_dev; next != NULL; ) {
            if (test_odev(next))
                result = next->devname;
            else
                free(next->devname);
            struct odev *fnext = next;
            next = next->next;
            free(fnext);
        }
    }
    return result;
}

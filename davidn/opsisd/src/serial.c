//
// Created by David Nugent on 31/01/2016.
//

#include <termios.h>
#include "serial.h"

// Miscellaneous serial functions

static long baudmap[][2] = {
    {B300,     300      },
    {B1200,    1200     },
    {B2400,    2400     },
    {B4800,    4800     },
    {B9600,    9600     },
    {B19200,   19200    },
    {B38400,   38400    },
    {B57600,   57600    },
#if defined(B115200)
    {B115200,  115200   },
#endif
#if defined(B230400)
    {B230400,  230400   },
#endif
#if defined(B460800)
    {B460800,  460800   },
#endif
#if defined(B576000)
    {B576000,  576000   },
#endif
#if defined(B921600)
    {B921600,  921600   },
#endif
    {B0,       0        }
};

// System specific speed to baud translations
// Baud rate values are those define for serial ports for the host OS

long
speed_to_baud(long speed) {
    for (int i =0; baudmap[i][1] != 0; i++)
        if (baudmap[i][1] == speed)
            return baudmap[i][0];
    return BINVALID;
}

long
baud_to_speed(long baud) {
    for (int i =0; baudmap[i][1] != 0; i++)
        if (baudmap[i][0] == baud)
            return baudmap[i][1];
    return BINVALID;
}

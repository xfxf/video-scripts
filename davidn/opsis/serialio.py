#!/usr/bin/env python3
#

import copy
import queue
import threading
import time
import serial
import os


class SerialIO(object):
    """
    A general object providing high level support functions for pyserial with sensible defaults
    """

    PORT_DEFAULTS = {
        'port': 'auto',
        'baudrate': 115200,
        'parity': serial.PARITY_NONE,
        'stopbits': serial.STOPBITS_ONE,
        'bytesize': serial.EIGHTBITS,
        'rtscts': True,
        'timeout': 1.0,
        'inter_byte_timeout': 0.05,
    }

    TIMERS = {
        'wait_byte': 0.10,           # wait time between chars sent
        'wait_line': 0.30,           # wait time after each "line"
    }

    @property
    def wait_byte(self):
        return SerialIO.TIMERS['wait_byte']

    @property
    def wait_line(self):
        return SerialIO.TIMERS['wait_line']

    class SerialError(Exception):
        """ Generic exception class for non-IO exceptions """
        def __init__(self, message):
            super().__init__(message=message)
            self.message = message

        def __str__(self):
            return 'SerialError<' + repr(self.message) + '>'

    def __init__(self, **kwargs):
        self.serial = copy.copy(SerialIO.PORT_DEFAULTS)
        self.serial.update(kwargs)
        self.port = None                # type serial.Serial
        self.receiver_thread = None
        self.receiver_running = False
        self.receive_queue = queue.Queue()
        self.receive_buffer = bytearray(b'')

    def findport(self, devroot):
        acmdevs = [dev for dev in os.listdir('/dev') if dev.startswith(devroot)]
        return '/dev/' + acmdevs[0] if acmdevs else None

    def open(self, **kwargs) -> bool:
        """ opens the serial port
            :param kwargs: additional parameters used to override
        """
        if self.port is None or not self.port.isOpen():
            self.serial.update(kwargs)
            params = copy.copy(self.serial)
            if params['port'] == 'auto':
                params['port'] = self.findport('ttyACM')
            self.port = serial.Serial(**params)
            self.port.setDTR()
            self.receiver_thread = threading.Thread(target=self.receiver)
            self.receiver_thread.start()
            return True
        return False

    def send(self, bytes2send: bytes) -> bool:
        """ send bytes (with no inter byte delay)
            :param bytes2send: bytes to send...
        """
        self.port.write(bytes2send)

    def timed_send(self, bytes2send: bytes) -> bool:
        """ send bytes with an inter byte delay and delay after line
        :param bytes2send: bytes to send...
        """
        print(bytes.decode(bytes2send), end="")
        if self.port is not None and self.port.isOpen():
            for ch in bytes2send:
                self.port.write(bytes(ch))
                time.sleep(self.wait_byte)
            time.sleep(self.wait_line)
            return True
        return False

    def receiver(self):
        """
        this function runs a dedicated receiver thread in order to
        (hopefully) cope with unbuffered input
        """
        self.receiver_running = True
        if self.port.isOpen():
            try:
                while self.receiver_running:
                    data = self.port.read(256)
                    self.receive_queue.put(data)
            except:
                self.port.close()
        else:
            time.sleep(1)
        self.receiver_running = False

    def stop_receiver(self):
        self.receiver_running = False

    def recv(self):
        # re-open here in case we got disconnected
        # otherwise this is benign
        self.open()
        # set the timer
        waituntil = self.port.timeout + time.time()
        while waituntil > time.time():
            if self.receiver_running:
                while not self.receive_queue.empty():
                    data = self.receive_queue.get()
                    self.receive_buffer += data
            if len(self.receive_buffer) > 0:
                ch = self.receive_buffer[0]
                del self.receive_buffer[0]
                return bytes([ch])
            time.sleep(0.05)
        return b''

    def recv_line(self, eol=b'\n') -> bytes:
        """ receive bytes from the serial port
        :param eol: end of line chars (any 1 matches
        :return: bytes read
        """
        bytes_read = b''
        while True:
            try:
                ch = self.recv()
                bytes_read += ch
                if ch in eol:
                    break
            except:
                break
        print(bytes.decode(bytes_read), end="")
        return bytes_read

    def expect(self, waitfor, multiline =False, timeout =0):
        """ simple expect interface, keep receiving until an expected set of bytes arrives
        :param waitfor: bytes to wait for
        :param multiline: don't stop searching at newline
        :param timeout: return false on timeout
        :return:
        """
        length = len(waitfor)
        bytes_read = b''
        matched = False
        ch = 0
        expire = time.time() + timeout if timeout else 0
        while multiline or ch != b'\n':
            try:
                ch = self.recv()
                if waitfor is not None and bytes_read[:length] == waitfor:
                    matched = True
                    break
                bytes_read += ch
                if expire and expire < time.time():
                    break
            except Exception as exc:
                break
        try:
            print(bytes.decode(bytes_read), end="")
        except UnicodeDecodeError:
            bytes_read = b''
        return matched

    def expect_send(self, waitfor: bytes, bytes2send: bytes =None):
        """ simple expect/send, same as expect, but optional send after
        :param waitfor: bytes to expect
        :param bytes2send: (optional) bytes to send when string is received
        """
        while not self.expect(waitfor):
            pass
        if bytes2send is not None:
            self.timed_send(bytes2send)

    def close(self):
        try:
            if self.receiver_running:
                self.receiver_running = False
            if self.port is not None and self.port.isOpen():
                self.port.close()
        except:
            pass

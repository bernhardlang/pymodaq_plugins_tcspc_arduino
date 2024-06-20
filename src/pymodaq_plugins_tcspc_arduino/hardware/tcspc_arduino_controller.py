import numpy as np
from PyQt5.QtSerialPort import QSerialPortInfo


class TcspcArduinoController:

    available_ports = { port.portName(): port \
                        for port in QSerialPortInfo.availablePorts() }
    baudrates = QSerialPortInfo.standardBaudRates()
    default_baudrate = 115200

    def __init__(self):
        self._baudrate = 115200
        self._timeout = 1
        self._threshold = 0.5
        self._bin_size = 0.05
        self._offset = 0.1
        self._n_bins = 100
        self._max_time = 0
        self._max_samples = 0
        self._refresh = 0.1
        self._lifetime = 20
        self._time_zero = 0.5
        self._count_rate = 10000
        self._dark_rate = 30000

    def connect(self):
        pass

    def disconnect(self):
        pass

    def get_x_axis(self):
        return np.linspace(self._offset,
                           self._offset + self._n_bins * self._bin_size,
                           self._n_bins)

    @property
    def baudrate(self):
        return self._baudrate

    @baudrate.setter
    def baudrate(self, b):
        self._baudrate = b

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, t):
        self._timeout = t

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, t):
        self._threshold = t

    @property
    def bin_size(self):
        return self._bin_size

    @bin_size.setter
    def bin_size(self, b):
        self._bin_size = b

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, o):
        self._offset = o

    @property
    def n_bins(self):
        return self._n_bins

    @n_bins.setter
    def n_bins(self, n):
        self._n_bins = n

    @property
    def max_time(self):
        return self._max_time

    @max_time.setter
    def max_time(self, t):
        self._max_time = t

    @property
    def max_samples(self):
        return self._max_samples

    @max_samples.setter
    def max_samples(self, s):
        self._max_samples = s

    @property
    def refresh(self):
        return self._refresh

    @refresh.setter
    def refresh(self, r):
        self._refresh = r

    @property
    def lifetime(self):
        return self._lifetime

    @lifetime.setter
    def lifetime(self, t):
        self._lifetime = t

    @property
    def time_zero(self):
        return self._time_zero

    @time_zero.setter
    def time_zero(self, z):
        self._time_zero = z

    @property
    def count_rate(self):
        return self._count_rate

    @count_rate.setter
    def count_rate(self, c):
        self._count_rate = c

    @property
    def dark_rate(self):
        return self._dark_rate

    @dark_rate.setter
    def dark_rate(self, d):
        self._dark_rate = d

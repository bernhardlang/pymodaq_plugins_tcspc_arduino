import numpy as np
import io
from serial import Serial
from time import sleep
from PyQt5.QtSerialPort import QSerialPortInfo
from pymodaq.utils.data import DataToExport


class TcspcArduinoController:

    available_ports = { port.portName(): port \
                        for port in QSerialPortInfo.availablePorts() }
    baudrates = QSerialPortInfo.standardBaudRates()
    default_baudrate = 115200

    TAGGER = 0
    SPC    = 1
    TCSPC  = 2

    def __init__(self):
        self.serial = None
        self.simulating = False
        self.port = '/dev/ttyACM0'
        self.baudrate = 115200
        self.timeout = 1
        self.read_waiting_time = 0
        self.is_acquiring = False
        self.mode = self.TCSPC
        self.max_time = 0
        self.max_counts = 0
        self._threshold = 0.5
        self._bin_size = 0.05
        self._offset = 0.1
        self._n_bins = 100
        self._refresh = 0.1
        self._lifetime = 20
        self._time_zero = 0.5
        self._count_rate = 10000
        self._dark_rate = 30000
        self.random_generator = np.random.default_rng()

    def connect(self):
        if len(self.port) > 0:
            if self.serial is not None:
                self.disconnect()
            try:
                self.serial = Serial("/dev/%s" % self.port, self.baudrate,
                                     timeout=self.timeout)
                self.sio = io.TextIOWrapper(io.BufferedRWPair(self.serial,
                                                              self.serial))
                self.simulating = False
            except:
                self.simulating = True
        else:
            self.simulating = True

    def disconnect(self):
        self.serial.close()
        self.sio = None
        self.serial = None

    def start_tcspc(self):
        self.is_acquiring = True
        self.total_hist = np.zeros(self._n_bins)
        if self.simulating == False:
            self.sio.write(r'record\r')
        self.start_time = datetime.now() if self._max_time > 0 else None

    def start_spc(self):
        self.is_acquiring = True
        if self.simulating == False:
            self.sio.write(r'rate\r')

    def stop(self):
        self.is_acquiring = False
        if self.simulating == False:
            self.sio.write(r'stop\r')

    def get_x_axis(self):
        return np.linspace(self._offset,
                           self._offset + self._n_bins * self._bin_size,
                           self._n_bins)

    def read_histogram(self):
        if self.simulating == True:
            sleep(self._refresh)
            counts = self.random_generator.poisson(self.simulation_data)
            return np.array(counts, dtype=float)

        hist = numpy.empty(self._n_bins)
        for i in range(self._n_bins):
            hist[i] = float(self.sio.readline())
        return hist
        
    def get_histogram(self):
        if self.simulating == False:
            self.serial.write('record 1\r')
        return self.read_histogram()

    def read_rate(self):
        if self.simulating == True:
            sleep(self._refresh)
            return float(self.random_generator.poisson(self.count_rate))
        return float(self.sio.readline())
        
    def get_rate(self):
        if self.simulating == False:
            self.serial.write('rate 1\r')
        return self.read_rate()

    def tcspc_loop(self):
        current_hist = self.read_histogram()
        self.total_hist += current_hist
            
    def spc_loop(self):
        current_rate = self.read_rate()
        dfp = DataFromPlugins(name='tcspc', data=current_rate, dim='Data0D',
                              labels=['counts'])
        self.dte_signal.emit(DataToExport('tcspc', data=[dfp]))

    def get_property(self, name):
        if self.is_acquiring == True:
            raise RuntimeError("Must not query property during acquisition")
        if self.simulating == True:
            return getattr(self, "_%s" % name)
        self.sio.write(r"%s\r", name)
        return self.sio.readline()
        
    def set_property(self, name, value):
        if self.is_acquiring == True:
            raise RuntimeError("Must not set property during acquisition")
        if self.simulating == True:
            setattr(self, "_%s" % name, value)
            if name in ['bin_size', 'offset', 'n_bins', 'lifetime', 'time_zero',
                        'count_rate', 'dark_rate']:
                self.update_simulation_data()
        else:
            self.sio.write(r"%s %s\r" % (name, str(value)))
        
    @property
    def threshold(self):
        return self.get_property('threshold')

    @threshold.setter
    def threshold(self, t):
        self.set_property('threshold', t)

    @property
    def bin_size(self):
        return self.get_property('bin_size')

    @bin_size.setter
    def bin_size(self, b):
        self.set_property('bin_size', b)
        if self.simulating == True:
            self.update_simulation_data()

    @property
    def offset(self):
        return self.get_property('offset')

    @offset.setter
    def offset(self, o):
        self.set_property('offset', o)
        if self.simulating == True:
            self.update_simulation_data()

    @property
    def n_bins(self):
        return self.get_property('n_bins')

    @n_bins.setter
    def n_bins(self, n):
        self.set_property('n_bins', n)
        if self.simulating == True:
            self.update_simulation_data()

    @property
    def refresh(self):
        return self.get_property('refresh')

    @refresh.setter
    def refresh(self, r):
        self.set_property('refresh', r)
        if self.simulating == True:
            self.update_simulation_data()

    @property
    def lifetime(self):
        return self.get_property('lifetime')

    @lifetime.setter
    def lifetime(self, r):
        self.set_property('lifetime', r)
        if self.simulating == True:
            self.update_simulation_data()
            
    @property
    def time_zero(self):
        return self.get_property('time_zero')

    @time_zero.setter
    def time_zero(self, r):
        self.set_property('time_zero', r)
        if self.simulating == True:
            self.update_simulation_data()
            
    @property
    def count_rate(self):
        return self.get_property('count_rate')

    @count_rate.setter
    def count_rate(self, r):
        self.set_property('count_rate', r)
        if self.simulating == True:
            self.update_simulation_data()
            
    @property
    def dark_rate(self):
        return self.get_property('dark_rate')

    @dark_rate.setter
    def dark_rate(self, r):
        self.set_property('dark_rate', r)

    def update_simulation_data(self):
        bin_size = self._bin_size * 1e-6
        offset = self._offset * 1e-6
        time_scale = np.linspace(offset + 0.5 * bin_size,
                                 offset + bin_size * (self._n_bins - 0.5),
                                 self._n_bins)
        lifetime = self.lifetime * 1e-6
        time_zero = self.time_zero * 1e-6
        dark = self.dark_rate * bin_size
        self.simulation_data = \
            np.where(time_scale >= time_zero,
                     dark + self.count_rate * np.exp(-time_scale / lifetime),
                     dark)

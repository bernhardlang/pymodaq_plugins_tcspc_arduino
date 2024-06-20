import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, \
    comon_parameters, main
from pymodaq.utils.parameter import Parameter
from pymodaq.utils.parameter.utils import iter_children
from pymodaq_plugins_tcspc_arduino.hardware.tcspc_arduino_controller \
    import TcspcArduinoController


class DAQ_1DViewer_tcspc_arduino(DAQ_Viewer_base):
    """ Instrument plugin class for a 1D viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s 
    DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and 
    the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * The set of instruments that should be compatible with this 
          instrument plugin.
        * With which instrument it has actually been tested.
        * The version of PyMoDAQ during the test.
        * The version of the operating system.
        * Installation instructions: what manufacturer’s drivers should be 
          installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, 
        in general a python wrapper around the hardware library.
         
    # TODO add your particular attributes here if any

    """
    # live_mode_available = True
    device_ids = list(TcspcArduinoController.available_ports.keys())
    default_device_id = \
        device_ids[0] if len(device_ids) > 0 else ''
    baudrates = TcspcArduinoController.baudrates

    params = comon_parameters+[
        { 'title': 'Device identifier', 'name': 'device_id', 'type': 'str',
          'limits': device_ids, 'value': default_device_id },
        { 'title': 'Baudrate', 'name': 'baudrate', 'type': 'list',
          'limits': baudrates,
          'value': TcspcArduinoController.default_baudrate },
        { 'title': 'Timeout (s)', 'name': 'timeout', 'type': 'float', 'min': 0.,
          'value': 1. },
        { 'title': 'Trigger threshold (mV)', 'name': 'threshold',
          'type': 'float', 'min': -5., 'max': 5. },
        { 'title': 'Bin size (µs)', 'name': 'bin_size', 'type': 'float',
          'min': 0.03 },
        { 'title': 'Offset (µs)', 'name': 'offset', 'type': 'float',
          'min': 0.03 },
        { 'title': 'Number of bins', 'name': 'n_bins', 'type': 'int',
          'min': 10, 'max': 1000 },
        { 'title': 'Accumulation time (s)', 'name': 'max_time', 'type': 'float',
          'min': 0. },
        { 'title': 'Maximum samples', 'name': 'max_samples',
          'type': 'int', 'min': 0 },
        { 'title': 'Refresh time (s)', 'name': 'refresh', 'type': 'float',
          'min': 0.1 },
        ]

    if len(device_ids) == 0: # simulation
        params = params + [
            { 'title': 'Lifetime (µs)', 'name': 'lifetime', 'type': 'float',
              'min': 40., 'max': 1000, 'value': 350. },
            { 'title': 'Time zero (µs)', 'name': 'time_zero', 'type': 'float',
              'min': 0., 'max': 10, 'value': 0.12 },
            { 'title': 'Count rate (Hz)', 'name': 'count_rate', 'type': 'int',
              'min': 1, 'max': 65535 },
            { 'title': 'Dark rate (Hz)', 'name': 'dark_rate', 'type': 'int',
              'min': 1, 'max': 65535 },
        ]
        
    def ini_attributes(self):
        self.controller: TcspcArduinoController = None


    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been
            changed by the user.
        """

        if param.name() == "device_id":
            self.controller.device_id = param.value()
        elif param.name() == "baudrate":
            self.controller.baudrate = param.value()
        elif param.name() == "timeout":
            self.controller.timeout = param.value()
        if param.name() == "threshold":
            self.controller.threshold = param.value()
        elif param.name() == "bin_size":
            self.controller.bin_size = param.value()
        elif param.name() == "offset":
            self.controller.offset = param.value()
        elif param.name() == "n_bins":
            self.controller.n_bins = param.value()
        elif param.name() == "max_time":
            self.controller.max_time = param.value()
        elif param.name() == "max_samples":
            self.controller.max_samples = param.value()
        elif param.name() == "refresh":
            self.controller.refresh = param.value()

        if param.name() in ["bin_size", "offset", "n_bins"]:
            self.emit_new_x_axis()

        if len(self.device_ids) == 0: # simulation
            if param.name() == "lifetime":
                self.controller.lifetime = param.value()
            elif param.name() == "time_zero":
                self.controller.time_zero = param.value()
            elif param.name() == "count_rate":
                self.controller.count_rate = param.value()
            elif param.name() == "dark_rate":
                self.controller.dark_rate = param.value()

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one 
            actuator/detector by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        self.ini_detector_init(old_controller=controller,
                               new_controller=TcspcArduinoController())
        if len(self.device_ids) == 0: # simulation
            for key in ['lifetime', 'time_zero', 'count_rate', 'dark_rate' ]:
                self.commit_settings(Parameter(name=key,
                                               value=self.settings[key]))
        self.controller.connect()
        self.emit_new_x_axis()

        info = "TCSPC Arduino successfully initialised"
        initialized = True
        return info, initialized

    def emit_new_x_axis(self):
        data_x_axis = self.controller.get_x_axis()
        self.x_axis = Axis(data=data_x_axis, label='Time', units='µs')
        n_bins = self.controller.n_bins
        dfp = DataFromPlugins(name='TCSPC',
                              data=[np.zeros(n_bins), np.zeros(n_bins)],
                              dim='Data1D', labels=['current', 'total'],
                              axes=[self.x_axis])
        self.dte_signal_temp.emit(DataToExport(name='tcspc_arduino',
                                               data=[dfp]))
        
    def close(self):
        """Terminate the communication protocol"""
        self.contoller.disconnect()

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, 
            self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        data_tot = self.controller.get_histograms()
        dfp = DataFromPlugins(name='TCSPC', data=data_tot,
                              dim='Data1D', labels=['current', 'total'],
                              axes=[self.x_axis])
        self.dte_signal.emit(DataToExport('tcspc_arduino', data=[dfp]))


    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        self.controller.stop()
        return ''


if __name__ == '__main__':
    main(__file__)

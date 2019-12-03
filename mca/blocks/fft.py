import numpy as np

import mca.framework
from mca.framework import validator
from mca.language import _


class FFT(mca.framework.Block):
    """Block class which calculates the FFT of the input signal.

    This block has one input and one output.
    """
    name = "FFTBlock"
    description = _("Computes the FFT of the input signal.")

    def __init__(self, **kwargs):
        super().__init__()

        self._new_output(
            meta_data=mca.framework.data_types.MetaData(
                "Test", _("Frequency"), "f", "Hz", _("Voltage"), "U", "V"
            )
        )
        self._new_input()
        self.read_kwargs(kwargs)

    def _process(self):
        if self.check_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data
        ordinate = np.fft.fft(input_signal.ordinate)
        increment = 1 / (
                    input_signal.increment * input_signal.values) * 2 * np.pi
        values = input_signal.values
        self.outputs[0].data = mca.framework.data_types.Signal(
            meta_data=self.outputs[0].meta_data,
            abscissa_start=0,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )

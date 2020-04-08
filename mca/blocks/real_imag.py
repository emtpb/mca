import copy

import mca.framework
from mca.framework import validator
from mca.language import _


class RealImag(mca.framework.Block):
    """Block class which separates the real and imaginary part of the input
    signal in two output signals.

    This block has one input and two outputs. First output has the real part
    and second output has the imaginary part.
    """
    name = "RealImagBlock"
    description = _("Divides the real and imaginary part of "
                    "the input signal into two output signals.")

    def __init__(self, **kwargs):
        super().__init__()

        self._new_output(
            meta_data=mca.framework.data_types.MetaData(
                "Test", _("Time"), "t", "s", _("Voltage"), "U", "V"
            ),
            name=_("Real part")
        )
        self._new_output(
            meta_data=mca.framework.data_types.MetaData(
                "Test", _("Time"), "t", "s", _("Voltage"), "U", "V"
            ),
            name=_("Imaginary part")
        )
        self._new_input()
        self.read_kwargs(kwargs)

    def _process(self):
        if self.check_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)
        real_signal = copy.deepcopy(self.inputs[0].data)
        real_signal.ordinate = real_signal.ordinate.real
        imag_signal = copy.deepcopy(self.inputs[0].data)
        imag_signal.ordinate = imag_signal.ordinate.imag
        self.outputs[0].data = real_signal
        self.outputs[1].data = imag_signal

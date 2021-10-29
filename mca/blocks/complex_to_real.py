import copy

from mca.framework import validator, data_types, Block
from mca.language import _


class ComplexToReal(Block):
    """Separates the real and imaginary part of the input
    signal in two signals.

    First output yields the real part and second output yields the imaginary
    part.
    """
    name = _("ComplexToReal")
    description = _("Separates the real and imaginary part of "
                    "the input signal into two output signals. First output "
                    "yields the real part and second output yields the "
                    "imaginary part.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output(name=_("Real part"))
        self.new_output(name=_("Imaginary part"))
        self.new_input()

    def setup_parameters(self):
        pass

    def _process(self):
        if self.all_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)

        real_signal = copy.copy(self.inputs[0].data)
        real_signal.ordinate = real_signal.ordinate.real
        imag_signal = copy.copy(self.inputs[0].data)
        imag_signal.ordinate = imag_signal.ordinate.imag

        self.outputs[0].data = real_signal
        self.outputs[0].data.metadata = self.outputs[0].get_metadata(
            real_signal.metadata)
        self.outputs[1].data = imag_signal
        self.outputs[1].data.metadata = self.outputs[1].get_metadata(
            imag_signal.metadata)

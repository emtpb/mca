import numpy as np

from mca.framework import validator, data_types, Block
from mca.language import _


class AutoCorrelation(Block):
    """Computes the auto correlation of the input signal."""
    name = _("ACF")
    description = _(
        "Computes the auto correlation function of the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        pass

    def _process(self):
        if self.all_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data
        unit_o = self.inputs[0].metadata.unit_o ** 2
        unit_a = self.inputs[0].metadata.unit_a
        ordinate = np.correlate(input_signal.ordinate, input_signal.ordinate,
                                mode="full")
        abscissa_start = input_signal.abscissa_start - (
                    input_signal.values - 1) * input_signal.increment

        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=input_signal.values * 2 - 1,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        self.outputs[0].external_metadata = data_types.MetaData(None, unit_a,
                                                                unit_o)

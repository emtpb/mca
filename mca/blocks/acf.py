import numpy as np

from mca.framework import Block, data_types, util
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

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Calculate the ordinate
        ordinate = np.correlate(input_signal.ordinate, input_signal.ordinate,
                                mode="full")
        # Calculate the abscissa start
        abscissa_start = input_signal.abscissa_start - (
                    input_signal.values - 1) * input_signal.increment
        # Calculate the amount of values
        values = input_signal.values * 2 - 1
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        # Calculate units for abscissa and ordinate
        unit_o = self.inputs[0].metadata.unit_o ** 2
        unit_a = self.inputs[0].metadata.unit_a
        # Apply new metadata to the output
        self.outputs[0].external_metadata = data_types.MetaData(
            name=None, unit_a=unit_a, unit_o=unit_o
        )

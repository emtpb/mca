import numpy as np

from mca.framework import data_types, util, Block
from mca.language import _


class CrossCorrelation(Block):
    """Computes the cross correlation of the input signal."""
    name = _("CCF")
    description = _(
        "Computes the cross correlation function of the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()
        self.new_input()

    def setup_parameters(self):
        pass

    @util.abort_any_inputs_empty
    @util.validate_type_signal
    @util.validate_units(abscissa=True)
    @util.validate_intervals
    def _process(self):
        unit_o = self.inputs[0].metadata.unit_o * self.inputs[1].metadata.unit_o
        unit_a = 1 / self.inputs[0].metadata.unit_a
        metadata = data_types.MetaData(None, unit_a, unit_o)

        first_signal = self.inputs[0].data
        second_signal = self.inputs[1].data

        ccf = np.correlate(first_signal.ordinate, second_signal.ordinate,
                           mode="full")
        abscissa_start = first_signal.abscissa_start - (
                    second_signal.values - 1) * second_signal.increment
        values = first_signal.values + second_signal.values - 1

        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=first_signal.increment,
            ordinate=ccf,
        )
        self.outputs[0].external_metadata = metadata

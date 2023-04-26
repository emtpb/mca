import copy
import numpy as np

from mca.framework import data_types, DynamicBlock, util
from mca.language import _


class Adder(DynamicBlock):
    """Adds multiple signals to one new signal."""
    name = _("Adder")
    description = _("Adds multiple signals to one signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.dynamic_input = (1, None)
        self.new_output()
        self.new_input()
        self.new_input()

    def setup_parameters(self):
        pass

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    @util.validate_units(abscissa=True, ordinate=True)
    @util.validate_intervals
    def _process(self):
        signals = [copy.copy(i.data) for i in self.inputs if i.data]
        modified_signals = util.fill_zeros(signals)
        ordinate = np.zeros(modified_signals[0].values)
        for sgn in modified_signals:
            ordinate += sgn.ordinate
        abscissa_start = modified_signals[0].abscissa_start
        values = modified_signals[0].values
        increment = modified_signals[0].increment
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate)
        self.outputs[0].external_metadata = self.inputs[0].metadata

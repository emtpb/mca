import copy
import numpy as np

from mca.framework import validator, data_types, DynamicBlock, helpers
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

    def _process(self):
        if self.all_inputs_empty():
            return
        for i in self.inputs:
            validator.check_type_signal(i.data)
        signals = [copy.copy(i.data) for i in self.inputs if i.data]
        metadatas = [copy.copy(i.metadata) for i in self.inputs if i.metadata]
        abscissa_units = [metadata.unit_a for metadata in metadatas]
        ordinate_units = [metadata.unit_o for metadata in metadatas]
        validator.check_same_units(abscissa_units)
        validator.check_same_units(ordinate_units)
        validator.check_intervals(signals)

        modified_signals = helpers.fill_zeros(signals)

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

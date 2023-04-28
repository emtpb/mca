import copy

import numpy as np

from mca.framework import DynamicBlock, data_types, util
from mca.language import _


class Multiplier(DynamicBlock):
    """Multiplies the input signals with each other."""
    name = _("Multiplier")
    description = _("Multiplies the input signals with each other.")
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
    @util.validate_units(abscissa=True)
    @util.validate_intervals
    def process(self):
        # Read the input data
        signals = [copy.copy(i.data) for i in self.inputs if i.data]
        # Read the input metadata
        metadatas = [copy.copy(i.metadata) for i in self.inputs if i.metadata]
        # Fill the signals with zeros so their lengths match
        matched_signals = util.fill_zeros(signals)
        # Initialize the ordinate and the units
        ordinate = np.ones(matched_signals[0].values)
        unit_a = metadatas[0].unit_a
        unit_o = 1
        # Calculate the ordinate and the ordinate unit
        for sgn, metadata in zip(matched_signals, metadatas):
            ordinate *= sgn.ordinate
            unit_o *= metadata.unit_o
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=matched_signals[0].abscissa_start,
            values=matched_signals[0].values,
            increment=matched_signals[0].increment,
            ordinate=ordinate,
        )
        # Apply new metadata to the output
        self.outputs[0].process_metadata = data_types.MetaData(
            name=None, unit_a=unit_a, unit_o=unit_o
        )

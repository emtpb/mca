import copy

import numpy as np

from mca.framework import validator, data_types, DynamicBlock, util
from mca.language import _


class Multiplier(DynamicBlock):
    """Multiplies the input signals with each other."""
    name = _("Multiplier")
    description = _("Multiplies the input signals with each other.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.dynamic_input = (1, None)
        self.new_input()
        self.new_input()

    def setup_parameters(self):
        pass

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    @util.validate_units(abscissa=True)
    @util.validate_intervals
    def _process(self):
        signals = [copy.copy(i.data) for i in self.inputs if i.data]
        metadatas = [copy.copy(i.metadata) for i in self.inputs if i.metadata]

        matched_signals = util.fill_zeros(signals)
        ordinate = np.ones(matched_signals[0].values)
        unit_a = metadatas[0].unit_a
        unit_o = 1
        for sgn, metadata in zip(matched_signals, metadatas):
            ordinate *= sgn.ordinate
            unit_o *= metadata.unit_o
        metadata = data_types.MetaData(None, unit_a, unit_o)
        abscissa_start = matched_signals[0].abscissa_start
        values = matched_signals[0].values
        increment = matched_signals[0].increment
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
        self.outputs[0].external_metadata = metadata

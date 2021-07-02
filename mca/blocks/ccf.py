from mca.framework import validator, data_types, Block
from mca.language import _

import numpy as np
from copy import deepcopy


class CrossCorrelation(Block):
    """Computes the cross correlation of the input signal."""
    name = _("CrossCorrelation")
    description = _("Computes the cross correlation of the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self._new_output(meta_data=data_types.default_meta_data())
        self._new_input()
        self._new_input()

    def setup_parameters(self):
        pass

    def _process(self):
        if self.check_any_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)
        validator.check_type_signal(self.inputs[1].data)
        validator.check_same_units([self.inputs[0].data.meta_data.unit_a,
                                   self.inputs[1].data.meta_data.unit_a])
        first_signal = self.inputs[0].data
        second_signal = self.inputs[1].data
        ordinate = np.correlate(first_signal.ordinate, second_signal.ordinate,
                                mode="full")
        abscissa_start = first_signal.abscissa_start - (second_signal.values-1)*second_signal.increment
        meta_data = deepcopy(first_signal.meta_data)
        unit_o = first_signal.meta_data.unit_o * second_signal.meta_data.unit_o
        meta_data.unit_o = unit_o
        meta_data.quantity_o = unit_o.quantity
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(meta_data),
            abscissa_start=abscissa_start,
            values=first_signal.values*2-1,
            increment=first_signal.increment,
            ordinate=ordinate,
        )
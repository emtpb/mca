from mca.framework import validator, data_types, parameters, Block
from mca.language import _

import numpy as np


class Zerofill(Block):
    """Adds dead time or zero padding to the input signal."""
    name = _("Zerofill")
    description = _("Adds dead time and zero padding to the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self._new_output()
        self._new_input()

    def setup_parameters(self):
        self.parameters.update({
            "dtime_values": parameters.IntParameter(
                _("Dead Time Values"), min_=0, value=0
            ),
            "zpad_values": parameters.IntParameter(
                _("Zero Padding Values"), min_=0, value=0)})

    def _process(self):
        if self.check_all_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)

        dtime_values = self.parameters["dtime_values"].value
        zpad_values = self.parameters["zpad_values"].value

        input_signal = self.inputs[0].data
        ordinate = np.concatenate((np.zeros(dtime_values),
                                   input_signal.ordinate, np.zeros(zpad_values)))
        values = dtime_values + zpad_values + input_signal.values
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(input_signal.meta_data),
            abscissa_start=input_signal.abscissa_start,
            values=values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )

import numpy as np

from mca.framework import Block, data_types, parameters, util
from mca.language import _


class Zerofill(Block):
    """Adds dead time or zero padding to the input signal."""
    name = _("Zerofill")
    description = _("Adds dead time and zero padding to the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters["dtime_values"] = parameters.IntParameter(
                name=_("Dead Time Values"), min_=0, default=0
        )
        self.parameters["zpad_values"] = parameters.IntParameter(
                name=_("Zero Padding Values"), min_=0, default=0
        )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        dtime_values = self.parameters["dtime_values"].value
        zpad_values = self.parameters["zpad_values"].value
        # Calculate the ordinate
        ordinate = np.concatenate((np.zeros(dtime_values),
                                   input_signal.ordinate,
                                   np.zeros(zpad_values)))
        # Calculate the amount of values
        values = dtime_values + zpad_values + input_signal.values
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        # Apply metadata from the input to the output
        self.outputs[0].external_metadata = self.inputs[0].metadata

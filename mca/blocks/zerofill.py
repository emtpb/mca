import numpy as np

from mca.framework import Block, data_types, parameters, util


class Zerofill(Block):
    """Adds dead time or zero padding to the input signal."""
    name = "Zerofill"
    description = "Adds dead time and zero padding to the input signal."
    tags = ("Processing",)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters["dtime_values"] = parameters.IntParameter(
                name="Dead Time Values", min_=0, default=0
        )
        self.parameters["shift_dead"] = parameters.BoolParameter(
            name="Shift the signal by the dead time", default=False)
        self.parameters["zpad_values"] = parameters.IntParameter(
                name="Zero Padding Values", min_=0, default=0
        )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        dtime_values = self.parameters["dtime_values"].value
        shift_dead = self.parameters["shift_dead"].value
        zpad_values = self.parameters["zpad_values"].value
        # Calculate the ordinate
        ordinate = np.concatenate((np.zeros(dtime_values),
                                   input_signal.ordinate,
                                   np.zeros(zpad_values)))
        # Calculate the amount of values
        values = dtime_values + zpad_values + input_signal.values

        if not shift_dead:
            abscissa_start = input_signal.abscissa_start - dtime_values*input_signal.increment
        else:
            abscissa_start = input_signal.abscissa_start
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = self.inputs[0].metadata

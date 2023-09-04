from mca.framework import Block, data_types, parameters, util

import numpy as np


class DownSample(Block):
    """Downsample the input signal by taking only nth-data point.
    The overall length of the signal approximately stays the same.
    """
    name = "Downsample"
    description = "Downsample the input signal by taking only nth-data point. " \
                  "The overall length of the signal approximately stays " \
                  "the same."
    tags = ("Processing",)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters["step"] = parameters.IntParameter(name="Step",
                                                          min_=1,
                                                          default=1,
                                                          description="Step between the data points to sample."
                                                                      " This can only be positive Integer values starting from 1"
                                                          )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        step = self.parameters["step"].value

        ordinate = input_signal.ordinate[::step]
        increment = input_signal.increment * step
        values = int(np.ceil(input_signal.values / step))

        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = self.inputs[0].metadata
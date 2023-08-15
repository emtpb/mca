import numpy as np

from mca.framework import Block, data_types, util


class CrossCorrelation(Block):
    """Computes the cross correlation of the input signal."""
    name = "CCF"
    description = "Computes the cross correlation function of the input signal."
    tags = ("Processing",)
    references = {"numpy.correlate":
        "https://numpy.org/doc/1.25/reference/generated/numpy.correlate.html"}

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
    def process(self):
        # Read the input data
        first_signal = self.inputs[0].data
        second_signal = self.inputs[1].data
        # Calculate the ordinate
        ccf = np.correlate(first_signal.ordinate, second_signal.ordinate,
                           mode="full")
        # Calculate the abscissa start
        abscissa_start = first_signal.abscissa_start - (
                    second_signal.values - 1) * second_signal.increment
        # Calculate the amount of values
        values = first_signal.values + second_signal.values - 1
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=first_signal.increment,
            ordinate=ccf,
        )
        # Calculate units for abscissa and ordinate
        unit_o = self.inputs[0].metadata.unit_o * self.inputs[1].metadata.unit_o
        unit_a = 1 / self.inputs[0].metadata.unit_a
        # Apply new metadata to the output
        self.outputs[0].process_metadata = data_types.MetaData(
            name=None, unit_a=unit_a,unit_o=unit_o
        )

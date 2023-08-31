from mca.framework import Block, data_types, parameters, util

from scipy.signal import fftconvolve


class Convolution(Block):
    """Computes the convolution of the two input signals."""
    name = "Convolution"
    description = "Computes the convolution of the two input signals."
    tags = ("Processing",)
    references = {"numpy.convolve": "https://numpy.org/doc/stable/reference/generated/numpy.convolve.html"}

    def setup_io(self):
        self.new_output()
        self.new_input()
        self.new_input()

    def setup_parameters(self):
        self.parameters["mode"] = parameters.ChoiceParameter(
            name="Mode", choices=(("full", "Full"),
                                  ("same", "Same"),
                                  ("valid", "Valid")),
                                  default="full",
                                  description=("Full: Returns the full convolution with the length of M+N-1.\n"
                                               "Same: Returns the convolution of length max(N,M).\n"
                                               "Valid: Returns the convolution only where both input signals fully overlap.\n"),
                                  )

    @util.abort_any_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        first_signal, second_signal = self.inputs[0].data, self.inputs[1].data
        # Read the parameters
        mode = self.parameters["mode"].value
        # Calculate the ordinate
        ordinate = fftconvolve(first_signal.ordinate, second_signal.ordinate, mode=mode)
        if mode == "full":
            abscissa_start = first_signal.abscissa_start - (second_signal.values-1)*second_signal.increment
        elif mode == "same":
            abscissa_start = first_signal.abscissa_start - (second_signal.values-1)*second_signal.increment/2
        else:
            abscissa_start = first_signal.abscissa_start
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=len(ordinate),
            increment=first_signal.increment,
            ordinate=ordinate,
        )
        # Calculate units for abscissa and ordinate
        unit_o = self.inputs[0].metadata.unit_o * self.inputs[1].metadata.unit_o
        unit_a = self.inputs[0].metadata.unit_a
        # Apply new metadata to the output
        self.outputs[0].process_metadata = data_types.MetaData(
            name=None, unit_a=unit_a,unit_o=unit_o
        )
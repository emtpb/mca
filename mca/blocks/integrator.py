import numpy as np
from scipy import integrate

from mca.framework import Block, data_types, parameters, util


class Integrator(Block):
    """Computes the numerical integration of the input signal."""
    name = "Integrator"
    description = "Computes the numerical integration of the input signal."
    tags = ("Processing",)
    references = {"scipy.integrate.cumulative_trapezoid":
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.cumulative_trapezoid.html",
        "numpy.cumsum":
        "https://numpy.org/doc/stable/reference/generated/numpy.cumsum.html"}

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters["int_rule"] = parameters.ChoiceParameter(
                name="Integration rule",
                choices=(("trapz", "Trapezoidal"),
                         ("rect", "Rectangular")),
                default="trapz",
        )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        int_rule = self.parameters["int_rule"].value
        # Calculate the ordinate
        if int_rule == "trapz":
            ordinate_int = integrate.cumulative_trapezoid(y=input_signal.ordinate,
                                              dx=input_signal.increment,
                                              initial=0)
        elif int_rule == "rect":
            ordinate_int = np.cumsum(
                input_signal.ordinate) * input_signal.increment
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate_int,
        )
        # Calculate units for abscissa and ordinate
        unit_a = self.inputs[0].metadata.unit_a
        unit_o = self.inputs[0].metadata.unit_o * self.inputs[0].metadata.unit_a
        # Apply new metadata to the output
        self.outputs[0].process_metadata = data_types.MetaData(
            name=None, unit_a=unit_a, unit_o=unit_o
        )

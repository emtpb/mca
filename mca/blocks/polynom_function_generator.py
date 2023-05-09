import numpy as np

from mca.framework import Block, data_types, parameters, util


class PolynomGenerator(Block):
    """Generates a signal based on a polynomial function with the maximum
    order of 5.
    """
    name = "PolynomGenerator"
    description = ("Generates a signal based on a polynomial function "
                    "with the maximum order of 5 (a*x⁵+b*x⁴+c*x³+d*x²+e*x¹+f*x⁰)")
    tags = ("Generating",)

    def setup_io(self):
        self.new_output(user_metadata_required=True)

    def setup_parameters(self):
        self.parameters["order_0"] = parameters.FloatParameter(
            name="Factor of the 0th order (x⁰)", default=0)
        self.parameters["order_1"] = parameters.FloatParameter(
            name="Factor of the 1st order (x¹)", default=0)
        self.parameters["order_2"] = parameters.FloatParameter(
            name="Factor of the 2nd order (x²)", default=0)
        self.parameters["order_3"] = parameters.FloatParameter(
            name="Factor of the 3rd order (x³)", default=0)
        self.parameters["order_4"] = parameters.FloatParameter(
            name="Factor of the 4th order (x⁴)", default=0)
        self.parameters["order_5"] = parameters.FloatParameter(
            name="Factor of the 5th order (x⁵)", default=0)
        abscissa = util.create_abscissa_parameter_block()
        self.parameters["abscissa"] = abscissa

    def process(self):
        # Read parameters values
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        a = self.parameters["order_5"].value
        b = self.parameters["order_4"].value
        c = self.parameters["order_3"].value
        d = self.parameters["order_2"].value
        e = self.parameters["order_1"].value
        f = self.parameters["order_0"].value
        # Calculate the abscissa
        abscissa = (
            np.linspace(
                abscissa_start, abscissa_start + (values - 1) * increment,
                values
            )
        )
        # Calculate the ordinate
        ordinate = a*abscissa**5 + b*abscissa**4 + c*abscissa**3 + \
                   d*abscissa**2 + e*abscissa + f
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start,
            values,
            increment,
            ordinate,
        )

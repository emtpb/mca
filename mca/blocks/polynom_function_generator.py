import numpy as np

from mca.framework import data_types, Block, parameters, helpers
from mca.language import _


class PolynomGenerator(Block):
    """Generates a signal based on a polynomial function with the maximum
    order of 5.
    """
    name = _("PolynomGenerator")
    description = _("Generates a signal based on a polynomial function "
                    "with the maximum order of 5 (a*x⁵+b*x⁴+c*x³+d*x²+e*x¹+f*x⁰)")
    tags = (_("Generating"),)

    def setup_io(self):
        self.new_output(
            metadata_input_dependent=False,
            ordinate_metadata=True,
            abscissa_metadata=True,
        )

    def setup_parameters(self):
        abscissa = helpers.create_abscissa_parameter_block()
        self.parameters["order_0"] = parameters.FloatParameter(
            name=_("Factor of the 0th order (x⁰)"), default=0)
        self.parameters["order_1"] = parameters.FloatParameter(
            name=_("Factor of the 1st order (x¹)"), default=0)
        self.parameters["order_2"] = parameters.FloatParameter(
            name=_("Factor of the 2nd order (x²)"), default=0)
        self.parameters["order_3"] = parameters.FloatParameter(
            name=_("Factor of the 3rd order (x³)"), default=0)
        self.parameters["order_4"] = parameters.FloatParameter(
            name=_("Factor of the 4th order (x⁴)"), default=0)
        self.parameters["order_5"] = parameters.FloatParameter(
            name=_("Factor of the 5th order (x⁵)"), default=0)
        self.parameters["abscissa"] = abscissa

    def _process(self):
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        a = self.parameters["order_5"].value
        b = self.parameters["order_4"].value
        c = self.parameters["order_3"].value
        d = self.parameters["order_2"].value
        e = self.parameters["order_1"].value
        f = self.parameters["order_0"].value

        abscissa = (
            np.linspace(
                abscissa_start, abscissa_start + (values - 1) * increment,
                values
            )
        )

        ordinate = a*abscissa**5 + b*abscissa**4 + c*abscissa**3 + \
                   d*abscissa**2 + e*abscissa + f

        self.outputs[0].data = data_types.Signal(
            self.outputs[0].get_metadata(None),
            abscissa_start,
            values,
            increment,
            ordinate,
        )
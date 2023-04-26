import numpy as np
from scipy import integrate

from mca.framework import data_types, util, Block, parameters
from mca.language import _


class Integrator(Block):
    """Computes the numerical integration of the input signal."""
    name = _("Integrator")
    description = _("Computes the numerical integration of the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters.update({
            "int_rule": parameters.ChoiceParameter(
                _("Integration rule"),
                [("trapz", _("Trapezoidal")), ("rect", _("Rectangular"))],
                default="trapz",
            )})

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
        input_signal = self.inputs[0].data
        int_rule = self.parameters["int_rule"].value

        unit_a = self.inputs[0].metadata.unit_a
        unit_o = self.inputs[0].metadata.unit_o * self.inputs[0].metadata.unit_a
        metadata = data_types.MetaData(None, unit_a=unit_a, unit_o=unit_o)

        if int_rule == "trapz":
            ordinate_int = integrate.cumtrapz(y=input_signal.ordinate,
                                              dx=input_signal.increment,
                                              initial=0)
        elif int_rule == "rect":
            ordinate_int = np.cumsum(
                input_signal.ordinate) * input_signal.increment

        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate_int,
        )

        self.outputs[0].external_metadata = metadata

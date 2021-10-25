from scipy import integrate
import numpy as np

from mca.framework import validator, data_types, Block, parameters
from mca.language import _


class Integrator(Block):
    """Computes the numerical integration of the input signal."""
    name = _("Integrator")
    description = _("Computes the numerical integration of the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self._new_output()
        self._new_input()

    def setup_parameters(self):
        self.parameters.update({
            "int_rule": parameters.ChoiceParameter(
                _("Integration rule"),
                [("trapz", _("Trapezoidal")), ("rect", _("Rectangular"))],
                default="trapz",
            )})

    def _process(self):
        if self.check_all_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data
        int_rule = self.parameters["int_rule"].value
        if int_rule == "trapz":
            ordinate_int = integrate.cumtrapz(y=input_signal.ordinate,
                                              dx=input_signal.increment,
                                              initial=0)
        elif int_rule == "rect":
            ordinate_int = np.cumsum(input_signal.ordinate) * input_signal.increment
        unit_a = input_signal.meta_data.unit_a
        unit_o = input_signal.meta_data.unit_o * input_signal.meta_data.unit_a
        meta_data = data_types.MetaData(None, unit_a=unit_a, unit_o=unit_o)
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(meta_data),
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate_int,
        )

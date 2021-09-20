from scipy.interpolate import interp1d
import numpy as np

from mca.framework import validator, data_types, Block, helpers, parameters
from mca.language import _
from mca import exceptions


class Interpolate(Block):
    """Interpolates the input signal by defining a new abscissa. The
    range of the new abscissa has to within the range of the abscissa of the
    input signal.
    """
    name = _("Interpolate")
    description = _("Interpolates the input signal by defining a new abscissa."
                    " The range of the new abscissa has to within the "
                    "range of the abscissa of the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self._new_output(meta_data=data_types.default_meta_data())
        self._new_input()

    def setup_parameters(self):
        abscissa = helpers.create_abscissa_parameter_block()
        abscissa.name = _("New abscissa")
        self.parameters.update(
            {"abscissa": abscissa,
             "interpol_kind": parameters.ChoiceParameter(
                 name=_("Interpolation kind"),
                 choices=[("linear", _("Linear")), ("slinear", _("SLinear")),
                          ("quadratic", _("Quadratic")), ("cubic", _("Cubic")),
                          ("zero", _("Zero")), ("previous", _("Previous")),
                          ("next", _("Next")), ("nearest", _("Nearest"))
                          ],
                 value="linear"
                )
             })

    def _process(self):
        if self.check_all_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data
        new_abscissa_start = self.parameters["abscissa"].parameters[
            "start"].value
        new_increment = self.parameters["abscissa"].parameters[
            "increment"].value
        new_values = self.parameters["abscissa"].parameters[
            "values"].value
        interpol_kind = self.parameters["interpol_kind"].value

        input_signal_abscissa = np.linspace(input_signal.abscissa_start,
                    input_signal.abscissa_start + input_signal.increment * (
                                input_signal.values - 1), input_signal.values)
        new_abscissa = np.linspace(new_abscissa_start,
                                   new_abscissa_start + new_increment*(
                                           new_values - 1),
                                   new_values)
        if new_abscissa_start < input_signal.abscissa_start:
            raise exceptions.ParameterValueError("New abscissa start is below "
                                                 "abscissa start of the input "
                                                 "signal.")
        if new_abscissa[-1] > input_signal_abscissa[-1]:
            raise exceptions.ParameterValueError("New abscissa end is above "
                                                 "the abscissa end of the "
                                                 "input signal.")

        f = interp1d(x=input_signal_abscissa, y=input_signal.ordinate,
                     kind=interpol_kind)
        new_ordinate = f(new_abscissa)
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(input_signal.meta_data),
            abscissa_start=new_abscissa_start,
            values=new_values,
            increment=new_increment,
            ordinate=new_ordinate,
        )

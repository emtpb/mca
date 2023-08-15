import numpy as np
from scipy.interpolate import interp1d

from mca import exceptions
from mca.framework import Block, data_types, parameters, util


class Interpolate(Block):
    """Interpolates the input signal by defining a new abscissa. The
    range of the new abscissa has to within the range of the abscissa of the
    input signal.
    """
    name = "Interpolate"
    description = ("Interpolates the input signal by defining a new abscissa."
                   " The range of the new abscissa has to within the "
                   "range of the abscissa of the input signal.")
    tags = ("Processing",)
    references = {"scipy.interpolate.interp1d (Legacy)":
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html"}

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        abscissa = util.create_abscissa_parameter_block()
        abscissa.name = "New abscissa"
        self.parameters["abscissa"] = abscissa
        self.parameters["interpol_kind"] = parameters.ChoiceParameter(
                 name="Interpolation kind",
                 choices=(("linear", "Linear"), ("slinear", "SLinear"),
                          ("quadratic", "Quadratic"), ("cubic", "Cubic"),
                          ("zero", "Zero"), ("previous", "Previous"),
                          ("next", "Next"), ("nearest", "Nearest")
                          ),
                 default="linear"
        )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        new_abscissa_start = self.parameters["abscissa"].parameters[
            "start"].value
        new_increment = self.parameters["abscissa"].parameters[
            "increment"].value
        new_values = self.parameters["abscissa"].parameters[
            "values"].value
        interpol_kind = self.parameters["interpol_kind"].value
        # Calculate the abscissa of the input signal
        input_signal_abscissa = np.linspace(input_signal.abscissa_start,
                                            input_signal.abscissa_start + input_signal.increment * (
                                                    input_signal.values - 1),
                                            input_signal.values)
        # Calculate the new abscissa
        new_abscissa = np.linspace(new_abscissa_start,
                                   new_abscissa_start + new_increment * (
                                           new_values - 1),
                                   new_values)
        # Validate the abscissa start and end
        if new_abscissa_start < input_signal.abscissa_start:
            raise exceptions.ParameterValueError("New abscissa start is below "
                                                 "abscissa start of the input "
                                                 "signal.")
        if new_abscissa[-1] > input_signal_abscissa[-1]:
            raise exceptions.ParameterValueError("New abscissa end is above "
                                                 "the abscissa end of the "
                                                 "input signal.")
        # Calculate the interpolated ordinate
        f = interp1d(x=input_signal_abscissa, y=input_signal.ordinate,
                     kind=interpol_kind)
        new_ordinate = f(new_abscissa)
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=new_abscissa_start,
            values=new_values,
            increment=new_increment,
            ordinate=new_ordinate,
        )
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = self.inputs[0].metadata

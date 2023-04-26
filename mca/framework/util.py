import numpy as np
import matplotlib.colors as crl

from mca.framework import parameters, validator
from mca.language import _


def create_abscissa_parameter_block():
    """Creates a template abscissa parameter block containing
    the following parameters: Values, Increment, Sampling Frequency,
    Measure Time, Abscissa Start. Those parameters get converted accordingly to
    the current selected conversion.

    For example: If the user assigns values to Increment and Measure Time then
    Values and Sampling Frequency get updated accordingly.

    Returns:
        :class:`.ParameterBlock` :  Abscissa parameter block.
    """
    values = parameters.IntParameter(_("Values"), min_=1, default=1000)
    increment = parameters.FloatParameter(_("Increment"), min_=0,
                                          default=0.01)
    sampling = parameters.FloatParameter(_("Sampling frequency"), default=100,
                                         min_=0, unit="Hz")
    measure_time = parameters.FloatParameter(_("Measure time"), default=10.0,
                                             min_=0, unit="s")
    start = parameters.FloatParameter("Start", default=0)

    def dt_to_fabt():
        sampling.value = 1 / increment.value

    def fabt_to_dt():
        increment.value = 1 / sampling.value

    def dt_values_to_tmess():
        measure_time.value = increment.value * values.value
        dt_to_fabt()

    def fabt_values_to_tmess():
        measure_time.value = values.value / sampling.value
        fabt_to_dt()

    def tmess_values_to_dt():
        increment.value = measure_time.value / values.value
        dt_to_fabt()

    def tmess_dt_to_values():
        values.value = (measure_time.value + increment.value) / increment.value
        dt_to_fabt()

    def tmess_fabt_to_values():
        values.value = measure_time.value * sampling.value
        fabt_to_dt()

    conversion = parameters.ParameterConversion(
        [increment, values], [sampling, measure_time], dt_values_to_tmess
    )
    conversion_1 = parameters.ParameterConversion(
        [sampling, values], [increment, measure_time], fabt_values_to_tmess)
    conversion_2 = parameters.ParameterConversion([values, measure_time],
                                                  [increment, sampling],
                                                  tmess_values_to_dt)
    conversion_3 = parameters.ParameterConversion([increment, measure_time],
                                                  [sampling, values],
                                                  tmess_dt_to_values)
    conversion_4 = parameters.ParameterConversion([sampling, measure_time],
                                                  [increment, values],
                                                  tmess_fabt_to_values)
    abscissa = parameters.ParameterBlock(name=_("Abscissa"),
                                         parameters={"start": start,
                                                     "values": values,
                                                     "increment": increment,
                                                     "sampling": sampling,
                                                     "measure_time": measure_time},
                                         param_conversions=[conversion,
                                                            conversion_1,
                                                            conversion_2,
                                                            conversion_3,
                                                            conversion_4],
                                         default_conversion=0)
    return abscissa


def get_plt_marker_parameter(name=None):
    """Returns a :class:`.ChoiceParameter` for matplotlib marker.

    Args:
        name (str): Name of the parameter. By default set to "Marker".
    """
    if name is None:
        name = _("Marker")
    marker = parameters.ChoiceParameter(
        name=name, choices=((None, _("No marker")),
                              (".", _("Point")),
                              (",", _("Pixel")),
                              ("o", _("Circle")),
                              ("v", _("Triangle down")),
                              ("^", _("Triangle up")),
                              ("<", _("Triangle left")),
                              (">", _("Triangle right")),
                              ("8", _("Octagon")),
                              ("s", _("Square")),
                              ("p", _("Pentagon")),
                              ("*", _("Star")),
                              ("h", _("Hexagon"))
                            )
    )
    return marker


def get_plt_color_parameter(name=_("Color")):
    """Returns a :class:`.ChoiceParameter` for matplotlib colors.

    Args:
        name (str): Name of the parameter. By default set to "Color".
    """
    colors = crl.BASE_COLORS
    color_names = (_("Blue"), _("Green"), _("Red"), _("Cyan"), _("Magenta"),
                   _("Yellow"), _("Black"), _("White"))
    choices = [(color, color_name) for color, color_name in zip(colors.keys(),
                                                                color_names)]
    color_param = parameters.ChoiceParameter(name=name, choices=choices, default=choices[0])
    return color_param


def fill_zeros(signals):
    """This is a helper method to match the abscissa and ordinate length of
    the given signals. Matching is done by adding zeros.

    Args:
        signals: Signals to match.
    Returns:
        list: List of zero filled signals.
    """
    new_signals = []
    increment = signals[0].increment
    min_abscissa_start = min(map(lambda signal: signal.abscissa_start, signals))
    max_abscissa_end = max(
        map(
            lambda
                signal: signal.abscissa_start + signal.values * signal.increment,
            signals,
        )
    )
    max_values = round((max_abscissa_end - min_abscissa_start) / increment)
    for signal in signals:
        zeros_insert = round(
            (signal.abscissa_start - min_abscissa_start) / increment
        )
        zeros_append = round(
            (
                    max_abscissa_end
                    - (signal.abscissa_start + signal.values * increment)
            )
            / increment
        )
        signal.abscissa_start = min_abscissa_start
        signal.values = max_values
        signal.ordinate = np.hstack(
            (
                np.zeros(zeros_insert),
                signal.ordinate,
                np.zeros(zeros_append),
            )
        )
        new_signals.append(signal)
    return new_signals


def abort_all_inputs_empty(process):
    """Abort the process function when the data of all Inputs is None.

    All outputs will be set to None. This function is supposed to be used as
    decorator for the process method of a block.
    """
    def tmp(self):
        if self.all_inputs_empty():
            for output in self.outputs:
                output.data = None
        else:
            process(self)
    return tmp


def abort_any_inputs_empty(process):
    """Abort the process function when the data of any Input is None.

    All outputs will be set to None. This function is supposed to be used as
    decorator for the process method of a block.
    """
    def tmp(self):
        if self.any_inputs_empty():
            for output in self.outputs:
                output.data = None
        else:
            process(self)
    return tmp


def validate_type_signal(process):
    """Checks the data of all Inputs to be type of signal.

    This function is supposed to be used as decorator for the process method
    of a block.
    """
    def tmp(self):
        for input_ in self.inputs:
            if input_.data is not None:
                validator.check_type_signal(input_.data)
        process(self)
    return tmp


def validate_units(abscissa=False, ordinate=False):
    """Checks if the units of the metadata of the Inputs are the same.

    This function is supposed to be used as decorator for the process method
    of a block.
    """
    def inner(process):
        def tmp(self):
            metadatas = [i.metadata for i in self.inputs if i.metadata]
            if abscissa:
                abscissa_units = [metadata.unit_a for metadata in metadatas]
                validator.check_same_units(abscissa_units)
            if ordinate:
                ordinate_units = [metadata.unit_o for metadata in metadatas]
                validator.check_same_units(ordinate_units)
            process(self)
        return tmp
    return inner


def validate_intervals(process):
    """Checks if the intervals of all Input signals are compatible."""
    def tmp(self):
        signals = [i.data for i in self.inputs if i.data]
        validator.check_intervals(signals)
        process(self)
    return tmp

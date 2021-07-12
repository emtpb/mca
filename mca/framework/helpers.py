from mca.framework import parameters
from mca.language import _

import numpy as np


def create_abscissa_parameter_block():
        values = parameters.IntParameter(_("Values"), min_=1, value=628)
        increment = parameters.FloatParameter(_("Increment"), min_=0,
                                              value=0.01)
        sampling = parameters.FloatParameter(_("Sampling frequency"), value=100, min_=0, unit="Hz")
        measure_time = parameters.FloatParameter(_("Measure time"), value=6.28, min_=0)
        start = parameters.FloatParameter("Start", value=0)

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
            values.value = measure_time.value / increment.value
            dt_to_fabt()

        def tmess_fabt_to_values():
            values.value = measure_time.value * sampling.value
            fabt_to_dt()

        conversion = parameters.ParameterConversion(
            [increment, values], [sampling, measure_time], dt_values_to_tmess
        )
        conversion_1 = parameters.ParameterConversion(
            [sampling, values], [increment, measure_time], fabt_values_to_tmess)
        conversion_2 = parameters.ParameterConversion([values, measure_time], [increment, sampling],
                                              tmess_values_to_dt)
        conversion_3 = parameters.ParameterConversion([increment, measure_time], [sampling, values],
                                              tmess_dt_to_values)
        conversion_4 = parameters.ParameterConversion([sampling, measure_time], [increment, values],
                                                      tmess_fabt_to_values)
        abscissa = parameters.ParameterBlock(name=_("Abscissa"),
                                             parameters={"start": start,
                                                         "values": values,
                                                         "increment": increment,
                                                         "sampling": sampling,
                                                         "measure_time": measure_time},
                                             param_conversions=[conversion, conversion_1, conversion_2, conversion_3, conversion_4],
                                             default_conversion=0)
        return abscissa


def fill_zeros(signals):
    """This is a helper method to match the abscissa and ordinate length of
    the given signals. Matching is done by adding zeros.

    Args:
        signals: Signals to match.
    """
    new_signals = []
    increment = signals[0].increment
    min_abscissa_start = min(
        list(map(lambda sgn: sgn.abscissa_start, signals))
    )
    max_abscissa_end = max(
        list(
            map(
                lambda sgn: sgn.abscissa_start + sgn.values * sgn.increment,
                signals,
            )
        )
    )
    max_values = int((max_abscissa_end - min_abscissa_start) / increment)
    for sgn in signals:
        zeros_to_beginning = round(
            (sgn.abscissa_start - min_abscissa_start) / increment
        )
        zeros_to_ending = round(
            (
                    (min_abscissa_start + max_values * increment)
                    - (sgn.abscissa_start + sgn.values * increment)
            )
            / increment
        )
        sgn.abscissa_start = min_abscissa_start
        sgn.values = max_values
        sgn.ordinate = np.hstack(
            (
                np.zeros(zeros_to_beginning),
                sgn.ordinate,
                np.zeros(zeros_to_ending),
            )
        )
        new_signals.append(sgn)
    return new_signals
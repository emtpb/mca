import numpy as np
import copy

from mca.framework import validator, data_types, DynamicBlock, helpers
from mca.language import _


class Adder(DynamicBlock):
    """Adds multiple signals to one new signal."""
    name = _("Adder")
    description = _("Adds multiple signals to one signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.dynamic_input = (1, None)
        self.new_output()
        self.new_input()
        self.new_input()

    def setup_parameters(self):
        pass

    def _process(self):
        if self.all_inputs_empty():
            return
        for i in self.inputs:
            validator.check_type_signal(i.data)
        signals = [copy.copy(i.data) for i in self.inputs if i.data]
        abscissa_units = [signal.metadata.unit_a for signal in signals]
        ordinate_units = [signal.metadata.unit_o for signal in signals]
        validator.check_same_units(abscissa_units)
        validator.check_same_units(ordinate_units)
        validator.check_intervals(signals)

        modified_signals = helpers.fill_zeros(signals)

        ordinate = np.zeros(modified_signals[0].values)
        for sgn in modified_signals:
            ordinate += sgn.ordinate
        abscissa_start = modified_signals[0].abscissa_start
        values = modified_signals[0].values
        increment = modified_signals[0].increment
        self.outputs[0].data = data_types.Signal(
            metadata=self.outputs[0].get_metadata(signals[0].metadata),
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate)


def fill_zeros(signals):
    """This is a helper method for :meth:`.Adder._process`.
    
    Intervals are often not identical thus cannot be added immediately.
    This method fills up the arrays with zeros.
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
